"""图 6.1.1：单位正方形在 A = [[3, 1], [1, 2]] 下变成面积为 5 的平行四边形；交换两列后行列式为 −5：
面积相同，但 e₁ 的像到 e₂ 的像由逆时针变成顺时针（翻面）。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow, figure, plt

A = np.array([[3.0, 1.0], [1.0, 2.0]])
F = A[:, ::-1]
sq = np.array([[0, 1, 1, 0, 0], [0, 0, 1, 1, 0]], float)
fig, axs = plt.subplots(1, 3, figsize=(11.6, 4.0))
for ax, (M, name) in zip(axs, ((np.eye(2), T("单位正方形：det I = 1", "unit square: det I = 1")),
                                (A, T("A：面积 5，det A = 5", "A: area 5, det A = 5")),
                                (F, T("交换两列：det = −5（翻面）", "columns swapped: det = −5 (flipped)")))):
    P = M @ sq
    ax.fill(P[0], P[1], color=ACC if np.linalg.det(M) > 0 else "#c9a0dc", alpha=0.55, ec=INK)
    arrow(ax, M[:, 0], RED, None, lw=2.4)
    arrow(ax, M[:, 1], GREEN, None, lw=2.4)
    # 方向：从第 1 列转到第 2 列的小弧
    a0, a1 = np.arctan2(M[1, 0], M[0, 0]), np.arctan2(M[1, 1], M[0, 1])
    tt = np.linspace(a0, a1, 30)
    ax.plot(0.55 * np.cos(tt), 0.55 * np.sin(tt), color=BLUE, lw=1.5)
    ax.annotate("", xy=(0.55 * np.cos(tt[-1]), 0.55 * np.sin(tt[-1])), xytext=(0.55 * np.cos(tt[-3]), 0.55 * np.sin(tt[-3])),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.5))
    ax.set_xlim(-0.6, 4.4)
    ax.set_ylim(-0.6, 3.4)
    ax.set_aspect("equal")
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.axvline(0, color=MUTED, lw=0.6)
    ax.set_title(name, fontsize=11)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig6_1_1")
