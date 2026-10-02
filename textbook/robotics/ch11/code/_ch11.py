"""第 11 章共用：旋量与矩阵指数、读取零件库模型、UR5e 的 DH 正运动学与解析逆运动学、自由度的秩判别。
以下划线开头，构建时不单独运行。

旋量、矩阵指数和读取模型的几个函数与第 12 章程序（ch12/code/_poe.py）相同，这里另存一份，
使本章的程序只依赖本章的文件。
"""
import json
import math
import struct
from pathlib import Path

import numpy as np

MODELS = Path(__file__).resolve().parents[2] / "models"


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


def screw_helical(w, q, h):
    """螺旋关节的旋量轴 S = (ω, −ω × q + h ω)，式 (11.1.2)。"""
    w = np.asarray(w, float)
    return np.r_[w, -np.cross(w, np.asarray(q, float)) + h * w]


def bracket(S):
    m = np.zeros((4, 4))
    m[:3, :3] = skew(S[:3])
    m[:3, 3] = S[3:]
    return m


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


def expm_series(A, n=60):
    """矩阵指数的级数定义，用来独立核对 exp6。"""
    S, term = np.eye(A.shape[0]), np.eye(A.shape[0])
    for k in range(1, n):
        term = term @ A / k
        S = S + term
    return S


def adjoint(T):
    """[Ad_T] = [[R 0]; [[p]R R]]，式 (12.2.6)。"""
    R, p = T[:3, :3], T[:3, 3]
    A = np.zeros((6, 6))
    A[:3, :3] = R
    A[3:, 3:] = R
    A[3:, :3] = skew(p) @ R
    return A


def tinv(T):
    R, p = T[:3, :3], T[:3, 3]
    o = np.eye(4)
    o[:3, :3] = R.T
    o[:3, 3] = -R.T @ p
    return o


def fk_space(Slist, M, theta):
    """指数积公式的空间形式 (12.2.3)。"""
    T = np.eye(4)
    for S, t in zip(Slist, theta):
        T = T @ exp6(S, t)
    return T @ M


def null_space(A, tol=1e-9):
    """A 的零空间的一组标准正交基（按列），用奇异值分解（2.4 节）。"""
    u, s, vt = np.linalg.svd(A)
    r = int((s > tol * max(1.0, s[0] if len(s) else 1.0)).sum())
    return vt[r:].T, r


def reciprocal(S1, S2):
    """两个旋量的互易积（6.6 节）：S1 = (ω1, v1)，S2 = (ω2, v2)，ω1·v2 + v1·ω2。"""
    return float(S1[:3] @ S2[3:] + S1[3:] @ S2[:3])


# ---------------------------------------------------------------- 自由度：约束的秩（11.2 节）

def mobility(n_moving, joints):
    """真实的（瞬时）自由度。

    把每个运动连杆的空间运动旋量 V_k（6 个数）和每个关节的关节速度当作未知数。关节 j 连接连杆 a、b，
    允许的相对运动由列为旋量的矩阵 S_j（6 × f_j）张成，约束为 V_b − V_a − S_j θ̇_j = 0（6 个方程）。
    机架的 V = 0。自由度 = 未知数个数 − 方程组系数矩阵的秩。joints: [(a, b, S_j)]，连杆编号 0 为机架。
    返回 (未知数个数, 方程个数, 秩, 自由度, 零空间基)。
    """
    nf = sum(S.shape[1] for _, _, S in joints)
    nu = 6 * n_moving + nf
    rows = []
    col = 6 * n_moving
    for a, b, S in joints:
        r = np.zeros((6, nu))
        if b > 0:
            r[:, 6 * (b - 1):6 * b] += np.eye(6)
        if a > 0:
            r[:, 6 * (a - 1):6 * a] -= np.eye(6)
        r[:, col:col + S.shape[1]] = -S
        col += S.shape[1]
        rows.append(r)
    A = np.vstack(rows)
    N, rank = null_space(A)
    return nu, A.shape[0], rank, nu - rank, N


def joint_R(w, q):
    return screw_revolute(w, q).reshape(6, 1)


def joint_P(v):
    return screw_prismatic(v).reshape(6, 1)


def joint_S(q):
    """球关节：过点 q、沿 x、y、z 的三个转动旋量。"""
    return np.column_stack([screw_revolute(e, q) for e in np.eye(3)])


