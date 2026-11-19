"""图 24.3.1：动作分箱数的代价。

（a）分箱数对任务成功率：太少掉得厉害，到十几个箱就追平连续动作；
（b）分箱数对动作抖动：单调下降，但**翻倍的收益一次比一次小**。
分箱口径参照资料卡里 RT-1 与 RT-2 的“每维 256 个均匀分箱”。
"""
import numpy as np

from _ch24 import DEGREE, SIM, evaluate, make_policy, sample_starts, sample_targets, train_policy
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
BINS = (2, 4, 8, 16, 32, 64, 128, 256)
N_TEST = 80

W = train_policy(160, rounds=4, seed=0)
pol = (lambda p, w: make_policy(W, DEGREE))
test_poses = sample_targets(N_TEST, seed=11)
test_starts = sample_starts(N_TEST, seed=11, spread=0.25)

base = evaluate(pol, test_poses, test_starts, SIM, seed=7)
res = [evaluate(pol, test_poses, test_starts, SIM, seed=7, bins=b) for b in BINS]
succ = np.array([r["success_pct"] for r in res])
jit = np.array([r["jitter"] for r in res])
xs = np.array(BINS, dtype=float)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 成功率
a.semilogx(xs, succ, "o-", color=C["x"], lw=2.2, ms=7, base=2)
a.axhline(base["success_pct"], color=C["muted"], lw=1.6, ls="--")
a.annotate(T(f"连续动作 {base['success_pct']:.1f}%", f"continuous actions {base['success_pct']:.1f}%"),
           xy=(xs[-1], base["success_pct"]), xytext=(-4, 7), textcoords="offset points",
           ha="right", fontsize=9, color=C["muted"])
a.annotate(T(f"2 个箱：{succ[0]:.0f}%，低 {base['success_pct'] - succ[0]:.0f} 个百分点",
             f"2 bins: {succ[0]:.0f}%, {base['success_pct'] - succ[0]:.0f} points lower"),
           xy=(xs[0], succ[0]), xytext=(24, -12), textcoords="offset points",
           fontsize=9, color=C["x"], arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.2))
i_sat = int(np.argmax(succ >= base["success_pct"] - 3.0))
a.plot(xs[i_sat], succ[i_sat], "o", color=C["x"], ms=13, mfc="none", mew=2)
a.annotate(T(f"{int(BINS[i_sat])} 个箱就追平了", f"{int(BINS[i_sat])} bins already match"),
           xy=(xs[i_sat], succ[i_sat]), xytext=(6, -40), textcoords="offset points",
           fontsize=9, color=C["x"], arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.2))
a.set_xticks(xs)
a.set_xticklabels([str(int(x)) for x in xs], fontsize=9)
a.set_xlabel(T("每维分箱数（均匀分箱）", "bins per action dimension (uniform)"))
a.set_ylabel(T("任务成功率（%，试 80 次）", "task success rate (%, 80 trials)"))
a.set_ylim(0, 104)
a.set_title(T("(a) 分箱太少成功率明显掉，十几个箱之后就不涨了",
              "(a) too few bins hurt; past a dozen bins success stops improving"), fontsize=10)
a.grid(alpha=0.25, lw=0.5, which="both")

# ---------------- (b) 抖动与翻倍的收益
b.loglog(xs, jit, "s-", color=C["z"], lw=2.2, ms=6, base=2,
         label=T("动作抖动（相邻两步之差）", "action jitter (step-to-step change)"))
b.axhline(base["jitter"], color=C["muted"], lw=1.4, ls="--")
b.annotate(T(f"连续动作 {base['jitter']:.3f}", f"continuous {base['jitter']:.3f}"),
           xy=(xs[0], base["jitter"]), xytext=(4, 6), textcoords="offset points",
           ha="left", fontsize=9, color=C["muted"])
gain = -np.diff(jit)
for i in range(len(BINS) - 1):
    b.annotate(f"−{gain[i]:.4f}", xy=(np.sqrt(xs[i] * xs[i + 1]), np.sqrt(jit[i] * jit[i + 1])),
               xytext=(9, 7), textcoords="offset points", fontsize=7.6, color=C["accent"])
b.set_xticks(xs)
b.set_xticklabels([str(int(x)) for x in xs], fontsize=9)
b.set_xlabel(T("每维分箱数（均匀分箱）", "bins per action dimension (uniform)"))
b.set_ylabel(T("动作抖动（无量纲）", "action jitter (dimensionless)"))
b.set_title(T("(b) 抖动一直在降，但每翻一倍省下的越来越少",
              "(b) jitter keeps falling, but each doubling buys less"), fontsize=10)
b.annotate(T(f"2 → 4 省 {gain[0]:.3f}，128 → 256 只省 {gain[-1]:.4f}"
             f"（差 {gain[0] / gain[-1]:.0f} 倍）：\n256 个箱买的不是成功率，是平顺",
             f"2 → 4 saves {gain[0]:.3f}; 128 → 256 only {gain[-1]:.4f} "
             f"({gain[0] / gain[-1]:.0f}× less):\n256 bins buy smoothness, not success"),
           xy=(0.97, 0.55), xycoords="axes fraction", ha="right", va="top",
           fontsize=8.5, color=C["accent"])
b.legend(fontsize=8.5, loc="upper right", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5, which="both")

fig.tight_layout()
figure(fig, "fig24_3_1")
