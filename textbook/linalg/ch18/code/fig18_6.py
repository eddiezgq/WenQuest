"""图 18.6.1：方程 x₁ + 2x₂ = 5 的全部解是一条直线；离原点最近的解 x⁺ 在行空间里，与零空间垂直。"""
import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, arrow, axes_box, figure, plt

a = np.array([1.0, 2.0])
xp = a * 5 / (a @ a)
n = np.array([2.0, -1.0]) / np.sqrt(5)
fig, ax = plt.subplots(figsize=(5.6, 5.2))
axes_box(ax, 5.2)
t = np.linspace(-6, 6, 2)
ax.plot(xp[0] + t * n[0], xp[1] + t * n[1], color=INK, lw=1.8)
ax.text(3.3, -0.55, r"$x_1+2x_2=5$", fontsize=12)
ax.plot([-2.2 * a[0], 2.5 * a[0]], [-2.2 * a[1], 2.5 * a[1]], color=BLUE, lw=1, ls="--")
ax.text(-2.6, -4.7, T("行空间 C(Aᵀ)", "row space C(Aᵀ)"), color=BLUE, fontsize=11)
ax.plot([-4.5 * n[0] * 1.2, 4.5 * n[0] * 1.2], [-4.5 * n[1] * 1.2, 4.5 * n[1] * 1.2], color=GREEN, lw=1, ls="--")
ax.text(-4.9, 2.2, T("零空间 N(A)", "null space N(A)"), color=GREEN, fontsize=11)
arrow(ax, xp, RED, r"$\boldsymbol{x}^+=(1,2)^{\mathrm{T}}$", (0.15, 0.1))
other = xp + 1.6 * n * np.sqrt(5) / 2
arrow(ax, other, MUTED, T("另一个解", "another solution"), (0.0, -0.75), lw=1.2)
ax.plot([xp[0], other[0]], [xp[1], other[1]], color=GREEN, lw=2.5)
fig.tight_layout()
figure(fig, "fig18_6_1")
