"""第 14 章共用：旋量与矩阵指数、读取零件库模型、三类帕登-卡汉子问题、各台机器人的解析逆运动学。
以下划线开头，构建时不单独运行。

旋量、矩阵指数和零件库模型的读法与第 12 章的 _poe.py 相同，这里重写一份，使本章程序自成一体：
- 关节表在 models/<模型>/entry.json，连杆矩阵在 default.glb（网页三维实验显示的就是它）；
- 模型的正运动学按三维引擎的做法计算：子连杆位姿 = 父连杆位姿 · 节点矩阵 · 绕关节轴转 θ。
这是与指数积公式、与本章逆解都无关的另一种算法，逆解求出的每一组关节角都拿它来核对。
"""
import json
import math
import struct
from pathlib import Path

import numpy as np

MODELS = Path(__file__).resolve().parents[2] / "models"
TWO_PI = 2 * math.pi


# ---------------------------------------------------------------- 旋量与指数（第 4、6、12 章的结论）

def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]], dtype=float)


def rot(w, t):
    """罗德里格斯公式 (4.4.5)：绕单位矢量 w 转 t。"""
    K = skew(np.asarray(w, float))
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def screw_revolute(w, q):
    """转动关节的旋量轴 S = (ω, −ω × q)，式 (12.1.3)。"""
    w = np.asarray(w, float)
    return np.r_[w, -np.cross(w, np.asarray(q, float))]


def screw_prismatic(v):
    """移动关节的旋量轴 S = (0, v)，式 (12.1.4)。"""
    return np.r_[np.zeros(3), np.asarray(v, float)]


def exp6(S, t):
    """e^{[S]θ}，式 (12.1.5)。"""
    S = np.asarray(S, float)
    w, v = S[:3], S[3:]
    T = np.eye(4)
    if np.linalg.norm(w) < 1e-12:
        T[:3, 3] = v * t
        return T
    K = skew(w)
    T[:3, :3] = rot(w, t)
    G = np.eye(3) * t + (1 - math.cos(t)) * K + (t - math.sin(t)) * K @ K
    T[:3, 3] = G @ v
    return T


def inv(T):
    R, p = T[:3, :3], T[:3, 3]
    o = np.eye(4)
    o[:3, :3] = R.T
    o[:3, 3] = -R.T @ p
    return o


def fk_space(Slist, M, theta):
    """空间形式的指数积 T = e^{[S1]θ1} ⋯ e^{[Sn]θn} M，式 (12.2.3)。"""
    T = np.eye(4)
    for S, t in zip(Slist, theta):
        T = T @ exp6(S, t)
    return T @ M


def act(T, p):
    """齐次变换作用在点上。"""
    return T[:3, :3] @ np.asarray(p, float) + T[:3, 3]


def wrap(a):
    """角度化到 (−π, π]。"""
    a = math.atan2(math.sin(a), math.cos(a))
    return math.pi if a <= -math.pi + 1e-15 else a


def angdiff(a, b):
    return abs(wrap(a - b))


def same_solution(a, b, tol=1e-6):
    return all(angdiff(x, y) < tol for x, y in zip(a, b))


def pose_err(A, B):
    """两个位姿之差：位置差的长度 (m)、姿态矩阵各元素之差的最大值。"""
    return float(np.linalg.norm(A[:3, 3] - B[:3, 3])), float(np.abs(A[:3, :3] - B[:3, :3]).max())


def clean(x, tol=1e-12):
    x = np.array(x, float)
    x[np.abs(x) < tol] = 0.0
    return x


# ---------------------------------------------------------------- A cos θ + B sin θ = C（式 (11.5.3)、(14.1.4)）

def trig_solve(A, B, C, tol=1e-12):
    """A cos θ + B sin θ = C 的全部解（0、1 或 2 个），用两个 atan2 写成，在两解合一处也不损失精度（式 (14.1.4)）。"""
    rho2 = A * A + B * B
    if rho2 < 1e-300:
        return []
    disc = rho2 - C * C
    if disc < -tol * rho2:
        return []
    s = math.sqrt(max(disc, 0.0))
    base = math.atan2(B, A)
    if s <= tol * math.sqrt(rho2):
        return [wrap(base)]
    d = math.atan2(s, C)
    return [wrap(base + d), wrap(base - d)]


