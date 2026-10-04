"""5.4 节：行交换与 PA = LU——零主元必须交换行；部分选主元（每列选绝对值最大的元素作主元）；
小主元的灾难：[[ε, 1], [1, 1]]，不选主元时误差巨大，选主元后正确。"""
import numpy as np
import scipy.linalg as sla

from _num import sci
from bookout import out, tex, vec


def plu(A):
    """部分选主元的 LU 分解：返回置换向量 p 与 L、U，满足 A[p] = L U。"""
    U = np.array(A, dtype=float)
    n = len(U)
    L, p = np.eye(n), np.arange(n)
    for k in range(n - 1):
        m = k + int(np.argmax(np.abs(U[k:, k])))
        if m != k:   # 交换 U 的两行、L 中已算出的乘数、置换记录
            U[[k, m]], p[[k, m]] = U[[m, k]], p[[m, k]]
            L[[k, m], :k] = L[[m, k], :k]
        for i in range(k + 1, n):
            L[i, k] = U[i, k] / U[k, k]
            U[i, k:] -= L[i, k] * U[k, k:]
    return p, L, U


# 不交换行就做不下去的例子：消去第 1 列后第 2 个主元为 0
A = np.array([[1.0, 1, 1], [2, 2, 5], [4, 6, 8]])
U1 = A.copy()
U1[1] -= 2 * U1[0]
U1[2] -= 4 * U1[0]
out(A=tex(A, 0), U1=tex(U1, 0))
p, L, U = plu(A)
P = np.eye(3)[p]
out(P=tex(P, 0), L=tex(L, 2), U=tex(U, 2), PA=bool(np.allclose(P @ A, L @ U)), lmax=float(np.abs(np.tril(L, -1)).max()))
# 与 SciPy 比较（SciPy 返回 A = P L U，它的 P 是这里的 Pᵀ）
Ps, Ls, Us = sla.lu(A)
out(scipy_same=bool(np.allclose(Ps.T, P) and np.allclose(Ls, L) and np.allclose(Us, U)))
# 小主元：ε = 10⁻¹⁷
eps = 1e-17
l = 1 / eps
u22, c2 = 1 - l, 2 - l
y = c2 / u22
x_no = (1 - y) / eps
x_piv = np.linalg.solve(np.array([[eps, 1], [1, 1]]), np.array([1.0, 2]))
out(l=sci(l, 0), u22=sci(u22, 0), x_no=vec(np.array([x_no, y]), 4), x_piv=vec(x_piv, 4))
# 误差随 ε 的变化（图 5.4.1 用）
for e in (1e-4, 1e-8, 1e-12):
    l = 1 / e
    y = (2 - l) / (1 - l)
    xn = (1 - y) / e
    out(**{f"err{int(-np.log10(e))}": sci(abs(xn - 1 / (1 - e)), 1)})
