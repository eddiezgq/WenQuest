"""5.6 节的示意图。

图 5.6.1：（a）压缩稀疏行（CSR）格式：一个 5×5 的稀疏矩阵只存非零元的值 val、列号 col，以及每行第一个非零元在 val 中的位置 ptr
（第 i 行是 val[ptr[i]] 到 val[ptr[i+1]−1]）；（b）幂律矩阵（2^20 行）各行长度的分布：一半的行不超过 7 个非零元，少数行有几千个，
与拉普拉斯矩阵（每行至多 5 个）形成对比。
"""
import numpy as np

from _ch5 import uniform
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
A = np.array([[4, -1, 0, 0, 0], [0, 3, 0, 2, 0], [0, 0, 0, 0, 0], [7, 0, 5, 1, 0], [0, 0, 0, 0, 6]])
val, col, ptr = [], [], [0]
for r in A:
    nz = np.nonzero(r)[0]
    val += list(r[nz])
    col += list(nz)
    ptr.append(len(val))
fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.25, 1]})
for i in range(5):
    for j in range(5):
        nz = A[i, j] != 0
        a.add_patch(plt.Rectangle((j, i), 1, 1, fc=C["z"] if nz else "#f2f4f6", alpha=0.35 if nz else 1, ec="white"))
        a.text(j + 0.5, i + 0.5, str(A[i, j]).replace("-", "−") if nz else "·", ha="center", va="center", fontsize=11)
    a.text(-0.4, i + 0.5, T(f"第 {i} 行", f"row {i}"), ha="right", va="center", fontsize=9, color=C["muted"])


def arr(y, name, xs, color):
    a.text(6.0, y + 0.5, name, ha="right", va="center", fontsize=10, family="monospace")
    for k, v in enumerate(xs):
        a.add_patch(plt.Rectangle((6.2 + k * 0.62, y), 0.58, 0.9, fc=color, alpha=0.3, ec="white"))
        a.text(6.2 + k * 0.62 + 0.29, y + 0.45, str(v).replace("-", "−"), ha="center", va="center", fontsize=9)


arr(0.5, "val", val, C["z"])
arr(1.9, "col", col, C["accent"])
arr(3.3, "ptr", ptr, C["y"])
a.text(6.2, 4.9, T("第 2 行是空行：ptr[2] = ptr[3]", "row 2 is empty: ptr[2] = ptr[3]"), fontsize=9, color=C["muted"])
a.set_xlim(-1.6, 11.6)
a.set_ylim(5.3, -0.3)
a.set_aspect("equal")
a.axis("off")
a.set_title(T("（a）CSR：只存非零元与每行的起点", "(a) CSR: the nonzeros and where each row starts"), fontsize=10)
L = np.minimum(4096, 1 + np.floor(4 * uniform(np.arange(2 ** 20) + (7 << 40)) ** -0.8)).astype(np.int64)
bins = np.unique(np.round(np.logspace(0, np.log10(4097), 30)).astype(int))
h, e = np.histogram(L, bins=bins)
b.bar(e[:-1], h, width=np.diff(e), align="edge", color=C["z"], alpha=0.6, ec="white")
b.axvline(5, color=C["x"], ls="--", lw=1.5, label=T("拉普拉斯矩阵：每行至多 5 个", "Laplacian: at most 5 per row"))
b.axvline(np.median(L), color=C["accent"], lw=1.5, label=T(f"幂律矩阵的中位数：{np.median(L):.0f}", f"power-law median: {np.median(L):.0f}"))
b.set_xscale("log")
b.set_yscale("log")
b.set_xlabel(T("一行的非零元个数", "nonzeros in a row"))
b.set_ylabel(T("行数", "rows"))
b.set_title(T("（b）幂律矩阵各行的长度", "(b) Row lengths of the power-law matrix"), fontsize=10)
b.legend(fontsize=9, frameon=False)
fig.tight_layout()
figure(fig, "fig5_6_1")
plt.close(fig)
