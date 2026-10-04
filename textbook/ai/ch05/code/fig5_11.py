"""5.11 节的示意图（数据同程序 5.11.1）。

图 5.11.1：A10 的屋顶线：单精度、TF32 张量核心、半精度张量核心三个屋顶，斜坡是显存带宽 600 GB/s。竖线是程序 5.7.1 各版本
按“不计缓存”的显存流量算出的计算强度；实测的点画在 GPU 实验 5.11 中。L2 缓存使实际的显存流量更小，所以分块较大的版本实际上可以越过竖线所示的位置。
"""
import numpy as np

from _ch5 import A10
from bookout import COLORS, T, figure, style
from gpusim import gemm_tiles

plt = style()
C = COLORS
n = 4096
bw = A10["bw"]
fig, ax = plt.subplots(figsize=(8.5, 5))
I = np.logspace(-1, 3.2, 300)
for peak, name, col in ((A10["fp32"], T("单精度", "FP32"), C["z"]), (A10["tf32t"], "TF32", C["y"]), (A10["fp16t"], T("半精度张量核心", "FP16 tensor"), C["x"])):
    ax.plot(I, np.minimum(peak, bw * I) / 1e12, color=col, lw=2, label=f"{name}  {peak / 1e12:.1f} TFLOP/s")
vers = {"naive": (1, 1, 4), "tiled": (32, 1, 4), "regtile": (128, 8, 4), "wmma": (128, 1, 2)}
for name, (t, tm, size) in vers.items():
    g = gemm_tiles(M=n, N=n, K=n, bm=t, bn=t, bk=8 if t == 128 else t, tm=tm, tn=tm)
    x = g["flop"] / (g["g_read"] * size + g["g_write"] * 4)
    ax.axvline(x, color=C["muted"], ls=":", lw=1)
    ax.text(x * 1.08, 0.055, name, rotation=90, fontsize=9, color=C["muted"], va="bottom")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(0.1, 1500)
ax.set_ylim(0.05, 200)
ax.set_xlabel(T("计算强度（FLOP/B）", "arithmetic intensity (FLOP/B)"))
ax.set_ylabel(T("可达到的算力（TFLOP/s）", "attainable performance (TFLOP/s)"))
ax.set_title(T("A10 的屋顶线与各版本的计算强度（不计缓存）", "A10 roofline and the intensity of each version (no caches)"), fontsize=10)
ax.legend(fontsize=9, frameon=False, loc="upper left")
fig.tight_layout()
figure(fig, "fig5_11_1")
plt.close(fig)
