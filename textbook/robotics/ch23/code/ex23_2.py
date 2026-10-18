"""23.2 节的计算：平行轴定理。

(1) 第 7 章的细杆：J_o = mL²/3 由平行轴定理得到，并与按定义直接求和核对。
(2) 算例 23.2.1：UR5e 大臂（upper_arm_link）对关节 2 轴的转动惯量。MJCF 给出的是对质心的主惯量和质心位置；
    用张量形式的平行轴定理 (23.2.3) 换到连杆坐标系原点，读出绕关节轴（连杆坐标系的 y 轴）的分量。
    MuJoCo 核对：只有这一个连杆、绕同一根轴转动的模型，其关节空间质量矩阵（减去电机转子惯量 armature）就是它。
    与“均匀细杆”估计 m L₁²/3 比较；与模型里电机转子的等效惯量 0.1 kg·m² 比较。
(3) 算例 23.2.2：夹爪 + 毛坯组合体（算例 23.1.1）对总质心、对法兰中心的惯量张量。MuJoCo 核对：同一个物体里放两个几何体，
    MuJoCo 自己合成的质量、质心和主惯量。
(4) 算例 23.2.3：复摆。UR5e 小臂（forearm_link）刹车松开后绕关节 3 轴的小幅摆动周期（式 (23.2.6)），
    与 MuJoCo 的仿真比较；10° 振幅的修正（完全椭圆积分）；米尺挂在不同位置的周期，周期最短的悬挂点 d = k（定理 23.2.3）。
(5) 习题答案。
"""
import math

import numpy as np
from scipy.special import ellipk

from _ch23 import (G0, GRIP_BOX, GRIP_C, GRIP_M, box_inertia, cyl_inertia, mj_load, mjcf_text, parse_links, sh301_blank,
                   sign_changes, steiner)
from bookout import out, tex

# ---------------------------------------------------------------- (1) 细杆（第 7 章，m = 2 kg，L = 0.5 m）
m_rod, L_rod = 2.0, 0.5
J_par = m_rod * L_rod ** 2 / 12 + m_rod * (L_rod / 2) ** 2
x = (np.arange(200000) + 0.5) / 200000 * L_rod
J_sum = float(np.sum(m_rod / 200000 * x ** 2))
assert abs(J_par - m_rod * L_rod ** 2 / 3) < 1e-15 and abs(J_sum / J_par - 1) < 1e-9

# ---------------------------------------------------------------- (2) 算例 23.2.1：大臂对关节 2 轴
links = {L.name: L for L in parse_links(mjcf_text())}
ua = links["upper_arm_link"]
Io = ua.I_link_o                                                    # 对连杆坐标系原点（关节 2 轴上）的惯量
J2 = float(Io[1, 1])                                                # 关节轴是连杆坐标系的 y 轴（MJCF 的默认 axis="0 1 0"）
assert np.allclose(ua.axis, [0, 1, 0])
J2_hand = ua.diag[1] + ua.m * ua.ipos[2] ** 2                        # 标量形式 (23.2.1)
assert abs(J2 - J2_hand) < 1e-15
J2_rod = ua.m * 0.425 ** 2 / 3
xml = (f'<mujoco><worldbody><body><joint type="hinge" axis="0 1 0" armature="0.1"/>'
       f'<inertial mass="{ua.m}" pos="{ua.ipos[0]} {ua.ipos[1]} {ua.ipos[2]}" diaginertia="{ua.diag[0]} {ua.diag[1]} {ua.diag[2]}"/>'
       f'</body></worldbody></mujoco>')
mj, mm, dd = mj_load(xml)
mj.mj_forward(mm, dd)
Mq = np.zeros((1, 1))
mj.mj_fullM(mm, dd, Mq)
J2_mj = float(Mq[0, 0] - 0.1)
assert abs(J2_mj - J2) < 1e-12

