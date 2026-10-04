"""6.5 节：克拉默法则与伴随矩阵——2 阶、3 阶方程组的克拉默法则；伴随矩阵与逆矩阵公式 A⁻¹ = adj(A)/det A；
AGV 矩阵的逆；运算量的比较。"""
from fractions import Fraction

import numpy as np

from bookout import out, tex, vec


def det(M):
    M = [list(r) for r in M]
    if len(M) == 1:
        return M[0][0]
    return sum((-1) ** j * M[0][j] * det([r[:j] + r[j + 1:] for r in M[1:]]) for j in range(len(M)))


def texF(M):
    def f(x):
        x = Fraction(x)
        return str(x.numerator) if x.denominator == 1 else rf"{'-' if x < 0 else ''}\tfrac{{{abs(x.numerator)}}}{{{x.denominator}}}"
    return r"\begin{pmatrix} " + r" \\ ".join(" & ".join(f(x) for x in r) for r in M) + r" \end{pmatrix}"


# 3 阶：3.2 节的方程组
A = [[2, 1, 1], [4, 3, 3], [8, 7, 9]]
b = [3, 7, 19]
D = det(A)
Ds = []
for j in range(3):
    Aj = [r[:] for r in A]
    for i in range(3):
        Aj[i][j] = b[i]
    Ds.append(det(Aj))
out(D=D, D1=Ds[0], D2=Ds[1], D3=Ds[2], x=vec(np.array(Ds, float) / D, 0))
# 伴随矩阵：代数余子式矩阵的转置
cof = [[(-1) ** (i + j) * det([r[:j] + r[j + 1:] for k, r in enumerate(A) if k != i]) for j in range(3)] for i in range(3)]
adj = [[cof[j][i] for j in range(3)] for i in range(3)]
inv = [[Fraction(adj[i][j], D) for j in range(3)] for i in range(3)]
out(adj=texF(adj), inv=texF(inv), inv_ok=bool(np.allclose(np.array(inv, float), np.linalg.inv(np.array(A, float)))))
# A·adj(A) = det(A) I
out(Aadj=texF((np.array(A) @ np.array(adj)).tolist()))
