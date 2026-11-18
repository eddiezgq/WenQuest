"""21.5 节的图：控制限不是规格限。

图 21.5.1：（a）一张均值图——控制限（过程自己的波动算出来的）与规格限（图纸给的）
画在一起，宽窄完全是两回事；（b）要多久才发现过程变了：均值漂移 vs 方差变大。
"""
import numpy as np

from _ch21 import A2, D2, alarms, capability, run_chart, xbar_limits
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N_SUB = 5
LSL, USL = -3.0, 3.0

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 一张均值图
g = run_chart(140, N_SUB, shift_at=90, shift=1.1, seed=5)
lim = xbar_limits(g[:60], A2[N_SUB])
means = g.mean(axis=1)
k = np.arange(len(means))
a.plot(k, means, "-o", color=C["z"], lw=1.2, ms=3.2)
fired = alarms(g, lim)
a.plot(k[fired], means[fired], "o", color=C["x"], ms=7, zorder=3,
       label=T("报警的子组", "alarms"))
a.axhline(lim["center"], color=C["ink"], lw=1.2)
for y, name in ((lim["ucl"], T("控制上限", "upper control limit")),
                (lim["lcl"], T("控制下限", "lower control limit"))):
    a.axhline(y, color=C["accent"], ls="--", lw=1.6)
    a.annotate(name, xy=(len(means) - 1, y), xytext=(-4, 4),
               textcoords="offset points", ha="right", fontsize=8, color=C["accent"])
for y, name in ((USL, T("规格上限（图纸）", "upper spec limit (drawing)")),
                (LSL, T("规格下限（图纸）", "lower spec limit (drawing)"))):
    a.axhline(y, color=C["muted"], ls=":", lw=1.6)
    a.annotate(name, xy=(0, y), xytext=(4, 4), textcoords="offset points",
               fontsize=8, color=C["muted"])
a.axvline(89.5, color=C["y"], lw=1.4)
a.annotate(T("这里过程真的变了（均值漂移 1.1σ）", "the process really shifts here"),
           xy=(89.5, LSL * 0.8), xytext=(6, 0), textcoords="offset points",
           fontsize=8.5, color=C["y"])
a.set_xlabel(T("第几个子组", "subgroup index"))
a.set_ylabel(T("子组均值", "subgroup mean"))
a.set_ylim(LSL * 1.25, USL * 1.25)
a.set_title(T("(a) 控制限管“过程有没有变”，规格限管“做得出合格品吗”",
              "(a) control limits watch the process; spec limits judge the part"),
            fontsize=10)
a.legend(fontsize=8, loc="upper left", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5)

sigma_hat = lim["rbar"] / D2[N_SUB]
cap = capability(0.0, sigma_hat, LSL, USL)
a.annotate(T(f"控制限宽 {lim['ucl'] - lim['lcl']:.2f}，规格限宽 {USL - LSL:.1f}"
             f"（Cp {cap['cp']:.2f}）——两者没有固定比例",
             f"control width {lim['ucl'] - lim['lcl']:.2f} vs spec width {USL - LSL:.1f}"),
           xy=(0.5, 0.045), xycoords="axes fraction", ha="center",
           fontsize=8.5, color=C["ink"])

# ---------------- (b) 多久才发现
shifts = [0.5, 0.75, 1.0, 1.5, 2.0]
arl_shift = []
for sh in shifts:
    det = []
    for sd in range(200):
        gg = run_chart(160, N_SUB, shift_at=60, shift=sh, seed=1000 + sd)
        li = xbar_limits(gg[:50], A2[N_SUB])
        idx = np.nonzero(alarms(gg, li)[60:])[0]
        det.append(int(idx[0]) + 1 if len(idx) else 100)
    arl_shift.append(float(np.median(det)))
spreads = [1.25, 1.5, 1.75, 2.0]
arl_spread = []
for sp in spreads:
    det = []
    for sd in range(200):
        gg = run_chart(160, N_SUB, shift_at=60, shift=0.0, spread=sp, seed=2000 + sd)
        li = xbar_limits(gg[:50], A2[N_SUB])
        idx = np.nonzero(alarms(gg, li)[60:])[0]
        det.append(int(idx[0]) + 1 if len(idx) else 100)
    arl_spread.append(float(np.median(det)))

b.semilogy(shifts, arl_shift, "o-", color=C["x"], lw=2.2, ms=5,
           label=T("均值漂移（横轴 = 漂移几个 σ）", "mean shift (in σ)"))
b.semilogy([(s - 1) * 2 for s in spreads], arl_spread, "s--", color=C["z"], lw=2.0, ms=5,
           label=T("方差变大（横轴 = (倍数−1)×2，便于并排看）",
                   "variance increase (rescaled to share the axis)"))
b.set_xlabel(T("过程变了多少（两条线的横轴口径不同，见图例）",
               "size of the change (note the two different scales)"))
b.set_ylabel(T("中位要多少个子组才报警（对数轴）",
               "median subgroups until an alarm (log scale)"))
b.set_title(T("(b) 均值图抓均值漂移快，抓方差变化慢",
              "(b) the mean chart is fast on shifts, slow on spread"), fontsize=10)
b.annotate(T(f"1σ 漂移要 {arl_shift[2]:.0f} 个子组；\n"
             f"方差变 1.5 倍要 {arl_spread[1]:.0f} 个，所以要配极差图",
             f"1σ shift: {arl_shift[2]:.0f} subgroups; 1.5× variance: {arl_spread[1]:.0f}"),
           xy=(0.45, 0.78), xycoords="axes fraction", ha="left",
           fontsize=8.5, color=C["accent"])
b.legend(fontsize=8, loc="lower left", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig21_5_1")
