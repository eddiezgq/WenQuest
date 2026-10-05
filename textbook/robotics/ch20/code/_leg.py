"""第 20 章共用：Go2 一条腿的正逆运动学与足端雅可比、浮动基座、质心、步态与支撑多边形，以及按关节表做 G1 的正运动学、
雅可比与数值逆解。以下划线开头，构建时不单独运行。

数据来源：
- textbook/robotics/models/<编号>/entry.json：零件库条目（关节表、限位、厂家参数表 datasheet）；
- 模型的 MJCF 原文件（MuJoCo Menagerie，提交 4d038b3feae26ec82b46a4d586379114012a8ac7，unitree_go2/go2.xml、
  unitree_g1/g1.xml）中几项不在关节表里的事实：各连杆质心在连杆坐标系中的位置与质量（<inertial pos mass>）、
  Go2 足端小球的半径与位置、G1 脚底四个接触小球的位置、Go2 电机的力矩上限（<motor ctrlrange>），抄在下面并注明出处。
记号与正文一致：{b} 为机身（Go2 的 base、G1 的 pelvis）坐标系，x 向前、y 向左、z 向上；{s} 为地面坐标系，z = 0 为地面。
"""
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
MODELS = HERE.parents[1] / "models"
G = 9.81                                   # 重力加速度 𝔤，m/s²（符号约定第九节）

LEGS = ["FL", "FR", "RL", "RR"]            # 左前、右前、左后、右后
LEG_ZH = {"FL": "左前", "FR": "右前", "RL": "左后", "RR": "右后"}
LEG_EN = {"FL": "front left", "FR": "front right", "RL": "rear left", "RR": "rear right"}


def entry(eid: str) -> dict:
    return json.loads((MODELS / eid / "entry.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- MJCF 中不在关节表里的事实
# go2.xml：<inertial pos=… mass=…>（连杆坐标系中的质心位置，m；质量，kg）
GO2_INERTIAL = {
    "base": ((0.021112, 0.0, -0.005366), 6.921),
    "FL_hip": ((-0.0054, 0.00194, -0.000105), 0.678), "FL_thigh": ((-0.00374, -0.0223, -0.0327), 1.152),
    "FL_calf": ((0.00629595, -0.000622121, -0.141417), 0.241352),
    "FR_hip": ((-0.0054, -0.00194, -0.000105), 0.678), "FR_thigh": ((-0.00374, 0.0223, -0.0327), 1.152),
    "FR_calf": ((0.00629595, 0.000622121, -0.141417), 0.241352),
    "RL_hip": ((0.0054, 0.00194, -0.000105), 0.678), "RL_thigh": ((-0.00374, -0.0223, -0.0327), 1.152),
    "RL_calf": ((0.00629595, -0.000622121, -0.141417), 0.241352),
    "RR_hip": ((0.0054, -0.00194, -0.000105), 0.678), "RR_thigh": ((-0.00374, 0.0223, -0.0327), 1.152),
    "RR_calf": ((0.00629595, 0.000622121, -0.141417), 0.241352),
}
GO2_FOOT_R = 0.022                          # go2.xml <default class="foot"><geom size="0.022" pos="-0.002 0 -0.213">
GO2_FOOT = (0.0, 0.0, -0.213)               # 足端中心取小腿坐标系的 (0, 0, −0.213)，与 1.6 节相同（MJCF 中小球再偏后 2 mm）
GO2_TAU_MAX = {"hip": 23.7, "thigh": 23.7, "calf": 45.43}   # go2.xml <motor ctrlrange>：髋、大腿 ±23.7 N·m，小腿 ±45.43 N·m

# g1.xml：<inertial pos=… mass=…>
G1_INERTIAL = {
    "pelvis": ((0.0, 0.0, -0.07605), 3.813),
    "left_hip_pitch_link": ((0.002741, 0.047791, -0.02606), 1.35), "left_hip_roll_link": ((0.029812, -0.001045, -0.087934), 1.52),
    "left_hip_yaw_link": ((-0.057709, -0.010981, -0.15078), 1.702), "left_knee_link": ((0.005457, 0.003964, -0.12074), 1.932),
    "left_ankle_pitch_link": ((-0.007269, 0.0, 0.011137), 0.074), "left_ankle_roll_link": ((0.026505, 0.0, -0.016425), 0.608),
    "right_hip_pitch_link": ((0.002741, -0.047791, -0.02606), 1.35), "right_hip_roll_link": ((0.029812, 0.001045, -0.087934), 1.52),
    "right_hip_yaw_link": ((-0.057709, 0.010981, -0.15078), 1.702), "right_knee_link": ((0.005457, -0.003964, -0.12074), 1.932),
    "right_ankle_pitch_link": ((-0.007269, 0.0, 0.011137), 0.074), "right_ankle_roll_link": ((0.026505, 0.0, -0.016425), 0.608),
    "waist_yaw_link": ((0.003494, 0.000233, 0.018034), 0.214), "waist_roll_link": ((0.0, 2.3e-05, 0.0), 0.086),
    "torso_link": ((0.00203158, 0.000339683, 0.184568), 7.818),
    "left_shoulder_pitch_link": ((0.0, 0.035892, -0.011628), 0.718), "left_shoulder_roll_link": ((-0.000227, 0.00727, -0.063243), 0.643),
    "left_shoulder_yaw_link": ((0.010773, -0.002949, -0.072009), 0.734), "left_elbow_link": ((0.064956, 0.004454, -0.010062), 0.6),
    "left_wrist_roll_link": ((0.0171394, 0.000537591, 4.8864e-07), 0.085445),
    "left_wrist_pitch_link": ((0.0229999, -0.00111685, -0.00111658), 0.48405),
    "left_wrist_yaw_link": ((0.0708244, 0.000191745, 0.00161742), 0.254576),
    "right_shoulder_pitch_link": ((0.0, -0.035892, -0.011628), 0.718), "right_shoulder_roll_link": ((-0.000227, -0.00727, -0.063243), 0.643),
    "right_shoulder_yaw_link": ((0.010773, 0.002949, -0.072009), 0.734), "right_elbow_link": ((0.064956, -0.004454, -0.010062), 0.6),
    "right_wrist_roll_link": ((0.0171394, -0.000537591, 4.8864e-07), 0.085445),
    "right_wrist_pitch_link": ((0.0229999, 0.00111685, -0.00111658), 0.48405),
    "right_wrist_yaw_link": ((0.0708244, -0.000191745, 0.00161742), 0.254576),
}
# g1.xml：脚底四个接触小球 <geom class="foot" pos=…>（踝横滚连杆坐标系），半径 0.005 m；<site name="left_foot"/> 在该坐标系原点
G1_SOLE = [(-0.05, 0.025, -0.03), (-0.05, -0.025, -0.03), (0.12, -0.03, -0.03), (0.12, 0.03, -0.03)]
G1_SOLE_R = 0.005
G1_PELVIS_Z0 = 0.793                        # g1.xml：<body name="pelvis" pos="0 0 0.793">（腿伸直时骨盆原点的高度）


# ---------------------------------------------------------------- 李群小工具（第 4～6 章）
def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]], float)


