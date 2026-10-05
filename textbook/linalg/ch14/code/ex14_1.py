"""14.1 节：实对称矩阵的特征值为实数，属于不同特征值的特征向量正交。
S = [[2, −1, 0], [−1, 2, −1], [0, −1, 2]]：特征值 2 − √2、2、2 + √2，特征向量两两正交；非对称矩阵 [[1, 2], [0, 3]] 的特征向量不正交。
重特征值：A = [[2, 1, 1], [1, 2, 1], [1, 1, 2]] 的特征值 4、1、1，属于 1 的特征空间是一个平面，可以在其中选两个正交的特征向量。
机器人：两连杆臂末端的柔度矩阵 C = J K_q⁻¹ Jᵀ 是对称的（麦克斯韦互易定理：在 x 方向加力引起的 y 向位移等于在 y 方向加同样的力引起的 x 向位移）。"""
import numpy as np

from _arm2 import compliance
from _num import fix_sign, sci
from bookout import out, tex, vec

S = np.array([[2.0, -1, 0], [-1, 2, -1], [0, -1, 2]])
w, Q = np.linalg.eigh(S)
Q = fix_sign(Q)
out(lamS=vec(w, 4), QtQ=sci(float(np.abs(Q.T @ Q - np.eye(3)).max()) + 1e-30, 0), q1=vec(Q[:, 0], 4), q2=vec(Q[:, 1], 4), q3=vec(Q[:, 2], 4),
    exact=vec([2 - 2 ** 0.5, 2, 2 + 2 ** 0.5], 4))
N = np.array([[1.0, 2], [0, 3]])
wn, Vn = np.linalg.eig(N)
out(Ndot=float(abs(Vn[:, 0] @ Vn[:, 1])), Nang=float(np.degrees(np.arccos(abs(Vn[:, 0] @ Vn[:, 1])))))
A = np.ones((3, 3)) + np.eye(3)
wa, Qa = np.linalg.eigh(A); Qa = fix_sign(Qa)
out(lamA=", ".join(f"{x:.0f}" for x in wa), QaQ=sci(float(np.abs(Qa.T @ Qa - np.eye(3)).max()) + 1e-30, 0), qa1=vec(Qa[:, 0], 4), qa2=vec(Qa[:, 1], 4))
C = compliance(np.radians(0), np.radians(90), 2000.0, 1000.0) * 1e3     # mm/N
out(C=tex(C, 4), Csym=sci(float(abs(C[0, 1] - C[1, 0])) + 1e-30, 0), dy_fx=float(C[1, 0] * 10), dx_fy=float(C[0, 1] * 10))
