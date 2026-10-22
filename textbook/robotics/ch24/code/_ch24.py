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


# ---------------------------------------------------------------- 24.2 节：平面两连杆臂

class Planar2:
    """竖直平面内的两连杆臂（24.2 节）。φ₁ 是连杆 1 与水平线的夹角，φ₂ 是连杆 2 相对连杆 1 的转角，逆时针为正；重力沿 −Y。
    a1：两关节轴之间的距离；m_i：连杆 i 的质量；(r_i, s_i)：质心在连杆坐标系中的位置（原点在关节 i 的轴上，x 沿连杆指向下一个关节，
    y 与之垂直）；J_i：连杆 i 绕关节 i 轴的转动惯量（= 对质心的 I_i + m_i(r_i² + s_i²)）；arm：电机转子的等效惯量，加在 M 的对角上。"""

    def __init__(self, a1, m1, r1, s1, J1, m2, r2, s2, J2, arm=(0.0, 0.0), g=G0):
        self.a1, self.m1, self.r1, self.s1, self.J1 = a1, m1, r1, s1, J1
        self.m2, self.r2, self.s2, self.J2 = m2, r2, s2, J2
        self.arm = np.asarray(arm, float)
        self.g0 = g

    def beta(self, p2):
        """β(φ₂) = m₂a₁(r₂ cos φ₂ − s₂ sin φ₂)：两根连杆之间的惯性耦合。"""
        return self.m2 * self.a1 * (self.r2 * math.cos(p2) - self.s2 * math.sin(p2))

    def hh(self, p2):
        """h(φ₂) = −dβ/dφ₂ = m₂a₁(r₂ sin φ₂ + s₂ cos φ₂)。"""
        return self.m2 * self.a1 * (self.r2 * math.sin(p2) + self.s2 * math.cos(p2))

    def M(self, p):
        b = self.beta(p[1])
        return np.array([[self.J1 + self.J2 + self.m2 * self.a1 ** 2 + 2 * b + self.arm[0], self.J2 + b],
                         [self.J2 + b, self.J2 + self.arm[1]]])

    def C(self, p, pd):
        """由克里斯托费尔符号得到的 C(φ, φ̇)，c = C φ̇。"""
        h = self.hh(p[1])
        return np.array([[-h * pd[1], -h * (pd[0] + pd[1])], [h * pd[0], 0.0]])

    def c(self, p, pd):
        h = self.hh(p[1])
        return np.array([-h * (2 * pd[0] * pd[1] + pd[1] ** 2), h * pd[0] ** 2])

    def g(self, p):
        p1, p12 = p[0], p[0] + p[1]
        g2 = self.m2 * self.g0 * (self.r2 * math.cos(p12) - self.s2 * math.sin(p12))
        g1 = self.m1 * self.g0 * (self.r1 * math.cos(p1) - self.s1 * math.sin(p1)) + self.m2 * self.g0 * self.a1 * math.cos(p1) + g2
        return np.array([g1, g2])

    def U(self, p):
        p1, p12 = p[0], p[0] + p[1]
        y1 = self.r1 * math.sin(p1) + self.s1 * math.cos(p1)
        y2 = self.a1 * math.sin(p1) + self.r2 * math.sin(p12) + self.s2 * math.cos(p12)
        return self.g0 * (self.m1 * y1 + self.m2 * y2)

    def K(self, p, pd):
        return 0.5 * pd @ self.M(p) @ pd

    def E(self, p, pd):
        return self.K(p, pd) + self.U(p)

    def tau(self, p, pd, pdd):
        return self.M(p) @ pdd + self.c(p, pd) + self.g(p)

    def fd(self, p, pd, tau=(0.0, 0.0), c_fun=None):
        """正动力学 φ̈ = M⁻¹(τ − c − g)；c_fun 可换成故意写错的科氏项（24.4.3 节）。"""
        c = self.c(p, pd) if c_fun is None else c_fun(self, p, pd)
        return np.linalg.solve(self.M(p), np.asarray(tau, float) - c - self.g(p))

    def rhs(self, tau=(0.0, 0.0), c_fun=None):
        def f(x):
            return np.r_[x[2:], self.fd(x[:2], x[2:], tau, c_fun)]
        return f

    def points(self, p):
        """作图用：关节 1、关节 2、连杆 2 末端（长度取 a₂ = self.a2，若有）。"""
        a2 = getattr(self, "a2", 2 * self.r2)
        P0 = np.zeros(2)
        P1 = self.a1 * np.array([math.cos(p[0]), math.sin(p[0])])
        P2 = P1 + a2 * np.array([math.cos(p[0] + p[1]), math.sin(p[0] + p[1])])
        return np.array([P0, P1, P2])


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


# ---------------------------------------------------------------- UR5e 的关节 2、3：平面两连杆臂（24.2.6 节）

PLANAR_KEEP = ("shoulder_lift_joint", "elbow_joint")


def quat_mul(a, b):
    w1, x1, y1, z1 = a
    w2, x2, y2, z2 = b
    return np.array([w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2, w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
                     w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2, w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2])


WELD = ("shoulder_pan_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint")


NOCONTACT = '<option><flag contact="disable"/></option>'


