# -*- coding: utf-8 -*-
"""第 5 轮第 6 步：C 部分 10 个机构——位置分析两种算法互核、闭环约束、传动比、运动表（R5）、WQR-105 与工厂数据一致。"""
import importlib.util
import math

import numpy as np
import pytest

import wqlib

trimesh = pytest.importorskip("trimesh")
from generators import c_mech  # noqa: E402

FACTORY_DATA = wqlib.ROOT.parent / "factory" / "factory" / "data.py"


def part(eid):
    e = next(x for x in wqlib.entries([eid]) if x["id"] == eid)
    return e, c_mech.params_of(e), c_mech.build(e, {})[0][1]


def table(pt):
    header, rows = pt["motion"]
    col = {h: i for i, h in enumerate(header)}
    return col, rows


def pos(col, r, mid):
    return np.array([r[col["{}.{}".format(mid, k)]] for k in ("x_m", "y_m", "z_m")])


def angle(col, r, mid):
    """绕 −Y 的转角（平面机构、齿轮）"""
    return -2 * math.atan2(r[col[mid + ".qy"]], r[col[mid + ".qw"]])


def unwrap(a):
    return np.unwrap(np.array(a))


def test_all_mechanisms_have_motion_and_members():
    es = [e for e in wqlib.entries(["C-"])]
    assert len(es) == 10
    for e in es:
        p = c_mech.params_of(e)
        pt = c_mech.build(e, {})[0][1]
        header, rows = pt["motion"]
        mech = pt["mechanism"]
        ids = [m["id"] for m in mech["members"] if not m.get("ground")]
        assert header == ["input"] + ["{}.{}".format(i, k) for i in ids for k in ("x_m", "y_m", "z_m", "qx", "qy", "qz", "qw")], e["id"]
        assert len(rows) >= 100 and mech["input"]["member"] in ids, e["id"]
        assert {b["name"] for b in pt["bodies"]} == {m["node"] for m in mech["members"]}
        for r in rows[:5]:
            for i in ids:
                q = [r[header.index(i + "." + k)] for k in ("qx", "qy", "qz", "qw")]
                assert abs(np.linalg.norm(q) - 1) < 1e-5


def test_four_bar_two_methods_and_closure():
    e, p, pt = part("C-LNK-4BAR")
    a, b, c, d = p["crank_m"], p["coupler_m"], p["rocker_m"], p["ground_m"]
    assert pt["mechanism"]["analysis"]["grashof"] and pt["mechanism"]["analysis"]["type"] == "曲柄摇杆"
    col, rows = table(pt)
    assert len(rows) == 180                                        # 曲柄整周可转
    for deg in range(0, 360, 7):
        A, B, th3, th4 = c_mech.four_bar_solve(p, math.radians(deg))
        assert np.linalg.norm(B - A) == pytest.approx(b, abs=1e-12) and np.linalg.norm(B - [d, 0]) == pytest.approx(c, abs=1e-12)
        f = c_mech.freudenstein_th4(p, math.radians(deg))                   # 弗洛伊登斯坦闭式解
        g = c_mech.freudenstein_th4(p, math.radians(deg), -1)
        assert min(abs(math.remainder(f - th4, 2 * math.pi)), abs(math.remainder(g - th4, 2 * math.pi))) < 1e-9
    for r in rows[::11]:                                            # 运动表：连杆起点 = 曲柄端点，摇杆在 O4
        th2 = angle(col, r, "crank")
        assert np.allclose(pos(col, r, "coupler")[[0, 2]], [a * math.cos(th2), a * math.sin(th2)], atol=1e-6)
        assert np.allclose(pos(col, r, "rocker")[[0, 2]], [d, 0], atol=1e-9)


def test_slider_crank_rod_length_and_stroke():
    e, p, pt = part("C-LNK-SLIDER")
    col, rows = table(pt)
    for r in rows:
        th = math.radians(r[0])
        A = np.array([p["crank_m"] * math.cos(th), 0, p["crank_m"] * math.sin(th)])
        assert np.linalg.norm(pos(col, r, "slider") - A) == pytest.approx(p["rod_m"], abs=1e-5)
    xs = [pos(col, r, "slider")[0] for r in rows]
    assert max(xs) - min(xs) == pytest.approx(2 * p["crank_m"], abs=1e-4)              # 对心：行程 = 2r


