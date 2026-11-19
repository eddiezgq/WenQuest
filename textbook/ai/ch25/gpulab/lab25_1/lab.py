# GPU 实验 25.1 的笔记本（百分号格式，构建时转成 .ipynb）
# %% [markdown]
# # GPU 实验 25.1　大规模车辆路径：启发式对已证明最优，与启发式对下界
# 这个实验要算的不是“排线”，是**怎样诚实地报一个排线有多好**。
#
# 三件事分开做、分开报：
#
# 1. **小规模**：在显卡上成批穷举出**已证明最优解**（全部客户次序 × 按容量的最优切分），
#    量出贪心的**真实差距**；
# 2. **同一批实例**换成跟**可证明的下界**比，看“对下界的比值”比真实差距夸大了多少；
# 3. **大规模**：穷举不了，手上只剩下界。这一段只能报“在这个下界的意义下差距不超过多少”。
#
# **先把口径说清楚**：
#
# * **下界不是最优解**。由下界算出来的“最多差多少”是一个**上界说法**：真实差距一定不超过它，
#   但不等于它。本实验在小规模上把两者同时量出来，就是为了让你看见中间差了多少个百分点；
# * **“最好已知解”会随时间变**。同一个 CVRPLIB X 集，已证明最优的实例数从 2017 年那篇论文的
#   40/100 变成今天的 61/100，“最好已知解”本身也在被一篇篇论文改掉——引用它必须写明日期；
# * 本实验的坐标、需求、载重全部是**合成的显式假设**，不取自任何企业数据，也不下载任何基准实例。
# %%
import itertools
import math
import time

import numpy as np
import wqgpu
env = wqgpu.check(("gpu", "torch"))

import torch
print(torch.cuda.get_device_name(0), torch.__version__)
dev = "cuda"
torch.set_grad_enabled(False)
INF = float("inf")

# %% [markdown]
# ## 1. 实例：一个库房 + n 个取送点（任务 2）
# **显式假设**：厂区 60 m 见方，库房在正中；每个取送点的需求在 8—33 之间（整数），车的载重 60。
# 坐标与需求都是合成的，不取自任何企业数据。
# %%
CAP = 60.0
SPAN = 60.0
M_SMALL = 64                 # 每种小规模算这么多个实例，取平均
M_BIG = 32                   # 大规模实例数（穷举不了，只算贪心与下界）
EXACT = [3, 4, 5, 6, 7, 8]   # 能穷举出已证明最优的规模（9 个点开始 n! 就吃不住了）
BIG = [10, 20, 40, 60, 100, 150, 300, 600]


def instances(n, m, seed):
    """m 个实例：坐标 (m, n+1, 2)、需求 (m, n+1)、距离矩阵 (m, n+1, n+1)。下标 0 是库房。"""
    g = torch.Generator(device=dev).manual_seed(seed + 7000 + n)
    xy = torch.rand((m, n + 1, 2), generator=g, device=dev) * SPAN
    xy[:, 0, :] = SPAN / 2
    dem = torch.randint(8, 34, (m, n + 1), generator=g, device=dev).to(torch.float32)
    dem[:, 0] = 0.0
    d = torch.cdist(xy, xy)
    return xy, dem, d


xy, dem, d = instances(8, M_SMALL, 0)
print(f"载重 {CAP:.0f}，厂区 {SPAN:.0f} m 见方；8 个点的实例 {M_SMALL} 个")
print(f"需求合计 {float(dem.sum(1).mean()):.0f}（平均），所以至少要跑 "
      f"{math.ceil(float(dem.sum(1).mean()) / CAP)} 趟")

# %% [markdown]
# ## 2. 调度室那一版：最近邻贪心（装不下就回库房）
# 一步一步选最近的那个还装得下的点；都装不下就回库房、开新的一趟。
# 整批实例一起走，所以这一段在显卡上是并行的。
# %%
def greedy(d, dem):
    """返回 (总行程, 用了几趟)，都是 (m,) 的张量。"""
    m, np1 = dem.shape
    n = np1 - 1
    row = torch.arange(m, device=d.device)
    left = torch.ones((m, np1), dtype=torch.bool, device=d.device)
    left[:, 0] = False
    cur = torch.zeros(m, dtype=torch.long, device=d.device)
    load = torch.zeros(m, device=d.device)
    total = torch.zeros(m, device=d.device)
    trips = torch.ones(m, dtype=torch.long, device=d.device)
    for _ in range(n):
        fits = left & (load.unsqueeze(1) + dem <= CAP + 1e-6)
        back = ~fits.any(1)                        # 都装不下了：回库房，开新的一趟
        if bool(back.any()):
            total = total + torch.where(back, d[row, cur, 0], torch.zeros_like(total))
            trips = trips + back.to(torch.long)
            load = torch.where(back, torch.zeros_like(load), load)
            cur = torch.where(back, torch.zeros_like(cur), cur)
            fits = left & (load.unsqueeze(1) + dem <= CAP + 1e-6)
        step = torch.where(fits, d[row, cur], torch.full_like(d[row, cur], INF))
        k = step.argmin(1)
        total = total + step.gather(1, k.unsqueeze(1)).squeeze(1)
        load = load + dem.gather(1, k.unsqueeze(1)).squeeze(1)
        left.scatter_(1, k.unsqueeze(1), False)
        cur = k
    return total + d[row, cur, 0], trips


