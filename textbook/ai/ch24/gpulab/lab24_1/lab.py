# GPU 实验 24.1 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 24.1　并行环境里训一个到达任务，并用两列成绩验收它
# 训练只是这个实验的一半。另一半——**也是更要紧的一半**——是回答三个问题：
#
# 1. 并行环境数买到了什么（**迭代轮数**少多少、**总环境步数**多多少，两个数分开报）；
# 2. 这个策略在**标称仿真参数**与**改掉的物理参数**上各得多少分（**两列分开报**，各写明验收了多少回合）；
# 3. 吞吐该怎么说（**只引四样齐全的公开值，不把自己的机时折算成吞吐**）。
#
# **先把口径说清楚**：
#
# * 这台机械臂是平面二连杆 + 一个只管夹爪朝向的腕关节，**物理步长 1/40 s、控制步长 1/20 s**
#   （decimation 2）、一回合 60 步，全都是本实验的显式假设；
# * 成功的定义与本章算例同口径：**夹爪闭合的那一刻** 位置误差 < 2 cm **且** 姿态误差 < 0.4 rad
#   ——走到位不闭合不算，闭合了没到位也不算；
# * **“改了物理参数”不是真机**：它只是换了连杆长度、摩擦、观测噪声与执行延迟的同一个玩具，
#   没有接触、形变、工件滑动、相机标定漂移。真机那一列只能靠真的试，试多少次也必须报；
# * 验收用的回合**不算进训练的环境步数**（算进去就是自欺欺人）。
# %%
import sys; sys.path.insert(0, "..")
import statistics
import time

import wqgpu
env = wqgpu.check(("gpu", "torch"))

import torch
print(torch.cuda.get_device_name(0), torch.__version__)
dev = "cuda"

# %% [markdown]
# ## 1. 成批的环境、策略，与一个参照（任务 2）
# 环境整个写在张量里：`q` 是 `[N, 3]` 的关节角，一步就把 N 个环境一起推进。
#
# 策略是**线性策略**，但特征里写进了运动学结构：常数项、任务空间误差
# （工件位姿 − **量出来的**夹爪位姿）、关节角的正余弦，以及**误差与正余弦的乘积**
# ——雅可比转置伺服正好是这些乘积的线性组合，所以这个策略族里**存在**一个好解。
# 这比堆层数便宜得多，也是工程上最先该做的一步。
#
# 为了有个“应该怎么走”的参照，这一节最后按手写的雅可比转置伺服直接填一组权重，
# 把它的两列成绩打出来——后面训出来的策略好不好，拿它比。
# %%
L1, L2 = 0.35, 0.30                  # 标称连杆长度（m），显式假设
PHYS_DT, DEC = 0.025, 2              # 物理步长 1/40 s，控制步长 = 2 × 物理步长 = 1/20 s
CTRL_DT = PHYS_DT * DEC
STEPS = 60                           # 一回合 60 步（3 秒）
TOL_P, TOL_R = 0.02, 0.4             # 成功判据：位置 2 cm、姿态 0.4 rad（与本章算例同口径）
VMAX = torch.tensor([1.6, 1.6, 2.2], device=dev)
QMIN = torch.tensor([-2.60, -2.50, -2.20], device=dev)
QMAX = torch.tensor([2.60, 2.50, 2.20], device=dev)
QHOME = torch.tensor([0.55, 0.95, -0.30], device=dev)

SIM = {"l1": L1, "l2": L2, "fric": 0.04, "noise": 0.0, "delay": 0, "name": "标称仿真参数"}
ALT = {"l1": 0.363, "l2": 0.288, "fric": 0.11, "noise": 0.004, "delay": 1, "name": "改掉之后的参数"}
NF, NA = 17, 4                       # 17 个特征，4 维动作（三个关节角速度 + 夹爪闭合）
NPAR = NF * NA
N_HOLDOUT = 256                      # 留出集回合数：两列都用这一组


def fk(q, W):
    """正运动学：[N,3] 关节角 → [N,3] 夹爪位姿（x, y, 朝向）。"""
    x = W["l1"] * torch.cos(q[:, 0]) + W["l2"] * torch.cos(q[:, 0] + q[:, 1])
    y = W["l1"] * torch.sin(q[:, 0]) + W["l2"] * torch.sin(q[:, 0] + q[:, 1])
    return torch.stack([x, y, q.sum(1)], 1)


def sample_targets(n, g):
    """工作空间里采 n 个工件位姿。"""
    r = 0.30 + 0.26 * torch.rand(n, generator=g, device=dev)
    a = -0.35 + 1.60 * torch.rand(n, generator=g, device=dev)
    th = -0.9 + 2.8 * torch.rand(n, generator=g, device=dev)
    return torch.stack([r * torch.cos(a), r * torch.sin(a), th], 1)


