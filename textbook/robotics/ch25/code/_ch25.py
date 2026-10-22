"""第 24 章共用：拉格朗日动力学。以下划线开头，构建时不单独运行。

前半部分是第 6、12、23 章的共用代码（叉积矩阵、罗德里格斯公式、矩阵指数、伴随矩阵、UR5e 的旋量轴（表 12.1.1）、
常见形体的惯量、平行轴定理、空间惯量、书中网页版 UR5e 模型的读法、数字工厂的毛坯与夹爪），原样抄来，使本章程序自成一体；
后半部分是本章新加的：
- 平面两连杆臂的 M(θ)、c(θ, θ̇)、g(θ)（24.2 节的结果，24.2 节的公式），能量，正、逆动力学；
- 把 UR5e 的关节 2、3 看作平面两连杆臂：关节 1、4、5、6 锁住时，从模型文件算出两根“等效连杆”的参数（24.2.6 节）；
  锁住的关节在 MJCF 中删去 <joint>，连杆就焊在父连杆上，得到与之完全对应的两自由度 MuJoCo 模型；
- 一般 n 关节机械臂：M(θ) = Σ J_iᵀ 𝒢_i J_i，由 M 的偏导数得到克里斯托费尔符号和 C(θ, θ̇)；
- 五次多项式点到点轨迹（式 (22.1.8)）；龙格-库塔积分（第 7 章）。
"""
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BOOK = HERE.parents[1]
MJCF_DIR = BOOK / "models" / "mjcf"
G0 = 9.81                                  # 𝔤，m/s²（符号约定第九节）

# ---------------------------------------------------------------- 第 3、6 章：叉积矩阵、转动、伴随


def skew(w):
    """[w]：w × x = [w] x（式 (3.2.10)）。"""
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]], dtype=float)


def rot(w, t):
    """罗德里格斯公式 (4.4.5)：绕单位矢量 w 转 t。"""
    K = skew(np.asarray(w, float))
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def rotx(t):
    return rot((1, 0, 0), t)


def roty(t):
    return rot((0, 1, 0), t)


def rotz(t):
    return rot((0, 0, 1), t)


def screw_revolute(w, q):
    """转动关节的旋量轴 S = (ω, −ω × q)，式 (12.1.3)。"""
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
    Gm = np.eye(3) * t + (1 - math.cos(t)) * K + (t - math.sin(t)) * K @ K
    T[:3, 3] = Gm @ v
    return T


def tf(R=None, p=None):
    T = np.eye(4)
    if R is not None:
        T[:3, :3] = R
    if p is not None:
        T[:3, 3] = p
    return T


def inv(T):
    R, p = T[:3, :3], T[:3, 3]
    return tf(R.T, -R.T @ p)


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


def bracket(V):
    """六维矢量 V = (ω, v) → 4×4 矩阵 [V]（式 (6.3.6)）。"""
    m = np.zeros((4, 4))
    m[:3, :3] = skew(V[:3])
    m[:3, 3] = V[3:]
    return m


def exp_twist(V):
    """e^{[V]}，V 为任意六维矢量（定理 6.4.1）。"""
    V = np.asarray(V, float)
    th = float(np.linalg.norm(V[:3]))
    if th < 1e-12:
        return tf(None, V[3:])
    return exp6(V / th, th)


def quat2R(q):
    """单位四元数 (q₀, q₁, q₂, q₃)（实部在前，4.6 节；MuJoCo 的 quat 也是这个次序）→ 旋转矩阵。"""
    q = np.asarray(q, float)
    q = q / np.linalg.norm(q)
    w, x, y, z = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - w * z), 2 * (x * z + w * y)],
                     [2 * (x * y + w * z), 1 - 2 * (x * x + z * z), 2 * (y * z - w * x)],
                     [2 * (x * z - w * y), 2 * (y * z + w * x), 1 - 2 * (x * x + y * y)]])


# ---------------------------------------------------------------- UR5e：表 12.1.1（指数积，基座坐标系 {s}）

H1, W1, L1, W2, L2, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1
YD = np.array([0, -1.0, 0])
UR_W = [np.array([0, 0, 1.0]), YD, YD, YD, np.array([0, 0, -1.0]), YD]
UR_Q = [np.array([0, 0, H1]), np.array([0, -W1, H1]), np.array([-L1, -W1 + W2, H1]), np.array([-L1 - L2, -W1 + W2, H1]),
        np.array([-L1 - L2, -W1 + W2 - W3, H1]), np.array([-L1 - L2, -W1 + W2 - W3, H1 - H2])]
UR_S = [screw_revolute(w, q) for w, q in zip(UR_W, UR_Q)]
UR_M = np.array([[1.0, 0, 0, -L1 - L2], [0, -1, 0, -W1 + W2 - W3 - W4], [0, 0, -1, H1 - H2], [0, 0, 0, 1]])


def ur_fk(theta):
    """法兰坐标系 {b} 的位姿 T_sb(θ) = e^{[S1]θ1}…e^{[S6]θ6} M（式 (12.2.3)）。"""
    T = np.eye(4)
    for S, t in zip(UR_S, theta):
        T = T @ exp6(S, t)
    return T @ UR_M


def ur_points(theta):
    """UR5e 的连杆折线（作图用）：基座、关节中心与连杆转折点、法兰中心。"""
    Es = [np.eye(4)]
    for S, t in zip(UR_S, theta):
        Es.append(Es[-1] @ exp6(S, t))
    q = UR_Q
    pts = [(0, np.zeros(3)), (0, q[0]), (1, q[1]), (2, q[1] + np.array([-L1, 0, 0])), (2, q[2]), (3, q[3]),
           (4, q[4]), (5, q[5]), (6, q[5] + np.array([0, -W4, 0]))]
    return np.array([(Es[k] @ np.r_[p, 1])[:3] for k, p in pts])


