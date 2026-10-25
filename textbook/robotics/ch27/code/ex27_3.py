"""27.3 节的计算：碰撞与恢复系数。

(1) 算例 27.3.1：Ø10 mm 钢球从 0.1 m 高处落到钢板上（赫兹弹性碰撞）：最大压入量、峰值力、接触时间；仿真时间步长要多小。
(2) 算例 27.3.2：恢复系数的模型。线性弹簧-阻尼（开尔文-沃伊特）e = exp(−πζ/√(1 − ζ²))；接触力降到零就分离时的 e；
    MuJoCo 中 solref 的阻尼比 ζ 取 0.05～0.5，球落地实测的 e、接触时间，与质量、高度无关。
(3) 亨特-克罗斯利模型 λ = Kδ^{3/2}(1 + cδ̇)：由目标恢复系数定 c 的两种公式（兰卡拉尼-尼克拉韦什、弗洛雷斯），积分检验；
    c 固定时 e 随撞击速度减小。
(4) 算例 27.3.3：协作机器人撞到人。UR5e（带夹爪和毛坯）在卡盘前 B 的姿态下，TCP 沿各方向的有效质量 1/(uᵀJM⁻¹Jᵀu)，
    与 ISO/TS 15066 的近似 M/2 + m_L 比较；手、胸两个部位的允许相对速度 v = F/√(m̄k)，m̄ 为约化质量。
"""
import math

import numpy as np

from _ch27 import (TC_COEF, FLANGE_Y, G0, RHO_STEEL, TCP, ball_xml, cell_move, contact_ode, e_star, hertz_impact, kv_restitution_no_tension, mj_drop,
                   parse_links, mjcf_text, payload_parts, skew, ur_chain)
from bookout import out

# ---------------------------------------------------------------- (1) 赫兹碰撞
R_BALL = 0.005
m_ball = RHO_STEEL * 4 / 3 * math.pi * R_BALL ** 3
H_DROP = 0.1
v_ball = math.sqrt(2 * G0 * H_DROP)
dmax, Fmax, tc = hertz_impact(m_ball, R_BALL, v_ball)
K_h = 4 / 3 * e_star() * math.sqrt(R_BALL)
e_el, tc_num, F_num, _ = contact_ode(m_ball, v_ball, K_h, 1.5, 0.0, "hc", dt=1e-9, tmax=1e-3)
assert abs(e_el - 1) < 1e-6 and abs(tc_num / tc - 1) < 1e-3 and abs(F_num / Fmax - 1) < 1e-4
F_over_W = Fmax / (m_ball * G0)
dt_need = tc / 20                                     # 一次接触至少要 20 步才算得出力的形状（示意）

# ---------------------------------------------------------------- (2) 线性弹簧-阻尼与 MuJoCo
ZETAS = [0.05, 0.1, 0.2, 0.3, 0.5]
e_lin = [math.exp(-math.pi * z / math.sqrt(1 - z * z)) for z in ZETAS]
e_nt = [kv_restitution_no_tension(z) for z in ZETAS]
e_mj, t_mj = [], []
for z in ZETAS:
    e, t, F, pen, vin = mj_drop(ball_xml(solref=f"0.02 {z}", dt=1e-4))
    e_mj.append(e)
    t_mj.append(t)
t_lin = [math.pi * 0.02 * z / math.sqrt(1 - z * z) for z in ZETAS]   # 半个阻尼振动周期：ω_n = 1/(τζ)
e_mj1 = mj_drop(ball_xml(solref="0.02 1", dt=1e-4))[0]              # 默认的临界阻尼：不反弹
# 与质量、高度无关
e_m = [mj_drop(ball_xml(m=m, solref="0.02 0.2", dt=1e-4))[0] for m in (0.1, 1.0, 10.0)]
e_h = [mj_drop(ball_xml(h=h, solref="0.02 0.2", dt=1e-4))[0] for h in (0.1, 0.5, 2.0)]
spread_m = max(e_m) - min(e_m)
spread_h = max(e_h) - min(e_h)
# 要 e = 0.5，ζ 取多少（线性公式）
e_target = 0.5
zeta_for = -math.log(e_target) / math.sqrt(math.pi ** 2 + math.log(e_target) ** 2)
e_at_zeta = mj_drop(ball_xml(solref=f"0.02 {zeta_for}", dt=1e-4))[0]

# ---------------------------------------------------------------- (3) 亨特-克罗斯利
E_T = [0.9, 0.7, 0.5]
e_LN, e_FL = [], []
for et in E_T:
    cLN = 3 * (1 - et ** 2) / (4 * v_ball)
    cFL = 8 * (1 - et) / (5 * et * v_ball)
    e_LN.append(contact_ode(m_ball, v_ball, K_h, 1.5, cLN, "hc", dt=1e-9, tmax=1e-3)[0])
    e_FL.append(contact_ode(m_ball, v_ball, K_h, 1.5, cFL, "hc", dt=1e-9, tmax=1e-3)[0])
