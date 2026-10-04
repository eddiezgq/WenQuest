"""算例 5.6.1—5.6.3：稀疏矩阵与向量相乘。
（1）零件热分析的二维拉普拉斯矩阵（n×n 网格，五点差分）的 CSR 存储、搬运量与计算强度；用 CSR 算 y = Ax 与 5.1 节的模板计算核对；
（2）标量版（一个线程一行）与线程束版（一个线程束一行）的访存：GPU 执行模拟器部分 ③ 算一个线程束读 val 的扇区数；
（3）幂律矩阵（行长度相差悬殊，与 code/runs/run5_6/spmv.cu 同一规则生成）：标量版一个线程束内的负载不均，ELL 格式的填充。"""
import numpy as np

from _ch5 import A10, uniform
from bookout import out
from gpusim import addresses, coalesce


def laplacian_csr(n):
    """n×n 网格上的 −Δ（五点差分，狄利克雷边界）：对角 4，上下左右的邻点 −1。按行主序编号，返回 CSR 的三个数组。"""
    rows, cols, vals = [], [], []
    idx = np.arange(n * n).reshape(n, n)
    for di, dj, v in [(-1, 0, -1.0), (0, -1, -1.0), (0, 0, 4.0), (0, 1, -1.0), (1, 0, -1.0)]:   # 每行按列号从小到大
        i0, i1 = max(0, -di), n - max(0, di)
        j0, j1 = max(0, -dj), n - max(0, dj)
        r = idx[i0:i1, j0:j1].ravel()
        rows.append(r)
        cols.append(idx[i0 + di:i1 + di, j0 + dj:j1 + dj].ravel())
        vals.append(np.full(r.size, v))
    rows, cols, vals = map(np.concatenate, (rows, cols, vals))
    order = np.lexsort((cols, rows))
    rows, cols, vals = rows[order], cols[order], vals[order]
    ptr = np.zeros(n * n + 1, np.int64)
    np.add.at(ptr, rows + 1, 1)
    return np.cumsum(ptr), cols, vals


def spmv(ptr, cols, vals, x):
    """CSR 的 y = Ax：第 i 行把 val[ptr[i]:ptr[i+1]] 与 x[col[...]] 逐项相乘再相加（每行至少一个非零元）。"""
    return np.add.reduceat(vals * x[cols], ptr[:-1])


def spmv_vector(ptr, cols, vals, x, i):
    """线程束版计算第 i 行：lane 号线程处理第 ptr[i] + lane、+ lane + 32、……个非零元，最后线程束内求和。"""
    part = np.zeros(32)
    for lane in range(32):
        for k in range(ptr[i] + lane, ptr[i + 1], 32):
            part[lane] += vals[k] * x[cols[k]]
    return part.sum()


# （1）小网格上核对：CSR 的 Ax 与直接按五点模板算的结果相同
n = 64
ptr, cols, vals = laplacian_csr(n)
x = np.random.default_rng(5).standard_normal(n * n)
u = np.pad(x.reshape(n, n), 1)
stencil = (4 * u[1:-1, 1:-1] - u[:-2, 1:-1] - u[2:, 1:-1] - u[1:-1, :-2] - u[1:-1, 2:]).ravel()
y = spmv(ptr, cols, vals, x)
assert np.allclose(y, stencil)
assert all(np.isclose(spmv_vector(ptr, cols, vals, x, i), y[i]) for i in range(0, n * n, 97))

# 实测用的大小：2048×2048 的网格
n = 2048
N = n * n
nnz = 5 * N - 4 * n
csr_B = nnz * 8 + (N + 1) * 4 + 2 * N * 4                    # val、col 各 4 字节，行指针，读 x 一遍、写 y 一遍（x 的重复读靠缓存）
B_per_nnz = csr_B / nnz
I = 2 * nnz / csr_B
t_min_us = csr_B / A10["bw"] * 1e6
dense_TB = N * N * 4 / 1e12

# （2）标量版：线程 t 处理第 r0 + t 行，第 j 轮读 val[ptr[r0+t] + j]，相邻线程相隔 5 个元素
sc = coalesce(addresses(kind="stride", k=5))
vec_lanes = 5 / 32                                           # 线程束版：一行只有 5 个非零元，32 个线程中只有 5 个干活

# （3）幂律矩阵：2^20 行，第 i 行的长度 min(4096, 1 + ⌊4 u^(−0.8)⌋)，u 取自 splitmix64(i + 7·2^40)
Np = 2 ** 20
L = np.minimum(4096, 1 + np.floor(4 * uniform(np.arange(Np) + (7 << 40)) ** -0.8)).astype(np.int64)
w = L.reshape(-1, 32)
scalar_eff = float(L.sum() / (32 * w.max(axis=1)).sum())      # 标量版：每个线程束要等最长的一行做完
ell_pad = float(Np * L.max() / L.sum())                      # ELL：每行都补到最长那一行的长度
out(n=n, N_M=N / 1e6, nnz_M=nnz / 1e6, csr_MB=csr_B / 1e6, B_per_nnz=B_per_nnz, I=I, t_min_us=t_min_us, dense_TB=dense_TB,
    sc_sectors=sc["sectors"], sc_eff=100 * sc["eff"], vec_lanes=100 * vec_lanes,
    pl_N_M=Np / 2 ** 20, pl_nnz_M=L.sum() / 1e6, pl_mean=float(L.mean()), pl_median=float(np.median(L)), pl_max=int(L.max()),
    pl_capped=int((L == 4096).sum()), scalar_eff=100 * scalar_eff, ell_pad=ell_pad)