g_cost, g_trips = greedy(d, dem)
print(f"贪心：平均总行程 {float(g_cost.mean()):.1f} m，平均 {float(g_trips.float().mean()):.2f} 趟")

# %% [markdown]
# ## 3. 已证明最优解：GPU 上成批穷举（任务 3）
# 任何可行解的若干条回路首尾相接就是一个客户次序；给定次序，按容量做动态规划切分
# 就能找到这个次序下最好的切法。所以**全部次序 × 最优切分**覆盖了全部可行解——
# 穷举出来的那个值是**真值**，不是“最好已知解”。
#
# 次数按 n! 增长：8 个点是 40 320 个次序，一批 64 个实例就是两百多万条待切的次序，
# 显卡一次算完；到 9 个点就吃不住了，所以程序在那里**直接报错**，不许悄悄拿启发式充当最优。
# %%
def optimal(d, dem, n):
    """穷举出已证明最优的总行程 (m,)。n > 8 直接报错。"""
    if n > 8:
        raise RuntimeError(f"{n} 个点穷举不了（n! 爆炸），这个规模只能跟下界比")
    m = dem.shape[0]
    perm = torch.tensor(list(itertools.permutations(range(1, n + 1))),
                        dtype=torch.long, device=d.device)              # (P, n)
    d0 = d[:, 0][:, perm]                                               # (m,P,n) 库房→第 k 个
    inner = torch.zeros((m, perm.shape[0], n), device=d.device)
    if n > 1:                                                          # 次序上相邻两点的距离，累加
        cons = d[:, perm[:, :-1], perm[:, 1:]]
        inner[:, :, 1:] = cons.cumsum(-1)
    dcum = torch.zeros((m, perm.shape[0], n + 1), device=d.device)
    dcum[:, :, 1:] = dem[:, perm].cumsum(-1)
    f = torch.full((m, perm.shape[0], n + 1), INF, device=d.device)
    f[:, :, 0] = 0.0
    for j in range(1, n + 1):
        best = torch.full((m, perm.shape[0]), INF, device=d.device)
        for i in range(j):                      # 这一条回路覆盖次序上的第 i..j-1 个点
            load = dcum[:, :, j] - dcum[:, :, i]
            seg = d0[:, :, i] + (inner[:, :, j - 1] - inner[:, :, i]) + d0[:, :, j - 1]
            v = torch.where(load <= CAP + 1e-6, f[:, :, i] + seg, torch.full_like(seg, INF))
            best = torch.minimum(best, v)
        f[:, :, j] = best
    return f[:, :, n].amin(1)


def lower_bound(d):
    """可证明的下界：每个客户两条最便宜的邻边之半求和。它**不可能超过最优值**。"""
    big = torch.eye(d.shape[1], device=d.device) * 1e9
    two = (d + big).topk(2, dim=2, largest=False).values               # (m, n+1, 2)
    return (two[:, 1:, :].sum(-1) / 2.0).sum(-1)


def min_trips(dem):
    """装箱下界：总需求除以载重向上取整——趟数不可能比这个少。"""
    return torch.ceil(dem.sum(1) / CAP - 1e-9).to(torch.long)


t0 = time.perf_counter()
rows = []
for n in EXACT:
    xy, dem, d = instances(n, M_SMALL, 13 * n)
    gc, gt = greedy(d, dem)
    oc = optimal(d, dem, n)
    lb = lower_bound(d)
    assert bool((lb <= oc + 1e-4).all()), "下界不可能超过最优值，超了说明下界写错了"
    assert bool((gc >= oc - 1e-4).all()), "贪心不可能比穷举出来的最优解更好"
    rows.append({"n": n,
                 "g_opt": float((gc / oc).mean()),
                 "g_lb": float((gc / lb).mean()),
                 "o_lb": float((oc / lb).mean()),
                 "worst": float((gc / oc).max()),
                 "extra": float((gt - min_trips(dem)).float().mean())})
exact_s = time.perf_counter() - t0
print("客户数   贪心/已证明最优   贪心/下界   最优/下界（下界有多松）   最差的那个实例")
for r in rows:
    print(f"{r['n']:>5}        {r['g_opt']:7.3f}       {r['g_lb']:7.3f}      "
          f"{r['o_lb']:7.3f}                {r['worst']:7.3f}")
print(f"穷举 {len(EXACT)} 档规模、每档 {M_SMALL} 个实例，用了 {exact_s:.1f} 秒")

