"""6.4 节：用消元法计算行列式——det A = ±（主元之积）；手算例子；排列公式与消元的耗时比较；
大矩阵的行列式会上溢或下溢，用 slogdet 求对数。"""
import math
import time
from itertools import permutations

import numpy as np
import scipy.linalg as sla

from _num import sci
from bookout import out, tex


def det_elim(A):
    """部分选主元消元，记录交换次数；det = (−1)^交换次数 × 主元之积。"""
    U = np.array(A, dtype=float)
    n, sign = len(U), 1.0
    for k in range(n - 1):
        m = k + int(np.argmax(np.abs(U[k:, k])))
        if U[m, k] == 0:
            return 0.0
        if m != k:
            U[[k, m]] = U[[m, k]]
            sign = -sign
        U[k + 1:] -= np.outer(U[k + 1:, k] / U[k, k], U[k])
    return sign * float(np.prod(np.diag(U)))


A = np.array([[0.0, 2, 1], [1, 1, 1], [2, 4, 6]])
out(A=tex(A, 0), dA=det_elim(A), npd=float(np.linalg.det(A)))
P, L, U = sla.lu(A)
out(U=tex(U, 2), psign=int(round(np.linalg.det(P))), pivprod=float(np.prod(np.diag(U))))


def det_perm(M):
    n = len(M)
    tot = 0.0
    for p in permutations(range(n)):
        inv = sum(1 for i in range(n) for j in range(i + 1, n) if p[i] > p[j])
        tot += (-1) ** inv * math.prod(M[i, p[i]] for i in range(n))
    return tot


rng = np.random.default_rng(64)
M = rng.standard_normal((9, 9))
t0 = time.perf_counter()
dp = det_perm(M)
tp = time.perf_counter() - t0
out(perm_ok=bool(abs(dp - det_elim(M)) < 1e-9 * max(1, abs(dp))), n9=math.factorial(9))
# 运算量：排列公式约 n·n! 次乘法；消元约 n³/3 次
out(perm20=sci(20 * math.factorial(20), 1), elim20=round(20 ** 3 / 3))
# 上溢、下溢与对数行列式
D = 0.1 * np.eye(400)
s, ld = np.linalg.slogdet(D)
out(under=float(np.linalg.det(D)), sign=int(s), logdet=ld, log10det=ld / math.log(10))
