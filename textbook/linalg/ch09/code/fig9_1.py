"""图 9.1.1：平面上的四个线性映射——旋转 30°、向 30° 直线投影、关于 30° 直线反射、剪切。灰色为原来的网格与小旗，彩色为像。
网格线变换后仍是等距的平行直线，原点不动。"""
import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, ACC, T, axes_box, figure, marker, plt

t = np.radians(30)
u = np.array([np.cos(t), np.sin(t)])
maps = [(np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]]), T("旋转 30°", "rotation by 30°"), BLUE),
        (np.outer(u, u), T("向 30° 直线投影", "projection onto the 30° line"), GREEN),
        (2 * np.outer(u, u) - np.eye(2), T("关于 30° 直线反射", "reflection in the 30° line"), RED),
        (np.array([[1.0, 0.8], [0, 1]]), T("剪切", "shear"), ACC)]
fig, axs = plt.subplots(1, 4, figsize=(12.0, 3.4))
for ax, (M, name, col) in zip(axs, maps):
    axes_box(ax, 2.2, ticks=False)
    for k in np.arange(-2, 2.01, 0.5):
        for a, b in ((np.array([k, -2]), np.array([k, 2])), (np.array([-2, k]), np.array([2, k]))):
            ax.plot(*np.c_[a, b], color=MUTED, lw=0.5, alpha=0.5)
            p, q = M @ a, M @ b
            ax.plot(*np.c_[p, q], color=col, lw=0.8, alpha=0.55)
    if name in (maps[1][1], maps[2][1]):
        ax.plot(*np.c_[-2.5 * u, 2.5 * u], color=INK, lw=0.8, ls="--", zorder=3)
    f0 = marker(scale=1.4)
    ax.fill(*f0, color=MUTED, alpha=0.5)
    img = M @ f0
    if abs(np.linalg.det(M)) < 1e-9:     # 投影把小旗压成线段：画粗线
        ax.plot(*img, color=col, lw=5, solid_capstyle="butt", zorder=4)
    else:
        ax.fill(*img, color=col, alpha=0.85)
    ax.plot([0], [0], "o", color=INK, ms=4)
    ax.set_title(name, fontsize=12, color=INK)
figure(fig, "fig9_1_1")
