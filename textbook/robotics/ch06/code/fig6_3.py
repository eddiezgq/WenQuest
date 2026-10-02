"""6.3 节的示意图。

图 6.3.1：运动旋量的速度场（莫齐定理）：刚体上各点的速度 = 绕螺旋轴转动的速度 + 沿轴的速度 h|ω|。
          轴上的点只沿轴运动；离轴越远，垂直于轴的速度越大。
图 6.3.2：算例 6.3.2：UR5e 零位时关节 1、3 同时转动，合成的运动旋量的瞬时螺旋轴（方向 ŝ、过点 q、节距 h）。
"""
import math

import numpy as np

from _screw import AXIS, C, UR_AXES, UR_M, UR_S, axes3d, axis_of, tight3d
from bookout import T, figure, style

plt = style()
d = math.radians

# ---------------------------------------------------------------- 图 6.3.1
fig, ax = axes3d(plt, size=(5.6, 4.6), elev=16, azim=-60)
w = np.array([0, 0, 1.0])           # 角速度 1 rad/s，沿 z
h = 0.35                            # 节距
ax.plot([0, 0], [0, 0], [-0.3, 1.55], color=C["ink"], lw=1.4, ls="-.")
ax.quiver(0, 0, 1.45, 0, 0, 0.25, color=C["ink"], lw=1.6, arrow_length_ratio=0.35)
ax.text(0.06, 0.0, 1.62, r"$\hat s$", fontsize=13)
k = 0.5
for z, rr in ((0.0, 0.0), (0.0, 0.5), (0.0, 1.0), (0.9, 0.0), (0.9, 1.0)):
    n = 1 if rr == 0 else 6
    for a in np.linspace(0, 2 * math.pi, n, endpoint=False) + (math.pi / 6 if rr else 0):   # 错开视线方向，免得圆上的点投影到轴上
        x = np.array([rr * math.cos(a), rr * math.sin(a), z])
        vel = np.cross(w, x) + h * w
        ax.scatter(*x, color=C["ink"], s=8, depthshade=False)
        ax.quiver(*x, *(vel * k), color=C["accent"] if rr else C["z"], lw=1.5, arrow_length_ratio=0.18)
    if rr:
        t = np.linspace(0, 2 * math.pi, 80)
        ax.plot(rr * np.cos(t), rr * np.sin(t), z + 0 * t, color=C["muted"], lw=0.6, ls=":")
# 一条螺旋线
t = np.linspace(0, 4.2, 200)
ax.plot(1.0 * np.cos(t), 1.0 * np.sin(t), 0.0 + h * t, color=C["x"], lw=1.2, alpha=0.8)
ax.text(0.1, 0.1, 1.05, r"$h|\omega|$", color=C["z"], fontsize=12, ha="left")
ax.text2D(0.0, 0.10, T("轴上的点：只沿轴运动", "on the axis: moves along it only"), transform=ax.transAxes, fontsize=9.5, color=C["z"])
ax.text2D(0.0, 0.04, T("离轴 r 处：垂直速度 |ω| r", "at distance r: |ω| r across"), transform=ax.transAxes, fontsize=9.5, color=C["accent"])
ax.text2D(0.0, -0.02, T("一点的轨迹：螺旋线", "a point's path: a helix"), transform=ax.transAxes, fontsize=9.5, color=C["x"])
tight3d(ax, np.array([[-1.1, -1.1, -0.3], [1.1, 1.1, 1.6]]), pad=0.0, zoom=1.25)
figure(fig, "fig6_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 6.3.2
r1 = r3 = d(30)
V = UR_S[0] * r1 + UR_S[2] * r3
s_hat, q, hp = axis_of(V)
pts = [np.zeros(3)] + [qq for _, qq in UR_AXES] + [UR_M[:3, 3]]
P = np.array(pts)
fig, ax = axes3d(plt, size=(6.2, 4.8), elev=20, azim=-35)
ax.plot(*P.T, color="#5b6b75", lw=4, solid_capstyle="round", alpha=0.6)
for qq in P[1:-1]:
    ax.scatter(*qq, color="white", edgecolor=C["ink"], s=26, depthshade=False, zorder=5)
# 关节 1、3 的轴
(w1, q1), (w3, q3) = UR_AXES[0], UR_AXES[2]
ax.plot(*np.array([q1 - 0.25 * w1, q1 + 0.45 * w1]).T, color=C["z"], lw=1.4, ls="--")
ax.text(*(q1 + 0.5 * w1), T("关节 1 的轴", "joint 1 axis"), color=C["z"], fontsize=9.5, ha="center")
ax.plot(*np.array([q3 - 0.35 * w3, q3 + 0.3 * w3]).T, color=C["z"], lw=1.4, ls="--")
ax.text(*(q3 + 0.36 * w3 + np.array([0, 0, -0.02])), T("关节 3 的轴", "joint 3 axis"), color=C["z"], fontsize=9.5, ha="left")
# 瞬时螺旋轴
A = np.array([q - 0.45 * s_hat, q + 0.55 * s_hat])
ax.plot(*A.T, color=C["accent"], lw=2.2)
ax.quiver(*(q + 0.4 * s_hat), *(0.15 * s_hat), color=C["accent"], lw=2.2, arrow_length_ratio=0.4)
ax.scatter(*q, color=C["accent"], s=30, depthshade=False)
ax.text(*(q + np.array([-0.02, 0.0, 0.05])), "$q$", color=C["accent"], fontsize=13)
ax.text(*(q + 0.6 * s_hat + np.array([0, 0, 0.02])), T("瞬时螺旋轴（节距 h = L₁/2）", "instantaneous screw axis (pitch h = L₁/2)"), color=C["accent"], fontsize=9.5, ha="center")
# 基座坐标系
for i in range(3):
    e = np.zeros(3)
    e[i] = 0.25
    ax.quiver(0.0, 0.0, -0.12, *e, color=AXIS[i], lw=1.8, arrow_length_ratio=0.25)
ax.text(-0.06, -0.06, -0.24, "{s}", fontsize=11)
tight3d(ax, np.vstack([P, A, [q1 + 0.5 * w1], [q3 + 0.5 * w3], [[0, 0, -0.2]]]), pad=0.05, zoom=1.2)
figure(fig, "fig6_3_2")
plt.close(fig)
