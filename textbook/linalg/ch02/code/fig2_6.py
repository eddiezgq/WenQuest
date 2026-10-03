"""图 2.6.1：平面 n·(x − P₁) = 0 与点到平面的距离 |n·(Q − P₁)|/‖n‖；直线 x = S + t d 与夹具上一点 K 到直线的距离。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

fig = plt.figure(figsize=(10.6, 4.6))
a1 = fig.add_subplot(1, 2, 1, projection="3d")
n = np.array([0.25, -0.15, 1.0])
P1 = np.array([0.0, 0.0, 0.0])
def zpl(x, y):
    return -(n[0] * x + n[1] * y) / n[2]
corners = [np.array([x, y, zpl(x, y)]) for x, y in ((-1.5, -1.2), (1.5, -1.2), (1.5, 1.2), (-1.5, 1.2))]
a1.add_collection3d(Poly3DCollection([corners], color=BLUE, alpha=0.18))
Q = np.array([0.6, 0.4, 1.3])
foot = Q - (n @ (Q - P1)) / (n @ n) * n
a1.quiver(*P1, *(n / np.linalg.norm(n)), color=RED, arrow_length_ratio=0.12, lw=2.2)
a1.text(*(n / np.linalg.norm(n) * 1.1), r"$\boldsymbol{n}$", color=RED, fontsize=13)
a1.quiver(*P1, *(Q - P1), color=GREEN, arrow_length_ratio=0.06, lw=1.6)
a1.plot(*zip(Q, foot), color=INK, ls="--", lw=1.2)
a1.scatter(*Q, color=GREEN, s=25)
a1.scatter(*P1, color=INK, s=20)
a1.scatter(*foot, color=INK, s=12)
a1.text(*(Q + np.array([0.05, 0, 0.08])), "Q", fontsize=12)
a1.text(*(P1 + np.array([-0.35, 0, -0.25])), r"$P_1$", fontsize=12)
a1.text(*(0.5 * (Q + foot) + np.array([0.08, 0, 0])), T("距离", "distance"), fontsize=10)
a1.set_xlim(-1.5, 1.5)
a1.set_ylim(-1.2, 1.2)
a1.set_zlim(-0.6, 1.6)
a1.set_box_aspect((3, 2.4, 2.2))
a1.view_init(18, -60)
a1.set_xticks([])
a1.set_yticks([])
a1.set_zticks([])
a1.set_title(T("平面、法向量与点到平面的距离", "Plane, normal vector, point-to-plane distance"), fontsize=11)
a2 = fig.add_subplot(1, 2, 2)
S, d = np.array([0.5, 0.6]), np.array([3.0, 1.2])
O = np.array([2.2, 2.4])
ts = np.array([-0.15, 1.25])
a2.plot(S[0] + ts * d[0], S[1] + ts * d[1], color=BLUE, lw=1.8)
a2.annotate("", xy=S + d, xytext=S, arrowprops=dict(arrowstyle="-|>", color=ACC, lw=2.2, mutation_scale=14))
t_ = (O - S) @ d / (d @ d)
F = S + t_ * d
a2.plot(*zip(O, F), color=INK, ls="--", lw=1.2)
a2.annotate("", xy=O, xytext=S, arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.4, mutation_scale=12))
for P, name, off in ((S, "S", (-0.25, -0.25)), (O, T("K（夹具上一点）", "K (point on the fixture)"), (0.08, 0.1)), (F, "", (0, 0))):
    a2.plot(*P, "o", color=INK, ms=4)
    if name:
        a2.text(P[0] + off[0], P[1] + off[1], name, fontsize=11)
a2.text(*(S + d + np.array([0.05, -0.3])), r"$\boldsymbol{d}$", color=ACC, fontsize=13)
a2.text(*(S + 0.5 * (O - S) + np.array([-0.55, 0.05])), r"$K-S$", color=GREEN, fontsize=12)
a2.text(*(0.5 * (O + F) + np.array([0.08, 0])), r"$\dfrac{\Vert\boldsymbol{d}\times(K-S)\Vert}{\Vert\boldsymbol{d}\Vert}$", fontsize=12)
a2.text(3.9, 1.7, r"$\boldsymbol{x}=S+t\boldsymbol{d}$", color=BLUE, fontsize=12)
a2.set_xlim(0, 4.8)
a2.set_ylim(0, 3.2)
a2.set_aspect("equal")
a2.axis("off")
a2.set_title(T("直线的参数方程与点到直线的距离", "Parametric line and point-to-line distance"), fontsize=11)
fig.tight_layout()
figure(fig, "fig2_6_1")
