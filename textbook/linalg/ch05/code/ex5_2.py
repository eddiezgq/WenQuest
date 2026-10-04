"""5.2 节：初等矩阵——三种行变换各对应一个初等矩阵，左乘就是做行变换；它们的逆；
三步消元 E₃₂E₃₁E₂₁A = U；高斯–若尔当法：(A | I) 化为 (I | A⁻¹)，用分数精确计算。"""
from fractions import Fraction

import numpy as np

from _elim import F, rref, tex_aug, tex_frac
from bookout import out, tex


def texF(M):
    rows = " \\\\ ".join(" & ".join(tex_frac(x) for x in r) for r in M)
    return f"\\begin{{pmatrix}} {rows} \\end{{pmatrix}}"


def mulF(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def eye(n):
    return [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]


A = F([[2, 1, 1], [4, 3, 3], [8, 7, 9]])
E21, E31, E32 = eye(3), eye(3), eye(3)
E21[1][0], E31[2][0], E32[2][1] = Fraction(-2), Fraction(-4), Fraction(-3)
U = mulF(E32, mulF(E31, mulF(E21, A)))
out(A=texF(A), E21=texF(E21), E31=texF(E31), E32=texF(E32), E21A=texF(mulF(E21, A)), U=texF(U))
# 初等矩阵的逆：把减号改成加号
E21i = eye(3)
E21i[1][0] = Fraction(2)
out(E21i=texF(E21i), E21chk=mulF(E21i, E21) == eye(3))
# 交换与数乘的初等矩阵
Ps = [eye(3)[i] for i in (1, 0, 2)]
D = eye(3)
D[1][1] = Fraction(5)
out(Pswap=texF(Ps), PswapA=texF(mulF(Ps, A)), Dsc=texF(D), DscA=texF(mulF(D, A)))
# 消元矩阵之积 E = E₃₂E₃₁E₂₁ 与它的逆 L（乘数原样出现在 L 中，E 中却混在一起）
E = mulF(E32, mulF(E31, E21))
E31i, E32i = eye(3), eye(3)
E31i[2][0], E32i[2][1] = Fraction(4), Fraction(3)
L = mulF(E21i, mulF(E31i, E32i))   # L = E₂₁⁻¹E₃₁⁻¹E₃₂⁻¹
out(E=texF(E), L=texF(L), EL=mulF(E, L) == eye(3))
# 高斯–若尔当：(A | I) → (I | A⁻¹)
aug = [list(A[i]) + list(eye(3)[i]) for i in range(3)]
R, piv = rref(aug, 3)
Ainv = [r[3:] for r in R]
out(aug=tex_aug(aug, 3), R=tex_aug(R, 3), Ainv=texF(Ainv), chk=mulF(A, Ainv) == eye(3),
    np_inv=bool(np.allclose(np.linalg.inv(np.array(A, dtype=float)), np.array(Ainv, dtype=float))))
