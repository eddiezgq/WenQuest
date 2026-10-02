"""第 13 章共用：DH 变换（标准与改进两种约定）、公垂线、DH 与指数积的相互换算，以及读取零件库模型。
以下划线开头，构建时不单独运行。

指数积部分（旋量、矩阵指数、伴随矩阵）与第 12 章的 _poe.py 相同，这里重写一份，使本章程序自成一体。
零件库模型的读法也与第 12 章相同：关节表在 entry.json，连杆矩阵在 default.glb（网页三维实验显示的就是它）。
"""
import json
import math
import struct
from pathlib import Path

import numpy as np

MODELS = Path(__file__).resolve().parents[2] / "models"


# ---------------------------------------------------------------- 基本变换（第 4、5 章）

def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]], dtype=float)


def rot(w, t):
    """罗德里格斯公式：绕单位矢量 w 转 t。"""
    K = skew(np.asarray(w, float))
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def Rz(t):
    T = np.eye(4)
    T[:3, :3] = rot((0, 0, 1), t)
    return T


def Rx(t):
    T = np.eye(4)
    T[:3, :3] = rot((1, 0, 0), t)
    return T


def Ry(t):
    T = np.eye(4)
    T[:3, :3] = rot((0, 1, 0), t)
    return T


def Tz(d):
    T = np.eye(4)
    T[2, 3] = d
    return T


def Tx(a):
    T = np.eye(4)
    T[0, 3] = a
    return T


def inv(T):
    R, p = T[:3, :3], T[:3, 3]
    out = np.eye(4)
    out[:3, :3] = R.T
    out[:3, 3] = -R.T @ p
    return out


# ---------------------------------------------------------------- DH 变换

def sdh(a, alpha, d, theta):
    """标准 DH：T_{i-1,i} = Rot(z, θ) Trans(z, d) Trans(x, a) Rot(x, α)，式 (13.1.4) 的四步连乘。"""
    return Rz(theta) @ Tz(d) @ Tx(a) @ Rx(alpha)


def sdh_closed(a, alpha, d, theta):
    """标准 DH 变换的展开式 (13.1.5)，用来与四步连乘互相核对。"""
    ct, st, ca, sa = math.cos(theta), math.sin(theta), math.cos(alpha), math.sin(alpha)
    return np.array([[ct, -st * ca, st * sa, a * ct], [st, ct * ca, -ct * sa, a * st], [0, sa, ca, d], [0, 0, 0, 1.0]])


def mdh(a_prev, alpha_prev, d, theta):
    """改进 DH（Craig）：T_{i-1,i} = Rot(x, α_{i-1}) Trans(x, a_{i-1}) Rot(z, θ_i) Trans(z, d_i)，式 (13.1.7)。"""
    return Rx(alpha_prev) @ Tx(a_prev) @ Rz(theta) @ Tz(d)


def mdh_closed(a_prev, alpha_prev, d, theta):
    """改进 DH 变换的展开式 (13.1.8)。"""
    ct, st, ca, sa = math.cos(theta), math.sin(theta), math.cos(alpha_prev), math.sin(alpha_prev)
    return np.array([[ct, -st, 0, a_prev], [st * ca, ct * ca, -sa, -sa * d], [st * sa, ct * sa, ca, ca * d], [0, 0, 0, 1.0]])


def joint_values(table, q, kinds=None, offsets=None):
    """把控制器的关节变量 q 换成每行的 (θ, d)：转动关节 θ = q + 偏置，移动关节 d = q + 偏置。"""
    kinds = kinds or ["R"] * len(table)
    offsets = offsets if offsets is not None else [0.0] * len(table)
    out = []
    for (a, al, d, th), k, qi, off in zip(table, kinds, q, offsets):
        if k == "R":
            out.append((a, al, d, th + qi + off))
        else:
            out.append((a, al, d + qi + off, th))
    return out


def fk_sdh(table, q, kinds=None, offsets=None, frames=False):
    """标准 DH 正运动学：table 每行 (a_i, α_i, d_i, θ_i)，θ_i 或 d_i 加上关节变量。frames=True 时返回 {0}…{n} 全部坐标系。"""
    T, Fs = np.eye(4), [np.eye(4)]
    for a, al, d, th in joint_values(table, q, kinds, offsets):
        T = T @ sdh(a, al, d, th)
        Fs.append(T.copy())
    return Fs if frames else T


