"""7.2 节的示意图（数据同程序 7.2.1）。

图 7.2.1：（a）列主序约定：按行主序存放的 2×3 矩阵 A，内存里是 a b c d e f；cuBLAS 按列主序读同一块内存（ld = 3），
读到的是 3×2 的 Aᵀ。所以行主序的 C = A·B 交给 cuBLAS 时，写成 Cᵀ = Bᵀ·Aᵀ：B 在前、A 在后，M、N 对调，不搬数据。
（b）注意力分数的 192 个小矩阵乘法：逐个启动时启动开销（每次 5 μs）远大于计算本身（按单精度峰值）；等步长批量矩阵乘法一次启动。
"""
from _ch7 import A10, B, DH, H, T as TT
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1.35, 1]})
names = "abcdef"


def cell(x, y, s, col):
    a.add_patch(plt.Rectangle((x, y), 0.6, 0.6, fc=col, alpha=0.35, ec=C["ink"], lw=0.8))
    a.text(x + 0.3, y + 0.3, s, ha="center", va="center", fontsize=11, style="italic")


for i in range(2):                                         # 行主序的 A
    for j in range(3):
        cell(j * 0.6, 2.4 + i * 0.6, names[i * 3 + j], C["z"])
a.text(0.9, 2.2, T("A（2×3，行主序）", "A (2×3, row-major)"), ha="center", fontsize=9)
for k in range(6):                                         # 内存
    cell(2.6 + k * 0.6, 2.7, names[k], C["muted"])
a.text(4.4, 2.5, T("内存：a b c d e f", "memory: a b c d e f"), ha="center", fontsize=9)
for i in range(3):                                         # 按列主序读
    for j in range(2):
        cell(7.0 + j * 0.6, 2.1 + i * 0.6, names[j * 3 + i], C["y"])
a.text(7.6, 1.9, T("cuBLAS 读到的：Aᵀ（3×2）", "what cuBLAS sees: Aᵀ (3×2)"), ha="center", fontsize=9)
a.annotate("", xy=(2.5, 3.0), xytext=(1.9, 3.0), arrowprops=dict(arrowstyle="->", color=C["ink"]))
a.annotate("", xy=(6.9, 3.0), xytext=(6.3, 3.0), arrowprops=dict(arrowstyle="->", color=C["ink"]))
a.text(4.4, 4.3, T("行主序 C = A·B  ⇔  交给 cuBLAS：Cᵀ = Bᵀ·Aᵀ（B 在前，M、N 对调）",
                   "row-major C = A·B  ⇔  ask cuBLAS for Cᵀ = Bᵀ·Aᵀ (B first, swap M and N)"), ha="center", fontsize=9.5)
a.set_xlim(-0.2, 8.6)
a.set_ylim(1.6, 4.6)
a.invert_yaxis()
a.axis("off")
a.set_title(T("（a）同一块内存，两种读法", "(a) One buffer, two readings"), fontsize=10)

nb = B * H
t_one = 2 * TT * TT * DH / A10["fp32"] * 1e6
rows = [(T("逐个启动 192 次", "192 separate launches"), nb * t_one, nb * 5.0), (T("等步长批量，一次启动", "strided batched, one launch"), nb * t_one, 5.0)]
for i, (n, comp, launch) in enumerate(rows):
    b.barh(i, comp, color=C["y"], alpha=0.7, label=T("计算（单精度峰值）", "compute (FP32 peak)") if i == 0 else None)
    b.barh(i, launch, left=comp, color=C["x"], alpha=0.5, label=T("启动开销", "launch overhead") if i == 0 else None)
    b.text(comp + launch + 15, i, f"{comp + launch:.0f} μs", va="center", fontsize=9)
b.set_yticks(range(2))
b.set_yticklabels([r[0] for r in rows], fontsize=9)
b.invert_yaxis()
b.set_xlim(0, 1250)
b.set_xlabel(T("最短时间（μs）", "lower bound (μs)"))
b.legend(frameon=False, fontsize=8, loc="lower right")
b.set_title(T("（b）注意力分数：192 个 256×256×64 的矩阵乘法", "(b) Attention scores: 192 GEMMs of 256×256×64"), fontsize=10)
fig.tight_layout()
figure(fig, "fig7_2_1")
plt.close(fig)
