"""算例 5.7.1—5.7.3：朴素的矩阵乘法。n×n 单精度，n = 4096：运算量、A10 上的下限；朴素版的显存流量与计算强度（不计缓存）；
两种线程映射下一个线程束每一步搬运的扇区数（GPU 执行模拟器部分 ③）；朴素版的计算方法（每个输出一个点积）在 CPU 上核对。"""
import numpy as np

import _gemm
from _ch5 import A10
from bookout import out
from gpusim import addresses, coalesce

n = 4096
flop = 2 * n ** 3
t_min_ms = flop / A10["fp32"] * 1e3
min_B = 3 * n * n * 4                                   # 每个矩阵只读写一次
I_best = flop / min_B
naive_B = (2 * n ** 3 + n * n) * 4                      # 每个输出读 A 的一行、B 的一列（不计缓存）
I_naive = flop / naive_B
t_naive_ms = naive_B / A10["bw"] * 1e3
gf_naive_bound = flop / (t_naive_ms * 1e-3) / 1e9

# 一个线程束在第 k 步读 A、B 各一次：
# x → 列（naive）：32 个线程同一行、相邻 32 列——读 A 是同一个地址，读 B 是连续 32 个数
good = coalesce(addresses(kind="stride", k=0))["sectors"] + coalesce(addresses(kind="contiguous"))["sectors"]
# x → 行（naive_rowx）：32 个线程相邻 32 行、同一列——读 A 相隔 K 个数，读 B 是同一个地址
bad = coalesce(addresses(kind="stride", k=n))["sectors"] + coalesce(addresses(kind="stride", k=0))["sectors"]

rng = np.random.default_rng(1)
A = rng.integers(-2, 3, (64, 64)).astype(np.float32)
B = rng.integers(-2, 3, (64, 64)).astype(np.float32)
assert (_gemm.naive(A, B) == A @ B).all()
out(n=n, GFLOP=flop / 1e9, t_min_ms=t_min_ms, peak_TF=A10["fp32"] / 1e12, min_MB=min_B / 1e6, I_best=I_best, naive_GB=naive_B / 1e9,
    I_naive=I_naive, t_naive_ms=t_naive_ms, gf_naive_bound=gf_naive_bound, ridge=A10["fp32"] / A10["bw"], good=good, bad=bad,
    l2_MB=A10["l2"] / 2 ** 20, row_KB=n * 4 / 1024)
