"""第 27 章共用：接触、碰撞与摩擦。以下划线开头，构建时不单独运行。

前半部分是第 6、12、23～25 章的共用代码（叉积矩阵、伴随矩阵、UR5e 的旋量轴、空间惯量、书中网页版 UR5e 模型的读法、
数字工厂的毛坯与夹爪、牛顿-欧拉递推 Chain、第 22 章的上下料动作），从第 26 章原样抄来，使本章程序自成一体；
后半部分是本章新加的：
- 赫兹接触：等效弹性模量、线接触与球-平面接触、弹性碰撞的峰值力与接触时间（27.1、27.3 节）；
- MuJoCo 软接触的阻抗函数 d(r) 与静止时的穿透量（27.1.4 节）；
- 两指夹爪（平口、V 形）夹 SH-301 毛坯：接触点、法向、线性化摩擦锥，最小夹紧力的线性规划（27.2、27.4 节）；
- 在 MuJoCo 里“做实验”：夹爪夹住毛坯提起来、毛坯掉到料台上（27.2、27.3 节）；
- 力封闭的判断与抓取质量（27.4 节）。
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


# ================================================================ 第 27 章：接触、碰撞与摩擦

E_STEEL = 210e9                          # 钢的弹性模量，Pa（手册值）
NU_STEEL = 0.3                           # 钢的泊松比
MU_JAW = 0.2                             # 钢制夹爪与钢毛坯之间的摩擦系数（干摩擦，示意值）
PAD_HALF = 0.02                          # 夹爪指面沿毛坯轴线的半长，m（示意值）：线接触用两端两点代表
V_HALF = math.pi / 4                     # V 形夹爪：接触线与夹紧方向的夹角 γ（90° V 形槽，γ = 45°）


def e_star(E1=E_STEEL, nu1=NU_STEEL, E2=E_STEEL, nu2=NU_STEEL):
    """赫兹接触的等效弹性模量 E* = [(1 − ν₁²)/E₁ + (1 − ν₂²)/E₂]⁻¹（式 (27.1.2)）。"""
    return 1.0 / ((1 - nu1 ** 2) / E1 + (1 - nu2 ** 2) / E2)


def hertz_line(P_len, R, Es=None):
    """圆柱与平面的线接触（单位长度载荷 P'）：接触半宽 b = √(4P'R/(πE*))，最大压强 p₀ = 2P'/(πb)（式 (27.1.4)）。"""
    Es = e_star() if Es is None else Es
    b = math.sqrt(4 * P_len * R / (math.pi * Es))
    return b, 2 * P_len / (math.pi * b)


def hertz_sphere(F, R, Es=None):
    """球与平面（或两球，R 为等效半径）：F = (4/3)E*√R δ^{3/2}（式 (27.1.3)），接触圆半径 a = √(Rδ)，p₀ = 3F/(2πa²)。"""
    Es = e_star() if Es is None else Es
    delta = (3 * F / (4 * Es * math.sqrt(R))) ** (2 / 3)
    a = math.sqrt(R * delta)
    return delta, a, 3 * F / (2 * math.pi * a * a)


def _tc_coef():
    """2∫₀¹ dx/√(1 − x^{5/2})：赫兹弹性碰撞的接触时间 t_c = (系数)·δ_max/v（式 (27.3.3)）。"""
    from scipy.integrate import quad
    return 2 * quad(lambda x: 1 / math.sqrt(1 - x ** 2.5), 0, 1, limit=200)[0]


TC_COEF = _tc_coef()


def hertz_impact(m, R, v, Es=None):
    """质量 m、等效半径 R 的球以速度 v 撞平面（完全弹性，赫兹）：最大压入量、峰值力、接触时间（式 (27.3.3)）。"""
    Es = e_star() if Es is None else Es
    K = 4 / 3 * Es * math.sqrt(R)
    dmax = (5 * m * v * v / (4 * K)) ** 0.4
    Fmax = K * dmax ** 1.5
    tc = TC_COEF * dmax / v
    return dmax, Fmax, tc


