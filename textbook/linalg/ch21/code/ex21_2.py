"""21.2 节：矩阵函数 f(A)。三种定义（幂级数、对角化、插值多项式）给出同一个结果；若尔当块上的 f(J)；
expm、logm、sqrtm；机器人姿态插值：R(t) = R₀ exp(t·log(R₀ᵀR₁)) 始终是旋转矩阵、匀速转动，
而对矩阵元素直接做线性插值得到的不是旋转矩阵。"""
import math

import numpy as np
from scipy.linalg import expm, logm, sqrtm

from bookout import out, tex, vec

# (1) 对称矩阵：三种定义
A = np.array([[2.0, 1.0], [1.0, 2.0]])
lam, V = np.linalg.eigh(A)
eA_diag = V @ np.diag(np.exp(lam)) @ V.T
eA_ser, term = np.zeros((2, 2)), np.eye(2)
for k in range(30):
    eA_ser += term
    term = term @ A / (k + 1)
l1, l2 = lam
eA_int = (math.exp(l1) * (A - l2 * np.eye(2)) / (l1 - l2) + math.exp(l2) * (A - l1 * np.eye(2)) / (l2 - l1))
assert np.allclose(eA_diag, eA_ser) and np.allclose(eA_diag, eA_int) and np.allclose(eA_diag, expm(A))
sA = V @ np.diag(np.sqrt(lam)) @ V.T
assert np.allclose(sA @ sA, A) and np.allclose(sA, sqrtm(A))
out(A=tex(A, 0), lam=vec(lam, 0), eA=tex(eA_diag, 3), sA=tex(sA, 4), c1=float((math.e ** 3 + math.e) / 2), c2=float((math.e ** 3 - math.e) / 2))
# 级数部分和的误差：前 k 项
errs = []
eA_ser, term = np.zeros((2, 2)), np.eye(2)
for k in range(20):
    eA_ser += term
    term = term @ A / (k + 1)
    errs.append(np.linalg.norm(eA_ser - eA_diag, 2))
out(ser5=float(errs[4]), ser10=float(errs[9]), ser15=float(errs[14]))

# (2) 若尔当块：f(J) = [[f, f′, f″/2], [0, f, f′], [0, 0, f]]
lj = 0.5
J = np.array([[lj, 1, 0], [0, lj, 1], [0, 0, lj]])
fJ = math.exp(lj) * np.array([[1, 1, 0.5], [0, 1, 1], [0, 0, 1]])
assert np.allclose(expm(J), fJ)
sJ = sqrtm(J)
fs = lambda x: math.sqrt(x)
sJ_formula = np.array([[fs(lj), 0.5 * lj ** -0.5, 0.5 * (-0.25) * lj ** -1.5], [0, fs(lj), 0.5 * lj ** -0.5], [0, 0, fs(lj)]])
assert np.allclose(sJ, sJ_formula)
out(J=tex(J, 1), sJ=tex(sJ_formula, 4))
# 没有平方根的矩阵：N = [[0, 1], [0, 0]]
# 负特征值的 log：对数不是实矩阵
R180 = np.diag([-1.0, -1.0])
L180 = logm(R180)
out(L180=tex(np.real(L180), 4), L180im=float(np.max(np.abs(np.imag(L180)))))

# (3) 机器人姿态插值：工具从 R₀ 转到 R₁
def rot(axis, ang):
    k = np.asarray(axis, float) / np.linalg.norm(axis)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K


def log_rot(R):
    th = math.acos(max(-1.0, min(1.0, (np.trace(R) - 1) / 2)))
    W = (R - R.T) * (th / (2 * math.sin(th)))
    return W, th


R0 = rot([0, 0, 1], math.radians(20))
R1 = rot([1, 0, 0], math.radians(90)) @ rot([0, 0, 1], math.radians(30))
Rrel = R0.T @ R1
W, th = log_rot(Rrel)
assert np.allclose(W, np.real(logm(Rrel)), atol=1e-10) and np.allclose(expm(W), Rrel)
axis = np.array([W[2, 1], W[0, 2], W[1, 0]]) / th
out(R0=tex(R0, 3), R1=tex(R1, 3), W=tex(W, 3), th=math.degrees(th), axis=vec(axis, 3))
# 两种插值：t = 0.5
Rexp = R0 @ expm(0.5 * W)
Rlin = 0.5 * R0 + 0.5 * R1
out(Rexp=tex(Rexp, 3), Rlin=tex(Rlin, 3), detlin=float(np.linalg.det(Rlin)), orth_lin=float(np.linalg.norm(Rlin.T @ Rlin - np.eye(3), 2)),
    orth_exp=float(np.linalg.norm(Rexp.T @ Rexp - np.eye(3), 2)))
# 转过的角度随 t：指数插值严格线性；线性插值后再正交化（SVD 取最近的旋转），角速度不均匀
ts = np.linspace(0, 1, 11)
ang_exp, ang_lin = [], []
for t in ts:
    Re = R0 @ expm(t * W)
    U, _, Vt = np.linalg.svd((1 - t) * R0 + t * R1)
    Rl = U @ Vt
    ang_exp.append(math.degrees(math.acos(max(-1, min(1, (np.trace(R0.T @ Re) - 1) / 2)))))
    ang_lin.append(math.degrees(math.acos(max(-1, min(1, (np.trace(R0.T @ Rl) - 1) / 2)))))
dl = np.diff(ang_lin)
out(step_exp=float(np.diff(ang_exp)[0]), step_lin_min=float(dl.min()), step_lin_max=float(dl.max()))
# 迹与行列式：det exp(A) = e^{tr A}
M = np.array([[0.3, -1.2, 0.5], [0.8, -0.1, 0.4], [0.0, 0.7, 0.2]])
out(det_eM=float(np.linalg.det(expm(M))), e_trM=float(math.exp(np.trace(M))))
# 不可交换时 e^{A+B} ≠ e^A e^B
P = np.array([[0.0, 1.0], [0.0, 0.0]])
Q = np.array([[0.0, 0.0], [1.0, 0.0]])
out(eApB=tex(expm(P + Q), 4), eAeB=tex(expm(P) @ expm(Q), 4))