# ---------------------------------------------------------------- 第 23 章：质量、惯量、空间惯量

def box_inertia(m, a, b, c):
    """长 a、宽 b、高 c 的均匀长方体，对质心、沿三条棱的惯量（式 (23.1.11)）。"""
    return m / 12 * np.diag([b * b + c * c, a * a + c * c, a * a + b * b])


def cyl_inertia(m, r, L):
    """半径 r、长 L 的均匀实心圆柱，对质心；轴线沿 z（式 (23.1.12)）。"""
    t = m * (3 * r * r + L * L) / 12
    return np.diag([t, t, m * r * r / 2])


def sphere_inertia(m, r):
    return np.eye(3) * 2 / 5 * m * r * r


def steiner(Ic, m, p):
    """平行轴定理的张量形式 (23.2.3)：质心在 p 处时，对原点的惯量 I_c + m(|p|² I − p pᵀ) = I_c − m [p]²。"""
    p = np.asarray(p, float)
    return Ic + m * ((p @ p) * np.eye(3) - np.outer(p, p))


def G_com(Ic, m):
    """质心坐标系中的空间惯量 G_c = diag(I_c, m I₃)（式 (23.3.10)）。"""
    G = np.zeros((6, 6))
    G[:3, :3] = Ic
    G[3:, 3:] = m * np.eye(3)
    return G


def G_frame(Ic, m, R_bc, p_bc):
    """物体上任一坐标系 {b} 中的空间惯量：质心坐标系 {c} 相对 {b} 的姿态 R_bc、位置 p_bc（式 (23.3.15)，先用 R_bc 转方向）。"""
    Ib = R_bc @ Ic @ R_bc.T
    P = skew(p_bc)
    G = np.zeros((6, 6))
    G[:3, :3] = Ib - m * P @ P
    G[:3, 3:] = m * P
    G[3:, :3] = -m * P
    G[3:, 3:] = m * np.eye(3)
    return G


def ne_wrench(G, V, Vdot):
    """旋量形式的牛顿-欧拉方程 (23.3.11)、(23.3.14)：F = G V̇ − [ad_V]ᵀ G V。"""
    return G @ Vdot - ad(V).T @ G @ V


def principal(I):
    """主惯量（从小到大）与主轴（列），并把主轴矩阵调成右手系。"""
    lam, Q = np.linalg.eigh(I)
    if np.linalg.det(Q) < 0:
        Q[:, 2] = -Q[:, 2]
    return lam, Q


# ---------------------------------------------------------------- 书中的网页版 UR5e 模型（MJCF）

PLACEHOLDERS = re.compile(r"<!--(OPTION|WORLD|TOOL|ACTUATOR)-->")


def mjcf_text(name="ur5e", tool="", world="", option="", actuator=""):
    """模型文本，四个占位注释换成给定的片段（不给就换成空），与实验框架 api.mjcf 相同。"""
    t = (MJCF_DIR / f"{name}.xml").read_text(encoding="utf-8")
    if "integrator=" in option:                          # 模型自带 <option integrator="implicitfast"/>，写在占位注释之后，会覆盖前面的设置
        t, k = re.subn(r'\s*<option integrator="[a-zA-Z0-9]+" />', "", t)
        assert k == 1
    parts = {"OPTION": option, "WORLD": world, "TOOL": tool, "ACTUATOR": actuator}
    return PLACEHOLDERS.sub(lambda m: parts[m.group(1)], t)


def mjcf_header(name="ur5e"):
    """文件头注释里写的来源提交（textbook/tools/mjcf_web.py 生成时写入）。"""
    t = (MJCF_DIR / f"{name}.xml").read_text(encoding="utf-8")
    return re.search(r"提交 ([0-9a-f]{40})", t).group(1)


def _floats(s, n=None):
    v = [float(x) for x in s.split()]
    if n is not None and len(v) != n:
        raise ValueError(s)
    return np.array(v)


class Link:
    def __init__(self, name, parent, pos, quat, joint_axis, joint_name, mass, ipos, iquat, diag):
        self.name, self.parent = name, parent
        self.pos, self.quat = pos, quat                         # 连杆坐标系相对父连杆（零位）
        self.axis, self.joint = joint_axis, joint_name          # 关节轴（在本连杆坐标系中），没有关节时为 None
        self.m, self.ipos, self.iquat, self.diag = mass, ipos, iquat, diag   # <inertial>
        self.R_ic = quat2R(iquat)                               # 惯量坐标系 {c} 相对连杆坐标系 {i} 的姿态

    @property
    def I_link_c(self):
        """对质心、在连杆坐标系 {i} 的方向中的惯量：R diag Rᵀ（式 (3.4.4)）。"""
        return self.R_ic @ np.diag(self.diag) @ self.R_ic.T

    @property
    def I_link_o(self):
        """对连杆坐标系原点的惯量（平行轴定理）。"""
        return steiner(self.I_link_c, self.m, self.ipos)

    @property
    def G(self):
        """连杆坐标系中的空间惯量 G_i（式 (23.3.15)）。"""
        return G_frame(np.diag(self.diag), self.m, self.R_ic, self.ipos)


