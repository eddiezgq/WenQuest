"""2.1 节的示意图。

图 2.1.1：平面 2R 臂（θ = (30°, 60°)）。关节 1、关节 2 单独转动时末端的速度方向就是雅可比矩阵的两列；
         末端速度 v = θ̇1 j1 + θ̇2 j2 是两列的线性组合（平行四边形）。
图 2.1.2：det J = L1 L2 sin θ2 随 θ2 的变化，以及 θ2 = 0°、90°、180° 时手臂的形态。
"""
import math

import numpy as np

from _la import C, L2R, arm_points, arrow, base, d, draw_arm, jac
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 2.1.1
th = [d(30), d(60)]
pts = arm_points(th, L2R)
J = jac(th, L2R)
thd = np.array([0.5, -1.0])
k = 0.9                                          # 速度画在图上的比例：1 m/s 画成 0.9 m
tip = pts[2]
a = tip + k * thd[0] * J[:, 0]
b = tip + k * thd[1] * J[:, 1]
v = tip + k * (J @ thd)

fig, ax = plt.subplots(figsize=(6.2, 4.6))
ax.set_aspect("equal")
ax.axis("off")
arrow(ax, (-0.08, 0), (0.62, 0), C["x"], 1.0)
arrow(ax, (0, -0.06), (0, 0.86), C["y"], 1.0)
ax.text(0.625, -0.03, "$x$", color=C["x"], fontsize=12)
ax.text(0.015, 0.85, "$y$", color=C["y"], fontsize=12)
base(ax)
draw_arm(ax, pts, "#7f8c95", lw=7)
# 关节到末端的连线（虚线）：末端速度垂直于它们
ax.plot([0, tip[0]], [0, tip[1]], color=C["muted"], lw=0.8, ls=":")
ax.text(0.2, 0.06, "$L_1$", fontsize=11, color=C["muted"])
ax.text(0.385, 0.4, "$L_2$", fontsize=11, color=C["muted"])
ax.text(0.03, -0.05, r"$\theta_1$", fontsize=11)
ax.text(pts[1][0] + 0.03, pts[1][1] - 0.02, r"$\theta_2$", fontsize=11)
arrow(ax, tip, a, C["z"], 1.8)
arrow(ax, tip, b, C["accent"], 1.8)
arrow(ax, tip, v, C["ink"], 2.4)
ax.plot([a[0], v[0]], [a[1], v[1]], color=C["muted"], lw=0.8, ls="--")
ax.plot([b[0], v[0]], [b[1], v[1]], color=C["muted"], lw=0.8, ls="--")
ax.text(a[0] + 0.0, a[1] - 0.075, r"$\dot\theta_1 j_1$", color=C["z"], fontsize=12)
ax.text(b[0] - 0.01, b[1] - 0.06, r"$\dot\theta_2 j_2$", color=C["accent"], fontsize=12)
ax.text(v[0] + 0.015, v[1] + 0.0, r"$v = J\dot\theta$", color=C["ink"], fontsize=12)
ax.text(tip[0] + 0.02, tip[1] - 0.05, T("末端", "end-effector"), fontsize=10, color=C["ink"])
ax.text(-0.08, -0.15, T("蓝：只转关节 1 时末端的速度；金：只转关节 2 时末端的速度；黑：两者之和",
                        "blue: end-effector velocity from joint 1 alone; gold: from joint 2 alone; black: their sum"),
        fontsize=9, color=C["ink"])
ax.set_xlim(-0.1, 0.75)
ax.set_ylim(-0.2, 0.9)
figure(fig, "fig2_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 2.1.2
L1, L2 = L2R
t2 = np.linspace(-180, 180, 361)
detJ = L1 * L2 * np.sin(np.radians(t2))
plt.rcParams["axes.unicode_minus"] = True        # 刻度上的负号用真正的减号 “−”
fig = plt.figure(figsize=(6.6, 4.0))
ax = fig.add_axes([0.1, 0.14, 0.86, 0.5])
ax.plot(t2, detJ, color=C["z"], lw=1.6)
ax.axhline(0, color=C["muted"], lw=0.8)
for x in (-180, 0, 180):
    ax.plot([x], [0], "o", color=C["x"], ms=5)
ax.plot([90], [L1 * L2], "o", color=C["accent"], ms=5)
ax.set_xlim(-185, 185)
ax.set_xticks([-180, -90, 0, 90, 180])
ax.set_xlabel(T(r"$\theta_2$ / (°)", r"$\theta_2$ / deg"))
ax.set_ylabel(r"$\det J$ / m$^2$")
ax.spines[["top", "right"]].set_visible(False)
# 三个形态的小图
for xc, t2v, lab in ((0.12, 0, T("θ₂ = 0°：伸直，det J = 0", "θ₂ = 0°: straight, det J = 0")),
                     (0.45, 90, T("θ₂ = 90°：det J 最大", "θ₂ = 90°: det J largest")),
                     (0.78, 180, T("θ₂ = 180°：折叠，det J = 0", "θ₂ = 180°: folded, det J = 0"))):
    sub = fig.add_axes([xc - 0.1, 0.68, 0.2, 0.3])
    sub.set_aspect("equal")
    sub.axis("off")
    p = arm_points([d(20), d(t2v)], L2R)
    base(sub, w=0.05)
    draw_arm(sub, p, "#7f8c95", lw=4)
    sub.set_xlim(-0.25, 0.85)
    sub.set_ylim(-0.1, 0.55)
    sub.text(-0.25, -0.18, lab, fontsize=8.5, color=C["ink"])
figure(fig, "fig2_1_2")
plt.close(fig)
