"""6.3 节：排列公式与按行展开——用逆序数定义的排列公式（n! 项）；余子式与代数余子式；按第 1 行展开（递归）；
与 np.linalg.det 比较；项数 n! 的增长。"""
import math
from itertools import permutations

import numpy as np

from _num import sci
from bookout import out, tex


def inversions(p):
    return sum(1 for i in range(len(p)) for j in range(i + 1, len(p)) if p[i] > p[j])


def det_perm(A):
    n = len(A)
    return sum((-1) ** inversions(p) * math.prod(A[i][p[i]] for i in range(n)) for p in permutations(range(n)))


def minor(A, i, j):
    return [r[:j] + r[j + 1:] for k, r in enumerate(A) if k != i]


def det_cof(A):
    """按第 1 行展开（递归）。"""
    if len(A) == 1:
        return A[0][0]
    return sum((-1) ** j * A[0][j] * det_cof(minor(A, 0, j)) for j in range(len(A)))


A = [[2, 1, 1], [4, 3, 3], [8, 7, 9]]
terms = []
for p in permutations(range(3)):
    s = (-1) ** inversions(p)
    terms.append(f"{'+' if s > 0 else '-'} {A[0][p[0]]}\\cdot{A[1][p[1]]}\\cdot{A[2][p[2]]}")
out(A=tex(np.array(A, float), 0), perm=det_perm(A), cof=det_cof(A), npdet=round(float(np.linalg.det(np.array(A, float)))),
    terms=" ".join(terms)[2:], inv31=inversions((2, 0, 1)), inv321=inversions((2, 1, 0)))
# 第 1 行三个元素的代数余子式
C = [(-1) ** j * det_cof(minor(A, 0, j)) for j in range(3)]
out(C11=C[0], C12=C[1], C13=C[2])
# 按第 2 列展开（含零元素多的行或列展开更省事）
B = [[1, 0, 2, 0], [3, 0, 1, 1], [2, 5, 0, 1], [0, 0, 4, 3]]
colexp = sum((-1) ** (i + 1) * B[i][1] * det_cof(minor(B, i, 1)) for i in range(4))
out(B=tex(np.array(B, float), 0), detB=det_cof(B), colexp=colexp)
# 项数
out(f10=math.factorial(10), f20=sci(math.factorial(20), 1), f25=sci(math.factorial(25), 1))