def parse_links(xml_text):
    """读出 MJCF 中每个 body 的 pos、quat、关节轴与 <inertial>（只用标准库，不经过 MuJoCo）。"""
    root = ET.fromstring(xml_text)
    defaults = {}

    def read_defaults(node, inherited):
        for d in node.findall("default"):
            cls = d.get("class")
            j = dict(inherited)
            je = d.find("joint")
            if je is not None:
                j.update(je.attrib)
            defaults[cls] = j
            read_defaults(d, j)
    read_defaults(root.find("default"), {})
    links = []

    def walk(body, parent, cls):
        cls = body.get("childclass", cls)
        pos = _floats(body.get("pos", "0 0 0"), 3)
        quat = _floats(body.get("quat", "1 0 0 0"), 4)
        je = body.find("joint")
        axis = jname = None
        if je is not None:
            attrs = dict(defaults.get(cls, {}))
            attrs.update(defaults.get(je.get("class"), {}) if je.get("class") else {})
            attrs.update(je.attrib)
            axis = _floats(attrs.get("axis", "0 0 1"), 3)
            jname = attrs.get("name")
        ie = body.find("inertial")
        if ie is None:                                  # 只起组织作用、没有质量的 body（如 FR3 的 base）
            links.append(Link(body.get("name"), parent, pos, quat, axis, jname, 0.0, np.zeros(3), np.array([1.0, 0, 0, 0]), np.zeros(3)))
        else:
            links.append(Link(body.get("name"), parent, pos, quat, axis, jname, float(ie.get("mass")),
                              _floats(ie.get("pos", "0 0 0"), 3), _floats(ie.get("quat", "1 0 0 0"), 4),
                              _floats(ie.get("diaginertia"), 3)))
        for ch in body.findall("body"):
            walk(ch, body.get("name"), cls)
    for b in root.find("worldbody").findall("body"):
        walk(b, None, None)
    return links


def link_poses(links, theta):
    """各连杆坐标系在 {s}（MJCF 的世界坐标系）中的位姿：沿运动链乘 (pos, quat) 和关节转动。"""
    T = {}
    k = 0
    for L in links:
        Tp = T[L.parent] if L.parent else np.eye(4)
        Ti = Tp @ tf(quat2R(L.quat), L.pos)
        if L.axis is not None:
            Ti = Ti @ tf(rot(L.axis / np.linalg.norm(L.axis), theta[k]))
            k += 1
        T[L.name] = Ti
    return T


def mj_load(xml_text):
    import mujoco
    m = mujoco.MjModel.from_xml_string(xml_text)
    return mujoco, m, mujoco.MjData(m)


# ---------------------------------------------------------------- 数字工厂的工件与本章示意值

def factory_data():
    """factory/factory/data.py：数字工厂的物料清单（与工厂仿真同一份数据）。"""
    p = ROOT / "factory"
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
    from factory import data            # noqa: E402
    return data


RHO_STEEL = 7850.0                       # 钢的密度，kg/m³（与 1.5 节相同）
D_BAR = 0.050                            # SH-301 用 Ø50 mm 圆钢（RM-45-D50）


def sh301_blank():
    """输出轴 SH-301 的毛坯：Ø50 mm 圆钢锯下的一段，每根耗料（物料清单）即毛坯质量，长度 = m/(ρπr²)。"""
    data = factory_data()
    m = dict(data.BOMS["SH-301"][1])["RM-45-D50"]
    r = D_BAR / 2
    L = m / (RHO_STEEL * math.pi * r * r)
    return m, r, L


GRIP_M = 1.0                             # 夹爪质量 1.0 kg（1.5 节的假设）
GRIP_BOX = (0.08, 0.06, 0.10)            # 夹爪外形（示意值）：沿 x、z、工具方向 y 的尺寸，m
GRIP_C = 0.05                            # 夹爪质心距法兰盘 0.05 m（示意值），沿工具方向 y_b
TCP = 0.15                               # TCP 距法兰盘 0.15 m（与第 5、22 章相同）
GRIP_TOP = 0.04                          # 夹持点（TCP）到毛坯上端的距离（与第 22 章相同）


# ---------------------------------------------------------------- 第 22 章：五次多项式点到点（式 (22.1.8)）

def quintic(qa, qb, T, t):
    """θ(t) = θ_A + s(t/T)(θ_B − θ_A)，s(τ) = 10τ³ − 15τ⁴ + 6τ⁵：两端速度、加速度为零。返回 (θ, θ̇, θ̈)。"""
    qa, qb = np.asarray(qa, float), np.asarray(qb, float)
    tau = min(max(t / T, 0.0), 1.0)
    s = 10 * tau ** 3 - 15 * tau ** 4 + 6 * tau ** 5
    sd = (30 * tau ** 2 - 60 * tau ** 3 + 30 * tau ** 4) / T
    sdd = (60 * tau - 180 * tau ** 2 + 120 * tau ** 3) / T ** 2
    d = qb - qa
    return qa + s * d, sd * d, sdd * d


# ---------------------------------------------------------------- 第 7 章：龙格-库塔法（式 (7.2.6)）

def rk4_step(f, x, h):
    k1 = f(x)
    k2 = f(x + 0.5 * h * k1)
    k3 = f(x + 0.5 * h * k2)
    k4 = f(x + h * k3)
    return x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


# ---------------------------------------------------------------- 一般 n 关节：M(θ) = Σ J_iᵀ 𝒢_i J_i 与克里斯托费尔符号

def body_jacobians(links, theta):
    """各连杆坐标系的物体雅可比 J_i（6×n，只有关节 1…i 的列；连杆 i 的坐标系原点在关节 i 上）与位姿。"""
    T = link_poses(links, theta)
    n = len(theta)
    axes = [(k, L) for k, L in enumerate(links) if L.axis is not None]
    Js = []
    for i, L in enumerate(links):
        Ti = T[L.name]
        J = np.zeros((6, n))
        for col, (k, Lj) in enumerate(axes):
            if k > i:
                break
            Sj = adjoint(T[Lj.name]) @ np.r_[Lj.axis / np.linalg.norm(Lj.axis), 0, 0, 0]
            J[:, col] = adjoint(inv(Ti)) @ Sj
        Js.append(J)
    return T, Js


def mass_matrix(links, theta, extra=None):
    """M(θ) = Σ J_iᵀ 𝒢_i J_i（不含电机转子惯量）。extra = (父连杆名, 𝒢)：固定在某个连杆上的负载，空间惯量写在该连杆坐标系中。"""
    T, Js = body_jacobians(links, theta)
    n = len(theta)
    M = np.zeros((n, n))
    for L, J in zip(links, Js):
        if L.m > 0:
            M += J.T @ L.G @ J
        if extra is not None and L.name == extra[0]:
            M += J.T @ extra[1] @ J
    return M


