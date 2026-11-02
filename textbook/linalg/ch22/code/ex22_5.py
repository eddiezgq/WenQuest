"""22.5 节：混合精度计算。(1) 一万个 [0, 1) 内的数的点积：半精度逐个累加、半精度输入加单精度累加、双精度的误差；
(2) 混合精度迭代改进：单精度做 LU 分解（便宜），双精度算残差、更新解。κ(A) 从 10² 到 10¹⁰，看几步收敛、收敛到哪里；
(3) 三种精度：半精度（逐步舍入模拟）做 LU，单精度解修正方程，双精度算残差——κ 小时仍收敛到双精度；
(4) 运算量：n = 10⁴ 的方程组，分解 2n³/3 次，改进每步只要 O(n²) 次。"""
import numpy as np
from scipy.linalg import lu_factor, lu_solve

from _num import sci
from bookout import out

rng = np.random.default_rng(22051)
# (1) 点积
N = 10000
x = rng.random(N)
y = rng.random(N)
exact = float(np.dot(x.astype(np.float64), y.astype(np.float64)))
x16, y16 = x.astype(np.float16), y.astype(np.float16)
ex16 = float(np.dot(x16.astype(np.float64), y16.astype(np.float64)))      # 半精度输入的精确点积
s16 = np.float16(0)
s32 = np.float32(0)
for a, b in zip(x16, y16):
    s16 = np.float16(s16 + np.float16(a * b))
    s32 = np.float32(s32 + np.float32(a) * np.float32(b))
out(dot_exact=exact, dot16=float(s16), dot16_32=float(s32), dot_rel16=float(abs(float(s16) - ex16) / ex16), dot_rel32=sci(abs(float(s32) - ex16) / ex16, 1),
    dot_in=sci(abs(ex16 - exact) / exact, 1))


def make(n, kappa, rng):
    U, _ = np.linalg.qr(rng.standard_normal((n, n)))
    V, _ = np.linalg.qr(rng.standard_normal((n, n)))
    s = np.logspace(0, -np.log10(kappa), n)
    return U @ np.diag(s) @ V.T


# (2) 单精度分解 + 双精度改进
n = 100
hist = {}
for kexp in (2, 4, 6, 8, 10):
    A = make(n, 10.0 ** kexp, rng)
    xt = rng.standard_normal(n)
    b = A @ xt
    F = lu_factor(A.astype(np.float32))
    xk = lu_solve(F, b.astype(np.float32)).astype(np.float64)
    errs = [np.linalg.norm(xk - xt) / np.linalg.norm(xt)]
    for it in range(10):
        r = b - A @ xk                                   # 双精度残差
        d = lu_solve(F, r.astype(np.float32)).astype(np.float64)
        xk = xk + d
        errs.append(np.linalg.norm(xk - xt) / np.linalg.norm(xt))
    hist[kexp] = errs
    xd = np.linalg.solve(A, b)
    out(**{f"k{kexp}_e0": sci(errs[0], 1), f"k{kexp}_e1": sci(errs[1], 1), f"k{kexp}_e3": sci(errs[3], 1), f"k{kexp}_e10": sci(errs[10], 1),
           f"k{kexp}_dbl": sci(float(np.linalg.norm(xd - xt) / np.linalg.norm(xt)), 1)})
out(u32=sci(2.0 ** -24, 1), u16=sci(2.0 ** -11, 1), lim32=sci(1 / 2.0 ** -24, 0))


# (3) 半精度 LU（每次运算后舍入到半精度），单精度解修正方程，双精度残差
def lu16(A):
    A = A.astype(np.float16)
    n = len(A)
    perm = np.arange(n)
    for k in range(n - 1):
        p = k + int(np.argmax(np.abs(A[k:, k].astype(np.float32))))
        A[[k, p]] = A[[p, k]]
        perm[[k, p]] = perm[[p, k]]
        A[k + 1:, k] = (A[k + 1:, k] / A[k, k]).astype(np.float16)
        A[k + 1:, k + 1:] = (A[k + 1:, k + 1:] - np.outer(A[k + 1:, k], A[k, k + 1:]).astype(np.float16)).astype(np.float16)
    return A, perm


def solve16(F, perm, r):
    L = np.tril(F.astype(np.float32), -1) + np.eye(len(F), dtype=np.float32)
    U = np.triu(F.astype(np.float32))
    y = np.linalg.solve(L, r[perm].astype(np.float32))
    return np.linalg.solve(U, y).astype(np.float64)


n3 = 50
for kexp in (1, 2, 3):
    A = make(n3, 10.0 ** kexp, rng)
    xt = rng.standard_normal(n3)
    b = A @ xt
    F, perm = lu16(A)
    xk = solve16(F, perm, b)
    e0 = np.linalg.norm(xk - xt) / np.linalg.norm(xt)
    errs = [e0]
    for it in range(30):
        xk = xk + solve16(F, perm, b - A @ xk)
        errs.append(np.linalg.norm(xk - xt) / np.linalg.norm(xt))
    conv = next((i for i, e in enumerate(errs) if e < 1e-14), None)
    out(**{f"h{kexp}_e0": sci(e0, 1), f"h{kexp}_end": sci(errs[-1], 1), f"h{kexp}_it": conv if conv is not None else -1})

# (4) 运算量
nn = 10 ** 4
out(fl_fact=sci(2 * nn ** 3 / 3, 1), fl_it=sci(2 * nn ** 2 + 2 * nn ** 2, 1))
