# -*- coding: utf-8 -*-
"""第 5 轮第 6 步：自建直角坐标、两连杆、倒立摆小车、Stewart——正/逆运动学、动力学线性化、并联闭链与运动表。"""
import math
import xml.etree.ElementTree as ET

import numpy as np
import pytest

import wqlib
from test_wq_robots import chain, part

trimesh = pytest.importorskip("trimesh")
from generators import b_wq  # noqa: E402


def test_cartesian_fk_matches_node_chain():
    e, pt = part("B-CRT-WQ3")
    p = b_wq.params_of(e)
    assert [j["type"] for j in pt["robot"]["joints"]] == ["prismatic"] * 3
    rng = np.random.default_rng(1)
    for _ in range(10):
        q = [rng.uniform(0, p["stroke_x_m"]), rng.uniform(0, p["stroke_y_m"]), rng.uniform(0, p["stroke_z_m"])]
        T = chain(pt, dict(zip(["J1", "J2", "J3"], q)))
        tool = T["ram"] @ np.array([0, 0, pt["robot"]["tool"]["xyz"][2], 1.0])
        assert np.allclose(tool[:3], b_wq.cartesian_fk(p, q), atol=1e-9)
    assert {j.get("name") for j in ET.fromstring(pt["urdf"]).findall("joint")} == {"J1", "J2", "J3"}


def test_planar_2r_fk_ik_both_elbows():
    e, pt = part("B-EDU-2R")
    p = b_wq.params_of(e)
    rng = np.random.default_rng(2)
    for _ in range(20):
        q = [rng.uniform(-2.5, 2.5), rng.uniform(0.1, 2.6) * rng.choice([-1, 1])]
        T = chain(pt, {"J1": q[0], "J2": q[1]})
        tip = T["link2"] @ np.array([p["link2_m"], 0, 0, 1.0])
        x, z = b_wq.planar_2r_fk(p, q)
        assert tip[0] == pytest.approx(x, abs=1e-9) and tip[2] == pytest.approx(z, abs=1e-9) and abs(tip[1]) < 1e-9
        sol = b_wq.planar_2r_ik(p, x, z, elbow_up=q[1] < 0)               # 同一组肘部解
        assert np.allclose(b_wq.planar_2r_fk(p, sol), [x, z], atol=1e-9)
        assert sol[1] == pytest.approx(q[1], abs=1e-9)
    assert b_wq.planar_2r_ik(p, p["link1_m"] + p["link2_m"] + 0.01, p["base_height_m"]) is None


def test_cart_pole_linearization_matches_nonlinear():
    e, pt = part("B-EDU-CARTPOLE")
    p = b_wq.params_of(e)
    dyn = pt["robot"]["dynamics"]
    A, B = np.array(dyn["linearized"]["A"]), np.array(dyn["linearized"]["B"])
    h = 1e-6
    xdd_th, thdd_th = [(a - b) / (2 * h) for a, b in zip(b_wq.cart_pole_accel(p, h, 0, 0), b_wq.cart_pole_accel(p, -h, 0, 0))]
    xdd_F, thdd_F = [(a - b) / (2 * h) for a, b in zip(b_wq.cart_pole_accel(p, 0, 0, h), b_wq.cart_pole_accel(p, 0, 0, -h))]
    assert A[1, 2] == pytest.approx(xdd_th, rel=1e-4) and A[3, 2] == pytest.approx(thdd_th, rel=1e-4)
    assert B[1, 0] == pytest.approx(xdd_F, rel=1e-4) and B[3, 0] == pytest.approx(thdd_F, rel=1e-4)
    assert A[3, 2] > 0                                                   # 竖直向上不稳定
    assert np.max(np.linalg.eigvals(A).real) > 0
    assert [l["mass_kg"] for l in pt["robot"]["links"]][1:] == [p["cart_mass_kg"], p["pole_mass_kg"]]


def test_stewart_ik_fk_and_motion_rows():
    e, pt = part("B-PAR-STEWART")
    p = b_wq.params_of(e)
    par = pt["robot"]["parallel"]
    header, rows = pt["motion"]
    assert len(rows) == 72 and header[0] == "input"
    col = {h: i for i, h in enumerate(header)}
    B, P = b_wq.stewart_anchors(p)
    for r in rows[::7]:
        pose = b_wq.stewart_path(p, r[0])
        L = b_wq.stewart_ik(p, pose)
        assert par["leg_length_m"]["min"] - 1e-9 <= min(L) and max(L) <= par["leg_length_m"]["max"] + 1e-9
        back = b_wq.stewart_fk(p, L, guess=[0, 0, p["home_height_m"], 0, 0, 0])      # 正解：由腿长迭代回位姿
        assert np.allclose(back, pose, atol=1e-8)
        for i in range(1, 7):                                            # 运动表：缸筒在下铰点、活塞杆在上铰点，同一方向
            c = np.array([r[col["cyl{}.{}".format(i, k)]] for k in ("x_m", "y_m", "z_m")])
            d = np.array([r[col["rod{}.{}".format(i, k)]] for k in ("x_m", "y_m", "z_m")])
            assert np.allclose(c, B[i - 1], atol=1e-6)
            assert np.linalg.norm(d - c) == pytest.approx(L[i - 1], abs=1e-5)
    assert par["actuated"] == ["J{}".format(i) for i in range(1, 7)] and pt["robot"]["dof"] == 6
