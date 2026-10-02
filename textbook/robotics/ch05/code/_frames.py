"""第 5 章共用：旋转矩阵、齐次变换、坐标系树、UR5e 工作站，以及读取零件库 UR5e 模型。以下划线开头，构建时不单独运行。

全书约定（符号约定.md）：T_ab 是 {b} 相对 {a} 的位姿，T_ab = [[R_ab, p_ab], [0, 1]]；
p_ab 是 {b} 的原点相对 {a} 原点的位置矢量在 {a} 中的分量。角度一律用弧度。
"""
import json
import math
import struct
from pathlib import Path

import numpy as np

MODELS = Path(__file__).resolve().parents[2] / "models"


# ---------------------------------------------------------------- 转动（第 4 章）

def rot_x(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], float)


def rot_y(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], float)


def rot_z(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], float)


def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]], float)


def rot_axis(w, t):
    """罗德里格斯公式，式 (4.4.5)。"""
    w = np.asarray(w, float) / np.linalg.norm(w)
    K = skew(w)
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def log_rot(R):
    """对数映射（4.4 节）：返回指数坐标 ω̂θ（转动矢量），0 ≤ θ ≤ π。"""
    a = np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / 2     # sin θ · ω̂
    th = math.atan2(np.linalg.norm(a), (np.trace(R) - 1) / 2)                          # 小角度时比 arccos 准确
    if th < 1e-15:
        return np.zeros(3)
    if math.pi - th < 1e-6:
        B = (R + np.eye(3)) / 2
        k = int(np.argmax(np.diag(B)))
        w = B[:, k] / math.sqrt(B[k, k])
        return w * th
    return a / np.linalg.norm(a) * th


def rpy_matrix(rpy):
    """URDF 的 rpy：先绕固定轴 x 转 r，再绕固定轴 y 转 p，再绕固定轴 z 转 y，即 Rz·Ry·Rx（4.5 节）。"""
    r, p, y = rpy
    return rot_z(y) @ rot_y(p) @ rot_x(r)


# ---------------------------------------------------------------- 齐次变换（5.2、5.3 节）

def T(R=None, p=(0, 0, 0)):
    """由 R、p 组成 4×4 齐次矩阵，式 (5.2.3)。"""
    M = np.eye(4)
    if R is not None:
        M[:3, :3] = R
    M[:3, 3] = p
    return M


def trans(x, y, z):
    return T(None, (x, y, z))


def inv(Tm):
    """求逆公式 T⁻¹ = [[Rᵀ, −Rᵀp], [0, 1]]，定理 5.3.2。"""
    R, p = Tm[:3, :3], Tm[:3, 3]
    return T(R.T, -R.T @ p)


def is_se3(Tm, tol=1e-9):
    R = Tm[:3, :3]
    return (np.allclose(R.T @ R, np.eye(3), atol=tol) and abs(np.linalg.det(R) - 1) < tol
            and np.allclose(Tm[3], [0, 0, 0, 1], atol=tol))


def hom(p):
    """点的齐次坐标 (p, 1)。"""
    return np.r_[np.asarray(p, float), 1.0]


def hdir(v):
    """自由矢量的齐次坐标 (v, 0)。"""
    return np.r_[np.asarray(v, float), 0.0]


def clean(x, tol=1e-12):
    """把 1e-17 这类舍入残差记为 0，便于印在书上。"""
    x = np.array(x, float)
    x[np.abs(x) < tol] = 0.0
    return x


# ---------------------------------------------------------------- 坐标系树（5.4 节）

class FrameTree:
    """坐标系树：每个坐标系只记一个父坐标系和 T_父,子。任意两个坐标系之间的位姿沿树中唯一的路径相乘。"""

    def __init__(self, root):
        self.root = root
        self.parent = {root: None}
        self.edge = {}                       # child -> T_parent,child

    def add(self, child, parent, T_pc):
        assert parent in self.parent, f"父坐标系 {parent} 不在树中"
        assert child not in self.parent, f"{child} 已有父坐标系（树中每个坐标系只能有一个父坐标系）"
        self.parent[child] = parent
        self.edge[child] = np.array(T_pc, float)

    def set(self, child, T_pc):
        self.edge[child] = np.array(T_pc, float)

    def chain_to_root(self, f):
        out = [f]
        while self.parent[out[-1]] is not None:
            out.append(self.parent[out[-1]])
        return out

    def path(self, a, b):
        """从 a 到 b 的唯一路径：先向上走到最近公共祖先，再向下走到 b。返回 [(from, to, 'up'|'down'), ...]。"""
        ua, ub = self.chain_to_root(a), self.chain_to_root(b)
        common = next(x for x in ua if x in ub)
        steps = []
        for x in ua[:ua.index(common)]:
            steps.append((x, self.parent[x], "up"))
        down = ub[:ub.index(common)]
        for x in reversed(down):
            steps.append((self.parent[x], x, "down"))
        return steps

    def T(self, a, b):
        """T_ab：沿路径相乘；向下走一步乘 T_父,子，向上走一步乘它的逆（下标相消规则，定理 5.3.1）。"""
        M = np.eye(4)
        for x, y, d in self.path(a, b):
            M = M @ (self.edge[y] if d == "down" else inv(self.edge[x]))
        return M

    def T_root(self, f):
        """T_root,f：从根往下乘到 f。"""
        M = np.eye(4)
        for x in reversed(self.chain_to_root(f)[:-1]):
            M = M @ self.edge[x]
        return M