def rot_axis(a, t):
    """罗德里格斯公式 (4.4 节)。"""
    a = np.asarray(a, float) / np.linalg.norm(a)
    K = skew(a)
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def rx(t):
    return rot_axis((1, 0, 0), t)


def ry(t):
    return rot_axis((0, 1, 0), t)


def rz(t):
    return rot_axis((0, 0, 1), t)


def rpy(r, p, y):
    """URDF 的 rpy：R = Rot(z, y) Rot(y, p) Rot(x, r)。机身姿态也用它：横滚 φ、俯仰 ϑ、偏航 ψ。"""
    return rz(y) @ ry(p) @ rx(r)


def Tm(R=None, p=(0, 0, 0)):
    T = np.eye(4)
    if R is not None:
        T[:3, :3] = R
    T[:3, 3] = p
    return T


def Tinv(T):
    R, p = T[:3, :3], T[:3, 3]
    return Tm(R.T, -R.T @ p)


def exp_twist(S, th):
    """式 (12.1.5)：旋量轴 S = (ω, v) 转过 th 的 4×4 矩阵指数。"""
    w, v = np.asarray(S[:3], float), np.asarray(S[3:], float)
    n = np.linalg.norm(w)
    if n < 1e-12:
        return Tm(np.eye(3), v * th)
    w, v, th = w / n, v / n, th * n                # 一般的运动旋量先化成单位旋量轴乘转角
    K = skew(w)
    Gm = np.eye(3) * th + (1 - math.cos(th)) * K + (th - math.sin(th)) * K @ K
    return Tm(rot_axis(w, th), Gm @ v)


def log_so3(R):
    c = max(-1.0, min(1.0, (np.trace(R) - 1) / 2))
    t = math.acos(c)
    if t < 1e-12:
        return np.zeros(3)
    return t / (2 * math.sin(t)) * np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])


