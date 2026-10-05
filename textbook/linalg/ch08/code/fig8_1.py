"""图 8.1.1：本章例子矩阵 A 的列空间是 ℝ³ 中的一个平面，由主元列 a₁ = (1, 2, 3)、a₃ = (0, 1, 1) 张成；
b = (1, 3, 4) 在平面上（Ax = b 有解），b′ = (1, 3, 5) 不在（无解）。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, RED, T, figure, plt

a1, a3 = np.array([1.0, 2, 3]), np.array([0.0, 1, 1])
fig = plt.figure(figsize=(6.2, 5.0))
ax = fig.add_subplot(projection="3d")
s = np.linspace(-0.6, 1.6, 2)
S, U = np.meshgrid(s, s)
P = S[..., None] * a1 + U[..., None] * a3
ax.plot_surface(P[..., 0], P[..., 1], P[..., 2], color=ACC, alpha=0.3, edgecolor="none")
for v, c, nm in ((a1, RED, "a₁"), (a3, GREEN, "a₃"), (np.array([1.0, 3, 4]), BLUE, "b"), (np.array([1.0, 3, 5]), INK, "b′")):
    ax.quiver(0, 0, 0, *v, color=c, lw=2.2, arrow_length_ratio=0.08)
    ax.text(*(v * 1.06), nm, color=c, fontsize=12)
ax.set_xlabel("b₁")
ax.set_ylabel("b₂")
ax.set_zlabel("b₃")
ax.view_init(elev=15, azim=-35)
ax.set_title(T("列空间 C(A)：ℝ³ 中的平面", "column space C(A): a plane in ℝ³"), fontsize=11)
fig.tight_layout()
figure(fig, "fig8_1_1")
