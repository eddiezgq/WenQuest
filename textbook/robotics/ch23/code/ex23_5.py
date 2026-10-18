"""23.5 节的计算：从零件库模型读取 UR5e 的惯性参数。

数据：书中的网页版 UR5e 模型 textbook/robotics/models/mjcf/ur5e.xml（由 MuJoCo Menagerie 生成，质量、惯量与原版相同，
来源提交写在文件头）；零件库条目 models/B-ARM-UR5E/entry.json（各连杆质量、厂家参数表）。

(1) 只用 Python 标准库的 XML 解析读出每个 body 的 pos、quat、关节轴和 <inertial>（mass、pos、quat、diaginertia）；
    读之前把四个占位注释换成空。质量与零件库条目逐个相同；MuJoCo 编译后的 body_mass、body_ipos、body_iquat、body_inertia 与读出的值相同。
(2) 表 23.5.1、23.5.2：各连杆在连杆坐标系中的惯性参数（十个数），G_i（式 (23.3.13)、(23.3.15)）。
(3) 算例 23.5.1：零位（手臂水平伸直）时整臂的质量、质心，对基座原点的惯量张量，绕关节 1 轴的转动惯量。
    自己沿运动链算连杆位姿（MJCF 的 pos、quat 与关节转动），与第 12 章的指数积公式核对（法兰位姿相同）；
    与 MuJoCo 核对：xipos、ximat、subtree_com，关节空间质量矩阵 M 的 (1,1) 元素减去电机转子惯量（armature = 0.1 kg·m²）。
    再用 M(θ) = Σ J_iᵀ G_i J_i（第 24 章）由本节的 G_i 算出整个 6×6 质量矩阵，与 MuJoCo 的 M − diag(armature) 核对。
(4) 算例 23.5.2：几种姿态下绕关节 1 轴的转动惯量；静止时关节 2 的重力矩由“关节 2 以外部分”的总质心求出，与 MuJoCo 的 qfrc_bias 核对。
(5) 算例 23.5.3：法兰上装夹爪 + SH-301 毛坯（算例 23.2.2）之后的整臂惯性参数；MuJoCo 用 <!--TOOL--> 处加的负载核对。
(6) 实验 23.5 的阈值：关节 1 不加驱动、自由转动时把小臂折起（θ₃ 由 0 到 150°，3 s），关节 1 的转速之比与绕关节 1 轴的转动惯量之比一致；
    转椅上收臂的人（示意值）。实验程序 lab23_5.js 用同样的模型文本修改。
(7) 习题答案：FR3 的总质量与零位质心。
"""
import json
import math

import numpy as np

from _ch23 import (BOOK, G0, GRIP_BOX, GRIP_C, GRIP_M, UR_S, adjoint, exp6, box_inertia, cyl_inertia, G_frame, inv, link_poses,
                   mj_load, mjcf_header, mjcf_text, parse_links, quat2R, sh301_blank, steiner, ur_fk, tf)
from bookout import out, tex

xml0 = mjcf_text()
links = parse_links(xml0)
names = [L.name for L in links]
entry = json.loads((BOOK / "models" / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))
lib_mass = {x["name"]: x["mass_kg"] for x in entry["robot"]["links"]}
assert all(abs(lib_mass[L.name] - L.m) < 1e-12 for L in links)            # 零件库条目的质量 = MJCF 的质量
m_all = sum(L.m for L in links)
m_move = sum(L.m for L in links[1:])                                       # 基座固定在地面上，不动
w_sheet = entry["datasheet"]["values"]["weight_kg"]
commit = mjcf_header()
assert commit == entry["source"]["commit"]
# 模型的质量从哪里来：优傲机器人公布的动力学参数（Universal Robots, "DH parameters for calculations of kinematics and
# dynamics"，零件库条目 data_sources 第 2 项）中 UR5（上一代）与 UR5e 的六个连杆质量，kg
UR5_OFFICIAL = [3.7, 8.393, 2.33, 1.219, 1.219, 0.1879]
UR5E_OFFICIAL = [3.761, 8.058, 2.846, 1.37, 1.3, 0.365]
m_model6 = [L.m for L in links[1:]]
dif = [abs(a - b) for a, b in zip(m_model6, UR5_OFFICIAL)]
assert max(dif[k] for k in (0, 1, 3, 4)) < 1e-12 and abs(dif[5] - 0.001) < 1e-12 and dif[2] > 0.05   # 与 UR5 相同；小臂不同；腕 3 多 1 g（算例 23.1.3）
m_ur5e = sum(UR5E_OFFICIAL)