# ---------------------------------------------------------------- Go2 一条腿
GO2 = entry("B-LEG-GO2")
_J = {j["name"]: j for j in GO2["robot"]["joints"]}
AX = _J["FL_hip_joint"]["origin"]["xyz"][0]        # 0.1934 m：髋关节轴在机身前后方向的位置
AY = _J["FL_hip_joint"]["origin"]["xyz"][1]        # 0.0465 m：髋关节轴的侧向位置
DY = _J["FL_thigh_joint"]["origin"]["xyz"][1]      # 0.0955 m：大腿关节相对髋关节的侧向偏距
L1 = -_J["FL_calf_joint"]["origin"]["xyz"][2]      # 0.213 m：大腿长（大腿关节到小腿关节）
L2 = -GO2_FOOT[2]                                   # 0.213 m：小腿长（小腿关节到足端中心）
REST = GO2["robot"]["rest"]
TH_REST = np.array([REST["FL_hip_joint"], REST["FL_thigh_joint"], REST["FL_calf_joint"]])
SIGN = {"FL": (1, 1), "FR": (1, -1), "RL": (-1, 1), "RR": (-1, -1)}   # (前后 s_x, 左右 s_y)
MASS_GO2 = sum(m for _, m in GO2_INERTIAL.values())


def limits(leg):
    return np.array([[_J[f"{leg}_{k}_joint"]["limit"]["lower"], _J[f"{leg}_{k}_joint"]["limit"]["upper"]] for k in ("hip", "thigh", "calf")])


def hip(leg):
    sx, sy = SIGN[leg]
    return np.array([sx * AX, sy * AY, 0.0])


def leg_fk(leg, th):
    """式 (20.1.5)、(20.1.6)：足端中心在 {b} 中的位置（闭式）。"""
    t1, t2, t3 = th
    sy = SIGN[leg][1]
    xp = -L1 * math.sin(t2) - L2 * math.sin(t2 + t3)
    zp = -L1 * math.cos(t2) - L2 * math.cos(t2 + t3)
    return hip(leg) + np.array([xp, sy * DY * math.cos(t1) - zp * math.sin(t1), sy * DY * math.sin(t1) + zp * math.cos(t1)])


def leg_screws(leg):
    """式 (20.1.2)、(20.1.3)：零位时三个关节在 {b} 中的旋量轴，与足端中心的零位位置 M。"""
    sy = SIGN[leg][1]
    q1 = hip(leg)
    q2 = q1 + np.array([0, sy * DY, 0])
    q3 = q2 + np.array([0, 0, -L1])
    ax, ay = np.array([1.0, 0, 0]), np.array([0, 1.0, 0])
    S = [np.r_[ax, -np.cross(ax, q1)], np.r_[ay, -np.cross(ay, q2)], np.r_[ay, -np.cross(ay, q3)]]
    M = q3 + np.array([0, 0, -L2])
    return S, M, (q1, q2, q3)


def leg_fk_poe(leg, th):
    """指数积公式 (20.1.4)：足端中心 = e^[S1]θ1 e^[S2]θ2 e^[S3]θ3 M。"""
    S, M, _ = leg_screws(leg)
    T = exp_twist(S[0], th[0]) @ exp_twist(S[1], th[1]) @ exp_twist(S[2], th[2])
    return (T @ np.r_[M, 1])[:3]


def leg_jac(leg, th):
    """式 (20.1.12)：足端中心的速度 ṗ = J θ̇（在 {b} 中）。"""
    t1, t2, t3 = th
    sy = SIGN[leg][1]
    xp = -L1 * math.sin(t2) - L2 * math.sin(t2 + t3)
    zp = -L1 * math.cos(t2) - L2 * math.cos(t2 + t3)
    R1 = rx(t1)
    c1 = R1 @ np.array([0.0, -zp, sy * DY])
    c2 = R1 @ np.array([zp, 0.0, -xp])
    c3 = R1 @ np.array([-L2 * math.cos(t2 + t3), 0.0, L2 * math.sin(t2 + t3)])
    return np.column_stack([c1, c2, c3])


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def leg_ik_all(leg, p):
    """定理 20.1.2：全部逆解（最多 4 组）。返回 [(θ, z′ 的符号, θ3 的符号)]；无解返回 []。"""
    sy = SIGN[leg][1]
    r = np.asarray(p, float) - hip(leg)
    rho2 = r[1] ** 2 + r[2] ** 2 - DY ** 2
    if rho2 < 0:
        return []
    out = []
    for zs in (-1, 1):
        zp = zs * math.sqrt(rho2)
        t1 = wrap(math.atan2(r[2], r[1]) - math.atan2(zp, sy * DY))
        xp = r[0]
        c3 = (xp ** 2 + zp ** 2 - L1 ** 2 - L2 ** 2) / (2 * L1 * L2)
        if abs(c3) > 1 + 1e-12:
            continue
        c3 = max(-1.0, min(1.0, c3))
        for ks in (-1, 1):
            t3 = ks * math.acos(c3)
            gam = math.atan2(-xp, -zp)
            t2 = wrap(gam - math.atan2(L2 * math.sin(t3), L1 + L2 * math.cos(t3)))
            out.append((np.array([t1, t2, t3]), zs, ks))
    return out


