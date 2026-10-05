"""20.5 节的计算：Go2 边走边转，G1 下蹲与弯腰取物。

算例 20.5.1  Go2 以 v = 0.5 m/s、ω = 0.5 rad/s 小跑左转（设 t_c = 0.5 s、β = 0.5、抬脚 0.08 m）：瞬心、各脚的支撑行程、
            一个周期的 12 个关节角；原地转（v = 0、ω = 0.8 rad/s）；用腿式里程计（20.2 节）由关节角速度反求 (v, ω) 核对。
算例 20.5.2  G1 两脚不动、骨盆竖直下降 0.10 m：每条腿 6 个关节，用牛顿-拉夫森迭代（15.1 节）求逆解，记录收敛过程，
            并用左右对称和关节表的正运动学核对。
算例 20.5.3  G1 两脚不动，右手伸到身前低处 (0.40, −0.20, 0.35) m：按优先级的全身逆运动学（脚 > 质心 > 手 > 姿势），
            35 个变量；去掉质心任务再解一次，比较质心的位置。
"""
import math

import numpy as np

from _leg import (AX, AY, DY, G1, G1_INERTIAL, G1_JOINTS, G1_LIM, G1_REST, GO2_FOOT_R, LEG_JOINTS, LEGS, MASS_G1, TH_REST, Tm,
                  com, fk_links, g1_leg_ik, g1_sole_world, g1_stand_height, g1_whole_body, hip, hull, in_limits, in_stance,
                  leg_fk, leg_ik, leg_jac, margin, rot_axis, rz, skew, swing_profile)
from bookout import T, out, tex, vec

deg = math.degrees
h_hip = -leg_fk("FL", TH_REST)[2]
nominal = {leg: leg_fk(leg, TH_REST) for leg in LEGS}          # 足端在 {b} 中的“中性”位置（站立姿态）


# ---------------------------------------------------------------- 算例 20.5.1：边走边转
def turning(v, om, tc=0.5, beta=0.5, hs=0.08, n=1000):
    """平面运动：机身以 (v, ω) 匀速运动、高度与姿态不变。支撑脚在 {s} 中不动，因而在 {b} 中绕瞬心以 −ω 转；
    落脚点取使支撑段关于中性位置对称的点（中性落脚点的推广）。返回各腿关节角序列、支撑行程、瞬心。"""
    icr = np.array([0.0, v / om]) if abs(om) > 1e-12 else None
    ph = {"RL": 0.0, "FR": 0.0, "FL": 0.5, "RR": 0.5}
    Tst = beta * tc
    res = {leg: [] for leg in LEGS}
    stroke = {}

    def rot_about(p, ang):             # 绕瞬心转过 ang
        R = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
        return icr + R @ (p - icr)

    def stance_pos(leg, s):            # s ∈ [0, 1]：支撑相的进度；{b} 中的足端水平位置
        p0 = nominal[leg][:2]
        if icr is None:
            return p0 + np.array([v * Tst * (0.5 - s), 0.0])
        return rot_about(p0, -om * Tst * (s - 0.5))
    for leg in LEGS:
        a, b = stance_pos(leg, 0.0), stance_pos(leg, 1.0)
        stroke[leg] = float(np.linalg.norm(b - a))
        for k in range(n):
            t = tc * k / n
            st, tau = in_stance(ph[leg], t, tc, beta)
            if st:
                pxy = stance_pos(leg, tau)
                z = -h_hip
            else:
                # 摆动相：在 {s} 中从抬脚点沿直线走到下一个落脚点（摆线进度），再换算到 {b}
                sp, hz = swing_profile(tau)
                Tsw = (1 - beta) * tc
                lift_b, land_b = stance_pos(leg, 1.0), stance_pos(leg, 0.0)
                # 机身在摆动开始后 τ·T_sw 时间内的平面位移（相对摆动开始时的机身坐标系）
                def body_pose(tt):
                    if abs(om) < 1e-12:
                        return np.array([v * tt, 0.0]), 0.0
                    return np.array([v / om * math.sin(om * tt), v / om * (1 - math.cos(om * tt))]), om * tt
                pe, ae = body_pose(Tsw)
                Re = np.array([[math.cos(ae), -math.sin(ae)], [math.sin(ae), math.cos(ae)]])
                land_s = pe + Re @ land_b                     # 落脚点在“摆动开始时机身坐标系”中的位置
                w = lift_b + sp * (land_s - lift_b)
                pt, at = body_pose(tau * Tsw)
                Rt = np.array([[math.cos(at), -math.sin(at)], [math.sin(at), math.cos(at)]])
                pxy = Rt.T @ (w - pt)
                z = -h_hip + hs * hz
            th = leg_ik(leg, np.array([pxy[0], pxy[1], z]))
            assert th is not None and in_limits(leg, th)
            res[leg].append(th)
        res[leg] = np.array(res[leg])
    return res, stroke, icr