def fk_mdh(table, q, kinds=None, offsets=None, frames=False):
    """改进 DH 正运动学：table 第 i 行 (a_{i-1}, α_{i-1}, d_i, θ_i)，与 Craig 和 Franka 文档的排法相同。"""
    T, Fs = np.eye(4), [np.eye(4)]
    for a, al, d, th in joint_values(table, q, kinds, offsets):
        T = T @ mdh(a, al, d, th)
        Fs.append(T.copy())
    return Fs if frames else T


# ---------------------------------------------------------------- 指数积（第 12 章）

def screw_revolute(w, q):
    w = np.asarray(w, float)
    return np.r_[w, -np.cross(w, np.asarray(q, float))]


def screw_prismatic(v):
    return np.r_[np.zeros(3), np.asarray(v, float)]


def exp6(S, t):
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


def adjoint(T):
    R, p = T[:3, :3], T[:3, 3]
    A = np.zeros((6, 6))
    A[:3, :3] = R
    A[3:, 3:] = R
    A[3:, :3] = skew(p) @ R
    return A


def fk_space(Slist, M, theta):
    T = np.eye(4)
    for S, t in zip(Slist, theta):
        T = T @ exp6(S, t)
    return T @ M


Z_REV = np.array([0, 0, 1.0, 0, 0, 0])       # 绕自身 z 轴转动的旋量
Z_PRI = np.array([0, 0, 0, 0, 0, 1.0])       # 沿自身 z 轴移动的旋量


# ---------------------------------------------------------------- 换算（13.4 节）

def sdh_to_poe(table, kinds=None, offsets=None, T_s0=None, T_nb=None):
    """标准 DH → 指数积（定理 13.4.1）：关节 i 的轴是零位时 {i-1} 的 z 轴，S_i = [Ad_{T_{0,i-1}(0)}] (0,0,1,0,0,0)。
    M = T_s0 T_{0n}(0) T_nb。"""
    n = len(table)
    kinds = kinds or ["R"] * n
    T_s0 = np.eye(4) if T_s0 is None else T_s0
    Fs = fk_sdh(table, np.zeros(n), kinds, offsets, frames=True)
    S = [adjoint(T_s0 @ Fs[i]) @ (Z_REV if k == "R" else Z_PRI) for i, k in enumerate(kinds)]
    M = T_s0 @ Fs[-1] @ (np.eye(4) if T_nb is None else T_nb)
    return S, M


def mdh_to_poe(table, kinds=None, offsets=None, T_s0=None, T_nb=None):
    """改进 DH → 指数积（推论 13.4.1）：关节 i 的轴是零位时 {i} 的 z 轴，S_i = [Ad_{T_{0i}(0)}] (0,0,1,0,0,0)。"""
    n = len(table)
    kinds = kinds or ["R"] * n
    T_s0 = np.eye(4) if T_s0 is None else T_s0
    Fs = fk_mdh(table, np.zeros(n), kinds, offsets, frames=True)
    S = [adjoint(T_s0 @ Fs[i + 1]) @ (Z_REV if k == "R" else Z_PRI) for i, k in enumerate(kinds)]
    M = T_s0 @ Fs[-1] @ (np.eye(4) if T_nb is None else T_nb)
    return S, M


def common_normal(p1, u1, p2, u2, tol=1e-12):
    """两条直线 (p1, u1)、(p2, u2) 的公垂线（13.1.2 节）。返回 (情形, 垂足1, 垂足2, 距离, 单位方向 n)。
    情形：'skew' 异面，'intersect' 相交，'parallel' 平行（公垂线不唯一，取过 p1 的那一条），'same' 重合。"""
    p1, u1, p2, u2 = (np.asarray(x, float) for x in (p1, u1, p2, u2))
    u1, u2 = u1 / np.linalg.norm(u1), u2 / np.linalg.norm(u2)
    c = np.cross(u1, u2)
    w = p2 - p1
    if np.linalg.norm(c) > tol:
        n = c / np.linalg.norm(c)
        dist = float(w @ n)
        # p1 + t u1 + dist n = p2 + s u2：在 u1、u2 方向上解 t、s
        A = np.array([[u1 @ u1, -(u1 @ u2)], [u1 @ u2, -(u2 @ u2)]])
        b = np.array([w @ u1, w @ u2])
        t, s = np.linalg.solve(A, b)
        f1, f2 = p1 + t * u1, p2 + s * u2
        if abs(dist) < 1e-12:
            return "intersect", f1, f2, 0.0, n
        if dist < 0:
            n, dist = -n, -dist
        return "skew", f1, f2, dist, n
    perp = w - (w @ u1) * u1
    if np.linalg.norm(perp) < tol:
        return "same", p1, p1, 0.0, None
    return "parallel", p1, p1 + perp, float(np.linalg.norm(perp)), perp / np.linalg.norm(perp)