def in_limits(leg, th, tol=1e-9):
    lim = limits(leg)
    return bool(np.all(th >= lim[:, 0] - tol) and np.all(th <= lim[:, 1] + tol))


def to_limits(leg, th):
    """角度相差 2π 的关节角是同一个位形：大腿关节的范围超过 180°，必要时把 θ2 换成 θ2 ± 2π 再与限位比较。"""
    lim = limits(leg)
    th = np.array(th, float)
    for k in range(3):
        for c in (th[k], th[k] + 2 * math.pi, th[k] - 2 * math.pi):
            if lim[k, 0] - 1e-9 <= c <= lim[k, 1] + 1e-9:
                th[k] = c
                break
    return th


def leg_ik(leg, p, below=True):
    """在 Go2 的关节限位内的解（定理 20.1.3）。below=True 时只取足端在髋外摆轴下方（z′ < 0）的那一组；没有则返回 None。"""
    sols = [to_limits(leg, s) for s, zs, _ in leg_ik_all(leg, p) if (zs < 0 or not below)]
    sols = [s for s in sols if in_limits(leg, s)]
    return sols[0] if sols else None


# ---------------------------------------------------------------- 按关节表做正运动学（Go2、G1 通用）
def joint_table(e):
    js = [j for j in e["robot"]["joints"] if j["type"] in ("revolute", "continuous", "prismatic")]
    return js


def fk_links(e, q, T_sb=None):
    """各连杆坐标系在 {s} 中的位姿（关节表的写法：平移、RPY、绕轴转）。q：{关节名: 角}。"""
    root = e["robot"]["links"][0]["name"]
    T = {root: np.eye(4) if T_sb is None else np.asarray(T_sb, float)}
    js = joint_table(e)
    pending = list(js)
    while pending:
        rest = []
        for j in pending:
            if j["parent"] not in T:
                rest.append(j)
                continue
            o = j["origin"]
            Tj = T[j["parent"]] @ Tm(rpy(*o["rpy"]), o["xyz"]) @ Tm(rot_axis(j["axis"], q.get(j["name"], 0.0)))
            T[j["child"]] = Tj
        pending = rest
    return T


def joint_axes(e, q, T_sb=None):
    """各关节轴在 {s} 中的方向与轴上一点（用于几何雅可比）。"""
    Tl = fk_links(e, q, T_sb)
    out = {}
    for j in joint_table(e):
        Tc = Tl[j["child"]]
        out[j["name"]] = (Tc[:3, :3] @ np.asarray(j["axis"], float), Tc[:3, 3].copy(), j["child"])
    return out, Tl


def com(e, inertial, q, T_sb=None):
    """质心在 {s}（或 T_sb 缺省时在 {b}）中的位置，式 (20.4.1)。"""
    Tl = fk_links(e, q, T_sb)
    m_tot, s = 0.0, np.zeros(3)
    for name, (c, m) in inertial.items():
        s += m * (Tl[name] @ np.r_[c, 1])[:3]
        m_tot += m
    return s / m_tot, m_tot


def go2_q(th12):
    """四条腿的 12 个关节角（按 FL、FR、RL、RR，各为 髋、大腿、小腿）→ 关节名字典。"""
    q = {}
    for i, leg in enumerate(LEGS):
        for k, nm in enumerate(("hip", "thigh", "calf")):
            q[f"{leg}_{nm}_joint"] = float(th12[3 * i + k])
    return q


