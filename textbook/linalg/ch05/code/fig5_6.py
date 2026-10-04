"""图 5.6.1：机器人一个关节经过 6 个路点的自然三次样条轨迹：角度、角速度、角加速度。
样条的二阶导数由一个三对角方程组决定，用追赶法求出。"""
import numpy as np
from scipy.interpolate import CubicSpline

from _fig import BLUE, GREEN, INK, RED, T, figure, plt

t = np.arange(6.0)
th = np.array([0.0, 20, 60, 90, 70, 40])
cs = CubicSpline(t, th, bc_type="natural")
tt = np.linspace(0, 5, 401)
fig, axs = plt.subplots(1, 3, figsize=(11.4, 3.4))
for ax, (y, c, name, unit) in zip(axs, ((cs(tt), BLUE, T("关节角", "joint angle"), "°"), (cs(tt, 1), GREEN, T("角速度", "angular velocity"), "°/s"),
                                       (cs(tt, 2), RED, T("角加速度", "angular acceleration"), "°/s²"))):
    ax.plot(tt, y, color=c, lw=2)
    if unit == "°":
        ax.plot(t, th, "o", color=INK, ms=6, label=T("路点", "waypoints"))
        ax.legend(frameon=False, fontsize=9)
    ax.set_title(name + " / " + unit, fontsize=11)
    ax.set_xlabel("t / s")
    ax.axhline(0, color="#999999", lw=0.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig5_6_1")
