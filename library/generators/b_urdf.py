# -*- coding: utf-8 -*-
"""B 部分 URDF 机器人（robot_descriptions 登记的原仓库，第 5 轮 P8）：按连杆分节点的 glTF 与关节表（R4）。

engine: urdf:<仓库键>/<URDF 相对路径>；仓库在 library/vendor_src/rd/<仓库键>（tools/fetch_sources.py 按固定提交稀疏检出）。
连杆坐标系 = URDF 连杆坐标系；子连杆相对父连杆的零位 = 关节 origin；关节轴在子连杆坐标系（URDF 定义即如此），anchor 为原点。
"""
import os
import re

import subprocess
from pathlib import Path

import numpy as np

from generators.b_robot import MAX_FACES, _rpy, _simplify

RD = Path(os.environ.get("WQ_RD_SRC", Path(__file__).resolve().parents[1] / "vendor_src" / "rd"))


def _rpy_to_R(r, p, y):
    cr, sr, cp, sp, cy, sy = np.cos(r), np.sin(r), np.cos(p), np.sin(p), np.cos(y), np.sin(y)
    return np.array([[cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
                     [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
                     [-sp, cp * sr, cp * cr]])


def _T(xyz, rpy):
    T = np.eye(4)
    T[:3, :3] = _rpy_to_R(*rpy)
    T[:3, 3] = xyz
    return T


def _quat(R):
    w = np.sqrt(max(0.0, 1 + R[0, 0] + R[1, 1] + R[2, 2])) / 2
    x = np.copysign(np.sqrt(max(0.0, 1 + R[0, 0] - R[1, 1] - R[2, 2])) / 2, R[2, 1] - R[1, 2])
    y = np.copysign(np.sqrt(max(0.0, 1 - R[0, 0] + R[1, 1] - R[2, 2])) / 2, R[0, 2] - R[2, 0])
    z = np.copysign(np.sqrt(max(0.0, 1 - R[0, 0] - R[1, 1] + R[2, 2])) / 2, R[1, 0] - R[0, 1])
    return [float(w), float(x), float(y), float(z)]


def _files(repo):
    out = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", "HEAD"], capture_output=True, text=True)
    return set(out.stdout.splitlines())


def _resolver(repo, urdf_rel):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
    from import_rd import resolve
    files = _files(repo)

    def handle(ref):
        p = resolve(ref, urdf_rel, files)
        return str(repo / p) if p else ref
    return handle


def _geom(g, handle):
    """URDF 几何 → trimesh（米）"""
    import trimesh
    if g.mesh is not None:
        path = handle(g.mesh.filename)
        if not os.path.exists(path):
            return None
        try:
            m = trimesh.load(path, force="mesh", process=False)
        except Exception:  # noqa: BLE001
            return None
        if path.lower().endswith(".dae"):          # Collada 自带长度单位（<unit meter="…">），trimesh 不处理，按 ROS 的做法换算
            mt = re.search(r'<unit[^>]*meter="([0-9.eE+-]+)"', open(path, encoding="utf-8", errors="replace").read(4000))
            if mt and abs(float(mt.group(1)) - 1.0) > 1e-9:
                m.apply_scale(float(mt.group(1)))
        if g.mesh.scale is not None:
            m.apply_scale(np.asarray(g.mesh.scale, float) if np.ndim(g.mesh.scale) else float(g.mesh.scale))
        return m
    if g.box is not None:
        return trimesh.creation.box(extents=g.box.size)
    if g.cylinder is not None:
        return trimesh.creation.cylinder(radius=g.cylinder.radius, height=g.cylinder.length, sections=24)
    if g.sphere is not None:
        return trimesh.creation.icosphere(subdivisions=2, radius=g.sphere.radius)
    return None


def build(entry, row):
    import trimesh
    import yourdfpy
    key, _, rel = entry["model"]["engine"].split(":", 1)[1].partition("/")
    repo = RD / key
    handle = _resolver(repo, rel)
    robot = yourdfpy.URDF.load(str(repo / rel), load_meshes=False, build_scene_graph=False,
                               filename_handler=lambda f: f).robot
    mats = {m.name: m for m in robot.materials or []}
    links = {l.name: l for l in robot.links}
    parent_of = {j.child: j for j in robot.joints}
    names = list(links) + [j.parent for j in robot.joints if j.parent not in links]     # 未声明的父连杆（如 world）当空根连杆
    names = list(dict.fromkeys(names))
    roots = [n for n in names if n not in parent_of]
    # 每个连杆的可视网格（连杆坐标系）
    meshes = {}
    for l in robot.links:
        parts = []
        for v in l.visuals or []:
            m = _geom(v.geometry, handle)
            if m is None or len(m.faces) == 0:
                continue
            if v.origin is not None:
                m.apply_transform(np.asarray(v.origin))
            rgba = None
            mat = v.material
            if mat is not None:
                c = mat.color or (mats.get(mat.name).color if mats.get(mat.name) else None)
                if c is not None and c.rgba is not None:
                    rgba = (np.clip(np.asarray(c.rgba, float), 0, 1) * 255).astype(np.uint8)
            if rgba is None:
                rgba = np.array([185, 190, 196, 255], np.uint8)
            m.visual = trimesh.visual.ColorVisuals(m, face_colors=np.tile(rgba, (len(m.faces), 1)))
            parts.append(m)
        meshes[l.name] = trimesh.util.concatenate(parts) if parts else None
    total = sum(len(m.faces) for m in meshes.values() if m is not None)
    ratio = min(1.0, MAX_FACES / max(total, 1))
    # 按运动链顺序排连杆（父在前）
    order, stack = [], list(roots)
    children = {}
    for j in robot.joints:
        children.setdefault(j.parent, []).append(j.child)
    while stack:
        n = stack.pop(0)
        order.append(n)
        stack.extend(children.get(n, []))
    bodies, world, joints, Tw = [], [], [], {}
    for n in order:
        j = parent_of.get(n)
        T = np.asarray(j.origin) if (j is not None and j.origin is not None) else np.eye(4)
        m = meshes.get(n)
        if m is not None:
            m.merge_vertices()
            if ratio < 1.0 and len(m.faces) > 200:
                m = _simplify(m, ratio)
        bodies.append({"name": n, "parent": j.parent if j is not None else None, "pos": T[:3, 3].tolist(),
                       "quat": _quat(T[:3, :3]), "mesh": m})
        Tw[n] = (Tw[j.parent] if j is not None else np.eye(4)) @ T
        if m is not None:
            world.append(m.copy().apply_transform(Tw[n]))
        if j is None:
            continue
        typ = j.type if j.type in ("revolute", "continuous", "prismatic") else "fixed"
        jt = {"name": j.name, "type": typ, "parent": j.parent, "child": n,
              "axis": [round(float(a), 6) for a in (j.axis if j.axis is not None else (1, 0, 0))],
              "origin": {"xyz": [round(float(x), 6) for x in T[:3, 3]], "rpy": _rpy_quat(T)}}
        lim = j.limit
        if lim is not None and typ in ("revolute", "prismatic") and lim.lower is not None and lim.upper is not None:
            jt["limit"] = {"lower": round(float(lim.lower), 6), "upper": round(float(lim.upper), 6)}
            if lim.velocity:
                jt["limit"]["velocity"] = round(float(lim.velocity), 6)
            if lim.effort:
                jt["limit"]["effort"] = round(float(lim.effort), 6)
        elif typ == "revolute":
            jt["type"] = "continuous"
        joints.append(jt)
    if not world:
        raise ValueError("URDF 没有可显示的几何（网格文件缺失？）")
    # glTF 导出（trimesh）把 world 当场景根的名字：同名连杆改名，节点与关节表一致
    ren = {"world": "world_frame"}
    for b_ in bodies:
        b_["name"] = ren.get(b_["name"], b_["name"])
        b_["parent"] = ren.get(b_["parent"], b_["parent"]) if b_["parent"] else None
    for j in joints:
        j["parent"], j["child"] = ren.get(j["parent"], j["parent"]), ren.get(j["child"], j["child"])
    links = {ren.get(k, k): v for k, v in links.items()}
    moving = [j for j in joints if j["type"] != "fixed"]
    def mass(n):
        lk = links.get(n)
        return round(float(lk.inertial.mass), 4) if lk is not None and lk.inertial is not None and lk.inertial.mass else None
    rob = {"links": [{"name": b["name"], "node": b["name"], "mass_kg": mass(b["name"])} for b in bodies],
           "joints": joints, "dof": len(moving)}
    return [("__scene__", {"bodies": bodies, "world": trimesh.util.concatenate(world).apply_scale(1000.0), "robot": rob})]


def _rpy_quat(T):
    return _rpy(_quat(T[:3, :3]))


