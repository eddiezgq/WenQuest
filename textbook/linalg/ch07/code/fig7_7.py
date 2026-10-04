"""图 7.7.1：同一个向量 x = (7, 11) 在两组基下的坐标。左：标准基，坐标 (7, 11)；右：基 b₁ = (2, 1)、b₂ = (1, 3)，
沿 b₁、b₂ 方向的斜网格，坐标 (2, 3)。"""
import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, arrow, figure, plt

fig, axs = plt.subplots(1, 2, figsize=(10.4, 4.6))
x = np.array([7.0, 11])
for ax, (b1, b2, c, name) in zip(axs, ((np.array([1.0, 0]), np.array([0.0, 1]), (7, 11), T("标准基：坐标 (7, 11)", "standard basis: (7, 11)")),
                                       (np.array([2.0, 1]), np.array([1.0, 3]), (2, 3), T("基 b₁、b₂：坐标 (2, 3)", "basis b₁, b₂: (2, 3)")))):
    for i in range(-2, 14):
        p, q = i * b1 - 3 * b2, i * b1 + 14 * b2
        ax.plot([p[0], q[0]], [p[1], q[1]], color=MUTED, lw=0.5, alpha=0.5)
        p, q = -3 * b1 + i * b2, 14 * b1 + i * b2
        ax.plot([p[0], q[0]], [p[1], q[1]], color=MUTED, lw=0.5, alpha=0.5)
    arrow(ax, c[0] * b1, RED, None, lw=2)
    arrow(ax, c[1] * b2, GREEN, None, lw=2, start=tuple(c[0] * b1))
    arrow(ax, b1, RED, "b₁" if c != (7, 11) else "e₁", lw=3)
    arrow(ax, b2, GREEN, "b₂" if c != (7, 11) else "e₂", lw=3)
    ax.plot(*x, "o", color=BLUE, ms=7)
    ax.text(x[0] + 0.3, x[1], "x", color=BLUE, fontsize=12)
    ax.set_xlim(-1, 12)
    ax.set_ylim(-1, 12.5)
    ax.set_aspect("equal")
    ax.set_title(name, fontsize=11)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig7_7_1")