def potential(links, theta, extra=None, g=G0):
    """U(θ) = Σ m_i 𝔤 z_ci（基座坐标系 z 轴竖直向上）。extra = (父连杆名, m, 质心在该连杆坐标系中的位置)。"""
    T = link_poses(links, theta)
    U = 0.0
    for L in links:
        Ti = T[L.name]
        U += L.m * g * (Ti[:3, :3] @ L.ipos + Ti[:3, 3])[2]
        if extra is not None and L.name == extra[0]:
            U += extra[1] * g * (Ti[:3, :3] @ extra[2] + Ti[:3, 3])[2]
    return U


def dM(Mfun, theta, h=1e-6):
    """∂M/∂θ_k（中心差分），返回 n×n×n 数组 D[k] = ∂M/∂θ_k。"""
    n = len(theta)
    D = np.zeros((n, n, n))
    for k in range(n):
        e = np.zeros(n)
        e[k] = h
        D[k] = (Mfun(theta + e) - Mfun(theta - e)) / (2 * h)
    return D


def christoffel(D):
    """Γ[i, j, k] = ½(∂M_ij/∂θ_k + ∂M_ik/∂θ_j − ∂M_jk/∂θ_i)（式 (24.3.4)），D[k] = ∂M/∂θ_k。"""
    n = D.shape[0]
    G = np.zeros((n, n, n))
    for i in range(n):
        for j in range(n):
            for k in range(n):
                G[i, j, k] = 0.5 * (D[k][i, j] + D[j][i, k] - D[i][j, k])
    return G


def coriolis_matrix(D, thd):
    """C_ij = Σ_k Γ_ijk θ̇_k（式 (24.3.5)）。"""
    return christoffel(D) @ thd


def gravity(Ufun, theta, h=1e-6):
    n = len(theta)
    g = np.zeros(n)
    for k in range(n):
        e = np.zeros(n)
        e[k] = h
        g[k] = (Ufun(theta + e) - Ufun(theta - e)) / (2 * h)
    return g


# ---------------------------------------------------------------- 负载（算例 23.2.2）

NOCONTACT = '<option><flag contact="disable"/></option>'


def payload_parts():
    """夹爪 + SH-301 毛坯（算例 23.2.2）：质量、对法兰坐标系（MJCF 的 wrist_3_link 坐标系，工具方向为 +y，法兰盘在 y = 0.1 m）的质心与对质心的惯量。"""
    m_b, r_b, L_b = sh301_blank()
    gx, gz, gy = GRIP_BOX
    cb = cyl_inertia(m_b, r_b, L_b)
    I_bl = np.diag([cb[0, 0], cb[2, 2], cb[0, 0]])                       # 毛坯轴线沿工具方向 y
    c_g = np.array([0, GRIP_C, 0])
    c_bl = np.array([0, TCP - GRIP_TOP + L_b / 2, 0])
    m_p = GRIP_M + m_b
    c_p = (GRIP_M * c_g + m_b * c_bl) / m_p
    I_pc = steiner(box_inertia(GRIP_M, gx, gy, gz), GRIP_M, c_g - c_p) + steiner(I_bl, m_b, c_bl - c_p)
    return m_p, c_p, I_pc


FLANGE_Y = 0.1                            # wrist_3_link 坐标系中法兰盘的位置（MJCF 的 attachment_site）


def payload_xml(m_p, c_p, I_pc):
    """把负载写成 <!--TOOL--> 处的一个 body（质心与主惯量；惯量主轴与法兰坐标系平行，算例 23.2.2）。"""
    assert abs(I_pc[0, 1]) + abs(I_pc[0, 2]) + abs(I_pc[1, 2]) < 1e-14
    return (f'<body name="payload" pos="0 {FLANGE_Y} 0"><inertial pos="0 {float(c_p[1])!r} 0" mass="{float(m_p)!r}" '
            f'diaginertia="{float(I_pc[0, 0])!r} {float(I_pc[1, 1])!r} {float(I_pc[2, 2])!r}"/></body>')


# ================================================================ 第 25 章：旋量形式的牛顿-欧拉递推

FLANGE = tf(None, np.array([0, FLANGE_Y, 0]))   # 法兰坐标系 {f} 在连杆 6 坐标系中的位姿：方向相同，原点在法兰盘中心
GRAV = np.array([0, 0, 0, 0, 0, G0])            # 𝒱̇₀ = (0, −𝔤)：基座以 𝔤 向上加速，代替各连杆的重力（25.1.5 节）


