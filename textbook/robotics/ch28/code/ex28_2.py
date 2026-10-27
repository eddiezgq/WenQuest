"""28.2 节的计算：线性倒立摆与零力矩点。G1 的数据取自网页版 MJCF（MuJoCo Menagerie unitree_g1）。

(1) 算例 28.2.1：G1“站立”关键帧的质量、质心高度、脚底四个接触小球围成的脚掌（长、宽），两脚中线的位置。
    MuJoCo 中 G1 用踝策略前后摆动（踝俯仰 −0.02 + 0.02 sin(2π·0.5t) rad，髋俯仰反向）：由质心运动和角动量按式 (28.2.3) 算出的
    零力矩点与接触力的压力中心逐步比较；线性倒立摆的近似 x − z ẍ/𝔤 的误差；0.8 Hz 时压力中心贴在脚跟上，摆幅 0.03 rad 时摔倒。
(2) 算例 28.2.2、28.2.3：线性倒立摆的 ω₀、时间常数；站立时被向前、向后推，不迈步能承受的最大速度（捕获点不出脚掌）；
    踝关节所需的力矩；迈一步能承受的最大速度（步长上限 0.4 m，示意值）。
(3) 算例 28.2.4：由零力矩点规划质心：步长 0.2 m、每步 0.6 s（含 0.1 s 双脚支撑，示意值），用有界解（定理 28.2.2）求质心的侧向摆幅
    与前向速度，核对 x − ẍ/ω² 回到给定的零力矩点；所需的摩擦系数 max|ẍ|/𝔤。
"""
import math

import numpy as np

from _ch28 import G, g1_stand, g1_sway, lip_bounded
from bookout import out

S = g1_stand()
m, com = S["m"], S["com"]
z_c = float(com[2])
L_ = S["soles"]["left"]
r_s = S["r"]
toe = float(L_[:, 0].max() + r_s) - 0.0            # 脚掌前缘（小球前沿），地面坐标系 x
heel = float(L_[:, 0].min() - r_s)
foot_len = toe - heel
foot_w_toe = float(np.ptp(L_[L_[:, 0] > 0, 1]) + 2 * r_s)
foot_w_heel = float(np.ptp(L_[L_[:, 0] < 0, 1]) + 2 * r_s)
y_out = float(L_[:, 1].max() + r_s)                 # 左脚外缘
y_in = float(L_[:, 1].min() - r_s)                  # 左脚内缘
y_foot = float(L_[:, 1].mean())                     # 左脚中线
x_foot = float(L_[:, 0].mean())
out(m_g1=m, z_c=z_c, com_x_mm=com[0] * 1000, toe_mm=toe * 1000, heel_mm=heel * 1000, foot_len_mm=foot_len * 1000,
    foot_w_toe_mm=foot_w_toe * 1000, foot_w_heel_mm=foot_w_heel * 1000, y_out_mm=y_out * 1000, y_in_mm=y_in * 1000,
    y_foot_mm=y_foot * 1000, x_foot_mm=x_foot * 1000, W_g1=m * G)

# MuJoCo：踝策略摆动
SW_A, SW_B, SW_F = 0.02, -0.02, 0.5
t, cop, zmp, lip, cx, fell = g1_sway(SW_A, SW_B, f=SW_F)
assert not fell
err_zmp = float(np.abs(zmp - cop).max())
err_lip = float(np.abs(lip - cop).max())
assert err_zmp < 1e-4
out(sway_A=SW_A, sway_B=SW_B, sway_f=SW_F, cop_lo_mm=cop.min() * 1000, cop_hi_mm=cop.max() * 1000, cx_lo_mm=cx.min() * 1000,
    cx_hi_mm=cx.max() * 1000, err_zmp_um=err_zmp * 1e6, err_lip_mm=err_lip * 1000,
    lip_rel=err_lip / (cop.max() - cop.min()) * 100)
# 摆得快一些（0.8 Hz）：压力中心有一段时间贴在脚跟的接触点上；再加大摆幅就摔倒
_, cop2, zmp2, _, _, fell2 = g1_sway(0.01, -0.02, f=0.8)
_, _, _, _, _, fell3 = g1_sway(0.03, -0.02, f=0.8)
assert not fell2 and fell3
heel_c = float(L_[:, 0].min())                      # 脚跟接触小球的中心
stick = float(np.mean(np.abs(cop2 - heel_c) < 1.5e-3) * 100)   # 压力中心离脚跟小球中心不到 1.5 mm 的时间所占的百分比
out(cop2_lo_mm=np.nanmin(cop2) * 1000, stick2=stick, err_zmp2_um=float(np.abs(zmp2 - cop2).max()) * 1e6, sway_A3=0.03)

# ---------------------------------------------------------------- (2) 线性倒立摆与捕获点
w = math.sqrt(G / z_c)
Tc = 1 / w
front = toe - com[0]
back = com[0] - heel
v_front, v_back = w * front, w * back
STEP_MAX = 0.4
v_step = w * (STEP_MAX + front)                     # 迈到 0.4 m 外，脚掌前缘再多出 front
out(w=w, Tc_ms=Tc * 1000, front_mm=front * 1000, back_mm=back * 1000, v_front=v_front, v_back=v_back,
    step_max=STEP_MAX, v_step=v_step)