mj, mm, dd = mj_load(xml0)
for b, L in enumerate(links, 1):
    assert abs(mm.body_mass[b] - L.m) < 1e-12 and np.allclose(mm.body_ipos[b], L.ipos, atol=1e-12)
    assert np.allclose(mm.body_inertia[b], L.diag, rtol=1e-12, atol=0)
    assert np.allclose(quat2R(mm.body_iquat[b]), L.R_ic, atol=1e-12)
arm = np.array(mm.dof_armature)
assert np.allclose(arm, 0.1)

# ---------------------------------------------------------------- (2) 表 23.5.1、23.5.2
def esc(s):
    return s.replace("_", "\\_")


def g(x):
    """表中的数：0.001 以下写成 a × 10⁻ⁿ。"""
    if x == 0:
        return "0"
    if abs(x) < 1e-3:
        m_, e_ = f"{x:.5e}".split("e")
        return f"{float(m_):g}\\times 10^{{{int(e_)}}}"
    return f"{x:.6g}"


def z4(x):
    return "0" if abs(x) < 5e-5 else f"{x:.4f}"


t1 = []
t2 = []
for L in links:
    t1.append(f"\\text{{{esc(L.name)}}} & {L.m:g} & ({',\\ '.join(g(v) for v in L.ipos)}) & ({',\\ '.join(g(v) for v in L.iquat)}) & "
              f"({',\\ '.join(g(v) for v in L.diag)})")
    Io = L.I_link_o
    assert abs(Io[0, 1]) < 1e-15 and abs(Io[0, 2]) < 1e-15 and abs(Io[1, 2]) < 1e-15     # UR5e 各连杆的惯性积都为零
    t2.append(f"\\text{{{esc(L.name)}}} & {z4(L.m * L.ipos[0])} & {z4(L.m * L.ipos[1])} & {z4(L.m * L.ipos[2])} & "
              f"{Io[0, 0]:.5f} & {Io[1, 1]:.5f} & {Io[2, 2]:.5f}")
    assert np.allclose(L.G, L.G.T) and np.linalg.eigvalsh(L.G).min() > 0
w3 = links[-1]
I_w3 = w3.I_link_c                                                         # quat = (1, 0, 0, 1)/√2：绕 z 转 90°
assert np.allclose(I_w3, np.diag([w3.diag[1], w3.diag[0], w3.diag[2]]), atol=1e-18)
G_w3 = w3.G

# ---------------------------------------------------------------- (3) 算例 23.5.1：零位
def arm_props(theta, extra=None):
    """整臂（不含基座）的质量、质心、对 {s} 原点的惯量、绕关节 1 轴的转动惯量、{s} 中的合成空间惯量。
    extra: (质量, 质心在法兰坐标系, 对质心的惯量在法兰坐标系) —— 负载。"""
    T = link_poses(links, theta)
    m = 0.0
    mc = np.zeros(3)
    I_O = np.zeros((3, 3))
    Gs = np.zeros((6, 6))
    parts = [(L.m, T[L.name], L.ipos, L.I_link_c, L.G) for L in links[1:]]
    if extra is not None:
        mp, cp, Ip = extra
        Tf = ur_fk(theta)                                                  # 法兰坐标系 {b}
        parts.append((mp, Tf, cp, Ip, G_frame(Ip, mp, np.eye(3), cp)))
    for mi, Ti, ci, Ici, Gi in parts:
        R, p = Ti[:3, :3], Ti[:3, 3]
        c_s = R @ ci + p
        m += mi
        mc += mi * c_s
        I_O += steiner(R @ Ici @ R.T, mi, c_s)                              # 先转到 {s} 的方向，再用平行轴定理
        A = adjoint(inv(Ti))
        Gs += A.T @ Gi @ A                                                 # 式 (23.5.3)
    c = mc / m
    assert np.allclose(Gs[:3, :3], I_O, atol=1e-12) and np.allclose(Gs[3:, :3], -m * np.array([[0, -c[2], c[1]], [c[2], 0, -c[0]], [-c[1], c[0], 0]]), atol=1e-12)
    return m, c, I_O, float(I_O[2, 2]), Gs


th0 = np.zeros(6)
T0 = link_poses(links, th0)
assert np.allclose(T0["wrist_3_link"] @ tf(None, [0, 0.1, 0]), ur_fk(th0), atol=1e-12)   # 法兰 = 第 12 章的 M
rng = np.random.default_rng(5)
for _ in range(5):
    th = rng.uniform(-math.pi, math.pi, 6)
    assert np.allclose(link_poses(links, th)["wrist_3_link"] @ tf(None, [0, 0.1, 0]), ur_fk(th), atol=1e-12)