# ---------------------------------------------------------------- (3) 算例 23.2.2：夹爪 + 毛坯
m_b, r_b, L_b = sh301_blank()
gx, gz, gy = GRIP_BOX                                               # 夹爪：沿 x、z、工具方向 y 的尺寸
I_g = box_inertia(GRIP_M, gx, gy, gz)                               # 三条棱沿 x、y、z
c_g = np.array([0, GRIP_C, 0])
I_bl = np.diag([cyl_inertia(m_b, r_b, L_b)[0, 0], cyl_inertia(m_b, r_b, L_b)[2, 2], cyl_inertia(m_b, r_b, L_b)[0, 0]])   # 轴线沿 y
y_blank = 0.15 - 0.04 + L_b / 2
c_bl = np.array([0, y_blank, 0])
m_p = GRIP_M + m_b
c_p = (GRIP_M * c_g + m_b * c_bl) / m_p
I_flange = steiner(I_g, GRIP_M, c_g) + steiner(I_bl, m_b, c_bl)       # 对法兰中心（{b} 的原点）
I_pc = steiner(I_g, GRIP_M, c_g - c_p) + steiner(I_bl, m_b, c_bl - c_p)   # 对组合体的质心
assert np.allclose(steiner(I_pc, m_p, c_p), I_flange, atol=1e-15)    # 两步走与一步走一致：先到质心，再到法兰
xml = (f'<mujoco><worldbody><body><freejoint/>'
       f'<geom type="box" pos="0 {GRIP_C} 0" size="{gx / 2} {gy / 2} {gz / 2}" mass="{GRIP_M}"/>'
       f'<geom type="cylinder" pos="0 {y_blank} 0" quat="0.7071067811865476 0.7071067811865476 0 0" size="{r_b} {L_b / 2}" mass="{m_b}"/>'
       f'</body></worldbody></mujoco>')
mj, mm, dd = mj_load(xml)
assert abs(mm.body_mass[1] - m_p) < 1e-12 and np.allclose(mm.body_ipos[1], c_p, atol=1e-12)
assert np.allclose(np.sort(mm.body_inertia[1]), np.sort(np.linalg.eigvalsh(I_pc)), rtol=1e-10, atol=0)
k_p = math.sqrt(I_pc[0, 0] / m_p)

# ---------------------------------------------------------------- (4) 算例 23.2.3：复摆
fa = links["forearm_link"]
d_fa = float(fa.ipos[2])
Jo_fa = float(fa.diag[0] + fa.m * d_fa ** 2)
T_fa = 2 * math.pi * math.sqrt(Jo_fa / (fa.m * G0 * d_fa))
J_rod_fa = fa.m * 0.392 ** 2 / 3


def pendulum_period(m, Ic, d, amp_deg, T=8.0, dt=0.0005):
    """MuJoCo：绕水平轴 y 自由摆动的刚体，质心在轴下方 d 处；由角速度相邻两次变号的间隔求周期。"""
    xml = (f'<mujoco><option timestep="{dt}" integrator="RK4" gravity="0 0 -{G0}"/><worldbody>'
           f'<body pos="0 0 1"><joint type="hinge" axis="0 1 0"/><inertial pos="0 0 {-d}" mass="{m}" diaginertia="{Ic} {Ic} {Ic}"/>'
           f'</body></worldbody></mujoco>')
    mj, mm, dd = mj_load(xml)
    dd.qpos[0] = math.radians(amp_deg)
    t, wv = [], []
    for _ in range(int(T / dt)):
        mj.mj_step(mm, dd)
        t.append(dd.time)
        wv.append(dd.qvel[0])
    sc = sign_changes(np.array(t), np.array(wv))
    return float(2 * np.mean(np.diff(sc)))


T_fa_mj2 = pendulum_period(fa.m, fa.diag[0], d_fa, 2.0)
T_fa_mj10 = pendulum_period(fa.m, fa.diag[0], d_fa, 10.0)
corr10 = 2 / math.pi * ellipk(math.sin(math.radians(10) / 2) ** 2)    # T(θ₀)/T₀ = (2/π) K(sin²(θ₀/2))
assert abs(T_fa_mj10 / T_fa - corr10) < 1e-5
corr2 = 2 / math.pi * ellipk(math.sin(math.radians(2) / 2) ** 2)
assert abs(T_fa_mj2 / T_fa - corr2) < 1e-5