class Chain:
    """串联机械臂的递推数据（25.1.2 节）。连杆坐标系 {i} 取 MJCF 中各 body 的坐标系：原点在关节 i 的轴上，关节轴在 {i} 中是常矢量 ω_i；
    {0} 取世界坐标系（基座固定），最后一个连杆之外是法兰坐标系 {n+1} = {f}。
      A[i]    关节 i 的旋量轴在 {i} 中的坐标 A_i = (ω_i, 0)
      Mi[i]   θ_i = 0 时 {i−1} 在 {i} 中的位姿 M_{i,i−1}
      G[i]    连杆 i 在 {i} 中的空间惯量 𝒢_i（式 (23.3.15)）；负载并入最后一个连杆
      arm[i]  电机转子的等效惯量（MJCF 的 armature，24.3.6 节），只加在关节力矩上
    payload = (m, c, I_c)：负载的质量、质心在 {f} 中的位置、对质心的惯量（方向同 {f}）。"""

    def __init__(self, links, payload=None, arm=0.1, Mf=FLANGE):
        T0 = link_poses(links, np.zeros(sum(L.axis is not None for L in links)))
        mov = [L for L in links if L.axis is not None]
        self.names = [L.name for L in mov]
        self.n = len(mov)
        prev = np.eye(4)
        self.A, self.Mi, self.G = [], [], []
        for L in mov:
            w = L.axis / np.linalg.norm(L.axis)
            self.A.append(np.r_[w, 0, 0, 0])
            self.Mi.append(inv(T0[L.name]) @ prev)
            self.G.append(L.G.copy())
            prev = T0[L.name]
        # 固定在运动连杆上、没有关节的 body（如 MJCF 的 base 固定在世界上）：只有最前面的 base，不带质量进入递推
        self.Mf = Mf                                     # {f} 在 {n} 中的位姿
        self.payload = payload
        if payload is not None:
            m_p, c_p, I_pc = payload
            self.G[-1] = self.G[-1] + G_frame(I_pc, m_p, np.eye(3), Mf[:3, 3] + Mf[:3, :3] @ c_p)
        self.arm = np.full(self.n, arm) if np.isscalar(arm) else np.asarray(arm, float)

    def T_rel(self, i, th):
        """T_{i,i−1}(θ_i) = e^{−[A_i]θ_i} M_{i,i−1}（式 (25.1.2)）。关节轴过 {i} 的原点，e^{−[A_i]θ} 只是转动。"""
        return tf(rot(self.A[i][:3], -th)) @ self.Mi[i]

    def forward(self, th, thd, thdd, Vd0=GRAV):
        """前向递推（式 (25.1.3)、(25.1.4)）：各连杆在自己坐标系中的运动旋量和加速度。返回 (T, V, Vd)，T[i] = T_{i,i−1}。"""
        V, Vd = np.zeros(6), np.asarray(Vd0, float)
        Ts, Vs, Vds = [], [], []
        for i in range(self.n):
            T = self.T_rel(i, th[i])
            Ad = adjoint(T)
            V = Ad @ V + self.A[i] * thd[i]
            Vd = Ad @ Vd + ad(V) @ self.A[i] * thd[i] + self.A[i] * thdd[i]
            Ts.append(T)
            Vs.append(V)
            Vds.append(Vd)
        return Ts, Vs, Vds

    def rnea(self, th, thd, thdd, Vd0=GRAV, Ftip=None, full=False):
        """牛顿-欧拉递推（算法 25.2.1）。Ftip：连杆 n 经法兰对外界施加的力旋量，写在 {f} 中。
        返回关节力矩 τ（含转子惯量 arm·θ̈）；full=True 时再返回各关节传给连杆 i 的力旋量 ℱ_i（写在 {i} 中）与 (T, V, V̇)。"""
        Ts, Vs, Vds = self.forward(th, thd, thdd, Vd0)
        F = np.zeros(6) if Ftip is None else np.asarray(Ftip, float)
        Tn = inv(self.Mf)                                # T_{n+1,n}：{n} 在 {f} 中的位姿
        tau = np.zeros(self.n)
        Fs = [None] * self.n
        for i in reversed(range(self.n)):
            Tnext = Tn if i == self.n - 1 else Ts[i + 1]
            F = adjoint(Tnext).T @ F + self.G[i] @ Vds[i] - ad(Vs[i]).T @ self.G[i] @ Vs[i]
            Fs[i] = F
            tau[i] = F @ self.A[i] + self.arm[i] * thdd[i]
        if full:
            return tau, Fs, (Ts, Vs, Vds)
        return tau

    # -------------------------------------------- 25.3 节：闭式（把各连杆的量排成长矢量）
    def stacked(self, th, thd):
        """𝒜、𝒢、𝒲、ℒ = (I − 𝒲)⁻¹（式 (25.3.2)、(25.3.4)）。"""
        n = self.n
        A = np.zeros((6 * n, n))
        G = np.zeros((6 * n, 6 * n))
        W = np.zeros((6 * n, 6 * n))
        for i in range(n):
            A[6 * i:6 * i + 6, i] = self.A[i]
            G[6 * i:6 * i + 6, 6 * i:6 * i + 6] = self.G[i]
            if i > 0:
                W[6 * i:6 * i + 6, 6 * i - 6:6 * i] = adjoint(self.T_rel(i, th[i]))
        L = np.linalg.inv(np.eye(6 * n) - W)
        return A, G, W, L

    def closed_form(self, th, thd, Vd0=GRAV):
        """M(θ)、c(θ, θ̇)、g(θ)（式 (25.3.5)～(25.3.7)），M 含转子惯量。"""
        n = self.n
        A, G, W, L = self.stacked(th, thd)
        V = L @ A @ thd
        D = np.zeros((6 * n, 6 * n))                     # diag([ad_{A_i θ̇_i}])
        adV = np.zeros((6 * n, 6 * n))                   # diag([ad_{𝒱_i}])
        for i in range(n):
            D[6 * i:6 * i + 6, 6 * i:6 * i + 6] = ad(self.A[i] * thd[i])
            adV[6 * i:6 * i + 6, 6 * i:6 * i + 6] = ad(V[6 * i:6 * i + 6])
        Vb = np.zeros(6 * n)
        Vb[:6] = adjoint(self.T_rel(0, th[0])) @ Vd0
        M = A.T @ L.T @ G @ L @ A + np.diag(self.arm)
        c = A.T @ L.T @ (G @ L @ (-D @ W @ V) - adV.T @ G @ V)
        g = A.T @ L.T @ G @ L @ Vb
        return M, c, g

    def jacobians(self, th):
        """连杆 i 的物体雅可比 J_i（6×n）就是 ℒ𝒜 的第 i 个块行（定理 25.3.1）。"""
        A, G, W, L = self.stacked(th, np.zeros(self.n))
        LA = L @ A
        return [LA[6 * i:6 * i + 6] for i in range(self.n)]

    def flange_pose(self, th):
        T = np.eye(4)                                    # T_{0,i} = T_{0,i−1} T_{i−1,i}
        for i in range(self.n):
            T = T @ inv(self.T_rel(i, th[i]))
        return T @ self.Mf


