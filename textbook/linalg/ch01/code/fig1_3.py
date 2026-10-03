"""图 1.3.1：四个网页的链接与 PageRank（圆的面积与得分成正比）。"""
import numpy as np

from _fig import ACC, BLUE, INK, MUTED, T, figure, plt
from matplotlib.patches import FancyArrowPatch

links = {1: [2, 3], 2: [3], 3: [1], 4: [1, 3]}
n = 4
M = np.zeros((n, n))
for j, outs in links.items():
    for i in outs:
        M[i - 1, j - 1] = 1 / len(outs)
G = 0.85 * M + 0.15 / n
x = np.ones(n) / n
for _ in range(200):
    x = G @ x
pos = {1: (0, 1), 2: (1.6, 1), 3: (1.6, -0.4), 4: (0, -0.4)}
fig, ax = plt.subplots(figsize=(5.8, 4.4))
for j, outs in links.items():
    for i in outs:
        ax.add_patch(FancyArrowPatch(pos[j], pos[i], arrowstyle="-|>", mutation_scale=16, color=MUTED, lw=1.5,
                                     shrinkA=28, shrinkB=28, connectionstyle="arc3,rad=0.15"))
for k, (px, py) in pos.items():
    r = 0.12 + 0.55 * np.sqrt(x[k - 1])
    ax.add_patch(plt.Circle((px, py), r, color=BLUE if k != 3 else ACC, alpha=0.85, zorder=3))
    ax.text(px, py, T(f"网页 {k}\n{x[k - 1]:.3f}", f"page {k}\n{x[k - 1]:.3f}"), ha="center", va="center", color="white", fontsize=10, zorder=4)
ax.set_xlim(-0.7, 2.3)
ax.set_ylim(-1.05, 1.65)
ax.set_aspect("equal")
ax.axis("off")
figure(fig, "fig1_3_1")