def contact_ode(m, v, K, n=1.5, c=0.0, kind="hc", dt=1e-8, tmax=1.0):
    """单自由度碰撞的数值积分：δ̈ = −λ/m。kind = "kv"：λ = Kδ + cδ̇（开尔文-沃伊特，力为负时分离）；
    "hc"：λ = Kδⁿ(1 + cδ̇)（亨特-克罗斯利）。返回恢复系数、接触时间、峰值力和 (t, δ, λ) 曲线。"""
    d, dd, t, Fm = 0.0, v, 0.0, 0.0
    T, D, F = [0.0], [0.0], [0.0]
    while t < tmax:
        lam = (K * max(d, 0) ** n * (1 + c * dd)) if kind == "hc" else (K * d + c * dd)
        if t > 0 and (d <= 0 or lam <= 0):
            break
        lam = max(lam, 0.0)
        acc = -lam / m
        # 半隐式欧拉，步长足够小
        dd += acc * dt
        d += dd * dt
        t += dt
        Fm = max(Fm, lam)
        if len(T) < 4000 or int(t / dt) % 50 == 0:
            T.append(t); D.append(d); F.append(lam)
    return -dd / v, t, Fm, (np.array(T), np.array(D), np.array(F))


# ---------------------------------------------------------------- MuJoCo 软接触（27.1.4 节）

SOLIMP = (0.9, 0.95, 0.001, 0.5, 2.0)     # MuJoCo 的默认 solimp：d₀、d_宽、宽度、中点、指数


def mj_impedance(r, imp=SOLIMP):
    """MuJoCo 的阻抗 d(r)：|r| 从 0 到“宽度”时由 d₀ 平滑地过渡到 d_宽（两段幂函数），之外为 d_宽。"""
    d0, dw, w, mid, p = imp
    x = min(abs(r) / w, 1.0)
    if x >= 1:
        return dw
    y = (x / mid) ** p / 2 if x <= mid else 1 - ((1 - x) / (1 - mid)) ** p / 2
    return d0 + y * (dw - d0)


def mj_rest_penetration(timeconst=0.02, dampratio=1.0, g=G0, imp=SOLIMP):
    """静止接触的穿透量：(1 − d)(−g) + d·k|r| = 0，k = d/(d_宽 τ ζ)² ⇒ |r| = (1 − d)g(d_宽 τ ζ)²/d²（式 (27.1.7)），d 依赖 r，迭代求解。"""
    r = 1e-4
    for _ in range(200):
        d = mj_impedance(r, imp)
        r = (1 - d) * g * (imp[1] * timeconst * dampratio) ** 2 / d ** 2
    return r


def ball_xml(m=1.0, r=0.05, h=0.5, solref="0.02 1", dt=0.001, condim=1, extra=""):
    """一个球落在地面上；两个几何体都用同一个 solref（MuJoCo 按两者的平均值混合）。"""
    return (f'<mujoco><option timestep="{dt}"/><default><geom solref="{solref}" condim="{condim}"/></default><worldbody>'
            f'<geom type="plane" size="2 2 0.1"/>{extra}<body name="b" pos="0 0 {r + h}"><freejoint/>'
            f'<geom type="sphere" size="{r}" mass="{m}"/></body></worldbody></mujoco>')


def mj_rest(xml, steps=4000):
    import mujoco
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    for _ in range(steps):
        mujoco.mj_step(m, d)
    return m, d


def mj_drop(xml, tmax=3.0):
    """落下、第一次接触到分离：返回恢复系数（离开与撞入的竖直速度之比）、接触持续时间、峰值接触力、最大穿透量。"""
    import mujoco
    m = mujoco.MjModel.from_xml_string(xml)
    d = mujoco.MjData(m)
    vin = None
    t_in = 0.0
    Fm = 0.0
    pen = 0.0
    f = np.zeros(6)
    while d.time < tmax:
        mujoco.mj_step(m, d)
        if d.ncon > 0:
            if vin is None:
                vin, t_in = -d.qvel[2], d.time
            mujoco.mj_contactForce(m, d, 0, f)
            Fm = max(Fm, f[0])
            pen = max(pen, -d.contact[0].dist)
        elif vin is not None:
            return d.qvel[2] / vin, d.time - t_in, Fm, pen, vin
    return 0.0, None, Fm, pen, vin


def kv_restitution_no_tension(zeta, tau=0.02, v=3.0, dt=1e-7):
    """质量归一的线性弹簧-阻尼接触（ω_n = 1/(τζ)，阻尼比 ζ）在接触力降为零时分离：恢复系数（与 v 无关）。"""
    w = 1 / (tau * zeta)
    x, xd, t = 0.0, -v, 0.0
    while True:
        a = -2 * zeta * w * xd - w * w * x
        xd += a * dt
        x += xd * dt
        t += dt
        if t > 1e-5 and 2 * zeta * w * xd + w * w * x >= 0:
            return xd / v


