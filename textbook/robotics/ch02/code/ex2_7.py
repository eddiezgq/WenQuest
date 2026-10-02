"""2.7 节的算例：格拉姆-施密特正交化。

算例 2.7.1：三点法示教工件坐标系（用户坐标系）。示教点 p0（原点）、p1（x 轴上）、p2（xy 平面内），单位 mm。
           两个示教方向不严格垂直；用格拉姆-施密特法得到 x、y 轴，第三根轴用同一方法由 (0, 0, 1) 得到，
           与叉积 x × y 核对；组成的矩阵是旋转矩阵。写成 QR 分解。换先后次序，结果不同。
算例 2.7.2：传感器给出的姿态矩阵 M（与算例 4.8.2 相同）带有误差，按列做格拉姆-施密特正交化：第 1 列方向不变，
           误差被推给后两列。
算例 2.7.3：几乎线性相关的三列（Läuchli 矩阵，ε = 1e-8）：经典格拉姆-施密特法失去正交性，修正的方法保持住。
"""
import math

import numpy as np

from bookout import out, tex, vec


def gs(A):
    """经典格拉姆-施密特法：返回 Q（各列标准正交）和上三角 R，A = QR。"""
    A = np.asarray(A, float)
    m, n = A.shape
    Q, R = np.zeros((m, n)), np.zeros((n, n))
    for j in range(n):
        w = A[:, j].copy()
        for i in range(j):
            R[i, j] = Q[:, i] @ A[:, j]            # 与原来的第 j 列作点积
            w -= R[i, j] * Q[:, i]
        R[j, j] = np.linalg.norm(w)
        Q[:, j] = w / R[j, j]
    return Q, R


def mgs(A):
    """修正的格拉姆-施密特法：每减去一个投影，就用减过之后的向量去算下一个投影。"""
    A = np.asarray(A, float)
    m, n = A.shape
    Q, R = np.zeros((m, n)), np.zeros((n, n))
    W = A.copy()
    for j in range(n):
        R[j, j] = np.linalg.norm(W[:, j])
        Q[:, j] = W[:, j] / R[j, j]
        for k in range(j + 1, n):
            R[j, k] = Q[:, j] @ W[:, k]
            W[:, k] -= R[j, k] * Q[:, j]
    return Q, R


# ---------------------------------------------------------------- 算例 2.7.1
p0 = np.array([500.0, -200.0, 30.0])
p1 = np.array([800.0, -195.0, 31.0])
p2 = np.array([505.0, 100.0, 29.0])
a1, a2 = p1 - p0, p2 - p0
ang = math.degrees(math.acos(a1 @ a2 / (np.linalg.norm(a1) * np.linalg.norm(a2))))
e1 = a1 / np.linalg.norm(a1)
r12 = e1 @ a2
w2 = a2 - r12 * e1
e2 = w2 / np.linalg.norm(w2)
assert abs(e1 @ e2) < 1e-15
a3 = np.array([0.0, 0.0, 1.0])
w3 = a3 - (e1 @ a3) * e1 - (e2 @ a3) * e2
e3 = w3 / np.linalg.norm(w3)
assert np.allclose(e3, np.cross(e1, e2))                          # 与叉积（第 3 章）一致
Rf = np.column_stack([e1, e2, e3])
assert np.allclose(Rf.T @ Rf, np.eye(3)) and abs(np.linalg.det(Rf) - 1) < 1e-12
A = np.column_stack([a1, a2])
Q, R = gs(A)
assert np.allclose(Q @ R, A) and np.allclose(Q[:, 0], e1) and np.allclose(Q[:, 1], e2)
Qn, Rn = np.linalg.qr(A)                                          # 数值库（豪斯霍尔德变换）：各列可能差一个符号
S = np.diag(np.sign(np.diag(Rn)))
assert np.allclose(Qn @ S, Q) and np.allclose(S @ Rn, R)
dev_y = math.degrees(math.acos(e2 @ a2 / np.linalg.norm(a2)))     # y 轴相对示教方向转过的角度
# 换次序：先定 y 轴
Q2, _ = gs(np.column_stack([a2, a1]))
x_alt = Q2[:, 1]
dx_alt = math.degrees(math.acos(min(1.0, x_alt @ e1)))
assert dx_alt > 0.5

# ---------------------------------------------------------------- 算例 2.7.2
def rot_x(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_z(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


R_d = rot_z(math.radians(30)) @ rot_x(math.radians(45))
noise = np.array([[0.004, -0.010, 0.006], [0.008, 0.003, -0.005], [-0.006, 0.009, 0.002]])
M = R_d + noise                                                    # 与算例 4.8.2 相同
G, _ = gs(M)
assert np.allclose(G.T @ G, np.eye(3)) and np.linalg.det(G) > 0
turn = [math.degrees(math.acos(min(1.0, G[:, j] @ M[:, j] / np.linalg.norm(M[:, j])))) for j in range(3)]
assert turn[0] < 1e-6 and turn[1] > 0.1 and turn[2] > 0.1
orth_err_M = float(np.abs(M.T @ M - np.eye(3)).max())
dist_G = float(np.linalg.norm(G - M))

# ---------------------------------------------------------------- 算例 2.7.3
eps = 1e-8
Lc = np.array([[1, 1, 1], [eps, 0, 0], [0, eps, 0], [0, 0, eps]], float)
Qc, _ = gs(Lc)
Qm, _ = mgs(Lc)
Qh, _ = np.linalg.qr(Lc)
loss_c = float(np.abs(Qc.T @ Qc - np.eye(3)).max())
loss_m = float(np.abs(Qm.T @ Qm - np.eye(3)).max())
loss_h = float(np.abs(Qh.T @ Qh - np.eye(3)).max())
assert loss_c > 0.1 and loss_m < 1e-7 and loss_h < 1e-14

out(
    a1=vec(a1, 0), a2=vec(a2, 0), ang=ang, dot12=float(a1 @ a2), n1=float(np.linalg.norm(a1)), n2=float(np.linalg.norm(w2)),
    na2=float(np.linalg.norm(a2)),
    e1=vec(e1, 4), r12=r12, w2=vec(w2, 3), e2=vec(e2, 4), e3=vec(e3, 4), Rf=tex(Rf, 4), Rqr=tex(R, 3),
    dev_y=dev_y, dx_alt=dx_alt,
    M=tex(M, 4), G=tex(G, 4), turn2=turn[1], turn3=turn[2], orth_err_M=orth_err_M, dist_G=dist_G,
    loss_c=loss_c, loss_m=loss_m, loss_h=loss_h,
)
