"""第 28 章共用：移动、足式与空中机器人的动力学。以下划线开头，构建时不单独运行。

数据来源：
- 牵引式 AGV（19.4 节）：轴距 L = 1.2 m、轮距 w = 0.8 m 取自第 19 章；质量、质心位置与高度、轮胎侧偏刚度是本章的示意值；
- 轿车（生活例子）：中型轿车的典型参数（示意值）；
- Go2、G1、X2：textbook/robotics/models/mjcf/ 下的网页版 MJCF（textbook/tools/mjcf_web.py 由 MuJoCo Menagerie 生成，
  提交 4d038b3feae26ec82b46a4d586379114012a8ac7；质量、惯量、关节、执行器与原版相同）。
记号与正文一致：{b} 为车体（机身）坐标系，x 向前、y 向左、z 向上；𝔤 = 9.81 m/s²（符号约定第九节）。
"""
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BOOK = HERE.parents[1]
MJCF_DIR = BOOK / "models" / "mjcf"
G = 9.81


# ---------------------------------------------------------------- 李群小工具
def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]], float)


def rotx(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def roty(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rotz(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def quat2R(q):
    w, x, y, z = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
                     [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
                     [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]])


def R2quat(R):
    import mujoco
    q = np.zeros(4)
    mujoco.mju_mat2Quat(q, np.asarray(R, float).reshape(9))
    return q


def mjcf_text(name, option="", world="", actuator="", tool=""):
    t = (MJCF_DIR / f"{name}.xml").read_text(encoding="utf-8")
    return (t.replace("<!--OPTION-->", option).replace("<!--WORLD-->", world)
            .replace("<!--ACTUATOR-->", actuator).replace("<!--TOOL-->", tool))


def mj_load(xml):
    import mujoco
    m = mujoco.MjModel.from_xml_string(xml)
    return m, mujoco.MjData(m)


# ---------------------------------------------------------------- 28.1 轮式车辆（示意值）
AGV = dict(m=800.0,          # 满载总质量：车 300 kg + 货 500 kg
           L=1.2, w=0.8,     # 轴距、轮距（19.4 节）
           a=0.65, b=0.55,   # 质心到前轴、后轴的距离
           h=0.65,           # 满载时质心离地高度
           Iz=800.0 * (1.8 ** 2 + 1.0 ** 2) / 12,   # 绕竖直轴的转动惯量：按 1.8 m × 1.0 m 的均质板估算
           Cf=2.0e4, Cr=2.0e4,                       # 前轴、后轴的侧偏刚度（两个轮子合计），N/rad
           v_max=2.0)        # 最高车速
CAR = dict(m=1500.0, L=2.7, w=1.55, a=1.2, b=1.5, h=0.55, Iz=2500.0, Cf=1.0e5, Cr=1.2e5)
MU_DRY, MU_WET = 0.7, 0.4    # 干、湿水泥地面（示意值）


def axle_loads(P, ax=0.0, g=G):
    """前、后轴的法向载荷（静载 + 纵向加速度 ax 引起的载荷转移）。"""
    m, L, a, b, h = P["m"], P["L"], P["a"], P["b"], P["h"]
    Fzf = m * (g * b - ax * h) / L
    Fzr = m * (g * a + ax * h) / L
    return Fzf, Fzr


def fiala(alpha, C, mu, Fz):
    """刷子模型（Fiala）的侧向力：小侧偏角时 C α，侧偏角达到 α_sl = arctan(3μF_z/C) 后整片接地印迹滑动，为 μF_z。"""
    t = math.tan(alpha)
    tsl = 3 * mu * Fz / C
    if abs(t) >= tsl:
        return math.copysign(mu * Fz, t)
    return C * t - C * C * abs(t) * t / (3 * mu * Fz) + C ** 3 * t ** 3 / (27 * mu * mu * Fz * Fz)


def understeer_K(P):
    """不足转向度 K（rad/(m/s²)）：稳态转弯时 δ = L/R + K a_y（线性轮胎）。"""
    return P["m"] / P["L"] * (P["b"] / P["Cf"] - P["a"] / P["Cr"])


def bicycle_rhs(P, x, delta, vx, mu=None):
    """动力学自行车模型，状态 x = (v_y, r)：侧向速度（质心处，{b} 中）与横摆角速度。
    前、后轮的侧偏角 α_f = δ − (v_y + a r)/v_x，α_r = −(v_y − b r)/v_x；侧向力为线性（mu=None）或 Fiala 模型。"""
    vy, r = x
    m, a, b, Iz = P["m"], P["a"], P["b"], P["Iz"]
    af = delta - math.atan2(vy + a * r, vx)
    ar = -math.atan2(vy - b * r, vx)
    if mu is None:
        Fyf, Fyr = P["Cf"] * af, P["Cr"] * ar
    else:
        Fzf, Fzr = axle_loads(P)
        Fyf, Fyr = fiala(af, P["Cf"], mu, Fzf), fiala(ar, P["Cr"], mu, Fzr)
    vyd = (Fyf * math.cos(delta) + Fyr) / m - vx * r
    rd = (a * Fyf * math.cos(delta) - b * Fyr) / Iz
    return np.array([vyd, rd]), af, ar, Fyf, Fyr


def bicycle_steady(P, delta, vx):
    """线性自行车模型的稳态：v_y、r（由 A x + B δ = 0 解出）。"""
    m, a, b, Iz, Cf, Cr = P["m"], P["a"], P["b"], P["Iz"], P["Cf"], P["Cr"]
    A = np.array([[-(Cf + Cr) / (m * vx), -(a * Cf - b * Cr) / (m * vx) - vx],
                  [-(a * Cf - b * Cr) / (Iz * vx), -(a * a * Cf + b * b * Cr) / (Iz * vx)]])
    B = np.array([Cf / m, a * Cf / Iz])
    return np.linalg.solve(A, -B * delta), A, B


def agv_xml(mu, R_wheel=0.15, m_w=10.0, k=1e6):
    """MuJoCo 中的牵引式 AGV：车体（含货）+ 四个圆柱车轮，每个车轮有一根竖直的悬架弹簧（刚度 k，预压使静止时弹簧在原位），
    前轮有转向关节（位置伺服），后轮由速度伺服驱动。车体坐标系原点在后轴中点的地面上。"""
    P = AGV
    L, w, a, b, h = P["L"], P["w"], P["a"], P["b"], P["h"]
    mc = P["m"] - 4 * m_w
    zc = (P["m"] * h - 4 * m_w * R_wheel) / mc
    xc = (P["m"] * b - 2 * m_w * L) / mc
    I = [mc * (1.0 ** 2 + 0.5 ** 2) / 12, mc * (1.8 ** 2 + 0.5 ** 2) / 12, mc * (1.8 ** 2 + 1.0 ** 2) / 12]
    Fzf, Fzr = axle_loads(P)

    def wheel(n, x, y, steer, Fz):
        pre = (Fz / 2 - m_w * G) / k                 # 弹簧预压：静止时悬架关节在 0 位
        s = (f'<body name="{n}" pos="{x} {y} {R_wheel}"><joint name="{n}_z" type="slide" axis="0 0 1" stiffness="{k}" '
             f'damping="{0.1 * math.sqrt(k * mc / 4) * 2:.1f}" springref="{pre:.6f}"/>')
        if steer:
            s += f'<joint name="{n}_s" axis="0 0 1" range="-0.8 0.8"/>'
        s += (f'<joint name="{n}_r" axis="0 1 0"/><geom type="cylinder" size="{R_wheel} 0.05" quat="0.7071068 0.7071068 0 0" '
              f'mass="{m_w}" friction="{mu} 0.005 0.0001"/></body>')
        return s
    return (f'<mujoco><option timestep="0.001" integrator="implicitfast" cone="elliptic" impratio="10"/>'
            f'<default><joint armature="0.05"/></default><worldbody>'
            f'<geom type="plane" size="50 50 .1" friction="{mu} 0.005 0.0001"/>'
            f'<body name="car"><freejoint/><inertial pos="{xc} 0 {zc}" mass="{mc}" diaginertia="{I[0]} {I[1]} {I[2]}"/>'
            + wheel("fl", L, w / 2, 1, Fzf) + wheel("fr", L, -w / 2, 1, Fzf) + wheel("rl", 0, w / 2, 0, Fzr) + wheel("rr", 0, -w / 2, 0, Fzr)
            + '</body></worldbody><actuator><position joint="fl_s" kp="200000" kv="5000"/><position joint="fr_s" kp="200000" kv="5000"/>'
            '<velocity joint="rl_r" kv="3000"/><velocity joint="rr_r" kv="3000"/></actuator></mujoco>')


def agv_circle(mu, v_of_t, R=3.0, T=6.0, avg=1.0, stop=None, R_wheel=0.15):
    """MuJoCo：AGV 按阿克曼转角沿半径 R（后轴中点）的圆行驶，后轮按电子差速给转速，车速 v_of_t(t)。
    返回最后 avg 秒的平均值：质心的侧向加速度（由地面合力求出）、内侧两轮的法向力之和、后轴中点的侧滑速度（向外为正）、质心高度。
    stop(rec) 为真时提前结束并返回当时的值。"""
    import mujoco
    P = AGV
    L, w = P["L"], P["w"]
    m, d = mj_load(agv_xml(mu, R_wheel))
    di, do = math.atan(L / (R - w / 2)), math.atan(L / (R + w / 2))
    car = m.body("car").id
    v0 = v_of_t(0.0)
    d.qvel[0], d.qvel[5] = v0, v0 / R
    for j, rad in (("fl_r", math.hypot(L, R - w / 2)), ("fr_r", math.hypot(L, R + w / 2)), ("rl_r", R - w / 2), ("rr_r", R + w / 2)):
        d.qvel[m.joint(j).dofadr[0]] = v0 * rad / R / R_wheel
    d.qpos[m.joint("fl_s").qposadr[0]], d.qpos[m.joint("fr_s").qposadr[0]] = di, do
    d.ctrl[0], d.ctrl[1] = di, do
    recs = []
    f6 = np.zeros(6)
    while d.time < T:
        v = v_of_t(d.time)
        d.ctrl[2], d.ctrl[3] = v * (R - w / 2) / R / R_wheel, v * (R + w / 2) / R / R_wheel
        mujoco.mj_step(m, d)
        if int(round(d.time * 1000)) % 10:
            continue
        F, inner = np.zeros(3), 0.0
        for i in range(d.ncon):
            c = d.contact[i]
            mujoco.mj_contactForce(m, d, i, f6)
            fw = c.frame.reshape(3, 3).T @ f6[:3]
            b2 = m.geom_bodyid[c.geom2]
            wb = b2 if b2 != 0 else m.geom_bodyid[c.geom1]
            fw = fw if b2 != 0 else -fw
            F += fw
            if m.body(wb).name in ("fl", "rl"):
                inner += f6[0]
        Rm = d.xmat[car].reshape(3, 3)
        vb = Rm.T @ d.qvel[0:3]
        ay = (Rm.T @ F)[1] / P["m"]
        rec = (d.time, v, ay, inner, -vb[1], d.subtree_com[car][2])
        recs.append(rec)
        if stop and stop(rec):
            return rec
    r = np.array([x for x in recs if x[0] > T - avg])
    return r.mean(axis=0)


# ---------------------------------------------------------------- 28.2 G1：零力矩点与线性倒立摆
FLOOR = '<geom name="floor" type="plane" size="20 20 .1"/>'


def g1_model():
    return mj_load(mjcf_text("g1", world=FLOOR))


def g1_stand():
    """G1 的“站立”关键帧：总质量、质心、两只脚底接触小球的中心（地面坐标系）与半径。"""
    import mujoco
    m, d = g1_model()
    mujoco.mj_resetDataKeyframe(m, d, 0)
    mujoco.mj_forward(m, d)
    soles = {"left": [], "right": []}
    for g in range(m.ngeom):
        bn = m.body(m.geom_bodyid[g]).name
        if m.geom_type[g] == mujoco.mjtGeom.mjGEOM_SPHERE and bn.endswith("ankle_roll_link"):
            soles["left" if bn.startswith("left") else "right"].append(d.geom_xpos[g].copy())
            r = float(m.geom_size[g][0])
    return dict(m=float(m.body_subtreemass[1]), com=d.subtree_com[1].copy(),
                soles={k: np.array(v) for k, v in soles.items()}, r=r)


def g1_sway(A, B=-0.02, f=0.8, T=6.0, t_avg=2.0):
    """MuJoCo：G1 站立，两个踝关节俯仰按 B + A sin(2πft) 摆动、髋关节俯仰反向，使身体整体前后摆（踝策略）。
    每步记录：质心、质心速度、对质心的角动量（mj_subtreeVel），以及地面接触力的合力与压力中心。
    返回 t、压力中心 x、按式 (28.2.3) 由质心运动和角动量算出的零力矩点、线性倒立摆的近似 x − z ẍ/𝔤、质心 x、是否摔倒。
    质心加速度与角动量变化率用前向差商（MuJoCo 每一步 v_{k+1} = v_k + h a_k，所以与这一步的接触力严格对应）。"""
    import mujoco
    m, d = g1_model()
    mujoco.mj_resetDataKeyframe(m, d, 0)
    ctrl0 = d.ctrl.copy()
    ia = {m.actuator(i).name: i for i in range(m.nu)}
    M = float(m.body_subtreemass[1])
    floor = m.geom("floor").id
    f6 = np.zeros(6)
    rec = []
    while d.time < T:
        th = (B + A * math.sin(2 * math.pi * f * d.time)) * min(d.time / 1.0, 1.0)
        d.ctrl[:] = ctrl0
        for s in ("left", "right"):
            d.ctrl[ia[f"{s}_ankle_pitch_joint"]] = th
            d.ctrl[ia[f"{s}_hip_pitch_joint"]] = -th
        mujoco.mj_step(m, d)
        mujoco.mj_subtreeVel(m, d)
        F, Mo = np.zeros(3), np.zeros(3)
        for i in range(d.ncon):
            c = d.contact[i]
            if floor not in (c.geom1, c.geom2):
                continue
            mujoco.mj_contactForce(m, d, i, f6)
            fw = c.frame.reshape(3, 3).T @ f6[:3]
            if c.geom1 != floor:
                fw = -fw
            F += fw
            Mo += np.cross(c.pos, fw)
        cop = -Mo[1] / F[2] if F[2] > 1e-6 else float("nan")
        rec.append((d.time, *d.subtree_com[1], *d.subtree_linvel[1], *d.subtree_angmom[1], cop))
    r = np.array(rec)
    t, c, v, L, cop = r[:, 0], r[:, 1:4], r[:, 4:7], r[:, 7:10], r[:, 10]
    h = t[1] - t[0]
    acc = np.diff(v, axis=0) / h
    Ld = np.diff(L, axis=0) / h
    c, t, cop = c[:-1], t[:-1], cop[:-1]
    zmp = c[:, 0] - (c[:, 2] * acc[:, 0] + Ld[:, 1] / M) / (acc[:, 2] + G)
    lip = c[:, 0] - c[:, 2] * acc[:, 0] / G
    fell = bool(c[:, 2].min() < 0.5)
    sl = t > t_avg
    return t[sl], cop[sl], zmp[sl], lip[sl], c[sl, 0], fell


def lip_bounded(p, dt, w):
    """线性倒立摆 ẍ = ω²(x − p) 在 p(t) 给定时唯一的有界解：x(t) = (ω/2)∫ e^{−ω|t−s|} p(s) ds（定理 28.2.2）。
    p 按等间隔 dt 取样（把前后两端的值延长到无穷）；用两次一阶递推（向前、向后各一次）精确计算分段线性 p 的卷积。"""
    n = len(p)
    e = math.exp(-w * dt)
    # 对分段线性的 p，一步内的积分 ∫_0^dt ω e^{−ω(dt−s)} p(s) ds 的精确系数
    c0 = 1 - (1 - e) / (w * dt)               # 乘 p_{k+1}
    c1 = (1 - e) / (w * dt) - e               # 乘 p_k
    fwd = np.empty(n)
    bwd = np.empty(n)
    fwd[0] = p[0]
    for k in range(1, n):
        fwd[k] = e * fwd[k - 1] + c1 * p[k - 1] + c0 * p[k]
    bwd[-1] = p[-1]
    for k in range(n - 2, -1, -1):
        bwd[k] = e * bwd[k + 1] + c1 * p[k + 1] + c0 * p[k]
    return (fwd + bwd) / 2


# ---------------------------------------------------------------- 28.3 四旋翼 X2
RHO_AIR = 1.225              # 空气密度（x2.xml 的 <option density>），kg/m³
EZ = np.array([0.0, 0.0, 1.0])


def x2_params():
    """由网页版 x2.xml 读出：质量、质心（机体坐标系）、对质心的惯量张量（机体坐标轴）、以质心为原点的旋翼位置、
    反扭矩系数 c 与方向、推力上限、旋翼半径（旋翼碰撞椭球的半径）。"""
    import mujoco
    m, d = mj_load(mjcf_text("x2"))
    b = m.body("x2").id
    Rp = quat2R(m.body_iquat[b])
    J = Rp @ np.diag(m.body_inertia[b]) @ Rp.T          # 对质心、沿机体坐标轴的惯量张量
    com = m.body_ipos[b].copy()
    r, sig = [], []
    for i in range(4):
        s = m.site(f"thrust{i + 1}").id
        r.append(m.site_pos[s] - com)
        sig.append(int(np.sign(m.actuator_gear[i][5])))
    c = abs(float(m.actuator_gear[0][5]))
    R_rot = float(m.geom_size[m.geom("rotor1").id][0])
    return dict(m=float(m.body_mass[b]), com=com, J=J, r=r, sig=sig, c=c, fmax=float(m.actuator_ctrlrange[0][1]),
                R_rot=R_rot, hover=float(m.key_ctrl[0][0]), principal=m.body_inertia[b].copy(), Rp=Rp)


def x2_alloc(P):
    """4×4 推力分配矩阵：(f, m_x, m_y, m_z) = A (f_1, …, f_4)，与式 (21.1.6) 相同；A6 为力旋量 (m_b, f_b)。"""
    A6 = np.zeros((6, 4))
    for i, (ri, si) in enumerate(zip(P["r"], P["sig"])):
        A6[0:3, i] = np.cross(ri, EZ) + si * P["c"] * EZ
        A6[3:6, i] = EZ
    return np.vstack([A6[5], A6[0], A6[1], A6[2]]), A6


def eul(psi, th, phi):
    return rotz(psi) @ roty(th) @ rotx(phi)


def Wmat(phi, th):
    """ω_b = W(φ, θ) (φ̇, θ̇, ψ̇)（式 (16.2.x)，与 21.4 节相同）。"""
    return np.array([[1, 0, -math.sin(th)],
                     [0, math.cos(phi), math.sin(phi) * math.cos(th)],
                     [0, -math.sin(phi), math.cos(phi) * math.cos(th)]])


def attitude(zb, psi):
    """定理 21.2.1：由推力方向 z_b 和偏航角 ψ 求 R。"""
    yc = np.array([-math.sin(psi), math.cos(psi), 0.0])
    xb = np.cross(yc, zb)
    xb /= np.linalg.norm(xb)
    yb = np.cross(zb, xb)
    R = np.column_stack([xb, yb, zb])
    w = rotz(psi).T @ zb
    phi = math.atan2(-w[1], math.hypot(w[0], w[2]))
    th = math.atan2(w[0], w[2])
    return R, th, phi


def flat(d, psi, dpsi, ddpsi, m):
    """微分平坦映射（21.4 节，与 ch21/code/_uav.py 相同）：d = [p, ṗ, p̈, p⃛, p⁽⁴⁾] →
    姿态 R、总推力 f、物体角速度 ω_b、物体角加速度 ω̇_b。"""
    a, j, s = d[2], d[3], d[4]
    t = a + G * EZ
    nt = np.linalg.norm(t)
    f = m * nt
    zb = t / nt
    R, th, phi = attitude(zb, psi)
    xb, yb = R[:, 0], R[:, 1]
    P = np.eye(3) - np.outer(zb, zb)
    h = P @ j / nt
    wx, wy = -yb @ h, xb @ h
    wz = (math.cos(th) * dpsi - math.sin(phi) * wy) / math.cos(phi)
    w = np.array([wx, wy, wz])
    rates = np.linalg.solve(Wmat(phi, th), w)
    dnt = zb @ j
    dP = -(np.outer(h, zb) + np.outer(zb, h))
    dh = (dP @ j + P @ s) / nt - P @ j * dnt / nt ** 2
    dxb = R @ np.cross(w, [1, 0, 0])
    dyb = R @ np.cross(w, [0, 1, 0])
    dwx = -(dyb @ h + yb @ dh)
    dwy = dxb @ h + xb @ dh
    dphi, dth = rates[0], rates[1]
    num = math.cos(th) * dpsi - math.sin(phi) * wy
    dnum = -math.sin(th) * dth * dpsi + math.cos(th) * ddpsi - math.cos(phi) * dphi * wy - math.sin(phi) * dwy
    dwz = (dnum * math.cos(phi) + num * math.sin(phi) * dphi) / math.cos(phi) ** 2
    return dict(R=R, f=f, w=w, dw=np.array([dwx, dwy, dwz]), th=th, phi=phi)


def fig8(t, Ax=2.0, Ay=1.0, w8=0.8, h8=1.5):
    """算例 21.4.1 的“8”字形：p(t) = (A_x sin ωt, A_y sin 2ωt, h) 及其 1～4 阶导数。"""
    res = []
    for r in range(5):
        dx = Ax * w8 ** r * math.sin(w8 * t + r * math.pi / 2)
        dy = Ay * (2 * w8) ** r * math.sin(2 * w8 * t + r * math.pi / 2)
        res.append(np.array([dx, dy, h8 if r == 0 else 0.0]))
    return res


def x2_state(P, p_c, v_c, R, w_b):
    """由质心的位置、速度，姿态与物体角速度，给出 MuJoCo 自由关节的 qpos、qvel（qvel 的线速度是机体原点的、在 {s} 中；角速度在 {b} 中）。"""
    o = p_c - R @ P["com"]
    v_o = v_c + R @ np.cross(w_b, -P["com"])
    return np.concatenate([o, R2quat(R)]), np.concatenate([v_o, w_b])


# ---------------------------------------------------------------- 28.4 浮动基座：Go2
def go2_model(gravity=True):
    m, d = mj_load(mjcf_text("go2", world=FLOOR))
    if not gravity:
        m.opt.gravity[:] = 0
    return m, d


GO2_HOME = np.array([0, 0.9, -1.8] * 4)          # go2.xml 关键帧 home 的关节角（髋、大腿、小腿 × 左前、右前、左后、右后）


def go2_feet(m, d):
    """四个足端小球（FL、FR、RL、RR）的 geom 编号。"""
    return [m.geom(n).id for n in ("FL", "FR", "RL", "RR")]


def go2_contacts(m, d, feet, torque=False):
    """每只脚受地面的力（{s} 中，三维）与作用点；torque=True 时另返回每只脚受的接触力偶（go2.xml 的足端 condim = 6，
    有扭转摩擦和滚动摩擦）。"""
    import mujoco
    f6 = np.zeros(6)
    F = np.zeros((4, 3))
    Tq = np.zeros((4, 3))
    pos = np.zeros((4, 3))
    floor = m.geom("floor").id
    for i in range(d.ncon):
        c = d.contact[i]
        if floor not in (c.geom1, c.geom2):
            continue
        g = c.geom2 if c.geom1 == floor else c.geom1
        if g not in feet:
            continue
        k = feet.index(g)
        mujoco.mj_contactForce(m, d, i, f6)
        fw = c.frame.reshape(3, 3).T @ f6[:3]
        tw = c.frame.reshape(3, 3).T @ f6[3:]
        if c.geom1 != floor:
            fw, tw = -fw, -tw
        F[k] += fw
        Tq[k] += tw
        pos[k] = c.pos
    return (F, pos, Tq) if torque else (F, pos)


def go2_pd(m, d, q_ref, kp=60.0, kd=2.0):
    """关节 PD：τ = kp(q* − q) − kd q̇，按电机的力矩上限（go2.xml 的 ctrlrange）截断。"""
    q, qd = d.qpos[7:19], d.qvel[6:18]
    tau = kp * (q_ref - q) - kd * qd
    lo, hi = m.actuator_ctrlrange[:, 0], m.actuator_ctrlrange[:, 1]
    d.ctrl[:] = np.clip(tau, lo, hi)
    return tau
