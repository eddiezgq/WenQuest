"""28.4 节的计算：浮动基座动力学。Go2 的数据取自网页版 go2.xml（MuJoCo Menagerie unitree_go2）。

(1) 算例 28.4.1：Go2 的广义坐标与速度的维数；“home”姿态下质量矩阵左上角的块（左上 3×3 为 m I₃，平动与转动的耦合块）。
(2) 算例 28.4.2、28.4.5：Go2 从 0.3 m 高处落下，关节用 PD 控制保持站立姿态（kp = 60、100 N·m/rad，示意值）：
    用前向差商核对质心动力学 m c̈ = Σf + m𝔤、L̇ = Σ(p_i − c) × f_i + Σ（足端的接触力偶）；地面合力的峰值（10 ms 平均）与体重之比，
    机身下沉量，按“匀减速”估算 1 + h/s 比较；小腿关节力矩的最大值与上限 45.43 N·m。
(3) 算例 28.4.3：失重时（关掉重力）四条腿的大腿、小腿依次转动：总角动量保持为零；
    只来回转大腿，机身回到原来的姿态；大腿、小腿按“方框”的顺序转一圈，机身净转过一个角度，反向转则反向。
(4) 算例 28.4.4：静止站立时 MuJoCo 中四只脚的地面力：合力等于重力，对质心的合力矩为零；与最小范数解比较——MuJoCo 的解
    多了一组把四只脚往里拉的内力；对角线两只脚支撑时质心偏离对角线的距离。
"""
import math

import mujoco
import numpy as np

from _ch28 import G, GO2_HOME, go2_contacts, go2_feet, go2_model, go2_pd, quat2R, skew
from bookout import out

m, d = go2_model()
feet = go2_feet(m, d)
M = float(m.body_subtreemass[1])
W = M * G
out(M=M, W=W, nq=m.nq, nv=m.nv, nu=m.nu)

# ---------------------------------------------------------------- (1) 质量矩阵与静止站立
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)
Mfull = np.zeros((m.nv, m.nv))
mujoco.mj_fullM(m, d, Mfull)
assert np.allclose(Mfull[0:3, 0:3], M * np.eye(3), atol=1e-12)
c0 = d.subtree_com[1].copy()
R0 = quat2R(d.qpos[3:7])
# 左上 3×3 是 mI；平动与转动的耦合块 = −m[R^T(c − o)]（MuJoCo 自由关节的角速度在机身坐标系中）
r_oc = R0.T @ (c0 - d.qpos[0:3])
assert np.allclose(Mfull[0:3, 3:6], -M * R0 @ skew(r_oc), atol=1e-10)
out(com_home_z=c0[2], com_home_x_mm=c0[0] * 1000, Mxx=Mfull[0, 0], I_base_yy=Mfull[4, 4])

KP0, KD0 = 60.0, 2.0
mujoco.mj_resetDataKeyframe(m, d, 0)
while d.time < 2.0:
    go2_pd(m, d, GO2_HOME, KP0, KD0)
    mujoco.mj_step(m, d)
F, pos = go2_contacts(m, d, feet)
c = d.subtree_com[1].copy()
z_stand = float(d.qpos[2])                         # 站稳以后机身原点的高度
G6 = np.zeros((6, 12))
for k in range(4):
    G6[0:3, 3 * k:3 * k + 3] = np.eye(3)
    G6[3:6, 3 * k:3 * k + 3] = skew(pos[k] - c)
