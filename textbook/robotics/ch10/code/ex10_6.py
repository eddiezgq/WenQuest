"""算例 10.6.1–10.6.3：旋转参考系，加速度合成定理 a_abs = a_rel + a_tr + 2Ω × v_rel。

地面坐标系 {s}（定系）；转台坐标系 {p}（动系），原点在转台中心，与转台一起绕竖直轴转动。
算例 10.6.1：转台以 Ω = 0.5 rad/s（俯视逆时针）匀速转动；AGV 从转台中心出发，沿转台上画的一条半径以 v_rel = 0.4 m/s
  匀速向外行驶。t = 2.5 s（离中心 1.0 m）时求牵连加速度、科氏加速度、绝对加速度，以及 AGV 上加速度计（x 朝前、y 朝左）的读数。
  三种办法核对：(1) 合成定理；(2) 地面坐标中数值求二阶导数；(3) 10.3 节的极坐标公式 (10.3.9)。
  并按矩阵形式 (10.6.10) 逐项计算。
算例 10.6.2：同一时刻，转台正以 Ω̇ = 0.2 rad/s² 加速，AGV 同时以 0.3 m/s² 沿半径加速，求各项与总加速度。
算例 10.6.3：地球自转：上海（北纬 31.2°）一台 AGV 以 1.0 m/s 向正北行驶，科氏加速度的水平分量。
"""
import math

import numpy as np

from _kin import d1, d2, rotz, skew
from bookout import out

Om, vr = 0.5, 0.4
t1 = 2.5
z = np.array([0, 0, 1.0])


def pos_s(t, Om0=Om, Omd=0.0, vr0=vr, ar=0.0):
    """AGV 在地面 {s} 中的位置：转台转角 ψ = Om0 t + Omd t²/2，AGV 在 {p} 中位于 (ρ, 0, 0)，ρ = vr0 t + ar t²/2。"""
    psi = Om0 * t + 0.5 * Omd * t * t
    rho = vr0 * t + 0.5 * ar * t * t
    return rotz(psi) @ np.array([rho, 0, 0])


rho1 = vr * t1
psi1 = Om * t1
R = rotz(psi1)
r_p = np.array([rho1, 0, 0])              # AGV 在 {p} 中的位置
v_rel_p = np.array([vr, 0, 0])            # 相对速度（{p} 中的分量）
a_rel_p = np.zeros(3)
Om_s = Om * z
# 合成定理（{s} 中的分量）
r_s = R @ r_p
v_rel = R @ v_rel_p
v_tr = np.cross(Om_s, r_s)
v_abs = v_tr + v_rel
a_tr = np.cross(Om_s, np.cross(Om_s, r_s))           # 转台匀速，O′ 不动：只有向心项
a_C = 2 * np.cross(Om_s, v_rel)
a_abs = R @ a_rel_p + a_tr + a_C
# (2) 数值求导
assert np.allclose(d1(pos_s, t1, 1e-5), v_abs, atol=1e-9)
assert np.allclose(d2(pos_s, t1, 1e-3), a_abs, atol=1e-6)
# (3) 极坐标公式 (10.3.9)：ρ̇ = vr，φ̇ = Ω，ρ̈ = φ̈ = 0
a_rho = 0 - rho1 * Om ** 2
a_phi = rho1 * 0 + 2 * vr * Om
er, ep = R @ np.array([1.0, 0, 0]), R @ np.array([0, 1.0, 0])
assert np.allclose(a_rho * er + a_phi * ep, a_abs, atol=1e-14)
# 矩阵形式 (10.6.10)：r̈_s = p̈ + ([Ω̇] + [Ω]²) R r_p + 2[Ω] R ṙ_p + R r̈_p
A = skew(Om_s) @ skew(Om_s) @ R @ r_p + 2 * skew(Om_s) @ R @ v_rel_p + R @ a_rel_p
assert np.allclose(A, a_abs, atol=1e-15)
# 加速度计读数：AGV 车体 {b} 的 x 沿半径向外（与 e_ρ 同向），y 向左（与 e_φ 同向）；水平面内比力 = 加速度
imu = np.array([a_abs @ er, a_abs @ ep])

# ---------------------------------------------------------------- 算例 10.6.2
Omd, ar = 0.2, 0.3
# t1 时刻的状态与算例 10.6.1 相同（ψ1、Ω、ρ1 = 1.0 m、v_rel = 0.4 m/s），此刻 Ω̇ = 0.2 rad/s²、AGV 沿半径加速 0.3 m/s²


def f2(t):
    tau = t - t1
    psi = psi1 + Om * tau + 0.5 * Omd * tau * tau
    rho = rho1 + vr * tau + 0.5 * ar * tau * tau
    return rotz(psi) @ np.array([rho, 0, 0])


R2 = R
r2 = r_s
a_euler = np.cross(Omd * z, r2)
a_cent2 = np.cross(Om_s, np.cross(Om_s, r2))
a_C2 = 2 * np.cross(Om_s, R2 @ np.array([vr, 0, 0]))
a_rel2 = R2 @ np.array([ar, 0, 0])
a_abs2 = a_rel2 + a_euler + a_cent2 + a_C2
assert np.allclose(d2(f2, t1, 1e-3), a_abs2, atol=1e-6)
er2, ep2 = R2 @ np.array([1.0, 0, 0]), R2 @ np.array([0, 1.0, 0])
imu2 = np.array([a_abs2 @ er2, a_abs2 @ ep2])

# ---------------------------------------------------------------- 算例 10.6.3
w_E = 2 * math.pi / 86164.0905             # 地球相对恒星的自转角速度，rad/s（恒星日 86164.0905 s）
lat = math.radians(31.2)
v_n = 1.0
aC_h = 2 * w_E * v_n * math.sin(lat)       # 水平分量（指向东）
aC_v = 2 * w_E * v_n * 0.0                 # 向北运动时竖直分量为 0
# 当地坐标 (东, 北, 天) 中：Ω = ω_E (0, cos λ, sin λ)，v = (0, 1, 0)
Om_E = w_E * np.array([0, math.cos(lat), math.sin(lat)])
aC_vec = -2 * np.cross(Om_E, np.array([0, v_n, 0]))  # 不受横向力时看到的偏转 = −a_C（见 10.6.8 节）
assert abs(abs(aC_vec[0]) - aC_h) < 1e-18 and abs(aC_vec[2]) < 1e-18

out(Om=Om, vr=vr, t1=t1, rho1=rho1, psi1_deg=math.degrees(psi1),
    v_tr=float(np.linalg.norm(v_tr)), v_abs=float(np.linalg.norm(v_abs)),
    a_tr=float(np.linalg.norm(a_tr)), a_C=float(np.linalg.norm(a_C)), a_abs=float(np.linalg.norm(a_abs)),
    a_ang=math.degrees(math.atan2(imu[1], -imu[0])),
    imu_x=imu[0], imu_y=imu[1],
    Omd=Omd, ar=ar, a_euler=float(np.linalg.norm(a_euler)), imu2_x=imu2[0], imu2_y=imu2[1],
    a_abs2=float(np.linalg.norm(a_abs2)),
    w_E=w_E, lat_deg=31.2, aC_h=aC_h, aC_h_g=aC_h / 9.81, aC_h_um=aC_h * 1e6)