# ---------------------------------------------------------------- 帕登-卡汉子问题（14.3 节）

def sp1(w, r, p, q, tol=1e-9):
    """子问题 1：绕过点 r、方向 w 的轴转 θ，使点 p 到达 q。返回 θ；p 在轴上时返回 None（任意 θ 都行）。
    要求 wᵀ(p − r) = wᵀ(q − r) 且 |u′| = |v′|（式 (14.3.3)）；数据有微小误差时给出最接近的 θ。"""
    w = np.asarray(w, float)
    u, v = np.asarray(p, float) - r, np.asarray(q, float) - r
    up, vp = u - w * (w @ u), v - w * (w @ v)
    if np.linalg.norm(up) < tol:
        return None
    return math.atan2(w @ np.cross(up, vp), up @ vp)


def sp1_ok(w, r, p, q, tol=1e-9):
    """子问题 1 是否有精确解：两个条件 (14.3.3)。"""
    w = np.asarray(w, float)
    u, v = np.asarray(p, float) - r, np.asarray(q, float) - r
    up, vp = u - w * (w @ u), v - w * (w @ v)
    return abs(w @ u - w @ v) < tol and abs(np.linalg.norm(up) - np.linalg.norm(vp)) < tol


def sp2(w1, w2, r, p, q, tol=1e-10):
    """子问题 2：两根轴交于 r，求 (θ1, θ2) 使 e^{[ω1]θ1} e^{[ω2]θ2} p = q（绕 r 转动）。返回 0、1 或 2 组 (θ1, θ2, c)。"""
    w1, w2 = np.asarray(w1, float), np.asarray(w2, float)
    u, v = np.asarray(p, float) - r, np.asarray(q, float) - r
    k = w1 @ w2
    den = k * k - 1.0
    if abs(den) < 1e-12:
        raise ValueError("两根轴平行，子问题 2 不适用")
    a = (k * (w2 @ u) - w1 @ v) / den
    b = (k * (w1 @ v) - w2 @ u) / den
    n = np.cross(w1, w2)
    g2 = (u @ u - a * a - b * b - 2 * a * b * k) / (n @ n)
    if g2 < -tol:
        return []
    gs = [0.0] if g2 <= tol else [math.sqrt(g2), -math.sqrt(g2)]
    out = []
    for g in gs:
        z = a * w1 + b * w2 + g * n
        c = r + z
        t2 = sp1(w2, r, p, c)
        t1 = sp1(w1, r, c, q)
        out.append((0.0 if t1 is None else t1, 0.0 if t2 is None else t2, c))     # 点在轴上：该角任取，取 0
    return out


def sp3(w, r, p, q, delta, tol=1e-12):
    """子问题 3：绕过 r、方向 w 的轴转 θ，使 p 转到离 q 的距离为 δ 处。返回 0、1 或 2 个 θ（式 (14.3.9)）。"""
    w = np.asarray(w, float)
    u, v = np.asarray(p, float) - r, np.asarray(q, float) - r
    up, vp = u - w * (w @ u), v - w * (w @ v)
    d2 = delta * delta - (w @ (np.asarray(p, float) - q)) ** 2
    nu, nv = np.linalg.norm(up), np.linalg.norm(vp)
    if nu < 1e-12 or nv < 1e-12:
        raise ValueError("p 或 q 在轴上，子问题 3 退化")
    t0 = math.atan2(w @ np.cross(up, vp), up @ vp)
    c = (nu * nu + nv * nv - d2) / (2 * nu * nv)
    if c > 1 + tol or c < -1 - tol or d2 < -tol:
        return []
    c = min(1.0, max(-1.0, c))
    s = math.sqrt(max(0.0, 1 - c * c))
    if s < 1e-9:
        return [wrap(t0 + math.atan2(s, c))]
    d = math.atan2(s, c)
    return [wrap(t0 + d), wrap(t0 - d)]


# ---------------------------------------------------------------- 平面 2R、3R 臂（14.2 节）