# 被推后不迈步：x(t) 的发散；v = 0.3 m/s 时捕获点的位置
v_push = 0.3
xi = com[0] + v_push / w
out(v_push=v_push, xi_mm=xi * 1000)
# 推力 0.6 m/s：不迈步时 1 s 后的质心位置（零力矩点停在脚尖）
v6 = 0.6
x0 = com[0] - toe
x1 = x0 * math.cosh(w * 1.0) + v6 / w * math.sinh(w * 1.0)
out(v6=v6, x1_6=x1 + toe)
# 轨道能量：E = ẋ²/2 − ω²(x − p)²/2 守恒；E > 0 时质心越过支点
E_front = v_front ** 2 / 2 - w * w * front ** 2 / 2
assert abs(E_front) < 1e-12

# ---------------------------------------------------------------- (3) 由零力矩点规划质心
SL, TS, TD = 0.2, 0.6, 0.1                          # 步长、每步时间、双脚支撑时间（示意值）
dt = 0.001
NSTEP = 10
t_all = np.arange(0, (NSTEP + 4) * TS, dt)
yf = y_foot                                        # 左脚中线到身体中线的距离
px, py = np.zeros_like(t_all), np.zeros_like(t_all)
for i, tt in enumerate(t_all):
    k = int(tt // TS) - 1                          # 第 k 步（k < 0 为起步前，双脚站立）
    tau = tt - (k + 1) * TS
    if k < 0:
        px[i], py[i] = 0.0, 0.0
        continue
    if k > NSTEP:                                  # 站好以后不再动
        px[i], py[i] = (NSTEP - 1) * SL, 0.0
        continue
    side = 1 if k % 2 == 0 else -1                 # 支撑脚：先左后右
    x_now, y_now = k * SL, side * yf if k < NSTEP else 0.0
    x_prev = (k - 1) * SL if k >= 1 else 0.0
    y_prev = -side * yf if k >= 1 else 0.0
    if k == NSTEP:                                 # 最后一步后双脚并拢站好
        x_now, y_now = (NSTEP - 1) * SL, 0.0
    if tau < TD:                                   # 双脚支撑：零力矩点由上一只脚线性移到这一只
        s = tau / TD
        px[i] = x_prev + s * (x_now - x_prev)
        py[i] = y_prev + s * (y_now - y_prev)
    else:
        px[i], py[i] = x_now, y_now
xc = lip_bounded(px, dt, w)
yc = lip_bounded(py, dt, w)
xdd = np.gradient(np.gradient(xc, dt), dt)
ydd = np.gradient(np.gradient(yc, dt), dt)
inner = slice(int(0.5 / dt), len(t_all) - int(0.5 / dt))
back_x = xc - xdd / (w * w)
back_y = yc - ydd / (w * w)
err_back = float(max(np.abs(back_x - px)[inner].max(), np.abs(back_y - py)[inner].max()))
assert err_back < 2e-3                             # 二阶差商在零力矩点折线的拐角处有 O(h) 的误差
mid = (t_all > 3 * TS) & (t_all < (NSTEP - 2) * TS)
sway = float(np.abs(yc[mid]).max())
vx_mean = SL / TS
vx = np.gradient(xc, dt)
vx_lo, vx_hi = float(vx[mid].min()), float(vx[mid].max())
mu_req = float(np.hypot(xdd[mid], ydd[mid]).max() / G)
# 没有双脚支撑（瞬时换脚）时的侧向摆幅：yf(1 − 1/cosh(ωT/2))
sway_ss = yf * (1 - 1 / math.cosh(w * TS / 2))
out(SL=SL, TS=TS, TD=TD, sway_mm=sway * 1000, sway_ss_mm=sway_ss * 1000, vx_mean=vx_mean, vx_lo=vx_lo, vx_hi=vx_hi,
    mu_req=mu_req, err_back_um=err_back * 1e6, yf_mm=yf * 1000)
# 每步时间加倍（1.2 s，双脚支撑 0.2 s）时的侧向摆幅
TS2 = 1.2
sway_ss2 = yf * (1 - 1 / math.cosh(w * TS2 / 2))
out(TS2=TS2, sway_ss2_mm=sway_ss2 * 1000)

# 站在脚尖上：零力矩点放到脚掌前缘，两只踝关节各需的俯仰力矩（踝关节在脚底接触小球坐标系的原点上方，x = 0）
ANKLE_MAX = 50.0                                    # g1.xml：踝俯仰关节 actuatorfrcrange ±50 N·m
tau_ankle = m * G * toe / 2
out(tau_ankle=tau_ankle, ankle_max=ANKLE_MAX)

# ---------------------------------------------------------------- 习题
# 28.2.2 蹲低到 z_c = 0.6 m
zc2 = 0.6
w2 = math.sqrt(G / zc2)
out(zc2=zc2, w2=w2, Tc2_ms=1000 / w2, v_front2=w2 * front)
# 28.2.4 被推到 1.0 m/s，要迈到离质心多远处才能停住
out(v_p4=1.0, step4=1.0 / w)
# 28.2.5 每步 0.4 s（不计双脚支撑）时的侧向摆幅
out(TS5=0.4, sway5_mm=yf * (1 - 1 / math.cosh(w * 0.4 / 2)) * 1000)
# 28.2.6 人：质心高 1.0 m
out(Tc_h_ms=1000 / math.sqrt(G / 1.0))