def ur_chain(payload=None, arm=0.1):
    """书中的 UR5e 模型：连杆参数取自 MJCF（与第 23、24 章相同）。"""
    return Chain(parse_links(mjcf_text()), payload=payload, arm=arm)


def ur_mj(payload=None, option=NOCONTACT):
    """对应的 MuJoCo 模型（关闭接触；负载写成法兰上的 body）。"""
    tool = payload_xml(*payload) if payload is not None else ""
    return mj_load(mjcf_text(tool=tool, option=option))


# ---------------------------------------------------------------- 25.4 节：数一数乘法和加法

class Ops:
    """记录乘法、加法（减法算作加法）次数的数。数据（关节角的正余弦、连杆参数、θ̇、θ̈）都用它包起来，
    程序走一遍，就数出了这个算法一共做了多少次运算。三角函数不计入（两种算法都只对每个关节求一次 sin、cos）。"""
    mul = 0
    add = 0
    __slots__ = ("v",)

    def __init__(self, v):
        self.v = v

    @staticmethod
    def reset():
        Ops.mul = Ops.add = 0

    def _v(b):
        return b.v if isinstance(b, Ops) else b

    def __add__(a, b):
        Ops.add += 1
        return Ops(a.v + Ops._v(b))

    __radd__ = __add__

    def __sub__(a, b):
        Ops.add += 1
        return Ops(a.v - Ops._v(b))

    def __rsub__(a, b):
        Ops.add += 1
        return Ops(Ops._v(b) - a.v)

    def __mul__(a, b):
        Ops.mul += 1
        return Ops(a.v * Ops._v(b))

    __rmul__ = __mul__

    def __neg__(a):
        return Ops(-a.v)


def _vadd(a, b):
    return [x + y for x, y in zip(a, b)]


def _vsub(a, b):
    return [x - y for x, y in zip(a, b)]


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _mv(R, v):
    return [R[i][0] * v[0] + R[i][1] * v[1] + R[i][2] * v[2] for i in range(3)]


def _mtv(R, v):
    return [R[0][i] * v[0] + R[1][i] * v[1] + R[2][i] * v[2] for i in range(3)]


def _mm(A, B):
    return [[A[i][0] * B[0][j] + A[i][1] * B[1][j] + A[i][2] * B[2][j] for j in range(3)] for i in range(3)]


def _scale(v, s):
    return [x * s for x in v]


def _rodrigues(w, c, s):
    """R = I + s[ω] + (1 − c)[ω]²，ω 是单位矢量：R_ij = c δ_ij + (1 − c) ω_i ω_j − s ε_ijk ω_k。"""
    k = 1 - c
    return [[c + k * w[0] * w[0], k * w[0] * w[1] - s * w[2], k * w[0] * w[2] + s * w[1]],
            [k * w[1] * w[0] + s * w[2], c + k * w[1] * w[1], k * w[1] * w[2] - s * w[0]],
            [k * w[2] * w[0] - s * w[1], k * w[2] * w[1] + s * w[0], c + k * w[2] * w[2]]]


