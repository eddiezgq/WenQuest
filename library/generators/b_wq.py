# -*- coding: utf-8 -*-
"""问渠自建机器人（第 5 轮 P9、P12）：参数化生成 glTF（按连杆/构件分节点）、关节表（R4）、URDF；并联机构另出运动表（R5）。

engine: wqrobot:<型式>，参数取条目的 defaults（米、弧度），范围见 ranges：
    scara      SCARA：J1、J2 绕竖直轴转，J3 丝杠升降，J4 末端转
    delta      Delta 并联：三个主动臂各绕切向轴摆动；从动臂（平行四边形）与动平台由运动表给出
    diff_cart  差速小车：两个驱动轮（连续转动）+ 万向轮
返回 [("__scene__", {bodies, world, robot, mechanism?, motion?, urdf?})]，bodies 的格式同 b_robot（位姿相对父节点）。
"""
import math

import numpy as np

GREY, BLUE, DARK, YEL = [205, 210, 214, 255], [60, 120, 170, 255], [70, 76, 82, 255], [242, 183, 5, 255]


# ---------------------------------------------------------------- 小工具
def _cyl(r, h, color, axis="z", center=(0, 0, 0)):
    import trimesh
    m = trimesh.creation.cylinder(radius=r, height=h, sections=32)
    if axis == "x":
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0]))
    elif axis == "y":
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0]))
    m.apply_translation(center)
    m.visual.face_colors = color
    return m


def _box(ext, color, center=(0, 0, 0)):
    import trimesh
    m = trimesh.creation.box(extents=ext)
    m.apply_translation(center)
    m.visual.face_colors = color
    return m


def _cat(*ms):
    import trimesh
    return trimesh.util.concatenate([m for m in ms if m is not None])


def _quat_from_R(R):
    w = math.sqrt(max(0.0, 1 + R[0, 0] + R[1, 1] + R[2, 2])) / 2
    x = math.copysign(math.sqrt(max(0.0, 1 + R[0, 0] - R[1, 1] - R[2, 2])) / 2, R[2, 1] - R[1, 2])
    y = math.copysign(math.sqrt(max(0.0, 1 - R[0, 0] + R[1, 1] - R[2, 2])) / 2, R[0, 2] - R[2, 0])
    z = math.copysign(math.sqrt(max(0.0, 1 - R[0, 0] - R[1, 1] + R[2, 2])) / 2, R[1, 0] - R[0, 1])
    return [w, x, y, z]


def _Rz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])


def _Ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def _body(name, parent, pos, mesh, R=None):
    return {"name": name, "parent": parent, "pos": [float(x) for x in pos],
            "quat": _quat_from_R(R) if R is not None else [1.0, 0.0, 0.0, 0.0], "mesh": mesh}


def _joint(name, typ, parent, child, xyz, axis, rpy=(0, 0, 0), lower=None, upper=None, velocity=None):
    j = {"name": name, "type": typ, "parent": parent, "child": child, "axis": [float(a) for a in axis],
         "origin": {"xyz": [round(float(x), 6) for x in xyz], "rpy": [round(float(x), 6) for x in rpy]}}
    lim = {}
    if lower is not None:
        lim.update(lower=round(float(lower), 6), upper=round(float(upper), 6))
    if velocity is not None:
        lim["velocity"] = round(float(velocity), 6)
    if lim:
        j["limit"] = lim
    return j


