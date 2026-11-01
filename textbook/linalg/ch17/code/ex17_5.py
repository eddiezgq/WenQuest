"""17.5 节：λ-矩阵、不变因子与初等因子。
(1) 17.4 节的 6×6 矩阵 A：λI − A 的史密斯标准形 diag(1, 1, 1, 1, d₅, d₆)，不变因子 d₅ = (λ−2)，d₆ = (λ−2)³(λ+1)²；
    初等因子 (λ−2)³、(λ−2)、(λ+1)²，对应若尔当块 J₃(2)、J₁(2)、J₂(−1)；
(2) 行列式因子 D_k（k 阶子式的最大公因式）：用 3×3 的例子手算验证 d_k = D_k/D_{k−1}；
(3) 相似的判定：N(2,2) 与 N(3,1) 的不变因子不同；A 与它的转置 Aᵀ 的不变因子相同（A ~ Aᵀ）。"""
import itertools

import sympy as sp
from sympy.matrices.normalforms import invariant_factors, smith_normal_form

from _sym import stex
from bookout import out

lam = sp.Symbol("lambda")
dom = sp.QQ[lam]


def jb(l, k):
    return sp.Matrix(k, k, lambda i, j: l if i == j else (1 if j == i + 1 else 0))


J = sp.diag(jb(2, 3), jb(2, 1), jb(-1, 2))
P = sp.Matrix([[1, 0, -1, 0, 0, 0], [0, 1, 0, 1, 0, 0], [-1, 0, 1, 0, 0, 1], [0, 0, 0, 1, 0, -1], [1, 0, 0, 0, 1, 0], [-1, 0, 0, -1, 0, 1]])
A = P * J * P.inv()
inv = [sp.factor(f) for f in invariant_factors(lam * sp.eye(6) - A, domain=dom)]
out(inv=", ".join(sp.latex(f) for f in inv))
# (2) 行列式因子（3×3 例：J₂(2) ⊕ J₁(2)）
B = sp.Matrix([[2, 1, 0], [0, 2, 0], [0, 0, 2]])
Mb = lam * sp.eye(3) - B
Dk = []
for k in (1, 2, 3):
    minors = [Mb.extract(list(r), list(c)).det() for r in itertools.combinations(range(3), k) for c in itertools.combinations(range(3), k)]
    g = 0
    for m in minors:
        g = sp.gcd(g, sp.expand(m))
    Dk.append(sp.factor(sp.Poly(g, lam).monic().as_expr()))
dk = [Dk[0]] + [sp.factor(sp.cancel(Dk[i] / Dk[i - 1])) for i in (1, 2)]
snf = smith_normal_form(Mb, domain=dom)
out(Mb=stex(Mb), Dk=", ".join(sp.latex(x) for x in Dk), dk=", ".join(sp.latex(x) for x in dk),
    snf=stex(sp.Matrix(3, 3, lambda i, j: sp.factor(snf[i, j]))))
# (3) 相似判定


def invf(M):
    n = M.shape[0]
    return [sp.factor(f) for f in invariant_factors(lam * sp.eye(n) - M, domain=dom)]


N22 = sp.diag(jb(0, 2), jb(0, 2))
N31 = sp.diag(jb(0, 3), jb(0, 1))
out(inv22=", ".join(sp.latex(f) for f in invf(N22)), inv31=", ".join(sp.latex(f) for f in invf(N31)),
    AT_same=bool(invf(A) == invf(A.T)))