# ---------------------------------------------------------------- 浮动基座（20.2 节）
def stance_ik(T_sb, feet_s):
    """机身位姿 T_sb 给定、四只脚在 {s} 中的位置给定，求 12 个关节角（每条腿各解一次逆运动学）。"""
    Ti = Tinv(T_sb)
    th = []
    for leg in LEGS:
        pb = (Ti @ np.r_[feet_s[leg], 1])[:3]
        s = leg_ik(leg, pb)
        th.append(s if s is not None else np.full(3, np.nan))
    return np.concatenate(th)


def body_from_feet(feet_b, feet_s):
    """定理 20.2.4：由脚在 {b} 与 {s} 中的位置求机身位姿（点集配准，4.8 节的正交化）。"""
    A = np.array([feet_b[k] for k in feet_b])
    B = np.array([feet_s[k] for k in feet_b])
    ca, cb = A.mean(0), B.mean(0)
    H = (B - cb).T @ (A - ca)
    U, _, Vt = np.linalg.svd(H)
    R = U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt
    return Tm(R, cb - R @ ca)


# ---------------------------------------------------------------- 支撑多边形（20.4 节）
def hull(pts):
    """平面点集的凸包（单调链算法），逆时针。"""
    P = sorted(set((round(float(x), 12), round(float(y), 12)) for x, y in pts))
    if len(P) <= 2:
        return np.array(P)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in P:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(P):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return np.array(lo[:-1] + up[:-1])


def margin(poly, c):
    """静态稳定裕度（定义 20.4.4）：质心投影 c 到支撑多边形各边的最短距离，在多边形内为正、外为负。
    多边形退化为线段或点时，内部为空，裕度取 −(到它的距离)。"""
    c = np.asarray(c, float)[:2]
    P = np.asarray(poly, float)
    if len(P) < 3:
        if len(P) == 1:
            return -float(np.linalg.norm(c - P[0]))
        a, b = P[0], P[1]
        t = np.clip((c - a) @ (b - a) / ((b - a) @ (b - a)), 0, 1)
        return -float(np.linalg.norm(c - (a + t * (b - a))))
    d = []
    inside = True
    for k in range(len(P)):
        a, b = P[k], P[(k + 1) % len(P)]
        e = b - a
        n = np.array([e[1], -e[0]]) / np.linalg.norm(e)      # 逆时针多边形的外法向
        s = (c - a) @ n
        if s > 0:
            inside = False
        d.append(-s)
    if inside:
        return float(min(d))
    best = 1e9                                                # 在外面：到多边形边界的距离
    for k in range(len(P)):
        a, b = P[k], P[(k + 1) % len(P)]
        t = np.clip((c - a) @ (b - a) / ((b - a) @ (b - a)), 0, 1)
        best = min(best, float(np.linalg.norm(c - (a + t * (b - a)))))
    return -best


# ---------------------------------------------------------------- 步态（20.3 节）
GAITS = {   # 各腿的相位 φ_i（以左后腿 RL 落地为 0，单位为周期）与典型占地系数 β
    "walk": ({"RL": 0.0, "FL": 0.25, "RR": 0.5, "FR": 0.75}, 0.75),
    "trot": ({"RL": 0.0, "FR": 0.0, "FL": 0.5, "RR": 0.5}, 0.5),
    "pace": ({"RL": 0.0, "FL": 0.0, "RR": 0.5, "FR": 0.5}, 0.5),
    "bound": ({"RL": 0.0, "RR": 0.0, "FL": 0.5, "FR": 0.5}, 0.4),
    "gallop": ({"RL": 0.0, "RR": 0.1, "FL": 0.5, "FR": 0.6}, 0.3),
    "pronk": ({"RL": 0.0, "RR": 0.0, "FL": 0.0, "FR": 0.0}, 0.4),
}


def in_stance(phase, t, tc, beta):
    """t 时刻，相位为 phase 的腿是否处于支撑相；返回 (是否支撑, 在本相中的归一化时间 τ ∈ [0, 1))。"""
    u = (t / tc - phase) % 1.0
    if u < beta:
        return True, u / beta
    return False, (u - beta) / (1 - beta)


def swing_profile(tau):
    """式 (20.3.8)：摆线型摆动轨迹的水平进度 s(τ) ∈ [0, 1] 与高度系数 h(τ) ∈ [0, 1]。"""
    return tau - math.sin(2 * math.pi * tau) / (2 * math.pi), (1 - math.cos(2 * math.pi * tau)) / 2


