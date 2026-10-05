"""第 18 章共用：旋量与矩阵指数，平面 2R 臂与平面五杆机器人，Stewart 平台（几何同算例 11.5.4），
Delta（零件库 B-PAR-DELTA）的逆解、正解（三球求交）、速度关系与约束力偶，零件库模型的读法。
以下划线开头，构建时不单独运行。

旋量、指数和读模型的函数与前几章相同（ch11/code/_ch11.py、ch16/code/_jac.py），这里另存一份，
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


def rpy(roll, pitch, yaw):
    """绕固定轴 x、y、z 依次转 roll、pitch、yaw（RPY），即 ZYX 欧拉角 (yaw, pitch, roll)，4.5 节。"""
    return rot([0, 0, 1], yaw) @ rot([0, 1, 0], pitch) @ rot([1, 0, 0], roll)


def screw_revolute(w, q):
    """转动关节的旋量轴 S = (ω, −ω × q)，式 (12.1.3)。"""
    w = np.asarray(w, float)
    return np.r_[w, -np.cross(w, np.asarray(q, float))]


def screw_prismatic(v):
    """移动关节的旋量轴 S = (0, v)，式 (12.1.4)。"""
    return np.r_[np.zeros(3), np.asarray(v, float)]


def force_wrench(s, q):
    """作用线过点 q、方向为单位矢量 s 的单位力的力旋量 ℱ = (q × s, s)（力矩在前，6.6 节）。"""
    s = np.asarray(s, float)
    return np.r_[np.cross(np.asarray(q, float), s), s]


def couple_wrench(m):
    """纯力偶 ℱ = (m, 0)。"""
    return np.r_[np.asarray(m, float), np.zeros(3)]


def exp6(S, t=1.0):
    """e^{[S]θ}，式 (12.1.5)。S 不必是单位旋量。"""
    S = np.asarray(S, float) * t
    w, v = S[:3], S[3:]
    T = np.eye(4)
    th = np.linalg.norm(w)
    if th < 1e-12:
        T[:3, 3] = v
        return T
    wh, vh = w / th, v / th
    K = skew(wh)
    T[:3, :3] = rot(wh, th)
    G = np.eye(3) * th + (1 - math.cos(th)) * K + (th - math.sin(th)) * K @ K
    T[:3, 3] = G @ vh
    return T


def adjoint(T):
    """[Ad_T] = [[R 0]; [[p]R R]]，式 (6.5.4)。"""
    R, p = T[:3, :3], T[:3, 3]
    A = np.zeros((6, 6))
    A[:3, :3] = R
    A[3:, 3:] = R
    A[3:, :3] = skew(p) @ R
    return A


def pose(R, p):
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = p
    return T


def null_space(A, tol=1e-9):
    """A 的零空间的一组标准正交基（按列）与秩，用奇异值分解（2.4 节）。"""
    u, s, vt = np.linalg.svd(np.atleast_2d(A))
    r = int((s > tol * max(1.0, s[0] if len(s) else 1.0)).sum())
    return vt[r:].T, r


def reciprocal(S1, S2):
    """互易积 (6.6.10)：两个旋量都按“方向在前、矩在后”书写。"""
    return S1[:3] @ S2[3:] + S2[:3] @ S1[3:]


def power(F, V):
    """力旋量 ℱ = (m, f) 对运动旋量 𝒱 = (ω, v) 的功率 ℱᵀ𝒱，式 (6.6.3)。"""
    return float(np.asarray(F) @ np.asarray(V))


# ---------------------------------------------------------------- 平面 2R 臂与平面五杆机器人（18.1、18.2 节）

FIVE = dict(c=0.15, l1=0.20, l2=0.30)       # 五杆：两台电机在 (∓c, 0)，主动杆 l1，从动杆 l2；同 11.2 节的五杆机构
ARM2 = dict(L1=0.20, L2=0.30)               # 对照的 2R 串联臂：基座在原点，大臂 L1、小臂 L2


def e2(t):
    return np.array([math.cos(t), math.sin(t)])


def ep2(t):
    """e(t) 逆时针转 90°：de/dt。"""
    return np.array([-math.sin(t), math.cos(t)])


def five_motors(c=FIVE["c"]):
    return np.array([-c, 0.0]), np.array([c, 0.0])


def five_leg_ik(P, A, sigma, l1=FIVE["l1"], l2=FIVE["l2"]):
    """一条支链（从电机 A 出发的 2R）的逆解：|P − A − l1 e(θ)| = l2。sigma = ±1 选两个解中的一个。无解返回 None。"""
    d = np.asarray(P, float) - A
    r = np.hypot(*d)
    c = (l1 * l1 + r * r - l2 * l2) / (2 * l1 * r) if r > 1e-12 else 2.0
    if abs(c) > 1:
        return None
    return math.atan2(d[1], d[0]) + sigma * math.acos(c)


SIG_OUT = (+1, -1)          # 五杆的常用工作模式：两条支链的肘部都朝外


def five_ik(P, sig=SIG_OUT, **kw):
    A1, A2 = five_motors(kw.pop("c", FIVE["c"]))
    t1, t2 = five_leg_ik(P, A1, sig[0], **kw), five_leg_ik(P, A2, sig[1], **kw)
    return None if (t1 is None or t2 is None) else np.array([t1, t2])


def five_elbows(th, c=FIVE["c"], l1=FIVE["l1"]):
    A1, A2 = five_motors(c)
    return A1 + l1 * e2(th[0]), A2 + l1 * e2(th[1])


def five_fk(th, kappa=+1, c=FIVE["c"], l1=FIVE["l1"], l2=FIVE["l2"]):
    """正解：两个肘点为圆心、半径 l2 的两圆求交；kappa = +1 取在 B1→B2 连线左侧（上方）的交点。"""
    B1, B2 = five_elbows(th, c, l1)
    d = B2 - B1
    L = np.hypot(*d)
    if L > 2 * l2 + 1e-12 or L < 1e-12:
        return None
    h = math.sqrt(max(l2 * l2 - (L / 2) ** 2, 0.0))
    n = np.array([-d[1], d[0]]) / L
    return (B1 + B2) / 2 + kappa * h * n


def five_AB(P, th, c=FIVE["c"], l1=FIVE["l1"]):
    """速度关系 A ẋ = B θ̇（式 (18.1.4)）：A 的行是从动杆矢量 P − B_i，B = diag((P − B_i)·l1 e⊥(θ_i))。"""
    B1, B2 = five_elbows(th, c, l1)
    A = np.array([P - B1, P - B2])
    B = np.diag([(P - B1) @ (l1 * ep2(th[0])), (P - B2) @ (l1 * ep2(th[1]))])
    return A, B


def arm2_ik(P, sigma=+1, L1=ARM2["L1"], L2=ARM2["L2"]):
    """2R 臂的逆解（14.2 节）：sigma = +1 取 θ2 > 0（肘部在右，从基座看向末端）。"""
    x, y = P
    c2 = (x * x + y * y - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    if abs(c2) > 1:
        return None
    t2 = sigma * math.acos(c2)
    t1 = math.atan2(y, x) - math.atan2(L2 * math.sin(t2), L1 + L2 * math.cos(t2))
    return np.array([t1, t2])


def arm2_fk(th, L1=ARM2["L1"], L2=ARM2["L2"]):
    return L1 * e2(th[0]) + L2 * e2(th[0] + th[1])


def arm2_J(th, L1=ARM2["L1"], L2=ARM2["L2"]):
    t1, t12 = th[0], th[0] + th[1]
    return np.array([[-L1 * math.sin(t1) - L2 * math.sin(t12), -L2 * math.sin(t12)],
                     [L1 * math.cos(t1) + L2 * math.cos(t12), L2 * math.cos(t12)]])


# ---------------------------------------------------------------- Stewart 平台（几何同算例 11.5.4）

ST = dict(ra=0.5, rb=0.3, h=0.6)
ST_A_DEG = [-10, 10, 110, 130, 230, 250]          # 机架上万向节中心的方位角
ST_B_DEG = [-50, 50, 70, 170, 190, 290]           # 动平台上球关节中心的方位角（平台坐标系）
ST_A = np.array([ST["ra"] * np.array([math.cos(t), math.sin(t), 0.0]) for t in np.radians(ST_A_DEG)])
ST_B = np.array([ST["rb"] * np.array([math.cos(t), math.sin(t), 0.0]) for t in np.radians(ST_B_DEG)])
ST_HOME = pose(np.eye(3), [0, 0, ST["h"]])
ST_LMIN, ST_LMAX = 0.55, 0.85                     # 电动缸的长度范围（本章取定）


def st_points(T):
    """动平台上六个球关节中心在 {s} 中的位置 q_i = p + R b_i。"""
    return (T[:3, :3] @ ST_B.T).T + T[:3, 3]


def st_ik(T):
    """逆解 (11.5.9)：l_i = |p + R b_i − a_i|。"""
    return np.linalg.norm(st_points(T) - ST_A, axis=1)


def st_W(T):
    """六条腿的单位力旋量按列排成的 6×6 矩阵 Aᵀ = (ℱ_1 … ℱ_6)，ℱ_i = (a_i × ŝ_i, ŝ_i)；书中的 A 是它的转置，腿长速度 l̇ = A𝒱_s（式 (18.3.3)）。"""
    q = st_points(T)
    s = q - ST_A
    s = s / np.linalg.norm(s, axis=1)[:, None]
    return np.array([force_wrench(si, ai) for si, ai in zip(s, ST_A)]).T


def st_fk(lengths, T0, tol=1e-12, itmax=50, hist=None):
    """正解：牛顿法 (18.3.5)。T ← exp([Δ𝒱]) T，A Δ𝒱 = l − l(T)。返回 (T, 迭代次数, 是否收敛)。"""
    T = T0.copy()
    for k in range(itmax):
        r = np.asarray(lengths) - st_ik(T)
        if hist is not None:
            hist.append(np.abs(r).max())
        if np.abs(r).max() < tol:
            return T, k, True
        W = st_W(T)
        try:
            dV = np.linalg.solve(W.T, r)
        except np.linalg.LinAlgError:
            return T, k, False
        n = np.linalg.norm(dV)
        if n > 0.5:                                   # 限步长（15.5 节）：一步不超过 0.5（rad 与 m 混合）
            dV *= 0.5 / n
        T = exp6(dV) @ T
    return T, itmax, False


# ---------------------------------------------------------------- Delta（零件库 B-PAR-DELTA）

DELTA = dict(Rb=0.15, Rp=0.04, La=0.22, Lb=0.5)
D_LO, D_HI = math.radians(-40), math.radians(90)      # 主动臂限位
D_WMAX = 10.471976                                    # 主动臂转速上限 (rad/s)，模型 entry.json：600°/s
D_REST = np.array([0, 0, -0.42])


def ek(k):
    f = 2 * math.pi * k / 3
    return np.array([math.cos(f), math.sin(f), 0.0])


def tk(k):
    """支链 k 主动臂的转轴方向 t_k = ẑ × e_k。"""
    return np.cross([0, 0, 1.0], ek(k))


def elbow(k, th, D=DELTA):
    """肘点 E_k = R_b e_k + L_a(cos θ e_k − sin θ ẑ)。"""
    e = ek(k)
    return D["Rb"] * e + D["La"] * (math.cos(th) * e - math.sin(th) * np.array([0, 0, 1.0]))


def delbow(k, th, D=DELTA):
    """∂E_k/∂θ_k。"""
    e = ek(k)
    return D["La"] * (-math.sin(th) * e - math.cos(th) * np.array([0, 0, 1.0]))


def delta_leg_ik(k, p, sign=1, D=DELTA):
    """式 (11.5.7)：A cos θ + B sin θ = C；sign = +1 为肘部朝外的解。无解返回 None。"""
    e = ek(k)
    q = np.asarray(p, float) + (D["Rp"] - D["Rb"]) * e
    u, h = q @ e, q[2]
    A, B = -2 * D["La"] * u, 2 * D["La"] * h
    C = D["Lb"] ** 2 - D["La"] ** 2 - q @ q
    r = math.hypot(A, B)
    if abs(C) > r:
        return None
    t = math.atan2(B, A) + sign * math.acos(C / r)
    return math.atan2(math.sin(t), math.cos(t))


def delta_ik(p, D=DELTA):
    th = [delta_leg_ik(k, p, 1, D) for k in range(3)]
    return None if any(t is None for t in th) else np.array(th)


def delta_fk(th, D=DELTA, lower=True):
    """正解：三个球心 c_k = E_k − R_p e_k，半径 L_b，三球求交（式 (11.5.8)），取下方的交点。"""
    c = [elbow(k, th[k], D) - D["Rp"] * ek(k) for k in range(3)]
    ex = c[1] - c[0]
    d = np.linalg.norm(ex)
    ex = ex / d
    i = ex @ (c[2] - c[0])
    ey = c[2] - c[0] - i * ex
    ey = ey / np.linalg.norm(ey)
    ez = np.cross(ex, ey)
    j = ey @ (c[2] - c[0])
    R = D["Lb"]
    x = d / 2
    y = (i * i + j * j - 2 * i * x) / (2 * j)
    z2 = R * R - x * x - y * y
    if z2 < 0:
        return None
    z = math.sqrt(z2)
    P1, P2 = c[0] + x * ex + y * ey + z * ez, c[0] + x * ex + y * ey - z * ez
    return min(P1, P2, key=lambda P: P[2]) if lower else max(P1, P2, key=lambda P: P[2])


def delta_u(p, th, D=DELTA):
    """三根从动杆的单位方向 u_k（从肘点指向动平台上的球关节）。"""
    U = []
    for k in range(3):
        d = np.asarray(p) + D["Rp"] * ek(k) - elbow(k, th[k], D)
        U.append(d / np.linalg.norm(d))
    return np.array(U)


def delta_AB(p, th, D=DELTA):
    """速度关系 A v = B θ̇（式 (18.4.2)）：A 的第 k 行为 u_kᵀ，B = diag(u_k·∂E_k/∂θ_k)。"""
    U = delta_u(p, th, D)
    B = np.diag([U[k] @ delbow(k, th[k], D) for k in range(3)])
    return U, B


def delta_J(p, th, D=DELTA):
    A, B = delta_AB(p, th, D)
    return np.linalg.solve(A, B)


def delta_couples(p, th, D=DELTA):
    """三条支链的约束力偶方向 n_k = t_k × u_k（18.2 节），按行排列。"""
    U = delta_u(p, th, D)
    return np.array([np.cross(tk(k), U[k]) for k in range(3)])


def delta_ok(p, D=DELTA):
    """p 在工作空间内（三条支链都有肘部朝外的解，且在限位以内）时返回转角，否则 None。"""
    th = delta_ik(p, D)
    if th is None or (th < D_LO - 1e-12).any() or (th > D_HI + 1e-12).any():
        return None
    return th


def v_guaranteed(J, wmax=D_WMAX):
    """电机转速不超过 wmax 时，平台在任何方向上都能达到的速度：wmax / max_k ‖J⁻¹ 的第 k 行‖（式 (18.4.5)）。"""
    Ji = np.linalg.inv(J)
    return wmax / np.linalg.norm(Ji, axis=1).max()


def v_along(J, d, wmax=D_WMAX):
    """沿单位方向 d 运动时，电机转速不超过 wmax 所允许的最大速度：wmax / ‖J⁻¹d‖_∞（式 (18.4.4)）。"""
    return wmax / np.abs(np.linalg.solve(J, d)).max()


# ---------------------------------------------------------------- 零件库模型（同 ch11/code/_ch11.py）

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


def delta_model_elbows(th):
    """按零件库模型（entry.json 的关节表 + default.glb 的节点矩阵）算三根主动臂的末端：与 elbow() 无关的另一种算法。"""
    d = MODELS / "B-PAR-DELTA"
    entry = json.loads((d / "entry.json").read_text(encoding="utf-8"))
    nodes = _glb_nodes(d / "default.glb")
    base = nodes["base"]["m"]
    out = []
    for k, j in enumerate(entry["robot"]["joints"]):
        Tn = base @ nodes[j["child"]]["m"]
        a = np.asarray(j["axis"], float)
        M = np.eye(4)
        M[:3, :3] = rot(a / np.linalg.norm(a), th[k])
        T = Tn @ M
        out.append(T[:3, :3] @ np.array([DELTA["La"], 0, 0]) + T[:3, 3])
    return np.array(out), entry


def _exp6_batch(V):
    """一批运动旋量的矩阵指数（N×6 → N×4×4），用罗德里格斯公式。"""
    w, v = V[:, :3], V[:, 3:]
    th = np.linalg.norm(w, axis=1)
    small = th < 1e-12
    ths = np.where(small, 1.0, th)
    wh = w / ths[:, None]
    K = np.zeros((len(V), 3, 3))
    K[:, 0, 1], K[:, 0, 2], K[:, 1, 0], K[:, 1, 2], K[:, 2, 0], K[:, 2, 1] = -wh[:, 2], wh[:, 1], wh[:, 2], -wh[:, 0], -wh[:, 1], wh[:, 0]
    K2 = K @ K
    s, c = np.sin(th)[:, None, None], np.cos(th)[:, None, None]
    I = np.eye(3)[None]
    R = I + s * K + (1 - c) * K2
    G = I * ths[:, None, None] + (1 - c) * K + (ths[:, None, None] - s) * K2
    p = np.einsum("nij,nj->ni", G, v / ths[:, None])
    R[small], p[small] = np.eye(3), v[small]
    T = np.zeros((len(V), 4, 4))
    T[:, :3, :3], T[:, :3, 3], T[:, 3, 3] = R, p, 1.0
    return T


def st_fk_batch(lengths, T0, itmax=60, tol=1e-12, step=0.5):
    """许多个初值同时做牛顿法 (18.3.5)（与 st_fk 相同，只是向量化）。返回 (T, 是否收敛)。"""
    T = T0.copy()
    L = np.asarray(lengths)
    done = np.zeros(len(T), bool)
    for _ in range(itmax):
        q = np.einsum("nij,kj->nki", T[:, :3, :3], ST_B) + T[:, None, :3, 3]
        d = q - ST_A[None]
        l = np.linalg.norm(d, axis=2)
        r = L[None] - l
        done = np.abs(r).max(1) < tol
        if done.all():
            break
        s = d / l[..., None]
        Wt = np.concatenate([np.cross(ST_A[None].repeat(len(T), 0), s), s], axis=2)      # N×6×6，第 i 行是 ℱ_iᵀ
        ok = np.abs(np.linalg.det(Wt)) > 1e-14
        dV = np.zeros((len(T), 6))
        dV[ok] = np.linalg.solve(Wt[ok], r[ok][..., None])[..., 0]
        n = np.linalg.norm(dV, axis=1)
        dV *= np.minimum(1.0, step / np.maximum(n, 1e-300))[:, None]
        dV[done] = 0
        T = _exp6_batch(dV) @ T
    q = np.einsum("nij,kj->nki", T[:, :3, :3], ST_B) + T[:, None, :3, 3]
    r = L[None] - np.linalg.norm(q - ST_A[None], axis=2)
    return T, np.abs(r).max(1) < 1e-10


def random_rotations(n, rng):
    """n 个均匀分布的随机旋转矩阵（由单位四元数，4.6 节）。"""
    q = rng.normal(size=(n, 4))
    q /= np.linalg.norm(q, axis=1)[:, None]
    a, b, c, d = q.T
    return np.stack([np.stack([a * a + b * b - c * c - d * d, 2 * (b * c - a * d), 2 * (b * d + a * c)], -1),
                     np.stack([2 * (b * c + a * d), a * a - b * b + c * c - d * d, 2 * (c * d - a * b)], -1),
                     np.stack([2 * (b * d - a * c), 2 * (c * d + a * b), a * a - b * b - c * c + d * d], -1)], 1)


def distinct_poses(Ts, tol=1e-6):
    out = []
    for T in Ts:
        if not any(np.abs(T - S).max() < tol for S in out):
            out.append(T)
    return out
