"""算例 5.9.1—5.9.3：寄存器分块、向量化访存与双缓冲。
（1）GPU 执行模拟器部分 ⑤：线程块 128×128、沿 K 每步 8、每个线程 8×8：计算强度、每次乘加读共享内存的次数、共享内存与寄存器的用量；
    与每个线程 1×1、2×2、4×4 比较；
（2）部分 ④：regtile 读 Bs 时（线程负责连续的 8 列）的存储体冲突；vec 按 float4、相隔 64 的两组读时（每四分之一个线程束一组）没有冲突；
（3）每个 SM 能驻留几个线程块（寄存器限制）；
（4）在 CPU 上模拟 regtile、vec、dbuf 三个核函数并核对。"""
import numpy as np

import _gemm
from _ch5 import A10, A10_SM
from bookout import out
from gpusim import banks, gemm_tiles

n = 4096
cfg = {t: gemm_tiles(M=n, N=n, K=n, bm=128, bn=128, bk=8, tm=t, tn=t) for t in (1, 2, 4, 8)}
r8 = gemm_tiles(M=n, N=n, K=n, bm=128, bn=128, bk=8, tm=8, tn=8, stages=2)
budget = 32 / (A10["cores"] // A10["sm"])
# regtile 读 Bs[k][tcol*8 + j]：线程 lane 的 tcol = lane % 16，同一个 j 下 32 个线程的字地址
ways_reg = max(banks([(lane % 16) * 8 + j for lane in range(32)])["ways"] for j in range(8))
# vec：float4 读 Bs[k][tcol*4 .. +3]，按四分之一个线程束（8 个线程）一组处理；第一组线程 0–7 读 32 个字
ways_vec = max(banks([(lane % 16) * 4 + q + off for lane in range(g * 8, g * 8 + 8) for q in range(4)])["ways"]
               for g in range(4) for off in (0, 64))
# 存 A 的转置块 As[k][m]：线程 tid 写第 (tid % 8) 行、第 tid / 8 列（regtile）
ways_store = banks([(tid % 8) * 128 + tid // 8 for tid in range(32)])["ways"]
# 共享内存的访问次数（每次 32 个存储体各读一个字，称一次访问）与每条线程束乘加指令之比，预算 0.25：
# regtile 每个 k：读 A 8 次（线程束内只有 2 个不同的字，落在不同的存储体，各 1 次访问），读 B 8 次（每次 4 路冲突，4 次访问）
acc_reg = (8 * 1 + 8 * ways_reg) / 64
# vec 每个 k：4 条 128 位的读（A、B 各 2 条），每条按四分之一个线程束分 4 次访问，无冲突
acc_vec = 4 * 4 / 64
# 寄存器：64 个累加 + 16 个从共享内存取来的数 + 地址与循环变量，按每个线程约 128 个估计
regs = 128
blocks_sm = A10_SM["regs"] // (regs * 256)
warps_sm = blocks_sm * 256 // 32

rng = np.random.default_rng(3)
A = rng.integers(-2, 3, (256, 128)).astype(np.float32)
B = rng.integers(-2, 3, (128, 256)).astype(np.float32)
R = A @ B
assert (_gemm.regtile(A, B) == R).all() and (_gemm.vec(A, B) == R).all() and (_gemm.vec(A, B, True) == R).all()
out(**{f"smem_{t}": cfg[t]["smem_per_fma"] for t in cfg}, **{f"thr_{t}": cfg[t]["threads"] for t in cfg},
    I=r8["intensity"], smem_KB=cfg[8]["smem_bytes"] / 1024, smem2_KB=r8["smem_bytes"] / 1024, acc=r8["acc_regs"], budget=budget,
    ways_reg=ways_reg, ways_vec=ways_vec, acc_reg=acc_reg, acc_vec=acc_vec, bound_reg=100 * budget / acc_reg, ways_store=ways_store, regs=regs, blocks_sm=blocks_sm, warps_sm=warps_sm,
    occ=100 * warps_sm / A10_SM["max_warps"], ridge=A10["fp32"] / A10["bw"], steps=n // 8)