def ik2r(x, y, l1, l2, tol=1e-12):
    """平面 2R 臂：返回 [(θ1, θ2), ...]，θ2 > 0 的一组在前。
    1 − cos θ2、1 + cos θ2 由式 (14.2.6) 的因式分解直接算出，再用 θ2 = atan2(±sin θ2, cos θ2)，在边界附近也不损失精度。"""
    r = math.hypot(x, y)
    om = (l1 + l2 - r) * (l1 + l2 + r) / (2 * l1 * l2)          # 1 − cos θ2
    op = (r - abs(l1 - l2)) * (r + abs(l1 - l2)) / (2 * l1 * l2)  # 1 + cos θ2
    if om < -tol or op < -tol:
        return []
    om, op = max(om, 0.0), max(op, 0.0)
    c = (op - om) / 2
    s = math.sqrt(om * op)
    out = []
    for sg in ((1.0,) if s <= tol else (1.0, -1.0)):
        t2 = math.atan2(sg * s, c)
        t1 = math.atan2(y, x) - math.atan2(l2 * math.sin(t2), l1 + l2 * math.cos(t2))
        out.append((wrap(t1), t2))
    return out


def ik2r_naive(x, y, l1, l2):
    """教科书上最常见的写法：θ2 = ±arccos(c)，c 由余弦定理直接算出（只用来比较精度）。"""
    c = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2)
    if abs(c) > 1:
        return []
    out = []
    for sg in (1.0, -1.0):
        t2 = sg * math.acos(c)
        t1 = math.atan2(y, x) - math.atan2(l2 * math.sin(t2), l1 + l2 * math.cos(t2))
        out.append((wrap(t1), t2))
    return out


def fk2r(t, l1, l2):
    return np.array([l1 * math.cos(t[0]) + l2 * math.cos(t[0] + t[1]), l1 * math.sin(t[0]) + l2 * math.sin(t[0] + t[1])])


def ik3r(x, y, phi, l1, l2, l3):
    """平面 3R 臂：末端位置 (x, y)、工具朝向 φ。先求腕点，再用 2R，最后 θ3 = φ − θ1 − θ2。"""
    wx, wy = x - l3 * math.cos(phi), y - l3 * math.sin(phi)
    return [(t1, t2, wrap(phi - t1 - t2)) for t1, t2 in ik2r(wx, wy, l1, l2)]


def fk3r(t, l1, l2, l3):
    a1, a2, a3 = t[0], t[0] + t[1], t[0] + t[1] + t[2]
    return np.array([l1 * math.cos(a1) + l2 * math.cos(a2) + l3 * math.cos(a3),
                     l1 * math.sin(a1) + l2 * math.sin(a2) + l3 * math.sin(a3), wrap(a3)])


# ---------------------------------------------------------------- UR5e（表 12.1.1，零件库模型尺寸）

H1, W1, L1, W2, L2, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1
D4 = W1 - W2 + W3                     # 关节 2、3、4 所在平面与基座轴线的距离（DH 参数 d4）
YD = np.array([0, -1.0, 0])
UR_W = [np.array([0, 0, 1.0]), YD, YD, YD, np.array([0, 0, -1.0]), YD]
UR_Q = [np.array([0, 0, H1]), np.array([0, -W1, H1]), np.array([-L1, -W1 + W2, H1]), np.array([-L1 - L2, -W1 + W2, H1]),
        np.array([-L1 - L2, -W1 + W2 - W3, H1]), np.array([-L1 - L2, -W1 + W2 - W3, H1 - H2])]
UR_S = [screw_revolute(w, q) for w, q in zip(UR_W, UR_Q)]
UR_M = np.array([[1.0, 0, 0, -L1 - L2], [0, -1, 0, -W1 + W2 - W3 - W4], [0, 0, -1, H1 - H2], [0, 0, 0, 1]])
P56 = UR_Q[5].copy()                  # 关节 5、6 两轴的交点（零位）：法兰中心沿法线退回 W4


def ur_fk(theta):
    return fk_space(UR_S, UR_M, theta)


