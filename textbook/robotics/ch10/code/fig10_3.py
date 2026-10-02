"""10.3 节的示意图。

图 10.3.1：柱面坐标 (ρ, φ, z) 与点 P 处的局部基 e_ρ、e_φ、e_z（斜投影）。
图 10.3.2：算例 10.3.1，SCARA 俯视：末端的极坐标 (ρ, φ)，局部基，速度与加速度的径向、横向分量。
"""
import math

import numpy as np

from _kin import A_COL, AXIS, C, G_COL, V_COL, arrow, cyl_basis, oblique
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 10.3.1
fig, ax = plt.subplots(figsize=(5.6, 4.6))
ax.set_aspect("equal")
ax.axis("off")
O = np.zeros(3)
for i, (lab, L) in enumerate((("x", 1.5), ("y", 1.6), ("z", 1.35))):
    e = np.zeros(3)
    e[i] = L
    arrow(ax, oblique(O), oblique(e), AXIS[i], 1.1)
    ax.text(*(oblique(e) + np.array([0.04, -0.04 if i < 2 else 0.02])), f"${lab}$", color=AXIS[i], fontsize=12)
rho, phi, z = 1.1, math.radians(50), 0.9
P = np.array([rho * math.cos(phi), rho * math.sin(phi), z])
Pf = np.array([P[0], P[1], 0])
t = np.linspace(0, phi, 40)
ax.plot(*np.array([oblique([0.45 * math.cos(a), 0.45 * math.sin(a), 0]) for a in t]).T, color=C["accent"], lw=1.2)
ax.text(*(oblique([0.55 * math.cos(phi / 2), 0.55 * math.sin(phi / 2), 0]) + np.array([-0.02, -0.08])), r"$\varphi$", color=C["accent"], fontsize=12)
tt = np.linspace(0, 2 * math.pi, 120)
ax.plot(*np.array([oblique([rho * math.cos(a), rho * math.sin(a), z]) for a in tt]).T, color=G_COL, lw=0.7, ls=":")
ax.plot(*np.array([oblique([rho * math.cos(a), rho * math.sin(a), 0]) for a in tt]).T, color=G_COL, lw=0.7, ls=":")
ax.plot(*np.array([oblique(O), oblique(Pf)]).T, color=C["ink"], lw=1.0)
ax.text(*(oblique(Pf * 0.5) + np.array([0.02, -0.12])), r"$\rho$", fontsize=12)
ax.plot(*np.array([oblique(Pf), oblique(P)]).T, color=C["ink"], lw=1.0, ls="--")
ax.text(*(oblique((Pf + P) / 2) + np.array([0.04, 0])), "$z$", fontsize=12)
ax.plot(*np.array([oblique([0, 0, z]), oblique(P)]).T, color=G_COL, lw=0.8, ls="--")
ax.plot(*oblique(P), "o", color=C["ink"], ms=5, zorder=6)
ax.text(*(oblique(P) + np.array([-0.18, 0.07])), "P", fontsize=12)
er, ep, ez = cyl_basis(phi)
for e, lab, col in ((er, r"$e_\rho$", AXIS[0]), (ep, r"$e_\varphi$", AXIS[1]), (ez, r"$e_z$", AXIS[2])):
    q = oblique(P + 0.55 * e)
    arrow(ax, oblique(P), q, col, 2.0)
    ax.text(*(q + np.array([0.03, 0.02])), lab, color=col, fontsize=13)
ax.text(-1.25, -0.95, T(r"局部基随 P 的方位角 $\varphi$ 而转动；$e_z$ 方向不变", r"the local basis turns with the azimuth $\varphi$ of P; $e_z$ keeps its direction"),
        fontsize=9, color=C["ink"])
