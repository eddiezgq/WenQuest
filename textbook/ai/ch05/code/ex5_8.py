"""算例 5.8.1—5.8.3：共享内存分块的矩阵乘法。
（1）GPU 执行模拟器部分 ⑤：n = 4096、块边长 T = 1（不分块）、8、16、32、64 时的显存读量、计算强度、每次乘加读共享内存的次数；
（2）共享内存带宽给出的上限：每个 SM 每周期能从共享内存读 32 个字（32 个存储体），却能做 128 次乘加；
（3）在 CPU 上模拟 tiled 核函数并核对。"""
import numpy as np

import _gemm
from _ch5 import A10
from bookout import out
from gpusim import gemm_tiles

n = 4096
rows = {}
for t in (1, 8, 16, 32, 64):
    r = gemm_tiles(M=n, N=n, K=n, bm=t, bn=t, bk=t)
    rows[t] = r
lanes = A10["cores"] // A10["sm"]                      # 每个 SM 的单精度通道数（每周期乘加次数）
words = 32                                             # 共享内存每周期 32 个字
budget = words / lanes                                 # 每次乘加最多能从共享内存读几个字
t32 = rows[32]
# 每个线程每次乘加发出 2 次 32 位的共享内存读：As[ty][k]（线程束内广播）与 Bs[k][tx]。广播不省带宽：
# 一条线程束级的读指令无论读几个不同的字，至少占共享内存一个周期。所以每次乘加 2 次读，上限是预算的一半
reads = t32["smem_per_fma"]
bound_t32 = budget / reads
# 编译器可能把 As[ty][k..k+3] 合成一条 128 位的读（LDS.128）：A 每 4 个 k 只读一次，每次乘加 1/4 + 1 次
bound_vec = budget / (0.25 + 1)
r = gemm_tiles(M=n, N=n, K=n, bm=32, bn=32, bk=32)
rng = np.random.default_rng(2)
A = rng.integers(-2, 3, (128, 96)).astype(np.float32)
B = rng.integers(-2, 3, (96, 64)).astype(np.float32)
assert (_gemm.tiled(A, B) == A @ B).all()
out(n=n, **{f"I_{t}": rows[t]["intensity"] for t in rows}, **{f"GB_{t}": rows[t]["g_read"] * 4 / 1e9 for t in rows},
    smem_t32=t32["smem_per_fma"], smem_KB=t32["smem_bytes"] / 1024, threads=t32["threads"], ridge=A10["fp32"] / A10["bw"],
    lanes=lanes, budget=budget, reads=reads, bound_pct=100 * bound_t32, bound_vec_pct=100 * bound_vec, bound_GF=bound_t32 * A10["fp32"] / 1e9,
    steps=len(r["steps"]))