w_req = np.r_[0, 0, W, 0, 0, 0]
res = G6 @ F.reshape(12) - w_req
assert np.abs(res[:3]).max() < 0.02 and np.abs(res[3:]).max() < 0.02
f_mn = (np.linalg.pinv(G6) @ w_req).reshape(4, 3)
f_int = F - f_mn                                   # MuJoCo 的解与最小范数解之差：内力，合力、合力矩都为零
assert np.abs(G6 @ f_int.reshape(12)).max() < 0.03
mu_used = float((np.hypot(F[:, 0], F[:, 1]) / F[:, 2]).max())
out(Fz_front=F[0, 2], Fz_rear=F[2, 2], Fy_front=abs(F[0, 1]), Fy_rear=abs(F[2, 1]), Fx_front=abs(F[0, 0]),
    mn_front=f_mn[0, 2], mn_rear=f_mn[2, 2], com_x_mm=c[0] * 1000, com_z=c[2], foot_x_f=pos[0, 0], foot_x_r=pos[2, 0],
    foot_y=abs(pos[0, 1]), mu_used=mu_used, res_max=float(np.abs(res).max()))
# 对角线两只脚（左前、右后）支撑：质心到对角线的距离
u = pos[3, :2] - pos[0, :2]
n_ = np.array([-u[1], u[0]]) / np.linalg.norm(u)
diag_mm = abs((c[:2] - pos[0, :2]) @ n_) * 1000
out(diag_mm=diag_mm)

# ---------------------------------------------------------------- (2) 落地
H_DROP = 0.3
# 脚刚碰到地面时机身原点的高度：“home”关键帧（机身原点 0.27 m）中四个足端小球已压进地面一点
mujoco.mj_resetDataKeyframe(m, d, 0)
mujoco.mj_forward(m, d)
Z_KEY = float(d.qpos[2])
low = min(float(d.geom_xpos[g][2] - m.geom_size[g][0]) for g in feet)
Z_TOUCH = Z_KEY - low
out(z_key=Z_KEY, z_touch=Z_TOUCH, pen_key_mm=-low * 1000, sag_mm=(Z_TOUCH - z_stand) * 1000)


def drop(kp, kd, h=H_DROP, T=1.0):
    """足端离地 h 时从静止释放（机身原点高 Z_TOUCH + h），关节保持“home”姿态。"""
    mujoco.mj_resetDataKeyframe(m, d, 0)
    d.qpos[2] = Z_TOUCH + h
    rec = []
    tq = 0.0
    while d.time < T:
        tau = go2_pd(m, d, GO2_HOME, kp, kd)
        mujoco.mj_step(m, d)                         # 这一步的接触力与 v_k → v_{k+1} 严格对应
        mujoco.mj_subtreeVel(m, d)
        Fc, pc, Tc = go2_contacts(m, d, feet, torque=True)
        tq = max(tq, float(np.abs(tau[2::3]).max()))
        L = d.subtree_angmom[1].copy()
        cc = d.subtree_com[1].copy()
        rec.append((d.time, *cc, *d.subtree_linvel[1], *L, *Fc.sum(axis=0),
                    *(sum(np.cross(pc[k] - cc, Fc[k]) for k in range(4)) + Tc.sum(axis=0)), d.qpos[2]))
    r = np.array(rec)
    return r, tq


r60, tq60 = drop(60.0, 2.0)
r100, tq100 = drop(100.0, 3.0)
h = r60[1, 0] - r60[0, 0]
# 质心动力学：m (v_{k+1} − v_k)/h = Σf_k + m𝔤；(L_{k+1} − L_k)/h = Σ(p_i − c) × f_i
vdot = np.diff(r60[:, 4:7], axis=0) / h
Ldot = np.diff(r60[:, 7:10], axis=0) / h
Fsum, Mc = r60[:-1, 10:13], r60[:-1, 13:16]
err_lin = float(np.abs(M * vdot - Fsum - np.array([0, 0, -W])).max())
err_ang = float(np.abs(Ldot - Mc).max())
rel_lin = err_lin / float(np.abs(Fsum).max())
rel_ang = err_ang / float(np.abs(Mc).max())
assert rel_lin < 2e-3 and rel_ang < 2e-2          # 差商只有一阶精度：MuJoCo 先更新速度、再用新速度更新位置
out(err_lin=err_lin, err_ang=err_ang, rel_lin=rel_lin * 100, rel_ang=rel_ang * 100, Fpk_raw=float(r60[:, 12].max()) / W)
k10 = int(round(0.01 / h))


