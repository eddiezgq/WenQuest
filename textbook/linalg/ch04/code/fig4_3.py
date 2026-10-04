"""图 4.3.1：先剪切再转动（RS）与先转动再剪切（SR）作用在同一面小旗上，结果不同：矩阵乘法不可交换。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow, figure, plt

t = math.radians(30)
R = np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])
S = np.array([[1.0, 1.0], [0.0, 1.0]])
flag = np.array([[0.0, 0.0], [1.0, 0.0], [1.0, 0.5], [0.5, 0.5], [0.5, 1.0], [0.0, 1.0], [0.0, 0.0]]).T
fig, axs = plt.subplots(1, 3, figsize=(10.6, 3.9))
for ax, (M, name) in zip(axs, ((np.eye(2), T("原来的小旗", "the original flag")), (R @ S, T("RS：先剪切，再转 30°", "RS: shear first, then rotate")),
                                (S @ R, T("SR：先转 30°，再剪切", "SR: rotate first, then shear")))):
    for i in range(-3, 4):
        for P, Q in (([i, -3], [i, 3]), ([-3, i], [3, i])):
            p, q = M @ P, M @ Q
            ax.plot([p[0], q[0]], [p[1], q[1]], color=BLUE, lw=0.6, alpha=0.35)
    F = M @ flag
    ax.fill(F[0], F[1], color=ACC, alpha=0.6, ec=INK)
    arrow(ax, M[:, 0], RED, None, lw=2.2)
    arrow(ax, M[:, 1], GREEN, None, lw=2.2)
    ax.set_xlim(-1.5, 2.5)
    ax.set_ylim(-1.0, 2.0)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(name, fontsize=11)
fig.tight_layout()
figure(fig, "fig4_3_1")
