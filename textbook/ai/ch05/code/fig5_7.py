"""5.7 节的示意图。

图 5.7.1：朴素矩阵乘法中，一个线程束（32 个线程，图中只画 8 个）在第 k 步读 A、B 的哪些元素。
（a）threadIdx.x 对应 C 的列：32 个线程在 C 的同一行、相邻 32 列——读 A 是同一个数（广播），读 B 是同一行中相邻的 32 个数（合并）；
（b）threadIdx.x 对应 C 的行：32 个线程在 C 的同一列、相邻 32 行——读 A 是同一列中的 32 个数，每个相隔一整行（不合并）。
"""
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, axs = plt.subplots(1, 2, figsize=(12, 4.4))
G = 12                                                     # 画 12×12 的小矩阵
for ax, mode in zip(axs, ("col", "row")):
    for name, x0 in (("A", 0), ("B", 14), ("C", 28)):
        for i in range(G):
            for j in range(G):
                ax.add_patch(plt.Rectangle((x0 + j, i), 1, 1, fc="#f2f4f6", ec="white", lw=0.5))
        ax.text(x0 + G / 2, -0.8, name, ha="center", fontsize=12)
    k, r0, c0 = 5, 3, 2
    for t in range(8):
        r, c = (r0, c0 + t) if mode == "col" else (r0 + t, c0)
        ax.add_patch(plt.Rectangle((28 + c, r), 1, 1, fc=C["accent"], alpha=0.8, ec="white"))
        ax.add_patch(plt.Rectangle((0 + k, r), 1, 1, fc=C["x"], alpha=0.75, ec="white"))
        ax.add_patch(plt.Rectangle((14 + c, k), 1, 1, fc=C["z"], alpha=0.75, ec="white"))
    ax.text(12.9, G / 2, "×", ha="center", va="center", fontsize=16)
    ax.text(26.9, G / 2, "=", ha="center", va="center", fontsize=16)
    ax.set_xlim(-0.5, 40.5)
    ax.set_ylim(G + 0.5, -1.6)
    ax.set_aspect("equal")
    ax.axis("off")
    if mode == "col":
        ax.set_title(T("（a）x 对应列：读 A 广播一个数，读 B 一行中连续的数（合并）", "(a) x → column: A is one broadcast value, B a contiguous run"), fontsize=10)
    else:
        ax.set_title(T("（b）x 对应行：读 A 一列中的数，相隔一整行（不合并）", "(b) x → row: A down a column, a full row apart (uncoalesced)"), fontsize=10)
fig.tight_layout()
figure(fig, "fig5_7_1")
plt.close(fig)
