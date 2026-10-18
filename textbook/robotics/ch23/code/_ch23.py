"""第 23 章共用：刚体动力学基础。以下划线开头，构建时不单独运行。

前半部分是第 6、12 章的共用代码（叉积矩阵、罗德里格斯公式、矩阵指数、伴随矩阵、李括号矩阵、UR5e 的旋量轴（表 12.1.1）），
原样抄来，使本章程序自成一体；后半部分是本章新加的：
- 常见形体的质量与惯量（式 (23.1.11)～(23.1.14)）、平行轴定理（式 (23.2.3)）、空间惯量 G（式 (23.3.10)、(23.3.13)、(23.3.15)）；
- 自由刚体的欧拉方程与四阶龙格-库塔积分（本章自己写，用来与 MuJoCo 互相核对）；
- 书中网页版 UR5e 模型（textbook/robotics/models/mjcf/ur5e.xml）的读法：只用 Python 标准库的 XML 解析，
  不经过 MuJoCo，自己算出各连杆的位姿、惯量，再与 MuJoCo 的结果逐项比较；
- 数字工厂的工件：输出轴 SH-301 的毛坯（factory/factory/data.py 的物料清单），以及本章各算例的示意值。
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


# ---------------------------------------------------------------- 自由刚体：欧拉方程与 RK4（与 MuJoCo 互相核对）

def euler_rhs(Ivec, w):
    """无外力矩的欧拉方程（主轴坐标系）：I ω̇ = (I ω) × ω。"""
    I = np.asarray(Ivec, float)
    return np.cross(I * w, w) / I


def free_spin(Ivec, w0, T, dt=1e-3):
    """四阶龙格-库塔积分欧拉方程，返回 (t, ω(t))。只积分角速度（物体坐标系中的分量）。"""
    n = int(round(T / dt))
    W = np.zeros((n + 1, 3))
    W[0] = w0
    w = np.array(w0, float)
    for k in range(n):
        k1 = euler_rhs(Ivec, w)
        k2 = euler_rhs(Ivec, w + 0.5 * dt * k1)
        k3 = euler_rhs(Ivec, w + 0.5 * dt * k2)
        k4 = euler_rhs(Ivec, w + dt * k3)
        w = w + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        W[k + 1] = w
    return np.arange(n + 1) * dt, W


def sign_changes(t, x):
    """x(t) 变号的时刻（线性插值）。"""
    s = np.sign(x)
    idx = np.where(s[1:] * s[:-1] < 0)[0]
    return np.array([t[i] - x[i] * (t[i + 1] - t[i]) / (x[i + 1] - x[i]) for i in idx])


# ---------------------------------------------------------------- 书中的网页版 UR5e 模型（MJCF）

PLACEHOLDERS = re.compile(r"<!--(OPTION|WORLD|TOOL|ACTUATOR)-->")


def mjcf_text(name="ur5e", tool="", world="", option="", actuator=""):
    """模型文本，四个占位注释换成给定的片段（不给就换成空），与实验框架 api.mjcf 相同。"""
    t = (MJCF_DIR / f"{name}.xml").read_text(encoding="utf-8")
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