def ur_ik(Td, tol=1e-9):
    """UR5e 的解析逆运动学（14.5 节）：指数积 + 子问题。返回 [(θ, 标签)]，标签为 (肩, 腕, 肘) 三个 ±1。

    第 1 步 θ1：腕点 p_w = p − W4·y_b 只受关节 1–4 影响；关节 2、3、4 的轴都平行于 ω2，
               所以 e^{−[S1]θ1} p_w 沿 ω2 的分量恒等于零位时的 D4：x sin θ1 − y cos θ1 = D4（式 (14.5.2)）。
    第 2 步 θ5、θ6：R_g = e^{−[ω1]θ1} R_d R_Mᵀ = Rot(ω2, θ2+θ3+θ4) R5 R6，于是 R5 R6 (R_gᵀ ω2) = ω2：
               对方向矢量用子问题 2（轴 5、6 交于 P56）。
    第 3 步 θ3、θ2、θ4：g = e^{[S2]θ2} e^{[S3]θ3} e^{[S4]θ4} 已知；q4 在轴 4 上，
               |e^{[S3]θ3} q4 − q2| = |g q4 − q2| 是子问题 3，求出 θ3 后 θ2、θ4 各是一次子问题 1。
    """
    Rd, pd = Td[:3, :3], Td[:3, 3]
    pw = pd - W4 * Rd[:, 1]
    sols = []
    for s1, t1 in zip((1, -1), _theta1(pw)):
        E1i = exp6(UR_S[0], -t1)
        Rg = E1i[:3, :3] @ Rd @ UR_M[:3, :3].T
        v = Rg.T @ YD
        for s5, (t5, t6, _) in zip((1, -1), _wrist56(v)):
            for s3, t in zip((1, -1), ur_ik_234(Td, t1, t5, t6)):
                sols.append((np.array([t1, t[0], t[1], t[2], t5, t6]), (s1, s5, s3)))
    return sols


def ur_ik_234(Td, t1, t5, t6):
    """第 3 步：已知 θ1、θ5、θ6，求 (θ2, θ3, θ4)，0、1 或 2 组。"""
    g = exp6(UR_S[0], -t1) @ Td @ inv(UR_M) @ exp6(UR_S[5], -t6) @ exp6(UR_S[4], -t5)
    p4 = act(g, UR_Q[3])
    dl = np.linalg.norm(p4 - UR_Q[1])
    out = []
    for t3 in sp3(UR_W[2], UR_Q[2], UR_Q[3], UR_Q[1], dl):
        a = act(exp6(UR_S[2], t3), UR_Q[3])
        t2 = sp1(UR_W[1], UR_Q[1], a, p4)
        h = inv(exp6(UR_S[2], t3)) @ inv(exp6(UR_S[1], t2)) @ g
        t4 = sp1(UR_W[3], UR_Q[3], UR_Q[5], act(h, UR_Q[5]))
        out.append((t2, t3, t4))
    return out


def _theta1(pw):
    x, y = pw[0], pw[1]
    rho = math.hypot(x, y)
    if rho < D4 - 1e-12:
        return []
    base, d = math.atan2(x, -y), math.atan2(math.sqrt(max(0.0, rho * rho - D4 * D4)), D4)
    return [wrap(base + d), wrap(base - d)]


def _wrist56(v):
    """R5 R6 v = ω2：子问题 2 用在方向上（以 P56 为公共点）。只返回两组；sin θ5 = 0 时 θ6 任取 0。"""
    c5 = float(np.clip(v @ YD, -1, 1))
    if abs(abs(c5) - 1) < 1e-12:
        return [(0.0 if c5 > 0 else math.pi, 0.0, None)] * 2
    out = sp2(UR_W[4], UR_W[5], P56, P56 + v, P56 + YD)
    out = [(wrap(a), wrap(b), c) for a, b, c in out]
    out.sort(key=lambda x: -x[0])          # θ5 > 0 的一组在前
    return out


