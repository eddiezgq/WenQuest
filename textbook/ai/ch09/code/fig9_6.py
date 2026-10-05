"""9.6 节的示意图（数据同程序 9.6.1）。

图 9.6.1：（a）FlashAttention 的分块：Q 按行分块（每块 B_r 行），对一个 Q 块依次读入 K、V 的各块，算出 B_r × B_c 的一小块分数，
用在线 softmax 更新这几行的结果；因果掩码下，对角线右上方的块整个跳过。整个 N × N 的分数矩阵从不写进显存。
（b）一个头的显存流量（N = 4096，d = 64，半精度，B_r = 128）：标准实现与 FlashAttention。
"""
import numpy as np

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.2, 1]})
nb = 8
for i in range(nb):
    for j in range(nb):
        if j > i:
            col, al = "white", 1
        elif i == 3:
            col, al = C["z"], 0.3 + 0.08 * j
        else:
            col, al = C["muted"], 0.15
        a.add_patch(plt.Rectangle((j, nb - 1 - i), 0.95, 0.95, fc=col, alpha=al, ec=C["grid"] if "grid" in C else "#cccccc"))
for j in range(4):
    a.annotate("", xy=(j + 0.8, nb - 3.6), xytext=(j + 0.15, nb - 3.6), arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.2))
a.text(-0.3, nb - 3.55, T("Q 块", "Q block"), ha="right", va="center", fontsize=9, color=C["z"])
a.text(nb / 2, nb + 0.3, T("K、V 的各块 →", "blocks of K, V →"), ha="center", fontsize=9)
a.text(nb + 0.2, nb - 1.5, T("右上方：因果掩码，\n整块跳过", "upper right: causal\nmask, skipped"), ha="left", fontsize=9, color=C["muted"])
a.set_xlim(-1.5, nb + 3.0)
a.set_ylim(-0.3, nb + 0.8)
a.set_aspect("equal")
a.axis("off")
a.set_title(T("（a）一次处理一小块分数，在线更新 softmax", "(a) One tile of scores at a time, online softmax"), fontsize=10)
N, d, Br, by = 4096, 64, 128, 2
std = (4 * N * N + 4 * N * d) * by / 1e6
fl = (2 * N * d + 2 * N * d * (N // Br)) * by / 1e6
b.bar([0, 1], [std, fl], color=[C["x"], C["z"]], alpha=0.7)
for i, v in enumerate([std, fl]):
    b.text(i, v * 1.02, f"{v:.0f} MB", ha="center", fontsize=9)
b.set_xticks([0, 1])
b.set_xticklabels([T("标准实现", "standard"), "FlashAttention"])
b.set_ylabel(T("显存流量（MB，一个头）", "memory traffic (MB, one head)"))
b.set_title(T("（b）N = 4096、d = 64 时一个头的显存流量", "(b) Traffic of one head, N = 4096, d = 64"), fontsize=10)
fig.tight_layout()
figure(fig, "fig9_6_1")
plt.close(fig)
