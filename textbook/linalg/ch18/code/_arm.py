"""第 18 章共用：读取零件库机器人模型（关节表），计算正运动学与雅可比矩阵。以下划线开头，构建时不单独运行。

模型取自 textbook/linalg/models/（零件库 2026.10.9 版，见 models/来源.md）。关节表中每个关节给出：
父连杆、子连杆、子连杆坐标系相对父连杆的位置 xyz 与姿态 rpy、子连杆坐标系中的转轴 axis。
子连杆位姿 = 父连杆位姿 · Trans(xyz) · Rot_rpy · Rot(axis, θ)，与网页三维实验的引擎做法相同。

雅可比矩阵按“末端点”写成 6×n：前三行是末端的角速度 ω，后三行是末端点 p 的线速度 v，
第 i 列为 (z_i, z_i × (p − q_i))，z_i 是第 i 个关节的转轴方向，q_i 是轴上一点（都在基座坐标系中）。
"""
import json
import math
from pathlib import Path

import numpy as np

MODELS = Path(__file__).resolve().parents[2] / "models"


def _rpy(r, p, y):
    cr, sr, cp, sp, cy, sy = math.cos(r), math.sin(r), math.cos(p), math.sin(p), math.cos(y), math.sin(y)
    Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
    Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def _axis_rot(a, t):
    a = np.asarray(a, float) / np.linalg.norm(a)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


class Arm:
    """一台串联机械臂：从基座连杆到末端连杆的转动关节链；末端点在末端连杆坐标系中的位置为 tool_xyz。"""

    def __init__(self, eid: str, tool_link: str, tool_xyz=(0.0, 0.0, 0.0)):
        self.entry = json.loads((MODELS / eid / "entry.json").read_text(encoding="utf-8"))
        js = self.entry["robot"]["joints"]
        by_child = {j["child"]: j for j in js}
        chain, n = [], tool_link
        while n in by_child:
            chain.insert(0, by_child[n])
            n = by_child[n]["parent"]
        self.joints = [j for j in chain if j["type"] == "revolute"]
        self.names = [j["name"] for j in self.joints]
        self.tool_xyz = np.asarray(tool_xyz, float)
        self.version = self.entry.get("version", "")

    def frames(self, q):
        """每个关节转动之前的子连杆坐标系（用来读转轴），以及末端连杆坐标系。"""
        T = np.eye(4)
        axes = []
        for j, t in zip(self.joints, q):
            O = np.eye(4)
            O[:3, :3] = _rpy(*j["origin"]["rpy"])
            O[:3, 3] = j["origin"]["xyz"]
            T = T @ O
            a = np.asarray(j["axis"], float)
            axes.append((T[:3, :3] @ (a / np.linalg.norm(a)), T[:3, 3].copy()))
            M = np.eye(4)
            M[:3, :3] = _axis_rot(a, t)
            T = T @ M
        return axes, T

    def tool(self, q):
        _, T = self.frames(q)
        return T[:3, :3] @ self.tool_xyz + T[:3, 3]

    def jacobian(self, q):
        axes, T = self.frames(q)
        p = T[:3, :3] @ self.tool_xyz + T[:3, 3]
        return np.array([np.r_[z, np.cross(z, p - o)] for z, o in axes]).T


def ur5e():
    """UR5e，末端点取 wrist_3_link 坐标系原点。"""
    return Arm("B-ARM-UR5E", "wrist_3_link")


def panda():
    """Franka Panda 七个关节，末端点取 link7 坐标系 z 轴上 0.107 m 处（法兰中心）。"""
    return Arm("B-ARM-PANDA", "link7", (0.0, 0.0, 0.107))


def planar2(t1, t2, l1, l2):
    """两连杆平面臂的末端位置与 2×2 雅可比矩阵（角度为弧度）。"""
    p = np.array([l1 * math.cos(t1) + l2 * math.cos(t1 + t2), l1 * math.sin(t1) + l2 * math.sin(t1 + t2)])
    J = np.array([[-l1 * math.sin(t1) - l2 * math.sin(t1 + t2), -l2 * math.sin(t1 + t2)],
                  [l1 * math.cos(t1) + l2 * math.cos(t1 + t2), l2 * math.cos(t1 + t2)]])
    return p, J


def ur5e_links():
    """UR5e 上臂与前臂的长度（肩关节到肘关节、肘关节到腕关节 1 沿连杆方向的距离），由关节表读出。"""
    js = {j["name"]: j for j in json.loads((MODELS / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))["robot"]["joints"]}
    return js["elbow_joint"]["origin"]["xyz"][2], js["wrist_1_joint"]["origin"]["xyz"][2]


def svd_fixed(A):
    """NumPy 的奇异值分解，再按本书约定统一奇异向量的符号：每个 v_i 中第一个绝对值最大的分量为正
    （绝对值相差不到 1e-9 的算作一样大，取靠前的一个），u_i 随之变号。"""
    U, s, Vt = np.linalg.svd(A)
    V = Vt.T.copy()
    for i in range(V.shape[1]):
        a = np.abs(V[:, i])
        k = int(np.flatnonzero(a >= a.max() - 1e-9)[0])
        if V[k, i] < 0:
            V[:, i] *= -1
            if i < U.shape[1]:
                U[:, i] *= -1
    return U, s, V
