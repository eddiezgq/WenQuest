"""图 9.4.1：复合的顺序。左：先转 30°（R）再投影到 x 轴（P），即 PR；右：先投影再转，即 RP。灰色为原来的小旗，虚线为第一步的结果，彩色为最终结果。"""
import numpy as np

from _fig import BLUE, INK, MUTED, RED, T, axes_box, figure, marker, plt

t = np.radians(30)
R = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
P = np.array([[1.0, 0], [0, 0]])
f0 = marker(scale=2.2)
fig, axs = plt.subplots(1, 2, figsize=(8.4, 3.8))
for ax, (first, second, name, col) in zip(axs, [(R, P, T("先转 30° 再投影：PR", "rotate 30°, then project: PR"), BLUE),
                                               (P, R, T("先投影再转 30°：RP", "project, then rotate 30°: RP"), RED)]):
    axes_box(ax, 2.0, ticks=False)
    ax.set_xlim(-0.6, 2.4)
    ax.set_ylim(-0.6, 2.0)
    ax.fill(*f0, color=MUTED, alpha=0.45)
    mid = first @ f0
    ax.plot(*mid, color=INK, lw=1.2, ls="--")
    fin = second @ mid
    ax.plot(*fin, color=col, lw=6, solid_capstyle="butt")
    ax.plot([0], [0], "o", color=INK, ms=4)
    ax.set_title(name, fontsize=12, color=INK)
figure(fig, "fig9_4_1")
