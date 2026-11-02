"""图 21.2.1：左：单摆相图（能量等值线，分界线）；右：有阻尼单摆的轨线螺旋地落入最低点。"""
import numpy as np
from scipy.integrate import solve_ivp

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

g, l = 9.81, 0.5
k = g / l
th = np.linspace(-1.5 * np.pi, 3.5 * np.pi, 600)
w = np.linspace(-14, 14, 400)
TH, W = np.meshgrid(th, w)
E = 0.5 * W ** 2 - k * np.cos(TH)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
for ax in (a1, a2):
    ax.contour(TH, W, E, levels=np.linspace(-k + 1, 3 * k, 14), colors=MUTED, linewidths=0.7, linestyles="solid")
    ax.contour(TH, W, E, levels=[k], colors=RED, linewidths=1.8)
    ax.set_xticks(np.arange(-1, 4) * np.pi)
    ax.set_xticklabels(["−π", "0", "π", "2π", "3π"])
    ax.set_xlabel(T("摆角 θ / rad", "angle θ / rad"))
    ax.set_ylabel(T("角速度 ω / (rad/s)", "angular speed ω / (rad/s)"))
    for p in (0, 2 * np.pi):
        ax.plot(p, 0, "o", color=GREEN, ms=5)
    for p in (-np.pi, np.pi, 3 * np.pi):
        ax.plot(p, 0, "o", color=RED, ms=5)
a1.set_title(T("单摆的相图：摆动、转动与分界线（红）", "Pendulum phase portrait: swings, rotations, separatrix (red)"), fontsize=10)
s = solve_ivp(lambda t, y: [y[1], -k * np.sin(y[0]) - 0.5 * y[1]], (0, 30), [0, 1.2 * 2 * np.sqrt(k)], max_step=0.01)
a2.plot(s.y[0], s.y[1], color=BLUE, lw=1.6)
a2.plot(s.y[0][0], s.y[1][0], "s", color=BLUE)
a2.set_title(T("有阻尼（c = 0.5 /s）：能量减小，轨线螺旋地落入最低点", "Damped (c = 0.5 /s): energy falls, the orbit spirals into a minimum"), fontsize=10)
for ax in (a1, a2):
    ax.set_xlim(-1.5 * np.pi, 3.5 * np.pi)
    clean(ax)
fig.tight_layout()
figure(fig, "fig21_2_1")
