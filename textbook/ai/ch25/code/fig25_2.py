"""本章第二幅图（`fig25_2_1`）：“对最优的比值”与“对下界的比值”是两条完全不同的线。

图 `fig25_2_1`：（a）同一批车辆路径实例上，贪心解分别对**已证明最优解**与对**下界**的比值；
穷举得动的规模才有前一条线，再往右只剩后一条；
（b）下界本身有多松（最优值是下界的多少倍）——右边那条线越走越高，
有一大半是这个原因，不是贪心变差了。
"""
import numpy as np

from _ch25 import vrp_cost, vrp_greedy, vrp_instance, vrp_lower_bound, vrp_optimal
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
CAP, M = 60.0, 16
EXACT = list(range(3, 9))
BIG = [9, 12, 16, 22, 30]

r_opt, r_lb, tight = [], [], []
for n in EXACT:
    a, b, t = [], [], []
    for s in range(M):
        inst = vrp_instance(n, seed=s * 13 + n, cap=CAP)
        g = vrp_cost(inst, vrp_greedy(inst))
        o, _ = vrp_optimal(inst)
        lb = vrp_lower_bound(inst)
        a.append(g / o)
        b.append(g / lb)
        t.append(o / lb)
    r_opt.append(np.mean(a))
    r_lb.append(np.mean(b))
    tight.append(np.mean(t))

big_lb = []
for n in BIG:
    big_lb.append(np.mean([vrp_cost(inst, vrp_greedy(inst)) / vrp_lower_bound(inst)
                           for inst in (vrp_instance(n, seed=s * 13 + n, cap=CAP)
                                        for s in range(M))]))

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 两条比值线
a.axvspan(EXACT[0] - 0.4, EXACT[-1] + 0.4, color=C["accent"], alpha=0.10)
a.annotate(T("这一段穷举得动\n（有已证明最优解）", "exhaustive here\n(proven optimum)"),
           xy=((EXACT[0] + EXACT[-1]) / 2, 2.95), ha="center", va="top", fontsize=8.5,
           color=C["accent"])
a.plot(EXACT + BIG, r_lb + big_lb, "o-", color=C["z"], lw=2.2, ms=5,
       label=T("贪心 / 下界", "greedy / lower bound"))
a.plot(EXACT, r_opt, "s-", color=C["x"], lw=2.2, ms=5,
       label=T("贪心 / 已证明最优", "greedy / proven optimum"))
a.axhline(1.0, color=C["muted"], lw=1.0, ls=":")
a.annotate(T("1.0 = 跟最优一样好", "1.0 = as good as optimal"), xy=(BIG[-1], 1.0),
           xytext=(-4, 6), textcoords="offset points", ha="right", fontsize=8,
           color=C["muted"])
a.annotate(T(f"{EXACT[-1]} 个点：对最优 +{(r_opt[-1] - 1) * 100:.0f}%，"
             f"对下界 +{(r_lb[-1] - 1) * 100:.0f}%",
             f"n={EXACT[-1]}: +{(r_opt[-1] - 1) * 100:.0f}% vs optimum, "
             f"+{(r_lb[-1] - 1) * 100:.0f}% vs bound"),
           xy=(EXACT[-1], r_lb[-1]), xytext=(18, -26), textcoords="offset points",
           fontsize=8.5, color=C["ink"],
           arrowprops=dict(arrowstyle="->", color=C["ink"], lw=1.0))
a.set_xlabel(T("取送点个数", "number of stops"))
a.set_ylabel(T("贪心解的倍数", "greedy cost ratio"))
a.set_ylim(0.9, 3.9)
a.set_title(T("(a) 同一批解，跟谁比，差距差一倍不止",
              "(a) same solutions: the baseline decides the number"), fontsize=10)
a.legend(fontsize=8.5, loc="upper left", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 下界有多松
b.plot(EXACT, tight, "o-", color=C["y"], lw=2.2, ms=6)
for n, t in zip(EXACT, tight):
    b.annotate(f"{t:.2f}", xy=(n, t), xytext=(0, 8), textcoords="offset points",
               ha="center", fontsize=8, color=C["y"])
b.axhline(1.0, color=C["muted"], lw=1.0, ls=":")
b.annotate(T("1.0 = 下界正好等于最优（那它就是真值了）",
             "1.0 = the bound equals the optimum"), xy=(EXACT[0], 1.0),
           xytext=(0, 6), textcoords="offset points", fontsize=8, color=C["muted"])
b.set_xlabel(T("取送点个数", "number of stops"))
b.set_ylabel(T("已证明最优 / 下界", "proven optimum / lower bound"))
b.set_ylim(0.95, max(tight) + 0.25)
b.set_title(T("(b) 这个下界本身就松：最优值差不多是它的两倍",
              "(b) the bound is loose: the optimum is about twice it"), fontsize=10)
b.annotate(T("所以“对下界差了百分之几十”里，\n有一大半是下界的毛病，不是解的毛病——\n"
             "穷举不动的规模上，这两件事分不开",
             "so most of the gap to the bound is the bound's fault,\n"
             "and beyond the exhaustive range the two cannot be separated"),
           xy=(0.5, 0.30), xycoords="axes fraction", ha="center", va="bottom",
           fontsize=8.5, color=C["accent"])
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig25_2_1")
