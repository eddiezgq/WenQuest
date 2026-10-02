"""6.2 节的算例。

算例 6.2.1：UR5e 从零位出发，关节 1 以 30°/s、关节 6 以 90°/s 同时匀速转动。求 t = 1 s 时法兰盘的
            空间角速度 ω_s 和物体角速度 ω_b。三种算法互相核对：
            (a) 各关节角速度的矢量和（定理 3.6.2），关节 6 的轴被关节 1 带着转；
            (b) 由姿态 R(t) 数值求导：[ω_s] = Ṙ Rᵀ，[ω_b] = Rᵀ Ṙ（式 (6.2.3)、(6.2.4)）；
            (c) ω_b = Rᵀ ω_s。
算例 6.2.2：1 s 内姿态的总变化 R(1)R(0)ᵀ 的指数坐标，与角速度对时间的积分 ∫ω_s dt 比较：两者不同。
            再验证：只有一个关节转动（转轴固定）时两者相同。
另：陀螺仪积分。按 R_{k+1} = R_k e^{[ω_b]Δt}（右乘，物体角速度）逐步积分，与精确姿态比较；
    若误把 ω_b 左乘，误差不随步长减小而消失。
"""
import math

import numpy as np
from scipy.integrate import quad

from _screw import UR_AXES, UR_M, exp3, log3, skew, unskew
from bookout import out, tex, vec

d = math.radians
w1, w6 = UR_AXES[0][0], UR_AXES[5][0]           # 关节 1、6 的转轴（零位，{s} 中）
R0 = UR_M[:3, :3]
r1, r6 = d(30), d(90)                            # 关节速度 rad/s


def R(t):
    """姿态：e^{[ω1]θ1} e^{[ω6]θ6} R0（指数积公式的转动部分，第 12 章）。"""
    return exp3(w1 * r1 * t) @ exp3(w6 * r6 * t) @ R0


t = 1.0
Rt = R(t)
# (a) 角速度的矢量和
ws_a = r1 * w1 + r6 * exp3(w1 * r1 * t) @ w6
# (b) 数值求导
h = 1e-6
Rdot = (R(t + h) - R(t - h)) / (2 * h)
Ws = Rdot @ Rt.T
Wb = Rt.T @ Rdot
assert np.allclose(Ws, -Ws.T, atol=1e-8) and np.allclose(Wb, -Wb.T, atol=1e-8)   # Ṙ Rᵀ、Rᵀ Ṙ 反对称
ws_b, wb_b = unskew(Ws), unskew(Wb)
assert np.allclose(ws_a, ws_b, atol=1e-8)
# (c) ω_b = Rᵀ ω_s
wb_c = Rt.T @ ws_a
assert np.allclose(wb_c, wb_b, atol=1e-8)
assert abs(np.linalg.norm(ws_a) - np.linalg.norm(wb_c)) < 1e-12               # 大小相同
assert np.allclose(skew(wb_c), Rt.T @ skew(ws_a) @ Rt)                          # 式 (3.4.6)
# t = 0 时
ws0 = r1 * w1 + r6 * w6
wb0 = R0.T @ ws0

# ---------------------------------------------------------------- 算例 6.2.2
Dt = Rt @ R(0).T
w_log, th_log = log3(Dt)
expc = w_log * th_log
a = r1
integral = r1 * w1 + r6 * np.array([(1 - math.cos(a)) / a, -math.sin(a) / a, 0.0])  # ∫0^1 Rot(z, a t)(−ŷ) dt 的闭式
num = np.array([quad(lambda s, i=i: (r1 * w1 + r6 * exp3(w1 * r1 * s) @ w6)[i], 0, 1)[0] for i in range(3)])
assert np.allclose(integral, num, atol=1e-10)
assert np.allclose(exp3(expc), Dt)
gap = float(np.linalg.norm(expc - integral))
assert gap > 1e-2                                                               # 两者确实不同
# 只转关节 6（转轴固定）时，两者相同
D6 = exp3(w6 * r6 * 1.0)
w6log, th6 = log3(D6)
assert np.allclose(w6log * th6, r6 * w6)

# ---------------------------------------------------------------- 陀螺仪积分
def integrate(n, right=True):
    Rk, dt = R(0).copy(), 1.0 / n
    for k in range(n):
        tm = (k + 0.5) * dt
        wb = R(tm).T @ (r1 * w1 + r6 * exp3(w1 * r1 * tm) @ w6)   # 陀螺仪读数：物体角速度
        Rk = Rk @ exp3(wb * dt) if right else exp3(wb * dt) @ Rk
    return Rk


def err_deg(A, B):
    return math.degrees(math.acos(np.clip((np.trace(A.T @ B) - 1) / 2, -1, 1)))


e_r10, e_r100 = err_deg(integrate(10), Rt), err_deg(integrate(100), Rt)
e_l100 = err_deg(integrate(100, right=False), Rt)
assert e_r100 < e_r10 < 0.1 and e_l100 > 10

out(Rt=tex(Rt, 4), ws=vec(ws_a, 4), wb=vec(wb_c, 4), wnorm=float(np.linalg.norm(ws_a)), wnorm_deg=math.degrees(np.linalg.norm(ws_a)),
    ws0=vec(ws0, 4), wb0=vec(wb0, 4), Ws=tex(Ws, 4), Wb=tex(Wb, 4),
    w_log=vec(w_log, 4), th_log_deg=math.degrees(th_log), expc=vec(expc, 4), integral=vec(integral, 4), gap=gap,
    gap_deg=math.degrees(gap), e_r10=e_r10, e_r100=e_r100, e_l100=e_l100, r1=r1, r6=r6)
