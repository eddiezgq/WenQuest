"""第 31 章共用：结构、材料与强度。以下划线开头，构建时不单独运行。

主角仍是问渠机器人厂的 WQ-CR5。几何、零件、质量直接读机器人厂的原件 factory/digital/cae/wqcr5.py；
截面内力、关节载荷用它第 66 轮新加的 section()、joint_loads()（与问渠 CAE“WQ-CR5 大臂”示例零件的预设载荷同一段代码）；
谐波减速器的扭转刚度读零件库 D-RDC-HD-CSF 的规格表（厂商官网数据）；材料性能读问渠 CAE 的材料表 factory/digital/cae/materials.py。
WQ-CR5 的数都是示例值。
"""
import csv
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CAE = ROOT / "factory" / "digital" / "cae"
G0 = 9.81


def wqcr5():
    p = str(CAE)
    if p not in sys.path:
        sys.path.insert(0, p)
    import wqcr5 as W                    # noqa: E402
    return W


def materials():
    p = str(CAE.parent)
    if p not in sys.path:
        sys.path.insert(0, p)
    from cae import materials as MT      # noqa: E402
    return MT


W = wqcr5()
Q_OUT = np.radians(W.OUTSTRETCHED_DEG)          # 手臂水平伸直、工具朝下
SIZE = {"L": 32, "M": 25, "S": 17}              # 模组里的谐波减速器型号（与清单相同）


def harmonic_stiffness():
    """零件库 D-RDC-HD-CSF：{型号: (K1, K2, K3)}，N·m/rad（减速比 100）"""
    f = ROOT / "library" / "catalog" / "D" / "D-RDC-HD-CSF" / "specs.csv"
    out = {}
    with f.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["ratio"] == "100" and r["K1_1e4_Nm_rad"]:
                out[int(r["size_code"])] = tuple(float(r[f"K{i}_1e4_Nm_rad"]) * 1e4 for i in (1, 2, 3))
    return out


def joint_K(which=0, modules=None):
    """六个关节的扭转刚度 N·m/rad：which = 0 用 K1（小负载区，最软），2 用 K3（大负载区，最硬）"""
    K = harmonic_stiffness()
    return np.array([K[SIZE[s]][which] for s in (modules or W.JOINT_MODULE)])


def tube_props(r_out, t, E=None, nu=None):
    """薄壁圆管：面积 A、惯性矩 I、极惯性矩 J = 2I、抗弯截面系数 Wb = I/r，EI、GJ（SI 单位）"""
    E = W.E_AL if E is None else E
    nu = W.NU_AL if nu is None else nu
    ri = r_out - t
    A = math.pi * (r_out ** 2 - ri ** 2)
    I = math.pi / 4 * (r_out ** 4 - ri ** 4)
    G = E / (2 * (1 + nu))
    return {"A": A, "I": I, "J": 2 * I, "Wb": I / r_out, "EI": E * I, "GJ": G * 2 * I, "G": G}


def tubes():
    """大臂、小臂：(构件号, 名称, 外半径, 壁厚)"""
    return [(1, "upper", *W.TUBES["upper"]), (2, "fore", *W.TUBES["fore"])]


def tcp_point(q):
    """负载点（MJCF 的 tcp）在底座坐标里的位置"""
    return (W.link_world(q)[5] @ np.append(W.tcp_local(), 1.0))[:3]


def load_points(q, payload_kg=W.PAYLOAD_KG, self_weight=True):
    """重力的作用点 [(构件号, 质量 kg, 底座坐标, 是否沿管均布)]：self_weight=False 时只有负载"""
    if not self_weight:
        return [(6, payload_kg, tcp_point(q), False)]
    return [(i, m, r, ("铝管" in n or "罩壳" in n)) for i, m, r, n in W.gravity_points(q, payload_kg)]