# ---------------------------------------------------------------- 两指夹爪夹毛坯（27.2、27.4 节）
# 夹爪坐标系 {h}：原点在 TCP（夹持点），z_h 沿毛坯轴线指向法兰（毛坯的质心在 z_h = −d），x_h 为夹紧方向。
# 在连杆 6 的坐标系中：x_h = x_6，y_h = z_6，z_h = −y_6，原点在 (0, FLANGE_Y + TCP, 0)。

R_6H = np.array([[1.0, 0, 0], [0, 0, -1.0], [0, 1.0, 0]])
P_6H = np.array([0, FLANGE_Y + TCP, 0])


def blank_in_hand():
    """毛坯在 {h} 中：质量、质心 (0, 0, −d)、对质心的惯量（轴线沿 z_h）。"""
    m_b, r_b, L_b = sh301_blank()
    d = L_b / 2 - GRIP_TOP
    I = cyl_inertia(m_b, r_b, L_b)                      # 轴线沿 z
    return m_b, np.array([0, 0, -d]), I


def jaw_contacts(jaw="flat", gam=V_HALF, half=PAD_HALF, r=D_BAR / 2):
    """接触点（在 {h} 中）、内法向（夹爪对毛坯的压力方向）和所属夹爪（0：+x 一侧，1：−x 一侧）。
    平口：每个夹爪一条接触线；V 形：每个夹爪两条，与夹紧方向成 ±γ。每条线用两端两点（z = ±half）代表。"""
    C = []
    for s, j in ((1, 0), (-1, 1)):
        for a in ([0.0] if jaw == "flat" else [gam, -gam]):
            ang = a if s > 0 else math.pi - a
            p = np.array([r * math.cos(ang), r * math.sin(ang), 0.0])
            for z in (half, -half):
                C.append((p + np.array([0, 0, z]), -p / np.linalg.norm(p), j))
    return C


def cone_edges(n, mu, k):
    """线性化摩擦锥：以 n 为轴、半顶角 arctan μ 的圆锥的 k 条母线（内接棱锥，式 (27.2.3)）。"""
    t1 = np.cross(n, [0, 0, 1.0]) if abs(n[2]) < 0.9 else np.cross(n, [1.0, 0, 0])
    t1 /= np.linalg.norm(t1)
    t2 = np.cross(n, t1)
    return [n + mu * (math.cos(2 * math.pi * q / k) * t1 + math.sin(2 * math.pi * q / k) * t2) for q in range(k)]


def min_grip(C, F_need, mu=MU_JAW, k=64, equal_ends=False):
    """最小夹紧力（线性规划，式 (27.4.6)）：各接触力在线性化摩擦锥内，所有接触力的合力旋量等于 F_need（在 {h} 中、对 {h} 原点）；
    两指同步（平行夹爪的常见结构）：两个夹爪沿夹紧方向受的力为 F + Δ、F − Δ，Δ 由同步机构承担，取值不限。
    equal_ends：同一条接触线两端的法向力相等（平口指面不能单独压紧一端）。返回 F 与各接触力。"""
    from scipy.optimize import linprog
    cols, jaw_x, nrm, owner = [], [], [], []
    for ci, (p, n, j) in enumerate(C):
        for e in cone_edges(n, mu, k):
            cols.append(np.r_[np.cross(p, e), e])
            jaw_x.append((j, -e[0] if j == 0 else e[0]))
            nrm.append(n @ e)
            owner.append(ci)
    A = np.array(cols).T
    N = A.shape[1]
    rows = [np.r_[A[i], 0.0] for i in range(6)]
    rhs = list(F_need)
    r_ = np.zeros(N + 1)                                    # 两个夹爪的力之和 = 2F（Δ 相消）
    for i, (jj, sx) in enumerate(jaw_x):
        r_[i] = sx
    r_[N] = -2
    rows.append(r_)
    rhs.append(0.0)
    if equal_ends:
        for c in range(0, len(C), 2):
            r_ = np.zeros(N + 1)
            for i in range(N):
                if owner[i] == c:
                    r_[i] = nrm[i]
                elif owner[i] == c + 1:
                    r_[i] = -nrm[i]
            rows.append(r_)
            rhs.append(0.0)
    cost = np.zeros(N + 1)
    cost[N] = 1
    res = linprog(cost, A_eq=np.array(rows), b_eq=np.array(rhs), bounds=[(0, None)] * (N + 1), method="highs")
    if res.status != 0:
        return None, None
    lam = res.x[:N]
    f = np.zeros((len(C), 3))
    for i in range(N):
        f[owner[i]] += lam[i] * np.array(cols[i][3:])
    return res.x[N], f


