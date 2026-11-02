"""图 21.5.1：左：捕食者–猎物方程的相图（守恒量 H 的等值线）；右：范德波尔振子（μ = 1）的极限环。"""
import numpy as np
from scipy.integrate import solve_ivp

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

a, b, c, d = 1.0, 0.1, 1.5, 0.075
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
for x0, col in ((18, GREEN), (14, BLUE), (10, ACC), (6, RED)):
    s = solve_ivp(lambda t, z: [a * z[0] - b * z[0] * z[1], -c * z[1] + d * z[0] * z[1]], (0, 12), [x0, 10.0], max_step=0.01, rtol=1e-9)
    a1.plot(s.y[0], s.y[1], color=col, lw=1.6)
a1.plot(c / d, a / b, "o", color=INK)
a1.annotate("", xy=(30, 4.0), xytext=(22, 3.2), arrowprops=dict(arrowstyle="->", color=MUTED))
a1.set_xlabel(T("猎物 x", "prey x"))
a1.set_ylabel(T("捕食者 y", "predators y"))
a1.set_title(T("捕食者–猎物：围绕平衡点 (20, 10) 的闭轨", "Predator–prey: closed orbits around (20, 10)"), fontsize=10)
clean(a1, zero=False)
vdp = lambda t, z: [z[1], (1 - z[0] ** 2) * z[1] - z[0]]
for z0, col in (((0.1, 0), BLUE), ((4, 0), RED)):
    s = solve_ivp(vdp, (0, 30), z0, max_step=0.01, rtol=1e-9)
    a2.plot(s.y[0], s.y[1], color=col, lw=1.3)
    a2.plot(*z0, "o", color=col)
s = solve_ivp(vdp, (0, 60), (2, 0), max_step=0.01, rtol=1e-10)
tail = s.t > 45
a2.plot(s.y[0][tail], s.y[1][tail], color=INK, lw=2.5)
a2.set_xlabel("x")
a2.set_ylabel("ẋ")
a2.set_title(T("范德波尔振子：里外的轨线都趋于极限环（黑）", "Van der Pol: orbits from inside and outside approach the limit cycle"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig21_5_1")