# %% [markdown]
# ## 4. 同一批实例，两种比法差多少（任务 4）
# 第二列总是不小于第一列（下界比最优小），两列之差就是**只看下界会夸大多少个百分点**。
# 第三列（最优/下界）直接量出这个下界有多松——**下界松，不等于解差**。
# %%
top = rows[-1]
lb_overstates_pts = (top["g_lb"] - top["g_opt"]) * 100
print(f"{top['n']} 个点：贪心比**已证明最优**贵 {(top['g_opt'] - 1) * 100:.1f}%，"
      f"而跟下界比是 {(top['g_lb'] - 1) * 100:.1f}%")
print(f"  → 只看下界，差距被**夸大了 {lb_overstates_pts:.0f} 个百分点**；"
      f"原因在第三列：最优值本来就是下界的 {top['o_lb']:.2f} 倍")
print(f"  最小规模（{rows[0]['n']} 个点）那一档：{rows[0]['g_opt']:.3f} 对 {rows[0]['g_lb']:.3f}，"
      f"夸大 {(rows[0]['g_lb'] - rows[0]['g_opt']) * 100:.0f} 个百分点")
assert all(r["g_lb"] >= r["g_opt"] - 1e-9 for r in rows), \
    "下界比最优小，所以“对下界的比值”必然不小于“对最优的比值”"
print("\n**这两列不是一回事**：第一列是真实差距，第二列是“差距不超过多少”的上界说法。")

# %% [markdown]
# ## 5. 穷举不了的规模：只剩下界这一列（任务 5）
# 从几十个点一路到几百个点。这一段**没有最优解**，所以每一行只能说一句话：
# “在这个下界的意义下，差距不超过这么多。”
# %%
t0 = time.perf_counter()
big_rows = []
for n in BIG:
    xy, dem, d = instances(n, M_BIG, 13 * n + 1)
    gc, gt = greedy(d, dem)
    lb = lower_bound(d)
    big_rows.append({"n": n, "g_lb": float((gc / lb).mean()),
                     "extra": float((gt - min_trips(dem)).float().mean()),
                     "trips": float(gt.float().mean())})
big_s = time.perf_counter() - t0
print("客户数   贪心/下界   平均趟数   比装箱下界多用的趟数")
for r in big_rows:
    print(f"{r['n']:>5}      {r['g_lb']:7.3f}   {r['trips']:8.2f}        {r['extra']:+6.2f}")
print(f"大规模扫了 {len(BIG)} 档、每档 {M_BIG} 个实例，用了 {big_s:.1f} 秒")
slope = float(np.polyfit([r["n"] for r in big_rows], [r["g_lb"] for r in big_rows], 1)[0])
print(f"\n“贪心/下界”随规模的斜率 {slope:+.5f}/点，到 {BIG[-1]} 个点已经 "
      f"{big_rows[-1]['g_lb']:.2f}")
print("**但不能由此说“贪心在大规模上差了这么多”**：这里面有多少是贪心变差、"
      "有多少是下界变松，手上没有最优解就分不开。")

# %% [markdown]
# ## 6. 画出来：哪一段是真值，哪一段只是上界说法（任务 6）
# 两条曲线画在同一张图上。左边那一段有最优解（实线），右边那一段只有下界（虚线）——
# 图上一定要把这条界线标出来，不然读图的人会把两段当成一回事。
# %%
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=120)
    ax.plot([r["n"] for r in rows], [r["g_opt"] for r in rows], "o-",
            label="greedy / proven optimum (ground truth)")
    ax.plot([r["n"] for r in rows] + [r["n"] for r in big_rows],
            [r["g_lb"] for r in rows] + [r["g_lb"] for r in big_rows], "s--",
            label="greedy / lower bound (upper-bound statement)")
    ax.axvline(EXACT[-1] + 0.5, color="grey", lw=1)
    ax.text(EXACT[-1] + 0.8, 1.02, "no optimum beyond here", fontsize=9, color="grey")
    ax.set_xscale("log")
    ax.set_xlabel("customers")
    ax.set_ylabel("ratio")
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig("ratio_vs_size.png")
    print("图已存成 ratio_vs_size.png：左段是真值，右段只是上界说法")
except Exception as e:                       # noqa: BLE001  画不出来也不耽误交结果
    print(f"没画图（{type(e).__name__}）：把两张表抄进报告也一样")
    for r in rows:
        print(f"  n={r['n']:>3}  贪心/最优 {r['g_opt']:.3f}  贪心/下界 {r['g_lb']:.3f}")
    for r in big_rows:
        print(f"  n={r['n']:>3}  贪心/最优 —（穷举不了）  贪心/下界 {r['g_lb']:.3f}")

# %% [markdown]
# ## 回传结果
# %%
wqgpu.submit(n_instances_small=M_SMALL * len(EXACT),
             n_exact_max=EXACT[-1],
             ratio_greedy_opt=top["g_opt"],
             ratio_greedy_lb=top["g_lb"],
             ratio_opt_lb=top["o_lb"],
             lb_overstates_pts=lb_overstates_pts,
             n_big_max=BIG[-1],
             ratio_greedy_lb_big=big_rows[-1]["g_lb"],
             extra_vehicles_big=big_rows[-1]["extra"],
             wall_s=exact_s + big_s)
