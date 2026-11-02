"""图 23.1.1：左：零件从 0.2 m 落下弹跳（e = 0.6），落地时刻累积成几何级数的部分和，趋于 0.81 s；右：几何级数 Σrᵏ 的部分和。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

g, h0, e = 9.81, 0.2, 0.6
t0 = math.sqrt(2 * h0 / g)
Ttot = t0 * (1 + e) / (1 - e)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
ts = np.linspace(0, t0, 100)
a1.plot(ts, (h0 - 0.5 * g * ts ** 2) * 1000, color=BLUE, lw=2)
land = [t0]
v = g * t0
for k in range(1, 14):
    v *= e
    tf = 2 * v / g
    tt = np.linspace(0, tf, 80)
    a1.plot(land[-1] + tt, (v * tt - 0.5 * g * tt ** 2) * 1000, color=BLUE, lw=2)
    land.append(land[-1] + tf)
a1.plot(land[:9], [0] * 9, "o", color=RED, ms=5, label=T("落地时刻（部分和）", "landing times (partial sums)"))
a1.axvline(Ttot, color=RED, ls="--", lw=1.2)
a1.text(Ttot + 0.01, 150, T(f"总时间 {Ttot:.2f} s", f"total {Ttot:.2f} s"), color=RED, fontsize=9)
a1.set_xlabel(T("时间 t / s", "time t / s")); a1.set_ylabel(T("零件高度 / mm", "part height / mm"))
a1.set_title(T("零件弹跳无穷多次，却在有限时间内停下", "Infinitely many bounces, yet it stops in finite time"), fontsize=10)
a1.legend(fontsize=9, frameon=False); clean(a1)
n = np.arange(0, 21)
for r, col in ((0.6, BLUE), (-0.6, GREEN), (0.9, ACC), (1.05, RED)):
    S = np.cumsum(r ** n)
    a2.plot(n, S, "o-", color=col, ms=3.5, lw=1.4, label=f"r = {r}")
    if abs(r) < 1:
        a2.axhline(1 / (1 - r), color=col, ls=":", lw=1)
a2.set_ylim(0, 12)
a2.set_xlabel(T("项数 n", "number of terms n")); a2.set_ylabel(T("部分和 Sₙ", "partial sum Sₙ"))
a2.set_title(T("几何级数：|r| < 1 收敛到 1/(1 − r)", "Geometric series: converges to 1/(1 − r) when |r| < 1"), fontsize=10)
a2.legend(fontsize=9, frameon=False, loc="upper left"); clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig23_1_1")
