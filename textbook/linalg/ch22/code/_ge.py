"""本章共用：带三种选主元策略的高斯消元（22.1 节），记录增长因子。以下划线开头，构建时不单独运行。
lu(A, piv) 返回 P、Q、L、U、增长因子 ρ，满足 P A Q = L U；piv 为 "none"、"partial"、"rook"、"complete"。
多重打靶矩阵 shooting(N, h) 来自 22.1.4 节的两点边值问题（赖特 1993 年的例子）。"""
import numpy as np
from scipy.linalg import expm


def lu(A, piv="partial"):
    A = np.array(A, dtype=float)
    n = A.shape[0]
    rows, cols = np.arange(n), np.arange(n)
    amax = np.abs(A).max()
    g = amax
    for k in range(n - 1):
        S = np.abs(A[k:, k:])
        if piv == "partial":
            i, j = int(np.argmax(S[:, 0])), 0
        elif piv == "complete":
            i, j = np.unravel_index(int(np.argmax(S)), S.shape)
        elif piv == "rook":                       # 交替在列、行中找最大，直到它同时是所在行、列的最大者
            i, j = int(np.argmax(S[:, 0])), 0
            while True:
                j2 = int(np.argmax(S[i, :]))
                if S[i, j2] <= S[i, j]:
                    break
                j = j2
                i2 = int(np.argmax(S[:, j]))
                if S[i2, j] <= S[i, j]:
                    break
                i = i2
        else:
            i, j = 0, 0
        i, j = i + k, j + k
        A[[k, i]] = A[[i, k]]
        rows[[k, i]] = rows[[i, k]]
        A[:, [k, j]] = A[:, [j, k]]
        cols[[k, j]] = cols[[j, k]]
        if A[k, k] == 0:
            continue
        A[k + 1:, k] /= A[k, k]
        A[k + 1:, k + 1:] -= np.outer(A[k + 1:, k], A[k, k + 1:])
        g = max(g, np.abs(A[k + 1:, k + 1:]).max())
    L = np.tril(A, -1) + np.eye(n)
    U = np.triu(A)
    P = np.eye(n)[rows]
    Q = np.eye(n)[:, cols]
    return P, Q, L, U, g / amax


def solve(A, b, piv="partial"):
    P, Q, L, U, g = lu(A, piv)
    from scipy.linalg import solve_triangular
    y = solve_triangular(L, P @ b, lower=True, unit_diagonal=True)
    z = solve_triangular(U, y)
    return Q @ z, g


def wilkinson(n):
    W = np.eye(n) - np.tril(np.ones((n, n)), -1)
    W[:, -1] = 1
    return W


M_BVP = np.array([[-1 / 6, 1.0], [1.0, -1 / 6]])


def shooting(N, h=0.3):
    """y′ = M y 在 N 个长 h 的小区间上的多重打靶方程组：y_{i+1} − e^{Mh} y_i = 0，边界条件 y_0 + y_N = c。"""
    E = expm(M_BVP * h)
    m = 2
    A = np.zeros((m * (N + 1), m * (N + 1)))
    for i in range(N):
        A[i * m:(i + 1) * m, i * m:(i + 1) * m] = -E
        A[i * m:(i + 1) * m, (i + 1) * m:(i + 2) * m] = np.eye(m)
    A[N * m:, :m] = np.eye(m)
    A[N * m:, N * m:] = np.eye(m)
    return A
