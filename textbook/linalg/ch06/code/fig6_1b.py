"""图 6.1.2：B 的三列张成的平行六面体，体积 det B = 6，等于混合积 b₁ · (b₂ × b₃)。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, RED, T, figure, plt

B = np.array([[1.0, 1.0, 0.0], [0.0, 2.0, 1.0], [0.0, 0.0, 3.0]])
b = [B[:, i] for i in range(3)]
fig = plt.figure(figsize=(5.6, 4.8))
ax = fig.add_subplot(projection="3d")
corners = {(i, j, k): i * b[0] + j * b[1] + k * b[2] for i in (0, 1) for j in (0, 1) for k in (0, 1)}
for (i, j, k), p in corners.items():
    for d in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
        q = (i + d[0], j + d[1], k + d[2])
        if q in corners:
            r = corners[q]
            ax.plot([p[0], r[0]], [p[1], r[1]], [p[2], r[2]], color=INK, lw=0.8, alpha=0.6)
for v, c, name in zip(b, (RED, GREEN, BLUE), ("b₁", "b₂", "b₃")):
    ax.quiver(0, 0, 0, *v, color=c, lw=2.5, arrow_length_ratio=0.12)
    ax.text(*(v * 1.08), name, color=c, fontsize=12)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
ax.set_title(T("平行六面体：体积 = det B = 6", "parallelepiped: volume = det B = 6"), fontsize=11)
ax.view_init(elev=22, azim=-58)
fig.tight_layout()
figure(fig, "fig6_1_2")
