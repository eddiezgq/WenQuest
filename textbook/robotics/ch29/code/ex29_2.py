"""29.2 节的计算：MuJoCo 模型（MJCF）。

(1) 算例 29.2.1：从零写一个两连杆臂（铝制胶囊体，程序 29.2.1 的模型）：编译后的质量、质心、主惯量与手算的胶囊体公式核对；
    质量矩阵与式 (24.2.4) 核对；惯量主轴的四元数。
(2) 算例 29.2.2：角度单位的陷阱：MJCF 默认 angle="degree"，把关节限位按弧度写成 range="-2.9 2.9"，手臂从水平放开后停在 2.9°；
    换成 <compiler angle="radian"/> 而限位仍按度写，限位就成了 ±170 rad，等于没有。
(3) 算例 29.2.3：位置伺服就是 PD：position 执行器的力 = kp(ctrl − q) − kv q̇，与 actuator_force 核对；两连杆臂在 kp = 200 N·m/rad 时
    水平保持的下垂角。问渠 WQ-CR5 的出厂位置环写成 position 执行器（kp = 2000、1000、300 N·m/rad）；带负载跑合台的标准负载在工作姿态静止时，
    各关节因“比例控制”而下垂，TCP 偏离目标多少；不动点 q = q_d − K⁻¹g(q) 与仿真核对；关节的库仑摩擦又能托住多少。
    转子惯量：关节模组的减速比 100 使电机转子惯量放大 10⁴ 倍，在质量矩阵对角元中所占的比例（与 Menagerie 的 UR5e 对比）。
(4) 算例 29.2.4：法兰上的力传感器（force、torque）读数的坐标系与方向：读数是父连杆作用在子连杆（负载）上的力，写在 site 坐标系中。
(5) 模型的规模：WQ-CR5、UR5e、Go2、G1 的 nq、nv、nu、nbody、ngeom；浮动基座 nq = nv + 1（四元数）。
"""
import math

import mujoco
import numpy as np

from _ch29 import (ARM2, CR_NAMES, G0, MJCF_DIR, Q_CR, Q_WORK, arm2_M, arm2_xml, capsule_mass_inertia, cr_chain, cr_load, cr_load_xml,
                   cr_servo_xml, cr_text, mjcf_text, quat2R, wqcr5)
from bookout import out

# ---------------------------------------------------------------- (1) 两连杆臂
P = ARM2
m = mujoco.MjModel.from_xml_string(arm2_xml())
d = mujoco.MjData(m)
m1, Ia1, It1 = capsule_mass_inertia(P["r"], P["L1"], P["rho"])
m2, Ia2, It2 = capsule_mass_inertia(P["r"], P["L2"], P["rho"])
assert abs(m.body_mass[1] - m1) < 1e-12 and abs(m.body_mass[2] - m2) < 1e-12
assert np.allclose(sorted(m.body_inertia[1]), sorted([Ia1, It1, It1]), atol=1e-15)
assert np.allclose(m.body_ipos[1], [P["L1"] / 2, 0, 0]) and np.allclose(m.body_ipos[2], [P["L2"] / 2, 0, 0])
Rq = quat2R(m.body_iquat[1])                           # 惯量主轴坐标系在连杆坐标系中的方向：主轴 z 沿连杆（x 轴）
assert np.allclose(np.abs(Rq[:, 2]), [1, 0, 0])
err_M = 0.0
for q2 in np.linspace(-2.5, 2.5, 11):
    q = np.array([0.4, q2])
    d.qpos[:] = q
    mujoco.mj_forward(m, d)
    M = np.zeros((2, 2))
    mujoco.mj_fullM(m, d, M)
    err_M = max(err_M, float(np.abs(M - arm2_M(q, m1, It1, P["L1"] / 2, m2, It2, P["L2"] / 2, P["L1"])).max()))
assert err_M < 1e-14
out(L1=P["L1"], L2=P["L2"], r_mm=P["r"] * 1000, rho=P["rho"], m1=m1, m2=m2, It1=It1, Ia1=Ia1, It2=It2, err_M=err_M,
    m1_cyl=P["rho"] * math.pi * P["r"] ** 2 * P["L1"], cap_share=(m1 - P["rho"] * math.pi * P["r"] ** 2 * P["L1"]) / m1 * 100,
    It1_rod=m1 * P["L1"] ** 2 / 12, nq_arm=m.nq, iquat_w=float(m.body_iquat[1][0]))

# ---------------------------------------------------------------- (2) 角度单位
def drop(xml, T=2.0):
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    while d.time < T - 1e-12:
        mujoco.mj_step(m, d)
    return m, d


