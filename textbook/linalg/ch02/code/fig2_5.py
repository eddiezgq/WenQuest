"""图 2.5.1：叉积——u × v 垂直于 u、v，长度等于平行四边形面积，方向按右手定则；混合积是平行六面体的体积。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

fig = plt.figure(figsize=(10.6, 4.6))
a1 = fig.add_subplot(1, 2, 1, projection="3d")
u, v = np.array([2.0, 0.3, 0.0]), np.array([0.6, 1.6, 0.0])
w = np.cross(u, v)
a1.add_collection3d(Poly3DCollection([[np.zeros(3), u, u + v, v]], color=ACC, alpha=0.3))
for vec_, col, name in ((u, BLUE, r"$\boldsymbol{u}$"), (v, GREEN, r"$\boldsymbol{v}$"), (w / 1.6, RED, r"$\boldsymbol{u}\times\boldsymbol{v}$")):
    a1.quiver(0, 0, 0, *vec_, color=col, arrow_length_ratio=0.1, lw=2.4)
    a1.text(*(vec_ * 1.08), name, color=col, fontsize=12)
a1.text(1.3, 0.9, 0, T("面积 = ‖u × v‖", "area = ‖u × v‖"), fontsize=10)
a1.set_xlim(0, 2.6)
a1.set_ylim(0, 2.0)
a1.set_zlim(0, 2.2)
a1.set_box_aspect((2.6, 2.0, 2.2))
a1.view_init(22, -55)
a1.set_xticks([])
a1.set_yticks([])
a1.set_zticks([])
a1.set_title(T("叉积：垂直于两者，长度是面积（红箭头按比例缩短）", "Cross product: perpendicular to both, length = area (red arrow shortened)"), fontsize=11)
a2 = fig.add_subplot(1, 2, 2, projection="3d")
a, b, c = np.array([2.0, 0, 0]), np.array([1.0, 3, 0]), np.array([1.0, 1, 4])
V = [np.zeros(3), a, a + b, b, c, a + c, a + b + c, b + c]
faces = [[V[0], V[1], V[2], V[3]], [V[4], V[5], V[6], V[7]], [V[0], V[1], V[5], V[4]], [V[2], V[3], V[7], V[6]], [V[1], V[2], V[6], V[5]], [V[0], V[3], V[7], V[4]]]
a2.add_collection3d(Poly3DCollection(faces, facecolor=ACC, edgecolor=MUTED, alpha=0.15, lw=0.6))
for vec_, col, name in ((a, BLUE, r"$\boldsymbol{a}$"), (b, GREEN, r"$\boldsymbol{b}$"), (c, RED, r"$\boldsymbol{c}$")):
    a2.quiver(0, 0, 0, *vec_, color=col, arrow_length_ratio=0.08, lw=2.4)
    a2.text(*(vec_ * 1.06), name, color=col, fontsize=13)
a2.text(0.0, 0.0, 5.0, T("体积 = |a·(b × c)| = 24", "volume = |a·(b × c)| = 24"), fontsize=10)
a2.set_xlim(0, 4)
a2.set_ylim(0, 4)
a2.set_zlim(0, 4)
a2.set_box_aspect((1, 1, 1))
a2.view_init(20, -60)
a2.set_xticks([])
a2.set_yticks([])
a2.set_zticks([])
a2.set_title(T("混合积：平行六面体的体积", "Triple product: volume of the parallelepiped"), fontsize=11)
fig.tight_layout()
figure(fig, "fig2_5_1")
