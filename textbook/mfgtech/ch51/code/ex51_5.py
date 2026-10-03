"""51.5 节：常用定位元件示意（图 51.5.1）：支承钉与支承板、V 形块、心轴与定位销、一面两销。"""
import numpy as np

import _mfg as M
from bookout import T, figure, out, style

plt = style()
fig, axs = plt.subplots(1, 4, figsize=(8.4, 2.5))
# (a) 平面：支承钉、支承板
ax = axs[0]
ax.add_patch(plt.Rectangle((0, 0.6), 4, 1.2, fc="#e8edf1", ec=M.INK))
for x in (0.6, 3.4):
    ax.add_patch(plt.Polygon([(x - 0.25, 0.1), (x + 0.25, 0.1), (x + 0.15, 0.6), (x - 0.15, 0.6)], fc=M.ACCENT, ec=M.INK))
ax.add_patch(plt.Rectangle((0, -0.3), 4, 0.4, fc="#c9d2d9", ec=M.INK))
ax.set_title(T("(a) 平面：支承钉", "(a) plane: rest pins"), fontsize=9)
# (b) V 形块
ax = axs[1]
ax.add_patch(plt.Polygon([(0, 0), (4, 0), (4, 1.6), (3.3, 1.6), (2, 0.3), (0.7, 1.6), (0, 1.6)], fc="#c9d2d9", ec=M.INK))
r = 1.0
yc = 0.3 + r / np.sin(np.pi / 4)
ax.add_patch(plt.Circle((2, yc), r, fc="#e8edf1", ec=M.INK))
ax.plot(2, yc, "+", color=M.RED, ms=8)
ax.set_title(T("(b) 外圆：V 形块", "(b) OD: V-block"), fontsize=9)
# (c) 心轴、定位销
ax = axs[2]
ax.add_patch(plt.Rectangle((0.4, 0.2), 3.2, 2.0, fc="#e8edf1", ec=M.INK))
ax.add_patch(plt.Rectangle((1.6, -0.2), 0.8, 2.8, fc=M.ACCENT, ec=M.INK, alpha=0.9))
ax.set_title(T("(c) 内孔：心轴、定位销", "(c) bore: mandrel, pin"), fontsize=9)
# (d) 一面两销
ax = axs[3]
ax.add_patch(plt.Rectangle((0, 0.4), 4, 1.6, fc="#e8edf1", ec=M.INK))
ax.add_patch(plt.Circle((0.7, 1.2), 0.25, fc=M.ACCENT, ec=M.INK))
ax.add_patch(plt.Polygon([(3.15, 1.2), (3.3, 1.45), (3.45, 1.2), (3.3, 0.95)], fc=M.WARM, ec=M.INK))
ax.text(0.7, 0.55, T("圆柱销", "round pin"), ha="center", fontsize=7.5)
ax.text(3.3, 0.55, T("削边销", "diamond pin"), ha="center", fontsize=7.5)
ax.set_title(T("(d) 一面两销", "(d) plane + two pins"), fontsize=9)
for ax in axs:
    ax.set_xlim(-0.3, 4.3); ax.set_ylim(-0.5, 3.0); ax.set_aspect("equal"); ax.axis("off")
figure(fig, "fig51_5_1")
out(n=4)