def sample_starts(n, g, spread=0.25):
    """围着收工位姿散开的起始关节角。"""
    return (QHOME + spread * torch.randn(n, 3, generator=g, device=dev)).clamp(QMIN, QMAX)


def feats(q, tip, p):
    """17 个特征。误差按分米计（×10），好让权重落在个位数上。"""
    e = p - tip
    ex, ey, eth = e[:, 0] * 10, e[:, 1] * 10, e[:, 2]
    d = torch.linalg.vector_norm(e[:, :2], dim=1) * 10
    s1, c1 = torch.sin(q[:, 0]), torch.cos(q[:, 0])
    s12, c12 = torch.sin(q[:, 0] + q[:, 1]), torch.cos(q[:, 0] + q[:, 1])
    one = torch.ones_like(d)
    return torch.stack([one, ex, ey, eth, d, s1, c1, s12, c12,
                        ex * s1, ex * c1, ex * s12, ex * c12,
                        ey * s1, ey * c1, ey * s12, ey * c12], 1)


def rollout(theta, p, q0, W, g):
    """N 个环境各带**自己的一套参数** theta[N, NPAR]，一起跑一回合。

    夹爪闭合指令为正就闭合：**这一刻定成败，回合结束**（之后这个环境原地冻住）。
    """
    n = p.shape[0]
    Wm = theta.view(n, NF, NA)
    q = q0.clone()
    buf = [torch.zeros(n, NA, device=dev) for _ in range(W["delay"])]
    alive = torch.ones(n, dtype=torch.bool, device=dev)
    ok = torch.zeros(n, dtype=torch.bool, device=dev)
    dsum = torch.zeros(n, device=dev)
    for t in range(STEPS):
        true_tip = fk(q, W)
        tip = true_tip + (W["noise"] * torch.randn(n, 3, generator=g, device=dev)
                          if W["noise"] > 0 else 0.0)
        a = torch.tanh(torch.einsum("ni,nij->nj", feats(q, tip, p), Wm))
        buf.append(a)
        ae = buf.pop(0)                                  # 执行延迟
        step = (1.0 - W["fric"]) * ae[:, :3] * VMAX * CTRL_DT * alive.unsqueeze(1).float()
        for _ in range(DEC):                             # decimation：一个控制周期走两个物理步
            q = (q + step / DEC).clamp(QMIN, QMAX)
        true_tip = fk(q, W)
        dp = torch.linalg.vector_norm(true_tip[:, :2] - p[:, :2], dim=1)
        dsum = dsum + dp * alive.float()
        close = (ae[:, 3] > 0.0) & alive
        ok = ok | (close & (dp < TOL_P) & ((true_tip[:, 2] - p[:, 2]).abs() < TOL_R))
        alive = alive & ~close
    final = torch.linalg.vector_norm(fk(q, W)[:, :2] - p[:, :2], dim=1)
    return ok, dsum / STEPS, final, alive


def reward(theta, p, q0, W, g):
    """奖励：抓成 +20，再减掉终点误差与路上的平均距离，不闭合另罚 2 分。

    这里的塑形项是**显式假设**；实验 24.4 专门讲它过大时会出什么事。
    """
    ok, dmean, final, alive = rollout(theta, p, q0, W, g)
    return 20.0 * ok.float() - 20.0 * final - 5.0 * dmean - 2.0 * alive.float()


def score(theta, p, q0, W, g):
    """一条策略在一套物理参数上的成功率（%）。验收的回合不算进训练步数。"""
    ok, _, _, _ = rollout(theta.unsqueeze(0).expand(p.shape[0], -1), p, q0, W, g)
    return ok.float().mean().item() * 100


g0 = torch.Generator(device=dev).manual_seed(0)
HP = sample_targets(N_HOLDOUT, g0)
HQ = sample_starts(N_HOLDOUT, g0)

hand = torch.zeros(NF, NA, device=dev)                   # 参照：手写的雅可比转置伺服
hand[9, 0], hand[11, 0] = -3.5 * L1, -3.5 * L2
hand[14, 0], hand[16, 0] = 3.5 * L1, 3.5 * L2
hand[11, 1], hand[16, 1] = -3.5 * L2, 3.5 * L2
hand[3, 2] = 3.5
hand[0, 3], hand[4, 3] = 0.6, -10.0
hand = hand.reshape(-1)
print(f"物理步长 {PHYS_DT:.4f} s（1/{round(1 / PHYS_DT)}）、控制步长 {CTRL_DT:.3f} s"
      f"（1/{round(1 / CTRL_DT)}）、一回合 {STEPS} 步、留出集 {N_HOLDOUT} 回合")
