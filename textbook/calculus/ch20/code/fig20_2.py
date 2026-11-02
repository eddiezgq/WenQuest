"""图 20.2.1：起重机器人收绳时货物的摆角（绳长 4 m 匀速收到 1 m）；两个解的朗斯基行列式与阿贝尔公式。"""
import numpy as np
from scipy.integrate import solve_ivp

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

g, l0, v, Tt = 9.81, 4.0, 0.3, 10.0
l = lambda t: l0 - v * t
rhs = lambda t, z: [z[1], -(-2 * v * z[1] + g * z[0]) / l(t)]
ts = np.linspace(0, Tt, 3000)
s1 = solve_ivp(rhs, (0, Tt), [1.0, 0.0], t_eval=ts, rtol=1e-10, atol=1e-12)
s2 = solve_ivp(rhs, (0, Tt), [0.0, 1.0], t_eval=ts, rtol=1e-10, atol=1e-12)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8))
a1.plot(ts, 0.05 * s1.y[0], color=BLUE, lw=1.6)
b = a1.twinx()
b.plot(ts, l(ts), color=MUTED, ls="--", lw=1)
b.set_ylabel(T("绳长 l / m（虚线）", "rope length l / m (dashed)"), color=MUTED, fontsize=9)
b.spines["top"].set_visible(False)
a1.set_xlabel(T("时间 t / s", "time t / s"))
a1.set_ylabel(T("摆角 θ / rad", "swing angle θ / rad"))
a1.set_title(T("收绳时摆动越来越快、越来越大", "Reeling in: the swing gets faster and larger"), fontsize=10)
clean(a1)
W = s1.y[0] * s2.y[1] - s1.y[1] * s2.y[0]
a2.plot(ts, W, color=BLUE, lw=2.5, label=T("数值解的 W(t)", "W(t) from numerical solutions"))
a2.plot(ts[::150], (l0 / l(ts[::150])) ** 2, "o", color=RED, ms=4, label=T("阿贝尔公式 (l₀/l)²", "Abel's formula (l₀/l)²"))
a2.set_xlabel(T("时间 t / s", "time t / s"))
a2.set_ylabel(T("朗斯基行列式 W", "Wronskian W"))
a2.set_title(T("朗斯基行列式：不解方程也能预言", "The Wronskian, predicted without solving"), fontsize=10)
a2.legend(fontsize=9, frameon=False)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig20_2_1")
