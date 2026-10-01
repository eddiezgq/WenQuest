# -*- coding: utf-8 -*-
"""按厂商公布的标准 DH 参数生成机械臂的简化模型和关节表（第 5 轮 P3、P4）。

engine: dh:<条目里 dh 段>   —— 条目（或其 vendor.yaml）里：
    dh: {params: [[a, d, alpha], ...], range_deg: [...], speed_deg_s: [...], reach_mm: 850}
连杆 i（i = 1..n）的坐标系放在 DH 坐标系 {i-1}，关节 i 绕本连杆的 z 轴转（anchor 为原点）；
连杆 i 的子连杆相对它的零位变换 = Tz(d_i) · Tx(a_i) · Rx(alpha_i)。与 Menagerie 机器人的关节表（R4）同一套字段。
外形是示意：关节处画圆柱，连杆画成连接相邻关节的圆管，粗细按臂展比例取；页面注明“按 DH 参数生成的示意模型”。
"""
import numpy as np


def _T(d, a, alpha):
    ca, sa = np.cos(alpha), np.sin(alpha)
    T = np.eye(4)
    T[:3, :3] = [[1, 0, 0], [0, ca, -sa], [0, sa, ca]]
    T[:3, 3] = [a, 0, d]
    return T


def _quat(R):
    """旋转矩阵 → 四元数 (w, x, y, z)"""
    w = np.sqrt(max(0.0, 1 + R[0, 0] + R[1, 1] + R[2, 2])) / 2
    x = np.sqrt(max(0.0, 1 + R[0, 0] - R[1, 1] - R[2, 2])) / 2
    y = np.sqrt(max(0.0, 1 - R[0, 0] + R[1, 1] - R[2, 2])) / 2
    z = np.sqrt(max(0.0, 1 - R[0, 0] - R[1, 1] + R[2, 2])) / 2
    x = np.copysign(x, R[2, 1] - R[1, 2])
    y = np.copysign(y, R[0, 2] - R[2, 0])
    z = np.copysign(z, R[1, 0] - R[0, 1])
    return [float(w), float(x), float(y), float(z)]


def _rpy(R):
    pitch = float(np.arcsin(np.clip(-R[2, 0], -1, 1)))
    if abs(np.cos(pitch)) > 1e-8:
        return [round(float(np.arctan2(R[2, 1], R[2, 2])), 6), round(pitch, 6), round(float(np.arctan2(R[1, 0], R[0, 0])), 6)]
    return [0.0, round(pitch, 6), round(float(np.arctan2(-R[0, 1], R[1, 1])), 6)]


def _tube(p0, p1, r, color):
    import trimesh
    v = np.asarray(p1, float) - np.asarray(p0, float)
    L = float(np.linalg.norm(v))
    if L < 1e-6:
        return None
    m = trimesh.creation.cylinder(radius=r, height=L, sections=24)
    z = np.array([0, 0, 1.0])
    axis = np.cross(z, v / L)
    s = np.linalg.norm(axis)
    R = np.eye(4)
    if s > 1e-9:
        R = trimesh.transformations.rotation_matrix(np.arccos(np.clip(np.dot(z, v / L), -1, 1)), axis / s)
    elif np.dot(z, v) < 0:
        R = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
    m.apply_transform(R)
    m.apply_translation((np.asarray(p0) + np.asarray(p1)) / 2)
    m.visual.face_colors = color
    return m


def build(entry, row):
    import trimesh
    dh = entry["dh"]
    P = dh["params"]
    n = len(P)
    reach = float(dh.get("reach_mm") or 1000) / 1000
    r = max(0.02, 0.055 * reach)                          # 关节圆柱半径（米）
    grey, blue = [200, 205, 210, 255], [60, 120, 170, 255]
    bodies = [{"name": "base", "parent": None, "pos": [0, 0, 0], "quat": [1, 0, 0, 0],
               "mesh": trimesh.util.concatenate([x for x in (
                   _tube([0, 0, 0], [0, 0, 0.6 * P[0][1]], r * 1.25, grey),) if x is not None])}]
    joints, links = [], [{"name": "base", "node": "base", "mass_kg": None}]
    world = [bodies[0]["mesh"].copy()]
    Tw = np.eye(4)
    for i, (a, d, alpha) in enumerate(P, start=1):
        name = "link{}".format(i)
        parent = "base" if i == 1 else "link{}".format(i - 1)
        rel = np.eye(4) if i == 1 else _T(*[P[i - 2][1], P[i - 2][0], P[i - 2][2]])
        Tw = Tw @ rel
        parts = [trimesh.creation.cylinder(radius=r, height=2.2 * r, sections=24)]   # 关节处的电机外壳（沿本连杆 z）
        parts[0].visual.face_colors = blue if i in (1, 2, 3) else grey
        p_d = [0, 0, d]
        for seg in (_tube([0, 0, 0], p_d, r * 0.8, grey), _tube(p_d, [a, 0, d], r * 0.8, grey)):
            if seg is not None:
                parts.append(seg)
        if i == n:                                       # 末端法兰
            fl = trimesh.creation.cylinder(radius=r * 0.7, height=0.01, sections=24)
            fl.apply_transform(_T(d, a, alpha))
            fl.visual.face_colors = [90, 95, 100, 255]
            parts.append(fl)
        mesh = trimesh.util.concatenate(parts)
        bodies.append({"name": name, "parent": parent, "pos": rel[:3, 3].tolist(), "quat": _quat(rel[:3, :3]), "mesh": mesh})
        world.append(mesh.copy().apply_transform(Tw))
        rng = (dh.get("range_deg") or [None] * n)[i - 1]
        spd = (dh.get("speed_deg_s") or [None] * n)[i - 1]
        j = {"name": "joint{}".format(i), "type": "revolute" if rng else "continuous", "parent": parent, "child": name,
             "axis": [0.0, 0.0, 1.0], "origin": {"xyz": [round(float(x), 6) for x in rel[:3, 3]], "rpy": _rpy(rel[:3, :3])}}
        if rng:
            j["limit"] = {"lower": round(-np.radians(rng), 6), "upper": round(np.radians(rng), 6)}
        if spd:
            j.setdefault("limit", {})["velocity"] = round(float(np.radians(spd)), 6)
        joints.append(j)
        links.append({"name": name, "node": name, "mass_kg": None})
    robot = {"links": links, "joints": joints, "dof": n, "tool": {"parent": "link{}".format(n),
             "xyz": [round(float(x), 6) for x in _T(P[-1][1], P[-1][0], P[-1][2])[:3, 3]]}}
    world_mm = trimesh.util.concatenate(world).apply_scale(1000.0)
    return [("__scene__", {"bodies": bodies, "world": world_mm, "robot": robot})]


def fk(params, q):
    """标准 DH 正运动学：返回末端（法兰）位姿 4×4（米）。测试用来核对模型与关节表一致。"""
    T = np.eye(4)
    for (a, d, alpha), qi in zip(params, q):
        c, s = np.cos(qi), np.sin(qi)
        Rz = np.eye(4)
        Rz[:2, :2] = [[c, -s], [s, c]]
        T = T @ Rz @ _T(d, a, alpha)
    return T
