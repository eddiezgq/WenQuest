"""17.4 节：若尔当标准形及其证明。
(1) 由秩序列确定若尔当块：A = PJP⁻¹（6×6，整数），J = J₃(2) ⊕ J₁(2) ⊕ J₂(−1)。
    r_k = rank (A − 2I)^k；大小 ≥ k 的块数 = r_{k−1} − r_k；与 SymPy 的 jordan_form 比较；
(2) 特征多项式、秩、几何重数都相同却不相似：4×4 幂零的 N(2,2) 与 N(3,1)，区别在 N² 的秩；
(3) 加加速度轴的极点配置：三个闭环极点都放在 −10（临界阻尼的推广），闭环矩阵 A_cl 是一个 3×3 若尔当块的相似形，
    响应中有 t²e^{−10t}；从 1 mm 位置误差出发，误差不过零（无超调），衰减到 1% 的时间。"""
import numpy as np
import scipy.linalg as sl
import sympy as sp
from scipy.optimize import brentq

from _sym import stex
from bookout import out

lam, t = sp.symbols("lambda t")


def jb(l, k):
    return sp.Matrix(k, k, lambda i, j: l if i == j else (1 if j == i + 1 else 0))


J = sp.diag(jb(2, 3), jb(2, 1), jb(-1, 2))
P = sp.Matrix([[1, 0, -1, 0, 0, 0], [0, 1, 0, 1, 0, 0], [-1, 0, 1, 0, 0, 1], [0, 0, 0, 1, 0, -1], [1, 0, 0, 0, 1, 0], [-1, 0, 0, -1, 0, 1]])
out(detP=int(P.det()))
A = P * J * P.inv()
out(A=stex(A), char=sp.latex(sp.factor((lam * sp.eye(6) - A).det())), integer=bool(all(x.is_integer for x in A)))
r = [6] + [int(((A - 2 * sp.eye(6)) ** k).rank()) for k in range(1, 5)]
ge = [r[k - 1] - r[k] for k in range(1, 5)]
out(ranks=", ".join(map(str, r)), ge=", ".join(map(str, ge)),
    ranks_m=", ".join(map(str, [6] + [int(((A + sp.eye(6)) ** k).rank()) for k in range(1, 4)])))
Pj, Jj = A.jordan_form()
out(J=stex(Jj), sympy_ok=bool(Pj * Jj * Pj.inv() == A))
# (2) 不相似的两个幂零矩阵
N22 = sp.diag(jb(0, 2), jb(0, 2))
N31 = sp.diag(jb(0, 3), jb(0, 1))
out(N22=stex(N22), N31=stex(N31), rk=f"{N22.rank()}, {N31.rank()}", rk2=f"{(N22 ** 2).rank()}, {(N31 ** 2).rank()}")
# (3) 加加速度轴：x = (e, v, a)，ẋ = N x + b j，j = −K x，闭环特征多项式 (λ + 10)³ = λ³ + 30λ² + 300λ + 1000
K = [1000, 300, 30]
Acl = sp.Matrix([[0, 1, 0], [0, 0, 1], [-K[0], -K[1], -K[2]]])
out(Acl=stex(Acl), charcl=sp.latex(sp.factor((lam * sp.eye(3) - Acl).det())),
    geo=int(3 - (Acl + 10 * sp.eye(3)).rank()))
Pc, Jc = Acl.jordan_form()
out(Jc=stex(Jc))
e = sp.simplify(((Acl * t).exp() * sp.Matrix([sp.Rational(1, 1000), 0, 0]))[0])
out(e_t=sp.latex(sp.expand(e * 1000)))
f = sp.lambdify(t, e * 1000, "numpy")
ts = np.linspace(0, 2, 20001)
out(emin=float(f(ts).min()), t1pct=float(brentq(lambda s: f(s) - 0.01, 0.05, 2)))