m0, c0, IO0, Izz0, G0s = arm_props(th0)
c_all0 = (m0 * c0 + links[0].m * T0["base"][:3, 3]) / m_all              # 连同基座


def mj_check(theta, xml=xml0, extra_body=False):
    mj, mm, dd = mj_load(xml)
    dd.qpos[:6] = theta
    mj.mj_forward(mm, dd)
    T = link_poses(links, theta)
    for b, L in enumerate(links, 1):
        assert np.allclose(dd.xipos[b], T[L.name][:3, :3] @ L.ipos + T[L.name][:3, 3], atol=1e-12)
    M = np.zeros((mm.nv, mm.nv))
    mj.mj_fullM(mm, dd, M)
    return dd.subtree_com[2].copy(), M - np.diag(mm.dof_armature), dd.qfrc_bias.copy()


sc0, Mq0, bias0 = mj_check(th0)
assert np.allclose(sc0, c0, atol=1e-12) and abs(Mq0[0, 0] - Izz0) < 1e-12


def mass_matrix(theta):
    """M(θ) = Σ J_iᵀ G_i J_i：J_i 是连杆 i 坐标系的物体雅可比（只有关节 1…i 的列）。"""
    T = link_poses(links, theta)
    n = len(theta)
    M = np.zeros((n, n))
    axes = [(k, L) for k, L in enumerate(links) if L.axis is not None]
    for i, L in enumerate(links[1:], 1):
        Ti = T[L.name]
        J = np.zeros((6, n))
        for col, (k, Lj) in enumerate(axes):
            if k > i:
                break
            Sj = adjoint(T[Lj.name]) @ np.r_[Lj.axis, 0, 0, 0]               # 关节 j 的空间旋量轴（关节在连杆 j 的原点）
            J[:, col] = adjoint(inv(Ti)) @ Sj
        M += J.T @ L.G @ J
    return M


errM = 0.0
for th in [th0] + [rng.uniform(-math.pi, math.pi, 6) for _ in range(5)]:
    _, Mq, _ = mj_check(th)
    errM = max(errM, float(np.abs(mass_matrix(th) - Mq).max()))
assert errM < 1e-12

# ---------------------------------------------------------------- (4) 算例 23.5.2：几种姿态
poses = {"zero": th0, "home": np.array([-math.pi / 2, -math.pi / 2, math.pi / 2, -math.pi / 2, -math.pi / 2, 0]),
         "fold": np.array([0, 0, math.radians(150), -math.pi / 2, 0, 0]), "up": np.array([0, -math.pi / 2, 0, -math.pi / 2, 0, 0])}
Izz = {k: arm_props(v)[3] for k, v in poses.items()}
cz = {k: arm_props(v)[1] for k, v in poses.items()}
for k, v in poses.items():
    _, Mq, _ = mj_check(v)
    assert abs(Mq[0, 0] - Izz[k]) < 1e-12
# 关节 2 的重力矩：关节 2 以外（upper_arm_link 起）部分的总质心
def tau2(theta, extra=None):
    T = link_poses(links, theta)
    ms, mc = 0.0, np.zeros(3)
    for L in links[2:]:
        Ti = T[L.name]
        ms += L.m
        mc += L.m * (Ti[:3, :3] @ L.ipos + Ti[:3, 3])
    if extra is not None:
        Tf = ur_fk(theta)
        ms += extra[0]
        mc += extra[0] * (Tf[:3, :3] @ extra[1] + Tf[:3, 3])
    c = mc / ms
    f = np.array([0, 0, ms * G0])                                            # 机器人托住它们所需的力
    Fs = np.r_[np.cross(c, f), f]
    # 关节 2 此刻的旋量轴：零位的 S₂ 被关节 1 带着转，S₂(θ) = [Ad_{e^{[S₁]θ₁}}] S₂
    S2 = adjoint(exp6(UR_S[0], theta[0])) @ UR_S[1]
    return ms, c, float(S2 @ Fs)


m2, c2, tau2_0 = tau2(th0)
assert abs(tau2_0 - bias0[1]) < 1e-10
d2x = c2[0] - (-0.0)                                                      # 关节 2 轴过 x = 0（零位，轴沿 −y）
_, _, bias_home = mj_check(poses["home"])
_, _, tau2_home = tau2(poses["home"])
assert abs(tau2_home - bias_home[1]) < 1e-10

