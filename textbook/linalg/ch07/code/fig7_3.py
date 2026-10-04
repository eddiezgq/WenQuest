"""图 7.3.1：左：过原点的平面 x + y + z = 0 是子空间，平面上两点之和仍在平面上；
右：不过原点的平面 x + y + z = 1 不是子空间，两点之和跑到了平面外。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, RED, T, figure, plt

fig = plt.figure(figsize=(10.6, 4.6))
s = np.linspace(-1.5, 1.5, 2)
S, Tt = np.meshgrid(s, s)
for k, (c, u, w, name) in enumerate(((0.0, np.array([1.0, -1, 0]), np.array([0.5, 0.5, -1]), T("x + y + z = 0：子空间", "x + y + z = 0: a subspace")),
                                      (1.0, np.array([1.0, 0, 0]), np.array([0.0, 1, 0]), T("x + y + z = 1：不是子空间", "x + y + z = 1: not a subspace")))):
    ax = fig.add_subplot(1, 2, k + 1, projection="3d")
    ax.plot_surface(S, Tt, c - S - Tt, color=ACC, alpha=0.35, edgecolor="none")
    for v, col, nm in ((u, RED, "u"), (w, GREEN, "w"), (u + w, BLUE, "u + w")):
        ax.quiver(0, 0, 0, *v, color=col, lw=2.2, arrow_length_ratio=0.1)
        ax.text(*(v * 1.1), nm, color=col, fontsize=11)
    ax.scatter([0], [0], [0], color=INK, s=20)
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_zlim(-2, 3)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    ax.view_init(elev=18, azim=-60)
    ax.set_title(name, fontsize=11)
fig.tight_layout()
figure(fig, "fig7_3_1")
