"""本章共用：经典与修正格拉姆–施密特正交化。以下划线开头，构建时不单独运行。"""
import numpy as np


def cgs(A):
    """经典格拉姆–施密特：第 j 列减去它在已得到的 q₁, …, q_{j−1} 上的投影（投影系数都用原来的 a_j 计算）。"""
    A = np.asarray(A, dtype=float)
    m, n = A.shape
    Q, R = np.zeros((m, n)), np.zeros((n, n))
    for j in range(n):
        v = A[:, j].copy()
        R[:j, j] = Q[:, :j].T @ A[:, j]
        v -= Q[:, :j] @ R[:j, j]
        R[j, j] = np.linalg.norm(v)
        Q[:, j] = v / R[j, j]
    return Q, R


def mgs(A):
    """修正格拉姆–施密特：每得到一个 q_k，立即从后面所有的列中减去它的分量（投影系数用已更新的列计算）。"""
    V = np.array(A, dtype=float)
    m, n = V.shape
    Q, R = np.zeros((m, n)), np.zeros((n, n))
    for k in range(n):
        R[k, k] = np.linalg.norm(V[:, k])
        Q[:, k] = V[:, k] / R[k, k]
        R[k, k + 1:] = Q[:, k] @ V[:, k + 1:]
        V[:, k + 1:] -= np.outer(Q[:, k], R[k, k + 1:])
    return Q, R


def cgs2(A):
    """经典格拉姆–施密特做两遍（再正交化）：“两遍就够了”。"""
    Q1, R1 = cgs(A)
    Q2, R2 = cgs(Q1)
    return Q2, R2 @ R1


def orth_err(Q):
    return float(np.linalg.norm(Q.T @ Q - np.eye(Q.shape[1]), 2))
