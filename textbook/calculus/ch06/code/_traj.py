"""本章 6.5、6.6 节共用的轨迹：两节连杆 1 s 内关节角线性插值，末端扫过一个点状障碍附近。以下划线开头，构建时不单独运行。"""
import math

from _arm import L1, L2

A = (math.radians(10), math.radians(100))      # 起点关节角 (θ₁, θ₂)
B = (math.radians(80), math.radians(20))       # 终点
OBS = (0.36, 0.62)                             # 障碍点 / m
W1, W2 = B[0] - A[0], B[1] - A[1]              # 关节角速度 / (rad/s)，T = 1 s
K = (L1 + L2) * abs(W1) + L2 * abs(W2)         # 末端速度的上界 / (m/s)，即 d(t) 的利普希茨常数


def ee(t):
    t1, t2 = A[0] + W1 * t, A[1] + W2 * t
    return L1 * math.cos(t1) + L2 * math.cos(t1 + t2), L1 * math.sin(t1) + L2 * math.sin(t1 + t2)


def clearance(t, obs=OBS):
    x, y = ee(t)
    return math.hypot(x - obs[0], y - obs[1])
