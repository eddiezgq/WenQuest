# -*- coding: utf-8 -*-
"""问渠自建机器人（第 5 轮 P9、P12）：参数化生成 glTF（按连杆/构件分节点）、关节表（R4）、URDF；并联机构另出运动表（R5）。

engine: wqrobot:<型式>，参数取条目的 defaults（米、弧度），范围见 ranges：
    scara      SCARA：J1、J2 绕竖直轴转，J3 丝杠升降，J4 末端转
    delta      Delta 并联：三个主动臂各绕切向轴摆动；从动臂（平行四边形）与动平台由运动表给出
    diff_cart  差速小车：两个驱动轮（连续转动）+ 万向轮
    cartesian  直角坐标（龙门）：X、Y、Z 三个移动关节            planar_2r 两连杆平面臂：竖直面内两个转动关节
    cart_pole  倒立摆小车：小车沿导轨移动 + 摆杆自由转动（带动力学参数与线性化模型）
    stewart    Stewart 六自由度并联平台：六根伸缩腿；腿与平台由运动表给出（第 5 轮第 6 步）
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


# ---------------------------------------------------------------- 直角坐标（龙门）
def cartesian(p):
    sx, sy, sz, H, b = p["stroke_x_m"], p["stroke_y_m"], p["stroke_z_m"], p["frame_height_m"], p["beam_m"]
    span = sy + 0.16                                      # 两根 X 梁的间距
    lx = sx + 0.2
    ram = sz + 0.12
    base = _cat(*[_box([lx, b, b], GREY, (0, s * span / 2, H)) for s in (-1, 1)],
                *[_box([b, b, H], DARK, (x, s * span / 2, H / 2)) for x in (-lx / 2 + b / 2, lx / 2 - b / 2) for s in (-1, 1)])
    bridge = _cat(_box([b * 1.4, span + b, b * 1.2], BLUE, (0, 0, 0)),
                  *[_box([b * 2, b * 1.2, b * 0.6], DARK, (0, s * span / 2, b * 0.9)) for s in (-1, 1)])
    carriage = _box([b * 2.2, b * 2.2, b * 1.6], YEL, (0, 0, 0.2 * b))
    zram = _cat(_box([b * 0.9, b * 0.9, ram], GREY, (0, 0, ram / 2 - 0.06)), _cyl(b * 0.5, 0.03, DARK, center=(0, 0, -0.075)))
    z0 = H + b * 1.4                                       # 横梁顶面
    bodies = [_body("base", None, [0, 0, 0], base),
              _body("bridge", "base", [-sx / 2, 0, z0], bridge),
              _body("carriage", "bridge", [0, -sy / 2, b * 0.6], carriage),
              _body("ram", "carriage", [0, 0, 0], zram)]
    joints = [_joint("J1", "prismatic", "base", "bridge", [-sx / 2, 0, z0], [1, 0, 0], lower=0, upper=sx, velocity=1.0),
              _joint("J2", "prismatic", "bridge", "carriage", [0, -sy / 2, b * 0.6], [0, 1, 0], lower=0, upper=sy, velocity=1.0),
              _joint("J3", "prismatic", "carriage", "ram", [0, 0, 0], [0, 0, -1], lower=0, upper=sz, velocity=0.5)]
    tool_z = -0.09
    rest = {"J1": round(sx / 2, 6), "J2": round(sy / 2, 6), "J3": 0.0}
    vis = {"base": [('<box size="{:.4g} {:.4g} {:.4g}"/>'.format(lx, b, b), (0, s * span / 2, H), (0, 0, 0)) for s in (-1, 1)],
           "bridge": [('<box size="{:.4g} {:.4g} {:.4g}"/>'.format(b * 1.4, span + b, b * 1.2), (0, 0, 0), (0, 0, 0))],
           "carriage": [('<box size="{:.4g} {:.4g} {:.4g}"/>'.format(b * 2.2, b * 2.2, b * 1.6), (0, 0, 0.2 * b), (0, 0, 0))],
           "ram": [('<box size="{:.4g} {:.4g} {:.4g}"/>'.format(b * 0.9, b * 0.9, ram), (0, 0, ram / 2 - 0.06), (0, 0, 0))]}
    robot = {"type": "cartesian", "dof": 3, "links": [{"name": x["name"], "node": x["name"], "mass_kg": None} for x in bodies],
             "joints": joints, "rest": rest, "rest_source": "问渠默认姿态（X、Y 行程中点，Z 最高）",
             "tool": {"parent": "ram", "xyz": [0, 0, tool_z]},
             "kinematics": {"type": "cartesian", "formula": {"zh": "x = −Sx/2 + q1，y = −Sy/2 + q2，z = z0 − q3（三个关节互不耦合）",
                                                            "en": "x = -Sx/2 + q1, y = -Sy/2 + q2, z = z0 - q3"},
                            "z0_m": round(z0 + b * 0.6 + tool_z, 6),
                            "workspace": {"x_m": [-sx / 2, sx / 2], "y_m": [-sy / 2, sy / 2], "z_m": [round(z0 + b * 0.6 + tool_z - sz, 6), round(z0 + b * 0.6 + tool_z, 6)]}}}
    q = {"bridge": _hom(np.eye(3), (rest["J1"], 0, 0)), "carriage": _hom(np.eye(3), (0, rest["J2"], 0))}
    return {"bodies": bodies, "world": _world(bodies, q), "robot": robot, "urdf": _urdf("wq_cartesian", bodies, joints, vis)}


def cartesian_fk(p, q):
    k = cartesian(p)["robot"]["kinematics"]
    return np.array([-p["stroke_x_m"] / 2 + q[0], -p["stroke_y_m"] / 2 + q[1], k["z0_m"] - q[2]])


# ---------------------------------------------------------------- 两连杆平面臂（竖直面 XZ）
def planar_2r(p):
    L1, L2, h, r = p["link1_m"], p["link2_m"], p["base_height_m"], p["link_radius_m"]
    base = _cat(_box([0.16, 0.16, 0.02], DARK, (0, 0, 0.01)), _cyl(r * 1.4, h, GREY, center=(0, 0, h / 2)),
                _cyl(r * 1.5, r * 3, BLUE, axis="y", center=(0, 0, h)))
    l1 = _cat(_box([L1, r * 1.6, r * 1.6], GREY, (L1 / 2, r * 2.2, 0)), _cyl(r * 1.3, r * 2.4, BLUE, axis="y", center=(L1, r * 2.2, 0)))
    l2 = _cat(_box([L2, r * 1.4, r * 1.4], GREY, (L2 / 2, r * 4.2, 0)), _cyl(r * 0.9, r * 1.5, YEL, axis="y", center=(L2, r * 4.2, 0)))
    bodies = [_body("base", None, [0, 0, 0], base), _body("link1", "base", [0, 0, h], l1), _body("link2", "link1", [L1, 0, 0], l2)]
    joints = [_joint("J1", "revolute", "base", "link1", [0, 0, h], [0, -1, 0], lower=-math.radians(170), upper=math.radians(170), velocity=math.radians(180)),
              _joint("J2", "revolute", "link1", "link2", [L1, 0, 0], [0, -1, 0], lower=-math.radians(160), upper=math.radians(160), velocity=math.radians(180))]
    rest = {"J1": round(math.radians(45), 6), "J2": round(math.radians(-60), 6)}
    vis = {"link1": [('<box size="{:.4g} {:.4g} {:.4g}"/>'.format(L1, r * 1.6, r * 1.6), (L1 / 2, r * 2.2, 0), (0, 0, 0))],
           "link2": [('<box size="{:.4g} {:.4g} {:.4g}"/>'.format(L2, r * 1.4, r * 1.4), (L2 / 2, r * 4.2, 0), (0, 0, 0))]}
    robot = {"type": "planar_2r", "dof": 2, "links": [{"name": x["name"], "node": x["name"], "mass_kg": None} for x in bodies],
             "joints": joints, "rest": rest, "rest_source": "问渠默认姿态（J1 = 45°，J2 = −60°）",
             "tool": {"parent": "link2", "xyz": [L2, 0, 0]},
             "kinematics": {"type": "planar_2r", "link1_m": L1, "link2_m": L2, "base_height_m": h, "plane": "xz",
                            "formula": {"zh": "x = L1 cos q1 + L2 cos(q1+q2)，z = h + L1 sin q1 + L2 sin(q1+q2)；逆解 cos q2 = (x²+(z−h)²−L1²−L2²)/(2L1L2)，肘上、肘下两组解",
                                        "en": "x = L1 cos q1 + L2 cos(q1+q2), z = h + L1 sin q1 + L2 sin(q1+q2)"},
                            "workspace": {"r_min_m": round(abs(L1 - L2), 4), "r_max_m": round(L1 + L2, 4)}}}
    q = {"link1": _hom(_Ry(-rest["J1"])), "link2": _hom(_Ry(-rest["J2"]))}
    return {"bodies": bodies, "world": _world(bodies, q), "robot": robot, "urdf": _urdf("wq_planar_2r", bodies, joints, vis)}


def planar_2r_fk(p, q):
    L1, L2, h = p["link1_m"], p["link2_m"], p["base_height_m"]
    return np.array([L1 * math.cos(q[0]) + L2 * math.cos(q[0] + q[1]), h + L1 * math.sin(q[0]) + L2 * math.sin(q[0] + q[1])])


def planar_2r_ik(p, x, z, elbow_up=True):
    """末端 (x, z) → (q1, q2)；够不着返回 None。elbow_up：q2 < 0（肘部在上）"""
    L1, L2, h = p["link1_m"], p["link2_m"], p["base_height_m"]
    zz = z - h
    c2 = (x * x + zz * zz - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    if abs(c2) > 1:
        return None
    q2 = math.acos(c2) * (-1 if elbow_up else 1)
    q1 = math.atan2(zz, x) - math.atan2(L2 * math.sin(q2), L1 + L2 * math.cos(q2))
    return q1, q2


# ---------------------------------------------------------------- 倒立摆小车
def cart_pole_dynamics(p):
    """线性化模型（在摆杆竖直向上 θ = 0 处）：ẋ = A x + B F，状态 x = [位移, 速度, 摆角, 角速度]；摆杆为均质细杆"""
    M, m, L, g = p["cart_mass_kg"], p["pole_mass_kg"], p["pole_length_m"], 9.81
    l = L / 2
    I = m * L * L / 12
    den = (M + m) * (I + m * l * l) - (m * l) ** 2
    A = [[0, 1, 0, 0], [0, 0, -(m * l) ** 2 * g / den, 0], [0, 0, 0, 1], [0, 0, (M + m) * m * g * l / den, 0]]
    B = [[0], [(I + m * l * l) / den], [0], [-m * l / den]]
    return A, B


def cart_pole_accel(p, theta, dtheta, F):
    """非线性方程（θ 从竖直向上量，向 +x 倒为正）：返回 (ẍ, θ̈)"""
    M, m, L, g = p["cart_mass_kg"], p["pole_mass_kg"], p["pole_length_m"], 9.81
    l = L / 2
    I = m * L * L / 12
    s, c = math.sin(theta), math.cos(theta)
    a11, a12, a21, a22 = M + m, m * l * c, m * l * c, I + m * l * l          # 拉格朗日方程（质心在 x + l sinθ, l cosθ）
    b1, b2 = F + m * l * dtheta * dtheta * s, m * g * l * s
    det = a11 * a22 - a12 * a21
    return (b1 * a22 - a12 * b2) / det, (a11 * b2 - a21 * b1) / det


def cart_pole(p):
    Lr, Lp, h = p["rail_length_m"], p["pole_length_m"], p["rail_height_m"]
    cw = 0.12
    rail = _cat(_box([Lr, 0.04, 0.02], DARK, (0, 0, h)), *[_box([0.03, 0.08, h], GREY, (s * (Lr / 2 - 0.015), 0, h / 2)) for s in (-1, 1)])
    cart = _cat(_box([cw, 0.08, 0.05], BLUE, (0, 0, 0.035)), _cyl(0.012, 0.03, DARK, axis="y", center=(0, -0.055, 0.05)))
    pole = _cat(_cyl(0.008, Lp, YEL, center=(0, 0, Lp / 2)), _cyl(0.016, 0.02, GREY, axis="y"))
    bodies = [_body("rail", None, [0, 0, 0], rail), _body("cart", "rail", [0, 0, h + 0.01], cart), _body("pole", "cart", [0, -0.055, 0.05], pole)]
    joints = [_joint("J1", "prismatic", "rail", "cart", [0, 0, h + 0.01], [1, 0, 0], lower=-(Lr / 2 - cw), upper=Lr / 2 - cw, velocity=2.0),
              _joint("J2", "continuous", "cart", "pole", [0, -0.055, 0.05], [0, 1, 0])]
    A, B = cart_pole_dynamics(p)
    robot = {"type": "cart_pole", "dof": 2,
             "links": [{"name": "rail", "node": "rail", "mass_kg": None}, {"name": "cart", "node": "cart", "mass_kg": p["cart_mass_kg"]},
                       {"name": "pole", "node": "pole", "mass_kg": p["pole_mass_kg"]}],
             "joints": joints, "rest": {"J1": 0.0, "J2": round(math.radians(8), 6)}, "rest_source": "摆杆偏离竖直 8°（演示不稳定平衡）",
             "dynamics": {"type": "cart_pole", "cart_mass_kg": p["cart_mass_kg"], "pole_mass_kg": p["pole_mass_kg"],
                          "pole_length_m": Lp, "pole": "均质细杆，质心在杆长一半处", "g_m_s2": 9.81,
                          "equations": {"zh": "(M+m)ẍ + m·l·cosθ·θ̈ − m·l·θ̇²·sinθ = F；m·l·cosθ·ẍ + (I+m·l²)·θ̈ − m·g·l·sinθ = 0（θ 从竖直向上量、向 +x 倒为正，l = L/2，I = mL²/12）",
                                        "en": "(M+m)x'' + m l cos(th) th'' - m l th'^2 sin(th) = F; m l cos(th) x'' + (I + m l^2) th'' - m g l sin(th) = 0"},
                          "linearized": {"state": ["x_m", "v_m_s", "theta_rad", "omega_rad_s"], "input": "F_N",
                                         "A": [[round(v, 6) for v in r] for r in A], "B": [[round(v[0], 6)] for v in B]}}}
    vis = {"cart": [('<box size="{:.4g} 0.08 0.05"/>'.format(cw), (0, 0, 0.035), (0, 0, 0))],
           "pole": [('<cylinder radius="0.008" length="{:.4g}"/>'.format(Lp), (0, 0, Lp / 2), (0, 0, 0))]}
    q = {"pole": _hom(_Ry(math.radians(8)))}
    return {"bodies": bodies, "world": _world(bodies, q), "robot": robot, "urdf": _urdf("wq_cart_pole", bodies, joints, vis)}


# ---------------------------------------------------------------- Stewart 平台
def stewart_anchors(p):
    """基座铰点 B[i] 与平台铰点 P[i]（平台坐标系），按 120° 三组、每组两点，腿两两交叉"""
    Rb, Rp = p["base_radius_m"], p["platform_radius_m"]
    ab, ap = math.radians(p["base_half_angle_deg"]), math.radians(p["platform_half_angle_deg"])
    B, P = [], []
    for k in range(3):
        c = math.radians(120 * k)
        for s in (-1, 1):
            B.append(np.array([Rb * math.cos(c + s * ab), Rb * math.sin(c + s * ab), 0.0]))
            cp = c + s * (math.radians(60) - ap)
            P.append(np.array([Rp * math.cos(cp), Rp * math.sin(cp), 0.0]))
    return B, P


def _rpy_R(roll, pitch, yaw):
    cr, sr, cp, sp, cy, sy = math.cos(roll), math.sin(roll), math.cos(pitch), math.sin(pitch), math.cos(yaw), math.sin(yaw)
    return np.array([[cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
                     [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr], [-sp, cp * sr, cp * cr]])


def stewart_ik(p, pose):
    """平台位姿 (x, y, z, roll, pitch, yaw) → 六根腿长（两铰点距离）"""
    B, P = stewart_anchors(p)
    R = _rpy_R(*pose[3:])
    t = np.asarray(pose[:3], float)
    return [float(np.linalg.norm(t + R @ Pi - Bi)) for Bi, Pi in zip(B, P)]


def stewart_fk(p, lengths, guess=None, iters=50):
    """六根腿长 → 平台位姿（牛顿迭代，从 guess 或原位出发）"""
    x = np.array(guess if guess is not None else [0, 0, p["home_height_m"], 0, 0, 0], float)
    Lt = np.asarray(lengths, float)
    for _ in range(iters):
        f = np.array(stewart_ik(p, x)) - Lt
        if np.max(np.abs(f)) < 1e-12:
            break
        J = np.zeros((6, 6))
        for k in range(6):
            dx = np.zeros(6)
            dx[k] = 1e-7
            J[:, k] = (np.array(stewart_ik(p, x + dx)) - np.array(stewart_ik(p, x - dx))) / 2e-7
        x -= np.linalg.solve(J, f)
    return x


def stewart_path(p, deg):
    a = math.radians(deg)
    A, T = p["demo_amplitude_m"], math.radians(p["demo_tilt_deg"])
    return [A * math.cos(a), A * math.sin(a), p["home_height_m"] + 0.5 * A * math.sin(2 * a), T * math.sin(a), T * math.cos(a), 0.0]


def stewart_poses(p, pose):
    B, P = stewart_anchors(p)
    R = _rpy_R(*pose[3:])
    t = np.asarray(pose[:3], float)
    out = {"platform": (t, R)}
    for i, (Bi, Pi) in enumerate(zip(B, P), start=1):
        Pw = t + R @ Pi
        Ru = _align_z(Pw - Bi)
        out["cyl{}".format(i)] = (Bi, Ru)                  # 缸筒：原点在下铰点，沿腿方向
        out["rod{}".format(i)] = (Pw, Ru)                  # 活塞杆：原点在上铰点，向下伸进缸筒
    return out


def stewart(p):
    B, P = stewart_anchors(p)
    home = [0, 0, p["home_height_m"], 0, 0, 0]
    L0 = stewart_ik(p, home)
    lmin, lmax = min(L0) - p["leg_stroke_m"] / 2, max(L0) + p["leg_stroke_m"] / 2
    cyl_len, rod_len = 0.62 * lmin, 0.62 * lmin
    base = _cat(_cyl(p["base_radius_m"] * 1.15, 0.025, GREY, center=(0, 0, -0.0125)),
                *[_cyl(0.018, 0.02, DARK, center=tuple(Bi + np.array([0, 0, 0.01]))) for Bi in B])
    bodies = [_body("base", None, [0, 0, 0], base)]
    members = [{"id": "base", "name": {"zh": "基座（机架）", "en": "Base (ground)"}, "node": "base", "ground": True}]
    joints = []
    for i in range(1, 7):
        bodies.append(_body("cyl{}".format(i), None, [0, 0, 0], _cyl(0.016, cyl_len, BLUE, center=(0, 0, cyl_len / 2))))
        bodies.append(_body("rod{}".format(i), None, [0, 0, 0], _cyl(0.009, rod_len, GREY, center=(0, 0, -rod_len / 2))))
        members += [{"id": "cyl{}".format(i), "name": {"zh": "腿 {} 缸筒".format(i), "en": "Leg {} cylinder".format(i)}, "node": "cyl{}".format(i)},
                    {"id": "rod{}".format(i), "name": {"zh": "腿 {} 活塞杆".format(i), "en": "Leg {} rod".format(i)}, "node": "rod{}".format(i)}]
        joints.append(_joint("J{}".format(i), "prismatic", "cyl{}".format(i), "rod{}".format(i), [0, 0, round(L0[i - 1], 6)], [0, 0, 1],
                             lower=-(L0[i - 1] - lmin), upper=lmax - L0[i - 1], velocity=0.2))
    plat = _cat(_cyl(p["platform_radius_m"] * 1.2, 0.02, BLUE, center=(0, 0, 0.012)), _box([0.05, 0.05, 0.03], YEL, (0, 0, 0.035)))
    bodies.append(_body("platform", None, [0, 0, 0], plat))
    members.append({"id": "platform", "name": {"zh": "动平台", "en": "Moving platform"}, "node": "platform"})
    poses = stewart_poses(p, home)
    for b in bodies:
        if b["name"] in poses:
            pos, R_ = poses[b["name"]]
            b["pos"], b["quat"] = [float(x) for x in pos], _quat_from_R(R_)
    header, rows = ["input"], []
    ids = [m["id"] for m in members if not m.get("ground")]
    for mid in ids:
        header += ["{}.{}".format(mid, k) for k in ("x_m", "y_m", "z_m", "qx", "qy", "qz", "qw")]
    for deg in range(0, 360, 5):
        pose = stewart_path(p, deg)
        Ls = stewart_ik(p, pose)
        if min(Ls) < lmin - 1e-9 or max(Ls) > lmax + 1e-9:
            continue
        ps = stewart_poses(p, pose)
        row = [deg]
        for mid in ids:
            pos, R_ = ps[mid]
            w, x, y, z = _quat_from_R(R_)
            row += [round(float(v), 6) for v in pos] + [round(x, 6), round(y, 6), round(z, 6), round(w, 6)]
        rows.append(row)
    robot = {"type": "stewart", "dof": 6, "links": [{"name": b["name"], "node": b["name"], "mass_kg": None} for b in bodies],
             "joints": joints, "rest": {"J{}".format(i): 0.0 for i in range(1, 7)}, "rest_source": "动平台在原位（高度 {} m、水平）".format(p["home_height_m"]),
             "parallel": {"type": "stewart", "actuated": ["J{}".format(i) for i in range(1, 7)],
                          "params": {k: p[k] for k in ("base_radius_m", "platform_radius_m", "base_half_angle_deg", "platform_half_angle_deg", "home_height_m")},
                          "leg_length_m": {"home": [round(x, 6) for x in L0], "min": round(lmin, 6), "max": round(lmax, 6)},
                          "anchors": {"base": [[round(float(v), 6) for v in b] for b in B], "platform": [[round(float(v), 6) for v in q] for q in P]},
                          "note": "六根腿长（铰点距离）由平台位姿直接算出（逆运动学）；由腿长求位姿（正运动学）要迭代。关节值 = 腿长 − 原位腿长"}}
    mech = {"dof": 6, "members": members,
            "input": {"member": "platform", "type": "path", "unit": "deg", "range": [0, 355], "step": 5,
                      "path": {"zh": "动平台画圆（半径 {} m）同时上下起伏、绕两轴各倾斜 ±{}°".format(p["demo_amplitude_m"], p["demo_tilt_deg"]),
                               "en": "Platform circles (r = {} m) while heaving and tilting ±{}°".format(p["demo_amplitude_m"], p["demo_tilt_deg"])}},
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


BUILDERS = {"scara": scara, "delta": delta, "diff_cart": diff_cart, "cartesian": cartesian, "planar_2r": planar_2r,
            "cart_pole": cart_pole, "stewart": stewart}


def params_of(entry, row=None):
    p = dict(entry.get("defaults") or {})
    for k, v in (row or {}).items():
        if k in p and v not in (None, ""):
            p[k] = float(v)
    return p


def build(entry, row):
    kind = entry["model"]["engine"].split(":")[1]
    return [("__scene__", BUILDERS[kind](params_of(entry, row)))]