def deflection(q, pts=None, K=None, EI=None, GJ=None, n_sec=200, target=None):
    """TCP 在重力下的位移，分成各个柔性来源（底座坐标，m）。原理：每个柔性的地方转一个小角度，TCP 就跟着移动“小角度 × 力臂”：
      关节 j：转角 φ_j = τ_j / K_j，绕关节轴 z_j，τ_j 为构件 j 及以外的重力对关节轴的力矩；
      铝管上长 ds 的一小段：转角 = (Mb/EI + T/GJ)·ds，Mb、T 为截面外侧的重力对截面形心的弯矩、扭矩。
    pts：load_points() 的格式（默认：整机自重 + 5 kg 负载）。返回 {来源: 位移向量}"""
    pts = load_points(q) if pts is None else pts
    K = joint_K() if K is None else np.asarray(K, float)
    p_t = tcp_point(q) if target is None else np.asarray(target, float)
    Tw = W.link_world(q)
    g = np.array([0.0, 0.0, -G0])
    out = {}
    for j in range(6):
        o, z = Tw[j][:3, 3], Tw[j][:3, 2]
        tau = sum(np.cross(r - o, m * g) for i, m, r, _ in pts if i >= j) @ z
        out[W.JOINTS[j]] = tau / K[j] * np.cross(z, p_t - o)
    for i, key, r, t in tubes():
        pr = tube_props(r, t)
        ei = pr["EI"] if EI is None else EI[key]
        gj = pr["GJ"] if GJ is None else GJ[key]
        p0 = Tw[i][:3, 3]
        p1 = (Tw[i] @ np.append(W._child_pos(i), 1.0))[:3]
        L = float(np.linalg.norm(p1 - p0))
        u = (p1 - p0) / L
        bend, tors = np.zeros(3), np.zeros(3)
        for k in range(n_sec):
            c = p0 + (k + 0.5) / n_sec * (p1 - p0)
            M = np.zeros(3)
            for li, m, rr, dist in pts:
                if li > i or (li == i and ((rr - c) @ u > 0 if dist else (rr - c) @ u > -1e-9)):
                    M += np.cross(rr - c, m * g)
            T = M @ u
            ds = L / n_sec
            bend += np.cross((M - T * u) / ei * ds, p_t - c)
            tors += np.cross(T * u / gj * ds, p_t - c)
        out[key + "_bend"] = bend
        out[key + "_tors"] = tors
    return out


def jacobian_v(q, p):
    """点 p 的线速度雅可比 J_v（3×6）：第 j 列 = z_j × (p − o_j)"""
    Tw = W.link_world(q)
    return np.array([np.cross(Tw[j][:3, 2], p - Tw[j][:3, 3]) for j in range(6)]).T


def joint_compliance_x(q, K=None, p=None):
    """关节柔度经雅可比变到 TCP：C_x = J_v C_θ J_vᵀ（3×3，m/N），C_θ = diag(1/K_j)"""
    K = joint_K() if K is None else np.asarray(K, float)
    p = tcp_point(q) if p is None else p
    J = jacobian_v(q, p)
    return J @ np.diag(1 / K) @ J.T


def mass_matrix(q, payload_kg=W.PAYLOAD_KG):
    """连杆侧的质量矩阵 M(q)（6×6，不含电机转子：关节刚度在减速器上，转子在弹簧的另一侧，由伺服锁住）"""
    import mujoco
    m = mujoco.MjModel.from_xml_string(W.mjcf(friction=False, payload_kg=payload_kg))
    d = mujoco.MjData(m)
    d.qpos[:6] = q
    mujoco.mj_forward(m, d)
    M = np.zeros((m.nv, m.nv))
    mujoco.mj_fullM(m, d, M)
    return M[:6, :6] - np.diag(W.armature())


def modes(q, K, payload_kg=W.PAYLOAD_KG):
    """关节柔性模型的固有频率：K v = ω² M v，返回 (频率 Hz 从小到大, 振型)"""
    from scipy.linalg import eigh
    w2, V = eigh(np.diag(K), mass_matrix(q, payload_kg))
    return np.sqrt(np.maximum(w2, 0)) / (2 * math.pi), V


def robot_plant_prices():
    """机器人厂清单（factory/plants/wenquest-robot.yaml）里各物料的示例价"""
    import yaml
    P = yaml.safe_load((ROOT / "factory" / "plants" / "wenquest-robot.yaml").read_text(encoding="utf-8"))
    return {it["code"]: it.get("price") for it in P["items"]}
