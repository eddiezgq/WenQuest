# -*- coding: utf-8 -*-
"""B 部分现成机器人：读 MJCF（MuJoCo Menagerie），按连杆（body）分节点，并提取关节表（附录 B.13、约定 R4）。

build(entry, row) 返回 [("__scene__", 构件)]：构件里有
    bodies：[{name, parent, pos, quat, mesh(顶点米、面、颜色)}]（位姿相对父连杆，关节为零位）
    world_tris：零位（或 home 关键帧）下全部三角形（世界坐标，毫米），缩略图用
    robot：entry.json 里的 robot 段（links、joints、dof）
"""
import os
from pathlib import Path

import numpy as np

MENAGERIE = Path(os.environ.get("WQ_MENAGERIE", Path(__file__).resolve().parents[1] / "vendor_src" / "mujoco_menagerie"))
MAX_FACES = 40000          # 每个机器人网页模型的三角形上限（超过就简化，B.5：glb ≤ 2 MB 左右）


def _quat_to_mat(q):
    w, x, y, z = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def _rpy(q):
    """四元数（w,x,y,z）→ URDF 的 roll, pitch, yaw（弧度）"""
    R = _quat_to_mat(q)
    pitch = float(np.arcsin(np.clip(-R[2, 0], -1, 1)))
    if abs(np.cos(pitch)) > 1e-8:
        roll = float(np.arctan2(R[2, 1], R[2, 2]))
        yaw = float(np.arctan2(R[1, 0], R[0, 0]))
    else:
        roll, yaw = 0.0, float(np.arctan2(-R[0, 1], R[1, 1]))
    return [round(roll, 6), round(pitch, 6), round(yaw, 6)]


def _primitive(mujoco, m, g):
    import trimesh
    t, s = int(m.geom_type[g]), m.geom_size[g]
    T = type("T", (), {k: int(getattr(mujoco.mjtGeom, k)) for k in dir(mujoco.mjtGeom) if k.startswith("mjGEOM_")})
    if t == T.mjGEOM_BOX:
        return trimesh.creation.box(extents=2 * s)
    if t == T.mjGEOM_SPHERE:
        return trimesh.creation.icosphere(subdivisions=2, radius=s[0])
    if t == T.mjGEOM_CAPSULE:
        return trimesh.creation.capsule(height=2 * s[1], radius=s[0], count=[16, 8])
    if t == T.mjGEOM_CYLINDER:
        return trimesh.creation.cylinder(radius=s[0], height=2 * s[1], sections=24)
    if t == T.mjGEOM_ELLIPSOID:
        mesh = trimesh.creation.icosphere(subdivisions=2, radius=1.0)
        mesh.apply_scale(s)
        return mesh
    if t == T.mjGEOM_MESH:
        mid = m.geom_dataid[g]
        va, vn = m.mesh_vertadr[mid], m.mesh_vertnum[mid]
        fa, fn = m.mesh_faceadr[mid], m.mesh_facenum[mid]
        return trimesh.Trimesh(vertices=m.mesh_vert[va:va + vn].copy(), faces=m.mesh_face[fa:fa + fn].copy(), process=False)
    return None                           # 平面、高度场等不画


def _rgba(m, g):
    mat = m.geom_matid[g]
    rgba = m.mat_rgba[mat] if mat >= 0 else m.geom_rgba[g]
    return (np.clip(rgba, 0, 1) * 255).astype(np.uint8)


def load(entry):
    import mujoco
    xml = MENAGERIE / entry["model"]["engine"].split(":", 1)[1]
    m = mujoco.MjModel.from_xml_path(str(xml))
    return mujoco, m


