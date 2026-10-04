"""在 CPU 上逐线程块、逐步模拟程序 5.7.1 中各个矩阵乘法核函数的下标计算（以下划线开头，构建时不单独运行；
ex5_8.py、ex5_9.py、ex5_10.py 用它在小矩阵上与 NumPy 的结果核对）。

每个函数与 gemm.cu 中同名的核函数一一对应：线程块逐个模拟；同一线程块的线程用 NumPy 数组一起算（tid 是 0..255 的数组），
下标表达式照抄 CUDA 程序。共享内存是 NumPy 数组；两次 __syncthreads() 之间的语句按“先全部写、再全部读”执行。
"""
import numpy as np

T = 32
BM, BN, BK, TM, TN, NT = 128, 128, 8, 8, 8, 256


def naive(A, B):
    M, K = A.shape
    N = B.shape[1]
    C = np.zeros((M, N), np.float32)
    for row in range(M):                         # 每个线程 (row, col) 算一个点积
        C[row] = (A[row][:, None] * B).sum(axis=0)
    return C


def tiled(A, B):
    M, K = A.shape
    N = B.shape[1]
    C = np.zeros((M, N), np.float32)
    ty, tx = np.meshgrid(np.arange(T), np.arange(T), indexing="ij")
    for by in range(M // T):
        for bx in range(N // T):
            row, col = by * T + ty, bx * T + tx
            s = np.zeros((T, T), np.float32)
            for k0 in range(0, K, T):
                As = A[row, k0 + tx]                 # As[ty][tx] = A[row * K + k0 + tx]
                Bs = B[k0 + ty, col]                 # Bs[ty][tx] = B[(k0 + ty) * N + col]
                for k in range(T):
                    s += As[ty, k] * Bs[k, tx]
            C[row, col] = s
    return C


def regtile(A, B):
    M, K = A.shape
    N = B.shape[1]
    C = np.zeros((M, N), np.float32)
    tid = np.arange(NT)
    trow, tcol = tid // 16, tid % 16
    for by in range(M // BM):
        for bx in range(N // BN):
            Ab, Bb = A[by * BM:], B[:, bx * BN:]
            acc = np.zeros((NT, TM, TN), np.float32)
            for k0 in range(0, K, BK):
                As = np.full((BK, BM), np.nan, np.float32)
                Bs = np.full((BK, BN), np.nan, np.float32)
                for i in range(BM * BK // NT):
                    e = tid + i * NT
                    m, k = e // BK, e % BK
                    As[k, m] = Ab[m, k0 + k]
                for i in range(BK * BN // NT):
                    e = tid + i * NT
                    k, n = e // BN, e % BN
                    Bs[k, n] = Bb[k0 + k, n]
                for k in range(BK):
                    ra = As[k][trow[:, None] * TM + np.arange(TM)]           # (NT, TM)
                    rb = Bs[k][tcol[:, None] * TN + np.arange(TN)]
                    acc += ra[:, :, None] * rb[:, None, :]
            for i in range(TM):
                for j in range(TN):
                    C[by * BM + trow * TM + i, bx * BN + tcol * TN + j] = acc[:, i, j]
    return C


def _load_tiles(Ab, Bb, k0, tid):
    a = np.stack([Ab[tid // 2, k0 + (tid % 2) * 4 + q] for q in range(4)], axis=1)       # float4
    b = np.stack([Bb[k0 + tid // 32, (tid % 32) * 4 + q] for q in range(4)], axis=1)
    return a, b


def _store_tiles(f, As, Bs, tid):
    a, b = f
    m, kq = tid // 2, (tid % 2) * 4
    for q in range(4):
        As[kq + q, m] = a[:, q]
        Bs[tid // 32, (tid % 32) * 4 + q] = b[:, q]


def _rows8(t):
    """线程负责的 8 个下标：t*4 + {0..3} 与 64 + t*4 + {0..3}（t 是数组）。"""
    return np.concatenate([t[:, None] * 4 + np.arange(4), 64 + t[:, None] * 4 + np.arange(4)], axis=1)


def _compute_step(As, Bs, acc, trow, tcol):
    for k in range(BK):
        ra = As[k][_rows8(trow)]
        rb = Bs[k][_rows8(tcol)]
        acc += ra[:, :, None] * rb[:, None, :]


def _store_c(C, acc, by, bx, trow, tcol):
    for i in range(8):
        r = (0 if i < 4 else 64) + trow * 4 + i % 4
        for j in range(8):
            c = (0 if j < 4 else 64) + tcol * 4 + j % 4
            C[by * BM + r, bx * BN + c] = acc[:, i, j]


def vec(A, B, double_buffer=False):
    """vec（double_buffer=False）与 dbuf（True）。双缓冲时按 gemm.cu 的顺序：先读下一步、算这一步、存进另一份、同步。"""
    M, K = A.shape
    N = B.shape[1]
    C = np.zeros((M, N), np.float32)
    tid = np.arange(NT)
    trow, tcol = tid // 16, tid % 16
    for by in range(M // BM):
        for bx in range(N // BN):
            Ab, Bb = A[by * BM:], B[:, bx * BN:]
            acc = np.zeros((NT, 8, 8), np.float32)
            if not double_buffer:
                for k0 in range(0, K, BK):
                    As, Bs = np.full((BK, BM), np.nan, np.float32), np.full((BK, BN), np.nan, np.float32)
                    _store_tiles(_load_tiles(Ab, Bb, k0, tid), As, Bs, tid)
                    _compute_step(As, Bs, acc, trow, tcol)
            else:
                As, Bs = np.full((2, BK, BM), np.nan, np.float32), np.full((2, BK, BN), np.nan, np.float32)
                steps = K // BK
                _store_tiles(_load_tiles(Ab, Bb, 0, tid), As[0], Bs[0], tid)
                for t in range(steps):
                    cur = t & 1
                    nxt = _load_tiles(Ab, Bb, (t + 1) * BK, tid) if t + 1 < steps else None
                    _compute_step(As[cur], Bs[cur], acc, trow, tcol)
                    if nxt is not None:
                        _store_tiles(nxt, As[cur ^ 1], Bs[cur ^ 1], tid)
            _store_c(C, acc, by, bx, trow, tcol)
    return C


def wmma(A, B):
    """wmma_gemm：8 个线程束排成 4×2，线程束 (wm, wn) 算 32×64 = 2×4 个 16×16 的块；每个 mma_sync 是一次 16×16×16 的乘加。
    A、B 是半精度，累加用单精度。"""
    M, K = A.shape
    N = B.shape[1]
    C = np.zeros((M, N), np.float32)
    WBK = 32
    for by in range(M // BM):
        for bx in range(N // BN):
            fc = {(w, i, j): np.zeros((16, 16), np.float32) for w in range(8) for i in range(2) for j in range(4)}
            for k0 in range(0, K, WBK):
                As = np.full((BM, WBK + 8), np.nan, np.float16)       # 每行多留 8 个（填充）
                Bs = np.full((WBK, BN + 8), np.nan, np.float16)
                Ab, Bb = A[by * BM:], B[:, bx * BN:]
                tid = np.arange(NT)
                for i in range(2):                                  # 每个线程搬 2 个 16 字节（8 个半精度数）
                    e = tid + i * NT
                    for q in range(8):
                        As[e // 4, (e % 4) * 8 + q] = Ab[e // 4, k0 + (e % 4) * 8 + q]
                        Bs[e // 16, (e % 16) * 8 + q] = Bb[k0 + e // 16, (e % 16) * 8 + q]
                for w in range(8):
                    wm, wn = w // 2, w % 2
                    for kk in (0, 16):
                        for i in range(2):
                            fa = As[wm * 32 + i * 16: wm * 32 + i * 16 + 16, kk:kk + 16].astype(np.float32)
                            for j in range(4):
                                fb = Bs[kk:kk + 16, wn * 64 + j * 16: wn * 64 + j * 16 + 16].astype(np.float32)
                                fc[w, i, j] += fa @ fb
            for (w, i, j), v in fc.items():
                wm, wn = w // 2, w % 2
                r0, c0 = by * BM + wm * 32 + i * 16, bx * BN + wn * 64 + j * 16
                C[r0:r0 + 16, c0:c0 + 16] = v
    return C
