"""10.1 节的示意图。

图 10.1.1：同一个参考系（车间地面）上的三个坐标系读同一点 P：直角坐标 {s}、极坐标、另一个直角坐标系 {w}。
图 10.1.2：AGV 沿圆弧转弯。(a) 以地面为参考系：零件静止，AGV 走圆；(b) 以 AGV 为参考系：零件绕点 (0, R0) 走圆。
"""
import math

import numpy as np

from _kin import C, G_COL, V_COL, arc, arrow, rotz
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 10.1.1
P = np.array([2.0, 0.5])
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.set_aspect("equal")
ax.axis("off")
ax.add_patch(plt.Rectangle((-0.6, -0.55), 3.9, 2.55, color="#eef1f3", zorder=0))
ax.text(3.22, -0.45, T("参考系：车间地面", "reference frame: workshop floor"), fontsize=9, color=G_COL, ha="right")
arrow(ax, (0, 0), (2.9, 0), C["x"], 1.2)
arrow(ax, (0, 0), (0, 1.7), C["y"], 1.2)
ax.text(2.93, -0.05, "$x_s$", color=C["x"], fontsize=12)
ax.text(0.05, 1.72, "$y_s$", color=C["y"], fontsize=12)
ax.text(-0.18, -0.2, "$O_s$", fontsize=11)
ax.plot([P[0], P[0]], [0, P[1]], ls=":", color=C["x"], lw=0.9)
ax.plot([0, P[0]], [P[1], P[1]], ls=":", color=C["y"], lw=0.9)
ax.plot([0, P[0]], [0, P[1]], color=C["ink"], lw=1.1)
arc(ax, (0, 0), 0.75, 0, math.atan2(P[1], P[0]), C["accent"], 1.2)
ax.text(0.8, 0.06, r"$\varphi$", color=C["accent"], fontsize=12)
ax.text(0.95, 0.33, r"$\rho$", fontsize=12)
ax.plot(*P, "o", color=C["ink"], ms=5, zorder=5)
ax.text(P[0] + 0.06, P[1] + 0.06, "P", fontsize=12)
# 另一个直角坐标系 {w}：原点 (2.8, 1.6)，转过 180°+30°
ow, aw = np.array([2.8, 1.6]), math.radians(210)
ex, ey = np.array([math.cos(aw), math.sin(aw)]), np.array([-math.sin(aw), math.cos(aw)])
arrow(ax, ow, ow + 0.8 * ex, C["x"], 1.2)
arrow(ax, ow, ow + 0.8 * ey, C["y"], 1.2)
ax.text(*(ow + 0.92 * ex + np.array([-0.05, -0.08])), "$x_w$", color=C["x"], fontsize=12)
ax.text(*(ow + 0.92 * ey + np.array([0.02, 0.0])), "$y_w$", color=C["y"], fontsize=12)
ax.text(ow[0] + 0.05, ow[1] + 0.05, "$O_w$", fontsize=11)
pw = np.array([(P - ow) @ ex, (P - ow) @ ey])
ax.text(-0.55, -0.78, T("同一点 P 的三组读数：", "Three readings of the same point P:"), fontsize=9.5)
ax.text(-0.55, -0.95, T(f"直角坐标 {{s}}：(x, y) = (2.0, 0.5) m", f"Cartesian {{s}}: (x, y) = (2.0, 0.5) m"), fontsize=9, color=C["ink"])
ax.text(-0.55, -1.10, T(f"极坐标：(ρ, φ) = ({math.hypot(*P):.3f} m, {math.degrees(math.atan2(P[1], P[0])):.2f}°)",
                       f"polar: (ρ, φ) = ({math.hypot(*P):.3f} m, {math.degrees(math.atan2(P[1], P[0])):.2f}°)"), fontsize=9, color=C["accent"])
ax.text(-0.55, -1.25, T(f"直角坐标 {{w}}：({pw[0]:.3f}, {pw[1]:.3f}) m", f"Cartesian {{w}}: ({pw[0]:.3f}, {pw[1]:.3f}) m"), fontsize=9, color=C["ink"])
ax.set_xlim(-0.65, 3.35)
ax.set_ylim(-1.32, 2.05)
figure(fig, "fig10_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 10.1.2
v, R0 = 0.5, 2.0
Om = v / R0
Cc = np.array([0.0, R0])
Pp = np.array([2.0, 0.5])


def agv_pose(t):
    psi = Om * t
    return Cc + R0 * np.array([math.sin(psi), -math.cos(psi)]), psi


def car(ax, o, psi, col, alpha=1.0):
    pts = np.array([[-0.22, -0.15], [0.22, -0.15], [0.22, 0.15], [-0.22, 0.15], [-0.22, -0.15]])
    R = rotz(psi)[:2, :2]
    q = (R @ pts.T).T + o
    ax.fill(q[:, 0], q[:, 1], color=col, alpha=0.35 * alpha, lw=0)
    ax.plot(q[:, 0], q[:, 1], color=col, lw=1.0, alpha=alpha)
    arrow(ax, o, o + R @ np.array([0.45, 0]), C["x"], 1.0)
    arrow(ax, o, o + R @ np.array([0, 0.45]), C["y"], 1.0)


fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.0, 4.4))
for a in (a1, a2):
    a.set_aspect("equal")
    a.axis("off")
