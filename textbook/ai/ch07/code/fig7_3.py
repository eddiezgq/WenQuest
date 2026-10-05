"""7.3 节的示意图（模型数据同程序 7.3.1；实测见表 7.3.1）。

图 7.3.1：同一个卷积层（B = 32，C = K = 64，56×56，3×3）各种算法纸面上的代价：（a）乘法次数（直接卷积为 1）；
（b）要额外占用的显存（工作区，维诺格拉德按“不融合”的写法、变换后的数用单精度存放，粗估），虚线是输入本身的大小（半精度）。
纸面上省乘法的算法要多搬数据、多占显存，谁最快只能实测。
"""
import numpy as np

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
Bn, Ch, K, H, W, R = 32, 64, 64, 56, 56, 3
mul_direct = Bn * K * H * W * Ch * R * R


def wino(m):
    tiles = Bn * (H // m) * (W // m)
    return tiles * K * Ch * (m + 2) ** 2, tiles * (Ch + K) * (m + 2) ** 2 * 4


N = 64
freq = N * (N // 2 + 1)
algos = [(T("隐式矩阵乘法", "implicit GEMM"), 1.0, 0.0),
         (T("显式矩阵乘法\n（im2col）", "explicit GEMM\n(im2col)"), 1.0, Bn * H * W * Ch * R * R * 2),
         (T("维诺格拉德\nF(2×2,3×3)", "Winograd\nF(2×2,3×3)"), wino(2)[0] / mul_direct, wino(2)[1]),
         (T("维诺格拉德\nF(4×4,3×3)", "Winograd\nF(4×4,3×3)"), wino(4)[0] / mul_direct, wino(4)[1]),
         (T("快速傅里叶变换\n（不计变换）", "FFT\n(excl. transforms)"), Bn * K * Ch * freq * 4 / mul_direct, (Bn * Ch + K * Ch + Bn * K) * freq * 8)]
fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.2))
x = np.arange(len(algos))
a.bar(x, [m for _, m, _ in algos], color=C["z"], alpha=0.7)
for i, (_, m, _) in enumerate(algos):
    a.text(i, m + 0.02, f"{m:.2f}", ha="center", fontsize=9)
a.set_xticks(x)
a.set_xticklabels([n for n, _, _ in algos], fontsize=8)
a.set_ylim(0, 1.12)
a.set_ylabel(T("乘法次数（直接卷积 = 1）", "multiplications (direct = 1)"))
a.set_title(T("（a）乘法次数", "(a) Multiplications"), fontsize=10)
b.bar(x, [w / 1e6 for _, _, w in algos], color=C["x"], alpha=0.6)
for i, (_, _, w) in enumerate(algos):
    b.text(i, w / 1e6 + 3, f"{w / 1e6:.0f} MB", ha="center", fontsize=9)
b.axhline(Bn * Ch * H * W * 2 / 1e6, color=C["muted"], ls="--", lw=1)
b.text(4.45, Bn * Ch * H * W * 2 / 1e6 + 4, T("输入本身", "the input itself"), ha="right", fontsize=8, color=C["muted"])
b.set_xticks(x)
b.set_xticklabels([n for n, _, _ in algos], fontsize=8)
b.set_ylabel(T("工作区（MB，粗估）", "workspace (MB, rough)"))
b.set_title(T("（b）额外占用的显存", "(b) Extra memory"), fontsize=10)
fig.tight_layout()
figure(fig, "fig7_3_1")
plt.close(fig)
