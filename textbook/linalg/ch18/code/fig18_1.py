"""图 18.1.1：A 把单位圆变成椭圆；图 18.1.2：UR5e 肩、肘两关节在 θ1 = 30°、θ2 = 60° 时的末端速度椭圆。"""
import math

import numpy as np

from _arm import planar2, svd_fixed, ur5e_links
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow, axes_box, circle_pts, figure, plt

A = np.array([[3.0, 0.0], [4.0, 5.0]])
U, s, V = svd_fixed(A)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.2, 4.4))
axes_box(a1, 1.6)
a1.plot(*circle_pts(), color=INK, lw=1.6)
arrow(a1, [1, 0], MUTED, r"$\boldsymbol{e}_1$", (0.05, -0.2), lw=1.2)
arrow(a1, [0, 1], MUTED, r"$\boldsymbol{e}_2$", (-0.3, 0.05), lw=1.2)
arrow(a1, V[:, 0], RED, r"$\boldsymbol{v}_1$")
arrow(a1, V[:, 1], GREEN, r"$\boldsymbol{v}_2$", (0.05, -0.25))
a1.set_title(T(r"单位圆 $\Vert\boldsymbol{x}\Vert = 1$", r"Unit circle $\Vert\boldsymbol{x}\Vert = 1$"), fontsize=12)
axes_box(a2, 7.2)
a2.plot(*circle_pts(A), color=INK, lw=1.6)
arrow(a2, A @ [1, 0], MUTED, r"$A\boldsymbol{e}_1$", (0.2, -0.3), lw=1.2)
arrow(a2, A @ [0, 1], MUTED, r"$A\boldsymbol{e}_2$", (-1.6, 0.2), lw=1.2)
arrow(a2, s[0] * U[:, 0], RED, r"$A\boldsymbol{v}_1=\sigma_1\boldsymbol{u}_1$", (0.2, 0.0))
arrow(a2, s[1] * U[:, 1], GREEN, r"$A\boldsymbol{v}_2=\sigma_2\boldsymbol{u}_2$", (0.2, -0.6))
a2.set_title(T(r"像：椭圆，两个半轴是 $\sigma_1\boldsymbol{u}_1$、$\sigma_2\boldsymbol{u}_2$", r"Image: an ellipse with semi-axes $\sigma_1\boldsymbol{u}_1$, $\sigma_2\boldsymbol{u}_2$"), fontsize=12)
fig.tight_layout()
figure(fig, "fig18_1_1")

# 图 18.1.2
l1, l2 = ur5e_links()
t1, t2 = math.radians(30), math.radians(60)
p, J = planar2(t1, t2, l1, l2)
Uj, sj, Vj = svd_fixed(J)
fig, (b1, b2) = plt.subplots(1, 2, figsize=(9.2, 4.6), gridspec_kw={"width_ratios": [1, 1.25]})
axes_box(b1, 1.25)
b1.plot(*circle_pts(), color=INK, lw=1.4)
arrow(b1, Vj[:, 0], RED, r"$\boldsymbol{v}_1$")
arrow(b1, Vj[:, 1], GREEN, r"$\boldsymbol{v}_2$", (-0.35, 0.08))
b1.set_xlabel(r"$\dot\theta_1$ / (rad/s)")
b1.set_ylabel(r"$\dot\theta_2$ / (rad/s)")
b1.set_title(T(r"关节速度：$\Vert\dot{\boldsymbol{\theta}}\Vert = 1$ rad/s", r"Joint velocities: $\Vert\dot{\boldsymbol{\theta}}\Vert = 1$ rad/s"), fontsize=12)
b2.set_aspect("equal")
j = np.array([l1 * math.cos(t1), l1 * math.sin(t1)])
b2.plot([0, j[0], p[0]], [0, j[1], p[1]], color=BLUE, lw=5, alpha=0.55, solid_capstyle="round", zorder=1)
b2.plot([0, j[0]], [0, j[1]], "o", color="white", mec=INK, ms=8)
k = 0.35                                                           # 速度椭圆画在末端，0.35 m 代表 1 m/s
E = circle_pts(J) * k + p[:, None]
b2.plot(E[0], E[1], color=INK, lw=1.6)
arrow(b2, k * sj[0] * Uj[:, 0], RED, T(r"最快 $\sigma_1$", r"fastest $\sigma_1$"), (-0.18, 0.05), start=p)
arrow(b2, k * sj[1] * Uj[:, 1], GREEN, T(r"最慢 $\sigma_2$", r"slowest $\sigma_2$"), (-0.27, -0.02), start=p)
b2.text(j[0] + 0.03, j[1] - 0.08, T("肘", "elbow"), color=MUTED)
b2.text(0.03, -0.08, T("肩", "shoulder"), color=MUTED)
b2.set_xlim(-0.35, 0.9)
b2.set_ylim(-0.15, 0.95)
b2.set_xlabel("x / m")
b2.set_ylabel("y / m")
b2.set_title(T("末端速度椭圆（0.35 m 代表 1 m/s）", "Tool velocity ellipse (0.35 m ≙ 1 m/s)"), fontsize=12)
fig.tight_layout()
figure(fig, "fig18_1_2")