# (a) 地面
t = np.linspace(0, 2 * math.pi, 200)
a1.plot(Cc[0] + R0 * np.cos(t), Cc[1] + R0 * np.sin(t), ls="--", color=G_COL, lw=0.9)
for tt, al in ((0.0, 0.5), (6.0, 1.0)):
    o, psi = agv_pose(tt)
    car(a1, o, psi, C["z"], al)
o0, _ = agv_pose(0.0)
o4, _ = agv_pose(6.0)
a1.text(o0[0] - 0.15, o0[1] - 0.45, "$t = 0$", fontsize=10)
a1.text(o4[0] + 0.3, o4[1] - 0.05, "$t = 6$ s", fontsize=10)
a1.plot(*Cc, "+", color=C["ink"], ms=8)
a1.text(Cc[0] + 0.08, Cc[1] + 0.08, "C", fontsize=11)
a1.plot(*Pp, "s", color=C["accent"], ms=7, zorder=6)
a1.text(Pp[0] + 0.1, Pp[1] - 0.05, T("零件 P（静止）", "part P (at rest)"), fontsize=9.5, color=C["accent"])
arrow(a1, (-2.4, -0.55), (-1.7, -0.55), C["x"], 1.1)
arrow(a1, (-2.4, -0.55), (-2.4, 0.15), C["y"], 1.1)
a1.text(-1.68, -0.62, "$x_s$", color=C["x"], fontsize=11)
a1.text(-2.35, 0.18, "$y_s$", color=C["y"], fontsize=11)
a1.set_title(T("(a) 以地面为参考系", "(a) Ground as the reference frame"), fontsize=11)
a1.set_xlim(-2.6, 3.4)
a1.set_ylim(-0.8, 4.3)
# (b) AGV
cb = np.array([0.0, R0])
d = float(np.linalg.norm(Pp - Cc))
a2.plot(cb[0] + d * np.cos(t), cb[1] + d * np.sin(t), ls="--", color=C["accent"], lw=1.0)
car(a2, np.zeros(2), 0.0, C["z"])
a2.text(0.12, -0.42, T("AGV（静止）", "AGV (at rest)"), fontsize=9.5, color=C["z"])
a2.plot(*cb, "+", color=C["ink"], ms=8)
a2.text(cb[0] + 0.08, cb[1] + 0.08, "C", fontsize=11)
for tt in (0.0, 6.0):
    o, psi = agv_pose(tt)
    pb = rotz(psi)[:2, :2].T @ (Pp - o)
    a2.plot(*pb, "s", color=C["accent"], ms=7, zorder=6)
    lab = "$t = 0$" if tt == 0 else "$t = 6$ s"
    a2.text(pb[0] - 0.15, pb[1] - 0.38, lab, fontsize=10)
    if tt == 6.0:
        vb = -np.array([-Om * pb[1], Om * pb[0]]) - np.array([v, 0])
        arrow(a2, pb, pb + 1.2 * vb, V_COL, 1.6)
        a2.text(pb[0] + 1.2 * vb[0] - 0.1, pb[1] + 1.2 * vb[1] - 0.4, r"$\dot p_b$", color=V_COL, fontsize=11)
a2.text(cb[0] - 2.4, cb[1] + 2.6, T("零件 P 的轨迹：以 C 为圆心、半径 |CP| 的圆", "path of P: circle about C, radius |CP|"),
        fontsize=9.5, color=C["accent"])
a2.text(0.5, 0.05, "$x_b$", color=C["x"], fontsize=11)
a2.text(-0.25, 0.48, "$y_b$", color=C["y"], fontsize=11)
a2.set_title(T("(b) 以 AGV 为参考系", "(b) The AGV as the reference frame"), fontsize=11)
a2.set_xlim(-2.8, 2.8)
a2.set_ylim(-0.8, 4.9)
figure(fig, "fig10_1_2")
plt.close(fig)
