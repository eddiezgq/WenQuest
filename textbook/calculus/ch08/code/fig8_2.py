"""图 8.2.1：线性化——关节重力矩在 θ₀ = 30° 处的线性近似与 1% 误差带；热敏电阻 R(T) 在 50 °C 处的切线。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _traj import ur5e_links

l1, l2 = ur5e_links()
m, g, L = 5, 9.81, l1 + l2
th0 = math.radians(30)
tau = lambda th: m * g * L * np.cos(th)
lin = lambda th: tau(th0) - m * g * L * math.sin(th0) * (th - th0)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
th = np.linspace(math.radians(-10), math.radians(80), 300)
a1.plot(np.degrees(th), tau(th), color=INK, lw=2, label=T("重力矩 τ(θ)", "gravity torque τ(θ)"))
a1.plot(np.degrees(th), lin(th), color=BLUE, lw=1.5, ls="--", label=T("在 30° 处的线性近似", "linearization at 30°"))
ok = np.abs(tau(th) - lin(th)) <= 0.01 * tau(th0)
a1.fill_between(np.degrees(th), 0, 45, where=ok, color=GREEN, alpha=0.12, label=T("误差 ≤ τ₀ 的 1%", "error ≤ 1% of τ₀"))
a1.plot([30], [tau(th0)], "o", color=INK)
a1.set_ylim(0, 45)
a1.set_xlabel(T("关节角 θ / (°)", "joint angle θ / (°)"))
a1.set_ylabel("N·m")
a1.legend(fontsize=8.5, frameon=False, loc="lower left")
clean(a1, zero=False)
R0, B, T0 = 10.0, 3950.0, 298.15
R = lambda T_: R0 * np.exp(B * (1 / T_ - 1 / T0))
tc = np.linspace(20, 90, 300)
Ta = 323.15
a2.plot(tc, R(tc + 273.15), color=INK, lw=2, label=T("R(T)", "R(T)"))
a2.plot(tc, R(Ta) - B / Ta ** 2 * R(Ta) * (tc + 273.15 - Ta), color=RED, lw=1.5, ls="--", label=T("在 50 °C 处的切线", "tangent at 50 °C"))
a2.set_ylim(0, 14)
a2.set_xlabel(T("温度 / °C", "temperature / °C"))
a2.set_ylabel("R / kΩ")
a2.legend(fontsize=9, frameon=False)
a2.set_title(T("NTC 热敏电阻：只在工作点附近近似为直线", "NTC thermistor: nearly straight only near the operating point"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig8_2_1")
