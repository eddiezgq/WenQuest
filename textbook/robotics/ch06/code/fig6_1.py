"""6.1 节的示意图。

图 6.1.1：算例 6.1.2 的螺旋运动：零件从输送带（位姿 1）到夹具（位姿 2），等价于绕螺旋轴转 θ、同时沿轴移 d；
          零件中心走过一段螺旋线。
图 6.1.2：算例 6.1.1 的平面位移：两点连线的中垂线交于极点 c，绕 c 转 60° 完成整个位移。
"""
import math

import numpy as np

from _screw import C, axes3d, box3d, exp3, log3, pose, rot_z, tight3d
from bookout import T, figure, style

plt = style()
d = math.radians

# ---------------------------------------------------------------- 图 6.1.1
p1 = np.array([0.5, -0.2, 0.1])
T1 = pose(np.eye(3), p1)
T2 = pose(rot_z(d(90)), np.array([0.3, 0.4, 0.25]))
D = T2 @ np.linalg.inv(T1)
R, p = D[:3, :3], D[:3, 3]
s, th = log3(R)
dd = float(s @ p)
pp = p - dd * s
q = 0.5 * (pp + np.cross(s, pp) / math.tan(th / 2))


def at(f):
    Rf = exp3(s * th * f)
    return pose(Rf, q + Rf @ (p1 - q) + f * dd * s)


fig, ax = axes3d(plt, size=(6.4, 4.0), elev=24, azim=-60)
dims = (0.14, 0.09, 0.06)


def part(Tm, face, edge, alpha, lw=2.4):
    box3d(ax, Tm, dims, face=face, edge=edge, alpha=alpha)


part(at(0), "#d9dee2", C["muted"], 0.6)
for f in (1 / 3, 2 / 3):
    part(at(f), "#f2f2f2", "#c4c4c4", 0.25, 1.2)
part(at(1), "#f3e2b3", C["accent"], 0.85)
H = np.array([at(f)[:3, 3] for f in np.linspace(0, 1, 120)])
ax.plot(*H.T, color=C["accent"], lw=1.8)
# 螺旋轴
z0, z1 = 0.0, 0.36
ax.plot([q[0], q[0]], [q[1], q[1]], [z0, z1], color=C["ink"], lw=1.4, ls="-.")
ax.quiver(q[0], q[1], z1 - 0.05, 0, 0, 0.06, color=C["ink"], lw=1.6, arrow_length_ratio=0.4)
ax.text(q[0] + 0.02, q[1] + 0.02, z1 + 0.01, r"$\hat s$", fontsize=13)
ax.scatter([q[0]], [q[1]], [0], color=C["ink"], s=14)
ax.text(q[0] + 0.03, q[1] - 0.03, -0.02, r"$q$", fontsize=13)
# 到轴的距离、平移 d
c1, c2 = p1, at(1)[:3, 3]
f1 = np.array([q[0], q[1], c1[2]])
f2 = np.array([q[0], q[1], c2[2]])
ax.plot(*np.array([f1, c1]).T, color=C["muted"], lw=0.9, ls=":")
ax.plot(*np.array([f2, c2]).T, color=C["muted"], lw=0.9, ls=":")
ax.plot([q[0]] * 2, [q[1]] * 2, [c1[2], c2[2]], color=C["z"], lw=3.0)
ax.text(q[0] + 0.03, q[1] + 0.03, (c1[2] + c2[2]) / 2 + 0.03, r"$d = h\theta$", color=C["z"], fontsize=12, ha="left")
arc = np.array([q + exp3(s * th * f) @ ((c1 - f1) * 0.45) + np.array([0, 0, c1[2]]) for f in np.linspace(0, 1, 40)])
ax.plot(*arc.T, color=C["accent"], lw=1.2)
ax.text(*(arc[22] + np.array([0.0, 0.0, 0.02])), r"$\theta$", color=C["accent"], fontsize=13)
ax.text(*(c1 + np.array([0.0, 0.0, -0.095])), T("位姿 1（输送带）", "pose 1 (conveyor)"), fontsize=9.5, color=C["muted"], ha="center")
ax.text(*(c2 + np.array([0.0, 0.0, 0.06])), T("位姿 2（夹具）", "pose 2 (fixture)"), fontsize=9.5, color=C["accent"], ha="center")
ax.text2D(1.0, 0.13, T("零件中心的\n螺旋线", "helix of the\npart centre"), transform=ax.transAxes, fontsize=9.5, color=C["accent"], ha="right")
tight3d(ax, np.vstack([H, [q + [0, 0, z0]], [q + [0, 0, z1]], [c1 + [0.08, -0.06, -0.06]], [c2 + [-0.08, 0.08, 0.06]]]), pad=0.02, zoom=1.45)
figure(fig, "fig6_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 6.1.2
def rot2(t):
    return np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])