def landing(r, tq):
    fz = np.convolve(r[:, 12], np.ones(k10) / k10, "valid")
    sink = Z_TOUCH - float(r[:, 16].min())          # 机身原点比脚刚着地时最多低多少
    zs = float(r[-1, 16])
    return float(fz.max()) / W, sink, zs, tq


pk60, sink60, zf60, _ = landing(r60, tq60)
pk100, sink100, zf100, _ = landing(r100, tq100)
v_imp = math.sqrt(2 * G * H_DROP)
est60 = 1 + H_DROP / sink60
est100 = 1 + H_DROP / sink100
TAU_CALF = float(m.actuator_ctrlrange[2, 1])
out(h_drop=H_DROP, v_imp=v_imp, pk60=pk60, pk100=pk100, sink60_mm=sink60 * 1000, sink100_mm=sink100 * 1000,
    est60=est60, est100=est100, tq60=tq60, tq100=tq100, tau_calf=TAU_CALF, pk_ratio60=pk60 / est60, pk_ratio100=pk100 / est100)

# ---------------------------------------------------------------- (3) 失重时的翻身
m0, d0 = go2_model(gravity=False)


def reorient(seq, T=0.5, kp=60.0, kd=2.0):
    mujoco.mj_resetDataKeyframe(m0, d0, 0)
    d0.qpos[2] = 1.0
    q = GO2_HOME.copy()
    Lmax, Lbase = 0.0, 0.0
    bid = m0.body("base_link").id if "base_link" in [m0.body(i).name for i in range(m0.nbody)] else 1
    for dth, dca in seq:
        q0 = q.copy()
        q1 = q.copy()
        q1[1::3] += dth
        q1[2::3] += dca
        t0 = d0.time
        while d0.time < t0 + T:
            s = (d0.time - t0) / T
            s = s * s * (3 - 2 * s)
            go2_pd(m0, d0, q0 + (q1 - q0) * s, kp, kd)
            mujoco.mj_step(m0, d0)
            mujoco.mj_subtreeVel(m0, d0)
            Lmax = max(Lmax, float(np.linalg.norm(d0.subtree_angmom[1])))
            # 机身本身的角动量（不计腿）：I_b ω，用来衡量“腿的角动量”有多大
            Ib = quat2R(d0.xquat[bid]) @ np.diag(m0.body_inertia[bid]) @ quat2R(d0.xquat[bid]).T
            Lbase = max(Lbase, float(np.linalg.norm(Ib @ d0.cvel[bid][:3])))
        q = q1
    t0 = d0.time
    while d0.time < t0 + 0.5:
        go2_pd(m0, d0, q, kp, kd)
        mujoco.mj_step(m0, d0)
    Rb = quat2R(d0.qpos[3:7])
    return math.degrees(math.atan2(-Rb[2, 0], Rb[0, 0])), Lmax, Lbase


A_ = 0.6
p_single, L1, _ = reorient([(A_, 0), (-A_, 0)])
p_loop, L2, Lb2 = reorient([(A_, 0), (0, A_), (-A_, 0), (0, -A_)])
p_rev, _, _ = reorient([(0, A_), (A_, 0), (0, -A_), (-A_, 0)])
assert abs(p_single) < 0.1 and p_loop > 1.0 and p_rev < -1.0
out(A_turn=A_, p_single=abs(p_single), p_loop=p_loop, p_rev=abs(p_rev), Lmax=max(L1, L2), Lbase=Lb2, n_turn=math.ceil(90 / p_loop))

# ---------------------------------------------------------------- 习题
# 28.4.2 原地起跳 0.2 m，蹬地距离 0.1 m
out(h_jump=0.2, v_to=math.sqrt(2 * G * 0.2), s_push=0.1, F_jump=1 + 0.2 / 0.1)
# 28.4.4 对角两脚支撑时重力对对角线的力矩
out(M_diag=W * diag_mm / 1000)