def build(entry, row):
    import trimesh
    mujoco, m = load(entry)
    d = mujoco.MjData(m)
    if m.nkey:                             # 有 home 关键帧就用它的姿态画缩略图
        mujoco.mj_resetDataKeyframe(m, d, 0)
    mujoco.mj_forward(m, d)
    name = lambda obj, i: mujoco.mj_id2name(m, obj, i) or "body_{}".format(i)  # noqa: E731
    B = mujoco.mjtObj.mjOBJ_BODY

    groups = set(m.geom_group.tolist())
    visual = [g for g in range(m.ngeom) if (m.geom_group[g] in (1, 2) if groups & {1, 2} else m.geom_group[g] != 3)
              and not (m.geom_contype[g] and m.geom_conaffinity[g] and groups & {1, 2})]
    if not visual:                         # 有的模型显示几何同时参与碰撞（如 Barkour v0）
        visual = [g for g in range(m.ngeom) if m.geom_group[g] in (1, 2)] or list(range(m.ngeom))
    per_body = {}
    for g in visual:
        mesh = _primitive(mujoco, m, g)
        if mesh is None or len(mesh.faces) == 0:
            continue
        T = np.eye(4)
        T[:3, :3] = _quat_to_mat(m.geom_quat[g])
        T[:3, 3] = m.geom_pos[g]
        mesh.apply_transform(T)
        mesh.visual = trimesh.visual.ColorVisuals(mesh, face_colors=np.tile(_rgba(m, g), (len(mesh.faces), 1)))
        per_body.setdefault(int(m.geom_bodyid[g]), []).append(mesh)

    total = sum(len(x.faces) for ms in per_body.values() for x in ms)
    ratio = min(1.0, MAX_FACES / max(total, 1))
    bodies, world = [], []
    for b in range(1, m.nbody):
        meshes = per_body.get(b, [])
        mesh = trimesh.util.concatenate(meshes) if meshes else None
        if mesh is not None:
            mesh.merge_vertices()
        if mesh is not None and ratio < 1.0 and len(mesh.faces) > 200:
            mesh = _simplify(mesh, ratio)
        parent = int(m.body_parentid[b])
        bodies.append({"name": name(B, b), "parent": name(B, parent) if parent else None,
                       "pos": m.body_pos[b].tolist(), "quat": m.body_quat[b].tolist(), "mesh": mesh})
        if mesh is not None:
            Tw = np.eye(4)
            Tw[:3, :3] = d.xmat[b].reshape(3, 3)
            Tw[:3, 3] = d.xpos[b]
            world.append(mesh.copy().apply_transform(Tw))

    robot = {"links": [], "joints": []}
    for b in range(1, m.nbody):
        robot["links"].append({"name": name(B, b), "node": name(B, b), "mass_kg": round(float(m.body_mass[b]), 4)})
    J = mujoco.mjtJoint
    dof = 0
    for j in range(m.njnt):
        t = int(m.jnt_type[j])
        if t not in (int(J.mjJNT_HINGE), int(J.mjJNT_SLIDE)):
            continue                       # 自由关节（移动底座、飞行器机体）、球关节不列
        dof += 1
        b = int(m.jnt_bodyid[j])
        limited = bool(m.jnt_limited[j])
        typ = "prismatic" if t == int(J.mjJNT_SLIDE) else ("revolute" if limited else "continuous")
        jt = {"name": mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j) or "joint_{}".format(j), "type": typ,
              "parent": name(B, int(m.body_parentid[b])), "child": name(B, b),
              "axis": [round(float(x), 6) for x in m.jnt_axis[j]],
              "origin": {"xyz": [round(float(x), 6) for x in m.body_pos[b]], "rpy": _rpy(m.body_quat[b])}}
        if any(abs(x) > 1e-9 for x in m.jnt_pos[j]):
            jt["anchor"] = [round(float(x), 6) for x in m.jnt_pos[j]]     # 转轴在子连杆坐标系中的位置
        if limited:
            jt["limit"] = {"lower": round(float(m.jnt_range[j][0]), 6), "upper": round(float(m.jnt_range[j][1]), 6)}
        robot["joints"].append(jt)
    robot["dof"] = dof
    if m.nkey:                                 # 学习平台 R7：第一个关键帧（通常是 home）的关节值 = 站立/初始姿态
        kq = m.key_qpos[0]
        rest = {}
        for j in range(m.njnt):
            if int(m.jnt_type[j]) in (int(J.mjJNT_HINGE), int(J.mjJNT_SLIDE)):
                rest[mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_JOINT, j) or "joint_{}".format(j)] = round(
                    float(kq[m.jnt_qposadr[j]]), 6)
        if any(abs(v) > 1e-9 for v in rest.values()):
            robot["rest"] = rest
            robot["rest_source"] = mujoco.mj_id2name(m, mujoco.mjtObj.mjOBJ_KEY, 0) or "keyframe 0"
    world_mm = trimesh.util.concatenate(world).apply_scale(1000.0) if world else None
    return [("__scene__", {"bodies": bodies, "world": world_mm, "robot": robot})]


def _simplify(mesh, ratio):
    """先用二次误差简化；有的网格（很多小的开放曲面）简化不动，就退一步用网格聚类（顶点对齐到小方格再合并）。"""
    import trimesh
    target = max(100, int(len(mesh.faces) * ratio))
    col = mesh.visual.face_colors[0] if len(mesh.faces) else [180, 180, 180, 255]
    v, f = mesh.vertices, mesh.faces
    try:
        import fast_simplification
        v, f = fast_simplification.simplify(np.asarray(v, np.float32), f, target_count=target)
    except ImportError:
        pass
    if len(f) > target * 1.3:
        v, f = _cluster(np.asarray(mesh.vertices, float), np.asarray(mesh.faces), target)
    out = trimesh.Trimesh(v, f, process=False)
    out.visual = trimesh.visual.ColorVisuals(out, face_colors=np.tile(col, (len(out.faces), 1)))
    return out


def _cluster(v, f, target):
    size = float(np.max(v.max(0) - v.min(0))) or 1.0
    cell = size / 400
    for _ in range(12):
        q = np.floor((v - v.min(0)) / cell).astype(np.int64)
        _, inv = np.unique(q, axis=0, return_inverse=True)
        inv = inv.reshape(-1)
        nf = inv[f]
        nf = nf[(nf[:, 0] != nf[:, 1]) & (nf[:, 1] != nf[:, 2]) & (nf[:, 0] != nf[:, 2])]
        if len(nf) <= target or cell > size / 8:
            break
        cell *= 1.4
    nv = np.zeros((inv.max() + 1, 3))
    cnt = np.bincount(inv)
    for k in range(3):
        nv[:, k] = np.bincount(inv, weights=v[:, k]) / cnt
    return nv, nf


def glb_bytes(scene_part):
    """连杆一个节点、节点名 = 连杆名，层级 = 运动链；root 把 Z 向上转成 Y 向上（B.13）。"""
    import trimesh
    sc = trimesh.Scene()
    rot = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])
    sc.graph.update(frame_from=sc.graph.base_frame, frame_to="root", matrix=rot)
    for bd in scene_part["bodies"]:
        T = np.eye(4)
        T[:3, :3] = _quat_to_mat(bd["quat"])
        T[:3, 3] = bd["pos"]
        parent = bd["parent"] or "root"
        if bd["mesh"] is not None:
            sc.add_geometry(bd["mesh"], node_name=bd["name"], geom_name=bd["name"], parent_node_name=parent, transform=T)
        else:
            sc.graph.update(frame_from=parent, frame_to=bd["name"], matrix=T)
    return sc.export(file_type="glb")