# 厂家式（标准 DH，取模型尺寸）的另一种解法：Hawkins (2013) 的公式，用来与本章的解法互相核对
UR_DH = [(0.0, H1, math.pi / 2), (-L1, 0.0, 0.0), (-L2, 0.0, 0.0), (0.0, D4, math.pi / 2), (0.0, H2, -math.pi / 2), (0.0, W4, 0.0)]
RX90 = np.array([[1.0, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])     # DH 末端坐标系绕自身 x 轴转 +90° 得到 {b}（12.3.3 节）


def dh_A(i, th):
    a, d, al = UR_DH[i]
    ct, st, ca, sa = math.cos(th), math.sin(th), math.cos(al), math.sin(al)
    return np.array([[ct, -st * ca, st * sa, a * ct], [st, ct * ca, -ct * sa, a * st], [0, sa, ca, d], [0, 0, 0, 1]])


def ur_fk_dh(q):
    T = np.eye(4)
    for i in range(6):
        T = T @ dh_A(i, q[i])
    return T


def ur_ik_dh(T):
    """Hawkins (2013) 的 UR 逆解，T 为 DH 末端坐标系的目标位姿。"""
    d6, a2, a3 = W4, -L1, -L2
    sols = []
    p05 = T @ np.array([0, 0, -d6, 1.0])
    r = math.hypot(p05[0], p05[1])
    if r < D4:
        return sols
    psi, phi = math.atan2(p05[1], p05[0]), math.acos(D4 / r)
    for t1 in (psi + phi + math.pi / 2, psi - phi + math.pi / 2):
        T16 = inv(dh_A(0, t1)) @ T
        c5 = (T16[2, 3] - D4) / d6
        if abs(c5) > 1:
            continue
        for t5 in (math.acos(c5), -math.acos(c5)):
            T61 = inv(T16)
            s5 = math.sin(t5)
            t6 = 0.0 if abs(s5) < 1e-12 else math.atan2(-T61[1, 2] / s5, T61[0, 2] / s5)
            T14 = T16 @ inv(dh_A(5, t6)) @ inv(dh_A(4, t5))
            p13 = (T14 @ np.array([0, -D4, 0, 1.0]))[:3]
            n = np.linalg.norm(p13)
            c3 = (n * n - a2 * a2 - a3 * a3) / (2 * a2 * a3)
            if abs(c3) > 1:
                continue
            for t3 in (math.acos(c3), -math.acos(c3)):
                t2 = -math.atan2(p13[1], -p13[0]) + math.asin(a3 * math.sin(t3) / n)
                T34 = inv(dh_A(2, t3)) @ inv(dh_A(1, t2)) @ T14
                t4 = math.atan2(T34[1, 0], T34[0, 0])
                sols.append(np.array([wrap(x) for x in (t1, t2, t3, t4, t5, t6)]))
    return sols


# ---------------------------------------------------------------- 球形手腕的六轴臂（14.4 节）

# 取 UR5e 的肩高、大臂、小臂和腕长，去掉全部侧向偏距，腕部三轴交于一点：皮珀准则的典型结构
SW = {"H1": 0.163, "L1": 0.425, "L2": 0.392, "D6": 0.1}
_xh, _yd = np.array([1.0, 0, 0]), np.array([0, -1.0, 0])
SW_W = [np.array([0, 0, 1.0]), _yd, _yd, _xh, _yd, _xh]
SW_PW = np.array([SW["L1"] + SW["L2"], 0, SW["H1"]])             # 腕心（零位）
SW_Q = [np.zeros(3), np.array([0, 0, SW["H1"]]), np.array([SW["L1"], 0, SW["H1"]]), SW_PW, SW_PW, SW_PW]
SW_S = [screw_revolute(w, q) for w, q in zip(SW_W, SW_Q)]
SW_M = np.eye(4)
SW_M[:3, 3] = SW_PW + np.array([SW["D6"], 0, 0])


def sw_fk(theta):
    return fk_space(SW_S, SW_M, theta)


def sw_ik(Td):
    """球形手腕六轴臂的逆解：腕心定位置（子问题 3 + 子问题 2），腕部定姿态（子问题 2 + 子问题 1）。返回 [(θ, 标签)]。"""
    g = Td @ inv(SW_M)
    pw = act(g, SW_PW)                                       # 关节 4、5、6 不动腕心
    q2 = SW_Q[1]
    sols = []
    for s3, t3 in zip((1, -1), sp3(SW_W[2], SW_Q[2], SW_PW, q2, np.linalg.norm(pw - q2))):
        a = act(exp6(SW_S[2], t3), SW_PW)
        for s1, (t1, t2, _) in zip((1, -1), sp2(SW_W[0], SW_W[1], q2, a, pw)):
            h = inv(exp6(SW_S[2], t3)) @ inv(exp6(SW_S[1], t2)) @ inv(exp6(SW_S[0], t1)) @ g   # = e^{S4θ4} e^{S5θ5} e^{S6θ6}
            ptool = SW_PW + np.array([0.0, 0.0, 0.1])            # 轴 6 以外的点（不在轴 4、5 上的方向）
            p6 = SW_PW + np.array([0.1, 0, 0])                   # 轴 6 上的点：不受 θ6 影响
            for s5, (t4, t5, _) in zip((1, -1), sp2(SW_W[3], SW_W[4], SW_PW, p6, act(h, p6))):
                k = inv(exp6(SW_S[4], t5)) @ inv(exp6(SW_S[3], t4)) @ h
                t6 = sp1(SW_W[5], SW_PW, ptool, act(k, ptool))
                sols.append((np.array([wrap(t1), wrap(t2), wrap(t3), wrap(t4), wrap(t5), wrap(t6)]), (s1, s3, s5)))
    return sols


# ---------------------------------------------------------------- SCARA（零件库 B-SCA-WQ4）与 Delta（B-PAR-DELTA）

SC = {"L1": 0.35, "L2": 0.25, "H": 0.4, "dz": 0.048 - 0.206}     # 立柱高、两臂长；工具连杆原点比关节 2 的平面低 0.158 m（零位）


def scara_ik(x, y, z, phi, z0):
    """SCARA：(x, y) 由关节 1、2 的平面 2R 决定，z 由丝杠（向下为正）决定，φ = θ1 + θ2 + θ4。z0 为零位时工具点高度。"""
    out = []
    for t1, t2 in ik2r(x, y, SC["L1"], SC["L2"]):
        out.append(np.array([t1, t2, z0 - z, wrap(phi - t1 - t2)]))
    return out


DELTA = {"Rb": 0.15, "Rp": 0.04, "La": 0.22, "Lb": 0.5}


def delta_ek(k):
    f = TWO_PI * k / 3
    return np.array([math.cos(f), math.sin(f), 0.0])


def delta_elbow(k, th):
    e, D = delta_ek(k), DELTA
    return D["Rb"] * e + D["La"] * (math.cos(th) * e - math.sin(th) * np.array([0, 0, 1.0]))


def delta_leg_sp3(k, p):
    """Delta 第 k 条支链的逆解看作子问题 3：主动臂端点 A_k（零位，水平伸出）绕铰点轴转 θ，
    使它到 P′_k = p + Rp e_k 的距离等于 Lb。θ 向下为正：绕 t_k = ẑ × e_k 转 θ，e_k 转向 −ẑ。"""
    D, e = DELTA, delta_ek(k)
    t = np.cross([0, 0, 1.0], e)
    r = D["Rb"] * e
    A0 = r + D["La"] * e
    return sp3(t, r, A0, p + D["Rp"] * e, D["Lb"])


def delta_leg_trig(k, p):
    """式 (11.5.7) 的写法：A cos θ + B sin θ = C。"""
    D, e = DELTA, delta_ek(k)
    q = p + (D["Rp"] - D["Rb"]) * e
    u, h = q @ e, q[2]
    A, B, C = -2 * D["La"] * u, 2 * D["La"] * h, D["Lb"] ** 2 - D["La"] ** 2 - q @ q
    return trig_solve(A, B, C)


def delta_fk(th):
    """三球求交（式 (11.5.8)），取下方的交点。"""
    D = DELTA
    c = [delta_elbow(k, th[k]) - D["Rp"] * delta_ek(k) for k in range(3)]
    ex = (c[1] - c[0]) / np.linalg.norm(c[1] - c[0])
    i = ex @ (c[2] - c[0])
    ey = c[2] - c[0] - i * ex
    ey /= np.linalg.norm(ey)
    ez = np.cross(ex, ey)
    d = np.linalg.norm(c[1] - c[0])
    j = ey @ (c[2] - c[0])
    x = d / 2
    y = (i * i + j * j - 2 * i * x) / (2 * j)
    z2 = D["Lb"] ** 2 - x * x - y * y
    if z2 < 0:
        return None
    cand = [c[0] + x * ex + y * ey + s * math.sqrt(z2) * ez for s in (1, -1)]
    return min(cand, key=lambda q: q[2])


# ---------------------------------------------------------------- 零件库模型（与第 12 章相同的读法）

def _glb_nodes(path: Path) -> dict:
    b = path.read_bytes()
    n = struct.unpack("<I", b[12:16])[0]
    js = json.loads(b[20:20 + n])
    nodes = {}
    for nd in js["nodes"]:
        m = np.eye(4)
        if "matrix" in nd:
            m = np.array(nd["matrix"], float).reshape(4, 4).T
        elif "translation" in nd or "rotation" in nd:
            raise ValueError("模型节点用了平移/四元数形式，本程序只读矩阵形式")
        nodes[nd.get("name")] = {"m": m, "children": [js["nodes"][c].get("name") for c in nd.get("children", [])]}
    return nodes


class Model:
    """零件库机器人：关节表 + 网页模型的节点矩阵。坐标以 base 连杆的父坐标系（机器人基座坐标系 {s}）表示。"""

    def __init__(self, eid: str, base: str, tool_link: str, tool_xyz=(0, 0, 0), joints=None):
        d = MODELS / eid
        self.entry = json.loads((d / "entry.json").read_text(encoding="utf-8"))
        self.nodes = _glb_nodes(d / "default.glb")
        self.base = base
        self.tool_link, self.tool_xyz = tool_link, np.asarray(tool_xyz, float)
        js = {j["name"]: j for j in self.entry["robot"]["joints"]}
        self.joints = [js[n] for n in (joints or [j["name"] for j in self.entry["robot"]["joints"] if j["type"] != "fixed"])]
        self.by_child = {j["child"]: j for j in self.joints}
        parent = {c: p for p, nd in self.nodes.items() for c in nd["children"]}
        chain, n = [], tool_link
        while n != base:
            chain.insert(0, n)
            n = parent[n]
        self.chain = chain

    def fk(self, theta) -> np.ndarray:
        val = {j["name"]: t for j, t in zip(self.joints, theta)}
        T = self.nodes[self.base]["m"].copy()
        for n in self.chain:
            T = T @ self.nodes[n]["m"]
            j = self.by_child.get(n)
            if j is not None:
                t = val.get(j["name"], 0.0)
                a = np.asarray(j["axis"], float)
                Mj = np.eye(4)
                if j["type"] == "prismatic":
                    Mj[:3, 3] = a * t
                else:
                    Mj[:3, :3] = rot(a / np.linalg.norm(a), t)
                T = T @ Mj
        tool = np.eye(4)
        tool[:3, 3] = self.tool_xyz
        return T @ tool


def ur_model():
    return Model("B-ARM-UR5E", "base", "wrist_3_link", (0, W4, 0))


def scara_model():
    return Model("B-SCA-WQ4", "base", "tool")


# ---------------------------------------------------------------- 数值逆解（只用来清点解的个数，第 15 章详讲）

def logR(R):
    c = max(-1.0, min(1.0, (np.trace(R) - 1) / 2))
    th = math.acos(c)
    if th < 1e-9:
        return np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / 2
    if math.pi - th < 1e-6:
        B = (R + np.eye(3)) / 2
        k = int(np.argmax(np.diag(B)))
        w = B[:, k] / math.sqrt(B[k, k])
        return w * th
    return th / (2 * math.sin(th)) * np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])


