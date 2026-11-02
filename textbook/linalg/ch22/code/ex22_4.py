"""22.4 节：BLAS、LAPACK 与分块算法。(1) 三级 BLAS 的运算量、访存量与“运算强度”（每读写一个数做几次运算）；
(2) 屋顶线模型：假设一台处理器峰值 1 TFLOP/s、内存带宽 100 GB/s，三级运算各能跑多快；
(3) 用一个小的 LRU 缓存模拟矩阵乘法：三重循环与分块（块大小 b）的缓存未命中次数；
(4) 分块的右视 LU 分解（块内部分选主元）：与逐列消元结果相同，大部分运算落在矩阵乘法（三级 BLAS）里；
(5) 仓库地面高度图的高斯过程回归：N 个测点的核矩阵稠密对称正定，乔列斯基分解要多少次运算、多少内存。
（计时随机器而变，书中的数都是数出来、算出来的，不是测出来的。）"""
from collections import OrderedDict

import numpy as np

from _num import sci
from bookout import out

# (1) 运算强度（双精度，每个数 8 字节）
n = 1000
ops = {"axpy": (2 * n, 3 * n), "gemv": (2 * n * n, n * n + 3 * n), "gemm": (2 * n ** 3, 4 * n * n)}
for k, (f, m) in ops.items():
    out(**{f"{k}_f": sci(f, 1), f"{k}_m": sci(m, 1), f"{k}_ai": f / m})
# (2) 屋顶线：可达速度 = min(峰值, 带宽 × 运算强度)
peak, bw = 1000.0, 100.0 / 8                          # GFLOP/s；G 个双精度数/秒
for k, (f, m) in ops.items():
    out(**{f"{k}_perf": min(peak, bw * f / m)})
out(balance=peak / bw)


# (3) 缓存模拟：完全相联、LRU、每行 8 个数，容量 C 个数
def misses(order, n, C, line=8):
    cache = OrderedDict()
    cap = C // line
    miss = 0
    def touch(arr, i, j):
        nonlocal miss
        key = (arr, (i * n + j) // line)              # 按行存储
        if key in cache:
            cache.move_to_end(key)
        else:
            miss += 1
            cache[key] = None
            if len(cache) > cap:
                cache.popitem(last=False)
    for i, j, k in order:
        touch("A", i, k); touch("B", k, j); touch("C", i, j)
    return miss


nn, C = 64, 512
naive = ((i, j, k) for i in range(nn) for j in range(nn) for k in range(nn))
mn = misses(naive, nn, C)
res = {}
for b in (4, 8, 16):
    blocked = ((i, j, k) for ii in range(0, nn, b) for jj in range(0, nn, b) for kk in range(0, nn, b)
               for i in range(ii, ii + b) for j in range(jj, jj + b) for k in range(kk, kk + b))
    res[b] = misses(blocked, nn, C)
out(cs_n=nn, cs_C=C, cs_naive=mn, cs_b4=res[4], cs_b8=res[8], cs_b16=res[16], cs_min=3 * nn * nn // 8, cs_access=3 * nn ** 3)


# (4) 分块右视 LU（块内部分选主元）
def blocked_lu(A, b):
    A = A.copy()
    n = len(A)
    perm = np.arange(n)
    fl3 = fl = 0
    for k in range(0, n, b):
        e = min(k + b, n)
        for j in range(k, e):                          # 面板：逐列消元（一、二级运算）
            p = j + int(np.argmax(np.abs(A[j:, j])))
            A[[j, p]] = A[[p, j]]
            perm[[j, p]] = perm[[p, j]]
            A[j + 1:, j] /= A[j, j]
            A[j + 1:, j + 1:e] -= np.outer(A[j + 1:, j], A[j, j + 1:e])
            fl += 2 * (n - j - 1) * (e - j - 1) + (n - j - 1)
        if e < n:
            L11 = np.tril(A[k:e, k:e], -1) + np.eye(e - k)
            A[k:e, e:] = np.linalg.solve(L11, A[k:e, e:])            # 三角求解（三级）
            A[e:, e:] -= A[e:, k:e] @ A[k:e, e:]                      # 矩阵乘法（三级）
            f3 = (e - k) ** 2 * (n - e) + 2 * (n - e) ** 2 * (e - k)
            fl += f3
            if b > 1:                                   # b = 1 时这一步只是秩 1 修正（二级运算）
                fl3 += f3
    return A, perm, fl, fl3


rng = np.random.default_rng(22041)
n4 = 400
M = rng.standard_normal((n4, n4))
for b in (1, 32):
    F, perm, fl, fl3 = blocked_lu(M, b)
    L = np.tril(F, -1) + np.eye(n4)
    U = np.triu(F)
    err = np.linalg.norm(M[perm] - L @ U) / np.linalg.norm(M)
    out(**{f"blu{b}_err": sci(err, 1), f"blu{b}_frac": fl3 / fl, f"blu{b}_fl": sci(fl, 2)})
out(lu_flops=sci(2 * n4 ** 3 / 3, 2))
F1 = blocked_lu(M, 1)[0]
F32 = blocked_lu(M, 32)[0]
out(blu_same=sci(float(np.abs(F1 - F32).max()), 1))

# (5) 高斯过程回归建地面高度图
for N in (5000, 50000):
    out(**{f"gp{N}_fl": sci(N ** 3 / 3, 1), f"gp{N}_mem": float(N * N * 8 / 1e9), f"gp{N}_t": float(N ** 3 / 3 / (0.5 * peak * 1e9))})