# ---------------------------------------------------------------- 爬行步态的静态稳定裕度（20.4 节）
def crawl_min_margin(beta, A, v=0.1, tc=2.0, hs=0.05, n=400, ret=False):
    """爬行步态（后左、前左、后右、前右）一个周期内的最小静态稳定裕度（算例 20.4.3）。机身匀速前进 v，侧摆 y_b = −A cos(2πt/t_c)，
    高度、姿态不变；支撑脚落在中性点（髋前方 ℓ/2）后在 {s} 中不动，摆动脚按式 (20.3.8)。ret=True 时同时返回过程。"""
    h0 = -leg_fk("FL", TH_REST)[2] + GO2_FOOT_R
    ph = GAITS["walk"][0]
    Ls, ell = v * tc, v * beta * tc
    out_t, out_m, out_c, out_poly, out_feet = [], [], [], [], []
    best = 1e9
    for k in range(n):
        t = tc * k / n
        xb = v * t
        yb = -A * math.cos(2 * math.pi * t / tc)        # 左腿摆动（t/t_c ∈ [0.75, 1.25)）时机身偏右，右腿摆动时偏左
        Tb = Tm(np.eye(3), (xb, yb, h0))
        feet, stance = {}, []
        for leg in LEGS:
            st, tau = in_stance(ph[leg], t, tc, beta)
            # t_td：最近一次落地的时刻；足端落在髋前方 ℓ/2（中性点），之后在 {s} 中不动，摆动时移向下一个落脚点 x0 + L_s
            u = (t / tc - ph[leg]) % 1.0
            t_td = t - u * tc                            # 本周期落地时刻
            hipw = np.array([leg_fk(leg, TH_REST)[0], leg_fk(leg, TH_REST)[1]])
            if st:
                x = hipw[0] + v * t_td + ell / 2
                feet[leg] = np.array([x, hipw[1], GO2_FOOT_R])
                stance.append(leg)
            else:
                s, hz = swing_profile(tau)
                x0 = hipw[0] + v * t_td + ell / 2        # 上一次的落脚点
                feet[leg] = np.array([x0 + Ls * s, hipw[1], GO2_FOOT_R + hs * hz])
        th = stance_ik(Tb, feet)
        assert not np.any(np.isnan(th)), "crawl: a foot is out of reach"
        c = com(GO2, GO2_INERTIAL, go2_q(th), Tb)[0]
        poly = hull(np.array([feet[l][:2] for l in stance]))
        mg = margin(poly, c[:2])
        best = min(best, mg)
        if ret:
            out_t.append(t), out_m.append(mg), out_c.append(c[:2]), out_poly.append(poly), out_feet.append({l: feet[l].copy() for l in LEGS})
    if ret:
        return best, (out_t, out_m, out_c, out_poly, out_feet)
    return best



# ---------------------------------------------------------------- G1：关节表、腿的数值逆解与全身逆运动学（20.5 节）
G1 = entry("B-HUM-G1")
G1_JOINTS = [j["name"] for j in joint_table(G1)]
G1_LIM = {j["name"]: (j["limit"]["lower"], j["limit"]["upper"]) for j in joint_table(G1)}
G1_REST = dict(G1["robot"]["rest"])
LEG_JOINTS = {s: [f"{s}_hip_pitch_joint", f"{s}_hip_roll_joint", f"{s}_hip_yaw_joint", f"{s}_knee_joint",
                  f"{s}_ankle_pitch_joint", f"{s}_ankle_roll_joint"] for s in ("left", "right")}
MASS_G1 = sum(m for _, m in G1_INERTIAL.values())


def g1_point_jac(q, T_sb, link, pt, names):
    """连杆 link 上一点（连杆坐标系中的 pt）在 {s} 中的位置，以及它对 names 中各关节角的雅可比（3×k）。"""
    ax, Tl = joint_axes(G1, q, T_sb)
    p = (Tl[link] @ np.r_[pt, 1])[:3]
    anc = set()
    node = link
    parent = {j["child"]: (j["parent"], j["name"]) for j in joint_table(G1)}
    while node in parent:
        anc.add(parent[node][1])
        node = parent[node][0]
    J = np.zeros((3, len(names)))
    for k, n in enumerate(names):
        if n in anc:
            w, o, _ = ax[n]
            J[:, k] = np.cross(w, p - o)
    return p, J