def _world(bodies, q=None):
    """按父子链把各连杆网格放到世界坐标（零位或给定关节值），缩略图用（毫米）"""
    import trimesh
    T = {}
    out = []
    for b in bodies:
        M = np.eye(4)
        w, x, y, z = b["quat"]
        M[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
        M[:3, 3] = b["pos"]
        if q and b["name"] in q:
            M = M @ q[b["name"]]
        T[b["name"]] = (T[b["parent"]] if b["parent"] else np.eye(4)) @ M
        if b["mesh"] is not None:
            out.append(b["mesh"].copy().apply_transform(T[b["name"]]))
    return trimesh.util.concatenate(out).apply_scale(1000.0)


def _urdf(name, bodies, joints, visuals):
    """简单 URDF：每个连杆一个 link（几何用基本形体），关节照关节表。visuals: 连杆名 → [(xml 几何, xyz, rpy)]"""
    out = ['<?xml version="1.0"?>', '<robot name="{}">'.format(name)]
    for b in bodies:
        out.append('  <link name="{}">'.format(b["name"]))
        for geo, xyz, rpy in visuals.get(b["name"], []):
            out.append('    <visual><origin xyz="{}" rpy="{}"/><geometry>{}</geometry></visual>'.format(
                " ".join("%.5g" % v for v in xyz), " ".join("%.5g" % v for v in rpy), geo))
        out.append("  </link>")
    for j in joints:
        out.append('  <joint name="{}" type="{}">'.format(j["name"], j["type"]))
        out.append('    <parent link="{}"/><child link="{}"/>'.format(j["parent"], j["child"]))
        out.append('    <origin xyz="{}" rpy="{}"/>'.format(" ".join("%.6g" % v for v in j["origin"]["xyz"]),
                                                            " ".join("%.6g" % v for v in j["origin"]["rpy"])))
        if j["type"] != "fixed":
            out.append('    <axis xyz="{}"/>'.format(" ".join("%g" % v for v in j["axis"])))
        lim = j.get("limit") or {}
        if j["type"] in ("revolute", "prismatic"):
            out.append('    <limit lower="{}" upper="{}" effort="100" velocity="{}"/>'.format(
                lim.get("lower", 0), lim.get("upper", 0), lim.get("velocity", 1)))
        out.append("  </joint>")
    out.append("</robot>")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------- SCARA
def scara(p):
    H, L1, L2, S, r = p["column_height_m"], p["arm1_m"], p["arm2_m"], p["stroke_m"], p["arm_radius_m"]
    quill = S + 0.08
    bodies = [
        _body("base", None, [0, 0, 0], _cat(_cyl(1.6 * r, H, GREY, center=(0, 0, H / 2)), _box([0.22, 0.22, 0.02], DARK, (0, 0, 0.01)))),
        _body("arm1", "base", [0, 0, H], _cat(_cyl(1.3 * r, 1.4 * r, BLUE), _box([L1, 1.6 * r, 0.9 * r], GREY, (L1 / 2, 0, 0)))),
        _body("arm2", "arm1", [L1, 0, 0], _cat(_cyl(1.1 * r, 1.4 * r, BLUE, center=(0, 0, 1.2 * r)),
                                                _box([L2, 1.4 * r, 0.8 * r], GREY, (L2 / 2, 0, 1.2 * r)))),
        _body("quill", "arm2", [L2, 0, 1.2 * r], _cyl(0.35 * r, quill, DARK, center=(0, 0, -quill / 2 + 0.6 * r))),
        _body("tool", "quill", [0, 0, -quill + 0.6 * r], _cat(_cyl(0.8 * r, 0.25 * r, YEL, center=(0, 0, -0.125 * r)),
                                                             _box([0.04, 0.012, 0.03], DARK, (0.012, 0, -0.035)),
                                                             _box([0.04, 0.012, 0.03], DARK, (-0.012, 0, -0.035)))),
    ]
    joints = [
        _joint("J1", "revolute", "base", "arm1", [0, 0, H], [0, 0, 1], lower=-math.radians(140), upper=math.radians(140), velocity=math.radians(420)),
        _joint("J2", "revolute", "arm1", "arm2", [L1, 0, 0], [0, 0, 1], lower=-math.radians(145), upper=math.radians(145), velocity=math.radians(720)),
        _joint("J3", "prismatic", "arm2", "quill", [L2, 0, 1.2 * r], [0, 0, -1], lower=0, upper=S, velocity=1.1),
        _joint("J4", "revolute", "quill", "tool", [0, 0, -quill + 0.6 * r], [0, 0, 1], lower=-2 * math.pi, upper=2 * math.pi, velocity=math.radians(2000)),
    ]
    rest = {"J1": 0.0, "J2": round(math.radians(60), 6), "J3": round(S / 2, 6), "J4": 0.0}
    vis = {"base": [('<cylinder radius="{:.4g}" length="{:.4g}"/>'.format(1.6 * r, H), (0, 0, H / 2), (0, 0, 0))],
           "arm1": [('<box size="{:.4g} {:.4g} {:.4g}"/>'.format(L1, 1.6 * r, 0.9 * r), (L1 / 2, 0, 0), (0, 0, 0))],
           "arm2": [('<box size="{:.4g} {:.4g} {:.4g}"/>'.format(L2, 1.4 * r, 0.8 * r), (L2 / 2, 0, 1.2 * r), (0, 0, 0))],
           "quill": [('<cylinder radius="{:.4g}" length="{:.4g}"/>'.format(0.35 * r, quill), (0, 0, -quill / 2 + 0.6 * r), (0, 0, 0))],
           "tool": [('<cylinder radius="{:.4g}" length="{:.4g}"/>'.format(0.8 * r, 0.25 * r), (0, 0, -0.125 * r), (0, 0, 0))]}
    q = {"arm2": _hom(_Rz(rest["J2"]))}
    robot = {"type": "scara", "dof": 4, "links": [{"name": b["name"], "node": b["name"], "mass_kg": None} for b in bodies],
             "joints": joints, "rest": rest, "rest_source": "问渠默认姿态（肘部 60°、丝杠中位）",
             "tool": {"parent": "tool", "xyz": [0, 0, -0.05]},
             "kinematics": {"type": "scara", "arm1_m": L1, "arm2_m": L2, "column_height_m": H, "stroke_m": S,
                            "workspace": {"r_min_m": round(abs(L1 - L2), 4), "r_max_m": round(L1 + L2, 4)}}}
    return {"bodies": bodies, "world": _world(bodies, q), "robot": robot, "urdf": _urdf("wq_scara", bodies, joints, vis)}


def _hom(R, t=(0, 0, 0)):
    M = np.eye(4)
    M[:3, :3], M[:3, 3] = R, t
    return M


def scara_fk(p, q):
    """末端（工具点）位置：x = L1 cos q1 + L2 cos(q1+q2)，y 同理，z = H + 抬高 - 丝杠下降"""
    L1, L2 = p["arm1_m"], p["arm2_m"]
    return np.array([L1 * math.cos(q[0]) + L2 * math.cos(q[0] + q[1]), L1 * math.sin(q[0]) + L2 * math.sin(q[0] + q[1])])


# ---------------------------------------------------------------- Delta
PHI = [0.0, 2 * math.pi / 3, 4 * math.pi / 3]


def delta_ik(p, P):
    """动平台中心 P=(x,y,z) → 三个主动臂摆角 θ（向下为正，弧度）；无解返回 None。肘部取外翻解。"""
    R, r, L, l = p["base_radius_m"], p["platform_radius_m"], p["upper_arm_m"], p["lower_arm_m"]
    out = []
    for phi in PHI:
        x, y, z = _Rz(-phi) @ np.asarray(P, float)
        a = x + r - R
        K = (a * a + y * y + z * z + L * L - l * l) / (2 * L)
        A, B, C = -a, z, -K
        n = math.hypot(A, B)
        if n < 1e-12 or abs(C / n) > 1:
            return None
        base, d = math.atan2(B, A), math.acos(C / n)
        cands = [base + d, base - d]
        th = max(cands, key=lambda t: math.cos(t))          # 肘部在外侧
        out.append(math.atan2(math.sin(th), math.cos(th)))
    return out


def delta_points(p, P, th):
    """各臂的肩、肘、平台铰点（世界坐标）"""
    R, r, L = p["base_radius_m"], p["platform_radius_m"], p["upper_arm_m"]
    pts = []
    for phi, t in zip(PHI, th):
        Rz = _Rz(phi)
        S = Rz @ np.array([R, 0, 0])
        E = Rz @ np.array([R + L * math.cos(t), 0, -L * math.sin(t)])
        W = np.asarray(P, float) + Rz @ np.array([r, 0, 0])
        pts.append((S, E, W))
    return pts


def _align_z(v):
    """把局部 z 轴转到方向 v 的旋转矩阵"""
    v = v / np.linalg.norm(v)
    z = np.array([0, 0, 1.0])
    ax = np.cross(z, v)
    s, c = np.linalg.norm(ax), float(np.dot(z, v))
    if s < 1e-12:
        return np.eye(3) if c > 0 else np.diag([1, -1, -1.0])
    k = ax / s
    Kx = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    ang = math.atan2(s, c)
    return np.eye(3) + math.sin(ang) * Kx + (1 - math.cos(ang)) * Kx @ Kx


def delta(p):
    R, r, L, l, rr = p["base_radius_m"], p["platform_radius_m"], p["upper_arm_m"], p["lower_arm_m"], p["rod_radius_m"]
    gap = p["parallelogram_width_m"]
    P0 = [0, 0, p["path_z_m"]]
    th0 = delta_ik(p, P0)
    base = _cat(_cyl(R * 1.35, 0.03, GREY, center=(0, 0, 0.03)),
                *[_cyl(0.035, 0.07, BLUE, axis="y", center=tuple(_Rz(phi) @ np.array([R, 0, 0])))
                  for phi in PHI])
    bodies = [_body("base", None, [0, 0, 0], base)]
    joints, members = [], [{"id": "base", "name": {"zh": "静平台（机架）", "en": "Base (ground)"}, "node": "base", "ground": True}]
    # 主动臂：在关节表里（绕切向轴摆动），网格沿局部 +x
    for i, phi in enumerate(PHI, start=1):
        S = _Rz(phi) @ np.array([R, 0, 0])
        mesh = _cat(_box([L, 2 * rr * 1.6, 2 * rr * 1.6], GREY, (L / 2, 0, 0)), _cyl(rr * 2.2, gap + 2 * rr, DARK, axis="y", center=(L, 0, 0)))
        bodies.append(_body("upper{}".format(i), "base", S, mesh, _Rz(phi)))
        joints.append(_joint("J{}".format(i), "revolute", "base", "upper{}".format(i), S, [0, 1, 0], rpy=(0, 0, phi),
                             lower=-math.radians(40), upper=math.radians(90), velocity=math.radians(600)))
        members.append({"id": "upper{}".format(i), "name": {"zh": "主动臂 {}".format(i), "en": "Upper arm {}".format(i)}, "node": "upper{}".format(i)})
    # 从动臂（两根平行杆）与动平台：机构坐标系下的独立节点，位姿由运动表给出
    for i, phi in enumerate(PHI, start=1):
        rods = _cat(*[_cyl(rr, l, GREY, center=tuple(s * gap / 2 * np.array([1, 0, 0]))) for s in (-1, 1)])
        bodies.append(_body("lower{}".format(i), None, [0, 0, 0], rods))
        members.append({"id": "lower{}".format(i), "name": {"zh": "从动臂 {}（平行四边形）".format(i), "en": "Lower arm {} (parallelogram)".format(i)},
                        "node": "lower{}".format(i)})
    plat = _cat(_cyl(r * 1.25, 0.02, BLUE), _cyl(0.012, 0.05, YEL, center=(0, 0, -0.035)))
    bodies.append(_body("platform", None, [0, 0, 0], plat))
    members.append({"id": "platform", "name": {"zh": "动平台", "en": "Moving platform"}, "node": "platform"})

    poses = delta_poses(p, P0, th0)
    for b in bodies:
        if b["name"] in poses and b["parent"] is None and b["name"] != "base":
            pos, R_ = poses[b["name"]]
            b["pos"], b["quat"] = [float(x) for x in pos], _quat_from_R(R_)
    # 运动表：动平台沿水平圆（半径 path_radius_m，高度 path_z_m）走一圈，每 5° 一行
    header, rows = ["input"], []
    ids = [m["id"] for m in members if not m.get("ground")]
    for mid in ids:
        header += ["{}.{}".format(mid, k) for k in ("x_m", "y_m", "z_m", "qx", "qy", "qz", "qw")]
    for deg in range(0, 360, 5):
        a = math.radians(deg)
        P = [p["path_radius_m"] * math.cos(a), p["path_radius_m"] * math.sin(a), p["path_z_m"]]
        th = delta_ik(p, P)
        if th is None:
            continue
        ps = delta_poses(p, P, th)
        row = [deg]
        for mid in ids:
            pos, R_ = ps[mid]
            w, x, y, z = _quat_from_R(R_)
            row += [round(float(v), 6) for v in pos] + [round(x, 6), round(y, 6), round(z, 6), round(w, 6)]
        rows.append(row)
    robot = {"type": "delta", "dof": 3, "links": [{"name": b["name"], "node": b["name"], "mass_kg": None} for b in bodies],
             "joints": joints, "rest": {"J{}".format(i + 1): round(t, 6) for i, t in enumerate(th0)},
             "rest_source": "动平台在工作区中心（z = {} m）".format(p["path_z_m"]),
             "parallel": {"type": "delta", "actuated": ["J1", "J2", "J3"],
                          "params": {k: p[k] for k in ("base_radius_m", "platform_radius_m", "upper_arm_m", "lower_arm_m")},
                          "note": "闭链：只拖主动臂不能保持闭合；看运动请用运动表（motion.csv），或按 params 自己算逆运动学"}}
    mech = {"dof": 3, "members": members,
            "input": {"member": "platform", "type": "path", "unit": "deg", "range": [0, 355], "step": 5,
                      "path": {"zh": "动平台沿水平圆走一圈：半径 {} m，高度 z = {} m".format(p["path_radius_m"], p["path_z_m"]),
                               "en": "Platform traces a horizontal circle, r = {} m at z = {} m".format(p["path_radius_m"], p["path_z_m"])}},
             "motion": "motion.csv"}
    world = []
    for b in bodies:
        M = np.eye(4)
        if b["name"] in poses:
            pos, R_ = poses[b["name"]]
            M[:3, :3], M[:3, 3] = R_, pos
        world.append(b["mesh"].copy().apply_transform(M))
    import trimesh
    return {"bodies": bodies, "world": trimesh.util.concatenate(world).apply_scale(1000.0), "robot": robot,
            "mechanism": mech, "motion": (header, rows)}


def delta_poses(p, P, th):
    """机构坐标系下各活动构件的位姿 {id: (位置, 旋转矩阵)}"""
    out = {}
    for i, (phi, t, (S, E, W)) in enumerate(zip(PHI, th, delta_points(p, P, th)), start=1):
        out["upper{}".format(i)] = (S, _Rz(phi) @ _Ry(t))
        d = W - E
        Rl = _align_z(d)
        # 两根平行杆的连线保持在切向（平行四边形的特点）：把局部 x 轴转到切向
        tang = _Rz(phi) @ np.array([0, 1.0, 0])
        xl = Rl[:, 0]
        tp = tang - np.dot(tang, Rl[:, 2]) * Rl[:, 2]
        if np.linalg.norm(tp) > 1e-9:
            tp /= np.linalg.norm(tp)
            ang = math.atan2(np.dot(np.cross(xl, tp), Rl[:, 2]), np.dot(xl, tp))
            Rl = Rl @ _Rz(ang)
        out["lower{}".format(i)] = ((E + W) / 2, Rl)
    out["platform"] = (np.asarray(P, float), np.eye(3))
    return out


# ---------------------------------------------------------------- 差速小车
def diff_cart(p):
    rw, track, Lc, Wc, Hc = p["wheel_radius_m"], p["track_m"], p["chassis_length_m"], p["chassis_width_m"], p["chassis_height_m"]
    ww = 0.025
    chassis = _cat(_box([Lc, Wc, Hc], BLUE, (-Lc * 0.15, 0, Hc / 2)),
                   _cyl(0.018, 0.018, DARK, center=(-Lc * 0.6, 0, -rw + 0.018 + 0.009)),
                   _box([0.06, 0.04, 0.03], YEL, (Lc * 0.2, 0, Hc + 0.015)))
    wheel = lambda: _cat(_cyl(rw, ww, DARK, axis="y"), _cyl(rw * 0.45, ww * 1.05, GREY, axis="y"))  # noqa: E731
    bodies = [_body("chassis", None, [0, 0, rw], chassis),
              _body("left_wheel", "chassis", [0, track / 2, 0], wheel()),
              _body("right_wheel", "chassis", [0, -track / 2, 0], wheel())]
    joints = [_joint("left_wheel_joint", "continuous", "chassis", "left_wheel", [0, track / 2, 0], [0, 1, 0], velocity=p["wheel_speed_rad_s"]),
              _joint("right_wheel_joint", "continuous", "chassis", "right_wheel", [0, -track / 2, 0], [0, 1, 0], velocity=p["wheel_speed_rad_s"])]
    vis = {"chassis": [('<box size="{:.4g} {:.4g} {:.4g}"/>'.format(Lc, Wc, Hc), (-Lc * 0.15, 0, Hc / 2), (0, 0, 0))],
           "left_wheel": [('<cylinder radius="{:.4g}" length="{:.4g}"/>'.format(rw, ww), (0, 0, 0), (math.pi / 2, 0, 0))],
           "right_wheel": [('<cylinder radius="{:.4g}" length="{:.4g}"/>'.format(rw, ww), (0, 0, 0), (math.pi / 2, 0, 0))]}
    robot = {"type": "mobile", "dof": 2, "links": [{"name": b["name"], "node": b["name"], "mass_kg": None} for b in bodies],
             "joints": joints,
             "kinematics": {"type": "differential_drive", "wheel_radius_m": rw, "track_m": track,
                            "wheels": {"left": "left_wheel_joint", "right": "right_wheel_joint"},
                            "formula": {"zh": "v = r(ωR + ωL)/2，ω = r(ωR − ωL)/b（r 轮半径，b 轮距）",
                                        "en": "v = r(wR + wL)/2, w = r(wR - wL)/b"}}}
    return {"bodies": bodies, "world": _world(bodies), "robot": robot, "urdf": _urdf("wq_diff_cart", bodies, joints, vis)}


def diff_cart_twist(p, wl, wr):
    """轮速 → 车体线速度 v（m/s）与角速度 ω（rad/s）"""
    r, b = p["wheel_radius_m"], p["track_m"]
    return r * (wr + wl) / 2, r * (wr - wl) / b


BUILDERS = {"scara": scara, "delta": delta, "diff_cart": diff_cart}


def params_of(entry, row=None):
    p = dict(entry.get("defaults") or {})
    for k, v in (row or {}).items():
        if k in p and v not in (None, ""):
            p[k] = float(v)
    return p


def build(entry, row):
    kind = entry["model"]["engine"].split(":")[1]
    return [("__scene__", BUILDERS[kind](params_of(entry, row)))]
