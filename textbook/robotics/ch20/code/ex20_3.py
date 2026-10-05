"""20.3 节的计算：步态的运动学。

定理 20.3.1  任一时刻平均有 4β 条腿着地：对各种步态在一个周期上数一数，核对。
算例 20.3.2  Go2 以 v = 0.8 m/s 小跑（设 t_c = 0.5 s、β = 0.5、抬脚高度 0.08 m）：步幅、支撑行程、中性落脚点、摆动脚的速度；
            由逆运动学（20.1 节）得到左前腿一个周期的关节角与关节速度，检查限位。
算例 20.3.1  支撑行程受足端工作空间限制：站立高度下足端前后能到多远；t_c、β 一定时的最高速度；要跑到 3.7 m/s，
            支撑时间与占地系数要多小，为什么会出现四脚腾空。
另：弗劳德数 Fr = v²/(𝔤h)。
"""
import math

import numpy as np

from _leg import AX, AY, DY, G, GAITS, GO2, GO2_FOOT_R, LEGS, TH_REST, in_stance, leg_fk, leg_ik, swing_profile
from bookout import T, out

deg = math.degrees
h_hip = -leg_fk("FL", TH_REST)[2]                         # 足端中心在大腿关节下方 0.2648 m
h0 = h_hip + GO2_FOOT_R

# ---------------------------------------------------------------- 定理 20.3.1：平均着地腿数 = 4β
avg = {}
for name, (ph, beta) in GAITS.items():
    ts = np.linspace(0, 1, 20000, endpoint=False)
    n = np.array([sum(in_stance(ph[l], t, 1.0, beta)[0] for l in LEGS) for t in ts])
    avg[name] = (float(n.mean()), int(n.min()), int(n.max()), beta)
    assert abs(n.mean() - 4 * beta) < 1e-3
walk_min = avg["walk"][1]
trot_min = avg["trot"][1]
assert walk_min == 3 and trot_min == 2 and avg["gallop"][1] == 0

# ---------------------------------------------------------------- 算例 20.3.2
v, tc, beta, hs = 0.8, 0.5, 0.5, 0.08
Ls = v * tc                                     # 步幅：一个周期机身前进的距离，也是每只脚一步迈出的距离
ell = v * beta * tc                             # 支撑行程：支撑相中足端相对机身后退的距离
x_td = ell / 2                                  # 中性落脚点：落地时足端在髋（大腿关节）前方 ℓ/2
t_sw = (1 - beta) * tc
v_sw_avg = Ls / t_sw                            # 摆动脚对地的平均速度 = v/(1 − β)
v_sw_peak = 2 * Ls / t_sw                       # 摆线：峰值是平均值的 2 倍
assert abs(v_sw_avg - v / (1 - beta)) < 1e-12

# 左前腿一个周期：机身匀速前进、高度不变、不转动；支撑相足端在 {s} 中不动，摆动相按式 (20.3.8)
ph = GAITS["trot"][0]["FL"]
N = 2000
ts = np.linspace(0, tc, N, endpoint=False)
hipx, hipy = AX, AY + DY                        # 足端中心在 {b} 中的“中性”位置：大腿关节正下方
foot_b, th = [], []
for t in ts:
    st, tau = in_stance(ph, t, tc, beta)
    if st:
        xb = x_td - v * beta * tc * tau          # 支撑相：相对机身匀速后退 ℓ
        zb = -h_hip
    else:
        s, hz = swing_profile(tau)
        x_world = -x_td + Ls * s                 # 摆动相：对地前进 L_s（以抬脚点为起点，机身坐标系随机身前进 v·t_sw·τ）
        xb = x_world - v * t_sw * tau
        zb = -h_hip + hs * hz
    p = np.array([hipx + xb, hipy, zb])
    s_ = leg_ik("FL", p)
    assert s_ is not None
    foot_b.append(p)
    th.append(s_)