v1, om1, tc, beta = 0.5, 0.5, 0.5, 0.5
res1, stroke1, icr1 = turning(v1, om1)
R1 = v1 / om1
dist = {leg: float(np.linalg.norm(nominal[leg][:2] - icr1)) for leg in LEGS}
for leg in LEGS:                                   # 支撑行程 = 弦长 2·d·sin(ω β t_c / 2)，d 为足端到瞬心的距离
    assert abs(stroke1[leg] - 2 * dist[leg] * math.sin(om1 * beta * tc / 2)) < 1e-12
th1_range = {leg: np.degrees(res1[leg].max(0) - res1[leg].min(0)) for leg in LEGS}
hip_amp = max(float(np.max(np.abs(np.degrees(res1[leg][:, 0])))) for leg in LEGS)
res0, stroke0, _ = turning(0.0, 0.8)
dist0 = float(np.linalg.norm(nominal["FL"][:2]))
assert all(abs(stroke0[l] - stroke0["FL"]) < 1e-12 for l in LEGS)
hip_amp0 = max(float(np.max(np.abs(np.degrees(res0[leg][:, 0])))) for leg in LEGS)
straight, stroke_s, _ = turning(0.5, 1e-15)

# 腿式里程计核对：支撑相中段，由两条支撑腿的关节速度和 ω（陀螺仪）求 v_b
n = 1000
k = int(0.25 * n)                                   # t = t_c/4：RL、FR 处于支撑相中段
dtk = tc / n
w_b = np.array([0, 0, om1])
v_est = []
for leg in ("RL", "FR"):
    th = res1[leg][k]
    thd = (res1[leg][k + 1] - res1[leg][k - 1]) / (2 * dtk)
    pb = leg_fk(leg, th)
    v_est.append(-(leg_jac(leg, th) @ thd) - np.cross(w_b, pb))
v_est = np.mean(v_est, axis=0)
assert abs(v_est[0] - v1) < 1e-5 and abs(v_est[1]) < 1e-5 and abs(v_est[2]) < 1e-5

# ---------------------------------------------------------------- 算例 20.5.2：G1 下蹲
z_pel = g1_stand_height()
T_p0 = Tm(np.eye(3), (0, 0, z_pel))
Tl0 = fk_links(G1, G1_REST, T_p0)
T_fl, T_fr = Tl0["left_ankle_roll_link"].copy(), Tl0["right_ankle_roll_link"].copy()
drop = 0.10
T_p1 = Tm(np.eye(3), (0, 0, z_pel - drop))
qL, itL, errL = g1_leg_ik("left", T_p1, T_fl)
# 记录收敛过程
from _leg import g1_frame_jac, pose_err   # noqa: E402
q = dict(G1_REST)
q.update({"left_hip_pitch_joint": -0.2, "left_knee_joint": 0.4, "left_ankle_pitch_joint": -0.2})
errs = []
for _ in range(8):
    Tf, J = g1_frame_jac(q, T_p1, "left_ankle_roll_link", LEG_JOINTS["left"])
    e = pose_err(Tf, T_fl)
    errs.append(float(np.linalg.norm(e)))
    dq = np.linalg.solve(J, e)
    for i, nm in enumerate(LEG_JOINTS["left"]):
        q[nm] += dq[i]
errs = np.array(errs)
assert errs[5] < 1e-10 and errs[4] / errs[3] ** 2 < 5 and errs[5] / errs[4] ** 2 < 5      # 二次收敛（定理 15.1.2）
qR, itR, errR = g1_leg_ik("right", T_p1, T_fr)
sq = {nm: deg(qL[nm]) for nm in LEG_JOINTS["left"]}
for a, b in zip(LEG_JOINTS["left"], LEG_JOINTS["right"]):        # 左右对称：俯仰、膝相同，横滚、偏航相反
    s = -1 if ("roll" in a or "yaw" in a) else 1
    assert abs(qL[a] - s * qR[b]) < 1e-9
for nm in LEG_JOINTS["left"]:
    lo, hi = G1_LIM[nm]
    assert lo <= qL[nm] <= hi
# 这次下蹲只用到三个俯仰关节：横滚、偏航仍为零
assert abs(qL["left_hip_roll_joint"]) < 1e-9 and abs(qL["left_hip_yaw_joint"]) < 1e-9

