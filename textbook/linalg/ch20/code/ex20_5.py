"""20.5 节：前向误差与后向误差；后向稳定性。二次方程的小根：问题良态、算法不稳定；
条件数从 10² 到 10¹⁴ 的方程组：后向误差始终约为 ε，前向误差约为 κ 乘后向误差；
部分选主元的增长因子：威尔金森矩阵上它达到 2ⁿ⁻¹，后向稳定性失效，而 QR 分解不受影响。"""
import math

import numpy as np
import scipy.linalg as sla

from _num import sci
from bookout import out

eps = np.finfo(float).eps
u = eps / 2

# (1) x² − 10⁸x + 1 = 0 的小根（真值约 1.0000000000000000e-8）
b = 1e8
disc = math.sqrt(b * b - 4)
x_naive = (b - disc) / 2
x_big = (b + disc) / 2
x_good = 1 / x_big                                # 韦达定理：两根之积为 1
from decimal import Decimal, getcontext           # noqa: E402
getcontext().prec = 50
x_true = float((Decimal(b) - (Decimal(b) ** 2 - 4).sqrt()) / 2)
out(x_naive=sci(x_naive, 6), x_good=sci(x_good, 6), x_true=sci(x_true, 6),
    rel_naive=sci(abs(x_naive - x_true) / x_true, 0), rel_good=float(abs(x_good - x_true) / x_true))

# (2) 条件数不同的方程组：后向误差、前向误差
rng = np.random.default_rng(2005)
n = 100
for k in (2, 6, 10, 14):
    Q1, _ = np.linalg.qr(rng.standard_normal((n, n)))
    Q2, _ = np.linalg.qr(rng.standard_normal((n, n)))
    s = np.logspace(0, -k, n)
    A = Q1 @ np.diag(s) @ Q2.T
    x = np.ones(n)
    bb = A @ x
    xh = np.linalg.solve(A, bb)
    r = bb - A @ xh
    eta = np.linalg.norm(r) / (np.linalg.norm(A, 2) * np.linalg.norm(xh) + np.linalg.norm(bb))
    fwd = np.linalg.norm(xh - x) / np.linalg.norm(x)
    kap = np.linalg.cond(A)
    out(**{f"eta{k}": sci(eta, 1), f"fwd{k}": sci(fwd, 1), f"keta{k}": sci(kap * eta, 1)})

# (3) 增长因子：威尔金森矩阵（对角线 1，严格下三角 −1，最后一列 1），部分选主元不换行，U 的最后一列翻倍增长
for nw in (20, 60):
    W = np.eye(nw) - np.tril(np.ones((nw, nw)), -1)
    W[:, -1] = 1.0
    P, L, U = sla.lu(W)
    growth = np.abs(U).max() / np.abs(W).max()
    xw = rng.standard_normal(nw)
    bw = W @ xw
    x_lu = np.linalg.solve(W, bw)
    Qw, Rw = np.linalg.qr(W)
    x_qr = sla.solve_triangular(Rw, Qw.T @ bw)
    out(**{f"g{nw}": sci(growth, 1), f"kW{nw}": float(np.linalg.cond(W)),
           f"flu{nw}": sci(np.linalg.norm(x_lu - xw) / np.linalg.norm(xw) + 1e-30, 0),
           f"fqr{nw}": sci(np.linalg.norm(x_qr - xw) / np.linalg.norm(xw) + 1e-30, 0)})
out(eps=sci(eps, 1), u=sci(u, 1))
# 随机矩阵上的增长因子很小（实践中几乎总是如此）
gs = []
for _ in range(200):
    G = rng.standard_normal((100, 100))
    _, _, Ug = sla.lu(G)
    gs.append(np.abs(Ug).max() / np.abs(G).max())
out(g_rand=float(np.max(gs)), g_med=float(np.median(gs)))
