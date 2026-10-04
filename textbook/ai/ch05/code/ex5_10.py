"""算例 5.10.1—5.10.3：张量核心。
（1）A10 的单精度、TF32、半精度张量核心峰值；一次 mma_sync（16×16×16）与一条单精度乘加指令的工作量之比；
（2）程序 5.7.1 中 wmma_gemm 的分块：显存读量与计算强度（A、B 半精度，C 单精度），与半精度屋脊比较；
（3）精度：随机矩阵在半精度、TF32 输入（单精度累加）下的相对误差，与单精度相比；
（4）在 CPU 上模拟 wmma_gemm 的线程束分工与数据搬运并核对。"""
import numpy as np

import _gemm
from _ch5 import A10
from bookout import out
from gpusim import gemm_tiles

fma_mma = 16 * 16 * 16                                  # 一次 mma_sync：一个线程束做 4096 次乘加
fma_ffma = 32                                           # 一条单精度乘加指令：一个线程束 32 次
n = 4096
g = gemm_tiles(M=n, N=n, K=n, bm=128, bn=128, bk=32)
bytes_w = g["g_read"] * 2 + g["g_write"] * 4            # A、B 半精度，C 单精度
I_w = g["flop"] / bytes_w
ridge16 = A10["fp16t"] / A10["bw"]
g256 = gemm_tiles(M=n, N=n, K=n, bm=256, bn=128, bk=32)
I_w256 = g256["flop"] / (g256["g_read"] * 2 + g256["g_write"] * 4)


def round_mantissa(x, bits):
    """把单精度数舍入到 bits 位尾数（就近舍入，不处理溢出）：bits = 10 即 TF32 与半精度的尾数长度。"""
    i = x.astype(np.float32).view(np.uint32).astype(np.int64)
    drop = 23 - bits
    i = (i + (1 << (drop - 1)) - 1 + ((i >> drop) & 1)) >> drop << drop
    return i.astype(np.uint32).view(np.float32)


rng = np.random.default_rng(10)
m, k = 256, 4096
A = rng.standard_normal((m, k))
B = rng.standard_normal((k, m))
exact = A @ B
rel = lambda C: float(np.linalg.norm(C - exact) / np.linalg.norm(exact))   # noqa: E731
e32 = rel((A.astype(np.float32) @ B.astype(np.float32)).astype(np.float64))
e16 = rel(A.astype(np.float16).astype(np.float32) @ B.astype(np.float16).astype(np.float32))
etf = rel(round_mantissa(A, 10) @ round_mantissa(B, 10))
assert np.allclose(round_mantissa(np.float32([1 + 2 ** -11, 1 + 3 * 2 ** -11]), 10), [1, 1 + 2 * 2 ** -10])   # 舍入到偶数

Ai = rng.integers(-2, 3, (256, 128)).astype(np.float16)
Bi = rng.integers(-2, 3, (128, 256)).astype(np.float16)
assert (_gemm.wmma(Ai, Bi) == Ai.astype(np.float32) @ Bi.astype(np.float32)).all()
out(fp32_TF=A10["fp32"] / 1e12, tf32_TF=A10["tf32t"] / 1e12, fp16_TF=A10["fp16t"] / 1e12, x16=A10["fp16t"] / A10["fp32"],
    ratio=fma_mma / fma_ffma, I_w=I_w, I_w256=I_w256, ridge16=ridge16, e32=e32, e16=e16, etf=etf, k=k,
    smem_KB=(128 * 40 + 32 * 136) * 2 / 1024)
