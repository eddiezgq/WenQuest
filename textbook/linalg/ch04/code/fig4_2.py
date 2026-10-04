"""图 4.2.1：矩阵乘法 C = AB 的四种看法：(a) cᵢⱼ = A 的第 i 行 · B 的第 j 列；(b) C 的第 j 列 = A 乘 B 的第 j 列；
(c) C 的第 i 行 = A 的第 i 行乘 B；(d) C = Σ (A 的第 k 列)(B 的第 k 行)，每一项是一个秩 1 矩阵。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from matplotlib.patches import Rectangle


def grid(ax, x0, y0, m, n, hl=None, col=ACC, label=""):
    for i in range(m):
        for j in range(n):
            on = hl is not None and hl(i, j)
            ax.add_patch(Rectangle((x0 + j, y0 - i - 1), 1, 1, fc=col if on else "white", ec=INK, lw=0.8, alpha=0.75 if on else 1))
    ax.text(x0 + n / 2, y0 + 0.35, label, ha="center", fontsize=12)


fig, axs = plt.subplots(2, 2, figsize=(10.0, 6.6))
specs = [(T("(a) 行乘列：一个元素", "(a) row times column: one entry"), lambda i, j: i == 1, lambda i, j: j == 2, lambda i, j: i == 1 and j == 2),
         (T("(b) 列：C 的第 j 列 = A × B 的第 j 列", "(b) columns: col j of C = A × col j of B"), lambda i, j: True, lambda i, j: j == 2, lambda i, j: j == 2),
         (T("(c) 行：C 的第 i 行 = A 的第 i 行 × B", "(c) rows: row i of C = row i of A × B"), lambda i, j: i == 1, lambda i, j: True, lambda i, j: i == 1),
         (T("(d) 列乘行之和：C = Σ (A 的第 k 列)(B 的第 k 行)", "(d) columns times rows: C = Σ (col k of A)(row k of B)"), lambda i, j: j == 1, lambda i, j: i == 1, lambda i, j: True)]
for ax, (name, ha, hb, hc) in zip(axs.flat, specs):
    grid(ax, 0, 3, 3, 4, ha, BLUE, "A")
    ax.text(4.5, 1.3, "×", fontsize=16, ha="center")
    grid(ax, 5, 3.5, 4, 4, hb, GREEN, "B")
    ax.text(9.5, 1.3, "=", fontsize=16, ha="center")
    grid(ax, 10, 3, 3, 4, hc, RED, "C")
    ax.set_xlim(-0.5, 14.5)
    ax.set_ylim(-1.2, 4.3)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(name, fontsize=11)
fig.tight_layout()
figure(fig, "fig4_2_1")