# ---------------------------------------------------------------- 算例 20.5.3：弯腰取物
soles = np.vstack([g1_sole_world(G1_REST, T_p0, "left"), g1_sole_world(G1_REST, T_p0, "right")])
poly = hull(soles[:, :2])
c_goal = poly.mean(0)                                         # 质心的目标：双脚支撑多边形的中心
target = np.array([0.40, -0.20, 0.35])
Tw, qw, hist = g1_whole_body(target, T_p0, G1_REST, T_fl, T_fr, c_goal)
Tn, qn, histn = g1_whole_body(target, T_p0, G1_REST, T_fl, T_fr, None)
# 初值的影响（15.5 节）：从膝稍弯的姿态出发，收敛到另一组同样满足三项任务的解
q_b = dict(G1_REST)
q_b.update({"left_knee_joint": 0.2, "right_knee_joint": 0.2})
Tb2, qb2, histb = g1_whole_body(target, Tm(np.eye(3), (0, 0, z_pel - 0.02)), q_b, T_fl, T_fr, c_goal)
assert histb[-1][0] < 1e-10 and histb[-1][1] < 1e-10 and histb[-1][2] < 1e-10
qr_ = np.array([G1_REST[n] for n in G1_JOINTS])
cost_w = float(np.linalg.norm(np.array([qw[n] for n in G1_JOINTS]) - qr_))
cost_b = float(np.linalg.norm(np.array([qb2[n] for n in G1_JOINTS]) - qr_))
assert cost_b > cost_w + 0.3 and abs(qb2["waist_pitch_joint"] - qw["waist_pitch_joint"]) > 0.5
cw, _ = com(G1, G1_INERTIAL, qw, Tw)
cn, _ = com(G1, G1_INERTIAL, qn, Tn)
mw, mn = margin(poly, cw[:2]), margin(poly, cn[:2])
assert hist[-1][0] < 1e-10 and hist[-1][1] < 1e-10 and hist[-1][2] < 1e-10
assert histn[-1][0] < 1e-10 and histn[-1][2] < 1e-10
assert mw > 0.05 and mn < 0
for nm in G1_JOINTS:
    lo, hi = G1_LIM[nm]
    assert lo - 1e-9 <= qw[nm] <= hi + 1e-9 and lo - 1e-9 <= qn[nm] <= hi + 1e-9
at_lim = [nm for nm in G1_JOINTS if min(abs(qw[nm] - G1_LIM[nm][0]), abs(qw[nm] - G1_LIM[nm][1])) < math.radians(1)]
Tlw = fk_links(G1, qw, Tw)
hand_w = (Tlw["right_wrist_yaw_link"] @ np.r_[0.08, 0, 0, 1])[:3]
assert np.linalg.norm(hand_w - target) < 1e-10
pel_tilt = deg(math.acos(min(1.0, Tw[2, 2])))                 # 骨盆 z 轴与竖直方向的夹角（前倾）
pel_tilt_n = deg(math.acos(min(1.0, Tn[2, 2])))
ankle_n = deg(qn["right_ankle_pitch_joint"])
it_w = len(hist)
it_n = len(histn)
nvar = 6 + len(G1_JOINTS)
ntask = 12 + 2 + 3

out(v1=v1, om1=om1, R1=R1, icry=icr1[1], tc=tc, beta=beta,
    s_FL=stroke1["FL"], s_FR=stroke1["FR"], s_RL=stroke1["RL"], s_RR=stroke1["RR"],
    d_FL=dist["FL"], d_FR=dist["FR"], s_straight=stroke_s["FL"],
    hip_amp=hip_amp, hip_amp0=hip_amp0, s0=stroke0["FL"], d0=dist0, om0=0.8,
    th2_FR=float(th1_range["FR"][1]), th2_FL=float(th1_range["FL"][1]),
    v_est=tex(v_est, 4),
    z_pel=z_pel, drop=drop, z_pel1=z_pel - drop, itL=itL,
    e0=errs[0], e1=errs[1], e2=errs[2], e3=errs[3], e4=errs[4], e5=errs[5], qc=errs[5] / errs[4] ** 2,
    q_hp=sq["left_hip_pitch_joint"], q_kn=sq["left_knee_joint"], q_ap=sq["left_ankle_pitch_joint"],
    tx=target[0], ty=target[1], tz=target[2], nvar=nvar, ntask=ntask, it_w=it_w, it_n=it_n,
    cw=vec(cw, 4), cn=vec(cn, 4), cwx=cw[0], cnx=cn[0], mw=mw, mn=mn, cgx=c_goal[0],
    pel_w=vec(Tw[:3, 3], 4), pel_n=vec(Tn[:3, 3], 4), pelx_w=Tw[0, 3], pelx_n=Tn[0, 3], pelz_w=Tw[2, 3],
    pel_tilt=pel_tilt, pel_tilt_n=pel_tilt_n, ankle_n=ankle_n,
    w_hp=deg(qw["right_hip_pitch_joint"]), w_kn=deg(qw["right_knee_joint"]), w_wp=deg(qw["waist_pitch_joint"]),
    w_wy=deg(qw["waist_yaw_joint"]), w_wr=deg(qw["waist_roll_joint"]), w_el=deg(qw["right_elbow_joint"]),
    at_lim=", ".join(nm.replace("_joint", "") for nm in at_lim), n_lim=len(at_lim),
    b_wp=deg(qb2["waist_pitch_joint"]), b_hp=deg(qb2["right_hip_pitch_joint"]), cost_w=cost_w, cost_b=cost_b,
    note=T("全身逆运动学", "whole-body inverse kinematics"))