def ur_weld_xml(angles=(0.0, -math.pi / 2, 0.0, 0.0), tool="", option=NOCONTACT, free=False):
    """锁住关节 1、4、5、6：删去它们的 <joint> 与执行器，连杆焊在父连杆上；锁住时的转角写进连杆的 quat
    （关节在连杆坐标系原点，绕关节轴转 q：quat ← quat ⊗ (cos q/2, sin q/2 · 轴)）。删去六关节的关键帧。只留关节 2、3。"""
    t = mjcf_text(tool=tool, option=option)
    links = {L.joint: L for L in parse_links(t) if L.joint}
    for name, q in zip(WELD, angles):
        L = links[name]
        ax = L.axis / np.linalg.norm(L.axis)
        qn = quat_mul(L.quat, np.r_[math.cos(q / 2), math.sin(q / 2) * ax])
        pat = re.compile(r'(<body name="%s"[^>]*?)(\s+quat="[^"]*")?(\s*/?>)' % L.name)
        mt = pat.search(t)
        assert mt is not None, L.name
        body = re.sub(r'\s+quat="[^"]*"', "", mt.group(1)) + ' quat="%s"' % " ".join(repr(float(x)) for x in qn) + mt.group(3)
        t = t[:mt.start()] + body + t[mt.end():]
        t, k = re.subn(r'\s*<joint name="%s"[^>]*/>' % name, "", t)
        assert k == 1, name
        t, k = re.subn(r'\s*<general [^>]*joint="%s"[^>]*/>' % name, "", t)
        assert k == 1, name
    t, k = re.subn(r"\s*<keyframe>.*?</keyframe>", "", t, flags=re.S)
    assert k == 1
    if free:                                             # 取消关节 2、3 的转角限位（自由下落时不碰限位）
        for name in PLANAR_KEEP:
            t, k = re.subn(r'(<joint name="%s")' % name, r'\1 limited="false"', t)
            assert k == 1
    return t


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


def planar_params(links, wrist=(-math.pi / 2, 0.0, 0.0), payload=None, arm=0.1):
    """把 UR5e 的关节 2、3 看作平面两连杆臂（关节 1 = 0，关节 4、5、6 锁在 wrist），从模型文件算出 Planar2 的参数。
    平面坐标：X 沿零位时手臂伸出的方向（基座 −x），Y 竖直向上（基座 z）。φ₁ = −θ₂，φ₂ = −θ₃（UR5e 的关节 2、3 绕 −y 转，
    正方向使手臂向下）。连杆 1 = upper_arm_link；连杆 2 = forearm_link 及其后的全部连杆（和负载）焊成一体。"""
    th = np.array([0.0, 0.0, 0.0, *wrist])
    T = link_poses(links, th)
    by = {L.name: L for L in links}
    def to_plane(p):                                     # 基座坐标 → 平面坐标 (X, Y)
        return np.array([-p[0], p[2]])
    o2 = to_plane(T["upper_arm_link"][:3, 3])            # 关节 2 的轴（零位时连杆坐标系原点在轴上）
    o3 = to_plane(T["forearm_link"][:3, 3])
    a1 = float(np.linalg.norm(o3 - o2))
    assert abs(o3[1] - o2[1]) < 1e-12                   # 零位时两关节在同一高度，连杆 1 沿 X
    n = np.array([0, -1.0, 0])                           # 关节轴方向（基座坐标系）
    def lump(names, origin_link, with_payload):
        ms, mc = 0.0, np.zeros(3)
        parts = []
        for nm in names:
            L, Ti = by[nm], T[nm]
            c = Ti[:3, :3] @ L.ipos + Ti[:3, 3]
            Ic = Ti[:3, :3] @ L.I_link_c @ Ti[:3, :3].T
            parts.append((L.m, c, Ic))
        if with_payload is not None:
            m_p, c_p, I_pc = with_payload
            Tw = T["wrist_3_link"]
            parts.append((m_p, Tw[:3, :3] @ (np.array([0, FLANGE_Y, 0]) + c_p) + Tw[:3, 3], Tw[:3, :3] @ I_pc @ Tw[:3, :3].T))
        for m_, c, _ in parts:
            ms += m_
            mc += m_ * c
        o = T[origin_link][:3, 3]
        # 绕关节轴（过 o、沿 n）的转动惯量：各部分对 o 的惯量张量投影到 n
        J = sum(n @ steiner(Ic, m_, c - o) @ n for m_, c, Ic in parts)
        cpl = to_plane(mc / ms) - to_plane(o)
        return ms, cpl, J
    m1, c1, J1 = lump(["upper_arm_link"], "upper_arm_link", None)
    rest = ["forearm_link", "wrist_1_link", "wrist_2_link", "wrist_3_link"]
    m2, c2, J2 = lump(rest, "forearm_link", payload)
    # 连杆 1 的 x 轴沿 o2 → o3（即 +X），所以 (r, s) 就是平面坐标；连杆 2 零位时也沿 +X
    P = Planar2(a1, m1, c1[0], c1[1], J1, m2, c2[0], c2[1], J2, arm=(arm, arm))
    return P


def ur_to_planar(th2, th3):
    return np.array([-th2, -th3])