def blank_wrench(V, Vd):
    """毛坯需要夹爪施加的力旋量（在 {h} 中，对 {h} 原点）：ℱ = 𝒢𝒱̇ − [ad_𝒱]ᵀ𝒢𝒱（式 (23.3.16)），𝒱̇ 中含 (0, −𝔤)。"""
    m_b, c, I = blank_in_hand()
    G = G_frame(I, m_b, np.eye(3), c)
    return G @ Vd - ad(V).T @ G @ V


def hand_motion(ch, th, thd, thdd):
    """{h} 的运动旋量及其导数（在 {h} 中，含“基座以 𝔤 向上加速”）。{h} 固定在连杆 6 上。"""
    _, Vs, Vds = ch.forward(th, thd, thdd)
    A = adjoint(inv(tf(R_6H, P_6H)))
    return A @ Vs[-1], A @ Vds[-1]


def force_closure(W, tol=1e-9):
    """一组力旋量（列）能否正张成整个空间（定理 27.4.1）：满秩，且存在严格为正的 k 使 Wk = 0。
    线性规划：max s，Wk = 0，k ≥ s，Σk = 1。返回 (是否力封闭, s)。"""
    from scipy.optimize import linprog
    n, N = W.shape
    if np.linalg.matrix_rank(W, 1e-10) < n:
        return False, 0.0
    c = np.zeros(N + 1)
    c[N] = -1
    Aeq = np.zeros((n + 1, N + 1))
    Aeq[:n, :N] = W
    Aeq[n, :N] = 1
    beq = np.r_[np.zeros(n), 1.0]
    Aub = np.zeros((N, N + 1))
    for i in range(N):
        Aub[i, i] = -1
        Aub[i, N] = 1
    res = linprog(c, A_ub=Aub, b_ub=np.zeros(N), A_eq=Aeq, b_eq=beq, bounds=[(0, None)] * N + [(None, None)], method="highs")
    s = -res.fun if res.status == 0 else 0.0
    return s > tol, s


def contact_wrenches(C, mu, k=8, scale=1.0, soft=None):
    """各接触的线性化摩擦锥母线对应的单位法向力旋量（力矩除以特征长度 scale）。soft = μ_t（长度）：软指的扭转摩擦，|m_n| ≤ μ_t f_n。"""
    cols = []
    for (p, n, *_) in C:
        for e in cone_edges(n, mu, k):
            cols.append(np.r_[np.cross(p, e) / scale, e])
        if soft:                                         # 软指：法向力 n 连同绕法向的扭转矩 ±μ_t n（纯力偶）
            for sg in (1, -1):
                cols.append(np.r_[(np.cross(p, n) + sg * soft * n) / scale, n])
    return np.array(cols).T


def ferrari_canny(W):
    """抓取质量 ε：W 的各列（每个接触的法向力取 1）的凸包内、以原点为中心的最大球的半径（费拉里-坎尼，式 (27.4.5)）。"""
    from scipy.spatial import ConvexHull
    h = ConvexHull(W.T)
    eq = h.equations                                     # a·x + b ≤ 0 在凸包内，|a| = 1
    if np.any(eq[:, -1] > 0):
        return 0.0
    return float(np.min(-eq[:, -1]))


