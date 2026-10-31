"""图 14.4.1：无人机停止水平推进后滑行（m = 1.5 kg，v₀ = 10 m/s）：只有线性阻力、只有二次阻力、两者都有时的速度与距离。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

m, c1, c2, v0 = 1.5, 0.3, 0.05, 10.0
t = np.linspace(0, 15, 600)
v_lin = v0 * np.exp(-c1 / m * t)
v_quad = 1 / (1 / v0 + c2 / m * t)
k = c1 / m
v_both = c1 * v0 * np.exp(-k * t) / (c1 + c2 * v0 * (1 - np.exp(-k * t)))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
for v, c, lab in ((v_lin, BLUE, T("只有线性阻力", "linear drag only")), (v_quad, GREEN, T("只有二次阻力", "quadratic drag only")),
                  (v_both, RED, T("两者都有", "both"))):
    a1.plot(t, v, color=c, lw=2, label=lab)
    x = np.concatenate([[0], np.cumsum((v[1:] + v[:-1]) / 2 * np.diff(t))])
    a2.plot(t, x, color=c, lw=2, label=lab)
a1.set_xlabel("t / s")
a1.set_ylabel("v / (m/s)")
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("高速时二次阻力为主，低速时线性阻力为主", "Quadratic drag dominates fast, linear slow"), fontsize=10)
clean(a1, zero=False)
a2.set_xlabel("t / s")
a2.set_ylabel("x / m")
a2.set_title(T("滑行距离", "Coasting distance"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig14_4_1")
