"""19.3 节的示意图：概率预报好不好，要用两把尺子量。

图 19.3.1：（a）可靠性图——"说 70% 的那些次是不是真有七成发生了"；
（b）离散度扫一遍——CRPS 同时罚"太自信"和"太含糊"。
"""
import numpy as np

from _ch19 import brier, crps_ensemble, make_ensemble, reliability, spread_skill
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
M, N, THRESH = 50, 4000, 1.0

fig, (a, b) = plt.subplots(1, 2, figsize=(11.0, 4.5))

# ---------------- (a) 可靠性图
a.plot([0, 1], [0, 1], "--", color=C["ink"], lw=1.2,
       label=T("完全可靠（45° 线）", "perfectly reliable (45° line)"))
for sf, col, name in ((1.0, C["z"], T("校准良好的集合", "well-calibrated ensemble")),
                      (0.5, C["x"], T("离散度不足（太自信）", "under-dispersed (over-confident)"))):
    mem, obs = make_ensemble(M, N, seed=1, spread_factor=sf)
    prob, occ = (mem > THRESH).mean(0), obs > THRESH
    rows = [(c, f, n) for c, f, n in reliability(prob, occ) if n > 30 and not np.isnan(f)]
    a.plot([c for c, _, _ in rows], [f for _, f, _ in rows], "o-", color=col, lw=2.0,
           ms=5, label=f"{name}  Brier {brier(prob, occ):.3f}")
a.annotate(T("在对角线下方：\n说得太满，实际没那么常发生",
             "below the line:\nclaims more than actually happens"),
           xy=(0.78, 0.60), xytext=(0.30, 0.74), fontsize=8.5, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.0))
a.annotate(T("在对角线上方：\n说得太保守", "above the line:\ntoo conservative"),
           xy=(0.18, 0.33), xytext=(0.30, 0.12), fontsize=8.5, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.0))
a.set_xlabel(T("预报说的概率", "forecast probability"))
a.set_ylabel(T("这一档里实际发生的频率", "observed frequency in that bin"))
a.set_xlim(0, 1); a.set_ylim(0, 1)
a.set_aspect("equal")
a.set_title(T("(a) 可靠性图：概率说得老实不老实",
              "(a) Reliability: is the stated probability honest?"), fontsize=10)
a.legend(fontsize=8, loc="upper left")
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 离散度扫一遍
sfs = np.arange(0.35, 1.85, 0.05)
ratios, crpss = [], []
for sf in sfs:
    m2, o2 = make_ensemble(M, N, seed=1, spread_factor=float(sf))
    ratios.append(spread_skill(m2, o2)[2])
    crpss.append(crps_ensemble(m2, o2))
ratios, crpss = np.array(ratios), np.array(crpss)
b.plot(ratios, crpss, "-", color=C["z"], lw=2.2)
best = int(np.argmin(crpss))
b.plot([ratios[best]], [crpss[best]], "o", color=C["accent"], ms=9, mec="white", mew=1.2,
       zorder=5)
b.axvline(1.0, color=C["ink"], ls=":", lw=1.2)
for sf, tag, dx, ha in ((0.5, T("太自信", "over-confident"), 0.07, "left"),
                        (1.4, T("太含糊", "too vague"), -0.07, "right")):
    i = int(np.argmin(np.abs(sfs - sf)))
    b.plot([ratios[i]], [crpss[i]], "o", color=C["x"], ms=6, mec="white", mew=1.0, zorder=5)
    b.annotate(f"{tag}\n{T('离散度/技巧比', 'spread/skill')} {ratios[i]:.2f}\nCRPS {crpss[i]:.4f}",
               xy=(ratios[i], crpss[i]), xytext=(ratios[i] + dx, crpss[i] + 0.004),
               fontsize=8.5, color=C["x"], ha=ha, va="bottom")
b.annotate(T(f"校准最好：比 {ratios[best]:.2f}，CRPS {crpss[best]:.4f}",
             f"best calibrated: ratio {ratios[best]:.2f}, CRPS {crpss[best]:.4f}"),
           xy=(ratios[best], crpss[best]), xytext=(ratios[best] - 0.42, crpss[best] + 0.004),
           fontsize=8.5, color=C["accent"], ha="left",
           arrowprops=dict(arrowstyle="->", color=C["accent"], lw=1.0))
b.set_xlabel(T("离散度 / 集合均值 RMSE", "spread / RMSE of the ensemble mean"))
b.set_ylabel(T("CRPS（越小越好）", "CRPS (lower is better)"))
b.set_title(T("(b) 两头都罚：太自信和太含糊都更差",
              "(b) Penalised at both ends: over-confident and too vague"), fontsize=10)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig19_3_1")
