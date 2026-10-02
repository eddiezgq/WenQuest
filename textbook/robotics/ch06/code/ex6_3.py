"""6.3 节的算例。

算例 6.3.1：UR5e 在零位，只有关节 2 以 30°/s 转动。求法兰盘的空间运动旋量 V_s 和物体运动旋量 V_b，以及法兰盘中心的速度。
            两种算法：由旋量轴 V_s = S₂θ̇₂ 和式 (6.3.9)；由位姿 T(t) 数值求导 Ṫ T⁻¹、T⁻¹ Ṫ（式 (6.3.4)、(6.3.7)）。
            法兰盘中心的速度再与第 3 章算例 3.6.2 的 ω × r 比较。
算例 6.3.2：零位时关节 1、3 同时以 30°/s 转动。求空间运动旋量和它的瞬时螺旋轴：方向、轴上一点 q、节距 h（式 (6.3.11)、(6.3.12)）。
            核对：轴上各点的速度都与 ω 平行，大小为 h|ω|；由数值求导得到的运动旋量与旋量轴之和相同；
            距离轴越远的点速度越大，速度在垂直于轴方向的分量与该点到轴的距离成正比。
"""
import math

import numpy as np

from _screw import UR_M, UR_S, axis_of, bracket, exp6, inv, screw_from_axis, skew, unbracket
from bookout import out, tex, vec

d = math.radians


def fk(th):
    T = np.eye(4)
    for S, t in zip(UR_S, th):
        T = T @ exp6(S, t)
    return T @ UR_M


def num_twists(theta_of_t, t=0.0, h=1e-6):
    T = fk(theta_of_t(t))
    Td = (fk(theta_of_t(t + h)) - fk(theta_of_t(t - h))) / (2 * h)
    return T, unbracket(Td @ inv(T)), unbracket(inv(T) @ Td)


# ---------------------------------------------------------------- 算例 6.3.1
rate2 = d(30)
S2 = UR_S[1]
Vs = S2 * rate2
T0, Vs_num, Vb_num = num_twists(lambda t: [0, rate2 * t, 0, 0, 0, 0])
assert np.allclose(Vs, Vs_num, atol=1e-8)
R, p = T0[:3, :3], T0[:3, 3]
w_s, v_s = Vs[:3], Vs[3:]
Vb = np.r_[R.T @ w_s, R.T @ (v_s + np.cross(w_s, p))]       # 式 (6.3.9) 反解：ω_b = Rᵀω_s，v_b = Rᵀṗ，ṗ = v_s + ω_s × p
assert np.allclose(Vb, Vb_num, atol=1e-8)
pdot = v_s + np.cross(w_s, p)                                # 法兰盘中心（{b} 原点）的速度
q2 = np.array([0, -0.138, 0.163])
assert np.allclose(pdot, np.cross(w_s, p - q2))             # 与第 3 章 ω × r 相同
assert np.allclose(R @ Vb[3:], pdot)

# ---------------------------------------------------------------- 算例 6.3.2
r1 = r3 = d(30)
V = UR_S[0] * r1 + UR_S[2] * r3
_, V_num, _ = num_twists(lambda t: [r1 * t, 0, r3 * t, 0, 0, 0])
assert np.allclose(V, V_num, atol=1e-8)
w, v = V[:3], V[3:]
wn = float(np.linalg.norm(w))
s_hat, q, hp = axis_of(V)
assert np.allclose(screw_from_axis(q, s_hat, hp) * wn, V)
# 轴上的点：速度 = v + ω × x，应与 ω 平行，大小 h|ω|
for lam in (-0.5, 0.0, 0.7):
    x = q + lam * s_hat
    vx = v + np.cross(w, x)
    assert np.allclose(np.cross(vx, w), 0, atol=1e-12) and abs(vx @ s_hat - hp * wn) < 1e-12
# 离轴 r 处的点：垂直于轴的速度分量 = |ω| r
e = np.cross(s_hat, [1.0, 0, 0])
e /= np.linalg.norm(e)
for r in (0.1, 0.3):
    x = q + r * e
    vx = v + np.cross(w, x)
    assert abs(np.linalg.norm(vx - (vx @ s_hat) * s_hat) - wn * r) < 1e-12
# 换一种方法求轴：在所有点中找速度最小的点（最小二乘）——速度 v + ω × x 最小的点都在螺旋轴上
A = skew(w)
x_ls = np.linalg.lstsq(A, -v, rcond=None)[0]                # 使 |v + ω × x| 最小的、离原点最近的点
assert np.allclose(x_ls, q, atol=1e-12)
# 节距与两轴的距离：h = θ̇1θ̇3 L1 /(θ̇1² + θ̇3²)
L1 = 0.425
assert abs(hp - r1 * r3 * L1 / (r1 ** 2 + r3 ** 2)) < 1e-12
vmin = hp * wn
# 转速相等时，螺旋轴经过两轴公垂线的中点 (−L1/2, 0, H1)
mid = np.array([-L1 / 2, 0.0, 0.163])
assert np.allclose(np.cross(mid - q, s_hat), 0, atol=1e-12)

out(Vs=vec(Vs, 4), Vb=vec(Vb, 4), pdot=vec(pdot, 4), pdot_len=float(np.linalg.norm(pdot)), p=vec(p, 3), rate2=rate2,
    S2=vec(S2, 3), S1=vec(UR_S[0], 3), S3=vec(UR_S[2], 3), V=vec(V, 4), s_hat=vec(s_hat, 4), q=vec(q, 4), h=hp, wn=wn,
    vmin=vmin, wv=float(w @ v), vsx=float(Vs[3]), mid=vec(mid, 4), Tdot=tex(bracket(Vs) @ T0, 4), M=tex(UR_M, 3))
