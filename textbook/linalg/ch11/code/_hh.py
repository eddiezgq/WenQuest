"""本章共用：豪斯霍尔德反射与吉文斯旋转。以下划线开头，构建时不单独运行。"""
import numpy as np


def house(x):
    """返回 v，使 H = I − 2vvᵀ/vᵀv 把 x 变成 −sign(x₁)‖x‖e₁（取与 x₁ 同号的方向相加，避免相减抵消）。"""
    x = np.asarray(x, dtype=float)
    v = x.copy()
    s = 1.0 if x[0] >= 0 else -1.0
    v[0] += s * np.linalg.norm(x)
    return v


def householder_qr(A, steps=None):
    """豪斯霍尔德 QR：逐列把对角线以下化为零。返回 Q、R 以及每一步之后的矩阵。"""
    R = np.array(A, dtype=float)
    m, n = R.shape
    Q = np.eye(m)
    hist = [R.copy()]
    for k in range(min(n, m - 1) if steps is None else steps):
        v = house(R[k:, k])
        if v @ v == 0:
            continue
        H = np.eye(m - k) - 2 * np.outer(v, v) / (v @ v)
        R[k:, :] = H @ R[k:, :]
        Q[:, k:] = Q[:, k:] @ H
        hist.append(R.copy())
    return Q, R, hist


def givens(a, b):
    """返回 (c, s)，使 [[c, s], [−s, c]] (a, b)ᵀ = (r, 0)ᵀ，r = √(a² + b²)。"""
    r = np.hypot(a, b)
    return (1.0, 0.0) if r == 0 else (a / r, b / r)
