"""22.1 节的计算：点到点运动的三次、五次多项式。

(1) 归一化的时间标度：直线 s = τ、三次 s = 3τ² − 2τ³、五次 s = 10τ³ − 15τ⁴ + 6τ⁵ 的速度、加速度、加加速度峰值
    （数值求最大值，与式 (22.1.6)、(22.1.11) 核对）；用一般的边界条件解线性方程组，与闭式核对。
(2) 最优性的数值核对：在满足同样边界条件的曲线中加入扰动，三次的 ∫s̈² 与五次的 ∫s⃛² 都只增不减。
(3) 算例 22.1.1：UR5e 上下料工位（示意值），TCP 从料架上方 A 到卡盘前 B 的关节空间点到点运动。
    关节速度上限 180°/s，加速度上限（设）6、6、6、12、12、12 rad/s²，加加速度上限（设）60、60、60、120、120、120 rad/s³。
    三次、五次多项式各自的最短时间（定理 22.1.3），哪个关节、哪个限制起作用；直线插值在起止时刻的速度跳变。
(4) 算例 22.1.2：关节空间的直线在笛卡尔空间是曲线：TCP 偏离 A、B 连线的最大距离；三次与五次的路径相同。
    TCP 位置用两种方法计算（指数积与零件库三维模型的节点矩阵），互相核对。
"""
import math

import numpy as np

from _traj import (AMAX, JMAX, TBT, VMAX, cell_joints, poly_coeffs, poly_eval, s_cubic, s_quintic, t_min_poly, tcp_fk,
                   ur_labels, ur_model)
from bookout import T as TT
from bookout import out, tex

deg = np.degrees

# ---------------------------------------------------------------- (1) 归一化的时间标度
tau = np.linspace(0, 1, 200001)
pk_c = [np.abs(s_cubic(tau, r)).max() for r in (1, 2)]
pk_q = [np.abs(s_quintic(tau, r)).max() for r in (1, 2, 3)]
assert abs(pk_c[0] - 1.5) < 1e-9 and abs(pk_c[1] - 6) < 1e-9
assert abs(pk_q[0] - 15 / 8) < 1e-9 and abs(pk_q[1] - 10 / math.sqrt(3)) < 1e-6 and abs(pk_q[2] - 60) < 1e-9
tau_amax_q = float(tau[np.argmax(s_quintic(tau, 2))])
assert abs(tau_amax_q - (0.5 - math.sqrt(3) / 6)) < 1e-5
# 一般边界条件的线性方程组与闭式一致
c3 = poly_coeffs(1.0, 0.0, 1.0)
c5 = poly_coeffs(1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0)
assert np.allclose(c3, [0, 0, 3, -2]) and np.allclose(c5, [0, 0, 0, 10, -15, 6])
# 非零端点速度的三次（埃尔米特）：闭式 (22.1.4)
Tg, q0g, q1g, v0g, v1g = 2.0, 0.3, 1.1, 0.4, -0.2
cg = poly_coeffs(Tg, q0g, q1g, v0g, v1g)
c2 = (3 * (q1g - q0g) - (2 * v0g + v1g) * Tg) / Tg ** 2
c3_ = (-2 * (q1g - q0g) + (v0g + v1g) * Tg) / Tg ** 3
assert np.allclose(cg, [q0g, v0g, c2, c3_])

# ---------------------------------------------------------------- (2) 最优性的数值核对
dtau = tau[1] - tau[0]


def integ(f):
    return float(np.sum((f[1:] ** 2 + f[:-1] ** 2) / 2) * dtau)


J_c = integ(s_cubic(tau, 2))                       # ∫ s̈² dτ = 12
J_q = integ(s_quintic(tau, 3))                     # ∫ s⃛² dτ = 720
assert abs(J_c - 12) < 1e-6 and abs(J_q - 720) < 1e-4
rng = np.random.default_rng(22)
worse_c = worse_q = 0
for _ in range(200):
    a = rng.normal(size=3)
    # 扰动 τ²(1−τ)² P(τ) 不改变 s(0)、s(1)、ṡ(0)、ṡ(1)；τ³(1−τ)³ P(τ) 还不改变两端的 s̈
    P = a[0] + a[1] * tau + a[2] * tau ** 2
    e2 = tau ** 2 * (1 - tau) ** 2 * P
    e3 = tau ** 3 * (1 - tau) ** 3 * P
    d2e2 = np.gradient(np.gradient(e2, dtau), dtau)
    d3e3 = np.gradient(np.gradient(np.gradient(e3, dtau), dtau), dtau)
    worse_c += integ(s_cubic(tau, 2) + d2e2[:]) > J_c
    worse_q += integ(s_quintic(tau, 3) + d3e3) > J_q