def g1_frame_jac(q, T_sb, link, names):
    """连杆坐标系的位姿与几何雅可比（6×k，上三行角速度、下三行原点线速度，均在 {s} 中，16.2 节）。"""
    ax, Tl = joint_axes(G1, q, T_sb)
    T = Tl[link]
    p = T[:3, 3]
    anc = set()
    node = link
    parent = {j["child"]: (j["parent"], j["name"]) for j in joint_table(G1)}
    while node in parent:
        anc.add(parent[node][1])
        node = parent[node][0]
    J = np.zeros((6, len(names)))
    for k, n in enumerate(names):
        if n in anc:
            w, o, _ = ax[n]
            J[:3, k] = w
            J[3:, k] = np.cross(w, p - o)
    return T, J


def pose_err(T, Td):
    """位姿误差：（姿态误差 log(R_d R^T)，位置误差 p_d − p），均在 {s} 中。"""
    return np.r_[log_so3(Td[:3, :3] @ T[:3, :3].T), Td[:3, 3] - T[:3, 3]]


def g1_leg_ik(side, T_sb, T_foot, q0=None, tol=1e-12, itmax=50):
    """G1 一条腿的数值逆解：牛顿-拉夫森迭代（15.1 节），6 个关节、6 维位姿。返回 (q 字典, 迭代次数, 误差)。"""
    names = LEG_JOINTS[side]
    q = dict(G1_REST if q0 is None else q0)
    if abs(q[names[3]]) < 0.05:                     # 初值：膝稍弯（腿伸直是奇异位形，牛顿法不能从那里出发）
        q.update({names[0]: -0.2, names[3]: 0.4, names[4]: -0.2})
    link = f"{side}_ankle_roll_link"
    for it in range(itmax):
        T, J = g1_frame_jac(q, T_sb, link, names)
        e = pose_err(T, T_foot)
        if np.linalg.norm(e) < tol:
            return q, it, float(np.linalg.norm(e))
        if np.linalg.cond(J) < 1e6:
            dq = np.linalg.solve(J, e)
        else:                                       # 接近奇异时改用阻尼最小二乘（15.3 节）
            dq = J.T @ np.linalg.solve(J @ J.T + 1e-4 * np.eye(6), e)
        for k, n in enumerate(names):
            q[n] += dq[k]
    T, _ = g1_frame_jac(q, T_sb, link, names)
    return q, itmax, float(np.linalg.norm(pose_err(T, T_foot)))


def g1_sole_world(q, T_sb, side):
    Tl = fk_links(G1, q, T_sb)
    T = Tl[f"{side}_ankle_roll_link"]
    return np.array([(T @ np.r_[np.array(p) + np.array([0, 0, -G1_SOLE_R]), 1])[:3] for p in G1_SOLE])


def g1_stand_height():
    """腿伸直、全部关节取零位、脚底水平时，骨盆原点离地的高度（脚底接触点在 z = 0）。"""
    Tl = fk_links(G1, {}, Tm(np.eye(3), (0, 0, 0)))
    z_sole = (Tl["left_ankle_roll_link"] @ np.r_[0, 0, G1_SOLE[0][2] - G1_SOLE_R, 1])[2]
    return -z_sole


# ---------------------------------------------------------------- G1 全身逆运动学：浮动基座 6 个变量 + 29 个关节，按优先级逐级投影（15.4 节）
G1_PARENT = {j["child"]: (j["parent"], j["name"]) for j in joint_table(G1)}


def _ancestors(link):
    s, n = set(), link
    while n in G1_PARENT:
        s.add(G1_PARENT[n][1])
        n = G1_PARENT[n][0]
    return s


G1_ANC = {l: _ancestors(l) for l in list(G1_INERTIAL) + ["right_wrist_yaw_link"]}
G1_HAND = np.array([0.08, 0.0, 0.0])        # 设：手心取右腕偏航连杆坐标系中的 (0.08, 0, 0) m


def wb_point_jac(ax, T_sb, p, link):
    """点 p（{s} 中）随广义速度 (ω, v_o, θ̇) 的雅可比：机身以角速度 ω 绕自身原点转、原点以 v_o 平移（式 (20.5.5)）。"""
    nq = len(G1_JOINTS)
    J = np.zeros((3, 6 + nq))
    J[:, 0:3] = -skew(p - T_sb[:3, 3])
    J[:, 3:6] = np.eye(3)
    for k, n in enumerate(G1_JOINTS):
        if n in G1_ANC[link]:
            w, o, _ = ax[n]
            J[:, 6 + k] = np.cross(w, p - o)
    return J


