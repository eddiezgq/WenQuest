"""算例 24.6：并行环境数与样本效率。

并行物理仿真的卖点是“几千个环境一起跑”。它换来的到底是什么？本算例把两个数分开报：

- **迭代轮数**：策略更新了多少次（每轮要等所有并行环境跑完）；
- **总环境步数**：所有环境加起来一共走了多少步（这才是算力的账）。

做法：在一个三参数的小策略族里爬山（它自己以为的两个连杆长度 + 增益），
每一轮用 `n_envs` 个回合估一次成绩，成绩不降就接受。
并行环境数越多，每轮的估计越准、走错的弯路越少 → **迭代轮数下降**；
但每轮要跑的回合数成倍上升 → **总环境步数上升**。这就是收益递减。

**墙钟时间与吞吐一个字都不编**（本章口径 c）：每秒多少步是（显卡、环境数、物理步长、任务）
四元组的函数，本书只在引用时照抄 Isaac Gym 论文正文那组四样齐全的公开值
（见 `conventions/robot_facts.py` 的 `ISAAC_GYM`），并注明是引用。
"""
import numpy as np

from _ch24 import SIM, evaluate, rollout, sample_starts, sample_targets, servo_policy
from bookout import out
from robot_facts import ISAAC_GYM

N_ENVS = (1, 2, 4, 8, 16, 32)
SEEDS = 6                      # 每个环境数跑 6 个随机种子，报中位数（单个种子噪声太大）
TARGET = 60.0                  # 达标线：留出集上的成功率（%）
MAX_ITER = 60
N_HOLDOUT = 40
P0 = np.array([0.25, 0.25, 1.0])        # 起点：它以为连杆各 25 cm、增益 1（成绩很差）
STEP_SIGMA = np.array([0.05, 0.05, 0.8])

v = {"n_envs": list(N_ENVS), "seeds": SEEDS, "target_pct": TARGET, "max_iter": MAX_ITER,
     "n_holdout": N_HOLDOUT, "p0": P0.tolist()}

ho_poses = sample_targets(N_HOLDOUT, seed=11)
ho_starts = sample_starts(N_HOLDOUT, seed=11, spread=0.25)


def holdout(p):
    """留出集上的成功率：**验收用的回合不算进训练的环境步数**（算进去就是自欺欺人）。"""
    return evaluate(lambda ps, w: servo_policy(gain=p[2], l1_hat=p[0], l2_hat=p[1]),
                    ho_poses, ho_starts, SIM, seed=7)["success_pct"]


print(f"起点参数 {P0.tolist()}：留出集成功率 {holdout(P0):.1f}%")


def train(n_envs, seed):
    """爬山：每轮用 n_envs 个回合估一次成绩。返回（达标用了几轮，总环境步数，最后的成绩）。"""
    g = np.random.default_rng(seed + 7)
    p = P0.copy()
    steps = 0

    def est(par, it):
        nonlocal steps
        poses = sample_targets(n_envs, seed=1000 + it * 13)
        starts = sample_starts(n_envs, seed=1000 + it * 13, spread=0.25)
        s = 0
        for k in range(n_envs):
            r = rollout(servo_policy(gain=par[2], l1_hat=par[0], l2_hat=par[1]),
                        poses[k], starts[k], SIM, seed=k + it * 31)
            steps += r["n_steps"]                    # **环境步数照实数**
            s += r["success"]
        return s / n_envs * 100

    cur = est(p, 0)
    for it in range(1, MAX_ITER + 1):
        cand = p + STEP_SIGMA * g.normal(0, 1, 3)
        cand[2] = abs(cand[2])
        cand[:2] = np.clip(cand[:2], 0.05, 0.8)
        sc = est(cand, it)
        if sc >= cur:
            p, cur = cand, sc
        if holdout(p) >= TARGET:
            return it, steps, holdout(p)
    return None, steps, holdout(p)


iters_med, steps_med, fails = [], [], []
print(f"\n并行环境数　达标迭代轮数（{SEEDS} 个种子的中位数）　总环境步数（中位数）　没达标的种子数")
for n in N_ENVS:
    its, sts, nf = [], [], 0
    for sd in range(SEEDS):
        it, steps, h = train(n, seed=sd * 17)
        if it is None:
            nf += 1
            it = MAX_ITER                            # 没达标的按上限计，**并注明有几个**
        its.append(it)
        sts.append(steps)
    iters_med.append(float(np.median(its)))
    steps_med.append(float(np.median(sts)))
    fails.append(nf)
    print(f"  {n:9d}　{np.median(its):9.1f}　{np.median(sts):14.0f}　{nf:9d}")