print(f"参照（手写伺服，不是学出来的）：{SIM['name']} {score(hand, HP, HQ, SIM, g0):.1f}%、"
      f"{ALT['name']} {score(hand, HP, HQ, ALT, g0):.1f}%")
print("**这两个数就是本实验报表的格式：两列，各带回合数**")

# %% [markdown]
# ## 2. 扫并行环境数（任务 3）
# 训练用**交叉熵方法**（CEM）：每一轮按当前分布采 `n_envs` 组参数，每组在**自己的那个环境**里
# 跑一个回合（各自的工件位姿与起始位姿都不同），取成绩最好的那 10% 当精英，
# 用精英重新估分布的均值与标准差。
#
# 这里**环境数决定的是“选得准不准”**：环境数少的时候，一组参数的成绩里有很大一部分是
# “这一回合的工件好不好抓”，于是精英里混进了一堆运气好的——分布往错的方向走。
# 环境数多了，这种运气被平均掉，选出来的精英才是真的好。
#
# 每两轮在**同一个留出集**上验收一次，第一次达到达标线就停下来，记下轮数与**总环境步数**。
# 每档跑 3 个随机种子，报**中位数**，并注明有几个种子没达标——单个种子的噪声太大，
# 一个数字下不了结论。
# %%
SIGMA0, ELITE, MAXIT, TARGET, SMIN = 0.6, 0.10, 400, 65.0, 0.03
N_ENVS = (128, 512, 2048, 8192)
SEEDS = 3


def train(n_envs, seed=0):
    """返回（达标轮数或 None，总环境步数，留出集成绩，墙钟秒数，策略参数）。"""
    g = torch.Generator(device=dev).manual_seed(seed + 7)
    m = torch.zeros(NPAR, device=dev)
    sd = torch.full((NPAR,), SIGMA0, device=dev)
    n_elite = max(int(n_envs * ELITE), 2)
    steps = 0
    t0 = time.perf_counter()
    for it in range(1, MAXIT + 1):
        pop = m + sd * torch.randn(n_envs, NPAR, generator=g, device=dev)
        p = sample_targets(n_envs, g)
        q0 = sample_starts(n_envs, g)
        r = reward(pop, p, q0, SIM, g)
        steps += n_envs * STEPS                          # **环境步数照实数**
        el = pop[torch.topk(r, n_elite).indices]
        m = el.mean(0)
        sd = el.std(0).clamp(min=SMIN)
        if it % 2 == 0 and score(m, HP, HQ, SIM, g) >= TARGET:
            return it, steps, score(m, HP, HQ, SIM, g), time.perf_counter() - t0, m
    return None, steps, score(m, HP, HQ, SIM, g), time.perf_counter() - t0, m


rows, headline = [], None
print(f"达标线：留出集成功率 ≥ {TARGET:.0f}%（{N_HOLDOUT} 回合），最多 {MAXIT} 轮，"
      f"每档 {SEEDS} 个种子报中位数\n")
print("并行环境数　达标轮数（中位数）　总环境步数（中位数）　训练用时（中位数）　没达标的种子数")
for n in N_ENVS:
    its, sts, wls, nf, best = [], [], [], 0, None
    for sd_i in range(SEEDS):
        it, st, h, wall, m = train(n, seed=sd_i * 17)
        if it is None:
            nf += 1
            it = MAXIT                                   # 没达标的按上限计，**并注明有几个**
        elif best is None:
            best = m
        its.append(it)
        sts.append(st)
        wls.append(wall)
    row = (n, statistics.median(its), statistics.median(sts), statistics.median(wls), nf)
    rows.append(row)
    if best is not None:
        headline = (n, row[1], row[2], row[3], best)
    print(f"  {n:9d}　{row[1]:16.1f}　{row[2]:18,.0f}　{row[3]:14.1f} s　{nf:9d}")

iter_speedup = rows[0][1] / max(rows[-1][1], 1e-9)
steps_blowup = rows[-1][2] / max(rows[0][2], 1e-9)
print(f"\n从 {N_ENVS[0]} 个环境到 {N_ENVS[-1]} 个环境：达标轮数少 {iter_speedup:.1f} 倍，"
      f"总环境步数多 {steps_blowup:.1f} 倍")
print("**这两件事要一起说**：并行环境把**等待的轮数**买下来了，代价是**多烧了几倍的环境步数**；"
      "环境数最少的那几档甚至根本达不到标——它买到的不是“更快”，而是“能不能收敛”。")
