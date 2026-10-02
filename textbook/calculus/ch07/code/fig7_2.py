"""图 7.2.2：不可导的四种情形；图 7.2.1：由关节角曲线读出角速度曲线。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _traj import quintic

fig, axs = plt.subplots(1, 4, figsize=(11, 3.0))
x = np.linspace(-1, 1, 801)
cbrt = np.cbrt(x)
cases = [(np.abs(x), T("角点：y = |x|", "corner: y = |x|")),
         (cbrt, T("竖直切线：y = ∛x", "vertical tangent: y = ∛x")),
         (np.cbrt(x**2), T("尖点：y = x^{2/3}", "cusp: y = x^{2/3}").replace("x^{2/3}", "$x^{2/3}$")),
         (np.where(x < 0, -0.5, 0.5), T("间断：跳跃", "discontinuity: a jump"))]
for ax, (y, title) in zip(axs, cases):
    if "跳跃" in title or "jump" in title:
        ax.plot(x[x < 0], y[x < 0], color=INK, lw=2)
        ax.plot(x[x >= 0], y[x >= 0], color=INK, lw=2)
        ax.plot([0], [0.5], "o", color=INK, ms=5)
        ax.plot([0], [-0.5], "o", mfc="white", mec=INK, ms=5)
    else:
        ax.plot(x, y, color=INK, lw=2)
    ax.plot([0], [0] if "跳跃" not in title and "jump" not in title else [0.5], "o", color=RED, ms=5)
    ax.set_title(title, fontsize=11)
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_xticks([-1, 0, 1])
    ax.set_yticks([-1, 0, 1])
    clean(ax)
    ax.axvline(0, color=MUTED, lw=0.6, zorder=0)
axs[1].axvline(0, color=RED, lw=1.2, ls="--")
fig.tight_layout()
figure(fig, "fig7_2_2")

T2, D = 2.0, math.pi / 2
t = np.linspace(0, T2, 400)
th, w, a, j = quintic(t, T2, D)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.4, 5.4), sharex=True)
a1.plot(t, np.degrees(th), color=INK, lw=2)
for tk, c in ((0.5, BLUE), (1.0, RED), (1.6, GREEN)):
    thk, wk = float(quintic(tk, T2, D)[0]), float(quintic(tk, T2, D)[1])
    s = np.array([tk - 0.3, tk + 0.3])
    a1.plot(s, np.degrees(thk + wk * (s - tk)), color=c, lw=1.6)
    a1.plot([tk], [math.degrees(thk)], "o", color=c, ms=5)
    a2.plot([tk], [math.degrees(wk)], "o", color=c, ms=6)
    a2.vlines(tk, 0, math.degrees(wk), color=c, lw=1, ls=":")
a2.plot(t, np.degrees(w), color=ACC, lw=2)
a1.set_ylabel(T("关节角 θ / (°)", "joint angle θ / (°)"))
a2.set_ylabel(T("角速度 ω = θ′ / (°/s)", "angular velocity ω = θ′ / (°/s)"))
a2.set_xlabel(T("时间 t / s", "time t / s"))
a1.set_title(T("上：各点切线的斜率；下：斜率随 t 变化，就是导函数", "Top: slopes of tangents; bottom: the slope as a function of t, the derivative"), fontsize=11)
clean(a1, zero=False)
clean(a2)
fig.tight_layout()
figure(fig, "fig7_2_1")
