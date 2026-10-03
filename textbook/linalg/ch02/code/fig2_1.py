"""图 2.1.1：向量是位移——车间地面上 AGV 的位移 d = B − A，同一个位移从 C 出发；UR5e 末端点的位置向量。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow, figure, plt

fig = plt.figure(figsize=(10.4, 4.4))
a1 = fig.add_subplot(1, 2, 1)
A, B, C = np.array([2.0, 1.0]), np.array([5.0, 5.0]), np.array([6.0, 2.0])
d = B - A
for x in range(0, 11):
    a1.axvline(x, color=MUTED, lw=0.4, alpha=0.4)
for y in range(0, 8):
    a1.axhline(y, color=MUTED, lw=0.4, alpha=0.4)
arrow(a1, d, BLUE, None, start=A, lw=2.4)
arrow(a1, d, BLUE, None, start=C, lw=2.4)
arrow(a1, A, MUTED, None, lw=1.0)
arrow(a1, B, MUTED, None, lw=1.0)
for P, name, off in ((A, "A (2, 1)", (0.15, -0.45)), (B, "B (5, 5)", (0.15, 0.1)), (C, "C (6, 2)", (0.15, -0.45)), (C + d, "C + d", (0.15, 0.1))):
    a1.plot(*P, "o", color=INK, ms=5, zorder=6)
    a1.text(P[0] + off[0], P[1] + off[1], name, fontsize=10)
a1.text(1.2, 3.6, r"$\boldsymbol{d}=(3,4)^{\mathrm{T}}$", color=BLUE, fontsize=12)
a1.text(8.0, 3.2, r"$\boldsymbol{d}$", color=BLUE, fontsize=12)
a1.text(0.15, 0.25, T("O（车间原点）", "O (workshop origin)"), fontsize=9, color=MUTED)
a1.set_xlim(0, 10)
a1.set_ylim(0, 7.5)
a1.set_aspect("equal")
a1.set_xlabel("x / m")
a1.set_ylabel("y / m")
a1.set_title(T("同一个位移，可以从任何地方出发", "One displacement, from any starting point"), fontsize=11)
a2 = fig.add_subplot(1, 2, 2, projection="3d")
p = np.array([0.652, 0.134, 0.335])
for v, c, n in ((np.array([0.8, 0, 0]), RED, "x"), (np.array([0, 0.8, 0]), GREEN, "y"), (np.array([0, 0, 0.6]), BLUE, "z")):
    a2.quiver(0, 0, 0, *v, color=c, arrow_length_ratio=0.08, lw=1.2)
    a2.text(*(1.05 * v), n, color=c, fontsize=11)
a2.quiver(0, 0, 0, *p, color=ACC, arrow_length_ratio=0.1, lw=2.4)
a2.plot([p[0], p[0]], [p[1], p[1]], [0, p[2]], color=MUTED, ls="--", lw=0.8)
a2.plot([0, p[0], p[0]], [p[1], p[1], 0], [0, 0, 0], color=MUTED, ls="--", lw=0.8)
a2.plot([p[0], p[0]], [0, p[1]], [0, 0], color=MUTED, ls="--", lw=0.8)
a2.text(p[0] - 0.45, p[1], p[2] + 0.12, r"$\boldsymbol{p}=(0.652,\,0.134,\,0.335)^{\mathrm{T}}$", fontsize=10, color=ACC)
a2.set_xlim(0, 0.8)
a2.set_ylim(0, 0.8)
a2.set_zlim(0, 0.6)
a2.set_box_aspect((0.8, 0.8, 0.6))
a2.view_init(22, -60)
a2.set_xlabel("x / m")
a2.set_ylabel("y / m")
a2.set_zlabel("z / m")
a2.set_title(T("UR5e 末端点的位置向量（基座坐标系）", "Position vector of the UR5e tool point (base frame)"), fontsize=11)
fig.tight_layout()
figure(fig, "fig2_1_1")
