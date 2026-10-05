"""图 10.3.1：向平面投影。A = [[1, 0], [1, 1], [1, 2]] 的列空间是 ℝ³ 中的平面；b = (6, 0, 0) 的投影 p = Pb = (5, 2, −1)，误差 e = b − p = (1, −2, 1)
垂直于平面。平面上另一点 q 离 b 更远：‖b − q‖² = ‖e‖² + ‖p − q‖²。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow3, figure, plt, view3

a1, a2 = np.array([1.0, 1, 1]), np.array([0.0, 1, 2])
b, p = np.array([6.0, 0, 0]), np.array([5.0, 2, -1])
e = b - p
q = 3.0 * a1 + 0.5 * a2
P, _ = view3(75, 25)
fig, ax = plt.subplots(figsize=(7.0, 5.0))
corners = [P(s * a1 + t * a2) for s, t in ((-1.0, -2.2), (6.5, -2.2), (6.5, 1.8), (-1.0, 1.8))]
ax.add_patch(plt.Polygon(corners, closed=True, fc=ACC, alpha=0.22, ec=ACC))
arrow3(ax, P, (0, 0, 0), a1, MUTED, "a₁", lw=1.6, size=11)
arrow3(ax, P, (0, 0, 0), a2, MUTED, "a₂", lw=1.6, size=11)
arrow3(ax, P, (0, 0, 0), b, BLUE, "b", off=(-0.15, 0.2))
arrow3(ax, P, (0, 0, 0), p, RED, "p = Pb", off=(-0.2, -0.45))
arrow3(ax, P, p, b, GREEN)
ax.text(*(P((p + b) / 2) + np.array([-1.35, -0.1])), "e = b − p", color=GREEN, fontsize=12)
ax.plot(*np.c_[P(q), P(b)], color=MUTED, lw=1.2, ls="--")
ax.plot(*P(q), "o", color=INK, ms=4)
ax.text(*(P(q) + np.array([-0.35, -0.35])), "q", fontsize=12, color=INK)
ax.plot(*np.c_[P(p), P(q)], color=MUTED, lw=1, ls=":")
u = (q - p) / np.linalg.norm(q - p) * 0.35
w = e / np.linalg.norm(e) * 0.35
ax.plot(*np.c_[P(p + u), P(p + u + w), P(p + w)], color=INK, lw=1)
ax.plot(*P(np.zeros(3)), "o", color=INK, ms=4)
top = max(corners, key=lambda c: c[1])
ax.text(*top + np.array([0.2, -0.6]), "C(A)", fontsize=13, color=INK)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title(T("b 在平面上的投影 p：误差 e 与平面垂直，p 是平面上离 b 最近的点", "the projection p of b onto the plane: e is perpendicular, p is the closest point"), fontsize=11)
figure(fig, "fig10_3_1")