# ---------------------------------------------------------------- 零件库 UR5e 模型

UR_JOINTS = ["shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", "wrist_1_joint", "wrist_2_joint", "wrist_3_joint"]
UR_LINKS = ["shoulder_link", "upper_arm_link", "forearm_link", "wrist_1_link", "wrist_2_link", "wrist_3_link"]
FLANGE_XYZ = (0.0, 0.1, 0.0)       # 法兰盘中心在 wrist_3_link 坐标系中的位置（第 12 章：W4 = 0.1 m）


def ur_entry():
    return json.loads((MODELS / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))


def glb_nodes(eid="B-ARM-UR5E"):
    b = (MODELS / eid / "default.glb").read_bytes()
    n = struct.unpack("<I", b[12:16])[0]
    js = json.loads(b[20:20 + n])
    out = {}
    for nd in js["nodes"]:
        m = np.array(nd.get("matrix", np.eye(4).T.ravel()), float).reshape(4, 4).T     # glTF 按列存
        out[nd["name"]] = m
    return out


def ur_edges_from_table(theta):
    """做法一：由模型关节表（entry.json）逐个写出 T_父,子(θ) = Trans(xyz)·Rot_rpy·Rot(axis, θ)。
    基座连杆 base 相对 {s} 绕 z 转 180°（模型文件中 base 的姿态），不在关节表中，单独给出。"""
    js = {j["name"]: j for j in ur_entry()["robot"]["joints"]}
    edges = [("base", "s", T(rot_z(math.pi)))]
    parent = "base"
    for name, link, t in zip(UR_JOINTS, UR_LINKS, theta):
        j = js[name]
        o = j["origin"]
        Tm = trans(*o["xyz"]) @ T(rpy_matrix(o["rpy"])) @ T(rot_axis(j["axis"], t))
        edges.append((link, parent, Tm))
        parent = link
    edges.append(("b", "wrist_3_link", trans(*FLANGE_XYZ)))
    return edges


def ur_fk_table(theta):
    M = np.eye(4)
    for _, _, Tm in ur_edges_from_table(theta):
        M = M @ Tm
    return M


def ur_fk_glb(theta):
    """做法二：按三维引擎的做法，用网页模型（default.glb）的节点矩阵乘以绕关节轴的转动。"""
    nodes = glb_nodes()
    js = {j["name"]: j for j in ur_entry()["robot"]["joints"]}
    M = nodes["base"].copy()
    for name, link, t in zip(UR_JOINTS, UR_LINKS, theta):
        M = M @ nodes[link] @ T(rot_axis(js[name]["axis"], t))
    return M @ trans(*FLANGE_XYZ)


# 第 12 章的指数积公式（表 12.1.1 的旋量轴与零位位姿 M），作为第三种独立算法
_H1, _W1, _L1, _W2, _L2, _W3, _H2, _W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1


def _screws():
    yd = np.array([0, -1.0, 0])
    tab = [(np.array([0, 0, 1.0]), np.array([0, 0, _H1])),
           (yd, np.array([0, -_W1, _H1])),
           (yd, np.array([-_L1, -_W1 + _W2, _H1])),
           (yd, np.array([-_L1 - _L2, -_W1 + _W2, _H1])),
           (np.array([0, 0, -1.0]), np.array([-_L1 - _L2, -_W1 + _W2 - _W3, _H1])),
           (yd, np.array([-_L1 - _L2, -_W1 + _W2 - _W3, _H1 - _H2]))]
    return [(w, -np.cross(w, q)) for w, q in tab]


