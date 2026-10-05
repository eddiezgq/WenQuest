"""8.1 节的示意图（格式参数同 _ch8.py 与程序 8.1.1）。

图 8.1.1：（a）各种格式的位分配：符号（红）、指数（蓝）、尾数（绿），按位数画成同样宽的格子；
（b）相邻两个可表示数的相对间隔随数值大小的变化（对数坐标）：规格化区内在 2^−m 与 2^−(m+1) 之间呈锯齿，进入次正规区后迅速变大，
左端是最小次正规数，右端是最大值。FP16 与 BF16 同为 16 位：BF16 的范围与 FP32 相同而精度粗 8 倍。
"""
import numpy as np

from _ch8 import FMTS
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 4.6), gridspec_kw={"width_ratios": [1.15, 1]})
names = list(FMTS)
for i, k in enumerate(names):
    f = FMTS[k]
    y = len(names) - 1 - i
    cols = [C["x"]] + [C["z"]] * f.e + [C["y"]] * f.m
    for j, c in enumerate(cols):
        a.add_patch(plt.Rectangle((j * 0.38, y + 0.15), 0.34, 0.7, fc=c, alpha=0.65, ec="none"))
    a.text(-0.3, y + 0.5, k, ha="right", va="center", fontsize=9)
    a.text(len(cols) * 0.38 + 0.25, y + 0.5, T(f"1 + {f.e} + {f.m}", f"1 + {f.e} + {f.m}"), va="center", fontsize=8, color=C["muted"])
a.set_xlim(-2.8, 14.5)
a.set_ylim(-0.2, len(names) + 0.1)
a.axis("off")
a.set_title(T("（a）位的分配：符号（红）、指数（蓝）、尾数（绿）", "(a) Bits: sign (red), exponent (blue), mantissa (green)"), fontsize=10)

for k, col in (("FP32", C["muted"]), ("BF16", C["x"]), ("FP16", C["z"]), ("FP8 E4M3", C["y"]), ("FP8 E5M2", C["accent"])):
    f = FMTS[k]
    xs = np.logspace(np.log10(f.min_sub), np.log10(f.max), 4000)
    ex = np.maximum(np.floor(np.log2(xs)), 1 - f.bias)
    gap = 2.0 ** (ex - f.m) / xs
    b.plot(xs, gap, color=col, lw=1.2, label=k)
b.set_xscale("log")
b.set_yscale("log")
b.set_xlim(1e-46, 1e40)
b.set_ylim(1e-8, 2)
b.set_xlabel(T("数值的大小", "magnitude"))
b.set_ylabel(T("相邻两数的相对间隔", "relative spacing"))
b.legend(frameon=False, fontsize=8, loc="upper right")
b.set_title(T("（b）范围与精度：横跨的宽度是范围，高低是精度", "(b) Range and precision: width is range, height is precision"), fontsize=10)
fig.tight_layout()
figure(fig, "fig8_1_1")
plt.close(fig)
