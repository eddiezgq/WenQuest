"""第 26 章共用：动力学性质与参数辨识。以下划线开头，构建时不单独运行。

前半部分是第 6、12、23～25 章的共用代码（叉积矩阵、伴随矩阵、UR5e 的旋量轴、空间惯量、书中网页版 UR5e 模型的读法、
数字工厂的毛坯与夹爪、牛顿-欧拉递推 Chain、第 22 章的上下料动作），原样抄来，使本章程序自成一体；
后半部分是本章新加的：
- 连杆的十个惯性参数 π_i 与空间惯量 𝒢_i 的互换；连杆力旋量对 π_i 的线性表示 Ψ_i（式 (26.1.3)）；
- 回归矩阵 Y(θ, θ̇, θ̈)（成批计算，式 (26.1.5)），加上转子惯量与摩擦的列；
- 基参数：对叠起来的回归矩阵做带列主元的 QR 分解，求可辨识的参数组合（26.1.4 节）；
- 有限项傅里叶级数的激励轨迹（26.2 节）；
- 在 MuJoCo 里“做实验”：带摩擦的 UR5e 跟踪激励轨迹，记录关节角和电机力矩（26.3 节）；
- 零相位低通滤波与数值微分。
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


# ================================================================ 第 26 章：动力学性质与参数辨识

PNAMES = ["m", "mc_x", "mc_y", "mc_z", "I_xx", "I_xy", "I_xz", "I_yy", "I_yz", "I_zz"]   # 连杆的十个惯性参数（26.1.2 节）


def G_from_pi(p):
    """π_i = (m, m c, I_xx, I_xy, I_xz, I_yy, I_yz, I_zz)（I 是对连杆坐标系原点的惯量）→ 𝒢_i（式 (23.3.15)）。对 π_i 是线性的。"""
    m, mc = p[0], np.asarray(p[1:4])
    Ixx, Ixy, Ixz, Iyy, Iyz, Izz = p[4:10]
    G = np.zeros((6, 6))
    G[:3, :3] = [[Ixx, Ixy, Ixz], [Ixy, Iyy, Iyz], [Ixz, Iyz, Izz]]
    P = skew(mc)
    G[:3, 3:] = P
    G[3:, :3] = -P
    G[3:, 3:] = m * np.eye(3)
    return G


def pi_from_G(G):
    I = G[:3, :3]
    return np.array([G[3, 3], G[2, 4], G[0, 5], G[1, 3], I[0, 0], I[0, 1], I[0, 2], I[1, 1], I[1, 2], I[2, 2]])


GBASIS = [G_from_pi(np.eye(10)[k]) for k in range(10)]


def chain_pi(ch):
    """Chain 的全部连杆参数排成 10n 维矢量（负载已并入最后一个连杆）。"""
    return np.concatenate([pi_from_G(G) for G in ch.G])


def link_regressor(V, Vd):
    """Ψ(𝒱, 𝒱̇)：连杆的合力旋量 𝒢𝒱̇ − [ad_𝒱]ᵀ𝒢𝒱 = Ψ π_i（式 (26.1.3)），6×10。"""
    adT = ad(V).T
    return np.column_stack([Gk @ Vd - adT @ (Gk @ V) for Gk in GBASIS])


def regressor(ch, q, qd, qdd, Vd0=GRAV):
    """连杆部分的回归矩阵 Y_L（n × 10n）：τ（不含转子、摩擦）= Y_L π（式 (26.1.5)）。前向递推一次，再把每个连杆的 Ψ 向里传。"""
    n = ch.n
    Ts, Vs, Vds = ch.forward(q, qd, qdd, Vd0)
    Ads = [adjoint(T) for T in Ts]
    Y = np.zeros((n, 10 * n))
    for i in range(n):
        X = link_regressor(Vs[i], Vds[i])
        for j in range(i, -1, -1):
            Y[j, 10 * i:10 * i + 10] = ch.A[j] @ X
            if j > 0:
                X = Ads[j].T @ X                         # 换到 {j − 1}：ℱ_(j−1) = [Ad_{T_{j,j−1}}]ᵀ ℱ_(j)
    return Y


def full_regressor(ch, q, qd, qdd, Vd0=GRAV):
    """加上转子惯量 J_r,i（列 θ̈_i）、库仑摩擦 f_c,i（列 sign θ̇_i）、黏性摩擦 f_v,i（列 θ̇_i）：n × 13n。"""
    n = ch.n
    return np.hstack([regressor(ch, q, qd, qdd, Vd0), np.diag(qdd), np.diag(np.sign(qd)), np.diag(qd)])


def full_pi(ch, fc, fv):
    return np.concatenate([chain_pi(ch), ch.arm, fc, fv])


def full_names(n):
    nm = [f"{p}^{i + 1}" for i in range(n) for p in PNAMES]
    return nm + [f"J_r{i + 1}" for i in range(n)] + [f"f_c{i + 1}" for i in range(n)] + [f"f_v{i + 1}" for i in range(n)]


def base_parameters(W, tol=None):
    """基参数（26.1.4 节）：W 是许多随机状态的回归矩阵叠成的矩阵。带列主元的 QR 分解 W P = Q R，
    rank r；前 r 个主元列独立，其余列 = 独立列 × K，K = R₁₁⁻¹R₁₂。基参数 π_b = π_独立 + K π_相关。
    返回 (独立列, 相关列, K, r)；完全为零的列（不可辨识的参数）也在相关列里，对应 K 的列为零。"""
    import scipy.linalg as sla
    Q, R, P = sla.qr(W, mode="economic", pivoting=True)
    d = np.abs(np.diag(R))
    if tol is None:
        tol = d[0] * max(W.shape) * 1e-12
    r = int(np.sum(d > tol))
    ind, dep = P[:r], P[r:]
    K = np.linalg.solve(R[:r, :r], R[:r, r:])
    return ind, dep, K, r


def base_from_full(pi, ind, dep, K):
    return pi[ind] + K @ pi[dep]


# ---------------------------------------------------------------- 26.2 节：有限项傅里叶级数的激励轨迹

class Fourier:
    """θ_i(t) = θ_i0 + Σ_l [a_il/(ω_f l) sin(ω_f l t) − b_il/(ω_f l) cos(ω_f l t)]（式 (26.2.1)），周期 T_f = 2π/ω_f。
    a、b 为 n × L。速度 θ̇_i = Σ_l [a_il cos + b_il sin]，周期的首尾自然衔接。"""

    def __init__(self, q0, a, b, Tf):
        self.q0, self.a, self.b, self.wf = np.asarray(q0, float), np.asarray(a, float), np.asarray(b, float), 2 * math.pi / Tf
        self.Tf = Tf

    def eval(self, t):
        t = np.atleast_1d(np.asarray(t, float))
        L = self.a.shape[1]
        l = np.arange(1, L + 1)
        wl = self.wf * l                                   # L
        S, C = np.sin(np.outer(t, wl)), np.cos(np.outer(t, wl))   # N × L
        q = self.q0 + S @ (self.a / wl).T - C @ (self.b / wl).T
        qd = C @ self.a.T + S @ self.b.T
        qdd = -S @ (self.a * wl).T + C @ (self.b * wl).T
        return q, qd, qdd


def stack_regressor(ch, q, qd, qdd, full=True):
    f = full_regressor if full else regressor
    return np.vstack([f(ch, q[k], qd[k], qdd[k]) for k in range(len(q))])


# ---------------------------------------------------------------- 26.3 节：在 MuJoCo 里做辨识实验

FC_TRUE = np.array([2.0, 2.0, 1.5, 0.6, 0.6, 0.5])        # 库仑摩擦，N·m（示意值，26.4 节）
FV_TRUE = np.array([1.5, 1.5, 1.0, 0.3, 0.3, 0.3])        # 黏性摩擦，N·m·s/rad（示意值）
SIGMA_TAU = np.array([0.4, 0.4, 0.3, 0.08, 0.08, 0.08])    # 电机力矩（由电流换算）的测量噪声，N·m（示意值）
SIGMA_Q = 2e-5                                             # 关节角的测量噪声，rad（示意值）
KP = np.array([2000, 2000, 2000, 400, 400, 400.0])         # 位置反馈增益（与模型执行器同量级）
KD = np.array([400, 400, 400, 80, 80, 80.0])


def friction_mjcf(fc=FC_TRUE, fv=FV_TRUE, payload=None, dt=0.001):
    """“真实”的 UR5e：书中模型加上关节摩擦（MuJoCo 的 frictionloss 为干摩擦，damping 为黏性摩擦），关掉执行器，
    力矩由程序直接加在关节上（qfrc_applied）。"""
    tool = payload_xml(*payload) if payload is not None else ""
    t = mjcf_text(tool=tool, option=f'<option timestep="{dt!r}" integrator="RK4"><flag contact="disable" actuation="disable"/></option>')
    names = ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"]
    for nm, c, v in zip(names, fc, fv):
        t, k = re.subn(rf'<joint name="{nm}"', f'<joint name="{nm}" frictionloss="{float(c)!r}" damping="{float(v)!r}"', t)
        assert k == 1
    return t


def run_experiment(traj, T, payload=None, fc=FC_TRUE, fv=FV_TRUE, dt=0.001, every=2, seed=0, model=None):
    """MuJoCo 中带摩擦的 UR5e 跟踪轨迹：τ = RNEA_名义(θ_d) + K_p(θ_d − θ) + K_d(θ̇_d − θ̇)，名义模型不知道摩擦。
    每 every 步（500 Hz）记录一次实际关节角和施加的力矩，再加上测量噪声。返回 t, θ_meas, τ_meas, θ_true, τ_true。"""
    import mujoco
    mj_m = mujoco.MjModel.from_xml_string(friction_mjcf(fc, fv, payload, dt))
    d = mujoco.MjData(mj_m)
    mj_m.jnt_limited[:] = 0
    nom = model if model is not None else ur_chain(payload=payload)
    q0, qd0, _ = traj(0.0)
    d.qpos[:], d.qvel[:] = q0, qd0
    N = int(round(T / dt))
    ts, Q, TAU = [], [], []
    for k in range(N):
        t = k * dt
        qd_, qdd_d, qddd = traj(t)
        tau = nom.rnea(qd_, qdd_d, qddd) + KP * (qd_ - d.qpos) + KD * (qdd_d - d.qvel)
        if k % every == 0:
            ts.append(t)
            Q.append(d.qpos.copy())
            TAU.append(tau.copy())
        d.qfrc_applied[:] = tau
        mujoco.mj_step(mj_m, d)
    ts, Q, TAU = np.array(ts), np.array(Q), np.array(TAU)
    rng = np.random.default_rng(seed)
    Qm = Q + rng.normal(0, SIGMA_Q, Q.shape)
    TAUm = TAU + rng.normal(0, 1, TAU.shape) * SIGMA_TAU
    return ts, Qm, TAUm, Q, TAU


def lowpass_derivatives(t, Q, TAU, fc_hz=8.0):
    """零相位低通（四阶巴特沃斯，前后各滤一次）后用中心差分求 θ̇、θ̈；力矩用同一个滤波器（26.3.3 节）。去掉两端各 0.5 s。"""
    from scipy.signal import butter, filtfilt
    dt = t[1] - t[0]
    b, a = butter(4, fc_hz * 2 * dt)
    Qf = filtfilt(b, a, Q, axis=0)
    TAUf = filtfilt(b, a, TAU, axis=0)
    Qd = np.gradient(Qf, dt, axis=0)
    Qdd = np.gradient(Qd, dt, axis=0)
    k0 = int(round(0.5 / dt))
    sl = slice(k0, len(t) - k0)
    return t[sl], Qf[sl], Qd[sl], Qdd[sl], TAUf[sl]


def ur_base_set(n_samples=300, seed=261):
    """书中 UR5e（含转子惯量、库仑和黏性摩擦，共 13n 个参数）的基参数：随机状态叠起来求（26.1.4 节）。"""
    ch = ur_chain()
    rng = np.random.default_rng(seed)
    W = np.vstack([full_regressor(ch, *rng.uniform(-3, 3, (3, 6))) for _ in range(n_samples)])
    return (W,) + base_parameters(W)


def Mdot_qd(ch, q, qd, eps=1e-6):
    """Ṁθ̇ = (dM/dt)θ̇，沿 θ̇ 方向的中心差分。"""
    Mp = ch.closed_form(q + eps * qd, qd)[0]
    Mm = ch.closed_form(q - eps * qd, qd)[0]
    return (Mp - Mm) / (2 * eps) @ qd


# 26.2 节优化得到的激励轨迹（程序 26.2.1 的结果，写在这里供 26.3、26.4 节和实验使用；程序 26.2.1 每次构建都重算并核对）
EXC_Q0 = np.radians([0.0, -90.0, 90.0, -90.0, -90.0, 0.0])
EXC_TF = 10.0
EXC_L = 5
EXC_VMAX = np.full(6, 1.5)                                  # 激励时的速度上限，rad/s（低于 UR5e 的 π rad/s）
EXC_AMAX = np.array([4.0, 4.0, 4.0, 8.0, 8.0, 8.0])         # 加速度上限，rad/s²（示意值）
EXC_RANGE = np.radians([90.0, 50.0, 40.0, 90.0, 90.0, 90.0])   # 偏离 θ₀ 的上限
EXC_ZMIN = 0.15                                             # 各关节原点和 TCP 离地面的最小高度，m


def lowest_point(ch, q):
    T = np.eye(4)
    zs = []
    for i in range(ch.n):
        T = T @ inv(ch.T_rel(i, q[i]))
        zs.append(T[2, 3])
    zs.append((T @ ch.Mf @ np.array([0, TCP, 0, 1.0]))[2])
    return min(zs)


def exc_violation(ch, tr, ts):
    """激励轨迹违反限制的程度（0 表示满足）：转角范围、速度、加速度、离地高度。"""
    q, qd, qdd = tr.eval(ts)
    v = np.sum(np.maximum(np.abs(q - tr.q0) - EXC_RANGE, 0) ** 2) + np.sum(np.maximum(np.abs(qd) - EXC_VMAX, 0) ** 2)
    v += 0.1 * np.sum(np.maximum(np.abs(qdd) - EXC_AMAX, 0) ** 2)
    zmin = min(lowest_point(ch, x) for x in q[::3])
    return v + 100 * max(EXC_ZMIN - zmin, 0) ** 2
EXC_A = np.array([[-0.797811,  0.134195, -0.033239, -0.21617 , -0.281421],
                  [-0.098781, -0.138661, -0.297528,  0.202307, -0.644069],
                  [ 0.06109 ,  0.162527,  0.243568, -0.441413,  0.00809 ],
                  [-0.582489,  0.198841,  0.423006,  0.135481, -0.099577],
                  [ 0.171012,  0.260319,  0.144237, -0.004926, -0.238638],
                  [-0.757907, -0.086944, -0.351509,  0.357326,  0.44112 ]])
EXC_B = np.array([[-0.304145, -0.19026 , -0.375126, -0.255614,  0.387034],
                  [-0.057374,  0.252901, -0.052444,  0.282505,  0.201235],
                  [ 0.269002,  0.156995, -0.013454, -0.225422,  0.29934 ],
                  [ 0.320599,  0.201782, -0.245445,  0.15699 , -0.134112],
                  [ 0.249801,  0.600106,  0.082994,  0.257953, -0.270796],
                  [ 0.062983,  0.077135, -0.195247,  0.18391 , -0.038834]])


def exc_experiment(payload=None, seed=263, periods=2, dec=5):
    """26.3 节的辨识实验：带摩擦（和负载）的“真实”UR5e 在 MuJoCo 中跟踪激励轨迹，控制器用不带负载、摩擦的名义模型。
    返回滤波、求导、每 dec 个取一个之后的 θ、θ̇、θ̈、τ，全部 78 列的回归矩阵 W（按名义的连杆几何算），以及原始记录。"""
    tr = Fourier(EXC_Q0, EXC_A, EXC_B, EXC_TF)

    def traj(t):
        q, qd, qdd = tr.eval(t)
        return q[0], qd[0], qdd[0]
    nom = ur_chain()
    ts, Qm, TAUm, Q, TAU = run_experiment(traj, periods * EXC_TF, payload=payload, model=nom, seed=seed)
    t1, Qf, Qd, Qdd, TAUf = lowpass_derivatives(ts, Qm, TAUm)
    Qf, Qd, Qdd, TAUf = Qf[::dec], Qd[::dec], Qdd[::dec], TAUf[::dec]
    W = np.vstack([full_regressor(nom, Qf[k], Qd[k], Qdd[k]) for k in range(len(Qf))])
    track = float(np.abs(Q - tr.eval(ts)[0]).max())
    return dict(ts=ts, Q=Q, TAU=TAU, Qf=Qf, Qd=Qd, Qdd=Qdd, TAUf=TAUf, W=W, y=TAUf.reshape(-1), track=track, n_raw=len(ts))


def collision_demo(KO=50.0, F_EXT=40.0, T0C=0.70, T1C=0.80):
    """算例 26.1.1：UR5e（带夹爪 + 毛坯）走第 22 章的上下料动作，T0C～T1C 秒在 TCP 处加水平力 F_EXT（模拟撞到人）。
    记录 θ、θ̇、τ 与真实的 Jᵀℱ_ext，再用广义动量观测器（式 (26.1.2)）离线算残差：模型带负载一次，不带负载一次。"""
    thA, thB, T_move = cell_move()
    pl = payload_parts()
    chp = ur_chain(payload=pl)
    DT = 0.001
    xml = mjcf_text(tool=payload_xml(*pl), option=f'<option timestep="{DT!r}" integrator="RK4"><flag contact="disable" actuation="disable"/></option>')
    mjp, mp, dp = mj_load(xml)
    mp.jnt_limited[:] = 0
    bid = mp.body("wrist_3_link").id
    dp.qpos[:] = thA
    N = int(round(T_move / DT))
    QH, VH, TH, EH, t_hist = [], [], [], [], []
    f_world = np.array([F_EXT, 0, 0])
    for k in range(N + 200):
        t = k * DT
        qd_, qdd_d, qddd = quintic(thA, thB, T_move, t)
        q, v = dp.qpos.copy(), dp.qvel.copy()
        tau = chp.rnea(qd_, qdd_d, qddd) + KP * (qd_ - q) + KD * (qdd_d - v)
        # 外力：加在 TCP（连杆 6 坐标系中 (0, 0.25, 0)）
        T06 = chp.flange_pose(q) @ inv(chp.Mf)
        p_tcp = T06[:3, :3] @ np.array([0, 0.1 + TCP, 0]) + T06[:3, 3]
        hit = T0C <= t < T1C
        dp.xfrc_applied[:] = 0
        if hit:
            dp.xfrc_applied[bid, :3] = f_world
            dp.xfrc_applied[bid, 3:] = np.cross(p_tcp - dp.xipos[bid], f_world)      # xfrc_applied 作用在连杆质心
        Jtcp = np.zeros((3, 6))                          # 真实的外力矩 Jᵀℱ（TCP 处的力）
        mjp.mj_jac(mp, dp, Jtcp, None, p_tcp, bid)
        QH.append(q), VH.append(v), TH.append(tau.copy()), EH.append(Jtcp.T @ f_world if hit else np.zeros(6)), t_hist.append(t)
        dp.qfrc_applied[:] = tau
        mjp.mj_step(mp, dp)
    QH, VH, TH, E_hist, t_hist = map(np.array, (QH, VH, TH, EH, t_hist))

    def observer(model):
        """ṗ = τ + Cᵀθ̇ − g + τ_ext，Cᵀθ̇ = Ṁθ̇ − Cθ̇（Ṁ = C + Cᵀ，定理 24.3.3）；r = K_O(p − p(0) − ∫(τ + Cᵀθ̇ − g + r)dt)。"""
        integ, p0, R = np.zeros(6), None, []
        for q, v, tau in zip(QH, VH, TH):
            M, c, g = model.closed_form(q, v)
            pmom = M @ v
            if p0 is None:
                p0 = pmom.copy()
            beta = g - (Mdot_qd(model, q, v) - c)
            r = KO * (pmom - p0 - integ)
            integ = integ + (tau - beta + r) * DT
            R.append(r)
        return np.array(R)

    R_hist = observer(chp)
    R_nom = observer(ur_chain())                       # 模型里没有夹爪和毛坯
    return t_hist, R_hist, R_nom, E_hist
