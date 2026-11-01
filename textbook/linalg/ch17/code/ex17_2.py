"""17.2 节：不变子空间；凯莱–哈密顿定理与最小多项式。
(1) 凯莱–哈密顿：随机整数 4×4 矩阵 A，p(A) = O（精确计算）；由它写出 A⁻¹ = A 的三次多项式；
(2) 最小多项式：diag(2, 2, 3) → (λ−2)(λ−3)；若尔当块 J₂(2) ⊕ (3) → (λ−2)²(λ−3)；特征多项式相同、最小多项式不同；
(3) 无差拍控制：位置轴（双积分器 ẍ = u/m，m = 1 kg）每 T = 0.01 s 采样、零阶保持。选反馈 u = −Kx 使闭环特征多项式为 λ²，
    由凯莱–哈密顿 A_cl² = O：任何初始误差两步归零。A_cl ≠ O，最小多项式是 λ²；
(4) 模型误差：实际质量比设计值大 5% 时，闭环特征值不再是 0，离开原点约 √δ 的量级（17.7 节）。"""
import numpy as np
import sympy as sp

from _num import sci
from _sym import stex
from bookout import out, tex, vec

lam = sp.Symbol("lambda")
A = sp.Matrix([[2, 1, 0, 3], [1, 0, -1, 2], [0, 4, 1, 1], [-2, 1, 0, 1]])
p = (lam * sp.eye(4) - A).det().expand()
coeffs = sp.Poly(p, lam).all_coeffs()
pA = sp.zeros(4)
for c in coeffs:
    pA = pA * A + c * sp.eye(4)
out(A=stex(A), p=sp.latex(p), pA_zero=bool(pA == sp.zeros(4)), detA=int(A.det()))
# A⁻¹ = −(A³ + c₁A² + c₂A + c₃I)/c₄
c = coeffs
Ainv = -(A ** 3 + c[1] * A ** 2 + c[2] * A + c[3] * sp.eye(4)) / c[4]
out(inv_ok=bool(Ainv == A.inv()), c4=int(c[4]))


def minpoly(M):
    """最小多项式：在特征多项式的因式里找次数最低的零化多项式。"""
    n = M.shape[0]
    roots = sp.roots(sp.Poly((lam * sp.eye(n) - M).det(), lam))
    best = None
    import itertools
    for ks in itertools.product(*[range(1, m + 1) for m in roots.values()]):
        P = sp.eye(n)
        for (r, _), k in zip(roots.items(), ks):
            P = P * (M - r * sp.eye(n)) ** k
        if P == sp.zeros(n) and (best is None or sum(ks) < sum(best[1])):
            best = (list(roots.keys()), ks)
    return sp.Mul(*[(lam - r) ** k for r, k in zip(*best)])


D = sp.diag(2, 2, 3)
Jb = sp.Matrix([[2, 1, 0], [0, 2, 0], [0, 0, 3]])
out(char_D=sp.latex(sp.factor((lam * sp.eye(3) - D).det())), min_D=sp.latex(minpoly(D)),
    char_J=sp.latex(sp.factor((lam * sp.eye(3) - Jb).det())), min_J=sp.latex(minpoly(Jb)), A_distinct=bool(sp.gcd(p, sp.diff(p, lam)) == 1))
# (3) 无差拍
T, m = 0.01, 1.0
Ad = np.array([[1, T], [0, 1]])
Bd = np.array([[T * T / 2], [T]]) / m
# 闭环 A_d − B_d K 的特征多项式 λ² + (k₁T²/2 + k₂T − 2)λ + (k₁T²/2 − k₂T + 1)，令两系数为 0
k1, k2 = 1 / T ** 2, 1.5 / T
K = np.array([[k1 * m, k2 * m]])
Acl = Ad - Bd @ K
out(K=f"({K[0, 0]:.0f},\\ {K[0, 1]:.0f})", Acl=tex(Acl, 4), Acl2=sci(float(np.abs(Acl @ Acl).max()) + 1e-30, 0), ev=vec(np.abs(np.linalg.eigvals(Acl)), 0))
x = np.array([0.01, 0.0])
traj, us = [x], []
for k in range(4):
    u = float((-K @ x)[0]); us.append(u)
    x = Ad @ x + (Bd * u).ravel(); traj.append(x)
out(traj=", ".join(f"({1000 * s[0]:.2f}, {s[1]:.3f})" for s in traj[:3]), u0=us[0], u1=us[1], x2=sci(float(np.abs(traj[2]).max()) + 1e-30, 0))
# (4) 质量误差 5%
for name, d in (("5", 0.05), ("1", 0.01)):
    Acl_t = Ad - Bd / (1 + d) @ K
    ev = np.linalg.eigvals(Acl_t)
    out(**{f"ev_err{name}": float(np.abs(ev).max()), f"sqrt{name}": float(np.sqrt(d))})
x = np.array([0.01, 0.0]); Acl_t = Ad - Bd / 1.05 @ K
xs = [x]
for k in range(6):
    x = Acl_t @ x; xs.append(x)
out(err_steps=", ".join(f"{1000 * s[0]:.3f}" for s in xs[:6]))