xml_bad = arm2_xml().replace('range="-170 170"', 'range="-2.9 2.9"')
mb, db = drop(xml_bad)
assert abs(mb.jnt_range[0, 1] - math.radians(2.9)) < 1e-12
q1_bad = math.degrees(db.qpos[0])
assert 2.8 < q1_bad < 3.2
mr = mujoco.MjModel.from_xml_string(arm2_xml(angle_unit="radian"))
assert mr.jnt_range[0, 1] == 170.0
out(q1_bad_deg=q1_bad, range_rad_mode=float(mr.jnt_range[0, 1]), range_deg_mode=float(mb.jnt_range[0, 1]))

# ---------------------------------------------------------------- (3) 位置伺服 = PD
KP_A, KV_A = 200.0, 10.0
m = mujoco.MjModel.from_xml_string(arm2_xml(kp=KP_A, kv=KV_A, integrator="implicitfast"))
d = mujoco.MjData(m)
d.ctrl[:] = 0.0
while d.time < 3.0 - 1e-12:
    mujoco.mj_step(m, d)
    f_pd = KP_A * (d.ctrl - d.qpos) - KV_A * d.qvel
mujoco.mj_forward(m, d)
assert np.allclose(d.actuator_force, KP_A * (d.ctrl - d.qpos) - KV_A * d.qvel, atol=1e-10)
assert np.allclose(d.actuator_force, d.qfrc_bias, atol=1e-6)          # 静止：执行器的力 = 重力项
sag_arm = d.qpos.copy()
# 不动点：kp(0 − q) = g(q)
q = np.zeros(2)
for _ in range(100):
    d2 = mujoco.MjData(m)
    d2.qpos[:] = q
    mujoco.mj_forward(m, d2)
    q = -d2.qfrc_bias / KP_A
assert np.allclose(q, sag_arm, atol=1e-6)
tip_sag_mm = (P["L1"] * math.sin(sag_arm[0]) + P["L2"] * math.sin(sag_arm.sum())) * 1000
out(kp_arm=KP_A, kv_arm=KV_A, sag1_deg=math.degrees(sag_arm[0]), sag2_deg=math.degrees(sag_arm[1]), tip_sag_mm=tip_sag_mm,
    g1_arm=float(d.qfrc_bias[0]))

# WQ-CR5 的位置环：出厂增益写成 position 执行器，带负载跑合台的标准负载停在工作姿态
W = wqcr5()
mp = cr_load()
tool = cr_load_xml().replace("<inertial", '<site name="ft" pos="0 0 0"/><inertial')
sensors = '</actuator><sensor><force name="f" site="ft"/><torque name="t" site="ft"/></sensor>'
xml_cr = cr_text(tool=tool, option='<option><flag contact="disable"/></option>', actuator=cr_servo_xml()).replace("</actuator>", sensors)
m = mujoco.MjModel.from_xml_string(xml_cr)
d = mujoco.MjData(m)
pos_act = [mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_ACTUATOR, "pos_" + n) for n in CR_NAMES]
kp = -m.actuator_biasprm[pos_act, 1]
kd = -m.actuator_biasprm[pos_act, 2]
assert np.allclose(m.actuator_gainprm[pos_act, 0], kp) and np.allclose(kp, W.SERVO_KP) and np.allclose(kd, W.SERVO_KV)
out(kp_big=kp[0], kp_mid=kp[2], kp_small=kp[3], kd_big=kd[0], kd_mid=kd[2], kd_small=kd[3],
    frc_big=W.torque_limit()[0], frc_mid=W.torque_limit()[2], frc_small=W.torque_limit()[3], cr_dt=m.opt.timestep, cr_integ=int(m.opt.integrator))
sid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "tcp")
d.qpos[:] = Q_CR
mujoco.mj_forward(m, d)
p_goal = d.site_xpos[sid].copy()
d.ctrl[pos_act] = Q_CR
while d.time < 4.0 - 1e-12:
    mujoco.mj_step(m, d)
dq = d.qpos - Q_CR
p_sag = d.site_xpos[sid].copy()
# 不动点：kp(θ_d − θ) = g(θ)（摩擦是库仑摩擦，静止时还能多托一点：这里先用不带摩擦的模型核对，再看摩擦让下垂少了多少）
ch = cr_chain(payload=mp)
q = Q_CR.copy()
for _ in range(50):
    _, _, g = ch.closed_form(q, np.zeros(6))
    q = Q_CR - g / kp