c_fix = 8 * (1 - 0.8) / (5 * 0.8 * 1.0)              # 按“1 m/s 时 e = 0.8”定 c（弗洛雷斯公式）
V_HC = [0.1, 0.3, 1.0, 3.0]
e_hc_v = [contact_ode(m_ball, v, K_h, 1.5, c_fix, "hc", dt=2e-9, tmax=1e-3)[0] for v in V_HC]

# ---------------------------------------------------------------- (4) 有效质量与 ISO/TS 15066
pl = payload_parts()
ch = ur_chain(payload=pl)
thA, thB, _ = cell_move()
M_, _, _ = ch.closed_form(thB, np.zeros(6))
J6 = ch.jacobians(thB)[-1]
p_tcp = np.array([0, FLANGE_Y + TCP, 0])
R06 = ch.flange_pose(thB)[:3, :3]
Jv = R06 @ np.hstack([-skew(p_tcp), np.eye(3)]) @ J6           # TCP 的线速度雅可比（世界坐标）
Linv = Jv @ np.linalg.solve(M_, Jv.T)
m_dir = [1 / (u @ Linv @ u) for u in np.eye(3)]
m_eig = np.linalg.eigvalsh(np.linalg.inv(Linv))
links = parse_links(mjcf_text())
M_move = sum(float(L.G[3, 3]) for L in links if L.axis is not None)
m_L = pl[0]
m_iso = M_move / 2 + m_L
REGIONS = {"hand": (140.0, 75e3, 0.6), "chest": (140.0, 25e3, 40.0)}   # ISO/TS 15066 附录 A：准静态允许力 N、等效刚度 N/m、等效质量 kg


def v_allow(F, k, mH, mR):
    mbar = 1 / (1 / mH + 1 / mR)                     # 约化质量
    return F / math.sqrt(mbar * k)


va = {}
for name, (F, k, mH) in REGIONS.items():
    va[name] = (v_allow(F, k, mH, m_iso), v_allow(F, k, mH, float(m_eig[0])), v_allow(F, k, mH, float(m_eig[-1])))   # 各方向有效质量的最小、最大值
# 以 0.5 m/s 撞手，峰值力（二质量-弹簧模型）
V_HIT = 0.5
mbar_hand = 1 / (1 / 0.6 + 1 / m_iso)
F_hit = V_HIT * math.sqrt(mbar_hand * 75e3)

# 习题
T_bounce = math.sqrt(2 * 0.5 / G0) * (1 + 0.6) / (1 - 0.6)               # 27.3.1：h = 0.5 m，e = 0.6，弹跳到停的总时间
F2 = hertz_impact(m_ball, R_BALL, 2 * v_ball)                            # 27.3.3：速度加倍
F_ratio2, t_ratio2 = F2[1] / Fmax, F2[2] / tc
zeta08 = -math.log(0.8) / math.sqrt(math.pi ** 2 + math.log(0.8) ** 2)   # 27.3.4：e = 0.8 要的 ζ
e_mj08, t_c08, *_ = mj_drop(ball_xml(solref=f"0.02 {zeta08}", dt=1e-4))
v_arm = v_allow(160.0, 40e3, 2.0, m_iso)                                 # 27.3.5：前臂（ISO/TS 15066 附录 A）

out(tc_coef=TC_COEF, T_bounce=T_bounce, F_ratio2=F_ratio2, t_ratio2=t_ratio2, zeta08=zeta08, e_mj08=e_mj08, t_c08_ms=t_c08 * 1e3, v_arm=v_arm, R_ball_mm=R_BALL * 1e3, m_ball_g=m_ball * 1e3, h_drop=H_DROP, v_ball=v_ball, dmax_um=dmax * 1e6, Fmax=Fmax, tc_us=tc * 1e6,
    F_over_W=F_over_W, dt_need_us=dt_need * 1e6,
    F_over_W_wan=F_over_W / 1e4, e_mj1=e_mj1,
    e_lin02=e_lin[2], e_nt02=e_nt[2], e_mj02=e_mj[2], e_lin05=e_lin[4], e_nt05=e_nt[4], e_mj05=e_mj[4],
    t_mj02=t_mj[2] * 1e3, t_lin02=t_lin[2] * 1e3, spread_m=spread_m, spread_h=spread_h,
    zeta_for=zeta_for, e_at_zeta=e_at_zeta,
    e_LN05=e_LN[2], e_FL05=e_FL[2], e_LN09=e_LN[0], e_FL09=e_FL[0], c_fix=c_fix, e_hc01=e_hc_v[0], e_hc1=e_hc_v[2], e_hc3=e_hc_v[3],
    m_x=m_dir[0], m_y=m_dir[1], m_z=m_dir[2], m_min=float(m_eig[0]), m_max=float(m_eig[-1]), M_move=M_move, m_L=m_L, m_iso=m_iso,
    v_hand_iso=va["hand"][0], v_hand_min=va["hand"][2], v_hand_max=va["hand"][1],
    v_chest_iso=va["chest"][0], v_chest_lo=va["chest"][2], v_chest_hi=va["chest"][1], v_hit=V_HIT, F_hit=F_hit)
