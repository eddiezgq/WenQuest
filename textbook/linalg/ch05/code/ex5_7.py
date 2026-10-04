"""5.7 节：为什么几乎从不真的去求逆——运算量：求逆约 2n³，LU 分解约 (2/3)n³；精度：病态矩阵上 inv(A) @ b 的残差
比 solve 大得多；正交矩阵的逆就是转置。"""
import numpy as np

from _num import sci
from bookout import out

rng = np.random.default_rng(57)


def make(n, cond):
    """构造条件数约为 cond 的 n×n 矩阵：A = U diag(s) Vᵀ，s 从 1 按几何级数降到 1/cond。"""
    U, _ = np.linalg.qr(rng.standard_normal((n, n)))
    V, _ = np.linalg.qr(rng.standard_normal((n, n)))
    s = np.logspace(0, -np.log10(cond), n)
    return U @ np.diag(s) @ V.T


n = 200
rows = {}
for c in (1e2, 1e6, 1e10, 1e14):
    A = make(n, c)
    xt = rng.standard_normal(n)
    b = A @ xt
    xs = np.linalg.solve(A, b)
    xi = np.linalg.inv(A) @ b
    res = lambda x: np.linalg.norm(b - A @ x) / (np.linalg.norm(A, 2) * np.linalg.norm(x))
    rows[f"crow{int(np.log10(c))}"] = f"$10^{{{int(np.log10(c))}}}$ | ${sci(res(xs), 1)}$ | ${sci(res(xi), 1)}$"
out(**rows)
# 运算量（浮点运算次数）：解一个方程组 (2/3)n³ + 2n²；求逆 2n³ 再乘向量 2n²
N = 1000
out(f_solve=sci(2 / 3 * N ** 3 + 2 * N ** 2, 1), f_inv=sci(2 * N ** 3 + 2 * N ** 2, 1))
# 正交矩阵：逆 = 转置
t = np.radians(30)
R = np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])
out(RT=bool(np.allclose(np.linalg.inv(R), R.T)))