iters_med = np.array(iters_med)
steps_med = np.array(steps_med)
v["iters_median"] = iters_med.tolist()
v["env_steps_median"] = steps_med.tolist()
v["n_failed_seeds"] = fails
v["n_envs_min"], v["n_envs_max"] = int(N_ENVS[0]), int(N_ENVS[-1])   # 第 175 轮补：正文表格的行标签

# ---------- 一、轮数降、总步数升
v["iters_1env"], v["iters_max_env"] = float(iters_med[0]), float(iters_med[-1])
v["steps_1env"], v["steps_max_env"] = float(steps_med[0]), float(steps_med[-1])
v["iter_speedup"] = v["iters_1env"] / max(v["iters_max_env"], 1e-9)
v["steps_blowup"] = v["steps_max_env"] / max(v["steps_1env"], 1e-9)
print(f"\n从 1 个环境到 {N_ENVS[-1]} 个环境：迭代轮数从 {v['iters_1env']:.0f} 降到 "
      f"{v['iters_max_env']:.0f}（少 {v['iter_speedup']:.1f} 倍），"
      f"总环境步数从 {v['steps_1env']:.0f} 涨到 {v['steps_max_env']:.0f}"
      f"（多 {v['steps_blowup']:.1f} 倍）")
assert v["iters_max_env"] < v["iters_1env"], "环境数增加，迭代轮数下降"
assert v["steps_max_env"] > v["steps_1env"], "环境数增加，总环境步数上升"
assert v["steps_blowup"] > v["iter_speedup"], \
    "总步数涨得比轮数降得多——这就是收益递减，必须写进打印里"
print(f"**这两件事要一起说**：并行环境把**等待的轮数**买下来了（少 "
      f"{v['iter_speedup']:.1f} 倍），代价是**多烧了 {v['steps_blowup']:.1f} 倍的环境步数**。"
      f"步数涨得比轮数降得多，所以**收益是递减的**：环境数再加下去，轮数降不了多少，"
      f"算力的账却照样翻倍")

# ---------- 二、每翻一倍，还剩多少收益
gain = -np.diff(iters_med)
v["iter_gain_per_doubling"] = gain.tolist()
print("\n环境数每翻一倍，省下的迭代轮数：")
for i in range(len(N_ENVS) - 1):
    print(f"  {N_ENVS[i]:2d} → {N_ENVS[i + 1]:2d}：{gain[i]:+.1f} 轮，"
          f"总步数 ×{steps_med[i + 1] / steps_med[i]:.1f}")
v["steps_per_iter_ratio"] = float(np.median(steps_med[1:] / steps_med[:-1]))
print(f"总步数差不多是每翻一倍就 ×{v['steps_per_iter_ratio']:.1f}（本来就该这样），"
      f"而省下的轮数越来越少")

# ---------- 三、吞吐与墙钟：只引公开值，不自己编
ant = ISAAC_GYM["ant"]
v["cited_gpu"] = ISAAC_GYM["gpu"]
v["cited_task"] = ant["task"]
v["cited_envs"] = ant["n_envs_for_train_avg"]
v["cited_steps_per_s"] = ant["train_avg_steps_per_s"]
v["cited_sim_dt_s"] = ant["sim_dt_s"]
v["cited_control_dt_s"] = ant["control_dt_s"]
v["cited_ref"] = ISAAC_GYM["ref"]
print(f"\n要把轮数换成时间，必须有吞吐；而吞吐只能引**四样齐全**的公开值："
      f"{v['cited_gpu']}、{v['cited_task']} 任务、{v['cited_envs']} 个并行环境、"
      f"物理步长 1/{round(1 / v['cited_sim_dt_s']):.0f} s（控制步长 "
      f"1/{round(1 / v['cited_control_dt_s']):.0f} s）时，训练过程中平均 "
      f"{v['cited_steps_per_s']:,} 步/秒（引自 {v['cited_ref']}）")
# **不拿这个吞吐去除本算例的步数**：那样折算出来的机时是编的，本节不交这样的数给正文。
print(f"**这个数不能拿来算本算例的机时**：它是另一个任务、另一套物理参数、另一块显卡上的值。"
      f"本算例只报步数（{v['steps_max_env']:.0f} 步）与轮数（{v['iters_max_env']:.0f} 轮），"
      f"**墙钟时间与吞吐一个字不编**")
assert ISAAC_GYM["anymal"]["steps_per_s"] is None, "论文没单列的吞吐，不许补"
print("这个算例回答不了什么：真并行仿真里，环境数还影响显存、批量大小与策略更新的稳定性；"
      "而且一轮的墙钟时间并不随环境数线性涨（到显卡吃满才涨）。"
      "**这些都要在自己的机器上实测，不能照抄别人的四元组**")

out(**v)