def _signed_angle(a, b, axis):
    return math.atan2(float(np.cross(a, b) @ axis), float(a @ b))


def lines_to_sdh(axes, tool, T_s0=np.eye(4)):
    """指数积 → 标准 DH（13.4.3 节的步骤）。
    axes：零位时各关节轴 [(类型 'R'/'P', 方向 ω̂ 或 v, 轴上一点 q)]，在 {s} 中；tool：末端点（须在最后一根轴上）。
    {0} = T_s0，其 z 轴须沿关节 1 的轴。x_i 的正负取使 x_i 与 x_{i-1} 尽量同向（厂商手册的习惯：θ 偏置尽量为 0），
    所以 a_i 可以为负。返回 (表 [(a, α, d, θ偏置)], 各坐标系 {0}…{n})。"""
    F = [np.array(T_s0, float)]
    rows = []
    n = len(axes)
    for i in range(n):
        o, x, z = F[-1][:3, 3], F[-1][:3, 0], F[-1][:3, 2]
        if i < n - 1:
            u, q = np.asarray(axes[i + 1][1], float), np.asarray(axes[i + 1][2], float)
            u = u / np.linalg.norm(u)
            kind, f1, f2, dist, nrm = common_normal(o, z, q, u)
            if kind == "same":
                nrm, f1, f2 = x, o, o
            if kind == "parallel":          # 公垂线不唯一：取过 {i-1} 原点的那一条，使 d_i = 0
                f1 = o
            xi = nrm if nrm @ x >= -1e-12 else -nrm
            zi = u
            oi = f2
        else:                                # 最后一个坐标系：原点在末端点，z_n 与 z_{n-1} 同向，x_n 与 x_{n-1} 同向
            tp = np.asarray(tool, float)
            f1 = o + ((tp - o) @ z) * z
            assert np.linalg.norm(tp - f1) < 1e-9, "末端点不在最后一根轴上"
            xi, zi, oi = x, z, tp
        d = float((f1 - o) @ z)
        a = float((oi - f1) @ xi)
        alpha = _signed_angle(z, zi, xi)
        theta = _signed_angle(x, xi, z)
        rows.append((a, alpha, d, theta))
        Fi = np.eye(4)
        Fi[:3, 0], Fi[:3, 2] = xi, zi
        Fi[:3, 1] = np.cross(zi, xi)
        Fi[:3, 3] = oi
        F.append(Fi)
    return rows, F


# ---------------------------------------------------------------- UR5e（与第 12 章表 12.1.1 相同）

H1, W1, L1, W2, L2, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1


def ur_poe():
    """第 12 章表 12.1.1 的旋量轴和零位位姿 M（{b} 取模型最后一个连杆，原点在法兰盘中心）。"""
    yd = np.array([0, -1.0, 0])
    tab = [((0, 0, 1.0), (0, 0, H1)), (yd, (0, -W1, H1)), (yd, (-L1, -W1 + W2, H1)), (yd, (-L1 - L2, -W1 + W2, H1)),
           ((0, 0, -1.0), (-L1 - L2, -W1 + W2 - W3, H1)), (yd, (-L1 - L2, -W1 + W2 - W3, H1 - H2))]
    S = [screw_revolute(w, q) for w, q in tab]
    M = np.array([[1.0, 0, 0, -L1 - L2], [0, -1, 0, -W1 + W2 - W3 - W4], [0, 0, -1, H1 - H2], [0, 0, 0, 1]])
    return tab, S, M


def ur_vendor_raw():
    """零件库条目 B-ARM-UR5E 的 dh.params（每行 (a, d, α)）。条目把 α 存成七位小数 1.5707963。"""
    e = json.loads((MODELS / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))
    assert e["dh"]["convention"].startswith("standard")
    return [tuple(r) for r in e["dh"]["params"]]


