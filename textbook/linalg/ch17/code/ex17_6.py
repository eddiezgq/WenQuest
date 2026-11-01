"""17.6 节：有理标准形。
(1) 友矩阵 C(p)：p = λ³ + 2λ² − 5λ + 7 的友矩阵的特征多项式与最小多项式都是 p；
(2) 17.4 节的 A 的有理标准形 diag(C(λ − 2), C((λ−2)³(λ+1)²))：与 A 的不变因子相同，因而相似；
(3) 只用有理数：R = diag(R₉₀, R₉₀)（两个 90° 旋转块）的不变因子 λ² + 1、λ² + 1，有理标准形 diag(C(λ²+1), C(λ²+1))，
    特征值 ±i 不在 ℚ（也不在 ℝ）里，若尔当形要用复数，有理标准形不用；
(4) 控制：16.1 节的两节点热模型 ẋ = Ax + bP 化为能控标准形（友矩阵形式）z = T⁻¹x，A_c = T⁻¹AT 的最后一行是特征多项式的系数；
    在能控标准形中极点配置一目了然：K_c = (目标系数 − 原系数)，再变回 K = K_cT⁻¹；目标极点 −0.02、−0.05 s⁻¹。"""
import sympy as sp
from sympy.matrices.normalforms import invariant_factors

from _sym import stex
from bookout import out

lam = sp.Symbol("lambda")
dom = sp.QQ[lam]


def companion(p):
    c = sp.Poly(p, lam).all_coeffs()[::-1]       # a₀, a₁, …, 1
    n = len(c) - 1
    C = sp.zeros(n)
    for i in range(n - 1):
        C[i, i + 1] = 1
    for j in range(n):
        C[n - 1, j] = -c[j]
    return C


p = lam ** 3 + 2 * lam ** 2 - 5 * lam + 7
C = companion(p)
out(C=stex(C), charC=sp.latex(sp.expand((lam * sp.eye(3) - C).det())),
    invC=", ".join(sp.latex(sp.factor(f)) for f in invariant_factors(lam * sp.eye(3) - C, domain=dom)))


def jb(l, k):
    return sp.Matrix(k, k, lambda i, j: l if i == j else (1 if j == i + 1 else 0))


J = sp.diag(jb(2, 3), jb(2, 1), jb(-1, 2))
P = sp.Matrix([[1, 0, -1, 0, 0, 0], [0, 1, 0, 1, 0, 0], [-1, 0, 1, 0, 0, 1], [0, 0, 0, 1, 0, -1], [1, 0, 0, 0, 1, 0], [-1, 0, 0, -1, 0, 1]])
A = P * J * P.inv()
d6 = sp.expand((lam - 2) ** 3 * (lam + 1) ** 2)
Rf = sp.diag(companion(lam - 2), companion(d6))
same = [sp.factor(f) for f in invariant_factors(lam * sp.eye(6) - Rf, domain=dom)] == [sp.factor(f) for f in invariant_factors(lam * sp.eye(6) - A, domain=dom)]
out(d6=sp.latex(d6), C6=stex(companion(d6)), Rf_same=bool(same))
# (3) 旋转块
R90 = sp.Matrix([[0, -1], [1, 0]])
R = sp.diag(R90, R90)
out(invR=", ".join(sp.latex(sp.factor(f)) for f in invariant_factors(lam * sp.eye(4) - R, domain=dom)),
    CR=stex(companion(lam ** 2 + 1)))
# (4) 能控标准形：16.1 节的两节点热模型（状态为偏离工作点的温升，输入为加热功率的偏差）
Aj = sp.Matrix([[sp.Rational(-1, 25), sp.Rational(1, 25)], [sp.Rational(1, 250), sp.Rational(-3, 500)]])
Bj = sp.Matrix([sp.Rational(1, 50), 0])
W = Bj.row_join(Aj * Bj)                        # 能控性矩阵
a = sp.Poly((lam * sp.eye(2) - Aj).det(), lam).all_coeffs()[::-1]   # a₀, a₁, 1
T = W * sp.Matrix([[a[1], 1], [1, 0]])          # 能控标准形的变换：x = Tz
Ac, Bc = sp.simplify(T.inv() * Aj * T), sp.simplify(T.inv() * Bj)
out(Aj=stex(Aj), W=stex(W), rankW=int(W.rank()), a=f"{sp.latex(a[1])},\\ {sp.latex(a[0])}", T=stex(T), Ac=stex(Ac), Bc=stex(Bc.T))
target = sp.Poly(sp.expand((lam + sp.Rational(1, 50)) * (lam + sp.Rational(1, 20))), lam).all_coeffs()[::-1]
Kc = sp.Matrix([[target[0] - a[0], target[1] - a[1]]])
K = sp.simplify(Kc * T.inv())
out(target=sp.latex(sp.expand((lam + sp.Rational(1, 50)) * (lam + sp.Rational(1, 20)))), Kc=stex(Kc), K=stex(K),
    cl=sp.latex(sp.factor((lam * sp.eye(2) - (Aj - Bj * K)).det())), Kf=f"({float(K[0]):.3f},\\ {float(K[1]):.3f})")