def joint_U(w1, w2, q):
    """万向节：过点 q 的两个互相垂直的转动旋量。"""
    return np.column_stack([screw_revolute(w1, q), screw_revolute(w2, q)])


def grubler(m, N, f):
    """格吕布勒公式 (11.2.2)：m 为单个刚体的自由度（平面 3、空间 6），N 含机架，f 为各关节自由度。"""
    return m * (N - 1 - len(f)) + sum(f)


# ---------------------------------------------------------------- UR5e：零件库模型尺寸、DH 正运动学、解析逆运动学

H1, W1, L1u, W2, L2u, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1   # 模型关节表中的尺寸 (m)，同表 12.1.1
UR_DH = [(0.0, H1, math.pi / 2), (-L1u, 0.0, 0.0), (-L2u, 0.0, 0.0), (0.0, W1 - W2 + W3, math.pi / 2), (0.0, H2, -math.pi / 2), (0.0, W4, 0.0)]
D4, D6, A2, A3 = W1 - W2 + W3, W4, -L1u, -L2u


def ur_screws():
    """表 12.1.1 的六个旋量轴和零位位姿 M（{b} 的 y 轴沿法兰法线）。"""
    yd = np.array([0, -1.0, 0])
    table = [(np.array([0, 0, 1.0]), np.array([0, 0, H1])), (yd, np.array([0, -W1, H1])),
             (yd, np.array([-L1u, -W1 + W2, H1])), (yd, np.array([-L1u - L2u, -W1 + W2, H1])),
             (np.array([0, 0, -1.0]), np.array([-L1u - L2u, -W1 + W2 - W3, H1])),
             (yd, np.array([-L1u - L2u, -W1 + W2 - W3, H1 - H2]))]
    S = [screw_revolute(w, q) for w, q in table]
    M = np.array([[1.0, 0, 0, -L1u - L2u], [0, -1, 0, -W1 + W2 - W3 - W4], [0, 0, -1, H1 - H2], [0, 0, 0, 1]])
    return S, M


def dh_A(i, th):
    a, d, al = UR_DH[i]
    ct, st, ca, sa = math.cos(th), math.sin(th), math.cos(al), math.sin(al)
    return np.array([[ct, -st * ca, st * sa, a * ct], [st, ct * ca, -ct * sa, a * st], [0, sa, ca, d], [0, 0, 0, 1]])


def ur_fk_dh(q):
    """按标准 DH 参数（取模型尺寸）计算末端位姿；末端 z 轴沿法兰法线向外。"""
    T = np.eye(4)
    for i in range(6):
        T = T @ dh_A(i, q[i])
    return T


def ur_ik(T):
    """UR 型六轴臂的解析逆运动学（Hawkins 2013 的做法，第 14 章详讲）。T 为 DH 末端坐标系的目标位姿，返回全部解。"""
    sols = []
    p05 = T @ np.array([0, 0, -D6, 1.0])
    r = math.hypot(p05[0], p05[1])
    if r < D4:
        return sols
    psi, phi = math.atan2(p05[1], p05[0]), math.acos(D4 / r)
    for t1 in (psi + phi + math.pi / 2, psi - phi + math.pi / 2):
        T16 = tinv(dh_A(0, t1)) @ T
        c5 = (T16[2, 3] - D4) / D6
        if abs(c5) > 1:
            continue
        for t5 in (math.acos(c5), -math.acos(c5)):
            T61 = tinv(T16)
            s5 = math.sin(t5)
            t6 = 0.0 if abs(s5) < 1e-12 else math.atan2(-T61[1, 2] / s5, T61[0, 2] / s5)
            T14 = T16 @ tinv(dh_A(5, t6)) @ tinv(dh_A(4, t5))
            p13 = (T14 @ np.array([0, -D4, 0, 1.0]))[:3]
            n = np.linalg.norm(p13)
            c3 = (n * n - A2 * A2 - A3 * A3) / (2 * A2 * A3)
            if abs(c3) > 1:
                continue
            for t3 in (math.acos(c3), -math.acos(c3)):
                t2 = -math.atan2(p13[1], -p13[0]) + math.asin(A3 * math.sin(t3) / n)
                T34 = tinv(dh_A(2, t3)) @ tinv(dh_A(1, t2)) @ T14
                t4 = math.atan2(T34[1, 0], T34[0, 0])
                sols.append(np.array([t1, t2, t3, t4, t5, t6]))
    return sols


