"""第 15 章共用：旋量、矩阵指数与对数、伴随矩阵、物体雅可比，UR5e 的解析逆解（用来与数值解对照），
零件库模型的读法，以及三种数值逆解（牛顿-拉夫森、雅可比转置、阻尼最小二乘）。以下划线开头，构建时不单独运行。

旋量、指数、零件库模型和 UR5e 解析逆解与第 14 章的 _ik.py 相同，这里重写一份，使本章程序自成一体：
- 关节表在 models/<模型>/entry.json，连杆矩阵在 default.glb（网页三维实验显示的就是它）；
- 模型的正运动学按三维引擎的做法计算：子连杆位姿 = 父连杆位姿 · 节点矩阵 · 绕关节轴转 θ。
这是与指数积公式无关的另一种算法，数值逆解求出的关节角都拿它来核对。
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


# 厂家式（标准 DH，取模型尺寸）的另一种解法：Hawkins (2013) 的公式，用来与本章的解法互相核对
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


# ---------------------------------------------------------------- 三种数值逆解（15.1–15.3 节）

def nr(fk, jb, Td, th0, tol_w=1e-12, tol_v=1e-12, iters=60, lam=0.0, step_max=None):
    """李群上的牛顿-拉夫森迭代（式 (15.1.8)）：J_b Δθ = V_b。n ≠ 6 时用伪逆；lam > 0 时为阻尼最小二乘（15.3 节）；
    step_max 限制每步关节转角的最大值（15.5 节）。返回 (θ, 是否收敛, 历史 [(θ, V_b)])。"""
    th = np.array(th0, float)
    hist = []
    for _ in range(iters + 1):
        V = err_twist(fk(th), Td)
        hist.append((th.copy(), V))
        if np.linalg.norm(V[:3]) < tol_w and np.linalg.norm(V[3:]) < tol_v:
            return th, True, hist
        if len(hist) > iters:
            break
        J = jb(th)
        if lam > 0:
            d = J.T @ np.linalg.solve(J @ J.T + lam * lam * np.eye(6), V)
        elif J.shape[1] == 6:
            if np.linalg.cond(J) > 1e12:                  # 奇异：J_b 不可逆，牛顿-拉夫森法无法继续
                return th, False, hist
            d = np.linalg.solve(J, V)
        else:
            d = np.linalg.pinv(J) @ V
        if step_max is not None:
            m = np.abs(d).max()
            if m > step_max:
                d *= step_max / m
        th = th + d
    return th, False, hist


def jt(fk, jb, Td, th0, W=None, alpha=None, tol_w=1e-9, tol_v=1e-9, iters=20000):
    """雅可比转置法（15.2 节）：Δθ = α J_bᵀ W V_b。alpha=None 时每步取使线性化误差最小的 α（式 (15.2.8)）。"""
    th = np.array(th0, float)
    W = np.eye(6) if W is None else W
    hist = []
    for k in range(iters + 1):
        V = err_twist(fk(th), Td)
        hist.append((th.copy(), V))
        if np.linalg.norm(V[:3]) < tol_w and np.linalg.norm(V[3:]) < tol_v:
            return th, True, hist
        if k == iters:
            break
        J = jb(th)
        g = J.T @ W @ V
        if alpha is None:
            Jg = J @ g
            a = float(V @ W @ Jg) / float(Jg @ W @ Jg)
        else:
            a = alpha
        th = th + a * g
    return th, False, hist


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


def ur_screws_perturbed(dL1=0.0, dL2=0.0, tilt3=0.0):
    """“标定后的”UR5e：大臂、小臂长度改变 dL1、dL2（m），关节 3 的轴绕 x 轴偏斜 tilt3（rad）。返回 (S 列表, M)。"""
    l1, l2 = L1 + dL1, L2 + dL2
    w3 = rot([1.0, 0, 0], tilt3) @ YD
    W = [np.array([0, 0, 1.0]), YD, w3, YD, np.array([0, 0, -1.0]), YD]
    Q = [np.array([0, 0, H1]), np.array([0, -W1, H1]), np.array([-l1, -W1 + W2, H1]), np.array([-l1 - l2, -W1 + W2, H1]),
         np.array([-l1 - l2, -W1 + W2 - W3, H1]), np.array([-l1 - l2, -W1 + W2 - W3, H1 - H2])]
    M = np.array([[1.0, 0, 0, -l1 - l2], [0, -1, 0, -W1 + W2 - W3 - W4], [0, 0, -1, H1 - H2], [0, 0, 0, 1]])
    return [screw_revolute(w, q) for w, q in zip(W, Q)], M


def planar_nr(Td, th0, L=PL, iters=50, tol=1e-12):
    """平面 3R 臂在 SE(2) 上的牛顿-拉夫森迭代：J_b Δθ = V_b，V_b = log(T⁻¹T_d)。返回 (θ, 是否收敛, 历史 [(θ, V_b)])。"""
    th = np.array(th0, float)
    hist = []
    for k in range(iters + 1):
        V = log_se2(np.linalg.inv(planar_pose(th, L)) @ Td)
        hist.append((th.copy(), V))
        if np.linalg.norm(V) < tol:
            return th, True, hist
        J = jb_planar(th, L)
        if abs(np.linalg.det(J)) < 1e-12 or k == iters:
            break
        th = th + np.linalg.solve(J, V)
    return th, False, hist


def pole_se2(V):
    """平面位移 e^{[V]}（V = (φ, v_x, v_y)，φ ≠ 0）的极点 c（在 V 所在的坐标系中）：v = −ω × c，即 c = (−v_y, v_x)/φ。"""
    phi, vx, vy = V
    return np.array([-vy, vx]) / phi


# ---------------------------------------------------------------- 平面 2R 臂（第 7、8、14 章的同一台）

L2R = (0.425, 0.392)
PD2R = np.array([0.45, 0.35])


def jt_planar(pd, th0, L=L2R, alpha=None, tol=1e-10, iters=100000):
    """平面臂末端位置的雅可比转置法：Δθ = α Jᵀ e，e = p_d − p(θ)。alpha=None 时每步取式 (15.2.8) 的 α。
    返回 (θ, 迭代次数（未收敛为 None）, 各步 ‖e‖, 各步 θ)。"""
    th = np.array(th0, float)
    E, TH = [], []
    for k in range(iters + 1):
        e = pd - fk_planar(th, L)[:2]
        E.append(float(np.linalg.norm(e)))
        TH.append(th.copy())
        if E[-1] < tol:
            return th, k, E, TH
        if k == iters or not np.isfinite(E[-1]) or E[-1] > 1e3:
            break
        J = jac_planar(th, L)
        g = J.T @ e
        if alpha is None:
            Jg = J @ g
            if float(Jg @ Jg) == 0.0:
                break
            a = float(e @ Jg) / float(Jg @ Jg)
        else:
            a = alpha
        th = th + a * g
    return th, None, E, TH


def newton_planar(pd, th0, L=L2R, tol=1e-10, iters=60):
    """平面 2R 臂位置逆解的牛顿法（式 (7.3.8)）。"""
    th = np.array(th0, float)
    E, TH = [], []
    for k in range(iters + 1):
        e = pd - fk_planar(th, L)[:2]
        E.append(float(np.linalg.norm(e)))
        TH.append(th.copy())
        if E[-1] < tol:
            return th, k, E, TH
        th = th + np.linalg.solve(jac_planar(th, L), e)
    return th, None, E, TH


# ---------------------------------------------------------------- 算例 15.3.2：经过手腕奇异附近的直线路径

class WristPath:
    """UR5e 法兰盘姿态不变、中心沿水平直线以 0.1 m/s 移动 0.3 m；路径中点处 θ5 = 1°（手腕接近奇异）。
    方向取水平且垂直于手腕点的径向（关节 1 转动的方向）。起点为沿路径从中点连续退回到起点的同一支解析解。"""

    def __init__(self, v=0.1, dur=3.0, dt=0.002, Lc=0.1):
        self.th_mid = np.radians([30, -60, 90, -120, 1.0, 45])
        self.Tm = ur_fk(self.th_mid)
        pw = self.Tm[:3, 3] - W4 * self.Tm[:3, 1]
        rad = np.array([pw[0], pw[1], 0.0])
        rad /= np.linalg.norm(rad)
        self.d = np.cross([0, 0, 1.0], rad)
        self.v, self.dur, self.dt, self.N, self.Lc = v, dur, dt, int(round(dur / dt)), Lc
        th = self.th_mid.copy()
        for s in np.linspace(0, -0.15, 301):
            th = self.nearest(self.T_at_s(s), th)
        self.th0 = th

    def T_at_s(self, s):
        T = self.Tm.copy()
        T[:3, 3] += s * self.d
        return T

    def Tdes(self, t):
        return self.T_at_s(-0.15 + self.v * t)

    @staticmethod
    def nearest(T, prev):
        S = [s for s, _ in ur_ik(T)]
        return min(S, key=lambda s: np.linalg.norm([wrap(a - b) for a, b in zip(s, prev)]))

    def analytic(self):
        """沿路径逐点取同一支解析解（精确的关节轨迹）。"""
        traj, th = [], self.th0.copy()
        for k in range(self.N + 1):
            th = self.nearest(self.Tdes(k * self.dt), th)
            traj.append(th)
        return np.unwrap(np.array(traj), axis=0)

    def run(self, mode, lam=0.0, eps=0.0, K=10.0):
        """分解运动速率控制 θ̇ = J⁺(V_d + K V_err)，每 dt 一次。J⁺ 为精确的逆（mode="exact"）、固定阻尼（"fixed"）
        或可变阻尼（"var"，σ_min < ε 时 λ² = (1 − (σ_min/ε)²) λ_max²）。加权 W = diag(L_c I, I)。
        返回各时刻的关节角、关节速度、位置误差 (m)、姿态误差 (rad)、σ_min、λ²。"""
        W = np.diag([self.Lc] * 3 + [1] * 3)
        th = self.th0.copy()
        H = {"th": [], "dth": [], "ep": [], "eo": [], "smin": [], "l2": []}
        for k in range(self.N):
            T, Tk = ur_fk(th), self.Tdes(k * self.dt)
            Ve = err_twist(T, Tk)
            Vd = np.r_[np.zeros(3), T[:3, :3].T @ (self.v * self.d)]
            J = W @ ur_jb(th)
            b = W @ (Vd + K * Ve)
            smin = float(np.linalg.svd(J, compute_uv=False)[-1])
            if mode == "exact":
                l2 = 0.0
                dth = np.linalg.solve(J, b)
            else:
                l2 = lam ** 2 if mode == "fixed" else ((1 - (smin / eps) ** 2) * lam ** 2 if smin < eps else 0.0)
                dth = J.T @ np.linalg.solve(J @ J.T + l2 * np.eye(6), b)
            for key, val in (("th", th.copy()), ("dth", dth), ("ep", float(np.linalg.norm(Tk[:3, 3] - T[:3, 3]))),
                             ("eo", float(np.linalg.norm(Ve[:3]))), ("smin", smin), ("l2", l2)):
                H[key].append(val)
            th = th + dth * self.dt
        T, Tk = ur_fk(th), self.Tdes(self.N * self.dt)
        H["th_end"], H["ep_end"] = th, float(np.linalg.norm(Tk[:3, 3] - T[:3, 3]))
        return {k: np.array(v) if isinstance(v, list) else v for k, v in H.items()}


# ---------------------------------------------------------------- Panda（七轴，零件库 B-ARM-PANDA）与关节限位（15.4 节）

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


def in_limits_mod(q, lo, hi, tol=1e-9):
    """关节角加减 2π 的整数倍后能否落在限位以内（转动关节）。"""
    for x, a, b in zip(q, lo, hi):
        if not any(a - tol <= x + 2 * math.pi * k <= b + tol for k in (-2, -1, 0, 1, 2)):
            return False
    return True


def joint_center_grad(q, lo, hi):
    """关节居中指标 H(θ) = Σ ((θ_i − c_i)/(θ_max,i − θ_min,i))² 的梯度，c 为限位的中点（式 (15.4.6)）。"""
    c, r = (lo + hi) / 2, hi - lo
    return 2 * (q - c) / r ** 2


def ik_limits(fk, jb, Td, q0, lo, hi, mode, Lc=0.3, lam=1e-3, iters=100, tol=1e-9, kc=0.5, hist=None):
    """带关节限位的数值逆解（15.4 节）。误差旋量的移动部分除以特征长度 L_c 后与转动部分一起计量（15.2.6 节）。
    mode："free" 不管限位（伪逆，式 (15.1.9)）；"clamp" 每步后截断到限位（式 (15.4.2)）；
    "center" 伪逆加零空间中的居中项 −k_c (I − J⁺J)∇H（式 (15.4.7)），不截断；
    "box" 每步解有界的阻尼最小二乘 min ‖W(J Δ − V)‖² + λ²‖Δ‖²，θ_min − θ ≤ Δ ≤ θ_max − θ（式 (15.4.3)，一个二次规划）。
    hist 为列表时，记下每一步的 (θ, V, Δ)。返回 (θ, 是否收敛, 迭代次数)。"""
    from scipy.optimize import lsq_linear
    W = np.diag([1, 1, 1] + [1 / Lc] * 3)
    q = np.array(q0, float)
    n = len(q)
    for k in range(iters):
        V = err_twist(fk(q), Td)
        if np.linalg.norm(V[:3]) < tol and np.linalg.norm(V[3:]) < tol:
            return q, True, k
        J = jb(q)
        if mode == "box":
            A = np.vstack([W @ J, lam * np.eye(n)])
            b = np.r_[W @ V, np.zeros(n)]
            d = lsq_linear(A, b, bounds=(lo - q - 1e-12, hi - q + 1e-12), method="bvls", tol=1e-14).x
            d = np.clip(d, lo - q, hi - q)
        else:
            Jp = np.linalg.pinv(J)
            d = Jp @ V
            if mode == "center":
                d = d - kc * (np.eye(n) - Jp @ J) @ joint_center_grad(q, lo, hi)
        if hist is not None:
            hist.append((q.copy(), V, d))
        q = q + d
        if mode == "clamp":
            q = np.clip(q, lo, hi)
    V = err_twist(fk(q), Td)
    return q, bool(np.linalg.norm(V[:3]) < tol and np.linalg.norm(V[3:]) < tol), iters


# ---------------------------------------------------------------- 成批计算（15.5 节：初值平面上成千上万个起点同时迭代）

def _skew_b(w):
    z = np.zeros(w.shape[:-1] + (3, 3))
    z[..., 0, 1], z[..., 0, 2], z[..., 1, 2] = -w[..., 2], w[..., 1], -w[..., 0]
    z[..., 1, 0], z[..., 2, 0], z[..., 2, 1] = w[..., 2], -w[..., 1], w[..., 0]
    return z


def _exp_rev_b(S, t):
    """成批的 e^{[S]θ}（S 为单位转动旋量，θ 为长 B 的数组）：返回 (B, 4, 4)。"""
    w, v = S[:3], S[3:]
    K = _skew_b(w)
    s, c = np.sin(t)[:, None, None], np.cos(t)[:, None, None]
    T = np.zeros((len(t), 4, 4))
    T[:, :3, :3] = np.eye(3) + s * K + (1 - c) * (K @ K)
    G = np.eye(3) * t[:, None, None] + (1 - c) * K + (t[:, None, None] - s) * (K @ K)
    T[:, :3, 3] = G @ v
    T[:, 3, 3] = 1
    return T


def _adj_b(T):
    R, p = T[:, :3, :3], T[:, :3, 3]
    A = np.zeros((len(T), 6, 6))
    A[:, :3, :3] = R
    A[:, 3:, 3:] = R
    A[:, 3:, :3] = _skew_b(p) @ R
    return A


def _inv_b(T):
    Ti = np.zeros_like(T)
    Rt = np.transpose(T[:, :3, :3], (0, 2, 1))
    Ti[:, :3, :3] = Rt
    Ti[:, :3, 3] = -np.einsum("bij,bj->bi", Rt, T[:, :3, 3])
    Ti[:, 3, 3] = 1
    return Ti


def _log_b(T):
    """成批的 SE(3) 对数（定理 6.4.3），返回 (B, 6)。转角接近 π 的少数情形逐个用 log_twist 处理。"""
    R, p = T[:, :3, :3], T[:, :3, 3]
    c = np.clip((np.trace(R, axis1=1, axis2=2) - 1) / 2, -1, 1)
    th = np.arccos(c)
    d = np.stack([R[:, 2, 1] - R[:, 1, 2], R[:, 0, 2] - R[:, 2, 0], R[:, 1, 0] - R[:, 0, 1]], axis=1)
    out = np.zeros((len(T), 6))
    small = th < 1e-8
    near_pi = np.pi - th < 1e-4
    reg = ~small & ~near_pi
    wth = np.zeros((len(T), 3))
    wth[small] = 0.5 * d[small]
    wth[reg] = d[reg] * (th[reg] / (2 * np.sin(th[reg])))[:, None]
    out[:, :3] = wth
    out[small, 3:] = p[small]
    if reg.any():
        t = th[reg]
        w = wth[reg] / t[:, None]
        K = _skew_b(w)
        Gi = np.eye(3) / t[:, None, None] - 0.5 * K + (1 / t - 0.5 / np.tan(t / 2))[:, None, None] * (K @ K)
        out[reg, 3:] = t[:, None] * np.einsum("bij,bj->bi", Gi, p[reg])
    for i in np.where(near_pi)[0]:
        out[i] = log_twist(T[i])
    return out


def ur_batch(theta):
    """成批的 UR5e：θ 为 (B, 6)。返回末端位姿 (B, 4, 4) 与物体雅可比 (B, 6, 6)（J_b = [Ad_{T⁻¹}] J_s，式 (15.1.7)）。"""
    B = len(theta)
    P = np.tile(np.eye(4), (B, 1, 1))
    Js = np.zeros((B, 6, 6))
    for i in range(6):
        Js[:, :, i] = np.einsum("bij,j->bi", _adj_b(P), UR_S[i])
        P = P @ _exp_rev_b(UR_S[i], theta[:, i])
    T = P @ UR_M
    Jb = _adj_b(_inv_b(T)) @ Js
    return T, Jb


def ur_err_batch(theta, Td):
    """成批的误差旋量 V_b = log(T⁻¹T_d)；Td 为单个 4×4 或 (B, 4, 4)。"""
    T, Jb = ur_batch(theta)
    return _log_b(_inv_b(T) @ Td), Jb
