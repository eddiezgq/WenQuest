"""4.7 节的示意图（GPU 执行模拟器部分 ④，数据同程序 4.7.2）。

图 4.7.1：一个线程束按列读共享内存中 32×32 的单精度块。（a）每行 32 个字：一列的 32 个元素都在同一个存储体，
32 路冲突；（b）每行多留 1 个字（33 列）：同一列的元素依次落在 32 个不同的存储体上，一次读完。格中颜色表示存储体编号。
"""
import numpy as np

from bookout import COLORS, T, figure, style
from gpusim import bank_words, banks

plt = style()
C = COLORS
fig, axs = plt.subplots(1, 2, figsize=(11, 5.2))
cmap = plt.get_cmap("tab20b")
for ax, pad in zip(axs, (0, 1)):
    width = 32 + pad
    rows = 10                                       # 只画前 10 行
    for r in range(rows):
        for c in range(width):
            bank = (r * width + c) % 32
            ax.add_patch(plt.Rectangle((c, r), 1, 1, color=cmap(bank % 20), alpha=0.35 if c != 3 else 0.95, lw=0))
    ax.add_patch(plt.Rectangle((3, 0), 1, rows, fill=False, ec=C["x"], lw=2))
    w = banks(bank_words(kind="column", pad=pad, col=3))["ways"]
    ax.set_xlim(-0.5, 33.5)
    ax.set_ylim(rows + 0.5, -0.5)
    ax.set_aspect("equal")
    ax.set_xticks([0, 3, 32] if pad else [0, 3, 31])
    ax.set_yticks([0, 5, 9])
    ax.set_xlabel(T("列（字）", "column (word)"))
    ax.set_ylabel(T("行", "row"))
    banks_col = [((r * width + 3) % 32) for r in range(rows)]
    ax.set_title(T(f"（{'ab'[pad]}）每行 {width} 个字：第 3 列在存储体 {banks_col[:4]}…，{w} 路冲突",
                   f"({'ab'[pad]}) {width} words per row: column 3 in banks {banks_col[:4]}…, {w}-way"), fontsize=10)
fig.tight_layout()
figure(fig, "fig4_7_1")
plt.close(fig)
