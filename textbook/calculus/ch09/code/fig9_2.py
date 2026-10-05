"""图 9.2.1：拉格朗日中值定理与区间测速——左：位置 s(t) 与弦（平均速度），两处切线与弦平行；
右：车速 v(t)、平均速度 120 km/h 与限速 100 km/h，中值点 ξ 处 v(ξ) = 平均速度。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

Tm = 7.5
t = np.linspace(0, Tm, 400)
v = 95 + 50 * np.sin(np.pi * t / Tm) ** 2
s = (95 * t + 50 * (t / 2 - Tm * np.sin(2 * np.pi * t / Tm) / (4 * np.pi))) / 60
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
a1.plot(t, s, color=INK, lw=2, label="s(t)")
a1.plot([0, Tm], [0, s[-1]], color=RED, lw=1.5, label=T("弦：平均速度", "chord: average speed"))
for xi in (Tm / 4, 3 * Tm / 4):
    si = (95 * xi + 50 * (xi / 2 - Tm * np.sin(2 * np.pi * xi / Tm) / (4 * np.pi))) / 60
    tt = np.array([xi - 1.3, xi + 1.3])
    a1.plot(tt, si + 2.0 * (tt - xi), color=BLUE, lw=1.2, ls="--")
    a1.plot([xi], [si], "o", color=ACC, ms=6)
    a1.text(xi, si - 1.4, "ξ", ha="center", color=ACC)
a1.set_xlabel(T("时间 t / min", "time t / min"))
a1.set_ylabel(T("位置 s / km", "position s / km"))
a1.set_title(T("切线与弦平行的地方，瞬时速度 = 平均速度", "Where the tangent is parallel to the chord"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="upper left")
clean(a1, zero=False)
a2.plot(t, v, color=INK, lw=2, label="v(t)")
a2.axhline(120, color=RED, lw=1.3, label=T("平均速度 120", "average 120"))
a2.axhline(100, color=GREEN, lw=1.3, ls="--", label=T("限速 100", "limit 100"))
a2.plot([Tm / 4, 3 * Tm / 4], [120, 120], "o", color=ACC, ms=6)
a2.set_xlabel(T("时间 t / min", "time t / min"))
a2.set_ylabel(T("车速 / (km/h)", "speed / (km/h)"))
a2.set_ylim(80, 150)
a2.set_title(T("两端测速点都不超速，区间平均却是 120", "Legal at both cameras, yet averaging 120"), fontsize=10)
a2.legend(fontsize=9, frameon=False, loc="lower center")
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig9_2_1")
