"""6.4 节的示意图。

图 6.4.1：算例 6.4.2：UR5e 从零位（灰）运动到 θ = (30°, −45°, 60°, −15°, 90°, 30°)（金色）。
          由对数映射求出的螺旋轴（ŝ、q），以及沿螺旋轴插值 e^{[S]θs}M 时法兰盘中心走过的螺旋线，
          与两端点之间的直线对照。
"""
import math

import numpy as np

from _screw import AXIS, C, UR_AXES, UR_M, UR_S, axes3d, axis_of, exp6, frame3d, inv, log6, tight3d, ur_fk
from bookout import T, figure, style

plt = style()
d = math.radians
theta = np.array([d(30), d(-45), d(60), d(-15), d(90), d(30)])


def skeleton(th):
    """基座、六个关节中心（零位时取表 12.1.1 的 q_i）和法兰盘中心在 θ 下的位置。"""
    pts, E = [np.zeros(3)], np.eye(4)
    for i, (w, q) in enumerate(UR_AXES):
        pts.append((E @ np.r_[q, 1])[:3])
        E = E @ exp6(UR_S[i], th[i])
    pts.append(ur_fk(th)[:3, 3])
    return np.array(pts)


Tt = ur_fk(theta)
D = Tt @ inv(UR_M)
S, th = log6(D)
s_hat, q, h = axis_of(S)
P0, P1 = skeleton(np.zeros(6)), skeleton(theta)
path = np.array([(exp6(S, th * f) @ UR_M)[:3, 3] for f in np.linspace(0, 1, 80)])

fig, ax = axes3d(plt, size=(6.4, 5.0), elev=22, azim=60)
ax.plot(*P0.T, color="#9aa5ad", lw=4, alpha=0.6, solid_capstyle="round")
ax.plot(*P1.T, color=C["accent"], lw=4, alpha=0.75, solid_capstyle="round")
for P, col in ((P0, "#9aa5ad"), (P1, C["accent"])):
    ax.scatter(*P[1:-1].T, color="white", edgecolor=col, s=18, depthshade=False)
frame3d(ax, UR_M, 0.12, "", fs=10, show_axes_labels=False)
frame3d(ax, Tt, 0.12, "", fs=10, show_axes_labels=False)
A = np.array([q - 0.35 * s_hat, q + 0.45 * s_hat])
ax.plot(*A.T, color=C["ink"], lw=1.5, ls="-.")
ax.quiver(*(q + 0.42 * s_hat), *(0.12 * s_hat), color=C["ink"], lw=1.6, arrow_length_ratio=0.4)
ax.scatter(*q, color=C["ink"], s=16, depthshade=False)
ax.text(*(q + np.array([0.03, 0.0, 0.03])), "$q$", fontsize=13)
ax.text(*(q + 0.5 * s_hat + np.array([0.0, 0.05, 0.0])), r"$\hat s$", fontsize=13)
ax.plot(*path.T, color=C["x"], lw=2.0)
ax.plot(*np.array([path[0], path[-1]]).T, color=C["muted"], lw=1.0, ls="--")
ax.text(*(path[0] + np.array([0.0, 0.08, -0.12])), T("零位", "home"), fontsize=10, color=C["muted"], ha="center")
ax.text(*(path[-1] + np.array([0.0, 0.06, 0.07])), T("目标", "target"), fontsize=10, color=C["accent"], ha="center")
ax.text2D(0.02, 0.06, T("红：沿螺旋轴插值时法兰盘中心的路径", "red: flange-centre path under screw interpolation"), transform=ax.transAxes, fontsize=9.5, color=C["x"])
ax.text2D(0.02, 0.01, T("虚线：两端点之间的直线", "dashed: the straight line between the ends"), transform=ax.transAxes, fontsize=9.5, color=C["muted"])
for i in range(3):
    e = np.zeros(3)
    e[i] = 0.15
    ax.quiver(0, 0, 0, *e, color=AXIS[i], lw=1.4, arrow_length_ratio=0.3)
ax.text(0.03, 0.03, -0.07, "{s}", fontsize=10)
tight3d(ax, np.vstack([P0, P1, A, path, [[0, 0, -0.08]]]), pad=0.04, zoom=1.15)
figure(fig, "fig6_4_1")
plt.close(fig)
