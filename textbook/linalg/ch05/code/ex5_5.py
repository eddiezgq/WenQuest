"""5.5 节：对称矩阵的 LDLᵀ 分解——A = LU 中把 U 的对角元提出来，U = DLᵀ；只需算 L 和 D，运算量约 n³/6；
电路节点矩阵 G（3.7 节）的 D 全为正；与 Cholesky 分解的关系。"""
import numpy as np

from bookout import out, tex, vec


def ldl(A):
    """对称矩阵的 LDLᵀ 分解（不选主元）：只用下三角部分。"""
    A = np.array(A, dtype=float)
    n = len(A)
    L, d = np.eye(n), np.zeros(n)
    for j in range(n):
        d[j] = A[j, j] - (L[j, :j] ** 2) @ d[:j]
        for i in range(j + 1, n):
            L[i, j] = (A[i, j] - (L[i, :j] * L[j, :j]) @ d[:j]) / d[j]
    return L, d


A = np.array([[4.0, 2, 2], [2, 5, 3], [2, 3, 6]])
L, d = ldl(A)
U = np.diag(d) @ L.T
out(A=tex(A, 0), L=tex(L, 2), d=vec(d, 0), D=tex(np.diag(d), 0), U=tex(U, 0),
    ok=bool(np.allclose(L @ np.diag(d) @ L.T, A)))
# Cholesky：A = CCᵀ，C = L D^{1/2}
C = L @ np.diag(np.sqrt(d))
out(C=tex(C, 0), chol=bool(np.allclose(C, np.linalg.cholesky(A))))
# 3.7 节电机驱动电路的节点矩阵 G（Rs = 0.1 Ω）
g = lambda r: 1 / r
rb, RL, Rh, Ra, Rs = 0.2, 48, 0.05, 1.2, 0.1
G = np.array([[g(rb) + g(RL) + g(Rh), -g(Rh), 0, 0], [-g(Rh), g(Rh) + g(Ra), -g(Ra), 0],
              [0, -g(Ra), g(Ra) + g(Rh), -g(Rh)], [0, 0, -g(Rh), g(Rh) + g(Rs)]])
LG, dG = ldl(G)
out(dG=vec(dG, 3), Gpos=bool((dG > 0).all()))
# 对称但 D 有负元：不定矩阵
S = np.array([[1.0, 2], [2, 1]])
LS, dS = ldl(S)
out(S=tex(S, 0), LS=tex(LS, 0), dS=vec(dS, 0))