UR_M = np.array([[1.0, 0, 0, -_L1 - _L2], [0, -1, 0, -_W1 + _W2 - _W3 - _W4], [0, 0, -1, _H1 - _H2], [0, 0, 0, 1]])


def _exp6(w, v, t):
    K = skew(w)
    G = np.eye(3) * t + (1 - math.cos(t)) * K + (t - math.sin(t)) * K @ K
    return T(rot_axis(w, t), G @ v)


def ur_fk_poe(theta):
    """做法三：指数积公式 T = e^{[S1]θ1} ⋯ e^{[S6]θ6} M（式 (12.2.3)）。"""
    M = np.eye(4)
    for (w, v), t in zip(_screws(), theta):
        M = M @ _exp6(w, v, t)
    return M @ UR_M


def ur_ik(T_goal, seed, iters=100):
    """数值逆运动学（第 15 章）：阻尼牛顿迭代，误差为空间中的转动矢量与位置差。"""
    th = np.array(seed, float)
    for _ in range(iters):
        Tc = ur_fk_poe(th)
        e = np.r_[log_rot(T_goal[:3, :3] @ Tc[:3, :3].T), T_goal[:3, 3] - Tc[:3, 3]]
        if np.linalg.norm(e) < 1e-14:
            break
        J = np.zeros((6, 6))
        h = 1e-7
        for i in range(6):
            d = th.copy()
            d[i] += h
            Td = ur_fk_poe(d)
            J[:, i] = np.r_[log_rot(Td[:3, :3] @ Tc[:3, :3].T), Td[:3, 3] - Tc[:3, 3]] / h
        th = th + np.linalg.solve(J.T @ J + 1e-12 * np.eye(6), J.T @ e)
    return th


# ---------------------------------------------------------------- 5.5 节的工作站（单位 m、rad）

DEG = math.pi / 180
TABLE = (1.2, 0.8)                                   # 工作台台面 1.2 m × 0.8 m，{w} 在左前角
P_WS, YAW_WS = np.array([0.30, 0.40, 0.0]), math.pi  # 机器人基座：台面上 (0.30, 0.40)，绕 z 转 180°
P_WC = np.array([1.05, 0.40, 0.90])                  # 相机：支架上，高出台面 0.90 m
TILT_C = 15 * DEG                                    # 光轴偏离竖直方向 15°，朝机器人一侧
GRIP_L = 0.15                                        # 夹爪：指尖中心距法兰盘面 0.15 m
PART_H = 0.03                                        # 齿轮坯厚 30 mm，夹取高度在一半处


def T_ws():
    return T(rot_z(YAW_WS), P_WS)


def R_wc():
    """相机朝下：x_c 沿 y_w，y_c 沿 x_w，z_c（光轴）沿 −z_w；再绕自身 x_c 转 15°，光轴偏向机器人一侧。"""
    R0 = np.array([[0, 1, 0], [1, 0, 0], [0, 0, -1]], float)
    return R0 @ rot_x(TILT_C)


def T_wc():
    return T(R_wc(), P_WC)


def T_bt():
    """工具坐标系 {t}：原点在指尖中心；z_t 沿法兰盘法线（= y_b）向外，x_t = x_b。"""
    return T(rot_x(-math.pi / 2), (0, GRIP_L, 0))


def T_og():
    """抓取坐标系 {g}：在工件中心轴上、厚度的一半处；z_g 竖直向下（夹爪接近方向）。"""
    return T(rot_x(math.pi), (0, 0, PART_H / 2))


def texm(M, digits=4):
    """矩阵写成 LaTeX；与 bookout.tex 相同，但去掉小数末尾多余的 0（1.0500 写成 1.05）。"""
    from bookout import num
    A = np.atleast_2d(np.asarray(M, dtype=float))
    if A.shape[0] == 1 and np.asarray(M).ndim == 1:
        A = A.T

    def f(v):
        s = num(v, digits)
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        return "0" if s in ("-0", "") else s
    rows = [" & ".join(f(v) for v in row) for row in A]
    return "\\begin{pmatrix} " + r" \\ ".join(rows) + " \\end{pmatrix}"


def vecm(v, digits=4):
    """列向量写在一行：(a, b, c)ᵀ，去掉末尾多余的 0。"""
    from bookout import num

    def f(x):
        s = num(float(x), digits)
        if "." in s:
            s = s.rstrip("0").rstrip(".")
        return "0" if s in ("-0", "") else s
    return "(" + ",\\ ".join(f(x) for x in v) + ")^{\\mathsf T}"
