"""9.6 节：基变换与相似矩阵。新基 b1 = (1, 1)、b2 = (−1, 1)：坐标 [v]_B = P⁻¹v；A = [[2, 1], [1, 2]] 在新基下的矩阵 P⁻¹AP = diag(3, 1)。
相似矩阵的迹、行列式、秩相同。机器人：转台绕基座 z 轴转 30°，在倒装相机的坐标系中看，是绕另一根轴转同样的 30°。"""
import numpy as np

from bookout import out, tex, vec

P = np.array([[1.0, -1], [1, 1]])
v = np.array([3.0, 5.0])
cv = np.linalg.solve(P, v)
A = np.array([[2.0, 1], [1, 2]])
B = np.linalg.solve(P, A @ P)
out(P=tex(P, 0), v=vec(v, 0), cv=vec(cv, 0), Pinv=tex(np.linalg.inv(P), 1), A=tex(A, 0), B=tex(B, 0),
    Av=vec(A @ v, 0), Bcv=vec(B @ cv, 0), PBcv=vec(P @ B @ cv, 0))
# 换一组不“好”的基：矩阵变了，迹、行列式、秩不变
Q = np.array([[1.0, 2], [0, 1]])
C = np.linalg.solve(Q, A @ Q)
out(C=tex(C, 0), trA=float(np.trace(A)), trC=float(np.trace(C)), detA=float(np.linalg.det(A)), detC=float(np.linalg.det(C)))
# 相机坐标系 {c} 相对基座 {b}：相机朝下倒装，R_bc = Rz(90°) Rx(180°)；转台绕基座 z 轴转 30°
def Rx(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Rz(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


Rbc = Rz(np.pi / 2) @ Rx(np.pi)
M = Rz(np.radians(30))
Mc = Rbc.T @ M @ Rbc
axis = Rbc.T @ np.array([0.0, 0, 1])
ang = np.degrees(np.arccos((np.trace(Mc) - 1) / 2))
# 由 Mc 读出转轴：反对称部分
k = np.array([Mc[2, 1] - Mc[1, 2], Mc[0, 2] - Mc[2, 0], Mc[1, 0] - Mc[0, 1]])
out(Rbc=tex(Rbc, 0), Mc=tex(Mc, 4), angc=float(ang), axis=vec(axis, 0), axis_read=vec(k / np.linalg.norm(k), 0),
    trM=float(np.trace(M)), trMc=float(np.trace(Mc)))
