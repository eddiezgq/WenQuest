"""17.1 节：不能对角化的矩阵。
(1) 加加速度（jerk）控制的运动轴：状态 x = (s, v, a)，ẋ = Nx + b·j，N 是 3×3 的移位矩阵（幂零，N³ = O）。
    N 只有特征值 0、只有一个特征向量方向，不能对角化；e^{Nt} = I + Nt + N²t²/2 是多项式，给出熟悉的运动学公式；
    S 形加减速：j = ±50 m/s³ 各 0.1 s，起点静止，求终点的 s、v、a。
(2) A = [[3, 1], [−1, 1]]：二重特征值 2，几何重数 1；若尔当链 (A − 2I)v₂ = v₁，X⁻¹AX = J = [[2, 1], [0, 2]]；
(3) e^{Jt} = e^{2t}[[1, t], [0, 1]]，A^k = X J^k X⁻¹ 与直接计算比较。"""
import numpy as np
import scipy.linalg as sl
import sympy as sp

from _num import sci
from _sym import stex
from bookout import out

# (1) 移位矩阵
N = sp.Matrix([[0, 1, 0], [0, 0, 1], [0, 0, 0]])
t = sp.Symbol("t")
eN = (sp.eye(3) + N * t + N ** 2 * t ** 2 / 2)
out(N=stex(N), N2=stex(N ** 2), N3zero=bool(N ** 3 == sp.zeros(3)), eN=stex(eN),
    eN_ok=bool(sp.simplify((N * t).exp() - eN) == sp.zeros(3)), rankN=int(N.rank()), nullN=stex(N.nullspace()[0].T))
# S 形加减速：前 0.1 s j = +50，后 0.1 s j = −50（零阶保持下的精确解，16.6 节）
Nf = np.array(N.tolist(), float)
b = np.array([0.0, 0, 1])


def step(x, j, T):
    M = np.zeros((4, 4)); M[:3, :3] = Nf; M[:3, 3] = b
    E = sl.expm(M * T)
    return E[:3, :3] @ x + E[:3, 3] * j


x = np.zeros(3)
x1 = step(x, 50.0, 0.1)
x2 = step(x1, -50.0, 0.1)
out(x1=f"({x1[0] * 1000:.2f}\\ \\text{{mm}},\\ {x1[1]:.2f}\\ \\text{{m/s}},\\ {x1[2]:.0f}\\ \\text{{m/s}}^2)",
    x2=f"({x2[0] * 1000:.0f}\\ \\text{{mm}},\\ {x2[1]:.1f}\\ \\text{{m/s}},\\ {abs(x2[2]):.0f}\\ \\text{{m/s}}^2)",
    s1_formula=float(50 * 0.1 ** 3 / 6 * 1000))
# (2) 二重特征值、亏损
A = sp.Matrix([[3, 1], [-1, 1]])
lam = sp.Symbol("lambda")
out(A=stex(A), charA=sp.latex(sp.factor((A - lam * sp.eye(2)).det())), rankA2=int((A - 2 * sp.eye(2)).rank()))
v1 = (A - 2 * sp.eye(2)).nullspace()[0]
v1 = v1 / v1[0]
v2 = sp.Matrix([0, 1])                     # (A − 2I)v₂ = v₁ 的一个解
assert (A - 2 * sp.eye(2)) * v2 == v1
X = v1.row_join(v2)
J = X.inv() * A * X
out(v1=stex(v1.T), v2=stex(v2.T), X=stex(X), J=stex(J))
# (3) 幂与指数
k = 10
Ak = X * J ** k * X.inv()
out(Ak_ok=bool(Ak == A ** k), J10=stex(J ** k), A10=stex(A ** k))
eJt = sp.exp(2 * t) * sp.Matrix([[1, t], [0, 1]])
out(eJ_ok=bool(sp.simplify((J * t).exp() - eJt) == sp.zeros(2)))
# 浮点：numpy 的 eig 给出两个几乎平行的“特征向量”
w, V = np.linalg.eig(np.array(A.tolist(), float))
sinang = abs(V[0, 0] * V[1, 1] - V[1, 0] * V[0, 1]) / (np.linalg.norm(V[:, 0]) * np.linalg.norm(V[:, 1]))
out(np_w=", ".join(f"{z:.9f}" for z in np.real(w)), np_angle=sci(float(np.degrees(np.arcsin(sinang))), 1), np_split=sci(float(abs(np.real(w[0] - w[1]))), 1),
    np_cond=sci(float(np.linalg.cond(V)), 1))
