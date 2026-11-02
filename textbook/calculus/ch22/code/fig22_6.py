"""图 22.6.1：左：y′ = x² + y²、y(0) = 0 的皮卡迭代 y₁、y₂、y₃ 与准确解（x = 2.003 附近爆破）；右：格朗沃尔上界 δe^{Lt} 与两条摆动轨线的实际距离。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

xs = np.linspace(0, 1.95, 400)
s = solve_ivp(lambda x, y: [x * x + y[0] ** 2], (0, 1.95), [0.0], t_eval=xs, rtol=1e-10, atol=1e-12)
y1 = xs ** 3 / 3
y2 = y1 + xs ** 7 / 63
y3 = y2 + 2 * xs ** 11 / 2079 + xs ** 15 / 59535
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
a1.plot(xs, s.y[0], color=INK, lw=2.4, label=T("准确解（数值）", "exact (numerical)"))
for yy, col, lab in ((y1, RED, "y₁"), (y2, ACC, "y₂"), (y3, BLUE, "y₃")):
    a1.plot(xs, yy, color=col, lw=1.5, ls="--", label=lab)
a1.axvspan(0, 1 / math.sqrt(2), color=GREEN, alpha=0.1)
a1.text(0.04, 3.2, T("定理保证的区间\n|x| ≤ 1/√2", "interval guaranteed\n|x| ≤ 1/√2"), fontsize=9, color=GREEN)
a1.axvline(2.003, color=MUTED, ls=":", lw=1)
a1.set_ylim(0, 10); a1.set_xlim(0, 2.1)
a1.set_xlabel("x"); a1.set_ylabel("y")
a1.set_title(T("y′ = x² + y² 的皮卡迭代", "Picard iterates for y′ = x² + y²"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="upper left"); clean(a1, zero=False)
m, d, I, g = 8.393, 0.2125, 0.5129, 9.81
c = m * g * d / I
F = lambda t, y: [y[1], -c * math.cos(y[0])]
te = np.linspace(0, 2, 801)
A = solve_ivp(F, (0, 2), [0.0, 0.0], t_eval=te, rtol=1e-12, atol=1e-12).y
B = solve_ivp(F, (0, 2), [1e-3, 0.0], t_eval=te, rtol=1e-12, atol=1e-12).y
a2.semilogy(te, np.linalg.norm(A - B, axis=0), color=BLUE, lw=2, label=T("实际距离 ‖x(t) − x̃(t)‖", "actual distance ‖x(t) − x̃(t)‖"))
a2.semilogy(te, 1e-3 * np.exp(c * te), color=RED, lw=2, ls="--", label=T(f"格朗沃尔上界 δe^(Lt)，L = {c:.1f}", f"Gronwall bound δe^(Lt), L = {c:.1f}"))
a2.set_ylim(1e-4, 1e30)
a2.set_xlabel(T("时间 t / s", "time t / s")); a2.set_ylabel(T("距离", "distance"))
a2.set_title(T("UR5e 上臂，初始角度差 δ = 0.001 rad", "UR5e upper arm, initial angle difference δ = 0.001 rad"), fontsize=10)
a2.legend(fontsize=9, frameon=False, loc="upper left"); clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig22_6_1")