def numeric_ik(fk, Td, th0, iters=60, lam=1e-3):
    """阻尼最小二乘（第 7、8 章）：误差 = (姿态误差的指数坐标, 位置误差)，雅可比用差商。收敛返回 θ，否则 None。"""
    th = np.array(th0, float)
    n = len(th)
    for _ in range(iters):
        T = fk(th)
        e = np.r_[logR(T[:3, :3].T @ Td[:3, :3]), T[:3, :3].T @ (Td[:3, 3] - T[:3, 3])]
        if np.linalg.norm(e) < 1e-12:
            return np.array([wrap(x) for x in th])
        J = np.zeros((6, n))
        h = 1e-7
        for i in range(n):
            d = np.zeros(n)
            d[i] = h
            T2 = fk(th + d)
            e2 = np.r_[logR(T2[:3, :3].T @ Td[:3, :3]), T2[:3, :3].T @ (Td[:3, 3] - T2[:3, 3])]
            J[:, i] = (e2 - e) / h
        dth = -np.linalg.solve(J.T @ J + lam * np.eye(n), J.T @ e)
        th = th + dth
    T = fk(th)
    err = pose_err(T, Td)
    return np.array([wrap(x) for x in th]) if err[0] < 1e-10 and err[1] < 1e-10 else None


