"""10.3 节：投影矩阵。向直线 a = (1, 2, 2) 投影：P = aaᵀ/aᵀa；向 A = [[1, 0], [1, 1], [1, 2]] 的列空间（ℝ³ 中的平面）投影：
P = A(AᵀA)⁻¹Aᵀ，b = (6, 0, 0) 的投影 p = (5, 2, −1)，误差 e = (1, −2, 1) 与平面垂直；P² = P，Pᵀ = P；平面上任何别的点都离 b 更远。
三连杆臂的零空间投影 N = I − Jᵀ(JJᵀ)⁻¹J：把“想让关节 3 转”的意图投影成不影响末端的自运动。"""
import numpy as np
import scipy.linalg as sla

from _frac import fmat, fvec
from _num import sci
from bookout import out, tex, vec

a = np.array([1.0, 2, 2])
Pa = np.outer(a, a) / (a @ a)
b1 = np.array([1.0, 1, 1])
out(Pa=fmat(Pa), pa=fvec(Pa @ b1), rPa=int(np.linalg.matrix_rank(Pa)))
A = np.array([[1.0, 0], [1, 1], [1, 2]])
b = np.array([6.0, 0, 0])
P = A @ np.linalg.solve(A.T @ A, A.T)
p, e = P @ b, b - P @ b
out(A=tex(A, 0), AtA=tex(A.T @ A, 0), P=fmat(P), p=fvec(p), e=fvec(e), eA=vec(A.T @ e, 0), ne=float(np.linalg.norm(e)),
    PP=float(np.abs(P @ P - P).max()), PT=float(np.abs(P - P.T).max()), trP=float(np.trace(P)), IP=fmat(np.eye(3) - P))
# 平面上的随机点离 b 都不比 p 近
rng = np.random.default_rng(10)
d = min(float(np.linalg.norm(A @ rng.normal(size=2) * 3 - b)) for _ in range(10000))
out(dmin=d)
# 三连杆臂（8.3 节）的零空间投影
L = 0.3
th = np.radians([30, 45, -60])
c = np.cumsum(th)
J = np.array([[-L * np.sin(c[i:]).sum() for i in range(3)], [L * np.cos(c[i:]).sum() for i in range(3)]])
N = np.eye(3) - J.T @ np.linalg.solve(J @ J.T, J)
z = np.array([0.0, 0, 0.2])                     # 想让关节 3 以 0.2 rad/s 转（例如远离关节极限）
nz = N @ z
nv = sla.null_space(J)[:, 0]
out(N=tex(N, 4), Nz=vec(nz, 4), JNz=sci(float(np.abs(J @ nz).max()) + 1e-18, 0), NN=float(np.abs(N @ N - N).max()), trN=float(np.trace(N)),
    par=float(abs(nz @ nv) / np.linalg.norm(nz)))
