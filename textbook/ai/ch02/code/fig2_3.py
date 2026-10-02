"""2.3 节的示意图。

图 2.3.1：（a）一个形状为 (2, 3, 4) 的张量在内存中按行主序排成一行，步长为 (12, 4, 1)；（b）转置最后两维后，
同一块内存按步长 (12, 1, 4) 读取。
图 2.3.2：广播：形状 (3, 1) 的列与形状 (1, 4) 的行相加，各自沿长度为 1 的维度复制，得到 (3, 4)。
"""
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
pal = ["#dbe7f3", "#fdf3dc"]

# ---------------------------------------------------------------- 图 2.3.1
fig, axs = plt.subplots(2, 1, figsize=(10.4, 4.6))
for ax, (title, order) in zip(axs, ((T("（a）形状 (2, 3, 4)，行主序，步长 (12, 4, 1)：最后一维连续",
                                       "(a) Shape (2, 3, 4), row-major, strides (12, 4, 1): the last axis is contiguous"), "orig"),
                                    (T("（b）转置后两维，形状 (2, 4, 3)，步长 (12, 1, 4)：不搬数据，读的顺序跳跃",
                                       "(b) Last two axes swapped, shape (2, 4, 3), strides (12, 1, 4): no data moved, reads jump"), "t"))):
    ax.set_xlim(-0.3, 24.3)
    ax.set_ylim(-1.2, 2.6)
    ax.axis("off")
    ax.set_title(title, fontsize=10.5, loc="left")
    for m in range(24):
        i0, r = divmod(m, 12)
        i1, i2 = divmod(r, 4)
        ax.add_patch(Rectangle((m, 0), 0.95, 0.95, fc=pal[i0], ec=C["ink"], lw=0.8))
        ax.text(m + 0.47, 0.47, f"{i0}{i1}{i2}", ha="center", va="center", fontsize=7.4, color=C["ink"])
        ax.text(m + 0.47, -0.25, str(m), ha="center", va="center", fontsize=6.8, color=C["muted"])
    if order == "orig":
        seq = list(range(24))
    else:
        seq = [i0 * 12 + i1 * 4 + i2 for i0 in range(2) for i2 in range(4) for i1 in range(3)]
    for a, b in zip(seq[:7], seq[1:8]):
        ax.add_patch(FancyArrowPatch((a + 0.47, 1.0), (b + 0.47, 1.0), arrowstyle="-|>", mutation_scale=9, lw=1.0,
                                     color=C["x"], connectionstyle=f"arc3,rad={-0.5 if b > a else 0.35}"))
    ax.text(0, -0.85, T("格内为下标 $i_0 i_1 i_2$，格下为内存中的偏移；红色箭头为按新形状逐个读取的前几步",
                        "cells: indices $i_0 i_1 i_2$; below: memory offset; red arrows: first reads in the new shape's order"),
            fontsize=8.6, color=C["muted"])
fig.tight_layout()
figure(fig, "fig2_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 2.3.2
fig, ax = plt.subplots(figsize=(9.0, 3.0))
ax.set_xlim(0, 15.5)
ax.set_ylim(0.8, 3.7)
ax.axis("off")
a = np.array([1, 2, 3])
b = np.array([10, 20, 30, 40])


def grid(x0, vals, ghost=None, fc="#dbe7f3"):
    m, n = vals.shape
    for i in range(m):
        for j in range(n):
            g = ghost is not None and ghost[i, j]
            ax.add_patch(Rectangle((x0 + j * 0.75, 2.6 - i * 0.75), 0.72, 0.72, fc="#ffffff" if g else fc,
                                   ec=C["muted"] if g else C["ink"], lw=0.8, ls="--" if g else "-"))
            ax.text(x0 + j * 0.75 + 0.36, 2.96 - i * 0.75, str(vals[i, j]), ha="center", va="center", fontsize=9,
                    color=C["muted"] if g else C["ink"])


grid(0.2, np.tile(a[:, None], (1, 4)), ghost=np.tile(np.arange(4) > 0, (3, 1)))
ax.text(1.7, 3.45, T("形状 (3, 1)，沿列复制", "shape (3, 1), copied along columns"), ha="center", fontsize=9)
ax.text(3.6, 2.2, "+", fontsize=18, ha="center", va="center")
grid(4.1, np.tile(b[None, :], (3, 1)), ghost=np.tile(np.arange(3)[:, None] > 0, (1, 4)), fc="#fdf3dc")
ax.text(5.6, 3.45, T("形状 (1, 4)，沿行复制", "shape (1, 4), copied along rows"), ha="center", fontsize=9)
ax.text(7.5, 2.2, "=", fontsize=18, ha="center", va="center")
grid(8.0, a[:, None] + b[None, :], fc="#f1f6ef")
ax.text(9.5, 3.45, T("结果形状 (3, 4)", "result shape (3, 4)"), ha="center", fontsize=9)
ax.text(11.4, 2.3, T("规则：从最后一维向前逐维比较，\n两个长度相等，或其中一个为 1，\n才能广播；为 1 的一方被复制。\n虚线格并不真的占内存。",
                     "Rule: compare axes from the last one;\nlengths must be equal or one of them 1;\nthe side of length 1 is repeated.\nDashed cells take no memory."),
        fontsize=9, va="center", color=C["ink"], linespacing=1.5)
figure(fig, "fig2_3_2")
plt.close(fig)