def frame_from_z(a):
    """以单位矢量 a 为 z 轴，任取与之垂直的 x 轴，组成旋转矩阵（逐行处理一组 a）。"""
    a = np.atleast_2d(a)
    h = np.where(np.abs(a[:, [0]]) < 0.9, np.array([[1.0, 0, 0]]), np.array([[0, 1.0, 0]]))
    x = np.cross(h, a)
    x /= np.linalg.norm(x, axis=1, keepdims=True)
    y = np.cross(a, x)
    return np.stack([x, y, a], axis=2)          # (N, 3, 3)，第 k 列为第 k 根轴


def ur_reachable(p, a):
    """法兰中心到达 p、法兰法线朝向 a 时，逆运动学是否有解（逐行处理，向量化）。

    绕法兰法线的转动由关节 6 完成，不影响 p 和 a，所以有没有解只取决于 (p, a)。
    依次检查 Hawkins 解法中的三个反余弦是否有定义：θ1 一项、θ5 一项（恒有定义）和 θ3 一项。
    """
    p, a = np.atleast_2d(p), np.atleast_2d(a)
    N = len(p)
    R = frame_from_z(a)
    p05 = p - D6 * a
    r = np.hypot(p05[:, 0], p05[:, 1])
    ok_any = np.zeros(N, bool)
    good = r >= D4
    psi = np.arctan2(p05[:, 1], p05[:, 0])
    phi = np.arccos(np.clip(D4 / np.maximum(r, 1e-12), -1, 1))
    a1, d1 = UR_DH[0][0], UR_DH[0][1]
    for t1 in (psi + phi + math.pi / 2, psi - phi + math.pi / 2):
        c1, s1 = np.cos(t1), np.sin(t1)
        # T16 = A1(t1)^-1 T：位置和姿态在坐标系 1 中的分量
        def to1(v, is_point):
            x, y, z = v[:, 0], v[:, 1], v[:, 2] - (d1 if is_point else 0.0)
            u, w = c1 * x + s1 * y, -s1 * x + c1 * y
            return np.stack([u, z, -w], axis=1)          # 绕 x 转 −90°
        P16 = to1(p, True)
        R16 = np.stack([to1(R[:, :, k], False) for k in range(3)], axis=2)
        c5 = np.clip((P16[:, 2] - D4) / D6, -1, 1)
        for sgn in (1.0, -1.0):
            t5 = sgn * np.arccos(c5)
            s5 = np.sin(t5)
            # T61 = T16^-1：第 3 列的前两个分量
            R61 = np.transpose(R16, (0, 2, 1))
            s5s = np.where(np.abs(s5) < 1e-12, 1e-12, s5)
            t6 = np.arctan2(-R61[:, 1, 2] / s5s, R61[:, 0, 2] / s5s)
            # T14 = T16 · A6^-1 · A5^-1，只需要它把点 (0, −d4, 0) 送到哪里
            T16 = np.zeros((N, 4, 4))
            T16[:, :3, :3], T16[:, :3, 3], T16[:, 3, 3] = R16, P16, 1
            A6i = _batch_inv(_batch_A(5, t6))
            A5i = _batch_inv(_batch_A(4, t5))
            T14 = T16 @ A6i @ A5i
            p13 = np.einsum("nij,j->ni", T14, np.array([0, -D4, 0, 1.0]))[:, :3]
            n2 = (p13 ** 2).sum(1)
            c3 = (n2 - A2 * A2 - A3 * A3) / (2 * A2 * A3)
            ok_any |= good & (np.abs(c3) <= 1)
    return ok_any


def _batch_A(i, th):
    a, d, al = UR_DH[i]
    ct, st, ca, sa = np.cos(th), np.sin(th), math.cos(al), math.sin(al)
    N = len(th)
    A = np.zeros((N, 4, 4))
    A[:, 0, 0], A[:, 0, 1], A[:, 0, 2], A[:, 0, 3] = ct, -st * ca, st * sa, a * ct
    A[:, 1, 0], A[:, 1, 1], A[:, 1, 2], A[:, 1, 3] = st, ct * ca, -ct * sa, a * st
    A[:, 2, 1], A[:, 2, 2], A[:, 2, 3] = sa, ca, d
    A[:, 3, 3] = 1
    return A