# ---------------------------------------------------------------- (5) 算例 23.5.3：加负载
m_b, r_b, L_b = sh301_blank()
gx, gz, gy = GRIP_BOX
cb = cyl_inertia(m_b, r_b, L_b)
I_bl = np.diag([cb[0, 0], cb[2, 2], cb[0, 0]])
c_g = np.array([0, GRIP_C, 0])
c_bl = np.array([0, 0.15 - 0.04 + L_b / 2, 0])
m_p = GRIP_M + m_b
c_p = (GRIP_M * c_g + m_b * c_bl) / m_p
I_pc = steiner(box_inertia(GRIP_M, gx, gy, gz), GRIP_M, c_g - c_p) + steiner(I_bl, m_b, c_bl - c_p)
extra = (m_p, c_p, I_pc)
mL, cL, IOL, IzzL, _ = arm_props(th0, extra)
tool = (f'<body name="payload" pos="0 0.1 0"><inertial pos="{c_p[0]} {c_p[1]} {c_p[2]}" mass="{m_p}" '
        f'fullinertia="{I_pc[0, 0]} {I_pc[1, 1]} {I_pc[2, 2]} {I_pc[0, 1]} {I_pc[0, 2]} {I_pc[1, 2]}"/></body>')
mjL, mmL, ddL = mj_load(mjcf_text(tool=tool))
mjL.mj_forward(mmL, ddL)
ML = np.zeros((6, 6))
mjL.mj_fullM(mmL, ddL, ML)
assert abs(ML[0, 0] - 0.1 - IzzL) < 1e-12 and np.allclose(ddL.subtree_com[2], cL, atol=1e-12)
_, _, tau2L = tau2(th0, (m_p, c_p))
assert abs(tau2L - ddL.qfrc_bias[1]) < 1e-10

# ---------------------------------------------------------------- (6) 实验 23.5 的阈值
OPT = '<option timestep="0.002"/>'
J1_FREE = ('<joint name="shoulder_pan_joint" class="size3" axis="0 0 1" />',
           '<joint name="shoulder_pan_joint" class="size3" axis="0 0 1" armature="0" limited="false" />')
A1_OFF = ('<general class="size3" name="shoulder_pan" joint="shoulder_pan_joint" />',
          '<general class="size3" name="shoulder_pan" joint="shoulder_pan_joint" gainprm="0" biasprm="0 0 0" />')
xs = mjcf_text(option=OPT)
assert xs.count(J1_FREE[0]) == 1 and xs.count(A1_OFF[0]) == 1
xs = xs.replace(*J1_FREE).replace(*A1_OFF)
mjs, ms_, ds = mj_load(xs)
qa = np.array([0, 0, 0, -math.pi / 2, 0, 0])
qb = qa.copy()
qb[2] = math.radians(150)
ds.qpos[:] = qa
ds.ctrl[1:] = qa[1:]
ds.qvel[0] = 1.0
mjs.mj_forward(ms_, ds)
Mst = np.zeros((6, 6))
mjs.mj_fullM(ms_, ds, Mst)
w_start = float(ds.qvel[0])
I_start = arm_props(ds.qpos.copy())[3]
assert abs(Mst[0, 0] - I_start) < 1e-12
while ds.time < 6.0 - 1e-9:
    u = min(1.0, max(0.0, (ds.time - 1.0) / 3.0))
    sm = u * u * (3 - 2 * u)
    ds.ctrl[1:] = (qa + (qb - qa) * sm)[1:]
    mjs.mj_step(ms_, ds)
w_end = float(ds.qvel[0])
I_end = arm_props(ds.qpos.copy())[3]
ratio_w = w_end / w_start
ratio_I = I_start / I_end
spin_err = abs(ratio_w / ratio_I - 1) * 100
assert spin_err < 0.5                                                      # 实验任务的阈值取 1%
th3_end = math.degrees(ds.qpos[2])

