"""6.5 节的算例。

先验证伴随矩阵的性质：[Ad_T]V 与 T[V]T⁻¹ 一致（式 (6.5.5)）；[Ad_T1][Ad_T2] = [Ad_T1T2]；[Ad_T]⁻¹ = [Ad_T⁻¹]；
e^{[Ad_T S]θ} = T e^{[S]θ} T⁻¹（式 (6.5.9)）；节距和转角不随坐标系改变。
算例 6.5.1：UR5e 在零位，法兰盘上装一把长 0.15 m 的工具。要求工具绕自身 x 轴以 0.5 rad/s 转动、工具尖端不动。
            求工具坐标系、法兰盘坐标系和基座坐标系中的运动旋量。核对：由 V_s 算出的工具尖端速度为零；
            由 T_st(t) = T_st e^{[V_t]t} 数值求导得到的 V_s 与伴随矩阵的结果相同。
算例 6.5.2：UR5e 六个关节的物体旋量轴 B_i = [Ad_{M⁻¹}] S_i；用 M⁻¹[S_i]M 和指数积两种形式核对；
            并解答习题 6.4.4：物体坐标系中位移的对数是空间坐标系中位移的对数的伴随变换，转角、节距相同。
"""
import math

import numpy as np

from _screw import (UR_M, UR_S, adjoint, axis_of, bracket, exp3, exp6, inv, log6, pose, rot_x, rot_z, skew, unbracket,
                    ur_fk)
from bookout import num, out, tex, vec

d = math.radians
rng = np.random.default_rng(65)


def rand_T():
    w = rng.normal(size=3)
    return pose(exp3(w), rng.normal(size=3))


# ---------------------------------------------------------------- 性质
for _ in range(20):
    T1, T2, V = rand_T(), rand_T(), rng.normal(size=6)
    assert np.allclose(adjoint(T1) @ V, unbracket(T1 @ bracket(V) @ inv(T1)))
    assert np.allclose(adjoint(T1) @ adjoint(T2), adjoint(T1 @ T2))
    assert np.allclose(np.linalg.inv(adjoint(T1)), adjoint(inv(T1)))
    S = V / np.linalg.norm(V[:3])
    th = rng.uniform(0.2, 2.5)
    assert np.allclose(exp6(adjoint(T1) @ S, th), T1 @ exp6(S, th) @ inv(T1))
    s1, q1, h1 = axis_of(S)
    s2, q2, h2 = axis_of(adjoint(T1) @ S)
    assert abs(h1 - h2) < 1e-12                                             # 节距不变
    assert np.allclose(s2, T1[:3, :3] @ s1)                                 # 轴的方向随刚体变换
    x = T1 @ np.r_[q1, 1]
    assert np.allclose(np.cross(x[:3] - q2, s2), 0, atol=1e-10)             # 轴本身被搬到新的位置

# ---------------------------------------------------------------- 算例 6.5.1
Tbt = pose(np.eye(3), np.array([0, 0.15, 0]))         # 工具沿法兰盘法线（{b} 的 y 轴）伸出 0.15 m
Tst = UR_M @ Tbt
Vt = np.array([0.5, 0, 0, 0, 0, 0])                   # 绕工具自身 x 轴转，尖端不动
Vb = adjoint(Tbt) @ Vt
Vs = adjoint(Tst) @ Vt
assert np.allclose(Vs, adjoint(UR_M) @ Vb)            # V_s = [Ad_{T_sb}] V_b
p_tip = Tst[:3, 3]
assert np.allclose(Vs[3:] + np.cross(Vs[:3], p_tip), 0)   # 工具尖端速度为零
p_fl = UR_M[:3, 3]
v_flange = Vs[3:] + np.cross(Vs[:3], p_fl)
assert np.allclose(v_flange, UR_M[:3, :3] @ Vb[3:])   # 法兰盘中心的速度 = R v_b
h = 1e-6
Td = (Tst @ exp6(Vt / 0.5, 0.5 * h) - Tst @ exp6(Vt / 0.5, -0.5 * h)) / (2 * h)
assert np.allclose(unbracket(Td @ inv(Tst)), Vs, atol=1e-8)
assert np.allclose(unbracket(inv(UR_M) @ (Td @ inv(Tbt))), Vb, atol=1e-8)

# ---------------------------------------------------------------- 算例 6.5.2
AdMi = adjoint(inv(UR_M))
B = [AdMi @ S for S in UR_S]
for S, Bi in zip(UR_S, B):
    assert np.allclose(bracket(Bi), inv(UR_M) @ bracket(S) @ UR_M)
for _ in range(5):
    th = rng.uniform(-math.pi, math.pi, 6)
    Tb = UR_M.copy()
    for Bi, t in zip(B, th):
        Tb = Tb @ exp6(Bi, t)
    assert np.allclose(Tb, ur_fk(th))
rows = r" \\ ".join(f"{i} & " + " & ".join(num(float(x), 3) for x in Bi) for i, Bi in enumerate(B, 1))
# 习题 6.4.4
theta = np.array([d(30), d(-45), d(60), d(-15), d(90), d(30)])
Tt = ur_fk(theta)
Ss, ts = log6(Tt @ inv(UR_M))
Sb, tb = log6(inv(UR_M) @ Tt)
assert abs(ts - tb) < 1e-12 and np.allclose(Sb, AdMi @ Ss)
assert abs(axis_of(Ss)[2] - axis_of(Sb)[2]) < 1e-12

out(Tbt=tex(Tbt, 2), Tst=tex(Tst, 3), Vt=vec(Vt, 1), Vb=vec(Vb, 4), Vs=vec(Vs, 4), p_tip=vec(p_tip, 3), v_flange=vec(v_flange, 4),
    AdTbt=tex(adjoint(Tbt), 2), AdM=tex(adjoint(UR_M), 3), Brows=rows, B6=vec(B[5], 3), B1=vec(B[0], 3),
    h_space=axis_of(Ss)[2], h_body=axis_of(Sb)[2], th_deg=math.degrees(ts), Sb=vec(Sb, 4))
