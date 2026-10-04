"""5.3 节：A = LU——消元的乘数组成 L，消元的结果是 U；先解 Lc = b（前代），再解 Ux = c（回代）；
分解一次、解很多个右端：乘法次数的比较。"""
import numpy as np

from _num import sci
from bookout import out, tex, vec


def lu_nopivot(A):
    """不交换行的 LU 分解（杜利特尔形式：L 的对角元为 1）。"""
    U = np.array(A, dtype=float)
    n = len(U)
    L = np.eye(n)
    for k in range(n - 1):
        for i in range(k + 1, n):
            L[i, k] = U[i, k] / U[k, k]
            U[i, k:] -= L[i, k] * U[k, k:]
    return L, U


def forward_sub(L, b):   # Lc = b，L 为单位下三角
    c = np.array(b, dtype=float)
    for i in range(len(c)):
        c[i] -= L[i, :i] @ c[:i]
    return c


def back_sub(U, c):   # Ux = c
    x = np.array(c, dtype=float)
    for i in range(len(x) - 1, -1, -1):
        x[i] = (x[i] - U[i, i + 1:] @ x[i + 1:]) / U[i, i]
    return x


A = np.array([[2.0, 1, 1], [4, 3, 3], [8, 7, 9]])
L, U = lu_nopivot(A)
b = np.array([3.0, 7, 19])
c = forward_sub(L, b)
x = back_sub(U, c)
out(A=tex(A, 0), L=tex(L, 0), U=tex(U, 0), LU=bool(np.allclose(L @ U, A)), b=vec(b, 0), c=vec(c, 0), x=vec(x, 0))
# 第二个右端：只需前代和回代
b2 = np.array([1.0, 0, 0])
x2 = back_sub(U, forward_sub(L, b2))
out(b2=vec(b2, 0), x2=vec(x2, 2), x2chk=bool(np.allclose(A @ x2, b2)))
# 随机 200×200 检验
rng = np.random.default_rng(53)
M = rng.standard_normal((200, 200)) + 200 * np.eye(200)   # 对角占优，不选主元也稳定
Lm, Um = lu_nopivot(M)
out(rand_err=sci(float(np.abs(Lm @ Um - M).max()), 1))


def mults_solve(n):   # 一次完整的消元加回代（式 3.8.1 加回代）
    return n ** 3 / 3 + n ** 2 / 2 - 5 * n / 6 + n * (n + 1) / 2


def mults_lu(n, k):   # 分解一次（不含右端）+ k 次前代与回代
    return (n ** 3 - n) / 3 + k * n ** 2


n, k = 1000, 100
sep, once = k * mults_solve(n), mults_lu(n, k)
out(sep=sci(sep), once=sci(once), ratio=sep / once)
rows = {}
for kk in (1, 10, 100, 1000):
    rows[f"krow{kk}"] = f"{kk} | ${sci(kk * mults_solve(n))}$ | ${sci(mults_lu(n, kk))}$ | {kk * mults_solve(n) / mults_lu(n, kk):.1f}"
out(**rows)
