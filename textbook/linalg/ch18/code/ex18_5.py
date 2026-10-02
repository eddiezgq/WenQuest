"""18.5 节：极分解。算例 18.5.1（A = [[3, 0], [4, 5]]）；算例 18.5.2：由带噪声的测量得到的“旋转矩阵”的正交化。"""
import math

import numpy as np

from _arm import svd_fixed
from bookout import out, tex, vec

A = np.array([[3.0, 0.0], [4.0, 5.0]])
U, s, V = svd_fixed(A)
Q = U @ V.T
S = V @ np.diag(s) @ V.T
assert np.allclose(Q @ S, A) and np.allclose(Q.T @ Q, np.eye(2))
w, _ = np.linalg.eigh(S)
out(Q=tex(Q, 4), S=tex(S, 4), detQ=np.linalg.det(Q), qdeg=math.degrees(math.atan2(Q[1, 0], Q[0, 0])),
    S_eig=", ".join(f"{x:.4f}" for x in w[::-1]), sqrt5=math.sqrt(5), inv_sqrt5=1 / math.sqrt(5))
assert np.allclose(S, math.sqrt(5) * np.array([[2, 1], [1, 2]])) and np.allclose(Q, np.array([[2, -1], [1, 2]]) / math.sqrt(5))

# 算例 18.5.2：相机测得的工件姿态 R_meas = R_true + 噪声；求最近的正交矩阵
def rotz(t):
    c, s_ = math.cos(t), math.sin(t)
    return np.array([[c, -s_, 0], [s_, c, 0], [0, 0, 1]])


def roty(t):
    c, s_ = math.cos(t), math.sin(t)
    return np.array([[c, 0, s_], [0, 1, 0], [-s_, 0, c]])


Rt = rotz(math.radians(30)) @ roty(math.radians(20))
rng = np.random.default_rng(1852)
Rm = np.round(Rt + 0.01 * rng.standard_normal((3, 3)), 3)          # 测量结果保留 3 位小数
Um, sm, Vm = svd_fixed(Rm)
Rq = Um @ Vm.T
D = np.diag([1, 1, np.linalg.det(Um @ Vm.T)])
Rr = Um @ D @ Vm.T


def angle_err(R1, R2):
    return math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(R1.T @ R2) - 1) / 2))))


out(Rm=tex(Rm, 3), Rq=tex(Rq, 4), sm=", ".join(f"{x:.4f}" for x in sm), orth_m=np.linalg.norm(Rm.T @ Rm - np.eye(3), "fro"),
    orth_q=np.linalg.norm(Rq.T @ Rq - np.eye(3), "fro"), detq=np.linalg.det(Rq), dist_mq=np.linalg.norm(Rm - Rq, "fro"),
    err_true=angle_err(Rt, Rq), err_meas_cols=np.linalg.norm(Rm[:, 0]),
    # 只把各列除以长度（常见的“偷懒做法”），结果仍不正交
    naive_orth=np.linalg.norm((Rm / np.linalg.norm(Rm, axis=0)).T @ (Rm / np.linalg.norm(Rm, axis=0)) - np.eye(3), "fro"))
assert np.allclose(Rr, Rq)