# 米尺：长 1 m，均匀；挂在离质心 d 处
Ls = 1.0
k_s = Ls / math.sqrt(12)
dd_ = np.linspace(0.02, 0.5, 4801)
Ts = 2 * math.pi * np.sqrt((k_s ** 2 + dd_ ** 2) / (G0 * dd_))
d_best = float(dd_[np.argmin(Ts)])
assert abs(d_best - k_s) < 2e-4
T_min = 2 * math.pi * math.sqrt(2 * k_s / G0)
T_end = 2 * math.pi * math.sqrt(2 * Ls / (3 * G0))
T_mid20 = 2 * math.pi * math.sqrt((k_s ** 2 + 0.2 ** 2) / (G0 * 0.2))
d_conj = k_s ** 2 / 0.2                                             # 与 d = 0.2 m 周期相同的另一个悬挂点（仍在尺上：< 0.5 m）
assert abs(2 * math.pi * math.sqrt((k_s ** 2 + d_conj ** 2) / (G0 * d_conj)) - T_mid20) < 1e-12 and d_conj < Ls / 2
L_eq = 0.2 + d_conj                                                 # 等值摆长

# ---------------------------------------------------------------- 实验 23.2 的阈值（lab23_2.js 的同一个模型：显式 <inertial>）
T_stick5 = pendulum_period(0.15, 0.15 / 12, 0.5, 5.0)
assert abs(T_stick5 / T_end - 1) < 0.005                              # 任务 1：5° 时比小幅公式只长约 0.05%
T_stick29 = pendulum_period(0.15, 0.15 / 12, 0.29, 5.0)
T29 = 2 * math.pi * math.sqrt((k_s ** 2 + 0.29 ** 2) / (G0 * 0.29))
assert abs(T_stick29 / T29 - 1) < 0.005                               # 任务 2
T_fa5 = pendulum_period(fa.m, fa.diag[0], d_fa, 5.0)
assert abs(T_fa5 / T_fa - 1) < 0.005                                  # 任务 3
# ---------------------------------------------------------------- (5) 习题答案
# 23.2.2：毛坯对过一端、垂直于轴线的轴
I_end = cyl_inertia(m_b, r_b, L_b)[0, 0] + m_b * (L_b / 2) ** 2
# 23.2.4：0.30 × 0.20 × 0.01 m 钢板，离中心 (0.08, 0.05) m 处钻 Ø40 mm 通孔，对原中心、绕法线
rho = 7850.0
m_pl = rho * 0.30 * 0.20 * 0.01
m_h = rho * math.pi * 0.02 ** 2 * 0.01
I_hole_plate = m_pl * (0.30 ** 2 + 0.20 ** 2) / 12 - (0.5 * m_h * 0.02 ** 2 + m_h * (0.08 ** 2 + 0.05 ** 2))
# 23.2.6：小臂末端（关节 4 处，距关节 3 轴 0.392 m）加 1 kg 的质点负载
Jo_load = Jo_fa + 1.0 * 0.392 ** 2
d_load = (fa.m * d_fa + 1.0 * 0.392) / (fa.m + 1.0)
T_load = 2 * math.pi * math.sqrt(Jo_load / ((fa.m + 1.0) * G0 * d_load))
T_load5 = pendulum_period(fa.m + 1.0, Jo_load - (fa.m + 1.0) * d_load ** 2, d_load, 5.0)
assert abs(T_load5 / T_load - 1) < 0.005                              # 实验 23.2 任务 4

out(J_par=J_par, J_sum=J_sum,
    ua_m=ua.m, ua_c=ua.ipos[2], ua_Iy=ua.diag[1], ua_Ia=ua.diag[2], Io=tex(Io, 5), J2=J2, J2_rod=J2_rod, J2_mj=J2_mj, J2_err=abs(J2_rod / J2 - 1) * 100,
    arm_ratio=0.1 / J2 * 100,
    I_g=tex(I_g * 1e3, 4), I_bl=tex(I_bl * 1e3, 4), m_p=m_p, c_p=c_p[1], y_blank=y_blank,
    I_flange=tex(I_flange * 1e3, 4), I_pc=tex(I_pc * 1e3, 4), I_pc_mj=tex(np.sort(mm.body_inertia[1]) * 1e3, 4), k_p=k_p,
    fa_m=fa.m, d_fa=d_fa, fa_I=fa.diag[0], Jo_fa=Jo_fa, J_rod_fa=J_rod_fa, T_fa=T_fa, T_fa_mj2=T_fa_mj2, T_fa_mj10=T_fa_mj10,
    corr10=(corr10 - 1) * 100, k_s=k_s, T_min=T_min, T_end=T_end, T_mid20=T_mid20, d_conj=d_conj, L_eq=L_eq,
    I_end=I_end, T_load=T_load, d_load=d_load, I_hole_plate=I_hole_plate)
