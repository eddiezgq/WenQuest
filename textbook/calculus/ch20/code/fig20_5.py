"""图 20.5.1：左：液压油缸壁内的径向与周向应力（拉梅公式）；右：欧拉方程三类解的样子。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.9))
a, b, p = 20.0, 25.0, 10.0
C1, C2 = p * a * a / (b * b - a * a), p * a * a * b * b / (b * b - a * a)
r = np.linspace(a, b, 200)
a1.plot(r, C1 + C2 / r ** 2, color=RED, lw=2.4, label=T("周向应力 σ_θ", "hoop stress σ_θ"))
a1.plot(r, C1 - C2 / r ** 2, color=BLUE, lw=2.4, label=T("径向应力 σ_r", "radial stress σ_r"))
a1.axhline(p * a / (b - a), color=MUTED, ls="--", lw=1)
a1.text(20.2, 41, T("薄壁公式 pa/t", "thin-wall pa/t"), fontsize=9, color=MUTED)
a1.set_xlabel(T("半径 r / mm", "radius r / mm"))
a1.set_ylabel(T("应力 / MPa", "stress / MPa"))
a1.set_title(T("油缸壁内的应力（内压 10 MPa）", "Stress in the cylinder wall (10 MPa inside)"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="center right")
clean(a1)
x = np.linspace(0.02, 2.5, 800)
a2.plot(x, x * x - x, color=BLUE, lw=2, label=T("x² − x（实根 1、2）", "x² − x (roots 1, 2)"))
a2.plot(x, x * np.log(x), color=GREEN, lw=2, label=T("x ln x（重根 1）", "x ln x (double root 1)"))
a2.plot(x, np.cos(2 * np.log(x)), color=RED, lw=1.5, label=T("cos(2 ln x)（复根 ±2i）", "cos(2 ln x) (roots ±2i)"))
a2.set_ylim(-1.5, 2.5)
a2.set_xlabel("x")
a2.set_title(T("欧拉方程的三类解", "Three kinds of solutions of Euler equations"), fontsize=10)
a2.legend(fontsize=9, frameon=False, loc="upper left")
clean(a2)
fig.tight_layout()
figure(fig, "fig20_5_1")
