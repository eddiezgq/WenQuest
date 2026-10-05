"""9.4 节：复合与矩阵乘法——[S∘T] = [S][T]。平面上先转 30° 再投影到 x 轴与先投影再转不同；平面两连杆臂的姿态 R(θ1)R(θ2) = R(θ1 + θ2)
可交换；空间中绕 x 轴、绕 z 轴各转 90°，顺序不同结果相差 120°；两个转角都很小时差别是二阶小量（约为两角之积）。"""
import numpy as np

from bookout import out, tex


def R2(t):
    return np.array([[np.cos(t), -np.sin(t)], [np.sin(t), np.cos(t)]])


def Rx(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def Rz(t):
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def angle(A, B):
    """两个转动之间相差的角度（°）：A⁻¹B 的转角，cos φ = (tr(AᵀB) − 1)/2。"""
    return float(np.degrees(np.arccos(np.clip((np.trace(A.T @ B) - 1) / 2, -1, 1))))


Rt = R2(np.radians(30))
P = np.array([[1.0, 0], [0, 0]])
out(PR=tex(P @ Rt, 4), RP=tex(Rt @ P, 4))
e = np.array([1.0, 1.0])
out(PRe=tex(P @ Rt @ e, 4), RPe=tex(Rt @ P @ e, 4))
# 复合的矩阵就是乘积：逐点验证
rng = np.random.default_rng(4)
xs = rng.normal(size=(2, 50))
out(comp_err=float(np.abs(P @ (Rt @ xs) - (P @ Rt) @ xs).max()))
# 平面两连杆：姿态角相加，可交换
t1, t2 = np.radians(40), np.radians(25)
out(planar=float(np.abs(R2(t1) @ R2(t2) - R2(t1 + t2)).max()), planar_c=float(np.abs(R2(t1) @ R2(t2) - R2(t2) @ R2(t1)).max()))
# 空间转动：顺序不同，结果不同
a = np.radians(90)
A1, A2 = Rz(a) @ Rx(a), Rx(a) @ Rz(a)        # A1：先绕 x 转，再绕 z 转（列向量左乘）
out(A1=tex(A1, 0), A2=tex(A2, 0), ang90=angle(A1, A2))
for name, deg in (("ang5", 5), ("ang1", 1)):
    b = np.radians(deg)
    out(**{name: angle(Rz(b) @ Rx(b), Rx(b) @ Rz(b))})
out(prod5=float(np.degrees(np.radians(5) ** 2)), ang180=angle(Rz(np.pi) @ Rx(np.pi), Rx(np.pi) @ Rz(np.pi)))
