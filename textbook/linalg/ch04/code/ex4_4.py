"""4.4 节：分块矩阵——按块相乘的规则；二维齐次变换 T = [R t; 0 1]：车间 → AGV → 机械臂基座 → 末端，连乘得到末端在车间中的位置。"""
import math

import numpy as np

from bookout import out, tex, vec


def T2(theta_deg, tx, ty):
    t = math.radians(theta_deg)
    return np.array([[math.cos(t), -math.sin(t), tx], [math.sin(t), math.cos(t), ty], [0.0, 0.0, 1.0]])


# AGV 在车间中：转 30°，位于 (5, 3) m；机械臂基座在 AGV 前方 0.2 m 处，相对 AGV 转 90°；
# 末端在机械臂基座坐标系中位于 (0.6, 0.1) m
T_WA = T2(30, 5.0, 3.0)
T_AB = T2(90, 0.2, 0.0)
p_B = np.array([0.6, 0.1, 1.0])
T_WB = T_WA @ T_AB
p_W = T_WB @ p_B
out(T_WA=tex(T_WA, 4), T_AB=tex(T_AB, 4), T_WB=tex(T_WB, 4), p_W=vec(p_W[:2], 4))
# 分块验证：T_WB 的旋转块 = R_WA R_AB，平移块 = R_WA t_AB + t_WA
R1, t1, R2, t2 = T_WA[:2, :2], T_WA[:2, 2], T_AB[:2, :2], T_AB[:2, 2]
out(blockR=bool(np.allclose(T_WB[:2, :2], R1 @ R2)), blockt=bool(np.allclose(T_WB[:2, 2], R1 @ t2 + t1)), t_WB=vec(R1 @ t2 + t1, 4))
# 一般的 2×2 分块乘法检验：4×4 矩阵分成四个 2×2 块
rng = np.random.default_rng(44)
A, B = rng.integers(-3, 4, (4, 4)).astype(float), rng.integers(-3, 4, (4, 4)).astype(float)
A11, A12, A21, A22 = A[:2, :2], A[:2, 2:], A[2:, :2], A[2:, 2:]
B11, B12, B21, B22 = B[:2, :2], B[:2, 2:], B[2:, :2], B[2:, 2:]
Cb = np.block([[A11 @ B11 + A12 @ B21, A11 @ B12 + A12 @ B22], [A21 @ B11 + A22 @ B21, A21 @ B12 + A22 @ B22]])
out(block_ok=bool(np.allclose(Cb, A @ B)), A=tex(A, 0), B=tex(B, 0), AB=tex(A @ B, 0))
# 块对角矩阵：两个独立的 AGV 各自的运动学矩阵拼在一起
r, b = 0.075, 0.40
K = np.array([[r / 2, r / 2], [-r / b, r / b]])
KK = np.block([[K, np.zeros((2, 2))], [np.zeros((2, 2)), K]])
out(KK=tex(KK, 4), KKw=vec(KK @ np.array([4.0, 4.0, -2.0, 2.0]), 4))