def distinct(sols, tol=1e-5):
    out = []
    for s in sols:
        if s is not None and not any(same_solution(s, o, tol) for o in out):
            out.append(s)
    return out


def dh_fk_general(params, q):
    """一般 6R 臂的标准 DH 正运动学（第 13 章式 (13.1.x) 的乘积）。params: [(a, d, α)]。"""
    T = np.eye(4)
    for (a, d, al), qi in zip(params, q):
        ct, st, ca, sa = math.cos(qi), math.sin(qi), math.cos(al), math.sin(al)
        T = T @ np.array([[ct, -st * ca, st * sa, a * ct], [st, ct * ca, -ct * sa, a * st], [0, sa, ca, d], [0, 0, 0, 1]])
    return T


def random6r(seed=103, n_start=600):
    """一般几何的 6R 臂：DH 参数随机取（a ∈ [0.1, 0.5] m，d ∈ [−0.3, 0.3] m，α 任意），目标位姿由一组随机关节角算出。
    从 n_start 个随机初值出发用数值法求逆解。返回 (DH 参数, 目标位姿, 每个初值的结果, 各个不同解被找到的次数)。"""
    rng = np.random.default_rng(seed)
    P = [(rng.uniform(0.1, 0.5), rng.uniform(-0.3, 0.3), rng.uniform(-math.pi, math.pi)) for _ in range(6)]
    Td = dh_fk_general(P, rng.uniform(-math.pi, math.pi, 6))
    found = [numeric_ik(lambda q: dh_fk_general(P, q), Td, rng.uniform(-math.pi, math.pi, 6), iters=80) for _ in range(n_start)]
    D = distinct(found)
    hits = [sum(1 for f in found if f is not None and same_solution(f, d, 1e-5)) for d in D]
    return P, Td, found, hits


