"""图 20.1.1：左：悬臂铝管在末端负载下的挠度曲线（放大显示）；右：单摆周期与小摆幅周期之比随摆幅的变化。"""
import numpy as np
from scipy import special

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8))
E, ro, ri, L, F = 70e9, 0.045, 0.041, 0.425, 5 * 9.81
I = np.pi / 4 * (ro ** 4 - ri ** 4)
x = np.linspace(0, L, 200)
y = F * (L * x ** 2 / 2 - x ** 3 / 6) / (E * I)
a1.plot(x, -y * 1e6, color=BLUE, lw=2.4)
a1.plot([0, L], [0, 0], color=MUTED, ls="--", lw=1)
a1.plot([0, 0], [-25, 5], color=INK, lw=4)
a1.annotate("F = 49 N", (L, -y[-1] * 1e6), xytext=(L - 0.08, -24), fontsize=9, color=RED, arrowprops=dict(arrowstyle="->", color=RED))
a1.set_xlabel(T("离肩关节的距离 x / m", "distance from the shoulder x / m"))
a1.set_ylabel(T("挠度 / μm（向下为负）", "deflection / μm (down negative)"))
a1.set_title(T("悬臂铝管：末端挠度约 18 μm", "Cantilevered tube: tip deflection about 18 μm"), fontsize=10)
clean(a1)
th = np.linspace(0.5, 175, 400)
r = 2 / np.pi * special.ellipk(np.sin(np.radians(th) / 2) ** 2)
a2.plot(th, r, color=BLUE, lw=2, label=T("精确：(2/π)K(sin(θ₀/2))", "exact: (2/π)K(sin(θ₀/2))"))
a2.plot(th, 1 + np.radians(th) ** 2 / 16, color=ACC, ls="--", lw=1.5, label=T("近似：1 + θ₀²/16", "approx.: 1 + θ₀²/16"))
a2.axhline(1, color=MUTED, ls=":", lw=1)
a2.set_ylim(0.9, 3)
a2.set_xlabel(T("摆幅 θ₀ / °", "amplitude θ₀ / °"))
a2.set_ylabel("T / T₀")
a2.set_title(T("单摆：周期随摆幅增大", "Pendulum: the period grows with amplitude"), fontsize=10)
a2.legend(fontsize=9, frameon=False, loc="upper left")
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig20_1_1")
