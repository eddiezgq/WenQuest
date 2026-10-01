"""12.1 节的示意图。

图 12.1.1：平面 3R 臂的零位（虚线）与只转动关节 2（θ₂ = 30°）后的形态；标出 q₁、q₂、q₃、L₁、L₂、L₃。
图 12.1.2：UR5e 零位时的六根关节轴与点 q₁–q₆，基座坐标系 {s} 与末端坐标系 {b}（数据与算例 12.1.2 相同）。
"""
import math

import numpy as np

from _fig12 import C, L, arc_arrow, arm_points, axes3d, draw_arm, equal3d, frame2d, frame3d, plane
from _poe import Model
from bookout import figure, style

plt = style()

# ---------------------------------------------------------------- 图 12.1.1
fig, ax = plt.subplots(figsize=(6.4, 3.6))
plane(ax, (-0.12, 1.02), (-0.16, 0.42))
zero, _ = arm_points([0, 0, 0])
t2 = math.radians(30)
moved, a = arm_points([0, t2, 0])
draw_arm(ax, zero, C["muted"], lw=5, alpha=0.45, ls="--")
draw_arm(ax, moved, C["accent"], lw=6)
for k, (p, name) in enumerate(zip(zero[:3], ("q_1", "q_2", "q_3"))):
    ax.text(p[0] - 0.015, p[1] - 0.07, f"${name}$", fontsize=12, color=C["ink"])
for (p0, p1), name in zip(zip(zero[:-1], zero[1:]), ("L_1", "L_2", "L_3")):
    ax.text((p0[0] + p1[0]) / 2 - 0.02, -0.11, f"${name}$", fontsize=11, color=C["muted"])
frame2d(ax, (0, 0), 0, 0.09, "")
ax.text(-0.11, 0.02, "{s}", fontsize=10)
frame2d(ax, zero[-1], 0, 0.07, "")
ax.text(zero[-1][0] - 0.03, zero[-1][1] - 0.075, "M", fontsize=11, color=C["muted"])
frame2d(ax, moved[-1], a, 0.07, "")
ax.text(moved[-1][0] + 0.02, moved[-1][1] + 0.03, "{b}", fontsize=10)
arc_arrow(ax, zero[1], 0.16, 0.0, t2, C["accent"])
ax.text(zero[1][0] + 0.17, zero[1][1] + 0.03, r"$\theta_2$", fontsize=12, color=C["accent"])
r = L[1] + L[2]
tt = np.linspace(0, t2, 40)
ax.plot(zero[1][0] + r * np.cos(tt), zero[1][1] + r * np.sin(tt), color=C["accent"], lw=0.9, ls=":")
ax.text(0.0, 0.33, "只转动关节 2：关节 2 以外的部分绕 $q_2$ 整体转动，关节 2 以内不动", fontsize=9.5, color=C["ink"])
figure(fig, "fig12_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 12.1.2
ur = Model("B-ARM-UR5E", "base", "wrist_3_link", (0, 0.1, 0))
sc = ur.screws()
qs = [s[3] for s in sc]
M = ur.fk(np.zeros(6))
path = [np.zeros(3), qs[0], qs[1], qs[1] + np.array([-0.425, 0, 0]), qs[2], qs[2] + np.array([-0.392, 0, 0]),
        qs[3], qs[4], qs[5], M[:3, 3]]
fig, ax = axes3d(plt, size=(7.2, 4.6), elev=20, azim=-38)
P = np.array(path)
ax.plot(*P.T, color="#9aa6ad", lw=7, solid_capstyle="round", alpha=0.85)
cols = [C["accent"]] * 6
for i, (name, kind, w, q, S) in enumerate(sc):
    ax.quiver(*(q - 0.08 * w), *(0.2 * w), color=cols[i], lw=2.2, arrow_length_ratio=0.25)
    ax.scatter(*q, color=C["ink"], s=14)
    tip = q + 0.14 * w
    lab = {0: (0.02, 0.0, 0.0), 3: (0.0, 0.03, 0.06), 4: (0.02, 0.0, -0.03)}.get(i, (0.0, 0.0, 0.035))
    ax.text(*(tip + np.array(lab)), f"轴{i + 1}", fontsize=10, color=cols[i], weight="bold")
    qoff = {4: (0.03, 0.04, 0.02), 5: (0.03, 0.05, -0.05)}.get(i, (0.02, 0.05, -0.05))
    ax.text(*(q + np.array(qoff)), f"$q_{i + 1}$", fontsize=10, color=C["ink"])
frame3d(ax, np.eye(4), 0.15, "{s}")
frame3d(ax, M, 0.1, "")
ax.text(*(M[:3, 3] + np.array([0.0, -0.04, -0.09])), "{b}", fontsize=10)
equal3d(ax, np.r_[P, [[0.1, 0.1, -0.02]]], pad=0.0)
ax.set_box_aspect((1, 1, 1), zoom=1.35)
ax.text2D(0.0, 0.02, "关节 2、3、4 的轴互相平行（沿 −y）；关节 1、5 的轴竖直；箭头为转轴正方向", transform=ax.transAxes, fontsize=9)
figure(fig, "fig12_1_2")
plt.close(fig)