def test_cam_roller_touches_profile():
    e, p, pt = part("C-CAM-DISC")
    pitch, prof = c_mech.cam_profile(p)
    prof = np.array(prof)
    col, rows = table(pt)
    rr = p["roller_radius_m"]
    for r in rows[::9]:
        phi = angle(col, r, "cam")
        c = pos(col, r, "follower")[[0, 2]]
        cc = np.array([[math.cos(-phi), -math.sin(-phi)], [math.sin(-phi), math.cos(-phi)]]) @ c   # 滚子中心到凸轮坐标系
        dist = np.min(np.linalg.norm(prof - cc, axis=1))
        assert dist == pytest.approx(rr, abs=2.5e-4), r[0]                                   # 相切（轮廓按 720 点离散）
    s = [pos(col, r, "follower")[2] - p["base_radius_m"] - rr for r in rows]
    assert max(s) == pytest.approx(p["lift_m"], abs=1e-9) and min(s) == pytest.approx(0, abs=1e-9)


def _mesh_check(eid):
    """啮合：转动关系符合齿数比；在起始位置，两级齿轮都不干涉（相位对齐）"""
    from build123d import Axis, Pos
    e, p, pt = part(eid)
    col, rows = table(pt)
    z1, z2, z3, z4 = (int(p[k]) for k in ("z1", "z2", "z3", "z4"))
    a1 = unwrap([angle(col, r, "shaft1") for r in rows])
    a2 = unwrap([angle(col, r, "shaft2") for r in rows])
    a3 = unwrap([angle(col, r, "shaft3") for r in rows])
    assert np.allclose(a2 - a2[0], -(a1 - a1[0]) * z1 / z2, atol=1e-6)
    assert np.allclose(a3 - a3[0], (a1 - a1[0]) * z1 * z3 / (z2 * z4), atol=1e-6)
    off2, off4 = c_mech.mesh_phase(p)
    L = c_mech.gear_train_layout(p)
    for (m, za, zb, b, off_a, off_b, dist) in [(p["module1_mm"], z1, z2, p["face1_mm"], 0.0, off2, L["a1_m"]),
                                                 (p["module2_mm"], z3, z4, p["face2_mm"], off2, off4, L["a2_m"])]:
        c_mech.spur(m, za, b, c_mech.BLUE)
        c_mech.spur(m, zb, b, c_mech.BLUE)
        ga = c_mech._GEAR_CACHE[(m, za, b)].rotate(Axis.Y, -math.degrees(off_a))
        gb = Pos(dist * 1000, 0, 0) * c_mech._GEAR_CACHE[(m, zb, b)].rotate(Axis.Y, -math.degrees(off_b))
        bad = Pos(dist * 1000, 0, 0) * c_mech._GEAR_CACHE[(m, zb, b)].rotate(Axis.Y, -math.degrees(off_b + math.pi / zb))
        v, vbad = (ga & gb).volume, (ga & bad).volume
        assert v < 0.1 * vbad, (eid, za, zb, v, vbad)                  # 对齐后的干涉远小于错半个齿
    return p, pt


def test_gear_train_ratio_and_mesh():
    p, pt = _mesh_check("C-GER-TRAIN")
    assert pt["mechanism"]["analysis"]["ratio"] == pytest.approx(40 * 54 / (20 * 18))


@pytest.mark.skipif(not FACTORY_DATA.exists(), reason="没有工厂数据")
def test_wqr105_matches_factory_data():
    spec = importlib.util.spec_from_file_location("fdata", FACTORY_DATA)
    F = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(F)
    p, pt = _mesh_check("C-RED-WQR105")
    (a, b), (c, d) = F.STAGES
    assert (p["module1_mm"], p["z1"], p["z2"]) == (F.GEARS[a]["m"], F.GEARS[a]["z"], F.GEARS[b]["z"])
    assert (p["module2_mm"], p["z3"], p["z4"]) == (F.GEARS[c]["m"], F.GEARS[c]["z"], F.GEARS[d]["z"])
    an = pt["mechanism"]["analysis"]
    assert an["ratio"] == pytest.approx(F.ratio())
    assert [x * 1000 for x in an["center_distance_m"]] == pytest.approx([F.center_distance(F.GEARS[a]["m"], F.GEARS[a]["z"], F.GEARS[b]["z"]),
                                                                          F.center_distance(F.GEARS[c]["m"], F.GEARS[c]["z"], F.GEARS[d]["z"])])


