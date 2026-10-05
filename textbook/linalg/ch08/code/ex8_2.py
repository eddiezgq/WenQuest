"""8.2 节：矩阵的秩——主元个数；列秩等于行秩；A = CR（C 为主元列，R 为简化行阶梯形的非零行）；秩一矩阵是外积。"""
import numpy as np

from _a import A
from _elim import rref, tex_frac
from bookout import out, tex

R, piv = rref(A.tolist())
r = len(piv)
C = A[:, piv]
Rn = np.array([[float(x) for x in row] for row in R[:r]])
out(rank=r, rankT=int(np.linalg.matrix_rank(A.T)), C=tex(C, 0),
    Rn="\\begin{pmatrix} " + " \\\\ ".join(" & ".join(tex_frac(x) for x in row) for row in R[:r]) + " \\end{pmatrix}",
    CR=bool(np.allclose(C @ Rn, A)))
u, v = np.array([1.0, 2, 3]), np.array([2.0, 0, 1, 1])
out(uvT=tex(np.outer(u, v), 0), r1=int(np.linalg.matrix_rank(np.outer(u, v))))
# A 写成 r 个秩一矩阵之和：C 的第 i 列乘 R 的第 i 行
out(o1=tex(np.outer(C[:, 0], Rn[0]), 0), o2=tex(np.outer(C[:, 1], Rn[1]), 0))