class ScalarChain:
    """供数运算次数的通用串联臂：每个关节一个转动轴 ω_i（{i} 中的单位矢量，不假定是坐标轴），
    M_{i,i−1} = (R_i, p_i)，连杆质量 m_i、质心 c_i、对 {i} 原点的惯量 I_i（对称）。数据可以是 float，也可以是 Ops。"""

    def __init__(self, axes, Ms, ms, cs, Is, wrap=float):
        self.w = [[wrap(x) for x in a] for a in axes]
        self.R = [[[wrap(x) for x in row] for row in M[:3, :3]] for M in Ms]
        self.p = [[wrap(x) for x in M[:3, 3]] for M in Ms]
        self.m = [wrap(x) for x in ms]
        self.c = [[wrap(x) for x in c] for c in cs]
        self.I = [[[wrap(x) for x in row] for row in I] for I in Is]
        self.n = len(ms)

    @staticmethod
    def from_chain(ch, wrap=float):
        ms, cs, Is = [], [], []
        for G in ch.G:
            m = G[3, 3]
            mc = np.array([G[2, 4], G[0, 5], G[1, 3]])      # 𝒢 右上块 m[c]
            ms.append(m)
            cs.append(mc / m)
            Is.append(G[:3, :3])
        return ScalarChain([A[:3] for A in ch.A], ch.Mi, ms, cs, Is, wrap)

    @staticmethod
    def random(n, rng, wrap=float):
        axes, Ms, ms, cs, Is = [], [], [], [], []
        for _ in range(n):
            a = rng.normal(size=3)
            axes.append(a / np.linalg.norm(a))
            q = rng.normal(size=4)
            Ms.append(tf(quat2R(q), rng.uniform(-0.3, 0.3, 3)))
            m = rng.uniform(0.5, 5)
            c = rng.uniform(-0.2, 0.2, 3)
            B = rng.normal(size=(3, 3)) * 0.05
            ms.append(m)
            cs.append(c)
            Is.append(steiner(B @ B.T + 0.01 * np.eye(3), m, c))
        return ScalarChain(axes, Ms, ms, cs, Is, wrap)

    # -------------------------------------------- 牛顿-欧拉递推，三维矢量写法（25.4.2 节）
    def rnea(self, cs, ss, thd, thdd, g):
        """cs、ss：各关节的 cos θ_i、sin θ_i（已算好）。g：重力加速度的大小（{0} 的 z 轴竖直向上）。不含转子惯量。"""
        n = self.n
        z = type(self.m[0])(0.0)                          # 与数据同类型的 0（不计运算）
        w, v = [z, z, z], [z, z, z]
        dw, dv = [z, z, z], [z, z, g]
        Rs, ps, W, Vv, DW, DV = [], [], [], [], [], []
        for i in range(n):
            Rq = _rodrigues(self.w[i], cs[i], -ss[i])                  # Rot(ω_i, −θ_i)
            R = _mm(Rq, self.R[i])                                       # R_{i,i−1} = Rot(ω_i, −θ_i) R_i
            p = _mv(Rq, self.p[i])
            wp = _mv(R, w)                                 # 父连杆的角速度换到 {i}
            vp = _vadd(_mv(R, v), _cross(p, wp))
            ai = _scale(self.w[i], thd[i])
            w = _vadd(wp, ai)
            v = vp
            dwp = _mv(R, dw)
            dvp = _vadd(_mv(R, dv), _cross(p, dwp))
            dw = _vadd(_vadd(dwp, _cross(w, ai)), _scale(self.w[i], thdd[i]))   # [ad_V]Aθ̇ 的角量部分 ω × ω_i θ̇
            dv = _vadd(dvp, _cross(v, ai))                                         # 线量部分 v × ω_i θ̇
            Rs.append(R), ps.append(p), W.append(w), Vv.append(v), DW.append(dw), DV.append(dv)
        tau = [None] * n
        fm, ff = [z, z, z], [z, z, z]
        for i in reversed(range(n)):
            if i < n - 1:                                  # ℱ ← [Ad_{T_{i+1,i}}]ᵀ ℱ_{i+1}：m' = Rᵀ(m − p × f)，f' = Rᵀ f
                R, p = Rs[i + 1], ps[i + 1]
                fm, ff = _mtv(R, _vsub(fm, _cross(p, ff))), _mtv(R, ff)
            m, c, I = self.m[i], self.c[i], self.I[i]
            mc = _scale(c, m)
            w, v, dw, dv = W[i], Vv[i], DW[i], DV[i]
            # 𝒢𝒱 = (Iω + mc × v, m v − mc × ω)；𝒢𝒱̇ 同理；−[ad_𝒱]ᵀ(𝒢𝒱) = (ω × h_ω + v × h_v, ω × h_v)
            hw = _vadd(_mv(I, w), _cross(mc, v))
            hv = _vsub(_scale(v, m), _cross(mc, w))
            gw = _vadd(_mv(I, dw), _cross(mc, dv))
            gv = _vsub(_scale(dv, m), _cross(mc, dw))
            fm = _vadd(fm, _vadd(gw, _vadd(_cross(w, hw), _cross(v, hv))))
            ff = _vadd(ff, _vadd(gv, _cross(w, hv)))
            ax = self.w[i]
            tau[i] = ax[0] * fm[0] + ax[1] * fm[1] + ax[2] * fm[2]
        return tau

    # -------------------------------------------- 拉格朗日-欧拉方程，4×4 矩阵写法（尤克 1965；25.4.1 节）
    def lagrange_euler(self, cs, ss, thd, thdd, g):
        """τ_i = Σ_{j≥i} [ Σ_{k≤j} tr(U_jk J_j U_jiᵀ) θ̈_k + Σ_{k,l≤j} tr(U_jkl J_j U_jiᵀ) θ̇_k θ̇_l − m_j gᵀ U_ji r̄_j ]（式 (25.4.1)）。
        U_jk = ∂T_{0j}/∂θ_k = T_{0k}[A_k]T_{kj}，U_jkl = ∂²T_{0j}/∂θ_k∂θ_l。4×4 矩阵的最后一行总是 (0, 0, 0, 0) 或 (0, 0, 0, 1)，
        按 3×4 计算（这是通常的做法）。J_j 是伪惯量矩阵。"""
        n = self.n
        z = type(self.m[0])(0.0)
        one = type(self.m[0])(1.0)

        def mm34(A, B, B_is_T=True):
            # A、B 都是 3×4（隐含最后一行）；B_is_T：B 的最后一行是 (0,0,0,1)，否则是 0
            C = [[A[i][0] * B[0][j] + A[i][1] * B[1][j] + A[i][2] * B[2][j] for j in range(4)] for i in range(3)]
            if B_is_T:
                for i in range(3):
                    C[i][3] = C[i][3] + A[i][3]
            return C

        def T_of(R, p):
            return [[R[i][0], R[i][1], R[i][2], p[i]] for i in range(3)]

        # T_{i−1,i} = (R_{i,i−1})⁻¹ 与 [A_i]（只有转动部分 [ω_i]）
        Tloc, Q = [], []
        for i in range(n):
            Rq = _rodrigues(self.w[i], cs[i], -ss[i])
            R = _mm(Rq, self.R[i])
            p = _mv(Rq, self.p[i])
            Rt = [[R[j][k] for j in range(3)] for k in range(3)]
            pt = [-(x) for x in _mv(Rt, p)]
            Tloc.append(T_of(Rt, pt))
            w = self.w[i]
            Q.append([[z, -w[2], w[1], z], [w[2], z, -w[0], z], [-w[1], w[0], z, z]])
        # T_{k,j}，k < j（k = −1 表示 {0}）
        Tkj = {}
        for k in range(-1, n):
            T = None
            for j in range(k + 1, n):
                T = Tloc[j] if T is None else mm34(T, Tloc[j])
                Tkj[(k, j)] = T
        I3 = [[one, z, z, z], [z, one, z, z], [z, z, one, z]]

        def Tk(k, j):
            return I3 if k == j else Tkj[(k, j)]

        def U(j, k):                                    # ∂T_{0j}/∂θ_k，k ≤ j
            return mm34(mm34(Tk(-1, k), Q[k], False), Tk(k, j))

        def U2(j, k, l):                                # ∂²T_{0j}/∂θ_k∂θ_l，k ≤ l ≤ j
            if k > l:
                k, l = l, k
            return mm34(mm34(mm34(mm34(Tk(-1, k), Q[k], False), Tk(k, l)), Q[l], False), Tk(l, j))

        # 伪惯量矩阵 J = [[Σ m r rᵀ, m c], [m cᵀ, m]]，Σ m r rᵀ = ½tr(I)·I₃ − I
        Js = []
        for j in range(n):
            I, m, c = self.I[j], self.m[j], self.c[j]
            h = (I[0][0] + I[1][1] + I[2][2]) * 0.5
            S = [[(h if a == b else z) - I[a][b] for b in range(3)] for a in range(3)]
            mc = _scale(c, m)
            Js.append([[S[0][0], S[0][1], S[0][2], mc[0]], [S[1][0], S[1][1], S[1][2], mc[1]],
                       [S[2][0], S[2][1], S[2][2], mc[2]], [mc[0], mc[1], mc[2], m]])

        def tr_UJU(Ua, J, Ub):                           # tr(U_a J U_bᵀ)，U 的最后一行为 0
            s = None
            for r in range(3):
                for a in range(4):
                    t = Ua[r][0] * J[0][a] + Ua[r][1] * J[1][a] + Ua[r][2] * J[2][a] + Ua[r][3] * J[3][a]
                    s = t * Ub[r][a] if s is None else s + t * Ub[r][a]
            return s

        Us = {(j, k): U(j, k) for j in range(n) for k in range(j + 1)}
        U2s = {(j, k, l): U2(j, k, l) for j in range(n) for k in range(j + 1) for l in range(k, j + 1)}
        tau = []
        for i in range(n):
            s = z
            for j in range(i, n):
                for k in range(j + 1):
                    s = s + tr_UJU(Us[(j, k)], Js[j], Us[(j, i)]) * thdd[k]
                for k in range(j + 1):
                    for l in range(k, j + 1):
                        coef = tr_UJU(U2s[(j, k, l)], Js[j], Us[(j, i)])
                        s = s + (coef * thd[k] * thd[l] if k == l else coef * (2 * thd[k]) * thd[l])
                # −m_j gᵀ U_ji r̄_j，g = (0, 0, −𝔤, 0)：只用到第 3 行
                u = Us[(j, i)][2]
                c = self.c[j]
                s = s + self.m[j] * g * (u[0] * c[0] + u[1] * c[1] + u[2] * c[2] + u[3])
            tau.append(s)
        return tau