def ur_vendor():
    """UR 公司公布的 UR5e 标准 DH 参数，整理成 (a, α, d, θ偏置)。

    长度取零件库条目（照录 UR 网站文章）；UR 网站上 α 写作 0、π/2、−π/2，
    而零件库条目存的是截断的七位小数，所以这里把 α 还原为 π/2 的精确整数倍。"""
    rows = []
    for a, d, al in ur_vendor_raw():
        k = round(al / (math.pi / 2))
        assert abs(al - k * math.pi / 2) < 1e-6
        rows.append((a, k * math.pi / 2, d, 0.0))
    return rows


# ---------------------------------------------------------------- 零件库模型（与第 12 章 _poe.py 相同）

def _glb_nodes(path: Path) -> dict:
    b = path.read_bytes()
    n = struct.unpack("<I", b[12:16])[0]
    js = json.loads(b[20:20 + n])
    nodes = {}
    for nd in js["nodes"]:
        m = np.eye(4)
        if "matrix" in nd:
            m = np.array(nd["matrix"], float).reshape(4, 4).T
        elif "translation" in nd or "rotation" in nd:
            raise ValueError("模型节点用了平移/四元数形式，本程序只读矩阵形式")
        nodes[nd.get("name")] = {"m": m, "children": [js["nodes"][c].get("name") for c in nd.get("children", [])]}
    return nodes


class Model:
    """一个零件库机器人：关节表 + 网页模型的节点矩阵。坐标以机器人基座坐标系 {s} 表示。"""

    def __init__(self, eid: str, base: str, tool_link: str, tool_xyz=(0, 0, 0), joints=None):
        d = MODELS / eid
        self.entry = json.loads((d / "entry.json").read_text(encoding="utf-8"))
        self.nodes = _glb_nodes(d / "default.glb")
        self.base = base
        self.tool_link, self.tool_xyz = tool_link, np.asarray(tool_xyz, float)
        js = {j["name"]: j for j in self.entry["robot"]["joints"]}
        self.joints = [js[n] for n in (joints or [j["name"] for j in self.entry["robot"]["joints"] if j["type"] != "fixed"])]
        self.by_child = {j["child"]: j for j in self.joints}
        parent = {c: p for p, nd in self.nodes.items() for c in nd["children"]}
        chain, n = [], tool_link
        while n != base:
            chain.insert(0, n)
            n = parent[n]
        self.chain = chain

    def fk(self, theta) -> np.ndarray:
        """三维引擎的算法：从基座连杆起逐个乘节点矩阵和关节运动。"""
        val = {j["name"]: t for j, t in zip(self.joints, theta)}
        T = self.nodes[self.base]["m"].copy()
        for n in self.chain:
            T = T @ self.nodes[n]["m"]
            j = self.by_child.get(n)
            if j is not None:
                t = val.get(j["name"], 0.0)
                a = np.asarray(j["axis"], float)
                Mj = np.eye(4)
                if j["type"] == "prismatic":
                    Mj[:3, 3] = a * t
                else:
                    Mj[:3, :3] = rot(a / np.linalg.norm(a), t)
                T = T @ Mj
        tool = np.eye(4)
        tool[:3, 3] = self.tool_xyz
        return T @ tool

    def link(self, name, theta) -> np.ndarray:
        """某个连杆坐标系在 {s} 中的位姿。"""
        keep = self.tool_link, self.tool_xyz, self.chain
        parent = {c: p for p, nd in self.nodes.items() for c in nd["children"]}
        chain, n = [], name
        while n != self.base:
            chain.insert(0, n)
            n = parent[n]
        self.tool_link, self.tool_xyz, self.chain = name, np.zeros(3), chain
        try:
            return self.fk(theta)
        finally:
            self.tool_link, self.tool_xyz, self.chain = keep

    def axes(self):
        """零位时各关节的 (类型, 方向, 轴上一点)，在 {s} 中（由模型读出）。"""
        out, T = [], self.nodes[self.base]["m"].copy()
        for n in self.chain:
            T = T @ self.nodes[n]["m"]
            j = self.by_child.get(n)
            if j is None:
                continue
            a = T[:3, :3] @ (np.asarray(j["axis"], float) / np.linalg.norm(j["axis"]))
            out.append(("P" if j["type"] == "prismatic" else "R", a, T[:3, 3].copy()))
        return out


def clean(x, tol=1e-12):
    x = np.array(x, float)
    x[np.abs(x) < tol] = 0.0
    return x
