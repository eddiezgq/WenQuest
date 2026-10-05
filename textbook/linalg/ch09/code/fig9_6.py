"""图 9.6.1：同一个向量 v = (3, 5) 在两组基下的坐标。左：标准基，坐标 (3, 5)；右：基 b1 = (1, 1)、b2 = (−1, 1)，v = 4b1 + 1b2，坐标 (4, 1)。"""
import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, arrow, figure, plt

v = np.array([3.0, 5.0])
fig, axs = plt.subplots(1, 2, figsize=(8.6, 4.4))
for ax, (b1, b2, name, coef) in zip(axs, [(np.array([1.0, 0]), np.array([0.0, 1]), T("标准基：v = 3e₁ + 5e₂", "standard basis: v = 3e₁ + 5e₂"), (3, 5)),
                                          (np.array([1.0, 1]), np.array([-1.0, 1]), T("新基：v = 4b₁ + 1b₂", "new basis: v = 4b₁ + 1b₂"), (4, 1))]):
    ax.set_aspect("equal")
    ax.set_xlim(-2.5, 5.5)
    ax.set_ylim(-1.0, 6.5)
    ax.axis("off")
    for k in range(-6, 8):
        ax.plot(*np.c_[k * b1 - 8 * b2, k * b1 + 8 * b2], color=MUTED, lw=0.5, alpha=0.6)
        ax.plot(*np.c_[k * b2 - 8 * b1, k * b2 + 8 * b1], color=MUTED, lw=0.5, alpha=0.6)
    arrow(ax, coef[0] * b1, RED, lw=1.6)
    arrow(ax, coef[1] * b2, GREEN, lw=1.6, start=coef[0] * b1)
    arrow(ax, b1, RED, "b₁" if coef == (4, 1) else "e₁", offset=(0.1, -0.35), lw=3)
    arrow(ax, b2, GREEN, "b₂" if coef == (4, 1) else "e₂", offset=(-0.45, 0.05), lw=3)
    arrow(ax, v, BLUE, "v", offset=(0.12, 0.0), lw=2.4, size=14)
    ax.set_title(name, fontsize=12, color=INK)
figure(fig, "fig9_6_1")