# 实验 23.5：负载按 lab23_5.js 写的（四舍五入的）数字，3.8 kg 时与算例 23.5.3 相差不到 10⁻⁴
lab_tool = ('<body name="payload" pos="0 0.1 0"><inertial pos="0 0.16114 0" mass="3.8" diaginertia="0.0260338 0.0017083 0.0262671"/></body>')
assert abs(c_p[1] - 0.16114) < 1e-5 and np.allclose(np.diag(I_pc), [0.0260338, 0.0017083, 0.0262671], atol=1e-7)
mjT, mmT, ddT = mj_load(mjcf_text(tool=lab_tool))
mjT.mj_forward(mmT, ddT)
MT = np.zeros((6, 6))
mjT.mj_fullM(mmT, ddT, MT)
assert abs((MT[0, 0] - 0.1) / IzzL - 1) < 1e-4
I_up0 = arm_props(np.array([0, -math.pi / 2, 0, 0, 0, 0]))[3]        # 任务 2 的演示姿态（θ₄ = 0）
assert I_up0 < 1.0
# 生活场景：转椅上收臂（lab23_5.js 的同一个模型）
arm = lambda sg: (f'<body name="arm{"L" if sg > 0 else "R"}" pos="0 {sg * 0.2} 1.15"><joint name="sh{"L" if sg > 0 else "R"}" type="hinge" axis="{1 if sg > 0 else -1} 0 0" range="-1.6 0.2"/>'
                  f'<geom type="capsule" fromto="0 0 0 0 {sg * 0.6} 0" size="0.04" mass="3.5" contype="0" conaffinity="0"/>'
                  f'<geom type="sphere" size="0.06" pos="0 {sg * 0.62} 0" mass="2" contype="0" conaffinity="0"/></body>')
xc = ('<mujoco><compiler angle="radian"/><option timestep="0.001" integrator="RK4"/><worldbody><body name="chair"><joint name="swivel" type="hinge" axis="0 0 1"/>'
      '<geom type="cylinder" size="0.22 0.03" pos="0 0 0.5" mass="6" contype="0" conaffinity="0"/>'
      '<geom type="cylinder" size="0.15 0.35" pos="0 0 0.85" mass="50" contype="0" conaffinity="0"/>'
      '<geom type="sphere" size="0.11" pos="0 0 1.33" mass="5" contype="0" conaffinity="0"/>'
      '<geom type="box" size="0.02 0.02 0.03" pos="0.15 0 1.0" mass="0" contype="0" conaffinity="0"/>'
      + arm(1) + arm(-1) + '</body></worldbody><actuator><position joint="shL" kp="1500" kv="150"/><position joint="shR" kp="1500" kv="150"/></actuator></mujoco>')
mjc, mmc, ddc = mj_load(xc)


def izz_mj(mm_, dd_, first):
    s_ = 0.0
    for b in range(first, mm_.nbody):
        R = dd_.ximat[b].reshape(3, 3)
        c = dd_.xipos[b]
        s_ += (R @ np.diag(mm_.body_inertia[b]) @ R.T)[2, 2] + mm_.body_mass[b] * (c[0] ** 2 + c[1] ** 2)
    return s_


ddc.qvel[0] = 2 * math.pi
mjc.mj_forward(mmc, ddc)
Ic0 = izz_mj(mmc, ddc, 1)
while ddc.time < 5.5 - 1e-9:
    u = min(1.0, max(0.0, (ddc.time - 1.0) / 2.0))
    ddc.ctrl[:] = -1.45 * u * u * (3 - 2 * u)
    mjc.mj_step(mmc, ddc)
chair_rw = ddc.qvel[0] / (2 * math.pi)
chair_rI = Ic0 / izz_mj(mmc, ddc, 1)
assert abs(chair_rw / chair_rI - 1) < 1e-6 and chair_rw > 1.5
# 收臂的 UR5e 用 lab23_5.js 的同样方法（ximat、body_inertia）算 I_zz，与 arm_props 相同
mjs.mj_forward(ms_, ds)                                              # mj_step 之后的 xipos 是上一步的，先重算运动学
assert abs(izz_mj(ms_, ds, 2) - I_end) < 1e-12

# ---------------------------------------------------------------- (7) 习题答案：FR3
fr = parse_links(mjcf_text("fr3"))
mjf, mmf, ddf = mj_load(mjcf_text("fr3"))
mjf.mj_forward(mmf, ddf)
Tf0 = link_poses(fr, np.zeros(len([L for L in fr if L.axis is not None])))
m_fr = sum(L.m for L in fr)
c_fr = sum(L.m * (Tf0[L.name][:3, :3] @ L.ipos + Tf0[L.name][:3, 3]) for L in fr) / m_fr
assert abs(m_fr - mmf.body_mass.sum()) < 1e-9 and np.allclose(c_fr, ddf.subtree_com[0], atol=1e-9)
# 23.5.2：fullinertia → 主惯量与主轴（quat）
If = np.array([[0.020, 0.004, 0], [0.004, 0.030, 0], [0, 0, 0.025]])
lam_f, Q_f = np.linalg.eigh(If)
if np.linalg.det(Q_f) < 0:
    Q_f[:, 0] *= -1
