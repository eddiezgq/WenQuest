"""图 11.4.1：两种正交变换。左：豪斯霍尔德反射——以与 v 垂直的直线（高维时是超平面）为镜子，把 x 反射到 x 轴上，得 −‖x‖e₁，v = x + ‖x‖e₁；
右：吉文斯旋转——在一个坐标平面内转一个角度，把 (a, b) = (3, 4) 转到 (5, 0)。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow, axes_box, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 4.6))
x = np.array([2.0, 1.5])
nx = np.linalg.norm(x)
v = x + nx * np.array([1.0, 0])
u = v / np.linalg.norm(v)
mirror = np.array([-u[1], u[0]])
axes_box(a1, 3.2, ticks=False)
a1.plot(*np.c_[-3.0 * mirror, 3.0 * mirror], color=MUTED, lw=1.5, ls="--")
a1.text(*(2.6 * mirror + np.array([0.1, 0])), T("镜面（⊥ v）", "mirror (⊥ v)"), color=MUTED, fontsize=11)
arrow(a1, x, BLUE, "x", offset=(0.08, 0.05))
arrow(a1, np.array([-nx, 0.0]), RED, "Hx = −‖x‖e₁", offset=(-0.6, 0.2))
arrow(a1, 0.6 * u, GREEN, "v", offset=(0.05, 0.08))
a1.plot(*np.c_[x, np.array([-nx, 0.0])], color=INK, lw=0.8, ls=":")
a1.set_title(T("豪斯霍尔德反射：H = I − 2vvᵀ/vᵀv", "Householder reflection: H = I − 2vvᵀ/vᵀv"), fontsize=11)
axes_box(a2, 6.0, ticks=False)
a2.set_xlim(-1.0, 6.0); a2.set_ylim(-1.0, 5.5)
ab = np.array([3.0, 4.0])
arrow(a2, ab, BLUE, "(a, b) = (3, 4)", offset=(0.1, 0.05))
arrow(a2, np.array([5.0, 0.0]), RED, "(r, 0) = (5, 0)", offset=(-0.6, 0.25))
th = np.linspace(0, np.arctan2(4, 3), 50)
a2.plot(5 * np.cos(th), 5 * np.sin(th), color=MUTED, lw=1, ls="--")
th2 = np.linspace(0, np.arctan2(4, 3), 30)
a2.plot(1.2 * np.cos(th2), 1.2 * np.sin(th2), color=INK, lw=1)
a2.text(1.3, 0.45, "θ", fontsize=12)
a2.set_title(T("吉文斯旋转：c = a/r，s = b/r", "Givens rotation: c = a/r, s = b/r"), fontsize=11)
figure(fig, "fig11_4_1")
