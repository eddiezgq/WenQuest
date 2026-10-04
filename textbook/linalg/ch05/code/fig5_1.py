"""图 5.1.1：A 把网格和小旗拉歪，A⁻¹ 把它还原；奇异矩阵 S = [[1, 0.5], [0.6, 0.3]] 把平面压成一条直线，无法还原。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, RED, T, arrow, figure, plt

A = np.array([[1.2, 0.8], [0.2, 1.0]])
P = np.array([[1.0, 0.5], [0.6, 0.3]])
flag = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 0.5], [0.5, 0.5], [0.5, 1.0], [0.0, 1.0], [0.0, 0.0]]).T
fig, axs = plt.subplots(1, 4, figsize=(12.4, 3.5))
panels = ((np.eye(2), T("原图", "original")), (A, T("A 作用后", "after A")),
          (np.linalg.inv(A) @ A, T("再用 A⁻¹：还原", "then A⁻¹: restored")), (P, T("奇异矩阵：压成直线", "singular: flattened")))
for ax, (M, name) in zip(axs, panels):
    for i in range(-3, 4):
        for p0, q0 in (([i, -3], [i, 3]), ([-3, i], [3, i])):
            p, q = M @ p0, M @ q0
            ax.plot([p[0], q[0]], [p[1], q[1]], color=BLUE, lw=0.6, alpha=0.35)
    F = M @ flag
    ax.fill(F[0], F[1], color=ACC, alpha=0.6, ec=INK)
    arrow(ax, M[:, 0], RED, None, lw=2.2)
    arrow(ax, M[:, 1], GREEN, None, lw=2.2)
    ax.set_xlim(-1.2, 2.6)
    ax.set_ylim(-0.9, 2.0)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(name, fontsize=11)
fig.tight_layout()
figure(fig, "fig5_1_1")
