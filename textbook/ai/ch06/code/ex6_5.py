"""算例 6.5.1：用模型预测 Nsight Compute 会测到什么。第 5 章的矩阵乘法（n = 4096，单精度）：
不计缓存的显存流量（模拟器部分 ⑤）、算例 5.11.1 那样考虑 L2 复用的粗略估计（读）加上写 C、每个矩阵只读写一次的下限。"""
from _ch6 import A10
from bookout import out
from gpusim import gemm_tiles

n = 4096
flop = 2 * n ** 3
tiled = gemm_tiles(M=n, N=n, K=n, bm=32, bn=32, bk=32)["bytes"]
reg = gemm_tiles(M=n, N=n, K=n, bm=128, bn=128, bk=8)["bytes"]
slots = A10["sm"] * 2
rows_wave = slots / (n // 128)
l2_est = (n * n * 4 + rows_wave * 128 * n * 4) * ((n // 128) ** 2 / slots) + n * n * 4   # 读（按 L2 复用估计）+ 写 C
low = 3 * n * n * 4
out(n=n, tiled_GB=tiled / 1e9, reg_GB=reg / 1e9, l2_GB=l2_est / 1e9, low_GB=low / 1e9, I_low=flop / low, I_l2est=flop / l2_est)