print("环境数再往上加，轮数降不了多少，算力的账却照样翻倍——**收益是递减的**。")
for i in range(len(N_ENVS) - 1):
    print(f"  {N_ENVS[i]:5d} → {N_ENVS[i + 1]:5d}：轮数 {rows[i][1]:.0f} → {rows[i + 1][1]:.0f}，"
          f"总步数 ×{rows[i + 1][2] / max(rows[i][2], 1e-9):.1f}")

# %% [markdown]
# ## 3. 两列成绩（任务 4）
# 把达标那一档的策略拿出来，在**同一个留出集**上验收两遍：一遍用标称仿真参数，
# 一遍把物理参数改掉（连杆长度差十几毫米、摩擦大一倍半、观测带噪声、指令晚一拍）。
#
# **两列分开报，不要平均。** 左边那一列回答“这个策略在我建的模型里行不行”，
# 右边那一列回答“模型错一点它还剩多少”。平均出来的数不回答任何问题。
# %%
if headline is None:                                     # 一档都没达标：先把达标线调低，或把 MAXIT 加大
    raise RuntimeError("没有一档达到达标线：把 TARGET 调低或把 MAXIT 加大，再跑第 2 节")
n_envs, iters, env_steps, train_s, theta = headline
sim_success_pct = score(theta, HP, HQ, SIM, g0)
real_success_pct = score(theta, HP, HQ, ALT, g0)
n_trials = N_HOLDOUT
succ_ratio = real_success_pct / max(sim_success_pct, 1e-9)
print(f"报表那一行：{n_envs} 个并行环境、{iters:.0f} 轮、{env_steps:,.0f} 个环境步、"
      f"训练 {train_s:.1f} 秒\n")
print(f"{'验收用的物理参数':<22}{'成功率':>8}　验收回合数")
print(f"{SIM['name']:<22}{sim_success_pct:7.1f}%　{n_trials}")
print(f"{ALT['name']:<22}{real_success_pct:7.1f}%　{n_trials}")
print(f"\n改了参数那一列是仿真那一列的 {succ_ratio:.2f} 倍"
      f"（差 {sim_success_pct - real_success_pct:.1f} 个百分点）")
print("**只有仿真那一列的结果不采信**（本章第一号引用警告）。而且这里的“改了参数”也不是真机："
      "真机上还有接触、形变、工件滑动、相机标定漂移——真机那一列只能靠真的试，试多少次也必须报。")
print(f"参照（手写伺服）：{score(hand, HP, HQ, SIM, g0):.1f}% / {score(hand, HP, HQ, ALT, g0):.1f}%"
      "——训出来的策略与它比，差在哪一列上？")

# %% [markdown]
# ## 4. 吞吐怎么说（任务 5）
# 这一节一行代码都不跑计时。**“每秒多少步”不是性能指标，而是（显卡、环境数、物理步长、任务）
# 四元组的函数**，四样不全的吞吐数本章一律不印；本实验也**不把自己的机时折算成吞吐**
# ——那样折出来的数是编的。
#
# 要引吞吐，只能引四样齐全的公开值。本章用的是 Isaac Gym 论文正文那一组，抄在下面；
# **引用时必须连这四样一起写，并注明是引用**。
# %%
CITED = {
    "显卡": "单块 NVIDIA A100",
    "任务": "Ant",
    "并行环境数": 4096,
    "物理步长": "1/120 s（控制步长 1/60 s）",
    "训练过程中平均": "540,000 步/秒",
    "出处": "arXiv:2108.10470（Isaac Gym 论文）§4 表 4、§6.1.1——**引用，不是本机实测**",
}
width = max(len(k) for k in CITED)
for k, v in CITED.items():
    print(f"  {k:<{width}}  {v}")
print("\n同一块 A100 上，同一篇论文里 Ant 的峰值是 700,000 步/秒、Shadow Hand 只有 150,000 步/秒"
      "（16384 个环境）——**差好几倍**。所以跨任务、跨框架的吞吐比较本章不做。")
print(f"本机这一次训练：{env_steps:,.0f} 个环境步、{train_s:.1f} 秒。"
      "**这两个数不相除**：相除得到的“步/秒”缺任务与物理步长的对照口径，"
      "而且这里还混着留出集验收与显卡预热的时间，印出来只会被人拿去横向比。")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(n_envs=int(n_envs), iters=float(iters), env_steps=float(env_steps),
             sim_success_pct=sim_success_pct, real_success_pct=real_success_pct,
             n_trials=int(n_trials), succ_ratio=succ_ratio,
             iter_speedup=float(iter_speedup), steps_blowup=float(steps_blowup),
             train_s=float(train_s))
