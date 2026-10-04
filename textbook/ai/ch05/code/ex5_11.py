"""算例 5.11.1—5.11.3：与 cuBLAS 对比。
（1）各版本在 A10 屋顶线上的位置（按不计缓存的显存流量算计算强度）与可达到的上限；
（2）L2 缓存复用的粗略估计；（3）“波次量化”：线程块 128×128、每个 SM 同时驻留 2 个时，不同大小的方阵要几波、最后一波有多满；
（4）小型 Transformer 前馈网络第一层（B·T = 8192，d = 384，d_ff = 1536）的矩阵乘法。"""
import math

from _ch5 import A10
from bookout import out
from gpusim import gemm_tiles

n = 4096
P = {"fp32": A10["fp32"], "tf32": A10["tf32t"], "fp16": A10["fp16t"]}
bw = A10["bw"]
pts = {}
for name, (t, tm, size, roof) in {"naive": (1, 1, 4, "fp32"), "tiled": (32, 1, 4, "fp32"), "regtile": (128, 8, 4, "fp32"),
                                  "wmma": (128, 1, 2, "fp16")}.items():
    g = gemm_tiles(M=n, N=n, K=n, bm=t, bn=t, bk=8 if t == 128 else t, tm=tm, tn=tm)
    I = g["flop"] / (g["g_read"] * size + g["g_write"] * 4)
    pts[name] = dict(I=I, bound=min(P[roof], bw * I) / 1e12)
waves = {}
slots = A10["sm"] * 2
for m in (1024, 2048, 4096, 8192):
    blocks = (m // 128) ** 2
    w = blocks / slots
    waves[m] = dict(blocks=blocks, waves=w, eff=blocks / (math.ceil(w) * slots))
# L2 的复用（粗略估计）：一波 144 个线程块按 blockIdx.x 先走，覆盖 C 的 144 / 32 = 4.5 个行块；假设同一波的线程块大致同步地沿 K 前进，
# 共用的数据在 L2 中只从显存读一次，则每一波读全部 B 与 A 的 4.5 个行块
cols = n // 128
rows_wave = slots / cols
per_wave = n * n * 4 + rows_wave * 128 * n * 4
nwaves = (cols * cols) / slots
l2_GB = per_wave * nwaves / 1e9
I_l2 = 2 * n ** 3 / (per_wave * nwaves)
M, N, K = 32 * 256, 1536, 384
ff_flop = 2 * M * N * K
ff_blocks = (M // 128) * (N // 128)
ff_us = ff_flop / A10["fp16t"] * 1e6
ff_I = ff_flop / ((M * K + K * N) * 2 + M * N * 2)
out(**{f"I_{k}": v["I"] for k, v in pts.items()}, **{f"bound_{k}": v["bound"] for k, v in pts.items()}, slots=slots,
    **{f"blocks_{m}": v["blocks"] for m, v in waves.items()}, **{f"waves_{m}": v["waves"] for m, v in waves.items()},
    **{f"eff_{m}": 100 * v["eff"] for m, v in waves.items()}, ff_GFLOP=ff_flop / 1e9, ff_blocks=ff_blocks, ff_us=ff_us, ff_I=ff_I,
    ridge16=A10["fp16t"] / bw, ridge32=A10["fp32"] / bw, rows_wave=rows_wave, l2_GB=l2_GB, I_l2=I_l2, nocache_GB=gemm_tiles(M=n, N=n, K=n, bm=128, bn=128, bk=8)["bytes"] / 1e9)
