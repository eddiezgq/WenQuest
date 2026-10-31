"""图 14.1.1：左：分部积分的几何意义——曲线 (u, v) 下方与左方的两块面积之和等于两个矩形面积之差 uv|；
右：一阶系统的误差 e = e^{−t/τ}（τ = 0.1 s）及 e²、t·e，曲线下的面积分别是 IAE、ISE、ITAE。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4))
s = np.linspace(0, 1, 300)
u = 1 + 2 * s
v = 0.6 + 1.6 * s ** 2
a1.plot(u, v, color=INK, lw=2.2)
a1.fill_between(u, 0, v, color=BLUE, alpha=0.25)
a1.fill_betweenx(v, 0, u, color=RED, alpha=0.2)
a1.plot([u[0], u[0]], [0, v[0]], color=MUTED, lw=0.8, ls="--")
a1.plot([0, u[0]], [v[0], v[0]], color=MUTED, lw=0.8, ls="--")
a1.plot([u[-1], u[-1]], [0, v[-1]], color=MUTED, lw=0.8, ls="--")
a1.plot([0, u[-1]], [v[-1], v[-1]], color=MUTED, lw=0.8, ls="--")
a1.text(2.1, 0.5, r"$\int v\,du$", color=BLUE, fontsize=14)
a1.text(0.6, 1.55, r"$\int u\,dv$", color=RED, fontsize=14)
a1.set_xlabel("u")
a1.set_ylabel("v")
a1.set_xlim(0, 3.4)
a1.set_ylim(0, 2.5)
a1.set_title(T("两块面积之和 = u₁v₁ − u₀v₀", "Sum of the two areas = u₁v₁ − u₀v₀"), fontsize=10)
clean(a1, zero=False)
tau = 0.1
t = np.linspace(0, 0.6, 400)
e = np.exp(-t / tau)
a2.plot(t, e, color=BLUE, lw=2, label="e(t)")
a2.plot(t, e ** 2, color=GREEN, lw=2, label="e²(t)")
a2.plot(t, t * e / tau, color=RED, lw=2, label="t·e(t)/τ")
a2.fill_between(t, 0, t * e / tau, color=RED, alpha=0.12)
a2.set_xlabel("t / s")
a2.legend(fontsize=9, frameon=False)
a2.set_title(T("IAE = τ，ISE = τ/2，ITAE = τ²（e₀ = 1）", "IAE = τ, ISE = τ/2, ITAE = τ² (e₀ = 1)"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig14_1_1")