assert worse_c == 200 and worse_q == 200

# ---------------------------------------------------------------- (3) 算例 22.1.1
thR, thA, thB, thC = cell_joints()
dq = thB - thA
T3, T3j = t_min_poly(dq, VMAX, AMAX, "cubic")
T5, T5j = t_min_poly(dq, VMAX, AMAX, "quintic", JMAX)
k3 = int(np.argmax(T3j))
k5 = int(np.argmax(T5j))
assert k3 == 0 and k5 == 0                         # 关节 1 转得最多，又只能用 6 rad/s²
# 起作用的是加速度限制：按速度只需 1.5 Δ/v
Tv3 = 1.5 * abs(dq[0]) / VMAX[0]
Ta3 = math.sqrt(6 * abs(dq[0]) / AMAX[0])
assert abs(T3 - Ta3) < 1e-12 and Ta3 > Tv3
Tv5 = 15 / 8 * abs(dq[0]) / VMAX[0]
Ta5 = math.sqrt(10 / math.sqrt(3) * abs(dq[0]) / AMAX[0])
Tj5 = (60 * abs(dq[0]) / JMAX[0]) ** (1 / 3)
assert abs(T5 - Ta5) < 1e-12 and Ta5 > Tv5 and Ta5 > Tj5
# 两种轨迹的峰值（关节 1），逐点计算核对
t3 = np.linspace(0, T3, 20001)
t5 = np.linspace(0, T5, 20001)
v3 = dq[0] * s_cubic(t3 / T3, 1) / T3
a3 = dq[0] * s_cubic(t3 / T3, 2) / T3 ** 2
v5 = dq[0] * s_quintic(t5 / T5, 1) / T5
a5 = dq[0] * s_quintic(t5 / T5, 2) / T5 ** 2
j5 = dq[0] * s_quintic(t5 / T5, 3) / T5 ** 3
assert abs(np.abs(a3).max() - AMAX[0]) < 1e-9 and abs(np.abs(a5).max() - AMAX[0]) < 1e-6
assert np.all(np.abs(dq[:, None] * s_quintic(t5 / T5, 1)[None, :] / T5) <= VMAX[:, None] + 1e-12)
# 直线插值：同样时间 T3，起止时刻关节 1 的速度从 0 跳到 Δ/T
v_lin = dq[0] / T3

# ---------------------------------------------------------------- (4) 算例 22.1.2：TCP 走过的路径
M = ur_model()
ss = np.linspace(0, 1, 2001)
P = np.array([tcp_fk(thA + s * dq)[:3, 3] for s in ss])
pA, pB = P[0], P[-1]
u = (pB - pA) / np.linalg.norm(pB - pA)
dev = np.linalg.norm((P - pA) - np.outer((P - pA) @ u, u), axis=1)
k_dev = int(np.argmax(dev))
# 两种算法核对 TCP 位置：指数积 vs 零件库模型的节点矩阵
for s in (0.0, 0.3, 0.7, 1.0):
    th = thA + s * dq
    assert np.allclose(tcp_fk(th), M.fk(th) @ np.linalg.inv(np.eye(4)) @ TBT, atol=1e-9)
L_tcp = float(np.sum(np.linalg.norm(np.diff(P, axis=0), axis=1)))
chord = float(np.linalg.norm(pB - pA))
assert ur_labels(thA) == ur_labels(thB) == ("A", "up", False)

out(pk_c1=pk_c[0], pk_c2=pk_c[1], pk_q1=pk_q[0], pk_q2=pk_q[1], pk_q3=pk_q[2], tau_aq=tau_amax_q,
    J_c=J_c, J_q=J_q,
    thA=tex(deg(thA).reshape(1, -1), 2), thB=tex(deg(thB).reshape(1, -1), 2), dq=tex(deg(dq).reshape(1, -1), 2),
    dq1=deg(dq[0]), dq1r=dq[0], dq4=deg(dq[3]),
    T3=T3, T5=T5, Tv3=Tv3, Ta3=Ta3, Tv5=Tv5, Ta5=Ta5, Tj5=Tj5,
    v3max=np.abs(v3).max(), v5max=np.abs(v5).max(), v3max_deg=deg(np.abs(v3).max()), v5max_deg=deg(np.abs(v5).max()),
    j5max=np.abs(j5).max(), j5_0=abs(j5[0]), v_lin=v_lin, v_lin_deg=deg(v_lin),
    pA=tex(pA, 3), pB=tex(pB, 3), chord=chord, L_tcp=L_tcp, dev_mm=dev.max() * 1000, s_dev=ss[k_dev],
    joint_names=TT("关节 1", "joint 1"))
