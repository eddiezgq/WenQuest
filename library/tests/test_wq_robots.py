# -*- coding: utf-8 -*-
"""第 5 轮 P12（学习平台 R8）：自建 SCARA、Delta、差速小车——运动学、闭链、运动表、URDF 与关节表一致。"""
import math
import xml.etree.ElementTree as ET

import numpy as np
import pytest

import wqlib

trimesh = pytest.importorskip("trimesh")
from generators import b_wq  # noqa: E402


def part(eid):
    e = next(x for x in wqlib.entries([eid]) if x["id"] == eid)
    return e, b_wq.build(e, wqlib.specs(e)[0])[0][1]


def _M(b):
    w, x, y, z = b["quat"]
    M = np.eye(4)
    M[:3, :3] = [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                 [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                 [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]
    M[:3, 3] = b["pos"]
    return M


def _joint_M(j, v):
    ax = np.array(j["axis"], float)
    M = np.eye(4)
    if j["type"] == "prismatic":
        M[:3, 3] = ax * v
    else:
        K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
        M[:3, :3] = np.eye(3) + math.sin(v) * K + (1 - math.cos(v)) * K @ K
    return M


def chain(pt, q):
    """按节点父子链 + 关节表（与网页、学习平台相同的算法）算各节点的世界位姿"""
    bodies = {b["name"]: b for b in pt["bodies"]}
    js = {j["child"]: j for j in pt["robot"]["joints"]}
    T = {}

    def w(n):
        if n not in T:
            b = bodies[n]
            M = _M(b)
            if n in js:
                M = M @ _joint_M(js[n], q.get(js[n]["name"], 0.0))
            T[n] = (w(b["parent"]) if b["parent"] else np.eye(4)) @ M
        return T[n]
    return {n: w(n) for n in bodies}


def test_scara_kinematics_and_urdf():
    e, pt = part("B-SCA-WQ4")
    p = b_wq.params_of(e)
    assert [j["type"] for j in pt["robot"]["joints"]] == ["revolute", "revolute", "prismatic", "revolute"]
    rng = np.random.default_rng(3)
    for _ in range(10):
        q = {"J1": rng.uniform(-2, 2), "J2": rng.uniform(-2, 2), "J3": rng.uniform(0, p["stroke_m"]), "J4": rng.uniform(-3, 3)}
        T = chain(pt, q)
        assert np.allclose(T["tool"][:2, 3], b_wq.scara_fk(p, [q["J1"], q["J2"]]), atol=1e-9)
        z0 = chain(pt, dict(q, J3=0))["tool"][2, 3]
        assert abs((z0 - T["tool"][2, 3]) - q["J3"]) < 1e-9            # 丝杠向下为正
    root = ET.fromstring(pt["urdf"])
    uj = {j.get("name"): j for j in root.findall("joint")}
    assert set(uj) == {"J1", "J2", "J3", "J4"} and uj["J3"].get("type") == "prismatic"
    assert len(root.findall("link")) == 5
    assert pt["robot"]["rest"]["J2"] == pytest.approx(math.radians(60), abs=1e-6)


def test_delta_closed_chain_in_every_motion_row():
    e, pt = part("B-PAR-DELTA")
    p = b_wq.params_of(e)
    header, rows = pt["motion"]
    assert len(rows) == 72 and header[0] == "input"
    L, l = p["upper_arm_m"], p["lower_arm_m"]
    for row in rows:
        v = dict(zip(header, row))
        P = np.array([v["platform.x_m"], v["platform.y_m"], v["platform.z_m"]])
        assert abs(P[2] - p["path_z_m"]) < 1e-9 and abs(np.hypot(P[0], P[1]) - p["path_radius_m"]) < 1e-6
        assert abs(v["platform.qw"]) == pytest.approx(1.0)                 # 动平台只平移
        th = b_wq.delta_ik(p, P)
        for i, (S, E, W) in enumerate(b_wq.delta_points(p, P, th), start=1):
            assert abs(np.linalg.norm(E - S) - L) < 1e-9
            assert abs(np.linalg.norm(W - E) - l) < 1e-6                # 从动臂长度不变 = 闭链闭合
            mid = np.array([v["lower%d.%s" % (i, k)] for k in ("x_m", "y_m", "z_m")])
            assert np.allclose(mid, (E + W) / 2, atol=2e-6)
    # 关节表里的主动臂摆角与逆运动学一致（rest = 工作区中心）
    th0 = b_wq.delta_ik(p, [0, 0, p["path_z_m"]])
    assert [pt["robot"]["rest"]["J%d" % i] for i in (1, 2, 3)] == pytest.approx(th0, abs=1e-6)
    T = chain(pt, pt["robot"]["rest"])
    for i, phi in enumerate(b_wq.PHI, start=1):            # 主动臂末端（局部 +x 方向 L 处）= 肘点
        E = (T["upper%d" % i] @ np.array([L, 0, 0, 1]))[:3]
        assert np.allclose(E, b_wq.delta_points(p, [0, 0, p["path_z_m"]], th0)[i - 1][1], atol=1e-6)
    assert pt["mechanism"]["motion"] == "motion.csv" and pt["robot"]["parallel"]["actuated"] == ["J1", "J2", "J3"]


def test_diff_cart():
    e, pt = part("B-EDU-DIFF")
    p = b_wq.params_of(e)
    assert {j["type"] for j in pt["robot"]["joints"]} == {"continuous"}
    v, w = b_wq.diff_cart_twist(p, 10, 10)
    assert v == pytest.approx(10 * p["wheel_radius_m"]) and w == 0
    v, w = b_wq.diff_cart_twist(p, -5, 5)
    assert v == 0 and w == pytest.approx(2 * 5 * p["wheel_radius_m"] / p["track_m"])
    T = chain(pt, {})
    assert T["left_wheel"][1, 3] == pytest.approx(p["track_m"] / 2) and T["left_wheel"][2, 3] == pytest.approx(p["wheel_radius_m"])
    ET.fromstring(pt["urdf"])
