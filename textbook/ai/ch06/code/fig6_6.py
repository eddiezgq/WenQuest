"""6.6 节的示意图（数据同程序 6.6.1，模型值；实测点在 GPU 实验 6.5 中画出）。

图 6.6.1：A10 的分层屋顶线（单精度）：显存与共享内存两条斜坡、一个屋顶。第 5 章三个版本各画两个点：方块是按显存流量的计算强度
（tiled 不计缓存；regtile、vec 按算例 5.11.1 考虑 L2 复用的估计），圆点是按共享内存读取的计算强度。一个核函数可达到的算力取各层上限中最低的一个：
tiled 与 regtile 被共享内存这一层压住，vec 恰好到达共享内存的屋脊。
"""
import numpy as np

from _ch6 import A10
from bookout import COLORS, T, figure, style
from gpusim import gemm_tiles

plt = style()
C = COLORS
n = 4096
P = A10["fp32"]
bw = A10["bw"]
sm = 128 * A10["sm"] * A10["clock"]
I = np.logspace(-1.5, 3.2, 300)
fig, ax = plt.subplots(figsize=(8.5, 5))
ax.plot(I, np.minimum(P, bw * I) / 1e12, color=C["z"], lw=2, label=T("显存（600 GB/s）", "device memory (600 GB/s)"))
ax.plot(I, np.minimum(P, sm * I) / 1e12, color=C["y"], lw=2, label=T(f"共享内存（{sm / 1e12:.1f} TB/s）", f"shared memory ({sm / 1e12:.1f} TB/s)"))
slots = A10["sm"] * 2
l2 = (n * n * 4 + slots / (n // 128) * 128 * n * 4) * ((n // 128) ** 2 / slots)
flop = 2 * n ** 3
pts = {"tiled": (flop / gemm_tiles(M=n, N=n, K=n, bm=32, bn=32, bk=32)["bytes"], 64 / (2.0 * 128)),
       "regtile": (flop / l2, 64 / (40 / 64 * 128)), "vec": (flop / l2, 64 / (16 / 64 * 128))}
for k, (idram, ismem) in pts.items():
    yd, ys = min(P, bw * idram), min(P, sm * ismem)
    y = min(yd, ys)
    ax.plot([idram], [y / 1e12], "s", color=C["z"], ms=7)
    ax.plot([ismem], [y / 1e12], "o", color=C["y"], ms=7)
    ax.plot([ismem, idram], [y / 1e12, y / 1e12], ":", color=C["muted"], lw=1)
    ax.annotate(k, (ismem, y / 1e12), textcoords="offset points", xytext=(-8, 8), fontsize=9, ha="right")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(10 ** -1.5, 10 ** 3.2)
ax.set_ylim(0.3, 60)
ax.set_xlabel(T("计算强度（FLOP/B）", "intensity (FLOP/B)"))
ax.set_ylabel(T("可达到的算力（TFLOP/s）", "attainable (TFLOP/s)"))
ax.set_title(T("A10 的分层屋顶线（单精度）：方块按显存，圆点按共享内存", "A10 hierarchical roofline (FP32): squares by memory, dots by shared memory"), fontsize=10)
ax.legend(frameon=False, fontsize=9, loc="lower right")
fig.tight_layout()
figure(fig, "fig6_6_1")
plt.close(fig)
