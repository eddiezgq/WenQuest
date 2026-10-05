"""图 8.7.1：车间配电网的有向图：4 个节点、5 条支路（箭头为规定的正方向）；两个独立回路：1→2→3→1 与 2→3→4→2。"""
import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt

pos = {1: (0.0, 1.0), 2: (1.6, 2.0), 3: (1.6, 0.0), 4: (3.2, 1.0)}
edges = [(1, 2), (1, 3), (2, 3), (2, 4), (3, 4)]
fig, ax = plt.subplots(figsize=(6.4, 4.0))
for k, (i, j) in enumerate(edges):
    a, b = np.array(pos[i]), np.array(pos[j])
    ax.annotate("", xy=b - 0.13 * (b - a) / np.linalg.norm(b - a), xytext=a + 0.13 * (b - a) / np.linalg.norm(b - a),
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.8, mutation_scale=16))
    m = (a + b) / 2
    ax.text(m[0] + 0.08, m[1] + 0.08, f"e{k + 1}", color=MUTED, fontsize=11)
for nd, (x, y) in pos.items():
    ax.add_patch(plt.Circle((x, y), 0.12, fc="white", ec=BLUE, lw=2))
    ax.text(x, y, str(nd), ha="center", va="center", fontsize=12, color=BLUE)
ax.text(1.05, 1.0, T("回路 1", "loop 1"), color=RED, fontsize=10, ha="center")
ax.text(2.15, 1.0, T("回路 2", "loop 2"), color=GREEN, fontsize=10, ha="center")
ax.set_xlim(-0.4, 3.6)
ax.set_ylim(-0.4, 2.4)
ax.set_aspect("equal")
ax.axis("off")
figure(fig, "fig8_7_1")
