"""第 12 章共用：旋量、矩阵指数、伴随矩阵，以及读取零件库模型（关节表与网页模型）。以下划线开头，构建时不单独运行。

本章所有“模型读数”都来自 textbook/robotics/models/ 里的零件库模型：
- entry.json 的关节表：每个关节的父连杆、子连杆、转轴（子连杆坐标系中）；
- default.glb 的节点：每个连杆坐标系相对父连杆的 4×4 矩阵（网页三维实验显示的就是它）。
模型的正运动学按三维引擎的做法计算：子连杆位姿 = 父连杆位姿 · 节点矩阵 · 绕关节轴转 θ。
这是与指数积公式完全独立的另一种算法，用来核对。
"""
import json
import math
import struct
from pathlib import Path

import numpy as np

MODELS = Path(__file__).resolve().parents[2] / "models"


# ---------------------------------------------------------------- 旋量与指数（第 4、6 章的结论）

def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]], dtype=float)


def rot(w, t):
    """罗德里格斯公式 (4.4.5)。"""
    K = skew(np.asarray(w, float))
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def screw_revolute(w, q):
    """转动关节的旋量轴 S = (ω, −ω × q)，式 (12.1.3)。"""
    w = np.asarray(w, float)
    return np.r_[w, -np.cross(w, np.asarray(q, float))]


def screw_prismatic(v):
    """移动关节的旋量轴 S = (0, v)，式 (12.1.4)。"""
    return np.r_[np.zeros(3), np.asarray(v, float)]


def bracket(S):
    """[S]：4×4 矩阵 [[ω] v; 0 0]。"""
    m = np.zeros((4, 4))
    m[:3, :3] = skew(S[:3])
    m[:3, 3] = S[3:]
    return m


def exp6(S, t):
    """e^{[S]θ}，式 (12.1.5)：转动关节用罗德里格斯公式和 G(θ)，移动关节为平移。"""
    S = np.asarray(S, float)
    w, v = S[:3], S[3:]
    T = np.eye(4)
    if np.linalg.norm(w) < 1e-12:
        T[:3, 3] = v * t
        return T
    K = skew(w)
    T[:3, :3] = rot(w, t)
    G = np.eye(3) * t + (1 - math.cos(t)) * K + (t - math.sin(t)) * K @ K
    T[:3, 3] = G @ v
    return T


def expm_series(A, n=40):
    """矩阵指数的级数定义，用来独立核对 exp6。"""
    S, term = np.eye(4), np.eye(4)
    for k in range(1, n):
        term = term @ A / k
        S = S + term
    return S


def adjoint(T):
    """[Ad_T] = [[R 0]; [[p]R R]]，式 (12.2.6)。"""
    R, p = T[:3, :3], T[:3, 3]
    A = np.zeros((6, 6))
    A[:3, :3] = R
    A[3:, 3:] = R
    A[3:, :3] = skew(p) @ R
    return A


def inv(T):
    R, p = T[:3, :3], T[:3, 3]
    out = np.eye(4)
    out[:3, :3] = R.T
    out[:3, 3] = -R.T @ p
    return out


def fk_space(Slist, M, theta):
    """空间形式 T = e^{[S1]θ1} ⋯ e^{[Sn]θn} M，式 (12.2.3)。"""
    T = np.eye(4)
    for S, t in zip(Slist, theta):
        T = T @ exp6(S, t)
    return T @ M


def fk_body(Blist, M, theta):
    """物体形式 T = M e^{[B1]θ1} ⋯ e^{[Bn]θn}，式 (12.2.5)。"""
    T = M.copy()
    for B, t in zip(Blist, theta):
        T = T @ exp6(B, t)
    return T


# ---------------------------------------------------------------- 零件库模型

def _glb_nodes(path: Path) -> dict:
    b = path.read_bytes()
    n = struct.unpack("<I", b[12:16])[0]
    js = json.loads(b[20:20 + n])
    nodes = {}
    for nd in js["nodes"]:
        m = np.eye(4)
        if "matrix" in nd:
            m = np.array(nd["matrix"], float).reshape(4, 4).T        # glTF 按列存
        elif "translation" in nd or "rotation" in nd:
            raise ValueError("模型节点用了平移/四元数形式，本程序只读矩阵形式")
        nodes[nd.get("name")] = {"m": m, "children": [js["nodes"][c].get("name") for c in nd.get("children", [])]}
    return nodes


class Model:
    """一个零件库机器人：关节表 + 网页模型的节点矩阵。坐标都以 base_link 的父坐标系（机器人基座坐标系 {s}）表示。"""

    def __init__(self, eid: str, base: str, tool_link: str, tool_xyz=(0, 0, 0), joints: list[str] | None = None):
        d = MODELS / eid
        self.id = eid
        self.entry = json.loads((d / "entry.json").read_text(encoding="utf-8"))
        self.nodes = _glb_nodes(d / "default.glb")
        self.base = base
        self.tool_link, self.tool_xyz = tool_link, np.asarray(tool_xyz, float)
        js = {j["name"]: j for j in self.entry["robot"]["joints"]}
        self.joints = [js[n] for n in (joints or [j["name"] for j in self.entry["robot"]["joints"] if j["type"] != "fixed"])]
        self.by_child = {j["child"]: j for j in self.joints}
        # 从基座到工具连杆的节点链
        parent = {c: p for p, nd in self.nodes.items() for c in nd["children"]}
        chain, n = [], tool_link
        while n != base:
            chain.insert(0, n)
            n = parent[n]
        self.chain = chain

    def fk(self, theta) -> np.ndarray:
        """按三维引擎的做法算末端位姿：从基座连杆起，逐个乘节点矩阵和关节转动（或移动）。"""
        val = {j["name"]: t for j, t in zip(self.joints, theta)}
        T = self.nodes[self.base]["m"].copy()          # 基座连杆相对基座坐标系（UR5e 为绕 z 转 180°）
        for n in self.chain:
            T = T @ self.nodes[n]["m"]
            j = self.by_child.get(n)
            if j is not None:
                t = val.get(j["name"], 0.0)
                a = np.asarray(j["axis"], float)
                M = np.eye(4)
                if j["type"] == "prismatic":
                    M[:3, 3] = a * t
                else:
                    M[:3, :3] = rot(a / np.linalg.norm(a), t)
                T = T @ M
        tool = np.eye(4)
        tool[:3, 3] = self.tool_xyz
        return T @ tool

    def screws(self):
        """零位时各关节在 {s} 中的旋量轴（由模型读出转轴方向 ω 和轴上一点 q）。"""
        out, T = [], self.nodes[self.base]["m"].copy()
        for n in self.chain:
            T = T @ self.nodes[n]["m"]
            j = self.by_child.get(n)
            if j is None:
                continue
            a = T[:3, :3] @ (np.asarray(j["axis"], float) / np.linalg.norm(j["axis"]))
            q = T[:3, 3]
            out.append((j["name"], j["type"], a, q, screw_prismatic(a) if j["type"] == "prismatic" else screw_revolute(a, q)))
        return out


def clean(x, tol=1e-12):
    """把 1e-17 这类舍入残差记为 0，便于印在书上。"""
    x = np.array(x, float)
    x[np.abs(x) < tol] = 0.0
    return x