def count_ops(fn):
    Ops.reset()
    fn()
    return Ops.mul, Ops.add


# ---------------------------------------------------------------- 第 22 章的上下料动作（算例 22.1.1）

def cell_move():
    """UR5e 上下料工位：从料架上方 A 到卡盘前 B 的关节空间五次多项式（22.1 节），取第 22 章程序算出的关节角与最短时间
    （速度、加速度、加加速度上限，定理 22.1.3）。返回 (θ_A, θ_B, T)。"""
    p = str(BOOK / "ch22" / "code")
    if p not in sys.path:
        sys.path.insert(0, p)
    from _traj import AMAX, JMAX, VMAX, cell_joints, t_min_poly      # noqa: E402
    _, thA, thB, _ = cell_joints()
    T, _ = t_min_poly(thB - thA, VMAX, AMAX, "quintic", JMAX)
    return thA, thB, T


TAU_MAX = np.array([150.0, 150.0, 150.0, 28.0, 28.0, 28.0])   # UR5e 关节力矩上限：3 号关节 150 N·m，1 号关节 28 N·m（UR 公司资料，25.5 节）


def mj_link_motion(mj, m, d, body, q, qd, qdd):
    """MuJoCo 算出的连杆坐标系（xbody）的运动：在连杆自己的坐标系中，(ω, v) 与 (α, a)，a 是原点的加速度（含 MuJoCo 的“基座以 𝔤 向上加速”）。"""
    d.qpos[:], d.qvel[:], d.qacc[:] = q, qd, qdd
    mj.mj_fwdPosition(m, d)
    mj.mj_fwdVelocity(m, d)
    mj.mj_rnePostConstraint(m, d)
    bid = mj.mj_name2id(m, mj.mjtObj.mjOBJ_BODY, body)
    v, a = np.zeros(6), np.zeros(6)
    mj.mj_objectVelocity(m, d, mj.mjtObj.mjOBJ_XBODY, bid, v, 1)
    mj.mj_objectAcceleration(m, d, mj.mjtObj.mjOBJ_XBODY, bid, a, 1)
    return v, a


def mj_joint_wrenches(mj, m, d, names, q, qd, qdd):
    """MuJoCo 的 cfrc_int（父连杆经关节作用在连杆上的力旋量，写在“以根连杆子树质心为原点、世界坐标系方向”的坐标系中）
    换到各连杆坐标系 {i}：f_i = Rᵀf，m_i = Rᵀ(m_c − (p_i − c) × f)。"""
    d.qpos[:], d.qvel[:], d.qacc[:] = q, qd, qdd
    mj.mj_fwdPosition(m, d)
    mj.mj_fwdVelocity(m, d)
    mj.mj_rnePostConstraint(m, d)
    res = []
    for name in names:
        b = mj.mj_name2id(m, mj.mjtObj.mjOBJ_BODY, name)
        c = d.subtree_com[m.body_rootid[b]]
        R, p = d.xmat[b].reshape(3, 3), d.xpos[b]
        mc, f = d.cfrc_int[b][:3], d.cfrc_int[b][3:]
        res.append(np.r_[R.T @ (mc - np.cross(p - c, f)), R.T @ f])
    return res


def split_wrench(F, w):
    """关节传给连杆的力旋量分成：绕轴力矩、弯曲（倾覆）力矩、轴向力、径向力（25.2.5 节）。w 是关节轴（单位矢量）。"""
    mo, f = F[:3], F[3:]
    ma, fa = mo @ w, f @ w
    return ma, float(np.linalg.norm(mo - ma * w)), fa, float(np.linalg.norm(f - fa * w))
