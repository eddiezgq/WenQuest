"""6.5 节的示意图。

图 6.5.1：算例 6.5.1：UR5e 零位，法兰盘上装长 0.15 m 的工具。工具绕自身 x 轴转动、尖端不动。
          同一个运动，在工具坐标系 {t}、法兰盘坐标系 {b}、基座坐标系 {s} 中写成三个不同的六维矢量；
          转轴（过尖端、沿 x̂_t 的直线）是同一根。法兰盘中心绕这根轴走圆弧。
"""
import math

import numpy as np

from _screw import AXIS, C, UR_AXES, UR_M, axes3d, exp3, frame3d, pose, tight3d
from bookout import T, figure, style

plt = style()

Tbt = pose(np.eye(3), np.array([0, 0.15, 0]))
Tst = UR_M @ Tbt
pts = np.array([np.zeros(3)] + [q for _, q in UR_AXES] + [UR_M[:3, 3]])
tip = Tst[:3, 3]

fig, ax = axes3d(plt, size=(6.4, 4.8), elev=18, azim=-125)
W = pts[3:]                                       # 只画腕部：关节 3 之后的连杆、法兰盘和工具
ax.plot(*W.T, color="#9aa5ad", lw=7, alpha=0.7, solid_capstyle="round")
ax.scatter(*W[:-1].T, color="white", edgecolor="#7a868d", s=30, depthshade=False)
ax.plot(*np.array([UR_M[:3, 3], tip]).T, color=C["accent"], lw=7, solid_capstyle="round")
for Tm, name, off in ((UR_M, "{b}", (0.03, 0.05, 0.02)), (Tst, "{t}", (0.0, -0.02, 0.04))):
    frame3d(ax, Tm, 0.06, "", fs=10, show_axes_labels=False, lw=2.2)
    ax.text(*(Tm[:3, 3] + np.array(off)), name, fontsize=12)
ax.text(*(Tst[:3, 3] + 0.068 * Tst[:3, 0] + np.array([0, 0, 0.01])), r"$\hat x_t$", color=C["x"], fontsize=12)
# 转轴：过工具尖端，沿 x̂_t
xa = Tst[:3, 0]
L = np.array([tip - 0.16 * xa, tip + 0.14 * xa])
ax.plot(*L.T, color=C["ink"], lw=1.4, ls="-.")
ax.text(*(tip + 0.15 * xa + np.array([0, 0, 0.012])), T("转轴", "axis"), fontsize=10)
# 法兰盘中心绕转轴的圆弧
c = UR_M[:3, 3]
arc = np.array([tip + exp3(xa * a) @ (c - tip) for a in np.linspace(-0.7, 0.7, 40)])
ax.plot(*arc.T, color=C["x"], lw=1.8)
ax.quiver(*arc[-3], *(arc[-1] - arc[-3]) * 1.5, color=C["x"], lw=1.8, arrow_length_ratio=0.8)
ax.text2D(0.02, 0.10, T("同一个运动：", "One motion: ") + r"$\mathcal{V}_t = (0.5, 0, 0, 0, 0, 0)$", transform=ax.transAxes, fontsize=10)
ax.text2D(0.02, 0.04, r"$\mathcal{V}_b = [\mathrm{Ad}_{T_{bt}}]\mathcal{V}_t,\quad \mathcal{V}_s = [\mathrm{Ad}_{T_{st}}]\mathcal{V}_t$", transform=ax.transAxes, fontsize=10)
ax.text2D(0.02, 0.92, T("红：法兰盘中心绕转轴的圆弧（尖端不动）", "red: the flange centre's arc about the axis (tip still)"), transform=ax.transAxes, fontsize=9.5, color=C["x"])
ax.text2D(0.02, 0.86, T("{s} 在基座上（图外），见图 12.1.2", "{s} is at the base (off the picture), see Figure 12.1.2"), transform=ax.transAxes, fontsize=9.5, color=C["muted"])
tight3d(ax, np.vstack([W, L, arc, [tip]]), pad=0.02, zoom=1.1)
figure(fig, "fig6_5_1")
plt.close(fig)
