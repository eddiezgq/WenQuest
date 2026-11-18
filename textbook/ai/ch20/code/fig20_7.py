"""20.5 节的图：闭环要试多少次，以及什么会把闭环带进沟里。

图 20.7.1：（a）三种提议策略在同一个响应面上的遗憾随预算下降的样子；
（b）系统偏差扫描——偏差小的时候闭环照样找得到，**过了一个门槛就整段跑偏**，
而且方向相反的同样大小的偏差后果完全不同。遗憾一律按**真值**算，不按闭环自己报的分数算。
"""
import numpy as np

from _ch20 import closed_loop, response_surface
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
SEEDS = range(8)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 三种策略
budgets = [8, 12, 16, 24, 32, 48, 64]
for strat, col, name in (("grid", C["muted"], T("网格挨个试", "grid")),
                         ("random", C["y"], T("随机试", "random")),
                         ("bayes", C["x"], T("代理模型挑（上置信界）", "surrogate / UCB"))):
    med = []
    for n in budgets:
        rs = [closed_loop(strat, n, seed=s)["regret"] for s in SEEDS]
        med.append(float(np.median(rs)))
    a.semilogy(budgets, med, "o-", color=col, lw=2.0, ms=5, label=name)
a.set_xlabel(T("预算（一共做多少次实验）", "budget (number of experiments)"))
a.set_ylabel(T("遗憾：最好的真值减去选出来那个的真值",
               "regret: best truth minus truth of the pick"))
a.set_title(T("(a) 没有噪声没有偏差时，策略只影响要试多少次",
              "(a) with clean measurements, strategy sets the sample count"), fontsize=10)
a.legend(fontsize=8, loc="upper right", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5)

r_grid = float(np.median([closed_loop("grid", 24, seed=s)["regret"] for s in SEEDS]))
r_bayes = float(np.median([closed_loop("bayes", 24, seed=s)["regret"] for s in SEEDS]))
a.annotate(T(f"同样 24 次：网格 {r_grid:.3f}，代理模型 {r_bayes:.3f}",
             f"24 experiments: grid {r_grid:.3f}, surrogate {r_bayes:.3f}"),
           xy=(0.5, 0.07), xycoords="axes fraction", ha="center",
           fontsize=8.5, color=C["accent"])

# ---------------- (b) 系统偏差扫描（两个方向）
biases = np.round(np.arange(-1.2, 1.21, 0.1), 2)
med, believed, truth_best = [], [], response_surface(np.array([0.72]), np.array([0.35]))[0]
for bias in biases:
    rs = [closed_loop("bayes", 32, noise=0.02, bias=float(bias), seed=s) for s in SEEDS]
    med.append(float(np.median([r["regret"] for r in rs])))
    believed.append(float(np.median([r["believed"] for r in rs])))
med = np.array(med)
b.plot(biases, med, "o-", color=C["x"], lw=2.0, ms=4,
       label=T("按真值算的遗憾", "regret measured against the truth"))
b.plot(biases, np.array(believed) - truth_best, "s--", color=C["z"], lw=1.8, ms=4,
       label=T("闭环自己报的分数减去真正的最优", "self-reported score minus true optimum"))
b.axhline(0.0, color=C["muted"], ls=":", lw=1.0)

# 门槛：遗憾第一次超过"无偏差时的 3 倍"
base = float(np.median(med[np.abs(biases) < 0.05]))
pos = [bb for bb, m in zip(biases, med) if bb > 0 and m > 3 * max(base, 1e-6)]
neg = [bb for bb, m in zip(biases, med) if bb < 0 and m > 3 * max(base, 1e-6)]
if pos:
    b.axvline(min(pos), color=C["accent"], ls="--", lw=1.4)
    b.annotate(T(f"往这个方向，偏差到 {min(pos):+.1f} 才开始塌",
                 f"breaks down at {min(pos):+.1f}"),
               xy=(min(pos), med.max() * 0.55), xytext=(6, 0), textcoords="offset points",
               fontsize=8.5, color=C["accent"])
if neg:
    b.axvline(max(neg), color=C["y"], ls="--", lw=1.4)
    b.annotate(T(f"反方向是 {max(neg):+.1f}——同样大小，后果不同",
                 f"the other direction: {max(neg):+.1f}"),
               xy=(max(neg), med.max() * 0.8), xytext=(-6, 0), textcoords="offset points",
               ha="right", fontsize=8.5, color=C["y"])
b.set_ylim(-0.2, 0.36)
r_worst = float(med.max())
b_worst = float(biases[int(np.argmax(med))])
b.annotate(T(f"往负方向：偏差 {b_worst:+.1f} 时遗憾 {r_worst:.2f}，"
             f"是无偏差时的 {r_worst / max(base, 1e-9):.0f} 倍",
             f"regret {r_worst:.2f} at bias {b_worst:+.1f}"),
           xy=(0.98, 0.955), xycoords="axes fraction", ha="right",
           fontsize=8.5, color=C["x"])
b.set_xlabel(T("系统偏差的大小与方向（随成分漂移）",
               "systematic bias (drifts with composition)"))
b.set_ylabel(T("遗憾 / 自报分数的虚高", "regret / inflation of the self-reported score"))
b.set_title(T("(b) 偏差是个门槛现象，而且分方向",
              "(b) bias is a threshold effect, and direction matters"), fontsize=10)
b.annotate(T("两条线一起看才是要点：偏差越大，闭环自己报的分数越高，"
             "\n而它选出来的东西越差：自报的分数不能当成绩",
             "the self-reported score rises while the pick gets worse"),
           xy=(0.5, 0.045), xycoords="axes fraction", ha="center",
           fontsize=8.5, color=C["accent"])
b.legend(fontsize=8, loc="center right", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig20_7_1")
