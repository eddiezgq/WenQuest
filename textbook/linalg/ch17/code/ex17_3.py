"""17.3 节：根子空间分解。
A = PJP⁻¹，J = J₂(1) ⊕ (−1) ⊕ (−1)，P 为整数可逆矩阵（det P = 1），所以 A 是整数矩阵。
(1) 特征空间 E₁ = N(A − I) 只有 1 维，根子空间 G₁ = N((A − I)²) 有 2 维；E₋₁ = G₋₁ 有 2 维；ℂ⁴ = G₁ ⊕ G₋₁；
(2) 用贝祖等式 a(λ)(λ−1)² + b(λ)(λ+1) = 1 构造投影 P₁ = b(A)(A + I)、P₋₁ = a(A)(A − I)²：P₁ + P₋₁ = I，P₁² = P₁，P₁P₋₁ = O；
(3) 若尔当–谢瓦莱分解 A = D + N：D = 1·P₁ + (−1)·P₋₁ 可对角化，N = A − D 幂零（N² = O），DN = ND；
    e^{At} = e^{Dt}(I + Nt)，与 SymPy 的精确指数比较。"""
import sympy as sp

from _sym import stex
from bookout import out

lam, t = sp.symbols("lambda t")
J = sp.diag(sp.Matrix([[1, 1], [0, 1]]), -1, -1)
P = sp.Matrix([[1, 1, 0, 0], [0, 1, 1, 0], [0, 0, 1, 1], [1, 1, 1, 2]])
assert P.det() == 1 or P.det() == -1
A = P * J * P.inv()
out(A=stex(A), detP=int(P.det()), char=sp.latex(sp.factor((lam * sp.eye(4) - A).det())))
I4 = sp.eye(4)
E1 = (A - I4).nullspace()
G1 = ((A - I4) ** 2).nullspace()
Em = (A + I4).nullspace()
Gm = ((A + I4) ** 2).nullspace()
out(dimE1=len(E1), dimG1=len(G1), dimEm=len(Em), dimGm=len(Gm),
    E1=stex(E1[0].T), G1=", ".join(stex(v.T) for v in G1), Gm=", ".join(stex(v.T) for v in Gm),
    span_ok=bool(sp.Matrix.hstack(*G1, *Gm).rank() == 4))
# (2) 贝祖等式
q1, q2 = (lam - 1) ** 2, lam + 1
a, b, g = sp.gcdex(sp.expand(q1), q2, lam)
assert sp.simplify(g - 1) == 0


def polyM(f, M):
    f = sp.Poly(sp.expand(f), lam)
    R = sp.zeros(M.shape[0])
    for c in f.all_coeffs():
        R = R * M + c * sp.eye(M.shape[0])
    return R


P1 = polyM(b * q2, A)
Pm = polyM(a * q1, A)
out(a=sp.latex(sp.expand(a)), b=sp.latex(sp.expand(b)), P1=stex(P1), Pm=stex(Pm),
    proj_ok=bool(P1 + Pm == I4 and P1 * P1 == P1 and P1 * Pm == sp.zeros(4)),
    rangeP1=bool(((A - I4) ** 2 * P1) == sp.zeros(4)))
# (3) D + N
D = P1 - Pm
Nn = A - D
out(D=stex(D), N=stex(Nn), N2zero=bool(Nn ** 2 == sp.zeros(4)), commute=bool(D * Nn == Nn * D), Nzero=bool(Nn == sp.zeros(4)),
    D_diag=bool(D.is_diagonalizable()))
eDt = sp.exp(t) * P1 + sp.exp(-t) * Pm
eAt = sp.simplify(eDt * (I4 + Nn * t))
out(eAt_ok=bool(sp.simplify(eAt - (A * t).exp()) == sp.zeros(4)), eAt=stex(sp.simplify(eAt)))
