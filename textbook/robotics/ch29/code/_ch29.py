"""第 29 章共用：动力学仿真。以下划线开头，构建时不单独运行。

前半部分是第 6、12、23～25 章的共用代码（叉积矩阵、罗德里格斯公式、伴随矩阵、UR5e 的旋量轴、常见形体的惯量、空间惯量、
书中网页版 UR5e 模型的读法、数字工厂的毛坯与夹爪、牛顿-欧拉递推与闭式的 M、c、g），原样抄自 _ch25.py，使本章程序自成一体；
后半部分是本章新加的：
- 铰接体算法（ABA，29.1.3 节）与复合刚体算法（CRBA）加楚列斯基分解，两者的运算次数；
- 速度层的时间步进与投影高斯-赛德尔法（PGS，29.1.4 节）：叠放的料箱；
- 单自由度弹簧-阻尼器在各种积分方法下的放大矩阵与稳定区（29.3 节）；
- 带延迟的 PD 关节（29.4 节）。
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



def mj_option(timestep=0.002, integrator="implicitfast", flags="", extra=""):
    """书中 UR5e 模型的 <option>：时间步长、积分器、开关（如 contact="disable"），extra 是 <option> 的其他属性。"""
    return f'<option timestep="{timestep!r}" integrator="{integrator}" {extra}><flag {flags}/></option>'


def ur_model(timestep=0.002, integrator="implicitfast", flags='contact="disable"', tool="", extra=""):
    import mujoco
    m = mujoco.MjModel.from_xml_string(mjcf_text(tool=tool, option=mj_option(timestep, integrator, flags, extra)))
    return mujoco, m, mujoco.MjData(m)


UR_NAMES = ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"]
Q_WORK = np.array([0.0, -1.2, 1.5, -1.9, -1.57, 0.0])     # 本章常用的工作姿态（手臂伸向前方、工具朝下），rad


# ================================================================ 29.1 节：铰接体算法（ABA）

def aba(ch, th, thd, tau, Vd0=GRAV):
    """铰接体算法（算法 29.1.1）：由 θ、θ̇、τ 直接求 θ̈，不形成质量矩阵。记号与第 25 章的 Chain 相同：
    T[i] = Ad_{T_{i,i−1}}，c_i = ad_{𝒱_i} A_i θ̇_i（速度引起的加速度），𝒢^A_i、p^A_i 是铰接体惯量与偏置力。"""
    n = ch.n
    Ad, V, c, IA, pA = [], [], [], [], []
    v = np.zeros(6)
    for i in range(n):                                  # 第一遍（向外）：速度、速度积项、刚体惯量与偏置力
        X = adjoint(ch.T_rel(i, th[i]))
        v = X @ v + ch.A[i] * thd[i]
        Ad.append(X)
        V.append(v)
        c.append(ad(v) @ ch.A[i] * thd[i])
        IA.append(ch.G[i].copy())
        pA.append(-ad(v).T @ ch.G[i] @ v)
    U, D, u = [None] * n, np.zeros(n), np.zeros(n)
    for i in reversed(range(n)):                        # 第二遍（向内）：把关节 i 以外的部分“铰接”成一个等效惯量
        U[i] = IA[i] @ ch.A[i]
        D[i] = ch.A[i] @ U[i] + ch.arm[i]
        u[i] = tau[i] - ch.A[i] @ pA[i]
        if i > 0:
            Ia = IA[i] - np.outer(U[i], U[i]) / D[i]
            pa = pA[i] + Ia @ c[i] + U[i] * u[i] / D[i]
            IA[i - 1] = IA[i - 1] + Ad[i].T @ Ia @ Ad[i]
            pA[i - 1] = pA[i - 1] + Ad[i].T @ pa
    a = np.asarray(Vd0, float)
    thdd = np.zeros(n)
    for i in range(n):                                  # 第三遍（向外）：加速度
        ap = Ad[i] @ a + c[i]
        thdd[i] = (u[i] - U[i] @ ap) / D[i]
        a = ap + ch.A[i] * thdd[i]
    return thdd


class Count:
    """数乘法、加法的次数。按稠密矩阵计：r×c 矩阵乘矢量算 rc 次乘法、r(c − 1) 次加法，不利用矩阵中的零。"""
    mul = 0
    add = 0

    @staticmethod
    def reset():
        Count.mul = Count.add = 0

    @staticmethod
    def mv(A, x):
        r, k = A.shape
        Count.mul += r * k
        Count.add += r * (k - 1)
        return A @ x

    @staticmethod
    def mm(A, B):
        r, k = A.shape
        Count.mul += r * k * B.shape[1]
        Count.add += r * (k - 1) * B.shape[1]
        return A @ B

    @staticmethod
    def dot(x, y):
        Count.mul += len(x)
        Count.add += len(x) - 1
        return x @ y

    @staticmethod
    def vadd(x, y):
        Count.add += np.size(x)
        return x + y

    @staticmethod
    def sc(s, x):
        Count.mul += np.size(x)
        return s * x

    @staticmethod
    def Ad(T):
        """由 T = (R, p) 写出 Ad_T：只有 [p]R 一块要算，9 个元素各 2 次乘法、1 次加法。"""
        Count.mul += 18
        Count.add += 9
        return adjoint(T)


def aba_counted(ch, th, thd, tau, Vd0=GRAV):
    """与 aba 相同的算法，每一步运算都经 Count 计数。"""
    C = Count
    n = ch.n
    Ad, c, IA, pA = [], [], [], []
    v = np.zeros(6)
    for i in range(n):
        X = C.Ad(ch.T_rel(i, th[i]))
        v = C.vadd(C.mv(X, v), C.sc(thd[i], ch.A[i])) if i else C.sc(thd[i], ch.A[i])
        Ad.append(X)
        c.append(C.sc(thd[i], C.mv(ad(v), ch.A[i])))
        IA.append(ch.G[i].copy())
        pA.append(-C.mv(ad(v).T, C.mv(ch.G[i], v)))
    U, D, u = [None] * n, np.zeros(n), np.zeros(n)
    for i in reversed(range(n)):
        U[i] = C.mv(IA[i], ch.A[i])
        D[i] = C.dot(ch.A[i], U[i]) + ch.arm[i]
        u[i] = tau[i] - C.dot(ch.A[i], pA[i])
        C.add += 2
        if i > 0:
            r = 1 / D[i]
            C.mul += 2                                  # 1/D 与 u·(1/D)
            Ia = IA[i] - C.sc(r, np.outer(U[i], U[i]))
            C.mul += 36
            C.add += 36
            pa = C.vadd(C.vadd(pA[i], C.mv(Ia, c[i])), C.sc(u[i] * r, U[i]))
            IA[i - 1] = IA[i - 1] + C.mm(C.mm(Ad[i].T, Ia), Ad[i])
            C.add += 36
            pA[i - 1] = C.vadd(pA[i - 1], C.mv(Ad[i].T, pa))
    a = np.asarray(Vd0, float)
    thdd = np.zeros(n)
    for i in range(n):
        ap = C.vadd(C.mv(Ad[i], a), c[i])
        thdd[i] = (u[i] - C.dot(U[i], ap)) / D[i]
        C.add += 1
        C.mul += 1
        a = C.vadd(ap, C.sc(thdd[i], ch.A[i]))
    return thdd


def crba_counted(ch, th, thd, tau, Vd0=GRAV):
    """复合刚体算法求 M，牛顿-欧拉递推（θ̈ = 0）求 c + g，再用楚列斯基分解解 M θ̈ = τ − c − g。运算经 Count 计数。
    返回 (θ̈, 三部分各自的乘法次数)。"""
    C = Count
    n = ch.n
    m0 = C.mul
    Ad, V, Vd = [], [], []
    v, a = np.zeros(6), np.asarray(Vd0, float)
    for i in range(n):                                   # 牛顿-欧拉递推，θ̈ = 0
        X = C.Ad(ch.T_rel(i, th[i]))
        v = C.vadd(C.mv(X, v), C.sc(thd[i], ch.A[i]))
        a = C.vadd(C.mv(X, a), C.sc(thd[i], C.mv(ad(v), ch.A[i])))
        Ad.append(X)
        V.append(v)
        Vd.append(a)
    bias = np.zeros(n)
    F = np.zeros(6)
    for i in reversed(range(n)):
        Fi = C.vadd(C.mv(ch.G[i], Vd[i]), -C.mv(ad(V[i]).T, C.mv(ch.G[i], V[i])))
        F = C.vadd(Fi, C.mv(Ad[i + 1].T, F)) if i < n - 1 else Fi
        bias[i] = C.dot(F, ch.A[i])
    m1 = C.mul
    Ic = [g.copy() for g in ch.G]                        # 复合刚体惯量：从末端向基座累加
    for i in reversed(range(1, n)):
        Ic[i - 1] = Ic[i - 1] + C.mm(C.mm(Ad[i].T, Ic[i]), Ad[i])
        C.add += 36
    M = np.zeros((n, n))
    for i in range(n):
        F = C.mv(Ic[i], ch.A[i])
        M[i, i] = C.dot(F, ch.A[i]) + ch.arm[i]
        C.add += 1
        for j in range(i - 1, -1, -1):
            F = C.mv(Ad[j + 1].T, F)
            M[i, j] = M[j, i] = C.dot(F, ch.A[j])
    m2 = C.mul
    L = np.zeros((n, n))                                 # 楚列斯基分解 M = LLᵀ（开方算一次乘法）与两次回代
    for j in range(n):
        L[j, j] = math.sqrt(M[j, j] - L[j, :j] @ L[j, :j])
        C.mul += j + 1
        C.add += j
        for i in range(j + 1, n):
            L[i, j] = (M[i, j] - L[i, :j] @ L[j, :j]) / L[j, j]
            C.mul += j + 1
            C.add += j
    b = np.asarray(tau, float) - bias
    C.add += n
    y = np.zeros(n)
    for i in range(n):
        y[i] = (b[i] - L[i, :i] @ y[:i]) / L[i, i]
        C.mul += i + 1
        C.add += i
    x = np.zeros(n)
    for i in reversed(range(n)):
        x[i] = (y[i] - L[i + 1:, i] @ x[i + 1:]) / L[i, i]
        C.mul += n - i
        C.add += n - 1 - i
    m3 = C.mul
    return x, (m1 - m0, m2 - m1, m3 - m2)


def random_chain(n, rng):
    """n 个关节的随机串联臂：关节轴、相邻连杆的位姿、连杆的质量与惯量随机取（只用来数运算次数和核对算法）。"""
    import copy
    ch = copy.copy(ur_chain())
    ch.n = n
    ch.A, ch.Mi, ch.G = [], [], []
    for _ in range(n):
        w = rng.normal(size=3)
        ch.A.append(np.r_[w / np.linalg.norm(w), 0, 0, 0])
        u = rng.normal(size=3)
        ch.Mi.append(tf(rot(u / np.linalg.norm(u), rng.uniform(-math.pi, math.pi)), rng.normal(size=3) * 0.1))
        ch.G.append(G_frame(np.diag(rng.uniform(0.01, 0.05, 3)), rng.uniform(1, 3), np.eye(3), rng.normal(size=3) * 0.05))
    ch.arm = np.full(n, 0.1)
    ch.names = [f"j{i + 1}" for i in range(n)]
    return ch


# ================================================================ 29.1 节：时间步进与投影高斯-赛德尔法

def stack_delassus(masses):
    """叠放的 N 个料箱，只考虑竖直方向、不计摩擦：接触 k 在料箱 k − 1 与 k 之间（料箱 0 是地面）。
    间隙的变化率 ġ_k = v_k − v_{k−1}，J 的第 k 行是 e_k − e_{k−1}；返回 J 与 A = J M⁻¹ Jᵀ（式 (29.1.6)）。"""
    N = len(masses)
    J = np.zeros((N, N))
    for k in range(N):
        J[k, k] = 1.0
        if k > 0:
            J[k, k - 1] = -1.0
    A = J @ np.diag(1.0 / np.asarray(masses, float)) @ J.T
    return J, A


def pgs(A, b, lam0=None, iters=100, order=None, tol=0.0):
    """投影高斯-赛德尔法解 LCP：0 ≤ λ ⊥ Aλ + b ≥ 0。order：逐个更新接触的顺序。返回 (λ, 每次迭代后 λ 的历史)。"""
    n = len(b)
    lam = np.zeros(n) if lam0 is None else np.array(lam0, float)
    order = range(n) if order is None else order
    hist = []
    for _ in range(iters):
        for k in order:
            lam[k] = max(0.0, lam[k] - (A[k] @ lam + b[k]) / A[k, k])
        hist.append(lam.copy())
        if tol and np.linalg.norm(np.minimum(lam, A @ lam + b)) < tol:
            break
    return lam, hist


def stack_xml(N, solver="Newton", iterations=100, size=(0.4, 0.3, 0.2), mass=8.0, top=None, timestep=0.002, tolerance=1e-8):
    """MuJoCo 中叠放的 N 个料箱（400 mm × 300 mm × 200 mm，满载 8 kg，示意值）；top 给出时最上面一个的质量。"""
    a, b, c = size
    s = ""
    for k in range(N):
        mk = top if (top is not None and k == N - 1) else mass
        s += (f'<body name="box{k + 1}" pos="0 0 {c / 2 + k * c!r}"><freejoint/>'
              f'<geom type="box" size="{a / 2!r} {b / 2!r} {c / 2!r}" mass="{mk!r}" rgba="0.2 0.45 0.7 1"/></body>')
    return (f'<mujoco><option timestep="{timestep!r}" solver="{solver}" iterations="{iterations}" tolerance="{tolerance!r}"/>'
            f'<worldbody><geom type="plane" size="3 3 0.1"/>{s}</worldbody></mujoco>')


def run_stack(N, solver, iterations, T=2.0, **kw):
    """仿真 T 秒，返回 (顶上料箱下沉的距离 m, 最大倾角 rad, 每步求解器迭代次数的平均值, 最大值)。"""
    import mujoco
    m = mujoco.MjModel.from_xml_string(stack_xml(N, solver, iterations, **kw))
    d = mujoco.MjData(m)
    c = kw.get("size", (0.4, 0.3, 0.2))[2]
    nit = []
    while d.time < T - 1e-12:
        mujoco.mj_step(m, d)
        nit.append(int(d.solver_niter[0]))
    q = d.qpos.reshape(N, 7)
    tilt = max(2 * math.acos(min(1.0, abs(q[k, 3]))) for k in range(N))
    return c / 2 + (N - 1) * c - q[-1, 2], tilt, float(np.mean(nit)), int(np.max(nit))


# ================================================================ 29.2 节：从零写一个模型

ARM2 = dict(L1=0.40, L2=0.30, r=0.025, rho=2700.0)       # 两连杆臂：铝管做的连杆（示意值），胶囊体的半径与长度


def capsule_mass_inertia(r, L, rho):
    """胶囊体（圆柱长 L、两端半球半径 r）的质量与对质心的主惯量 (I_轴向, I_横向)：圆柱 + 两个半球，半球质心离底面 3r/8。"""
    mc = rho * math.pi * r * r * L
    ms = rho * 4 / 3 * math.pi * r ** 3
    Ia = mc * r * r / 2 + ms * 2 * r * r / 5
    It = mc * (r * r / 4 + L * L / 12) + ms * (2 * r * r / 5 + L * L / 4 + 3 * L * r / 8)
    return mc + ms, Ia, It


def arm2_xml(timestep=0.002, integrator="Euler", kp=None, kv=None, damping=0.0, angle_unit=None, flags='energy="enable"', one=False):
    """两连杆臂的 MJCF（程序 29.2.1 列出的模型）：竖直平面内两个铰链关节，连杆是铝制胶囊体，惯量由几何体算出。
    kp 给出时加两个位置伺服（position 执行器，kv 为速度增益）；angle_unit 给出时写 <compiler angle=...>；one=True 时只有连杆 1（单摆）。"""
    p = ARM2
    comp = f'<compiler angle="{angle_unit}"/>' if angle_unit else ""
    act = ""
    if kp is not None:
        kvs = f' kv="{kv!r}"' if kv else ""
        act = (f'<actuator><position name="a1" joint="j1" kp="{kp!r}"{kvs}/>'
               f'<position name="a2" joint="j2" kp="{kp!r}"{kvs}/></actuator>')
    link2 = "" if one else f'''
      <body name="link2" pos="{p['L1']!r} 0 0">
        <joint name="j2" range="-150 150"/>
        <geom fromto="0 0 0 {p['L2']!r} 0 0"/>
      </body>'''
    return f'''<mujoco model="arm2">{comp}
  <option timestep="{timestep!r}" integrator="{integrator}"><flag {flags}/></option>
  <default><joint type="hinge" axis="0 1 0" damping="{damping!r}"/><geom type="capsule" size="{p['r']!r}" density="{p['rho']!r}"/></default>
  <worldbody>
    <body name="link1" pos="0 0 1">
      <joint name="j1" range="-170 170"/>
      <geom fromto="0 0 0 {p['L1']!r} 0 0"/>{link2}
    </body>
  </worldbody>{act}
</mujoco>'''


def arm2_M(q, m1, I1, a1, m2, I2, a2, L1):
    """平面两连杆臂的质量矩阵（式 (24.2.4)，J_i = I_i + m_i a_i²，β = m₂L₁a₂cos q₂）：I_i 对质心，a_i 是质心到关节的距离。关节轴为 +y、角度从 x 轴量起。"""
    c2 = math.cos(q[1])
    M11 = I1 + m1 * a1 ** 2 + I2 + m2 * (L1 ** 2 + a2 ** 2 + 2 * L1 * a2 * c2)
    M12 = I2 + m2 * (a2 ** 2 + L1 * a2 * c2)
    return np.array([[M11, M12], [M12, I2 + m2 * a2 ** 2]])


# ================================================================ 29.3 节：积分方法的放大矩阵

def amp_matrix(h, w, c, method):
    """单自由度 ẍ = −ω²x − cẋ，一步把 (x, v) 变成 (x⁺, v⁺) 的矩阵。method：
    'euler'（半隐式欧拉，阻尼显式，MuJoCo 的 Euler 处理执行器阻尼时），'implicit'（阻尼隐式，MuJoCo 的 implicitfast 与
    Euler 处理关节 damping 时），'explicit'（显式欧拉），'rk4'。"""
    a, b = h * h * w * w, h * c
    if method == "euler":
        return np.array([[1 - a, h * (1 - b)], [-h * w * w, 1 - b]])
    if method == "implicit":
        return np.array([[1 - a / (1 + b), h / (1 + b)], [-h * w * w / (1 + b), 1 / (1 + b)]])
    if method == "explicit":
        return np.array([[1, h], [-h * w * w, 1 - b]])
    if method == "rk4":
        F = np.array([[0, 1], [-w * w, -c]])
        P = np.eye(2)
        S = np.eye(2)
        for k in range(1, 5):
            P = P @ (h * F) / k
            S = S + P
        return S
    raise ValueError(method)


def h_limit(w, c, method, hmax=1.0):
    """放大矩阵的谱半径不超过 1 的最大步长（二分）。"""
    rho = lambda h: max(abs(np.linalg.eigvals(amp_matrix(h, w, c, method))))
    lo, hi = 0.0, hmax
    if rho(hi) <= 1 + 1e-12:
        return math.inf
    for _ in range(200):
        mid = (lo + hi) / 2
        if rho(mid) <= 1 + 1e-12:
            lo = mid
        else:
            hi = mid
    return lo


def ur_linear(q=Q_WORK):
    """UR5e 在姿态 q 附近的线性化：质量矩阵 M（含转子惯量）与模型执行器的刚度 K = diag(kp)、阻尼 D = diag(kd)（gainprm、biasprm）。"""
    mujoco, m, d = ur_model()
    d.qpos[:] = q
    mujoco.mj_forward(m, d)
    M = np.zeros((6, 6))
    mujoco.mj_fullM(m, d, M)
    kp = -m.actuator_biasprm[:, 1].copy()
    kd = -m.actuator_biasprm[:, 2].copy()
    assert np.allclose(m.actuator_gainprm[:, 0], kp)
    return M, np.diag(kp), np.diag(kd)


def ur_amp(h, M, K, D, method):
    """多自由度 M q̈ = −K q − D q̇ 一步的放大矩阵：'euler'（D 显式）、'implicit'（D 隐式，(M + hD) v⁺ = Mv − hKq）、'rk4'。"""
    n = len(M)
    I = np.eye(n)
    Mi = np.linalg.inv(M)
    if method == "euler":
        Av = np.hstack([-h * Mi @ K, I - h * Mi @ D])
    elif method == "implicit":
        B = np.linalg.inv(M + h * D)
        Av = np.hstack([-h * B @ K, B @ M])
    elif method == "rk4":
        F = np.block([[np.zeros((n, n)), I], [-Mi @ K, -Mi @ D]])
        P, S = np.eye(2 * n), np.eye(2 * n)
        for k in range(1, 5):
            P = P @ (h * F) / k
            S = S + P
        return S
    else:
        raise ValueError(method)
    Aq = np.hstack([I, np.zeros((n, n))]) + h * Av
    return np.vstack([Aq, Av])


def ur_h_limit(M, K, D, method, hmax=0.2):
    rho = lambda h: max(abs(np.linalg.eigvals(ur_amp(h, M, K, D, method))))
    lo, hi = 0.0, hmax
    if rho(hi) <= 1 + 1e-12:
        return math.inf
    for _ in range(100):
        mid = (lo + hi) / 2
        if rho(mid) <= 1 + 1e-12:
            lo = mid
        else:
            hi = mid
    return lo


# ================================================================ 29.4 节：延迟、采样与模型误差

FC_NOM = np.array([2.0, 2.0, 1.5, 0.6, 0.6, 0.5])          # 关节的库仑摩擦，N·m（示意值，与第 26 章相同）
FV_NOM = np.array([1.5, 1.5, 1.0, 0.3, 0.3, 0.3])          # 黏性摩擦，N·m·s/rad（示意值）
KP_MJ = np.array([2000.0, 2000, 2000, 500, 500, 500])      # 书中模型执行器的增益（Menagerie 的 UR5e）
KD_MJ = np.array([400.0, 400, 400, 100, 100, 100])


def pd_delay_margin(I, kp, kd):
    """单关节 I θ̈ = kp(θ_d − θ(t − T)) − kd θ̇(t − T) 的穿越频率 ω_c、相位裕度 φ_m 与临界延迟 T* = φ_m/ω_c（式 (29.4.2)）。"""
    w2 = (kd * kd + math.sqrt(kd ** 4 + 4 * I * I * kp * kp)) / (2 * I * I)
    wc = math.sqrt(w2)
    pm = math.atan2(kd * wc, kp)
    return wc, pm, pm / wc


def pd_discrete_rho(I, kp, kd, nd, nc=4, h=0.0005):
    """单关节 I θ̈ = τ 的离散控制（与 cr_track 相同：每 h 一步，每 nc 步更新一次力矩并保持；测量延迟 nd 步）：
    τ = −kp θ_{k−nd} − kd ω_{k−nd}。返回一个控制周期的转移矩阵的谱半径（> 1 不稳定）。状态：[x_k, x_{k−1}, …, x_{k−nd}, τ]。"""
    n = 2 + 2 * nd + 1
    A = np.array([[1.0, h], [0.0, 1.0]])
    B = np.array([h * h / 2 / I, h / I])

    def one(sample):
        S = np.zeros((n, n))
        u = np.zeros(n)
        if sample:
            u[2 * nd], u[2 * nd + 1] = -kp, -kd
        else:
            u[n - 1] = 1.0
        S[0:2, 0:2] = A
        S[0:2, :] += np.outer(B, u)
        for i in range(nd):
            S[2 + 2 * i:4 + 2 * i, 2 * i:2 * i + 2] = np.eye(2)
        S[n - 1, :] = u
        return S
    T = np.eye(n)
    for k in range(nc):
        T = one(k == 0) @ T
    return float(max(abs(np.linalg.eigvals(T))))


def pd_gains(Mdiag, wn, zeta=1.0):
    """按质量矩阵的对角元设计各关节的 PD：kp = M_ii ω_n²，kd = 2ζω_n M_ii。"""
    Mdiag = np.asarray(Mdiag, float)
    return Mdiag * wn * wn, 2 * zeta * wn * Mdiag


def real_ur(payload=None, fc=FC_NOM, fv=FV_NOM, h=0.0005):
    """“现场”的 UR5e：书中模型加上关节摩擦（frictionloss、damping），关掉执行器，力矩由程序经 qfrc_applied 施加；关掉关节限位。"""
    import mujoco
    tool = payload_xml(*payload) if payload is not None else ""
    t = mjcf_text(tool=tool, option=mj_option(h, "implicitfast", 'contact="disable" actuation="disable"'))
    for nm, c, v in zip(UR_NAMES, fc, fv):
        t, k = re.subn(rf'<joint name="{nm}"', f'<joint name="{nm}" frictionloss="{float(c)!r}" damping="{float(v)!r}"', t)
        assert k == 1
    m = mujoco.MjModel.from_xml_string(t)
    m.jnt_limited[:] = 0
    return mujoco, m, mujoco.MjData(m)


def tcp_point(ch, q):
    """TCP（法兰前 0.15 m，沿工具方向 y）在世界坐标系中的位置。"""
    return (ch.flange_pose(q) @ np.array([0, TCP, 0, 1.0]))[:3]


def track(kp, kd, ff_model=None, fric_ff=None, payload=None, fc=FC_NOM, fv=FV_NOM, delay=0.0, Tc=0.002, h=0.0005,
          hold=1.0, move=None, every=0.01):
    """跟踪上下料动作（第 22 章的五次多项式，θ_A → θ_B，再停 hold 秒）：控制器每 Tc 采样一次，用 delay 秒以前的关节角和角速度，
    τ = K_p(θ_d − θ) + K_d(θ̇_d − θ̇) [+ 名义模型的逆动力学 RNEA(θ_d, θ̇_d, θ̈_d)] [+ 摩擦前馈 f_c sgn θ̇_d + f_v θ̇_d]，限幅后零阶保持。
    返回 dict：TCP 的最大误差（m）、停住后最后 0.5 s 关节角速度的最大值（rad/s，振荡的指标）、时间和关节误差的记录。"""
    thA, thB, T = cell_move() if move is None else move
    mujoco, m, d = real_ur(payload, fc, fv, h)
    ch_true = ur_chain(payload=payload)
    d.qpos[:] = thA
    nd = int(round(delay / h))
    nc = int(round(Tc / h))
    ne = int(round(every / h))
    buf = [(thA.copy(), np.zeros(6))] * (nd + 1)
    tau = np.zeros(6)
    Ttot = T + hold
    e_tcp, v_tail = 0.0, 0.0
    ts, es = [], []
    k = 0
    while d.time < Ttot - 1e-12:
        buf.append((d.qpos.copy(), d.qvel.copy()))
        buf.pop(0)
        if k % nc == 0:
            q, qd = buf[0]
            qr, vr, ar = quintic(thA, thB, T, d.time)
            tau = kp * (qr - q) + kd * (vr - qd)
            if ff_model is not None:
                tau = tau + ff_model.rnea(qr, vr, ar)
            if fric_ff is not None:
                tau = tau + fric_ff[0] * np.tanh(vr / 0.01) + fric_ff[1] * vr
            tau = np.clip(tau, -TAU_MAX, TAU_MAX)
        d.qfrc_applied[:] = tau
        mujoco.mj_step(m, d)
        k += 1
        if not np.isfinite(d.qpos).all():
            return dict(e_tcp=math.inf, v_tail=math.inf, t=np.array(ts), e=np.array(es))
        if k % ne == 0:
            qr, _, _ = quintic(thA, thB, T, d.time)
            e = float(np.linalg.norm(tcp_point(ch_true, d.qpos) - tcp_point(ch_true, qr)))
            e_tcp = max(e_tcp, e)
            ts.append(d.time)
            es.append(e)
        if d.time > Ttot - 0.5:
            v_tail = max(v_tail, float(np.abs(d.qvel).max()))
    return dict(e_tcp=e_tcp, v_tail=v_tail, t=np.array(ts), e=np.array(es))


# ================================================================ 第 58 轮：问渠机器人厂的 WQ-CR5（本章的主角）
# 模型由 factory/digital/cae/wqcr5.py 生成（零件库 B-ARM-WQCR5，教材 models/mjcf/wqcr5.xml）；这里直接读那个模块的常数，
# 与机器人厂、问渠 CAE 用的是同一台机器人。全部是示例值。

def wqcr5():
    """原件模块（只用 numpy）"""
    p = str(ROOT / "factory" / "digital" / "cae")
    if p not in sys.path:
        sys.path.insert(0, p)
    import wqcr5 as W                    # noqa: E402
    return W


CR_NAMES = ["J1", "J2", "J3", "J4", "J5", "J6"]
Q_CR = np.radians([0.0, -60.0, 80.0, -110.0, -90.0, 0.0])   # 本章 WQ-CR5 的工作姿态（手臂前伸、工具朝下），rad


def cr_text(tool="", option="", world="", actuator=""):
    return mjcf_text("wqcr5", tool=tool, option=option, world=world, actuator=actuator)


def cr_flange():
    """法兰坐标系 {f} 在连杆 6 坐标系中的位姿：方向相同，原点在 (0, 0, d6)，工具方向 +z"""
    return tf(None, np.array([0, 0, wqcr5().DH[5]["d"]]))


def cr_load():
    """负载跑合台的标准负载（钢块约 5 kg）：质量、对法兰的质心、对质心的惯量（方向同 {f}）"""
    L = wqcr5().RUNIN_LOAD
    a, b, c = L["size"]
    return L["mass"], np.array(L["com"], float), box_inertia(L["mass"], a, b, c)


def cr_load_xml():
    return wqcr5().runin_load_xml()


def cr_chain(payload=None, friction=False):
    """WQ-CR5 的递推数据：连杆参数从 MJCF 读出（与网页实验、零件库同一份），转子惯量取 MJCF 的 armature。"""
    W = wqcr5()
    return Chain(parse_links(cr_text()), payload=payload, arm=np.array(W.armature()), Mf=cr_flange())


def cr_model(timestep=0.002, integrator="implicitfast", flags='contact="disable"', tool="", actuator="", extra=""):
    import mujoco
    m = mujoco.MjModel.from_xml_string(cr_text(tool=tool, actuator=actuator, option=mj_option(timestep, integrator, flags, extra)))
    return mujoco, m, mujoco.MjData(m)


def cr_servo_xml(kp=None, kv=None):
    """出厂位置环写成 MJCF 的 position 执行器（放在 <!--ACTUATOR--> 处）：force = kp(ctrl − q) − kv q̇"""
    W = wqcr5()
    kp = W.SERVO_KP if kp is None else kp
    kv = W.SERVO_KV if kv is None else kv
    lim = W.torque_limit()
    return "".join(f'<position name="pos_{n}" joint="{n}" kp="{float(a)!r}" kv="{float(b)!r}" forcerange="{-l!r} {l!r}"/>'
                   for n, a, b, l in zip(CR_NAMES, kp, kv, lim))


def cr_tau_max():
    return np.array(wqcr5().torque_limit())


def cr_linear(q=Q_CR, payload=False, kp=None, kv=None):
    """WQ-CR5 在姿态 q 附近：质量矩阵 M（含转子惯量）、位置环的刚度 K = diag(kp)、阻尼 D = diag(kv)（加上关节的黏性摩擦）"""
    W = wqcr5()
    _, m, d = cr_model(tool=cr_load_xml() if payload else "")
    import mujoco
    d.qpos[:] = q
    mujoco.mj_forward(m, d)
    M = np.zeros((6, 6))
    mujoco.mj_fullM(m, d, M)
    kp = np.array(W.SERVO_KP if kp is None else kp, float)
    kv = np.array(W.SERVO_KV if kv is None else kv, float)
    return M, np.diag(kp), np.diag(kv + m.dof_damping)


def cr_friction():
    """名义摩擦（MJCF 的 frictionloss、damping；库仑摩擦 = 机器人厂关节测试台“空载摩擦力矩”的名义值）"""
    W = wqcr5()
    fc = np.array([W.MODULES[s]["frictionloss"] for s in W.JOINT_MODULE])
    fv = np.array([W.MODULES[s]["damping"] for s in W.JOINT_MODULE])
    return fc, fv


def cr_test_sigma():
    """关节测试台的散布（plants/wenquest-robot.yaml）：每个关节的空载摩擦力矩名义值、σ，背隙名义值、σ（arcmin）"""
    import yaml
    W = wqcr5()
    plant = yaml.safe_load((ROOT / "factory" / "plants" / "wenquest-robot.yaml").read_text(encoding="utf-8"))
    ch = {m["item"]: {c["code"]: c for c in m["chars"]} for m in plant["measurements"]}
    out = []
    for s in W.JOINT_MODULE:
        c = ch[W.MODULES[s]["code"]]
        out.append(dict(fric=c["joint_friction"]["nominal"], fric_sigma=c["joint_friction"]["sigma"], fric_hi=c["joint_friction"]["hi"],
                        backlash=c["joint_backlash"]["nominal"], backlash_sigma=c["joint_backlash"]["sigma"],
                        backlash_hi=c["joint_backlash"]["hi"]))
    return out


def real_cr(payload=True, fc=None, fv=None, h=0.0005):
    """“现场”的 WQ-CR5：零件库模型，关节摩擦取给定值，关掉执行器（力矩由程序经 qfrc_applied 施加）、关节限位。"""
    import mujoco
    fc0, fv0 = cr_friction()
    fc = fc0 if fc is None else fc
    fv = fv0 if fv is None else fv
    _, m, d = cr_model(timestep=h, flags='contact="disable" actuation="disable"', tool=cr_load_xml() if payload else "")
    m.dof_frictionloss[:] = fc
    m.dof_damping[:] = fv
    m.jnt_limited[:] = 0
    return mujoco, m, d


def cr_tcp(ch, q):
    """TCP：法兰前 0.1 m、偏 0.05 m（与整机标定的工具点相同）"""
    return (ch.flange_pose(q) @ np.array([0.05, 0, 0.10, 1.0]))[:3]


def cr_track(kp, kd, ff_model=None, fric_ff=None, scale=1.0, fc=None, fv=None, delay=0.0, Tc=0.002, h=0.0005,
             ref=None, T=None, every=0.01, backlash=None):
    """跟踪负载跑合台的标准动作（wqcr5.runin_ref）：控制器每 Tc 采样一次，用 delay 秒以前的关节角和角速度，
    τ = K_p(θ_d − θ) + K_d(θ̇_d − θ̇) [+ 名义模型的逆动力学] [+ 摩擦前馈]，限幅后零阶保持。
    scale：负载的质量、惯量是名义的几倍（模型误差）；backlash：各关节的背隙（rad），编码器在电机侧，测得的关节角有 ±backlash/2 的死区。
    返回 dict：TCP 的最大误差（m）、最后 0.3 s 关节角速度的最大值（rad/s，振荡的指标）、记录。"""
    W = wqcr5()
    ref = W.runin_ref if ref is None else ref
    T = W.runin_duration() if T is None else T
    import mujoco
    m_l, c_l, I_l = cr_load()
    mj, m, d = real_cr(True, fc, fv, h)
    bid = mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_BODY, "load")
    m.body_mass[bid] *= scale
    m.body_inertia[bid] *= scale
    ch_true = cr_chain(payload=(m_l * scale, c_l, I_l * scale))
    q0, _, _ = ref(0.0)
    d.qpos[:] = q0
    nd, nc, ne = int(round(delay / h)), int(round(Tc / h)), int(round(every / h))
    buf = [(q0.copy(), np.zeros(6))] * (nd + 1)
    tau = np.zeros(6)
    tmax = cr_tau_max()
    e_tcp = v_tail = 0.0
    vj_tail = np.zeros(6)
    ts, es = [], []
    gap = np.zeros(6) if backlash is None else np.asarray(backlash, float) / 2
    motor = q0.copy()                                     # 电机侧（减速前）的位置：关节角在 motor ± gap 之内自由
    k = 0
    while d.time < T - 1e-12:
        if backlash is not None:                          # 齿隙：关节角离电机侧超出间隙时，电机侧被带着走
            motor = np.clip(motor, d.qpos - gap, d.qpos + gap)
        meas = motor if backlash is not None else d.qpos
        buf.append((meas.copy(), d.qvel.copy()))
        buf.pop(0)
        if k % nc == 0:
            q, qd = buf[0]
            qr, vr, ar = ref(d.time)
            tau = kp * (qr - q) + kd * (vr - qd)
            if ff_model is not None:
                tau = tau + ff_model.rnea(qr, vr, ar)
            if fric_ff is not None:
                tau = tau + fric_ff[0] * np.tanh(vr / 0.01) + fric_ff[1] * vr
            tau = np.clip(tau, -tmax, tmax)
        d.qfrc_applied[:] = tau
        mujoco.mj_step(m, d)
        k += 1
        if not np.isfinite(d.qpos).all() or np.abs(d.qvel).max() > 100:
            return dict(e_tcp=math.inf, v_tail=math.inf, t=np.array(ts), e=np.array(es))
        if k % ne == 0:
            qr, _, _ = ref(d.time)
            e = float(np.linalg.norm(cr_tcp(ch_true, d.qpos) - cr_tcp(ch_true, qr)))
            e_tcp = max(e_tcp, e)
            ts.append(d.time)
            es.append(e)
        if d.time > T - 0.3:
            v_tail = max(v_tail, float(np.abs(d.qvel).max()))
            vj_tail = np.maximum(vj_tail, np.abs(d.qvel))
    return dict(e_tcp=e_tcp, v_tail=v_tail, vj_tail=vj_tail, t=np.array(ts), e=np.array(es))