def gripper_xml(jaw="flat", orient="v", mu=MU_JAW, half=PAD_HALF, gam=V_HALF, ns=10, arm=1e4, dt=0.0005):
    """MuJoCo 中的两指夹爪夹 SH-301 毛坯：夹爪座由竖直滑动关节带着（转子惯量 arm 很大，相当于按给定加速度运动），
    两个指由水平滑动关节和力电机驱动（夹紧力）；平口指是一块板，V 形指是两块成 ±γ 的板。毛坯是圆柱。
    orient = "v"：毛坯竖直（料架上方 A）；"h"：毛坯水平（卡盘前 B，重力垂直于夹紧方向和毛坯轴线）。
    椭圆摩擦锥、impratio = 10、noslip（27.2.3 节）。"""
    m_b, r, L_b = sh301_blank()
    quat = "1 0 0 0" if orient == "v" else "0.7071068 0.7071068 0 0"
    t = 0.005
    fingers = ""
    for s, name in ((1, "f1"), (-1, "f2")):
        g = ""
        angs = [0.0] if jaw == "flat" else [gam, -gam]
        for k, a in enumerate(angs):
            ang = a if s > 0 else math.pi - a
            c = (r + t) * np.array([math.cos(ang), math.sin(ang)]) - np.array([s * (r + 0.006), 0])
            g += (f'<geom name="{name}{k}" type="box" size="{t} 0.012 {half}" pos="{c[0]:.6f} {c[1]:.6f} 0" '
                  f'quat="{math.cos(ang / 2):.7f} 0 0 {math.sin(ang / 2):.7f}" mass="0.1" rgba="0.3 0.32 0.35 1"/>')
        fingers += (f'<body name="{name}" pos="{s * (r + 0.006)} 0 0"><joint name="j{name}" type="slide" axis="{-s} 0 0" damping="20"/>{g}</body>')
    return f"""<mujoco><option timestep="{dt}" cone="elliptic" impratio="10" noslip_iterations="{ns}"/>
<default><geom friction="{mu} 0.005 0.0001" solref="0.004 1"/></default>
<worldbody><body name="carriage" pos="0 0 0.5"><joint name="lift" type="slide" axis="0 0 1" armature="{arm}"/>
<geom type="box" size="0.04 0.04 0.02" pos="0 0 0.12" mass="1.0" rgba="0.25 0.5 0.75 1"/>
<body name="hand" quat="{quat}">{fingers}</body></body>
<body name="blank" pos="0 0 0.5" quat="{quat}"><freejoint/><geom name="bl" type="cylinder" size="{r} {L_b / 2}" pos="0 0 {-(L_b / 2 - GRIP_TOP)}" mass="{m_b}" rgba="0.62 0.63 0.66 1"/></body>
</worldbody><actuator><motor joint="lift"/><motor joint="jf1"/><motor joint="jf2"/></actuator></mujoco>"""


def lift_test(jaw, orient, F, a=0.0, mu=MU_JAW, ta=0.4, T=1.2, settle=0.5):
    """夹紧力 F 夹住毛坯（先在无重力下夹紧），然后在重力下静置 settle 秒，再以加速度 a 提起 ta 秒、减速 ta 秒。
    返回毛坯相对夹爪的最大位移（mm）与转角（°）。"""
    import mujoco
    m = mujoco.MjModel.from_xml_string(gripper_xml(jaw, orient, mu))
    d = mujoco.MjData(m)
    arm = m.dof_armature[0]
    mt = float(np.sum(m.body_mass[1:]))
    d.ctrl[1:] = F
    m.opt.gravity[:] = 0
    for _ in range(int(0.2 / m.opt.timestep)):
        mujoco.mj_step(m, d)
    m.opt.gravity[:] = [0, 0, -G0]
    b, hb = m.body("blank").id, m.body("hand").id
    rel0 = d.xmat[hb].reshape(3, 3).T @ (d.xpos[b] - d.xpos[hb])
    R0 = d.xmat[hb].reshape(3, 3).T @ d.xmat[b].reshape(3, 3)
    worst, ang = 0.0, 0.0
    t = 0.0
    while t < settle + 2 * ta + (T - 2 * ta):
        acc = a if settle <= t < settle + ta else (-a if settle + ta <= t < settle + 2 * ta else 0.0)
        d.ctrl[0] = arm * acc + mt * (G0 + acc)
        mujoco.mj_step(m, d)
        t += m.opt.timestep
        Rh = d.xmat[hb].reshape(3, 3)
        rel = Rh.T @ (d.xpos[b] - d.xpos[hb])
        worst = max(worst, float(np.linalg.norm(rel - rel0)))
        Rr = R0.T @ (Rh.T @ d.xmat[b].reshape(3, 3))
        ang = max(ang, math.degrees(math.acos(max(-1.0, min(1.0, (np.trace(Rr) - 1) / 2)))))
        if worst > 0.05:
            break
    return worst * 1000, ang


def mj_threshold(jaw, orient, a=0.0, lo=1.0, hi=600.0, tol=0.5, slip_mm=1.0):
    """二分法找 MuJoCo 中刚好不滑的夹紧力（滑移量小于 slip_mm）。"""
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if lift_test(jaw, orient, mid, a)[0] < slip_mm:
            hi = mid
        else:
            lo = mid
    return hi
