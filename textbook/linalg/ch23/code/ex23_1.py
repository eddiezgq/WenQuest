"""23.1 节：正规方程、QR、SVD 三种解法的精度与代价。
(1) 构造 m = 100、n = 10、条件数 κ = 10²～10¹⁰ 的最小二乘问题，残差分“几乎为零”（tan θ = 10⁻⁸）和“很大”（tan θ = 1）两种，
比较正规方程（乔列斯基）、豪斯霍尔德 QR、SVD 三种解法的相对误差，与 κu、κ²u·tan θ 两项对照；
(2) 运算量：m ≫ n 时正规方程约 mn²，QR 约 2mn²，SVD 约 2mn² + 11n³。"""
import numpy as np
from scipy.linalg import cho_factor, cho_solve, qr, solve_triangular

from _num import sci
from bookout import T, out

rng = np.random.default_rng(23011)
u = 2.0 ** -53


def solve_ne(A, b):
    F = cho_factor(A.T @ A)
    return cho_solve(F, A.T @ b)


def solve_qr(A, b):
    Q, R = qr(A, mode="economic")
    return solve_triangular(R, Q.T @ b)


def solve_svd(A, b):
    U, s, Vt = np.linalg.svd(A, full_matrices=False)
    return Vt.T @ ((U.T @ b) / s)


m, n = 100, 10
res = {}
for small in (True, False):
    for kexp in (2, 4, 6, 8, 10):
        U, _ = np.linalg.qr(rng.standard_normal((m, m)))
        V, _ = np.linalg.qr(rng.standard_normal((n, n)))
        s = np.logspace(0, -kexp, n)
        A = U[:, :n] @ np.diag(s) @ V.T
        x = rng.standard_normal(n)
        y = A @ x
        r = U[:, n:] @ rng.standard_normal(m - n)               # 与 A 的列空间正交
        tan = 1e-8 if small else 1.0
        r *= tan * np.linalg.norm(y) / np.linalg.norm(r)
        b = y + r
        e = {}
        for name, f in (("ne", solve_ne), ("qr", solve_qr), ("svd", solve_svd)):
            try:
                xs = f(A, b)
                e[name] = float(np.linalg.norm(xs - x) / np.linalg.norm(x))
            except np.linalg.LinAlgError:
                e[name] = float("nan")
        key = ("s" if small else "l") + str(kexp)
        k = 10.0 ** kexp
        out(**{f"{key}_ne": sci(e["ne"], 1) if e["ne"] == e["ne"] else T("\\text{失败}", "\\text{fails}"), f"{key}_qr": sci(e["qr"], 1), f"{key}_svd": sci(e["svd"], 1),
               f"{key}_b1": sci(k * u, 1), f"{key}_b2": sci(k * k * u * tan, 1)})
out(u=sci(u, 1))

# (2) 运算量（m = 1000、n = 50）
mm, nn = 1000, 50
out(fl_ne=sci(mm * nn ** 2 + nn ** 3 / 3, 2), fl_qr=sci(2 * mm * nn ** 2 - 2 * nn ** 3 / 3, 2), fl_svd=sci(2 * mm * nn ** 2 + 11 * nn ** 3, 2))