def wb_frame_jac(ax, T_sb, T, link):
    nq = len(G1_JOINTS)
    J = np.zeros((6, 6 + nq))
    p = T[:3, 3]
    J[:3, 0:3] = np.eye(3)
    J[3:, 0:3] = -skew(p - T_sb[:3, 3])
    J[3:, 3:6] = np.eye(3)
    for k, n in enumerate(G1_JOINTS):
        if n in G1_ANC[link]:
            w, o, _ = ax[n]
            J[:3, 6 + k] = w
            J[3:, 6 + k] = np.cross(w, p - o)
    return J


def wb_com_jac(ax, Tl, T_sb):
    """质心与质心雅可比（式 (20.4.2)）：各连杆质心的点雅可比按质量加权平均。"""
    m_tot, c = 0.0, np.zeros(3)
    J = np.zeros((3, 6 + len(G1_JOINTS)))
    for name, (cc, m) in G1_INERTIAL.items():
        p = (Tl[name] @ np.r_[cc, 1])[:3]
        c += m * p
        J += m * wb_point_jac(ax, T_sb, p, name)
        m_tot += m
    return c / m_tot, J / m_tot


def dls(J, e, lam):
    return J.T @ np.linalg.solve(J @ J.T + lam ** 2 * np.eye(J.shape[0]), e)


def g1_whole_body(target, T_sb0, q0, T_fl, T_fr, c_goal=None, its=400, tol=1e-12):
    """任务按优先级：(1) 两脚位姿不变；(2) 质心水平投影到 c_goal（None 则不要求）；(3) 手心到 target；(4) 关节回到站姿附近。
    每一步按式 (20.5.3)、(20.5.4) 逐级在前面任务的零空间里求解（阻尼最小二乘），关节到限位时锁住重解。返回 (T_sb, q, 记录)。"""
    nq = len(G1_JOINTS)
    T_sb, q = T_sb0.copy(), dict(q0)
    qr = np.array([G1_REST[n] for n in G1_JOINTS])
    Jp = np.zeros((nq, 6 + nq))
    Jp[:, 6:] = np.eye(nq)
    hist = []
    for it in range(its):
        ax, Tl = joint_axes(G1, q, T_sb)
        Tl_, Tr_ = Tl["left_ankle_roll_link"], Tl["right_ankle_roll_link"]
        J1 = np.vstack([wb_frame_jac(ax, T_sb, Tl_, "left_ankle_roll_link"), wb_frame_jac(ax, T_sb, Tr_, "right_ankle_roll_link")])
        e1 = np.r_[pose_err(Tl_, T_fl), pose_err(Tr_, T_fr)]
        c, Jc = wb_com_jac(ax, Tl, T_sb)
        ph = (Tl["right_wrist_yaw_link"] @ np.r_[G1_HAND, 1])[:3]
        Jh = wb_point_jac(ax, T_sb, ph, "right_wrist_yaw_link")
        e3 = target - ph
        e2 = (c_goal - c[:2]) if c_goal is not None else np.zeros(2)
        hist.append((float(np.linalg.norm(e1)), float(np.linalg.norm(e2)), float(np.linalg.norm(e3))))
        if hist[-1][0] < tol and hist[-1][1] < tol and hist[-1][2] < tol and it > 5:
            break
        qv = np.array([q[n] for n in G1_JOINTS])
        tasks = [(J1, e1, 1e-4)]
        if c_goal is not None:
            tasks.append((Jc[:2], e2, 1e-4))
        tasks += [(Jh, 0.5 * e3, 1e-3), (Jp, 0.1 * (qr - qv), 1e-2)]
        lock = np.zeros(6 + nq, bool)
        for _ in range(10):
            S = np.diag((~lock).astype(float))
            dx, N = np.zeros(6 + nq), S.copy()
            for J, e, lam in tasks:
                JN = J @ N
                dx = dx + N @ dls(JN, e - J @ dx, lam)
                N = N - np.linalg.pinv(JN, rcond=1e-6) @ JN
            again = False
            for k, n in enumerate(G1_JOINTS):
                lo, hi = G1_LIM[n]
                if not lock[6 + k] and not (lo - 1e-12 <= q[n] + dx[6 + k] <= hi + 1e-12):
                    lock[6 + k] = again = True
            if not again:
                break
        w = dx[:3]
        R = rot_axis(w, np.linalg.norm(w)) @ T_sb[:3, :3] if np.linalg.norm(w) > 1e-15 else T_sb[:3, :3]
        T_sb = Tm(R, T_sb[:3, 3] + dx[3:6])
        for k, n in enumerate(G1_JOINTS):
            lo, hi = G1_LIM[n]
            q[n] = min(hi, max(lo, q[n] + dx[6 + k]))
    return T_sb, q, hist
