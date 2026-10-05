"""7.2.2 节与算例 7.2.1、7.2.2：cuBLAS 的列主序约定、批量矩阵乘法、尾处理融合。
（1）cuBLAS 按列主序（Fortran 的习惯）解释内存。一块按行主序存放的 M×K 矩阵，按列主序读出来就是它的转置（K×M）。
    所以要算行主序的 C = A·B，只需让 cuBLAS 算 Cᵀ = Bᵀ·Aᵀ：把 B 当第一个矩阵、A 当第二个、M 与 N 对调，一个数也不用搬。
    这里用 NumPy 的步长视图模拟 cuBLAS 的 sgemm（只按列主序读写一块平铺的内存），在整数数据上逐位核对。
（2）注意力分数：B·h 个 T×d_h 乘 d_h×T 的矩阵乘法。每个各自多大、各自启动一次要多少开销。
（3）前馈网络第一层的输出加偏置再过 GELU：单独一个核函数读写一遍的时间，与矩阵乘法本身的时间相比（半精度）。"""
import numpy as np

from _ch7 import A10, B, D, DH, F, H, T
from bookout import out


def sgemm_colmajor(m, n, k, a_buf, lda, b_buf, ldb, c_buf, ldc):
    """cuBLAS 的 C = A·B（不转置）：A 是 m×k、B 是 k×n、C 是 m×n，全部按列主序存放在平铺的一维数组里，
    第 (i, j) 个元素在 buf[i + j·ld]。"""
    view = lambda buf, r, c, ld: np.lib.stride_tricks.as_strided(buf, (r, c), (buf.itemsize, ld * buf.itemsize))
    view(c_buf, m, n, ldc)[...] = view(a_buf, m, k, lda) @ view(b_buf, k, n, ldb)


rng = np.random.default_rng(7)
M, N, K = 5, 7, 3
A = rng.integers(-2, 3, (M, K)).astype(np.float32)          # 行主序
Bm = rng.integers(-2, 3, (K, N)).astype(np.float32)
C = np.zeros(M * N, np.float32)
# 行主序的 A（M×K）在内存里就是列主序的 Aᵀ（K×M，ld = K）；B 同理。算 Cᵀ（N×M）= Bᵀ（N×K）·Aᵀ（K×M），ld 都是行主序时的列数
sgemm_colmajor(N, M, K, Bm.ravel(), N, A.ravel(), K, C, N)
ok_swap = bool(np.array_equal(C.reshape(M, N), A @ Bm))
# 反例：不对调，直接把行主序的缓冲区当成列主序交给它，得到的不是 A·B
C2 = np.zeros(M * N, np.float32)
sgemm_colmajor(M, N, K, A.ravel(), M, Bm.ravel(), K, C2, M)
wrong = not np.array_equal(C2.reshape(M, N), A @ Bm)

# （2）注意力分数的批量矩阵乘法
nb = B * H
flop_one = 2 * T * T * DH
t_one_us = flop_one / A10["fp32"] * 1e6
launch_us = 5.0                                            # 每次启动的开销，与算例 6.2.2 相同
blocks_one = (T // 128) ** 2                               # 按 128×128 的输出块，一个矩阵乘法只有这么多个线程块
total_us = nb * t_one_us

# （3）前馈网络第一层：Y = X·W₁（8192×384 乘 384×1536），半精度
n = B * T
flop_ff1 = 2 * n * D * F
t_ff1_us = flop_ff1 / A10["fp16t"] * 1e6
y_bytes = n * F * 2
t_epi_us = 2 * y_bytes / A10["bw"] * 1e6                  # 另起一个核函数：读 Y、写 GELU(Y + b)
t_gemm_io_us = (n * D + D * F + n * F) * 2 / A10["bw"] * 1e6   # 矩阵乘法自己至少要读 X、W、写 Y

out(ok_swap=ok_swap, wrong=wrong, nb=nb, MFLOP_one=flop_one / 1e6, t_one_us=t_one_us, launch_us=launch_us,
    blocks_one=blocks_one, sm=A10["sm"], total_us=total_us, launches_us=nb * launch_us,
    GFLOP_ff1=flop_ff1 / 1e9, t_ff1_us=t_ff1_us, y_MB=y_bytes / 1e6, t_epi_us=t_epi_us, t_gemm_io_us=t_gemm_io_us,
    epi_ratio=t_epi_us / max(t_ff1_us, t_gemm_io_us))