ax.set_xlim(-1.3, 2.1)
ax.set_ylim(-1.05, 1.75)
figure(fig, "fig10_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 10.3.2
l1, l2 = 0.35, 0.25
q1, q2 = math.radians(30), math.radians(90)
J = np.array([l1 * math.cos(q1), l1 * math.sin(q1)])
E = J + l2 * np.array([math.cos(q1 + q2), math.sin(q1 + q2)])
rho = float(np.linalg.norm(E))
phi = math.atan2(E[1], E[0])
er, ep, _ = cyl_basis(phi)
er, ep = er[:2], ep[:2]
v_rho, v_phi = 0.30515, 0.21215          # 与程序 10.3.1 相同（只用于画箭头长度）
a_rho, a_phi = -0.32113, 0.15258
fig, ax = plt.subplots(figsize=(6.4, 5.0))
ax.set_aspect("equal")
ax.axis("off")
arrow(ax, (-0.05, 0), (0.55, 0), C["x"], 1.0)
arrow(ax, (0, -0.05), (0, 0.72), C["y"], 1.0)
ax.text(0.555, -0.015, "$x_s$", color=C["x"], fontsize=11)
ax.text(0.008, 0.72, "$y_s$", color=C["y"], fontsize=11)
ax.plot([0, J[0], E[0]], [0, J[1], E[1]], color="#8fa3b5", lw=7, solid_capstyle="round", zorder=1)
for p in (np.zeros(2), J):
    ax.plot(*p, "o", color="white", mec=C["ink"], ms=7, zorder=2)
ax.text(-0.075, -0.045, T("关节 1", "joint 1"), fontsize=8.5, color=G_COL)
ax.text(J[0] + 0.015, J[1] - 0.03, T("关节 2", "joint 2"), fontsize=8.5, color=G_COL)
ax.plot([0, E[0]], [0, E[1]], color=C["ink"], lw=1.0, ls="--", zorder=3)
ax.text(E[0] * 0.45 - 0.06, E[1] * 0.45 + 0.01, r"$\rho$", fontsize=12)
t = np.linspace(0, phi, 40)
ax.plot(0.1 * np.cos(t), 0.1 * np.sin(t), color=C["accent"], lw=1.1)
ax.text(0.13 * math.cos(math.radians(52)) - 0.01, 0.13 * math.sin(math.radians(52)), r"$\varphi$", color=C["accent"], fontsize=12)
ax.plot(*E, "o", color=C["ink"], ms=5, zorder=6)
ax.text(E[0] + 0.015, E[1] - 0.04, "E", fontsize=12)
k = 0.6
ax.plot(*np.array([E, E + 0.33 * er]).T, color=C["x"], lw=0.7, ls=":")
ax.plot(*np.array([E - 0.2 * ep, E + 0.33 * ep]).T, color=C["y"], lw=0.7, ls=":")
ax.text(*(E + 0.34 * er + np.array([0.0, 0.0])), r"$e_\rho$" + T(" 方向", " direction"), color=C["x"], fontsize=10)
ax.text(*(E + 0.34 * ep + np.array([-0.07, 0.01])), r"$e_\varphi$" + T(" 方向", " direction"), color=C["y"], fontsize=10)
arrow(ax, E, E + k * v_rho * er, V_COL, 1.2, ls="--")
arrow(ax, E, E + k * v_phi * ep, V_COL, 1.2, ls="--")
arrow(ax, E, E + k * (v_rho * er + v_phi * ep), V_COL, 2.0)
ax.text(*(E + k * (v_rho * er + v_phi * ep) + np.array([0.008, 0.0])), "$v$", color=V_COL, fontsize=12)
ka = 0.6
arrow(ax, E, E + ka * a_rho * er, A_COL, 1.2, ls="--")
arrow(ax, E, E + ka * a_phi * ep, A_COL, 1.2, ls="--")
arrow(ax, E, E + ka * (a_rho * er + a_phi * ep), A_COL, 2.0)
ax.text(*(E + ka * (a_rho * er + a_phi * ep) + np.array([-0.03, -0.035])), "$a$", color=A_COL, fontsize=12)
ax.text(*(E + ka * a_rho * er + np.array([0.012, -0.02])), r"$a_\rho$", color=A_COL, fontsize=10)
ax.text(*(E + ka * a_phi * ep + np.array([-0.02, -0.04])), r"$a_\varphi$", color=A_COL, fontsize=10)
ax.text(-0.17, -0.12, T("实线：速度 v（橙）与加速度 a（红）；虚线：它们的径向、横向分量",
                        "solid: velocity v (orange) and acceleration a (red); dashed: radial and transverse parts"), fontsize=8.5)
ax.set_xlim(-0.2, 0.62)
ax.set_ylim(-0.15, 0.78)
figure(fig, "fig10_3_2")
plt.close(fig)
