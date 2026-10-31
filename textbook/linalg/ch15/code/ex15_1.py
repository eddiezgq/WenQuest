"""15.1 节：二次型与它的矩阵。
(1) 写出 f = 2x₁² + 5x₂² + 5x₃² + 4x₁x₂ − 4x₁x₃ − 8x₂x₃ 的对称矩阵 A（交叉项系数平分到两个对称位置）；
(2) 任意方阵 B 与它的对称部分 (B + Bᵀ)/2 给出同一个二次型（随机向量检验）；
(3) 梯度 ∇(xᵀAx) = 2Ax、黑塞矩阵 2A（差分检验）；
(4) 换元 x = Cy 后二次型的矩阵是 CᵀAC；
(5) 机器人：腕部两个关节的刚度矩阵 K_q（N·m/rad），关节偏转 Δq 储存的弹性势能 U = ½ΔqᵀK_qΔq。"""
import numpy as np

from _frac import fmat
from _num import sci
from bookout import out, tex

A = np.array([[2.0, 2, -2], [2, 5, -4], [-2, -4, 5]])
f = lambda x: 2 * x[0] ** 2 + 5 * x[1] ** 2 + 5 * x[2] ** 2 + 4 * x[0] * x[1] - 4 * x[0] * x[2] - 8 * x[1] * x[2]
rng = np.random.default_rng(151)
X = rng.normal(size=(1000, 3))
out(A=tex(A), err_A=sci(max(abs(f(x) - x @ A @ x) for x in X) + 1e-17, 0))
# (2) 非对称矩阵与它的对称部分
B = np.array([[2.0, 6, -1], [-2, 5, -7], [-3, -1, 5]])
S = (B + B.T) / 2
out(B=tex(B), S=tex(S), same_S=bool(np.allclose(S, A)), err_B=sci(max(abs(x @ B @ x - x @ S @ x) for x in X) + 1e-17, 0))
# (3) 梯度与黑塞矩阵
x0 = np.array([1.0, -1.0, 2.0])
h = 1e-6
g = np.array([(f(x0 + h * e) - f(x0 - h * e)) / (2 * h) for e in np.eye(3)])
out(x0=f"({', '.join(str(int(v)) for v in x0)})", grad=f"({', '.join(str(int(round(v))) for v in 2 * A @ x0)})",
    err_g=sci(np.abs(g - 2 * A @ x0).max() + 1e-17, 0), f0=int(round(f(x0))))
# (4) 换元
C = np.array([[1.0, -1, 1 / 3], [0, 1, 2 / 3], [0, 0, 1]])        # 15.2 节配方法得到的换元
out(C=fmat(C), CAC=fmat(C.T @ A @ C))
Y = rng.normal(size=(1000, 3))
out(err_C=sci(max(abs(f(C @ y) - y @ (C.T @ A @ C) @ y) for y in Y) + 1e-17, 0))
# (5) 腕部刚度与弹性势能
Kq = np.array([[120.0, 30], [30, 60]])
dq = np.radians([1.0, -2.0])
U = 0.5 * dq @ Kq @ dq
out(Kq=tex(Kq), U_mJ=float(1000 * U), U_diag_mJ=float(1000 * 0.5 * (Kq[0, 0] * dq[0] ** 2 + Kq[1, 1] * dq[1] ** 2)))
