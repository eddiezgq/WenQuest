"""图 8.5.1：四个基本子空间的“大图”。左边 ℝⁿ：行空间（维数 r）与零空间（n − r）；右边 ℝᵐ：列空间（r）与左零空间（m − r）。
A 把行空间中的 x_r 送到列空间中的 Ax，把零空间中的 x_n 送到零。"""
from matplotlib.patches import FancyArrowPatch, Polygon

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, ax = plt.subplots(figsize=(10.0, 5.2))
ax.set_xlim(-0.5, 10.5)
ax.set_ylim(0, 6)
ax.axis("off")


def box(pts, color, text, sub):
    ax.add_patch(Polygon(pts, closed=True, fc=color, ec=INK, alpha=0.25, lw=1.2))
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    ax.text(cx, cy + 0.15, text, ha="center", va="center", fontsize=12, color=INK)
    ax.text(cx, cy - 0.3, sub, ha="center", va="center", fontsize=11, color=INK)


box([(0.6, 3.1), (2.6, 5.1), (4.0, 3.7), (2.0, 1.7)], BLUE, T("行空间 C(Aᵀ)", "row space C(Aᵀ)"), T("维数 r", "dim r"))
box([(0.6, 2.9), (2.0, 1.5), (1.2, 0.7), (-0.2, 2.1)], GREEN, T("零空间 N(A)", "null space N(A)"), "n − r")
box([(6.0, 3.7), (7.4, 5.1), (9.4, 3.1), (8.0, 1.7)], RED, T("列空间 C(A)", "column space C(A)"), T("维数 r", "dim r"))
box([(8.0, 1.5), (9.4, 2.9), (10.2, 2.1), (8.8, 0.7)], ACC, T("左零空间 N(Aᵀ)", "left null space N(Aᵀ)"), "m − r")
ax.plot([8.0], [1.6], "o", color=INK, ms=6)
ax.text(7.75, 1.25, "0", fontsize=12)
ax.plot([2.0], [1.6], "o", color=INK, ms=6)
ax.text(2.15, 1.25, "0", fontsize=12)
ax.text(2.0, 5.6, "ℝⁿ", fontsize=16, ha="center")
ax.text(8.0, 5.6, "ℝᵐ", fontsize=16, ha="center")
for (a, b, txt, c) in (((3.2, 3.6), (6.8, 3.6), "A x_r = A x", BLUE), ((1.1, 1.9), (7.95, 1.62), "A x_n = 0", GREEN)):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=16, color=c, lw=1.6, connectionstyle="arc3,rad=-0.15"))
    ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + (0.45 if c == BLUE else -0.55), txt, ha="center", fontsize=12, color=c)
ax.text(5.0, 0.25, T("x = x_r + x_n；行空间 ⊥ 零空间，列空间 ⊥ 左零空间（第 10 章）", "x = x_r + x_n; row space ⊥ null space, column space ⊥ left null space (Chapter 10)"),
        ha="center", fontsize=10, color=MUTED)
figure(fig, "fig8_5_1")
