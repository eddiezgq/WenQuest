"""第 16 章共用：旋量、矩阵指数与对数、伴随矩阵，空间雅可比与物体雅可比，UR5e 的旋量轴（表 12.1.1）与解析逆解（14.5 节），
零件库模型的读法，平面臂，Panda；以及本章新加的几何雅可比、欧拉角与指数坐标的速度关系、UR5e 奇异的三个因子、
雅可比矩阵的时间导数。以下划线开头，构建时不单独运行。

旋量、指数、零件库模型和 UR5e 解析逆解与第 14、15 章相同，这里重写一份，使本章程序自成一体：
- 关节表在 models/<模型>/entry.json，连杆矩阵在 default.glb（网页三维实验显示的就是它）；
- 模型的正运动学按三维引擎的做法计算：子连杆位姿 = 父连杆位姿 · 节点矩阵 · 绕关节轴转 θ。
这是与指数积公式无关的另一种算法，本章的雅可比矩阵都拿它用差商核对。
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