def _batch_inv(T):
    R, p = T[:, :3, :3], T[:, :3, 3]
    o = np.zeros_like(T)
    o[:, :3, :3] = np.transpose(R, (0, 2, 1))
    o[:, :3, 3] = -np.einsum("nji,nj->ni", R, p)
    o[:, 3, 3] = 1
    return o


def sphere_dirs(n):
    """球面上近似均匀的 n 个单位矢量（斐波那契网格）。"""
    k = np.arange(n) + 0.5
    z = 1 - 2 * k / n
    phi = math.pi * (3 - math.sqrt(5)) * k
    r = np.sqrt(1 - z * z)
    return np.stack([r * np.cos(phi), r * np.sin(phi), z], axis=1)


# ---------------------------------------------------------------- SCARA（零件库 B-SCA-WQ4）

SC_L1, SC_L2, SC_H0, SC_STROKE = 0.35, 0.25, 0.242, 0.15         # 两段水平臂、零位时工具连杆原点的高度、丝杠行程 (m)


def scara_limits():
    e = json.loads((MODELS / "B-SCA-WQ4" / "entry.json").read_text(encoding="utf-8"))
    return {j["name"]: (j["limit"]["lower"], j["limit"]["upper"]) for j in e["robot"]["joints"]}


def scara_reach_xy(x, y, lim1, lim2):
    """水平位置 (x, y) 能否由关节 1、2 在限位内到达（两种肘向任一可行即可）。"""
    r2 = x * x + y * y
    c2 = (r2 - SC_L1 ** 2 - SC_L2 ** 2) / (2 * SC_L1 * SC_L2)
    ok = np.abs(c2) <= 1
    c2 = np.clip(c2, -1, 1)
    res = np.zeros_like(x, bool)
    for s in (1.0, -1.0):
        t2 = s * np.arccos(c2)
        t1 = np.arctan2(y, x) - np.arctan2(SC_L2 * np.sin(t2), SC_L1 + SC_L2 * np.cos(t2))
        t1 = (t1 + np.pi) % (2 * np.pi) - np.pi
        res |= ok & (t1 >= lim1[0]) & (t1 <= lim1[1]) & (t2 >= lim2[0]) & (t2 <= lim2[1])
    return res


# ---------------------------------------------------------------- 零件库模型（同 ch12/code/_poe.py 的 Model）

def _glb_nodes(path: Path) -> dict:
    b = path.read_bytes()
    n = struct.unpack("<I", b[12:16])[0]
    js = json.loads(b[20:20 + n])
    nodes = {}
    for nd in js["nodes"]:
        m = np.eye(4)
        if "matrix" in nd:
            m = np.array(nd["matrix"], float).reshape(4, 4).T
        nodes[nd.get("name")] = {"m": m, "children": [js["nodes"][c].get("name") for c in nd.get("children", [])]}
    return nodes


class Model:
    """零件库机器人：关节表 + 网页模型的节点矩阵；坐标以机器人基座坐标系 {s} 表示。"""

    def __init__(self, eid: str, base: str, tool_link: str, tool_xyz=(0, 0, 0)):
        d = MODELS / eid
        self.entry = json.loads((d / "entry.json").read_text(encoding="utf-8"))
        self.nodes = _glb_nodes(d / "default.glb")
        self.base = base
        self.tool_link, self.tool_xyz = tool_link, np.asarray(tool_xyz, float)
        self.joints = [j for j in self.entry["robot"]["joints"] if j["type"] != "fixed"]
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
                M = np.eye(4)
                if j["type"] == "prismatic":
                    M[:3, 3] = a * t
                else:
                    M[:3, :3] = rot(a / np.linalg.norm(a), t)
                T = T @ M
        tool = np.eye(4)
        tool[:3, 3] = self.tool_xyz
        return T @ tool




# ---------------------------------------------------------------- 平面 2R 臂与圆形障碍物（11.3 节）

L1, L2 = 0.425, 0.392                      # 大臂、小臂 (m)，同 UR5e
OBS_C, OBS_R = np.array([0.45, 0.35]), 0.10