pA, pB, ph = np.array([0.30, 0.05]), np.array([0.54, 0.13]), d(60)
R2 = rot2(ph)
p2 = pB - R2 @ pA
c = np.linalg.solve(np.eye(2) - R2, p2)
part = np.array([[-0.03, -0.025], [0.18, -0.025], [0.18, 0.025], [-0.03, 0.025], [-0.03, -0.025]])   # 参考点在 (0, 0)
PA = part + pA
PB = (R2 @ part.T).T + pB
P1, P2 = pA, pA + np.array([0.15, 0.0])
Q1, Q2 = R2 @ P1 + p2, R2 @ P2 + p2

fig, ax = plt.subplots(figsize=(5.4, 4.6))
ax.set_aspect("equal")
ax.axis("off")
ax.annotate("", xy=(0.66, 0), xytext=(-0.03, 0), arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=1.0))
ax.annotate("", xy=(0, 0.52), xytext=(0, -0.03), arrowprops=dict(arrowstyle="-|>", color=C["y"], lw=1.0))
ax.text(0.665, -0.02, "$x$", color=C["x"], fontsize=12)
ax.text(0.01, 0.52, "$y$", color=C["y"], fontsize=12)
ax.fill(PA[:, 0], PA[:, 1], color="#d9dee2", alpha=0.7)
ax.plot(PA[:, 0], PA[:, 1], color=C["muted"], lw=0.9)
ax.fill(PB[:, 0], PB[:, 1], color="#f3e2b3", alpha=0.8)
ax.plot(PB[:, 0], PB[:, 1], color=C["accent"], lw=1.0)
for P, Q, name in ((P1, Q1, "1"), (P2, Q2, "2")):
    ax.plot(*np.array([P, Q]).T, color=C["muted"], lw=0.8, ls="--")
    m = (P + Q) / 2
    u = (c - m) / np.linalg.norm(c - m)
    seg = np.array([m - 0.05 * u, c + 0.07 * u])
    ax.plot(*seg.T, color=C["z"], lw=0.9)
    ax.plot(*m, "|", color=C["z"], ms=6)
    ax.plot(*P, "o", color=C["ink"], ms=3.5)
    ax.plot(*Q, "o", color=C["ink"], ms=3.5)
    ax.text(P[0] - 0.005, P[1] - 0.045, f"$P_{name}$", fontsize=11)
    ax.text(Q[0] + 0.012, Q[1] - 0.005, f"$P_{name}'$", fontsize=11)
ax.plot(*c, "o", color=C["accent"], ms=6, zorder=6)
ax.text(c[0] - 0.045, c[1] + 0.012, "$c$", fontsize=13, color=C["accent"])
for P in (P1, Q1):
    ax.plot(*np.array([c, P]).T, color=C["accent"], lw=0.8, ls=":")
rA = np.linalg.norm(pA - c)
a0 = math.atan2(*(pA - c)[::-1])
t = np.linspace(a0, a0 + ph, 50)
ax.plot(c[0] + rA * np.cos(t), c[1] + rA * np.sin(t), color=C["accent"], lw=1.2)
am = a0 + ph / 2
ax.text(c[0] + 0.085 * math.cos(am) - 0.01, c[1] + 0.085 * math.sin(am) - 0.012, r"$\varphi$", fontsize=12, color=C["accent"])
t2 = np.linspace(a0, a0 + ph, 30)
ax.plot(c[0] + 0.06 * np.cos(t2), c[1] + 0.06 * np.sin(t2), color=C["accent"], lw=0.9)
ax.text(0.30, -0.075, T("位姿 A", "pose A"), fontsize=10, color=C["muted"])
ax.text(0.585, 0.40, T("位姿 B", "pose B"), fontsize=10, color=C["accent"])
ax.text(0.06, 0.40, T("两条中垂线\n交于极点 c", "the two perpendicular\nbisectors meet at the pole c"), fontsize=9.5, color=C["z"])
ax.set_xlim(-0.05, 0.70)
ax.set_ylim(-0.10, 0.55)
figure(fig, "fig6_1_2")
plt.close(fig)