def test_worm_ratio():
    e, p, pt = part("C-WRM-WORM")
    col, rows = table(pt)
    for r in rows[::10]:
        assert angle(col, r, "wheel") == pytest.approx(math.remainder(math.radians(r[0]) * p["worm_starts"] / p["wheel_teeth"], 2 * math.pi), abs=1e-6)
    an = pt["mechanism"]["analysis"]
    assert an["center_distance_m"] == pytest.approx(p["module_mm"] * (p["diameter_factor"] + p["wheel_teeth"]) / 2000)
    assert an["lead_angle_deg"] == pytest.approx(math.degrees(math.atan(p["worm_starts"] / p["diameter_factor"])), abs=1e-4)


def test_belt_length_formula_matches_path():
    e, p, pt = part("C-BLT-BELT")
    g = c_mech.belt_geometry(p)
    path = np.array(c_mech.belt_path(p, n=4000) + [c_mech.belt_path(p, n=4000)[0]])
    assert np.sum(np.linalg.norm(np.diff(path, axis=0), axis=1)) == pytest.approx(g["length_m"], rel=1e-4)
    assert g["wrap_small_deg"] >= 120
    col, rows = table(pt)
    a1 = unwrap([angle(col, r, "pulley1") for r in rows])
    a2 = unwrap([angle(col, r, "pulley2") for r in rows])
    assert np.allclose(a2 - a2[0], (a1 - a1[0]) * p["d1_m"] / p["d2_m"], atol=1e-6)


def test_ratchet_one_tooth_per_cycle_never_back():
    e, p, pt = part("C-RAT-RATCHET")
    col, rows = table(pt)
    w = unwrap([angle(col, r, "wheel") for r in rows])
    assert np.all(np.diff(w) >= -1e-9)                                  # 不倒转
    pitch = 2 * math.pi / p["teeth"]
    for k in range(1, 4):
        assert c_mech.ratchet_state(p, 360 * k)[1] == pytest.approx(k * pitch)
    assert w[-1] - w[0] == pytest.approx(4 * pitch, abs=pitch * 0.02)


def test_geneva_indexing_and_pin_in_slot():
    e, p, pt = part("C-GNV-GENEVA")
    n, R = int(p["slots"]), p["crank_m"]
    C = R / math.sin(math.pi / n)
    step = 2 * math.pi / n
    assert c_mech.geneva_wheel_angle(p, 360) - c_mech.geneva_wheel_angle(p, 0) == pytest.approx(-step)
    lim = 90 - 180 / n
    for deg in np.arange(180 - lim, 180 + lim, 2.0):                    # 拨销在槽内：销的方向 = 某一条槽的方向
        th = math.radians(deg)
        pin = np.array([R * math.cos(th) + C, R * math.sin(th)])
        ang = math.atan2(pin[1], pin[0])
        w = c_mech.geneva_wheel_angle(p, deg)
        rel = (ang - w) / step
        assert abs(rel - round(rel)) < 1e-9, deg
    ws = [c_mech.geneva_wheel_angle(p, d) for d in np.arange(0, 720, 0.5)]
    assert np.max(np.abs(np.diff(ws))) < math.radians(3)                # 进出槽时连续，没有跳变
    assert pt["mechanism"]["analysis"]["motion_fraction"] == pytest.approx((n - 2) / (2 * n))


def test_lead_screw_nut_moves_one_lead_per_turn():
    e, p, pt = part("C-SCN-LEAD")
    col, rows = table(pt)
    x0 = pos(col, rows[0], "nut")[0]
    for r in rows[::12]:
        assert pos(col, r, "nut")[0] - x0 == pytest.approx(p["lead_mm"] / 1000 * r[0] / 360, abs=1e-9)