def segdist(p, a, b):
    ab = b - a
    t = np.clip(((p - a) * ab).sum(-1) / (ab * ab).sum(-1), 0, 1)[..., None]
    return np.linalg.norm(p - (a + t * ab), axis=-1)


def fk2(t1, t2):
    t1, t2 = np.asarray(t1, float), np.asarray(t2, float)
    e = np.stack([L1 * np.cos(t1), L1 * np.sin(t1)], -1)
    w = e + np.stack([L2 * np.cos(t1 + t2), L2 * np.sin(t1 + t2)], -1)
    return e, w


def collide(t1, t2):
    """两根连杆（看作线段）是否碰到圆形障碍物。"""
    e, w = fk2(t1, t2)
    o = np.zeros_like(e)
    return (segdist(OBS_C, o, e) < OBS_R) | (segdist(OBS_C, e, w) < OBS_R)


def wrap(a):
    return (np.asarray(a) + np.pi) % (2 * np.pi) - np.pi




# ---------------------------------------------------------------- 闭链与约束（11.5 节）

FB = (0.40, 0.15, 0.35, 0.30)              # 四杆机构：机架、曲柄、连杆、摇杆 (m)
FB_NG = (0.58, 0.15, 0.35, 0.30)           # 机架加长到 0.58 m：不满足格拉斯霍夫条件
DELTA = dict(Rb=0.15, Rp=0.04, La=0.22, Lb=0.5)     # 零件库 B-PAR-DELTA 的尺寸 (m)
AGV_R, AGV_B = 0.05, 0.26                  # 零件库 B-EDU-DIFF：轮半径、轮距 (m)


def fourbar(l0, l1, l2, l3, t1, mode):
    """曲柄角 t1 时摇杆角 θ3（两种装配模式 mode = ±1；mode = −1 为开式，+1 为交叉式）；无解返回 None。
    铰点：A(0,0)、D(l0,0)，B = A + l1 e(t1)，C = D + l3 e(θ3)：以 B 为圆心 l2、以 D 为圆心 l3 两圆求交。"""
    B = np.array([l1 * math.cos(t1), l1 * math.sin(t1)])
    D = np.array([l0, 0.0])
    d = np.linalg.norm(D - B)
    if d > l2 + l3 or d < abs(l2 - l3):
        return None
    a = (l3 ** 2 - l2 ** 2 + d * d) / (2 * d)          # 从 D 沿 DB 方向
    hh = math.sqrt(max(l3 ** 2 - a * a, 0))
    e = (B - D) / d
    C = D + a * e + mode * hh * np.array([-e[1], e[0]])
    return math.atan2(C[1] - D[1], C[0] - D[0])


def agv_drive(wR, wL, dt=1e-3, r=AGV_R, b=AGV_B):
    """差速 AGV 按约束 (11.5.13) 积分（每步按圆弧精确积分）。q = (x, y, φ, θR, θL)，返回每一步之后的 q（N×5）。"""
    q = np.zeros(5)
    out = []
    for a, c in zip(wR, wL):
        v, om = r * (a + c) / 2, r * (a - c) / b
        ph = q[2]
        if abs(om) < 1e-12:
            q[0] += v * dt * math.cos(ph)
            q[1] += v * dt * math.sin(ph)
        else:
            q[0] += v / om * (math.sin(ph + om * dt) - math.sin(ph))
            q[1] += -v / om * (math.cos(ph + om * dt) - math.cos(ph))
        q[2] += om * dt
        q[3] += a * dt
        q[4] += c * dt
        out.append(q.copy())
    return np.array(out)


def agv_programs(dt=1e-3, T=4.0):
    """11.5 节的两种轮速过程：过程 A 两轮变速同时转；过程 B 先只转右轮、再只转左轮，两轮总转角与 A 相同。"""
    t = np.arange(0, T, dt)
    wR1, wL1 = 10 + 6 * np.sin(1.3 * t), 10 - 4 * np.cos(0.7 * t)
    qa = agv_drive(wR1, wL1, dt)
    TR, TL = qa[-1, 3], qa[-1, 4]
    n = len(t) // 2
    wR2 = np.r_[np.full(n, TR / (n * dt)), np.zeros(len(t) - n)]
    wL2 = np.r_[np.zeros(n), np.full(len(t) - n, TL / ((len(t) - n) * dt))]
    qb = agv_drive(wR2, wL2, dt)
    return qa, qb