def ur_elbow_up(s):
    """肘点（关节 3 的中心）是否在肩（关节 2 的中心）—腕（关节 4 的中心）连线的上方（在手臂平面内看）。"""
    E1 = exp6(UR_S[0], s[0])
    E12 = E1 @ exp6(UR_S[1], s[1])
    E123 = E12 @ exp6(UR_S[2], s[2])
    sh, el, wr = act(E1, UR_Q[1]), act(E12, UR_Q[2]), act(E123, UR_Q[3])
    n = np.cross(E1[:3, :3] @ YD, wr - sh)
    n = n if n[2] >= 0 else -n
    return bool((el - sh) @ n > 0)


def ur_ordered(sols):
    """把 ur_ik 的解排成表 14.5.1 的次序：肩 A（式 (14.5.3) 取 + 号）在前，手腕不翻（θ5 > 0）在前，肘上在前。
    返回 [(θ, (肩 "A"/"B", 肘 "up"/"down", 腕不翻 True/False))]。"""
    out = [(s, ("A" if lab[0] > 0 else "B", "up" if ur_elbow_up(s) else "down", lab[1] > 0)) for s, lab in sols]
    out.sort(key=lambda x: (x[1][0], not x[1][2], x[1][1] != "up"))
    return out


def ur_points(theta):
    """UR5e 的连杆折线（用于作图和检查碰地）：基座、关节 1–6 的中心与连杆转折点、法兰中心。"""
    Es = [np.eye(4)]
    for S, t in zip(UR_S, theta):
        Es.append(Es[-1] @ exp6(S, t))
    q = UR_Q
    pts = [(0, np.zeros(3)), (0, q[0]), (1, q[1]), (2, q[1] + np.array([-L1, 0, 0])), (2, q[2]), (3, q[3]),
           (4, q[4]), (5, q[5]), (6, q[5] + np.array([0, -W4, 0]))]
    return np.array([act(Es[k], p) for k, p in pts])