m0 = mujoco.MjModel.from_xml_string(xml_cr)
m0.opt.disableflags |= mujoco.mjtDisableBit.mjDSBL_FRICTIONLOSS
d0 = mujoco.MjData(m0)
d0.qpos[:] = Q_CR
d0.ctrl[pos_act] = Q_CR
while d0.time < 4.0 - 1e-12:
    mujoco.mj_step(m0, d0)
assert np.allclose(q, d0.qpos, atol=1e-6)
mujoco.mj_forward(m0, d0)
p_sag0 = d0.site_xpos[sid].copy()
out(cr_sag2_deg=math.degrees(q[1] - Q_CR[1]), cr_sag3_deg=math.degrees(q[2] - Q_CR[2]), cr_sag4_deg=math.degrees(q[3] - Q_CR[3]),
    cr_tcp_sag_mm=float(np.linalg.norm(p_sag0 - p_goal)) * 1000, cr_tcp_dz_mm=float(p_sag0[2] - p_goal[2]) * 1000,
    cr_tcp_sag_fric_mm=float(np.linalg.norm(p_sag - p_goal)) * 1000, m_payload=mp[0],
    g2=float(np.abs(ch.closed_form(Q_CR, np.zeros(6))[2][1])), g3=float(np.abs(ch.closed_form(Q_CR, np.zeros(6))[2][2])))

# 转子惯量：减速比 100 使电机转子的惯量放大一万倍（J_m i²），在质量矩阵的对角元里占多少
d0.qpos[:] = Q_CR
mujoco.mj_forward(m0, d0)
Mfull = np.zeros((6, 6))
mujoco.mj_fullM(m0, d0, Mfull)
arm = np.array(W.armature())
share = arm / np.diag(Mfull) * 100
mu = mujoco.MjModel.from_xml_string(mjcf_text(option='<option><flag contact="disable"/></option>'))
du = mujoco.MjData(mu)
du.qpos[:] = Q_WORK
mujoco.mj_forward(mu, du)
Mu = np.zeros((6, 6))
mujoco.mj_fullM(mu, du, Mu)
out(arm=arm.tolist(), arm_L=arm[0], arm_M=arm[2], arm_S=arm[3], Jm_L=W.MODULES["L"]["motor"][2], Jm_S=W.MODULES["S"]["motor"][2],
    ratio=W.GEAR_RATIO, Mii_cr=np.diag(Mfull).tolist(), share=share.tolist(), share1=share[0], share2=share[1], share6=share[5],
    ur_arm=float(mu.dof_armature[0]), ur_share6=float(mu.dof_armature[5] / Mu[5, 5] * 100), ur_share2=float(mu.dof_armature[1] / Mu[1, 1] * 100))

# ---------------------------------------------------------------- (4) 力传感器
fid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_SITE, "ft")
R = d.site_xmat[fid].reshape(3, 3)
f_site = d.sensordata[0:3].copy()
t_site = d.sensordata[3:6].copy()
f_world = R @ f_site
assert abs(f_world[2] - mp[0] * G0) < 1e-3 and np.abs(f_world[:2]).max() < 1e-3      # 向上托住负载的力
assert np.allclose(t_site, -R.T @ np.cross(R @ mp[1], np.array([0, 0, -mp[0] * G0])), atol=1e-3)
out(f_site=f_site.tolist(), f_world_z=float(f_world[2]), W_payload=mp[0] * G0, t_site_norm=float(np.linalg.norm(t_site)),
    cp_mm=float(mp[1][2] * 1000), fz_site=float(f_site[2]))


# ---------------------------------------------------------------- (5) 模型的规模
def size(name):
    t = mjcf_text(name)
    mm = mujoco.MjModel.from_xml_string(t)
    return dict(nq=mm.nq, nv=mm.nv, nu=mm.nu, nbody=mm.nbody, ngeom=mm.ngeom, njnt=mm.njnt)


sz = {k: size(k) for k in ("wqcr5", "ur5e", "go2", "g1")}
assert sz["go2"]["nq"] == sz["go2"]["nv"] + 1 and sz["g1"]["nq"] == sz["g1"]["nv"] + 1
out(**{f"{k}_{a}": v for k, s in sz.items() for a, v in s.items()})

# ---------------------------------------------------------------- 习题
# 29.2.3：两连杆臂的连杆若当作细杆（不计半径），绕关节 1 的转动惯量差多少
J1_rod = m1 * P["L1"] ** 2 / 3
J1_cap = It1 + m1 * (P["L1"] / 2) ** 2
out(ex_J1_rod=J1_rod, ex_J1_cap=J1_cap, ex_J1_diff=(J1_cap - J1_rod) / J1_cap * 100)
