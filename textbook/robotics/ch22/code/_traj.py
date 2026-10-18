"""第 22 章共用：轨迹规划。以下划线开头，构建时不单独运行。

前半部分是第 16 章的共用代码（旋量、矩阵指数与对数、伴随矩阵、雅可比矩阵及其时间导数、UR5e 的旋量轴（表 12.1.1）
与解析逆解（14.5 节）、零件库模型的读法），原样抄来，使本章程序自成一体；
后半部分（“第 22 章”起）是本章新加的：点到点的多项式、梯形与 S 形速度曲线、样条与抛物线过渡、
笛卡尔直线与圆弧、SO(3)/SE(3) 上的插值、沿给定路径的时间最优参数化，以及 UR5e 上下料工位的数据（示意值）。
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


def distinct(sols, tol=1e-5):
    out = []
    for s in sols:
        if s is not None and not any(same_solution(s, o, tol) for o in out):
            out.append(s)
    return out


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


# ---------------------------------------------------------------- 李群上的对数、伴随与物体雅可比（第 6、12 章；15.1 节）

def vee(X):
    """se(3) 中的 4×4 矩阵 [V] → 六维矢量 V = (ω, v)。"""
    return np.array([X[2, 1], X[0, 2], X[1, 0], X[0, 3], X[1, 3], X[2, 3]])


def bracket(V):
    """六维矢量 V = (ω, v) → 4×4 矩阵 [V]（式 (6.3.6)）。"""
    m = np.zeros((4, 4))
    m[:3, :3] = skew(V[:3])
    m[:3, 3] = V[3:]
    return m


def exp_twist(V):
    """e^{[V]}，V 是任意六维矢量（不必是单位旋量）：定理 6.4.1。"""
    V = np.asarray(V, float)
    w = V[:3]
    th = float(np.linalg.norm(w))
    if th < 1e-12:
        T = np.eye(4)
        T[:3, 3] = V[3:]
        return T
    return exp6(V / th, th)


def log_twist(T):
    """SE(3) 的对数映射（定理 6.4.3）：返回六维矢量 V = Sθ，使 e^{[V]} = T。转角取 [0, π]。"""
    R, p = T[:3, :3], T[:3, 3]
    wth = logR(R)
    th = float(np.linalg.norm(wth))
    if th < 1e-12:
        return np.r_[np.zeros(3), p]
    w = wth / th
    K = skew(w)
    Ginv = np.eye(3) / th - 0.5 * K + (1 / th - 0.5 / math.tan(th / 2)) * K @ K      # 式 (6.4.8)
    return np.r_[wth, th * (Ginv @ p)]


def adjoint(T):
    """[Ad_T]，式 (6.5.4)。"""
    R, p = T[:3, :3], T[:3, 3]
    A = np.zeros((6, 6))
    A[:3, :3] = R
    A[3:, 3:] = R
    A[3:, :3] = skew(p) @ R
    return A


def ad(V):
    """[ad_V]，式 (6.7.5)。"""
    A = np.zeros((6, 6))
    A[:3, :3] = skew(V[:3])
    A[3:, 3:] = skew(V[:3])
    A[3:, :3] = skew(V[3:])
    return A


def fk_body(Blist, M, theta):
    """物体形式的指数积 T = M e^{[B1]θ1} ⋯ e^{[Bn]θn}，式 (12.2.5)。"""
    T = M.copy()
    for B, t in zip(Blist, theta):
        T = T @ exp6(B, t)
    return T


def jacobian_body(Blist, theta):
    """物体雅可比（式 (15.1.4)）：第 n 列为 Bn，第 i 列为 [Ad_{e^{−[B_n]θ_n} ⋯ e^{−[B_{i+1}]θ_{i+1}}}] B_i。"""
    n = len(theta)
    J = np.zeros((6, n))
    T = np.eye(4)
    for i in range(n - 1, -1, -1):
        J[:, i] = adjoint(T) @ Blist[i]
        T = T @ exp6(Blist[i], -theta[i])
    return J


def jacobian_space(Slist, theta):
    """空间雅可比：第 1 列为 S1，第 i 列为 [Ad_{e^{[S_1]θ_1} ⋯ e^{[S_{i−1}]θ_{i−1}}}] S_i（第 16 章）。"""
    n = len(theta)
    J = np.zeros((6, n))
    T = np.eye(4)
    for i in range(n):
        J[:, i] = adjoint(T) @ Slist[i]
        T = T @ exp6(Slist[i], theta[i])
    return J


def body_screws(Slist, M):
    """B_i = [Ad_{M^{-1}}] S_i，式 (12.2.8)。"""
    A = adjoint(inv(M))
    return [A @ S for S in Slist]


UR_B = body_screws(UR_S, UR_M)


def ur_jb(theta):
    return jacobian_body(UR_B, theta)


def err_twist(T, Td):
    """物体坐标系中的位姿误差旋量 V_b = log(T⁻¹ T_d)（定义 15.1.1）。"""
    return log_twist(inv(T) @ Td)


def ur_labels(theta):
    """一组 UR5e 关节角的三个标签：肩（式 (14.5.4) 取 + 号为 A）、肘（肘点在肩—腕连线上方为上）、腕（θ5 > 0 为不翻）。"""
    th = np.asarray(theta, float)
    T = ur_fk(th)
    pw = T[:3, 3] - W4 * T[:3, 1]
    t1s = _theta1(pw)
    sh = "A" if t1s and angdiff(th[0], t1s[0]) < angdiff(th[0], t1s[1]) else "B"
    el = "up" if ur_elbow_up(th) else "down"
    return sh, el, math.sin(th[4]) > 0


def ur_solution_index(theta, sols_ordered, tol=1e-6):
    """在表 14.5.1 的 8 组解中找到与 θ 相同的一组（各关节角相差 2π 的整数倍视为相同），返回编号 1–8；找不到返回 0。"""
    for i, s in enumerate(sols_ordered, 1):
        if same_solution(theta, s, tol):
            return i
    return 0


# ---------------------------------------------------------------- 平面臂（UR5e 侧视：大臂、小臂与腕段；14.2 节）

PL = (0.425, 0.392, 0.1)


def fk_planar(th, L=PL):
    """平面 nR 臂末端的位置与朝向 (x, y, φ)。"""
    a = np.cumsum(th)
    return np.array([np.sum(np.asarray(L) * np.cos(a)), np.sum(np.asarray(L) * np.sin(a)), a[-1]])


def joints_planar(th, L=PL, base=(0.0, 0.0)):
    a = np.cumsum(th)
    pts = [np.array(base, float)]
    for l, t in zip(L, a):
        pts.append(pts[-1] + l * np.array([math.cos(t), math.sin(t)]))
    return np.array(pts)


def jac_planar(th, L=PL):
    """平面 nR 臂末端位置的雅可比（2×n）：第 i 列是 ẑ × (p − p_i)。"""
    pts = joints_planar(th, L)
    p = pts[-1]
    J = np.zeros((2, len(th)))
    for i in range(len(th)):
        d = p - pts[i]
        J[:, i] = [-d[1], d[0]]
    return J


def se2(x, y, phi):
    c, s = math.cos(phi), math.sin(phi)
    return np.array([[c, -s, x], [s, c, y], [0, 0, 1.0]])


def log_se2(T):
    """SE(2) 的对数：返回 (φ, v_x, v_y)，e^{[V]} = T（平面转动绕极点，6.1.3 节）。"""
    phi = math.atan2(T[1, 0], T[0, 0])
    p = T[:2, 2]
    if abs(phi) < 1e-12:
        return np.array([0.0, p[0], p[1]])
    # e^{[V]} 的平移部分为 A v，A = (sin φ I + (1 − cos φ) J)/φ，J 为逆时针转 90°
    A = np.array([[math.sin(phi), -(1 - math.cos(phi))], [1 - math.cos(phi), math.sin(phi)]]) / phi
    v = np.linalg.solve(A, p)
    return np.array([phi, v[0], v[1]])


def exp_se2(V):
    phi, vx, vy = V
    if abs(phi) < 1e-12:
        return se2(vx, vy, 0.0)
    A = np.array([[math.sin(phi), -(1 - math.cos(phi))], [1 - math.cos(phi), math.sin(phi)]]) / phi
    p = A @ np.array([vx, vy])
    return se2(p[0], p[1], phi)


def planar_pose(th, L=PL):
    x, y, phi = fk_planar(th, L)
    return se2(x, y, phi)


def jb_planar(th, L=PL):
    """平面 nR 臂的物体雅可比（3×n，行次序 ω、v_x、v_y，在末端坐标系中表示）。"""
    x, y, phi = fk_planar(th, L)
    pts = joints_planar(th, L)
    c, s = math.cos(phi), math.sin(phi)
    J = np.zeros((3, len(th)))
    for i in range(len(th)):
        d = pts[-1] - pts[i]
        vs = np.array([-d[1], d[0]])                 # 末端原点的速度（{s} 中），ω = 1
        J[:, i] = [1.0, c * vs[0] + s * vs[1], -s * vs[0] + c * vs[1]]
    return J


# ---------------------------------------------------------------- 本章算例共用的数据

TH_STAR = np.radians([30, -60, 90, -120, -90, 45])          # 算例 12.3.1、14.5.1 的关节角：目标位姿由它算出
TH_CUR = np.radians([25, -55, 85, -115, -85, 40])           # 14.5.7 节“当前关节角”
TH_HOME = np.radians([0, -90, 90, -90, -90, 0])             # 常用的起始姿态（大臂竖直、小臂水平、法兰朝下）


def ur_target():
    return ur_fk(TH_STAR)


def ur_table():
    """表 14.5.1 的 8 组解（次序：肩 A 在前、腕不翻在前、肘上在前）。"""
    return [s for s, _ in ur_ordered(ur_ik(ur_target()))]


# ---------------------------------------------------------------- Panda（七轴，零件库 B-ARM-PANDA）

def panda():
    """返回 (fk, jb, 下限, 上限, ready 姿态)。旋量轴由零件库模型读出（与第 12 章相同）。"""
    pa = Model("B-ARM-PANDA", "link0", "hand", (0, 0, 0), [f"joint{i}" for i in range(1, 8)])
    lo = np.array([j["limit"]["lower"] for j in pa.joints])
    hi = np.array([j["limit"]["upper"] for j in pa.joints])
    S, T = [], pa.nodes[pa.base]["m"].copy()
    for n in pa.chain:
        T = T @ pa.nodes[n]["m"]
        j = pa.by_child.get(n)
        if j is None:
            continue
        S.append(screw_revolute(T[:3, :3] @ np.asarray(j["axis"], float), T[:3, 3]))
    M = pa.fk(np.zeros(7))
    B = body_screws(S, M)
    ready = np.array([0, -math.pi / 4, 0, -3 * math.pi / 4, 0, math.pi / 2, math.pi / 4])
    return (lambda q: fk_space(S, M, q)), (lambda q: jacobian_body(B, q)), lo, hi, ready, pa




# ---------------------------------------------------------------- 第 16 章新加的部分

def jacobian_space_dot(Slist, theta, dtheta):
    """空间雅可比对时间的导数（定理 16.1.3）：J̇_si = [ad_{Σ_{j<i} J_sj θ̇_j}] J_si。"""
    J = jacobian_space(Slist, theta)
    Jd = np.zeros_like(J)
    acc = np.zeros(6)
    for i in range(J.shape[1]):
        Jd[:, i] = ad(acc) @ J[:, i]
        acc = acc + J[:, i] * dtheta[i]
    return Jd


def jacobian_body_dot(Blist, theta, dtheta):
    """物体雅可比对时间的导数：J̇_bi = [ad_{J_bi}] Σ_{j>i} J_bj θ̇_j。"""
    J = jacobian_body(Blist, theta)
    n = J.shape[1]
    Jd = np.zeros_like(J)
    for i in range(n):
        acc = sum((J[:, j] * dtheta[j] for j in range(i + 1, n)), np.zeros(6))
        Jd[:, i] = ad(J[:, i]) @ acc
    return Jd


def ur_js(theta):
    return jacobian_space(UR_S, theta)


def ur_jg(theta):
    """几何雅可比（定义 16.2.1）：行为 (ω_s, ṗ)，ṗ 是法兰盘中心的速度，都在 {s} 中表示。J_g = [[I, 0], [−[p], I]] J_s。"""
    p = ur_fk(theta)[:3, 3]
    P = np.eye(6)
    P[3:, :3] = -skew(p)
    return P @ ur_js(theta)


def ur_wrist_point(theta):
    """手腕点 P56（关节 5、6 两轴的交点）此刻的位置。"""
    T = np.eye(4)
    for S, t in zip(UR_S[:4], theta[:4]):
        T = T @ exp6(S, t)
    return act(T, P56)


def ur_det_factors(theta):
    """UR5e 雅可比行列式的三个因子（定理 16.3.3）：sin θ3、sin θ5，以及手腕点到“过基座轴线、垂直于手臂平面的竖直平面”的带号距离 r。"""
    pw = ur_wrist_point(theta)
    c1, s1 = math.cos(theta[0]), math.sin(theta[0])
    # 手臂平面内的水平方向 x′ = Rot(z, θ1) x̂；r = x′ · p_w
    r = c1 * pw[0] + s1 * pw[1]
    return math.sin(theta[2]), math.sin(theta[4]), r


def ur_det(theta):
    return float(np.linalg.det(ur_js(theta)))


def ur_shoulder_r(theta):
    """r 的关节角表达式（式 (16.3.4)）：r = −L1 cos θ2 − L2 cos(θ2 + θ3) + H2 sin(θ2 + θ3 + θ4)。"""
    t2, t3, t4 = theta[1], theta[2], theta[3]
    return -L1 * math.cos(t2) - L2 * math.cos(t2 + t3) + H2 * math.sin(t2 + t3 + t4)


def rotz(a):
    return rot([0, 0, 1.0], a)


def roty(a):
    return rot([0, 1.0, 0], a)


def rotx(a):
    return rot([1.0, 0, 0], a)


def euler_zyx(R):
    """ZYX 欧拉角 (α, β, γ)：R = Rot(ẑ, α) Rot(ŷ, β) Rot(x̂, γ)（与 4.5 节的 (ψ, θ, φ) 相同，β ∈ [−π/2, π/2]）。"""
    b = math.asin(max(-1.0, min(1.0, -R[2, 0])))
    a = math.atan2(R[1, 0], R[0, 0])
    g = math.atan2(R[2, 1], R[2, 2])
    return np.array([a, b, g])


def R_zyx(e):
    return rotz(e[0]) @ roty(e[1]) @ rotx(e[2])


def B_zyx(e):
    """ZYX 欧拉角速率到空间角速度：ω_s = B(α, β) η̇（式 (16.2.7)）。"""
    a, b = e[0], e[1]
    return np.array([[0, -math.sin(a), math.cos(a) * math.cos(b)],
                     [0, math.cos(a), math.sin(a) * math.cos(b)],
                     [1, 0, -math.sin(b)]])


def A_exp(r):
    """指数坐标速率到空间角速度：ω_s = A(r) ṙ，A = I + (1 − cos φ)/φ² [r] + (φ − sin φ)/φ³ [r]²（定理 16.2.4）。"""
    r = np.asarray(r, float)
    ph = float(np.linalg.norm(r))
    K = skew(r)
    if ph < 1e-8:
        return np.eye(3) + 0.5 * K + K @ K / 6
    return np.eye(3) + (1 - math.cos(ph)) / ph ** 2 * K + (ph - math.sin(ph)) / ph ** 3 * K @ K


def jac_2r(th, L=(0.425, 0.392)):
    """平面 2R 臂末端位置的雅可比（式 (7.3.9)）。"""
    l1, l2 = L
    s1, c1, s12, c12 = math.sin(th[0]), math.cos(th[0]), math.sin(th[0] + th[1]), math.cos(th[0] + th[1])
    return np.array([[-l1 * s1 - l2 * s12, -l2 * s12], [l1 * c1 + l2 * c12, l2 * c12]])


def svals(J):
    return np.linalg.svd(J, compute_uv=False)


def manip(J):
    """可操作度 w = √det(J Jᵀ)（定义 2.4.4）。"""
    return float(math.sqrt(max(0.0, np.linalg.det(J @ J.T))))


def num_jac_space(fk, theta, h=1e-6):
    """空间雅可比的差商：第 i 列 = log(T(θ + h e_i) T(θ − h e_i)⁻¹)/(2h)。"""
    n = len(theta)
    J = np.zeros((6, n))
    for i in range(n):
        d = np.zeros(n)
        d[i] = h
        J[:, i] = log_twist(fk(theta + d) @ inv(fk(theta - d))) / (2 * h)
    return J


def num_jac_body(fk, theta, h=1e-6):
    n = len(theta)
    J = np.zeros((6, n))
    for i in range(n):
        d = np.zeros(n)
        d[i] = h
        J[:, i] = log_twist(inv(fk(theta - d)) @ fk(theta + d)) / (2 * h)
    return J


# ---------------------------------------------------------------- 算例 16.2.3 的路径

def gimbal_path(delta_deg=1.0, w_deg=20.0, dur=9.0, dt=0.005):
    """算例 16.2.3：UR5e 从 θ* 出发，法兰盘中心不动，以 w_deg °/s 绕一根水平轴转动 dur 秒；转轴为 z_b 向 x_b 偏 δ。
    返回各时刻的欧拉角、欧拉角速率、指数坐标速率、关节速度、J_g 的最小奇异值、法兰盘中心和关节角。"""
    th = TH_STAR.copy()
    R = ur_fk(th)[:3, :3]
    d = math.radians(delta_deg)
    u = R @ np.array([math.sin(d), 0, math.cos(d)])             # 转轴：z_b 向 x_b 偏 δ，此刻水平
    w = math.radians(w_deg) * u
    f = lambda q: np.linalg.solve(ur_jg(q), np.r_[w, 0, 0, 0])
    q = th.copy()
    H = {"t": [], "eta": [], "etad": [], "rd": [], "qd": [], "smin": [], "p": [], "q": []}
    n = int(round(dur / dt))
    for k in range(n + 1):
        Tq = ur_fk(q)
        e = euler_zyx(Tq[:3, :3])
        H["t"].append(k * dt)
        H["eta"].append(e)
        H["etad"].append(np.linalg.solve(B_zyx(e), w))
        H["rd"].append(np.linalg.solve(A_exp(logR(Tq[:3, :3])), w))
        H["qd"].append(f(q))
        H["smin"].append(svals(ur_jg(q))[-1])
        H["p"].append(Tq[:3, 3])
        H["q"].append(q.copy())
        if k < n:
            k1 = f(q)
            k2 = f(q + dt / 2 * k1)
            k3 = f(q + dt / 2 * k2)
            k4 = f(q + dt * k3)
            q = q + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return {k: np.array(v) for k, v in H.items()}, u


# ---------------------------------------------------------------- 16.4～16.6 节共用

TAU_MAX = np.array([150.0, 150.0, 150.0, 28.0, 28.0, 28.0])     # UR5e 各关节的最大力矩（N·m，厂商资料，16.5 节）


def ur_jv(theta):
    """几何雅可比的后三行：法兰盘中心的线速度对关节速度（3×6）。"""
    return ur_jg(theta)[3:]


def ur_jw(theta):
    """几何雅可比的前三行：角速度对关节速度（3×6），与 J_s 的前三行相同。"""
    return ur_js(theta)[:3]


def ellipsoid(J):
    """{J θ̇ : ‖θ̇‖ ≤ 1} 的半轴（从大到小）与方向（列）：J = U Σ Vᵀ，半轴 σ_i u_i（定理 16.4.1）。"""
    U, s, _ = np.linalg.svd(J)
    m = J.shape[0]
    s = np.r_[s, np.zeros(max(0, m - len(s)))][:m]
    return s, U


def held_ellipsoid(theta):
    """姿态保持不变（ω = 0）时，法兰盘中心能达到的线速度 {ṗ : ‖J_g⁻¹ (0, ṗ)‖ ≤ 1}：半轴与方向（定理 16.4.2）。"""
    G = np.linalg.inv(ur_jg(theta))[:, 3:]
    _, s, Vt = np.linalg.svd(G)
    order = np.argsort(1 / s)[::-1]
    return (1 / s)[order], Vt.T[:, order]


def trans_ratio(J, u):
    """速度传递比 α(u) = (uᵀ (J Jᵀ)⁻¹ u)^{-1/2}：单位关节速度沿单位方向 u 能产生的最大末端速度（定义 16.4.3）。"""
    u = np.asarray(u, float) / np.linalg.norm(u)
    return float(1 / math.sqrt(u @ np.linalg.solve(J @ J.T, u)))


def force_ratio(J, u):
    """力传递比 β(u) = (uᵀ J Jᵀ u)^{-1/2}：单位关节力矩沿单位方向 u 能平衡的最大末端力（定义 16.5.2）。"""
    u = np.asarray(u, float) / np.linalg.norm(u)
    return float(1 / math.sqrt(u @ (J @ J.T) @ u))


def kappa(J):
    s = svals(J)
    return float(s[0] / s[-1]) if s[-1] > 0 else float("inf")


def ur_closest(Td, prev):
    """UR5e 的 8 组解析解中离 prev 最近的一组（各角之差按 (−π, π] 计）；目标够不着时返回 None。"""
    sols = [s for s, _ in ur_ik(Td)]
    if not sols:
        return None
    return min(sols, key=lambda s: float(np.linalg.norm([wrap(a - b) for a, b in zip(s, prev)])))


def ur_radial(rhos, start=None):
    """16.4 节的径向路径：法兰盘姿态与高度保持 θ* 时的值，中心沿过 θ* 的那条水平射线（从基座轴线出发）移动，
    到基座轴线的水平距离为 ρ。从 θ* 出发向两侧延拓，每一步取离上一步最近的解析解（第 14 章），保证同一支。
    返回与 rhos 等长的关节角数组；够不着处为 nan。"""
    T0 = ur_fk(TH_STAR if start is None else start)
    p0 = T0[:3, 3]
    az = math.atan2(p0[1], p0[0])
    rho0 = math.hypot(p0[0], p0[1])
    rhos = np.asarray(rhos, float)
    out = np.full((len(rhos), 6), np.nan)
    for side in (1, -1):
        idx = [i for i in np.argsort(rhos)[::side] if (rhos[i] - rho0) * side >= 0]
        prev, last = TH_STAR.copy(), rho0
        for i in idx:
            # 细分步长，保证延拓不跳支
            n = max(1, int(abs(rhos[i] - last) / 0.002))
            ok = True
            for r in np.linspace(last, rhos[i], n + 1)[1:]:
                T = T0.copy()
                T[:3, 3] = [r * math.cos(az), r * math.sin(az), p0[2]]
                q = ur_closest(T, prev)
                if q is None:
                    ok = False
                    break
                prev = q
            if not ok:
                break
            out[i], last = prev, rhos[i]
    return out


def ur_radial_point(rho):
    p0 = ur_fk(TH_STAR)[:3, 3]
    az = math.atan2(p0[1], p0[0])
    return np.array([rho * math.cos(az), rho * math.sin(az), p0[2]])


def panda_screws():
    """Panda 的空间旋量轴 S_i、零位位姿 M 与各关节在零位时的轴上一点（由零件库模型读出，同 panda()）。"""
    pa = Model("B-ARM-PANDA", "link0", "hand", (0, 0, 0), [f"joint{i}" for i in range(1, 8)])
    S, Q, W, T = [], [], [], pa.nodes[pa.base]["m"].copy()
    for n in pa.chain:
        T = T @ pa.nodes[n]["m"]
        j = pa.by_child.get(n)
        if j is None:
            continue
        w = T[:3, :3] @ np.asarray(j["axis"], float)
        S.append(screw_revolute(w, T[:3, 3]))
        W.append(w)
        Q.append(T[:3, 3].copy())
    return S, pa.fk(np.zeros(7)), W, Q, pa


PANDA_READY = np.array([0, -math.pi / 4, 0, -3 * math.pi / 4, 0, math.pi / 2, math.pi / 4])


def ur_down(rho, z, az=None):
    """16.6 节：法兰盘保持 θ* 的姿态（竖直朝下）、中心到基座轴线的水平距离 ρ、高度 z 时的逆解（与 θ* 同一支）。
    这一族形态满足 θ5 = −90°、θ4 = −90° − θ2 − θ3、θ6 = θ1 + 15°；在随 θ1 转动的手臂坐标系中，法兰盘中心为
    (X − H2, −d4, Z − W4)，X = −L1 cos θ2 − L2 cos(θ2 + θ3)，Z = H1 − L1 sin θ2 − L2 sin(θ2 + θ3)。
    于是 X − H2 = −√(ρ² − d4²)（就是 16.3 节的 r），(θ2 + π, θ3) 是平面 2R 臂到达 (X, Z − H1) 的解，取 θ3 > 0 的一支。
    az 为法兰盘中心的方位角（默认取 θ* 的）。够不着时返回 None。"""
    if az is None:
        p0 = ur_fk(TH_STAR)[:3, 3]
        az = math.atan2(p0[1], p0[0])
    if rho < D4:
        return None
    r = -math.sqrt(rho * rho - D4 * D4)
    X, Zr = r + H2, z + W4 - H1
    sols = ik2r(X, Zr, L1, L2)
    sols = [s for s in sols if s[1] > 0] or [s for s in sols if abs(s[1]) < 1e-12]
    if not sols:
        return None
    t2, t3 = wrap(sols[0][0] - math.pi), sols[0][1]
    t1 = wrap(az - math.atan2(-D4, r))
    return np.array([t1, t2, t3, wrap(-math.pi / 2 - t2 - t3), -math.pi / 2, wrap(t1 + math.radians(15))])


# ================================================================ 第 22 章

# ---------------------------------------------------------------- 22.1 点到点的多项式

def poly_coeffs(T, q0, q1, v0=0.0, v1=0.0, a0=None, a1=None):
    """满足边界条件的多项式系数 c[0..n]（q(t) = Σ c_k t^k，0 ≤ t ≤ T）。
    a0、a1 都给出时是五次（式 (22.1.9) 的线性方程组），否则是三次（式 (22.1.4)）。直接解 4×4 或 6×6 的方程组。"""
    if a0 is None:
        A = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [1, T, T ** 2, T ** 3], [0, 1, 2 * T, 3 * T ** 2]], float)
        b = np.array([q0, v0, q1, v1], float)
    else:
        A = np.array([[1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0], [0, 0, 2, 0, 0, 0],
                      [1, T, T ** 2, T ** 3, T ** 4, T ** 5], [0, 1, 2 * T, 3 * T ** 2, 4 * T ** 3, 5 * T ** 4],
                      [0, 0, 2, 6 * T, 12 * T ** 2, 20 * T ** 3]], float)
        b = np.array([q0, v0, a0, q1, v1, a1], float)
    return np.linalg.solve(A, b)


def poly_eval(c, t, r=0):
    """多项式 Σ c_k t^k 的 r 阶导数（t 可以是数组）。"""
    t = np.asarray(t, float)
    out = np.zeros_like(t)
    for k in range(r, len(c)):
        f = 1.0
        for i in range(r):
            f *= k - i
        out = out + c[k] * f * t ** (k - r)
    return out


def s_cubic(tau, r=0):
    """归一化的三次时间标度 s = 3τ² − 2τ³ 及其对 τ 的导数（式 (22.1.5)）。"""
    tau = np.asarray(tau, float)
    return [3 * tau ** 2 - 2 * tau ** 3, 6 * tau - 6 * tau ** 2, 6 - 12 * tau, -12 + 0 * tau][r]


def s_quintic(tau, r=0):
    """归一化的五次时间标度 s = 10τ³ − 15τ⁴ + 6τ⁵ 及其对 τ 的导数（式 (22.1.10)）。"""
    tau = np.asarray(tau, float)
    return [10 * tau ** 3 - 15 * tau ** 4 + 6 * tau ** 5, 30 * tau ** 2 - 60 * tau ** 3 + 30 * tau ** 4,
            60 * tau - 180 * tau ** 2 + 120 * tau ** 3, 60 - 360 * tau + 360 * tau ** 2][r]


# 归一化时间标度的峰值（τ ∈ [0, 1]）：速度、加速度、加加速度；程序 22.1.1 用数值方法核对
CUBIC_PEAK = (1.5, 6.0, math.inf)
QUINTIC_PEAK = (15 / 8, 10 / math.sqrt(3), 60.0)


def t_min_poly(dq, vmax, amax, kind="cubic", jmax=None):
    """同步点到点运动的最短时间（定理 22.1.3）：各关节共用一条归一化时间标度，取各关节要求的最大者。"""
    pk = CUBIC_PEAK if kind == "cubic" else QUINTIC_PEAK
    dq = np.abs(np.asarray(dq, float))
    Tv = pk[0] * dq / vmax
    Ta = np.sqrt(pk[1] * dq / amax)
    T = np.maximum(Tv, Ta)
    if jmax is not None and kind == "quintic":
        T = np.maximum(T, np.cbrt(pk[2] * dq / jmax))
    return float(T.max()), T


# ---------------------------------------------------------------- 22.2 梯形与 S 形速度曲线

def trap_plan(L, v, a):
    """梯形速度曲线（定义 22.2.1）：从静止到静止走过 L ≥ 0，速度不超过 v、加速度不超过 a 的最短运动。
    返回 dict：ta 加速时间、tc 匀速时间、T 总时间、vp 实际的最高速度。L < v²/a 时是三角形（tc = 0）。"""
    if L <= 0:
        return dict(ta=0.0, tc=0.0, T=0.0, vp=0.0, a=a, L=0.0)
    if L >= v * v / a:
        ta, vp = v / a, v
        tc = L / v - v / a
    else:
        vp = math.sqrt(a * L)
        ta, tc = vp / a, 0.0
    return dict(ta=ta, tc=tc, T=2 * ta + tc, vp=vp, a=a, L=L)


def trap_eval(P, t):
    """梯形曲线在 t 时刻的 (位置, 速度, 加速度)；t 可以是数组。"""
    t = np.clip(np.asarray(t, float), 0, P["T"])
    ta, tc, a, vp, T = P["ta"], P["tc"], P["a"], P["vp"], P["T"]
    q = np.where(t < ta, 0.5 * a * t ** 2,
                 np.where(t < ta + tc, 0.5 * vp * ta + vp * (t - ta), P["L"] - 0.5 * a * (T - t) ** 2))
    v = np.where(t < ta, a * t, np.where(t < ta + tc, vp, a * (T - t)))
    acc = np.where(t < ta, a, np.where(t < ta + tc, 0.0, -a))
    return q, v, acc


def trap_sync(T, ta, L):
    """同步的梯形曲线：给定总时间 T 和加速时间 ta（各关节相同），走过 L 所需的最高速度与加速度（式 (22.2.6)）。"""
    vp = L / (T - ta)
    return dict(ta=ta, tc=T - 2 * ta, T=T, vp=vp, a=vp / ta, L=L)


def scurve_plan(L, v, a, j):
    """七段 S 形曲线（定义 22.2.2）：从静止到静止，|速度| ≤ v，|加速度| ≤ a，|加加速度| ≤ j 的最短运动。
    返回各段时长 (tj, ta, tv)：加加速度为 ±j 的段长 tj，加速度保持 ±a' 的段长 ta，匀速段长 tv，以及实际的 a'、v'。
    七段依次为 +j, 0, −j, 0（匀速）, −j, 0, +j，长度 tj, ta, tj, tv, tj, ta, tj。"""
    def accel_phase(vv):            # 从 0 加速到 vv 所需的 (tj, ta, 路程)
        if vv * j >= a * a:          # 加速度能达到 a
            tj, ta = a / j, vv / a - a / j
        else:                        # 达不到 a：只有两段 ±j
            tj, ta = math.sqrt(vv / j), 0.0
        Tacc = 2 * tj + ta
        return tj, ta, 0.5 * vv * Tacc
    tj, ta, D = accel_phase(v)
    if 2 * D <= L:
        vv = v
        tv = (L - 2 * D) / v
    else:                            # 达不到 v：二分法求最高速度，使两段加减速恰好走完 L
        lo, hi = 0.0, v
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if 2 * accel_phase(mid)[2] > L:
                hi = mid
            else:
                lo = mid
        vv = 0.5 * (lo + hi)
        tj, ta, D = accel_phase(vv)
        tv = 0.0
    ap = j * tj
    return dict(tj=tj, ta=ta, tv=tv, vp=vv, ap=ap, j=j, L=L, T=4 * tj + 2 * ta + tv)


def scurve_eval(P, t):
    """S 形曲线在 t 时刻的 (位置, 速度, 加速度, 加加速度)：按七段的加加速度逐段精确积分。"""
    j = P["j"]
    durs = [P["tj"], P["ta"], P["tj"], P["tv"], P["tj"], P["ta"], P["tj"]]
    jerk = [j, 0, -j, 0, -j, 0, j]
    t = np.atleast_1d(np.clip(np.asarray(t, float), 0, P["T"]))
    out = np.zeros((4, t.size))
    for n, tt in enumerate(t):
        q = v = acc = 0.0
        left = tt
        jj = 0.0
        for d, je in zip(durs, jerk):
            h = min(d, left)
            q += v * h + acc * h * h / 2 + je * h ** 3 / 6
            v += acc * h + je * h * h / 2
            acc += je * h
            jj = je
            left -= h
            if left <= 0:
                break
        out[:, n] = (q, v, acc, jj)
    return out


def box_filter(t, f, width):
    """时间信号 f(t)（等间隔采样）与宽度为 width 的盒形窗作滑动平均（向后平均：(1/w)∫_{t−w}^{t} f）。"""
    dt = t[1] - t[0]
    n = int(round(width / dt))
    c = np.concatenate([[0.0], np.cumsum((f[1:] + f[:-1]) / 2 * dt)])    # 梯形公式累积积分
    out = np.empty_like(f)
    for k in range(len(f)):
        k0 = k - n
        out[k] = (c[k] - (c[k0] if k0 >= 0 else c[0] + f[0] * k0 * dt)) / (n * dt)
    return out


def residual_vibration(t, acc, fn, zeta, extra=1.5):
    """弹性末端的残余振动：x'' + 2ζω x' + ω² x = −a(t)，a(t) 为（一个方向上的）加速度，运动结束后再算 extra 秒。
    用精确的离散化（分段线性的输入下解析积分，步长 = 采样间隔）。返回 (时间, x(t), 运动结束后的振幅)。"""
    w = 2 * math.pi * fn
    dt = t[1] - t[0]
    n_extra = int(round(extra / dt))
    a = np.concatenate([acc, np.zeros(n_extra)])
    tt = np.arange(len(a)) * dt
    # 状态方程 X' = A X + B u，用矩阵指数精确离散（零阶保持的中点值作为输入，二阶精度）
    A = np.array([[0, 1], [-w * w, -2 * zeta * w]])
    from scipy.linalg import expm
    E = expm(A * dt)
    G = np.linalg.solve(A, (E - np.eye(2)) @ np.array([0, -1.0]))
    X = np.zeros(2)
    xs = np.zeros(len(a))
    for k in range(len(a) - 1):
        u = 0.5 * (a[k] + a[k + 1])
        X = E @ X + G * u
        xs[k + 1] = X[0]
    after = tt >= t[-1]
    wd = w * math.sqrt(1 - zeta * zeta)
    # 运动结束时刻的振幅：由那一刻的位移和速度求（自由振动的包络）
    k_end = int(np.argmax(after))
    x0 = xs[k_end]
    v0 = (xs[k_end + 1] - xs[k_end - 1]) / (2 * dt)
    amp = math.sqrt(x0 ** 2 + ((v0 + zeta * w * x0) / wd) ** 2)
    return tt, xs, amp


def accel_breaks(kind, P):
    """梯形或 S 形曲线的加速度写成分段线性函数的折点 (t, a)（同一时刻出现两次表示跳变）。"""
    if kind == "trap":
        ta, tc, a, T = P["ta"], P["tc"], P["a"], P["T"]
        return [(0, a), (ta, a), (ta, 0), (ta + tc, 0), (ta + tc, -a), (T, -a)]
    tj, ta, tv, ap = P["tj"], P["ta"], P["tv"], P["ap"]
    t1 = tj
    t2 = t1 + ta
    t3 = t2 + tj
    t4 = t3 + tv
    t5 = t4 + tj
    t6 = t5 + ta
    t7 = t6 + tj
    return [(0, 0), (t1, ap), (t2, ap), (t3, 0), (t4, 0), (t5, -ap), (t6, -ap), (t7, 0)]


def poly_breaks(f, T, n=4000):
    """光滑的加速度 f(t)（如五次多项式）用 n 段折线近似，返回折点。"""
    t = np.linspace(0, T, n + 1)
    return list(zip(t, f(t)))


def response_pw(br, fn, zeta, extra=1.5, nsub=None, dt_out=0.002):
    """弹性模态 x'' + 2ζω x' + ω² x = −a(t) 对分段线性的 a(t) 的精确响应（每段用增广系统的矩阵指数）。
    返回 (时刻, x) 的采样（每段 nsub 个点，默认按间隔不大于 dt_out 取点；运动结束后再算 extra 秒，a = 0）与运动结束时的振幅
    A = √(x² + ((ẋ + ζωx)/ω_d)²)（之后的自由振动按 e^{−ζωt} 衰减）。"""
    from scipy.linalg import expm
    w = 2 * math.pi * fn
    wd = w * math.sqrt(1 - zeta * zeta)
    M = np.zeros((4, 4))
    M[0, 1] = 1
    M[1, 0], M[1, 1], M[1, 2] = -w * w, -2 * zeta * w, -1.0
    M[2, 3] = 1
    Z = np.zeros(4)
    ts, xs = [0.0], [0.0]
    T_end = br[-1][0]
    pieces = list(zip(br[:-1], br[1:])) + [((T_end, 0.0), (T_end + extra, 0.0))]
    amp = None
    for (t0, a0), (t1, a1) in pieces:
        h = t1 - t0
        if t0 >= T_end and amp is None:
            amp = math.sqrt(Z[0] ** 2 + ((Z[1] + zeta * w * Z[0]) / wd) ** 2)
        if h <= 0:
            continue
        Z[2], Z[3] = a0, (a1 - a0) / h
        ns = nsub or max(1, int(math.ceil(h / dt_out)))
        Es = expm(M * h / ns)
        Zk = Z.copy()
        for k in range(1, ns + 1):
            Zk = Es @ Zk
            ts.append(t0 + h * k / ns)
            xs.append(Zk[0])
        Z = expm(M * h) @ Z
    return np.array(ts), np.array(xs), amp


def fourier_pw(br, w):
    """分段线性函数 a(t) 的 ∫ a(t) e^{−iωt} dt（逐段精确积分）。无阻尼时残余振幅 = |F|/ω（定理 22.2.3 的证明）。"""
    F = 0j
    for (t0, a0), (t1, a1) in zip(br[:-1], br[1:]):
        h = t1 - t0
        if h <= 0:
            continue
        beta = (a1 - a0) / h
        alpha = a0 - beta * t0
        E = lambda t: np.exp(-1j * w * t)
        I0 = (E(t1) - E(t0)) / (-1j * w)
        I1 = E(t1) * (t1 / (-1j * w) + 1 / w ** 2) - E(t0) * (t0 / (-1j * w) + 1 / w ** 2)
        F += alpha * I0 + beta * I1
    return F


def sinc_factor(fn, tj):
    """盒形窗（宽 t_j）在频率 f_n 处的增益 |sin(π f_n t_j)/(π f_n t_j)|（定理 22.2.3）。"""
    x = math.pi * fn * tj
    return 1.0 if x == 0 else abs(math.sin(x) / x)


# ---------------------------------------------------------------- 22.3 样条与过路径点

def cubic_spline(ts, qs, v0=0.0, vN=0.0):
    """过路径点的三次样条（定义 22.3.2）：两端速度给定（夹持端），中间路径点处速度、加速度连续。
    未知数是各内点的速度 v_1…v_{N−1}，方程是式 (22.3.4) 的三对角方程组。qs 可以是 (N+1)×n 的数组（各关节同时算）。
    返回各段的三次多项式系数 [(T_k, c_k)]，c_k 为 4×n（局部时间 0…T_k）。"""
    ts = np.asarray(ts, float)
    qs = np.atleast_2d(np.asarray(qs, float))
    if qs.shape[0] != len(ts):
        qs = qs.T
    N = len(ts) - 1
    h = np.diff(ts)
    n = qs.shape[1]
    V = np.zeros((N + 1, n))
    V[0], V[N] = v0, vN
    if N >= 2:
        A = np.zeros((N - 1, N - 1))
        B = np.zeros((N - 1, n))
        for i in range(1, N):
            r = i - 1
            A[r, r] = 2 * (1 / h[i - 1] + 1 / h[i])
            if r > 0:
                A[r, r - 1] = 1 / h[i - 1]
            if r < N - 2:
                A[r, r + 1] = 1 / h[i]
            B[r] = 3 * ((qs[i] - qs[i - 1]) / h[i - 1] ** 2 + (qs[i + 1] - qs[i]) / h[i] ** 2)
        B[0] -= V[0] / h[0]
        B[-1] -= V[N] / h[N - 1]
        V[1:N] = np.linalg.solve(A, B)
    return hermite_segments(ts, qs, V)


def hermite_segments(ts, qs, V):
    """给定各路径点的位置与速度，每段用三次埃尔米特多项式连接（定理 22.1.1）。"""
    segs = []
    for k in range(len(ts) - 1):
        T = ts[k + 1] - ts[k]
        c = np.array([poly_coeffs(T, qs[k, i], qs[k + 1, i], V[k, i], V[k + 1, i]) for i in range(qs.shape[1])]).T
        segs.append((T, c))
    return segs


def heuristic_vel(ts, qs):
    """路径点处的速度取相邻两段平均斜率的平均值；斜率变号时取 0（22.3.3 节的经验做法）。两端为 0。"""
    ts = np.asarray(ts, float)
    qs = np.atleast_2d(np.asarray(qs, float))
    if qs.shape[0] != len(ts):
        qs = qs.T
    sl = np.diff(qs, axis=0) / np.diff(ts)[:, None]
    V = np.zeros_like(qs)
    for k in range(1, len(ts) - 1):
        m = 0.5 * (sl[k - 1] + sl[k])
        V[k] = np.where(sl[k - 1] * sl[k] > 0, m, 0.0)
    return V


def segs_eval(segs, t, r=0):
    """分段多项式在 t 时刻的 r 阶导数（t 为标量或数组）；返回 (len(t), n)。"""
    t = np.atleast_1d(np.asarray(t, float))
    ends = np.cumsum([0.0] + [T for T, _ in segs])
    out = np.zeros((t.size, segs[0][1].shape[1]))
    for m, tt in enumerate(t):
        k = int(np.clip(np.searchsorted(ends, tt, side="right") - 1, 0, len(segs) - 1))
        T, c = segs[k]
        u = min(max(tt - ends[k], 0.0), T)
        for i in range(c.shape[1]):
            out[m, i] = poly_eval(c[:, i], u, r)
    return out


def lspb_via(ts, qs, tb):
    """抛物线过渡的直线段（过路径点附近而不经过）：路径点 k 处的过渡时长 tb[k]，两端从静止加速、到静止减速。
    直线段的速度 v_k = (q_{k+1} − q_k)/(t_{k+1} − t_k)（两端各段按“从静止开始”修正，见定理 22.3.2 后的说明）。
    这里实现的是最常用的简化做法：两端也用对称的过渡，路径点的时刻 t_k 处于过渡的中点。
    返回函数 f(t, r)。"""
    ts = np.asarray(ts, float)
    qs = np.atleast_2d(np.asarray(qs, float))
    if qs.shape[0] != len(ts):
        qs = qs.T
    N = len(ts) - 1
    v = np.zeros((N + 2, qs.shape[1]))                     # v[0] = 0（起点之前），v[N+1] = 0（终点之后）
    v[1:N + 1] = np.diff(qs, axis=0) / np.diff(ts)[:, None]
    tb = np.asarray(tb, float)

    def f(t, r=0):
        # 先求直线段折线在 t 的值，再在每个过渡区间 [t_k − tb_k/2, t_k + tb_k/2] 内换成抛物线
        k = int(np.clip(np.searchsorted(ts, t, side="right") - 1, 0, N - 1))
        for m in range(N + 1):
            if abs(t - ts[m]) <= tb[m] / 2:
                vin, vout = v[m], v[m + 1]
                acc = (vout - vin) / tb[m]
                u = t - (ts[m] - tb[m] / 2)
                q0 = qs[m] - vin * tb[m] / 2
                return [q0 + vin * u + acc * u * u / 2, vin + acc * u, acc][r]
        if t < ts[0] - tb[0] / 2:
            return [qs[0], 0 * qs[0], 0 * qs[0]][r]
        if t > ts[N] + tb[N] / 2:
            return [qs[N], 0 * qs[N], 0 * qs[N]][r]
        return [qs[k] + v[k + 1] * (t - ts[k]), v[k + 1], 0 * qs[0]][r]
    return f


# ---------------------------------------------------------------- 22.4 笛卡尔直线与圆弧

def circle3(p1, p2, p3):
    """过三点的圆（定理 22.4.2）：返回 (圆心 c, 半径 ρ, 平面内的单位矢量 u、w, 三点的圆心角 φ2、φ3)。
    u 指向 p1，w 在平面内、与 u 垂直、使 p2 落在 0 < φ2 < φ3 的一侧（即按 p1→p2→p3 的顺序转）。"""
    p1, p2, p3 = (np.asarray(x, float) for x in (p1, p2, p3))
    a, b = p2 - p1, p3 - p1
    n = np.cross(a, b)
    nn = n @ n
    c = p1 + (np.cross(n, a) * (b @ b) + np.cross(b, n) * (a @ a)) / (2 * nn)
    rho = float(np.linalg.norm(p1 - c))
    u = (p1 - c) / rho
    nh = n / math.sqrt(nn)
    w = np.cross(nh, u)
    ang = lambda p: math.atan2((p - c) @ w, (p - c) @ u) % (2 * math.pi)
    return c, rho, u, w, ang(p2), ang(p3)


# ---------------------------------------------------------------- 22.5 SO(3)、SE(3) 上的插值

def expso3(r):
    r = np.asarray(r, float)
    th = float(np.linalg.norm(r))
    if th < 1e-14:
        return np.eye(3) + skew(r)
    return rot(r / th, th)


def slerp_R(RA, RB, s):
    """测地线（式 (4.7.1)）：R(s) = R_A e^{[r] s}，r = log(R_Aᵀ R_B)。"""
    return RA @ expso3(logR(RA.T @ RB) * s)


def A_left(r):
    """SO(3) 的左雅可比 A(r)（式 (16.2.10)）：e^{[r]} 的空间角速度 ω_s = A(r) ṙ；物体角速度 ω_b = A(r)ᵀ ṙ。"""
    r = np.asarray(r, float)
    th = float(np.linalg.norm(r))
    K = skew(r)
    if th < 1e-8:
        return np.eye(3) + 0.5 * K + K @ K / 6
    return np.eye(3) + (1 - math.cos(th)) / th ** 2 * K + (th - math.sin(th)) / th ** 3 * K @ K


def decoupled(TA, TB, s, d=np.zeros(3)):
    """解耦插值（定义 22.5.1）：参考点（在物体坐标系中的位置 d）走直线，姿态走测地线。返回 4×4 位姿（原坐标系）。"""
    RA, RB = TA[:3, :3], TB[:3, :3]
    pA, pB = TA[:3, :3] @ d + TA[:3, 3], TB[:3, :3] @ d + TB[:3, 3]
    R = slerp_R(RA, RB, s)
    p = (1 - s) * pA + s * pB
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = p - R @ d
    return T


def screw_interp(TA, TB, s):
    """旋量插值（式 (22.5.3)）：T(s) = T_A e^{[V] s}，V = log(T_A⁻¹ T_B)。"""
    return TA @ exp_twist(log_twist(inv(TA) @ TB) * s)


# ---------------------------------------------------------------- 22.6 沿给定路径的时间最优参数化

def _lp2_max_x(G, h, tol=1e-12):
    """二元线性规划：在 G (x, u)ᵀ ≤ h 中使 x 最大。可行域是凸多边形，最大值在某个顶点上：
    枚举两两约束的交点，取满足全部约束者中 x 最大的。不可行时返回 None。"""
    m = len(h)
    best = None
    i, j = np.triu_indices(m, 1)
    a1, b1, c1 = G[i, 0], G[i, 1], h[i]
    a2, b2, c2 = G[j, 0], G[j, 1], h[j]
    det = a1 * b2 - a2 * b1
    ok = np.abs(det) > 1e-14
    x = np.where(ok, (c1 * b2 - c2 * b1) / np.where(ok, det, 1), np.nan)
    u = np.where(ok, (a1 * c2 - a2 * c1) / np.where(ok, det, 1), np.nan)
    P = np.vstack([x, u])
    feas = ok & np.all(G @ np.nan_to_num(P) <= h[:, None] + 1e-9 * (1 + np.abs(h[:, None])), axis=0)
    if not feas.any():
        return None
    k = np.argmax(np.where(feas, x, -np.inf))
    return float(x[k]), float(u[k])


def path_constraints(dq, ddq, vmax, amax, k):
    """网格点 k 处的约束（式 (22.6.5)）：速度 x ≤ min v_i²/q_i'²；加速度 −a ≤ q' u + q'' x ≤ a。
    返回 (xv, Ga, ha)：Ga (x, u)ᵀ ≤ ha 为加速度约束（2n 行）。"""
    qp, qpp = dq[k], ddq[k]
    with np.errstate(divide="ignore"):
        xv = float(np.min(np.where(np.abs(qp) > 1e-12, vmax ** 2 / np.maximum(qp ** 2, 1e-300), 1e12)))
    Ga = np.vstack([np.column_stack([qpp, qp]), np.column_stack([-qpp, -qp])])
    ha = np.concatenate([amax, amax])
    return xv, Ga, ha


def topp(s, dq, ddq, vmax, amax, x0=0.0, xN=0.0, xcap=None, ucap=None):
    """沿给定路径的时间最优参数化（22.6.4 节）。路径 θ(s) 在网格 s_0 < … < s_N 上给出一、二阶导数 dq、ddq（(N+1)×n）。
    变量 x = ṡ²，u = s̈；每个网格区间内 u 为常数，x_{k+1} = x_k + 2 u_k Δs_k。
    第 1 遍（从终点向前）：求每个网格点能“刹得住”的最大 x，即可控集 [0, K_k]；
    第 2 遍（从起点向后）：每一步取允许的最大 u，且不超出下一点的可控集。返回 (x, u, 各点时刻 t)。
    xcap：另外给出的速度上限（例如末端速度），形如每个网格点 x 的上界数组；ucap：|s̈| 的上限（例如末端沿路径的加速度）。"""
    N = len(s) - 1
    ds = np.diff(s)
    n = dq.shape[1]
    big = 1e6
    XV = np.empty(N + 1)
    CON = []
    for k in range(N + 1):
        xv, Ga, ha = path_constraints(dq, ddq, vmax, amax, k)
        if xcap is not None:
            xv = min(xv, xcap[k])
        if ucap is not None:
            Ga = np.vstack([Ga, [[0, 1.0], [0, -1.0]]])
            ha = np.concatenate([ha, [ucap, ucap]])
        XV[k] = xv
        CON.append((Ga, ha))
    K = np.empty(N + 1)
    K[N] = min(xN, XV[N])
    for k in range(N - 1, -1, -1):
        Ga, ha = CON[k]
        G = np.vstack([Ga, [[1, 0], [-1, 0], [1, 2 * ds[k]], [-1, -2 * ds[k]], [0, 1], [0, -1]]])
        h = np.concatenate([ha, [XV[k], 0.0, K[k + 1], 0.0, big, big]])
        r = _lp2_max_x(G, h)
        if r is None:
            raise ValueError(f"路径在网格点 {k} 处无法满足约束")
        K[k] = r[0]
    if x0 > K[0] + 1e-12:
        raise ValueError("起点速度太大，刹不住")
    x = np.empty(N + 1)
    u = np.zeros(N)
    x[0] = x0
    for k in range(N):
        Ga, ha = CON[k]
        # 关于 u 的一元约束：Ga[:,1] u ≤ ha − Ga[:,0] x_k；以及 0 ≤ x_k + 2 u ds ≤ K_{k+1}
        lo, hi = -big, big
        for gx, gu, hh in zip(Ga[:, 0], Ga[:, 1], ha):
            rhs = hh - gx * x[k]
            if gu > 1e-14:
                hi = min(hi, rhs / gu)
            elif gu < -1e-14:
                lo = max(lo, rhs / gu)
        hi = min(hi, (K[k + 1] - x[k]) / (2 * ds[k]))
        lo = max(lo, -x[k] / (2 * ds[k]))
        if hi < lo - 1e-9 * (1 + abs(lo)):
            raise ValueError(f"第 2 遍在网格点 {k} 处无解")
        u[k] = hi
        x[k + 1] = max(0.0, x[k] + 2 * hi * ds[k])
    sd = np.sqrt(np.maximum(x, 0))
    dt = np.where(sd[:-1] + sd[1:] > 0, 2 * ds / np.maximum(sd[:-1] + sd[1:], 1e-300), 0.0)
    t = np.concatenate([[0.0], np.cumsum(dt)])
    return x, u, t, K, XV


def topp_classic(s, dq, ddq, vmax, amax):
    """另一种算法，用来核对：数值积分法（博布罗等，1985；第 19 章的“前推一遍、后推一遍”）。
    先求速度上限曲线 x ≤ XV 与加速度可行的上限（每点 x 的最大值，使 u 的可行区间非空），
    再从起点以最大 u 向前推、从终点以最小 u 向后推，三者取最小。"""
    N = len(s) - 1
    ds = np.diff(s)
    XV = np.empty(N + 1)
    UB = []
    for k in range(N + 1):
        xv, Ga, ha = path_constraints(dq, ddq, vmax, amax, k)
        # 加速度约束下 x 的最大值（MVC）：u 的可行区间非空
        G = np.vstack([Ga, [[1, 0], [-1, 0], [0, 1], [0, -1]]])
        h = np.concatenate([ha, [xv, 0.0, 1e6, 1e6]])
        XV[k] = _lp2_max_x(G, h)[0]
        UB.append((Ga, ha))

    def urange(k, x):
        Ga, ha = UB[k]
        lo, hi = -1e6, 1e6
        for gx, gu, hh in zip(Ga[:, 0], Ga[:, 1], ha):
            rhs = hh - gx * x
            if gu > 1e-14:
                hi = min(hi, rhs / gu)
            elif gu < -1e-14:
                lo = max(lo, rhs / gu)
        return lo, hi
    f = np.empty(N + 1)
    f[0] = 0.0
    for k in range(N):
        f[k + 1] = min(XV[k + 1], max(0.0, f[k] + 2 * ds[k] * urange(k, f[k])[1]))
    b = np.empty(N + 1)
    b[N] = 0.0
    for k in range(N - 1, -1, -1):
        b[k] = min(XV[k], max(0.0, b[k + 1] - 2 * ds[k] * urange(k + 1, b[k + 1])[0]))
    x = np.minimum(f, b)
    sd = np.sqrt(x)
    dt = 2 * ds / np.maximum(sd[:-1] + sd[1:], 1e-300)
    return x, np.concatenate([[0.0], np.cumsum(dt)]), XV


def arclength_path(f, f1, f2, U, N, n_fine=40):
    """把以 u ∈ [0, U] 为参数的关节路径 θ(u) 改用关节空间中的弧长 σ 作参数（‖dθ/dσ‖ = 1）。
    f、f1、f2 给出 θ、θ_u、θ_uu。返回 σ 网格（N + 1 个点）、对应的 u、θ′(σ)、θ″(σ)。
    dθ/dσ = θ_u/‖θ_u‖，d²θ/dσ² = (θ_uu − (θ_u·θ_uu/‖θ_u‖²) θ_u)/‖θ_u‖²。
    两端 θ_u = 0（起止静止的样条），在离端点 10⁻⁴ U 以内的点改用相邻点外推。"""
    uf = np.linspace(0, U, N * n_fine + 1)
    sp = np.linalg.norm(f1(uf), axis=1)
    sig = np.concatenate([[0.0], np.cumsum((sp[1:] + sp[:-1]) / 2 * np.diff(uf))])
    sg = np.linspace(0, sig[-1], N + 1)
    ug = np.interp(sg, sig, uf)
    d1, d2 = f1(ug), f2(ug)
    n2 = np.sum(d1 * d1, axis=1)
    ok = ug > 1e-4 * U
    ok &= ug < U * (1 - 1e-4)
    D = np.zeros_like(d1)
    DD = np.zeros_like(d1)
    D[ok] = d1[ok] / np.sqrt(n2[ok])[:, None]
    DD[ok] = (d2[ok] - (np.sum(d1[ok] * d2[ok], axis=1) / n2[ok])[:, None] * d1[ok]) / n2[ok][:, None]
    for k in np.where(~ok)[0]:                       # 端点：用最近的两个内部点线性外推
        nb = np.where(ok)[0]
        j = nb[np.argsort(np.abs(nb - k))[:2]]
        for A_ in (D, DD):
            A_[k] = A_[j[0]] + (A_[j[0]] - A_[j[1]]) * (k - j[0]) / (j[0] - j[1])
    from scipy.interpolate import CubicSpline
    u_of = CubicSpline(sig, uf)
    return sg, ug, D, DD, u_of


def resample_path(t_grid, s_grid, x, u, t):
    """由时间最优参数化的结果求任意时刻的 s：第 k 个网格区间内 s̈ = u_k 为常数，
    s(t) = s_k + ṡ_k τ + u_k τ²/2，τ = t − t_k，ṡ_k = √x_k。t 超出 [0, T] 时取两端的值。"""
    t = np.atleast_1d(np.asarray(t, float))
    k = np.clip(np.searchsorted(t_grid, t, side="right") - 1, 0, len(t_grid) - 2)
    tau = np.clip(t - t_grid[k], 0.0, t_grid[k + 1] - t_grid[k])
    out = s_grid[k] + np.sqrt(np.maximum(x[k], 0)) * tau + 0.5 * u[k] * tau ** 2
    out = np.where(t <= t_grid[0], s_grid[0], np.where(t >= t_grid[-1], s_grid[-1], out))
    return out


def fir_smooth(t, sig, width, end_value):
    """宽度为 width 的盒形窗滑动平均（定理 22.2.2 的做法），t 为等间隔时刻；t < 0 时取 sig[0]，t > 最后时刻取 end_value。
    返回延长 width 之后的时刻与滤波结果。"""
    dt = t[1] - t[0]
    n = int(round(width / dt))
    ext = np.concatenate([np.full(n, sig[0]), sig, np.full(n, end_value)])
    c = np.concatenate([[0.0], np.cumsum(ext)])
    m = len(sig) + n
    out = (c[n + 1:n + 1 + m] - c[1:1 + m]) / n            # 第 i 个输出 = ext[i+1 .. i+n] 的平均（向后平均，含当前点）
    tt = t[0] + dt * np.arange(m)
    return tt, out


# ---------------------------------------------------------------- UR5e 上下料工位（示意值）

VMAX = np.full(6, math.pi)                       # 关节速度上限 180°/s（厂商资料，第 16 章）
AMAX = np.array([6.0, 6.0, 6.0, 12.0, 12.0, 12.0])   # 关节加速度上限，rad/s²（设，示意值）
JMAX = np.array([60.0, 60.0, 60.0, 120.0, 120.0, 120.0])  # 关节加加速度上限，rad/s³（设，示意值）
GRIP_L = 0.15                                    # 夹爪：指尖中心（TCP）距法兰盘面 0.15 m（与第 5 章相同）
LIFT = 0.10                                      # 从料架抓起后竖直提升 0.10 m
INSERT = 0.12                                    # 沿主轴方向送入卡盘 0.12 m
P_PICK = np.array([0.20, -0.45, 0.05])           # 料架上抓取点（TCP），{s} 为 UR5e 基座坐标系
P_CHUCK = np.array([0.15, 0.35, 0.20])           # 卡盘内的放料点（TCP）；车床主轴沿 x_s，卡盘端面朝 +x_s
FN_TOOL, ZETA_TOOL = 8.0, 0.02                   # 夹爪与轴组成的弹性模态：固有频率 8 Hz，阻尼比 0.02（设，示意值）


def T_bt():
    """工具坐标系 {t} 相对法兰盘 {b}：原点在指尖中心，z_t 沿法兰盘法线（= y_b）向外（与第 5 章相同）。"""
    T = np.eye(4)
    T[:3, :3] = rotx(-math.pi / 2)
    T[:3, 3] = (0, GRIP_L, 0)
    return T


TBT = T_bt()


def pose(R, p):
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = p
    return T


R_DOWN = np.array([[-1.0, 0, 0], [0, 1, 0], [0, 0, -1]])      # 夹爪竖直朝下：x_t = −x_s，y_t = y_s，z_t = −z_s
R_CHUCK = np.array([[0.0, 0, -1], [-1, 0, 0], [0, 1, 0]])     # 水平送料：x_t = −y_s，y_t = z_s，z_t = −x_s


def tcp_fk(theta):
    """UR5e 的 TCP 位姿 T_st = T_sb(θ) T_bt。"""
    return ur_fk(theta) @ TBT


def tcp_ik(Tst, ref):
    """TCP 位姿的逆解：取与 ref 最近的一组（各关节按 2π 展开到 ref 附近）。够不着返回 None。"""
    Tsb = Tst @ inv(TBT)
    sols = [s for s, _ in ur_ik(Tsb)]
    if not sols:
        return None
    sols = [ref + np.array([wrap(a - b) for a, b in zip(s, ref)]) for s in sols]
    return min(sols, key=lambda s: float(np.linalg.norm(s - ref)))


def cell_poses():
    """工位的四个关键位姿（TCP）：抓取 R、提升后 A、送料前 B、卡盘内 C。"""
    TR = pose(R_DOWN, P_PICK)
    TA = pose(R_DOWN, P_PICK + np.array([0, 0, LIFT]))
    TB = pose(R_CHUCK, P_CHUCK + np.array([INSERT, 0, 0]))
    TC = pose(R_CHUCK, P_CHUCK)
    return TR, TA, TB, TC


def cell_joints():
    """四个关键位姿的关节角：都取肩 A、肘上、腕不翻的一支，并按连续性展开（θ1 可超过 180°）。"""
    TR, TA, TB, TC = cell_poses()
    thA = tcp_ik(TA, TH_STAR)
    thR = tcp_ik(TR, thA)
    thB = tcp_ik(TB, thA)
    thC = tcp_ik(TC, thB)
    return thR, thA, thB, thC


P_VIA = np.array([0.45, -0.05, 0.35])           # 越过车床防护罩的路径点 M（TCP），姿态取 A、B 两姿态测地线的中点


def via_pose():
    return pose(slerp_R(R_DOWN, R_CHUCK, 0.5), P_VIA)


def via_joints():
    thR, thA, thB, thC = cell_joints()
    return tcp_ik(via_pose(), (thA + thB) / 2)


def line_joints(T0, T1, ref, n):
    """TCP 沿直线（姿态不变或按测地线变化）从 T0 到 T1：n + 1 个等分点的逆解（与 ref 同一支、连续）。"""
    out, th = [], ref.copy()
    for s in np.linspace(0, 1, n + 1):
        T = decoupled(T0, T1, s)
        th = tcp_ik(T, th)
        out.append(th)
    return np.array(out)


# ---------------------------------------------------------------- 22.4 经过手腕奇异附近的直线（与算例 15.3.2 相同）

def wrist_line():
    """法兰盘姿态不变、中心沿水平直线移动 0.3 m，中点处 θ5 = 1°（算例 15.3.2）。方向水平且垂直于腕点的径向。
    返回 (中点位姿 Tm, 方向 d, 起点的关节角 th0)；起点为沿路径从中点连续退回 0.15 m 的同一支解析解。"""
    th_mid = np.radians([30, -60, 90, -120, 1.0, 45])
    Tm = ur_fk(th_mid)
    pw = Tm[:3, 3] - W4 * Tm[:3, 1]
    rad = np.array([pw[0], pw[1], 0.0])
    rad /= np.linalg.norm(rad)
    d = np.cross([0, 0, 1.0], rad)
    th = th_mid.copy()
    for s in np.linspace(0, -0.15, 301):
        T = Tm.copy()
        T[:3, 3] += s * d
        S = [x for x, _ in ur_ik(T)]
        th = min(S, key=lambda x: np.linalg.norm([wrap(a - b) for a, b in zip(x, th)]))
    return Tm, d, th


def follow_line(Tm, d, th0, ells):
    """沿 T(ℓ) = Tm 平移 (ℓ − 0.15) d 逐点取同一支解析解（ℓ 从 0 到 0.3 m），关节角按连续性展开。"""
    out, th = [], th0.copy()
    for l in ells:
        T = Tm.copy()
        T[:3, 3] += (l - 0.15) * d
        S = [x for x, _ in ur_ik(T)]
        best = min(S, key=lambda x: np.linalg.norm([wrap(a - b) for a, b in zip(x, th)]))
        th = th + np.array([wrap(a - b) for a, b in zip(best, th)])
        out.append(th.copy())
    return np.array(out)