foot_b, th = np.array(foot_b), np.array(th)
dt = tc / N
thd = (np.roll(th, -1, axis=0) - np.roll(th, 1, axis=0)) / (2 * dt)
fx = foot_b[:, 0] - hipx
fvx = (np.roll(fx, -1) - np.roll(fx, 1)) / (2 * dt)
v_rel_peak = float(np.max(fvx))                 # 摆动脚相对机身的最大前进速度
assert abs(v_rel_peak - (v_sw_peak - v)) < 2e-3
# 摆动脚相对机身先越过落脚点、再向后收回（式 (20.3.10)）：cos 2πτ* = ℓ/L_s = β
tau_s = 1 - math.acos(beta) / (2 * math.pi)
x_over = -x_td + ell * tau_s - Ls * math.sin(2 * math.pi * tau_s) / (2 * math.pi)
retract = x_over - x_td
assert abs(fx.max() - x_over) < 1e-6 and abs(fx.min() + x_over) < 1e-6 and abs(fx[0] + x_td) < 1e-12
th_range = np.degrees(th.max(0) - th.min(0))
thd_max = np.max(np.abs(thd), axis=0)

# ---------------------------------------------------------------- 算例 20.3.1：工作空间决定的最高速度
lo, hi = 0.0, 0.4
for _ in range(60):                             # 站立高度下，足端在大腿关节正下方的水平面内向前最远到哪里
    m = (lo + hi) / 2
    if leg_ik("FL", np.array([AX + m, AY + DY, -h_hip])) is not None:
        lo = m
    else:
        hi = m
x_reach = lo
D_max = math.sqrt(2 * 0.213 ** 2 * (1 + math.cos(GO2["robot"]["joints"][2]["limit"]["upper"])))
assert abs(x_reach - math.sqrt(D_max ** 2 - h_hip ** 2)) < 1e-9
ell_max = 2 * x_reach
v_max_05 = ell_max / (beta * tc)                # t_c = 0.5 s、β = 0.5 时运动学允许的最高速度
v_top = GO2["datasheet"]["values"]["max_speed_m_s"]           # 3.7 m/s
ell_use = 0.4                                   # 设：实际用的支撑行程（留出余量）
t_st_max = ell_use / v_top                      # 支撑时间上限
tc_fast = 0.3                                   # 设：高速时的步态周期
beta_fast = t_st_max / tc_fast
flight = 2 * (0.5 - beta_fast) * tc_fast        # 对角小跑：每周期两次四脚腾空，总时长
assert beta_fast < 0.5

fr_v = v ** 2 / (G * h0)
fr_top = v_top ** 2 / (G * h0)

out(v=v, tc=tc, beta=beta, hs=hs, Ls=Ls, ell=ell, x_td=x_td, t_sw=t_sw, v_sw_avg=v_sw_avg, v_sw_peak=v_sw_peak,
    v_rel_peak=v_rel_peak, h_hip=h_hip, tau_s=tau_s, x_over=x_over, retract=retract,
    avg_walk=avg["walk"][0], avg_trot=avg["trot"][0], avg_gallop=avg["gallop"][0],
    walk_min=walk_min, trot_min=trot_min, gallop_min=avg["gallop"][1], bound_min=avg["bound"][1],
    th2_rng=float(th_range[1]), th3_rng=float(th_range[2]), th2_min=deg(th[:, 1].min()), th2_max=deg(th[:, 1].max()),
    th3_min=deg(th[:, 2].min()), th3_max=deg(th[:, 2].max()),
    thd2_max=float(thd_max[1]), thd3_max=float(thd_max[2]),
    x_reach=x_reach, ell_max=ell_max, v_max_05=v_max_05, v_top=v_top, ell_use=ell_use, t_st_max=t_st_max,
    tc_fast=tc_fast, beta_fast=beta_fast, flight=flight, fr_v=fr_v, fr_top=fr_top, h0=h0,
    lab=T("小跑", "trot"))