mjq, mmq, _ = mj_load('<mujoco><worldbody><body><freejoint/><inertial pos="0 0 0" mass="1" fullinertia="0.020 0.030 0.025 0.004 0 0"/></body></worldbody></mujoco>')
assert np.allclose(np.sort(mmq.body_inertia[1]), lam_f, rtol=1e-12)
Rq = quat2R(mmq.body_iquat[1])
assert np.allclose(Rq @ np.diag(mmq.body_inertia[1]) @ Rq.T, If, atol=1e-15)
ang_f = (math.degrees(math.atan2(Q_f[1, 0], Q_f[0, 0])) + 90) % 180 - 90          # 轴的方向取在 (−90°, 90°]
# 23.5.3：URDF 的 rpy = (0, 1.5708, 0)（绕固定轴 x、y、z 依次转，R = Rz Ry Rx），质心 (0, 0, 0.1)，2 kg
RPY_U = 1.5708                                   # URDF 里常见的“π/2”写法
cr, sr = math.cos(RPY_U), math.sin(RPY_U)
R_u = np.array([[cr, 0, sr], [0, 1, 0], [-sr, 0, cr]])
I_u = steiner(R_u @ np.diag([0.01, 0.02, 0.03]) @ R_u.T, 2.0, [0, 0, 0.1])
tri = {L.name: (np.sort(L.diag)[0] + np.sort(L.diag)[1]) / np.sort(L.diag)[2] for L in fr if L.m > 0}
tri_name = min(tri, key=tri.get)
tri_fr = tri[tri_name]
assert tri_name == "fr3_link5"                                        # 最接近等号的是 link5（像薄板）
d7 = np.sort([L for L in fr if L.name == "fr3_link7"][0].diag)
assert d7[0] < 0.01 * d7[1] and abs(d7[1] / d7[2] - 1) < 0.01          # link7：一个主惯量几乎为零、另两个几乎相等（像细杆）
tri_fr7 = tri["fr3_link7"]
assert sorted(tri.values())[1] == tri_fr7                            # 其次是 link7
I_u_off = float(abs(I_u[0, 2]))

out(commit=commit[:7], m_all=m_all, m_move=m_move, w_sheet=w_sheet, dm_sheet=m_all - w_sheet,
    t1=r" \\ ".join(t1), t2=r" \\ ".join(t2), I_w3=tex(I_w3 * 1e6, 3), G_w3=tex(G_w3, 4),
    c0=tex(c0, 4), c_all0=tex(c_all0, 4), IO0=tex(IO0, 4), Izz0=Izz0, Izz_mj=Mq0[0, 0], errM=errM, rc0=math.hypot(c0[0], c0[1]),
    Izz_home=Izz["home"], Izz_fold=Izz["fold"], Izz_up=Izz["up"], ratio_zf=Izz["zero"] / Izz["fold"],
    m2=m2, c2=tex(c2, 4), d2x=d2x, d2x_abs=abs(d2x), tau2_0=tau2_0, bias2=bias0[1], tau2_home=tau2_home,
    m_p=m_p, c_p=c_p[1], mL=mL, cL=tex(cL, 4), IzzL=IzzL, dIzz=(IzzL / Izz0 - 1) * 100, tau2L=tau2L, dtau2=(tau2L / tau2_0 - 1) * 100,
    w_end=w_end, ratio_w=ratio_w, ratio_I=ratio_I, spin_err=spin_err, I_start=I_start, I_end=I_end, th3_end=th3_end,
    m_fr=m_fr, c_fr=tex(c_fr, 4), tri_fr=tri_fr, tri_fr7=tri_fr7, I_u_off=I_u_off, arm=0.1,
    m_ur5e=m_ur5e, dm_ur5e=m_ur5e - m_move, fa_m_model=m_model6[2], fa_m_ur5=UR5_OFFICIAL[2], ua_m=m_model6[1], ua_ur5e=UR5E_OFFICIAL[1],
    lam_f=tex(lam_f.reshape(1, -1), 5), chair_rw=chair_rw, chair_rI=chair_rI, q_f=tex(np.array(mmq.body_iquat[1]).reshape(1, -1), 4), ang_f=ang_f, I_u=tex(I_u, 4), rpy_u=f'{RPY_U:.4f}')
