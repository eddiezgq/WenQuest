"""第 17 章共用：旋量、矩阵指数与对数、伴随矩阵，空间雅可比与物体雅可比，零件库模型的读法（与第 12、15、16 章相同，
这里重写一份，使本章程序自成一体）；平面 3R 臂；UR5e 的旋量轴（表 12.1.1）；Panda 的旋量轴、限位与连杆折线；
以及本章新加的部分：任务雅可比、零空间矢量（广义叉积）、自运动的追踪、可操作度的梯度、点到线段的距离。
以下划线开头，构建时不单独运行。
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
    w = np.asarray(w, float)
    return np.r_[w, -np.cross(w, np.asarray(q, float))]


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


def act(T, p):
    return T[:3, :3] @ np.asarray(p, float) + T[:3, 3]


def wrap(a):
    return math.atan2(math.sin(a), math.cos(a))


def fk_space(Slist, M, theta):
    T = np.eye(4)
    for S, t in zip(Slist, theta):
        T = T @ exp6(S, t)
    return T @ M


def logR(R):
    c = max(-1.0, min(1.0, (np.trace(R) - 1) / 2))
    th = math.acos(c)
    if th < 1e-9:
        return np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / 2
    if math.pi - th < 1e-6:
        B = (R + np.eye(3)) / 2
        k = int(np.argmax(np.diag(B)))
        return B[:, k] / math.sqrt(B[k, k]) * th
    return th / (2 * math.sin(th)) * np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])


def log_twist(T):
    """SE(3) 的对数映射（定理 6.4.3）。"""
    R, p = T[:3, :3], T[:3, 3]
    wth = logR(R)
    th = float(np.linalg.norm(wth))
    if th < 1e-12:
        return np.r_[np.zeros(3), p]
    w = wth / th
    K = skew(w)
    Ginv = np.eye(3) / th - 0.5 * K + (1 / th - 0.5 / math.tan(th / 2)) * K @ K
    return np.r_[wth, th * (Ginv @ p)]


def adjoint(T):
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


def jacobian_space(Slist, theta):
    """空间雅可比（定理 16.1.1）。"""
    n = len(theta)
    J = np.zeros((6, n))
    T = np.eye(4)
    for i in range(n):
        J[:, i] = adjoint(T) @ Slist[i]
        T = T @ exp6(Slist[i], theta[i])
    return J


def jacobian_body(Blist, theta):
    n = len(theta)
    J = np.zeros((6, n))
    T = np.eye(4)
    for i in range(n - 1, -1, -1):
        J[:, i] = adjoint(T) @ Blist[i]
        T = T @ exp6(Blist[i], -theta[i])
    return J


def body_screws(Slist, M):
    A = adjoint(inv(M))
    return [A @ S for S in Slist]


def geometric_jacobian(Slist, M, theta):
    """几何雅可比（定义 16.2.1）：行为 (ω_s, ṗ)，ṗ 是末端原点的速度。J_g = [[I, 0], [−[p], I]] J_s。"""
    p = fk_space(Slist, M, theta)[:3, 3]
    P = np.eye(6)
    P[3:, :3] = -skew(p)
    return P @ jacobian_space(Slist, theta)


def dJs_dtheta(Js, k):
    """空间雅可比对 θ_k 的偏导数（由定理 16.1.3 取 θ̇ = e_k）：第 i 列为 [ad_{J_sk}] J_si（k < i），否则为零。"""
    D = np.zeros_like(Js)
    for i in range(k + 1, Js.shape[1]):
        D[:, i] = ad(Js[:, k]) @ Js[:, i]
    return D


# ---------------------------------------------------------------- 零件库模型（与第 12、16 章相同的读法）

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
    """零件库机器人：关节表 + 网页模型的节点矩阵；正运动学按三维引擎的做法逐个连杆计算（与指数积无关的另一种算法）。"""

    def __init__(self, eid, base, tool_link, joints):
        d = MODELS / eid
        self.entry = json.loads((d / "entry.json").read_text(encoding="utf-8"))
        self.nodes = _glb_nodes(d / "default.glb")
        self.base, self.tool_link = base, tool_link
        js = {j["name"]: j for j in self.entry["robot"]["joints"]}
        self.joints = [js[n] for n in joints]
        self.by_child = {j["child"]: j for j in self.joints}
        parent = {c: p for p, nd in self.nodes.items() for c in nd["children"]}
        chain, n = [], tool_link
        while n != base:
            chain.insert(0, n)
            n = parent[n]
        self.chain = chain

    def frames(self, theta):
        """各连杆坐标系的位姿（按 chain 的次序）。"""
        val = {j["name"]: t for j, t in zip(self.joints, theta)}
        T = self.nodes[self.base]["m"].copy()
        out = {}
        for n in self.chain:
            T = T @ self.nodes[n]["m"]
            j = self.by_child.get(n)
            if j is not None:
                Mj = np.eye(4)
                Mj[:3, :3] = rot(np.asarray(j["axis"], float) / np.linalg.norm(j["axis"]), val.get(j["name"], 0.0))
                T = T @ Mj
            out[n] = T.copy()
        return out

    def fk(self, theta):
        return self.frames(theta)[self.tool_link]


# ---------------------------------------------------------------- Panda（零件库 B-ARM-PANDA）

PANDA = Model("B-ARM-PANDA", "link0", "hand", [f"joint{i}" for i in range(1, 8)])


def _panda_screws():
    S, Q, W = [], [], []
    T = PANDA.nodes[PANDA.base]["m"].copy()
    for n in PANDA.chain:
        T = T @ PANDA.nodes[n]["m"]
        j = PANDA.by_child.get(n)
        if j is None:
            continue
        w = T[:3, :3] @ np.asarray(j["axis"], float)
        S.append(screw_revolute(w, T[:3, 3]))
        W.append(w)
        Q.append(T[:3, 3].copy())
    return S, W, Q


PA_S, PA_W, PA_Q = _panda_screws()
PA_M = PANDA.fk(np.zeros(7))
PA_LO = np.array([j["limit"]["lower"] for j in PANDA.joints])
PA_HI = np.array([j["limit"]["upper"] for j in PANDA.joints])
PA_READY = np.array([0, -math.pi / 4, 0, -3 * math.pi / 4, 0, math.pi / 2, math.pi / 4])
PA_QDMAX = np.array([2.175, 2.175, 2.175, 2.175, 2.61, 2.61, 2.61])     # 关节速度上限（rad/s，Franka 文档，17.4 节）
PA_TAUMAX = np.array([87.0, 87, 87, 87, 12, 12, 12])                    # 关节力矩上限（N·m，同上）


def pa_fk(theta):
    return fk_space(PA_S, PA_M, theta)


def pa_js(theta):
    return jacobian_space(PA_S, theta)


def pa_jg(theta):
    return geometric_jacobian(PA_S, PA_M, theta)


def pa_points(theta):
    """Panda 的连杆折线（作图、求距离用），8 个点：基座、肩 S（关节 1、2、3 三轴的交点）、上臂顶端 A、肘 E（关节 4 的
    轴上点）、前臂起点 B、腕 W（关节 5、6 两轴的交点）、关节 7 的轴上点 C、法兰中心 F（{b} 的原点）。
    各点取零位时的位置（表 12.3.1），由它所在连杆之前的关节搬到此刻的位置。"""
    Es = [np.eye(4)]
    for S, t in zip(PA_S, theta):
        Es.append(Es[-1] @ exp6(S, t))
    zs, ze, zw = PA_Q[1][2], PA_Q[3][2], PA_Q[5][2]
    pts = [np.zeros(3), np.array([0, 0, zs]),
           act(Es[3], [0, 0, ze]), act(Es[3], PA_Q[3]),
           act(Es[4], [0, 0, ze]), act(Es[4], [0, 0, zw]),
           act(Es[6], PA_Q[6]), act(Es[7] @ PA_M, np.zeros(3))]
    return np.array(pts)


PA_E, PA_WR = 3, 5          # pa_points 中肘点、腕点的序号


def pa_elbow(theta):
    return pa_points(theta)[PA_E]


def pa_wrist(theta):
    return pa_points(theta)[PA_WR]


# ---------------------------------------------------------------- UR5e（表 12.1.1）

H1, W1, L1, W2, L2, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1
YD = np.array([0, -1.0, 0])
UR_W = [np.array([0, 0, 1.0]), YD, YD, YD, np.array([0, 0, -1.0]), YD]
UR_Q = [np.array([0, 0, H1]), np.array([0, -W1, H1]), np.array([-L1, -W1 + W2, H1]), np.array([-L1 - L2, -W1 + W2, H1]),
        np.array([-L1 - L2, -W1 + W2 - W3, H1]), np.array([-L1 - L2, -W1 + W2 - W3, H1 - H2])]
UR_S = [screw_revolute(w, q) for w, q in zip(UR_W, UR_Q)]
UR_M = np.array([[1.0, 0, 0, -L1 - L2], [0, -1, 0, -W1 + W2 - W3 - W4], [0, 0, -1, H1 - H2], [0, 0, 0, 1]])
TH_STAR = np.radians([30, -60, 90, -120, -90, 45])


def ur_fk(theta):
    return fk_space(UR_S, UR_M, theta)


# ---------------------------------------------------------------- 平面臂

PL = (0.425, 0.392, 0.1)


def joints_planar(th, L=PL):
    a = np.cumsum(th)
    pts = [np.zeros(2)]
    for l, t in zip(L, a):
        pts.append(pts[-1] + l * np.array([math.cos(t), math.sin(t)]))
    return np.array(pts)


def tip_planar(th, L=PL):
    return joints_planar(th, L)[-1]


def jac_planar(th, L=PL):
    """平面 nR 臂末端位置的雅可比（2×n）：第 i 列是 ẑ × (p − p_i)。"""
    pts = joints_planar(th, L)
    J = np.zeros((2, len(th)))
    for i in range(len(th)):
        d = pts[-1] - pts[i]
        J[:, i] = [-d[1], d[0]]
    return J


def ik2r(x, y, l1, l2):
    """平面 2R 臂的两组解析解（第 14 章），够不着时返回空表。"""
    c2 = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2)
    if abs(c2) > 1 + 1e-12:
        return []
    c2 = max(-1.0, min(1.0, c2))
    out = []
    for s in (1, -1):
        t2 = s * math.acos(c2)
        t1 = math.atan2(y, x) - math.atan2(l2 * math.sin(t2), l1 + l2 * math.cos(t2))
        out.append((wrap(t1), t2))
    return out


# ---------------------------------------------------------------- 本章新加的部分

def null_vector(J):
    """m×(m+1) 矩阵的广义叉积（定理 17.2.1）：c_i = (−1)^{m+1+i} det J_(i)（i 从 1 数起），J_(i) 为删去第 i 列的方阵。
    满足 J c = 0、det[J; cᵀ] = ‖c‖² ≥ 0、‖c‖² = det(J Jᵀ)。"""
    m, n = J.shape
    assert n == m + 1
    c = np.zeros(n)
    for i in range(n):
        c[i] = (-1) ** (m + 1 + (i + 1)) * np.linalg.det(np.delete(J, i, axis=1))
    return c


def manip(J):
    return float(math.sqrt(max(0.0, np.linalg.det(J @ J.T))))


def pinv_rows(J):
    """行满秩矩阵的伪逆 Jᵀ(J Jᵀ)⁻¹。"""
    return J.T @ np.linalg.inv(J @ J.T)


def manip_grad(Slist, theta, rows=None):
    """可操作度 w = √det(J Jᵀ) 的梯度（定理 17.3.2）：∂w/∂θ_k = w · tr(J⁺ ∂J/∂θ_k)；J 取空间雅可比的若干行。"""
    Js = jacobian_space(Slist, theta)
    sel = slice(None) if rows is None else rows
    J = Js[sel]
    w = manip(J)
    Jp = pinv_rows(J)
    g = np.zeros(len(theta))
    for k in range(len(theta)):
        g[k] = w * np.trace(Jp @ dJs_dtheta(Js, k)[sel])
    return w, g


def seg_dist(p, a, b):
    """点 p 到线段 ab 的距离与线段上的最近点、最近点的参数 s ∈ [0, 1]。"""
    ab = b - a
    s = float(np.clip((p - a) @ ab / (ab @ ab), 0.0, 1.0))
    c = a + s * ab
    return float(np.linalg.norm(p - c)), c, s


def joint_mid_cost(theta, lo, hi):
    """式 (15.4.6) 的 H(θ) = Σ ((θ_i − θ̄_i)/(θ_max,i − θ_min,i))² 及其梯度。"""
    mid, rng = (lo + hi) / 2, hi - lo
    d = (theta - mid) / rng
    return float(d @ d), 2 * d / rng


def lim_margin(theta, lo, hi):
    """各关节到较近一侧限位的距离与限位范围之比（0 为顶在限位上，0.5 为在中点）。"""
    return np.minimum(theta - lo, hi - theta) / (hi - lo)


def pose_error_s(T, Td):
    """位姿误差：{s} 中的旋量 e = (ω, v) 使 e^{[e]} T = T_d，即 e = log(T_d T⁻¹)。"""
    return log_twist(Td @ inv(T))


def pose_error_g(T, Td):
    """几何雅可比所用的误差：(姿态误差的转动矢量（{s} 中）, 位置误差 p_d − p)。"""
    return np.r_[logR(Td[:3, :3] @ T[:3, :3].T), Td[:3, 3] - T[:3, 3]]


def pa_unit_null(q):
    c = null_vector(pa_js(q))
    return c / np.linalg.norm(c)


def pa_trace(qs, Td, h=0.01, correct=True, maxs=4000):
    """沿 Panda 的单位零空间矢量追踪自运动（17.2 节）：两阶龙格-库塔（中点法）预测一步 h，再用牛顿法把末端拉回 T_d
    （每步三次）；回到起点（模 2π）时停止。返回各点的关节角（不取模，连续）。"""
    q, pts = np.array(qs, float), [np.array(qs, float)]
    for k in range(maxs):
        q = q + h * pa_unit_null(q + 0.5 * h * pa_unit_null(q))
        if correct:
            for _ in range(3):
                q = q + pinv_rows(pa_js(q)) @ pose_error_s(pa_fk(q), Td)
        d = np.array([wrap(x) for x in q - qs])
        if k > 50 and np.linalg.norm(d) < 0.6 * h:
            break
        pts.append(q.copy())
    return np.array(pts)
