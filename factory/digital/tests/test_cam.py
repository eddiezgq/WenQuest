# -*- coding: utf-8 -*-
"""第 13 轮 数控编程：刀路、后处理、读程序、加工时间、仿真与检查。
验收（实施细则 三）：车削仿真与本工序尺寸差 ≤ 0.01 mm、不过切；铣削过切为 0、残留在刀具半径以内；
G 代码能被独立的开源解析器（pygcode）读通；超程、转速超限查得出；加工时间与手算差 < 2%。"""
import math

import numpy as np
import pytest

shapely = pytest.importorskip("shapely")
from shapely import contains_xy, distance, points  # noqa: E402
from shapely.geometry import Point, box  # noqa: E402

from cae import cam, cam_post, cam_sim  # noqa: E402

SEGS = [(30, 40), (35, 12), (40, 60), (35, 25), (30, 30)]          # SH-301（设计台默认参数）
ROUGH = {30: 31.5, 35: 36.5, 40: 41.5}                               # 粗车工序尺寸（工艺规程 20：单边留 0.75）
FINISH = {30: 30.0, 35: 35.3, 40: 40.3}                              # 精车工序尺寸（工艺规程 40：留磨量 0.3）
TURN = {1: {"kind": "turn"}, 2: {"kind": "turn"}, 3: {"kind": "groove", "w": 3.0}}


def lathe_prog(ops, number=1301):
    return {"machine": "CNC-L01", "number": number, "title": "SH-301 测试", "header": {"item": "SH-301", "revision": "A"}, "ops": ops}


def rough_finish():
    pr, L, _ = cam.shaft_profile([(ROUGH[d], l) for d, l in SEGS], 0, "right")
    pf, _, _ = cam.shaft_profile([(FINISH[d], l) for d, l in SEGS], 1.5, "right")
    return pr, pf, L


# ---------------------------------------------------------------- 车削
def test_shaft_profile_sides():
    pr, L, tot = cam.shaft_profile(SEGS, 1.5, "right")
    assert tot == 167 and L == 115                        # 右边一次车到最大直径那段（含）
    assert pr[0] == (0.0, 27.0) and pr[1] == (-1.5, 30)  # 倒角
    pl, L2, _ = cam.shaft_profile(SEGS, 1.5, "left")
    assert L2 == 52 and pl[-1] == (-52, 40)              # 调头：车到 Ø40 轴肩为止


def test_rough_turning_matches_operation_size():
    pr, _, L = rough_finish()
    mv = cam.turn_face(50, 2, 1.0, 0.2) + cam.turn_rough(pr, 50, 2.5, 0.3, 0.0, 0.0)
    g = cam_post.post(lathe_prog([{"tool": {"n": 1, "name": "外圆车刀"}, "spindle": {"css": 120, "max_rpm": 3000}, "moves": mv}]))
    r = cam_sim.run(g, "CNC-L01", {"d": 50, "z_right": 2, "z_left": -125}, TURN, target=pr)
    assert not [c for c in r["checks"] if c["level"] == "error"], r["checks"]
    s = r["sim"]
    assert s["dev_min"] > -0.01 and s["dev_max"] <= 0.01          # 与粗车工序尺寸差 ≤ 0.01
    assert s["face_left"] == 0                                     # 端面余量车干净
    assert s["ap_max"] <= 2.5 + 1e-6                               # 每刀不超过工艺规程的 ap


def test_rough_with_allowance_then_finish():
    pr, pf, L = rough_finish()
    # 粗车留 径向 0.3、轴向 0.1，再精车到精车工序尺寸
    mv1 = cam.turn_rough(pf, 50, 2.5, 0.3, 0.3, 0.1)
    mv2 = cam.turn_finish(pf, 50, 0.15)
    g = cam_post.post(lathe_prog([
        {"tool": {"n": 1, "name": "外圆粗车刀"}, "spindle": {"css": 120, "max_rpm": 3000}, "moves": mv1},
        {"tool": {"n": 2, "name": "外圆精车刀"}, "spindle": {"css": 150, "max_rpm": 3500}, "moves": mv2}]))
    p = cam_sim.parse(g, "CNC-L01")
    half = [m for m in p["moves"] if m["tool"] == 1]
    s1 = cam_sim.simulate_turn({"moves": half}, {"d": 50, "z_right": 0, "z_left": -125}, TURN,
                               target=cam.with_allowance(pf, 0.3, 0.1))
    assert s1["dev_min"] > -0.01 and s1["dev_max"] <= 0.01 and not s1["issues"]
    s2 = cam_sim.simulate_turn(p, {"d": 50, "z_right": 0, "z_left": -125}, TURN, target=pf)
    assert s2["dev_min"] > -0.01 and s2["dev_max"] <= 0.01, (s2["dev_min"], s2["dev_max"], s2["under_z"])
    assert not s2["issues"]
    assert len(p["tool_changes"]) == 2


def test_overcut_and_rapid_collision_detected():
    pr, pf, L = rough_finish()
    bad = [dict(m) for m in cam.turn_finish(pf, 50, 0.15)]
    for m in bad:                                     # 把一段轮廓故意往里多车 0.2
        if m["t"] == "feed" and abs(m.get("x", 0) - 35.3) < 1e-9:
            m["x"] = 34.9
    g = cam_post.post(lathe_prog([{"tool": {"n": 2}, "spindle": {"rpm": 1000}, "moves": bad}]))
    r = cam_sim.run(g, "CNC-L01", {"profile": pf, "d": 50, "z_right": 0, "z_left": -125}, TURN, target=pf)
    assert any("过切" in c["text"] for c in r["checks"])
    g2 = "G21 G18 G99\nT0101\nG97 S800 M03\nG00 X30.0 Z2.0\nG00 X30.0 Z-20.0\nM30\n"     # 快移直接扎进 Ø50 毛坯
    r2 = cam_sim.run(g2, "CNC-L01", {"d": 50, "z_right": 0, "z_left": -100}, TURN)
    assert any("快移撞到工件" in c["text"] for c in r2["checks"])


def test_groove():
    mv = cam.turn_groove(-40, 26, 7.0, 30, 0.05, 3.0)
    g = cam_post.post(lathe_prog([{"tool": {"n": 3, "name": "切槽刀 3mm"}, "spindle": {"rpm": 600}, "moves": mv}]))
    s = cam_sim.run(g, "CNC-L01", {"d": 30, "z_right": 0, "z_left": -80}, TURN)["sim"]
    groove = (s["z"] <= -40) & (s["z"] >= -47)
    assert np.allclose(s["r"][groove][1:-1], 13.0)
    assert np.allclose(s["r"][(s["z"] > -39.9) | (s["z"] < -47.1)], 15.0)


# ---------------------------------------------------------------- 铣削
POCKET = box(-30, -20, 30, 20).buffer(-5).buffer(5).difference(Point(0, 0).buffer(6, quad_segs=32))   # R5 圆角型腔，中间 Ø12 岛
OUTLINE = box(-50, -40, 50, 40)
HOLES = [(-40, -30), (40, -30), (40, 30), (-40, 30)]
MILL = {1: {"kind": "endmill", "d": 10}, 2: {"kind": "endmill", "d": 8}, 3: {"kind": "drill", "d": 8.5}}


def plate_program(pocket=POCKET):
    ops = [{"tool": {"n": 1, "name": "立铣刀", "d": 10}, "spindle": {"rpm": 2400}, "moves": cam.mill_contour(OUTLINE, 10, 10, 5, 480)},
           {"tool": {"n": 2, "name": "立铣刀", "d": 8}, "spindle": {"rpm": 3000}, "moves": cam.mill_pocket(pocket, 8, 8, 0.45, 2, 450, 150)},
           {"tool": {"n": 3, "name": "钻头", "d": 8.5}, "spindle": {"rpm": 1200}, "moves": cam.drill(HOLES, 15, 5, 120)}]
    return cam_post.post({"machine": "VMC-01", "number": 5001, "title": "测试板", "ops": ops})


def plate_target(pocket):
    def T(X, Y):
        t = np.where(contains_xy(OUTLINE, X, Y), 0.0, -10.0)
        t[contains_xy(pocket, X, Y)] = -8.0
        for x, y in HOLES:
            t[(X - x) ** 2 + (Y - y) ** 2 < 4.25 ** 2] = -15.0
        return t
    return T


@pytest.mark.parametrize("pocket", [POCKET, box(-30, -20, 30, 20)], ids=["圆角带岛", "尖角"])
def test_plate_no_overcut_residual_within_radius(pocket):
    g = plate_program(pocket)
    r = cam_sim.run(g, "VMC-01", {"box": (-52, -42, 52, 42)}, MILL, plate_target(pocket))
    assert not [c for c in r["checks"] if c["level"] == "error"], r["checks"][:3]
    s = r["sim"]
    assert s["over"] == 0
    X, Y = np.meshgrid(s["x"], s["y"], indexing="ij")
    um = s["under_mask"] & contains_xy(pocket, X, Y)
    if um.any():                                       # 残留只在型腔角上，离壁不超过刀具半径
        d = distance(pocket.boundary, points(X[um], Y[um]))
        assert d.max() <= 4.0 + s["h"]
    assert not (s["under_mask"] & ~contains_xy(pocket, X, Y)).any()


def test_keyway_on_shaft():
    """SH-301 键槽 12×45：精车后 Ø40.3，槽底到下母线 35.15 → 从顶点往下 5.15；Ø12 键槽铣刀一刀宽，分 5 层"""
    depth = 40.3 - 35.15
    mv = cam.mill_slot((-16.5, 0), (16.5, 0), 12, depth, 12, depth / 5, 120, 60)
    g = cam_post.post({"machine": "KEY-01", "number": 5050, "title": "键槽", "ops": [
        {"tool": {"n": 1, "name": "键槽铣刀", "d": 12}, "spindle": {"rpm": 800}, "moves": mv}]})
    slot = box(-16.5, -6, 16.5, 6).union(Point(-16.5, 0).buffer(6, quad_segs=64)).union(Point(16.5, 0).buffer(6, quad_segs=64))

    def T(X, Y):
        t = np.sqrt(np.clip(20.15 ** 2 - Y ** 2, 0, None)) - 20.15
        t[contains_xy(slot.buffer(-0.05), X, Y)] = -depth
        t[~contains_xy(slot.buffer(0.05), X, Y) & ~(np.abs(Y) < 20.15)] = np.nan
        edge = contains_xy(slot.buffer(0.05), X, Y) & ~contains_xy(slot.buffer(-0.05), X, Y)
        t[edge] = np.nan                                 # 槽边上一格不比
        return t
    r = cam_sim.run(g, "KEY-01", {"box": (-30, -20.15, 30, 20.15), "cyl_r": 20.15}, {1: {"kind": "endmill", "d": 12}}, T)
    s = r["sim"]
    assert not [c for c in r["checks"] if c["level"] == "error"], r["checks"]
    assert s["over"] == 0 and not s["under_mask"].any()
    assert s["ap_max"] == pytest.approx(depth / 5, abs=0.01)       # 每层切深 = 槽深 / 5


# ---------------------------------------------------------------- G 代码：独立解析、检查、时间
def test_independent_parser_reads_both_posts():
    pygcode = pytest.importorskip("pygcode")
    pr, pf, L = rough_finish()
    progs = [cam_post.post(lathe_prog([{"tool": {"n": 1}, "spindle": {"css": 120, "max_rpm": 3000},
                                        "moves": cam.turn_rough(pf, 50, 2.5, 0.3)}])), plate_program()]
    for g in progs:
        mine = cam_sim.parse(g, "CNC-L01" if "G18" in g else "VMC-01")
        n_motion = 0
        for raw in g.splitlines():
            if raw.strip() in ("%", "") or raw.startswith("O"):
                continue
            line = pygcode.Line(raw)                      # 读不通会抛异常
            n_motion += sum(1 for c in line.block.gcodes if c.word_key and str(c.word_key) in ("G00", "G01"))
            n_motion += 1 if (not line.block.gcodes and any(str(w)[0] in "XYZ" for w in line.block.modal_params)) else 0
        assert n_motion > 10
        assert len(mine["moves"]) >= n_motion * 0.9


def test_fanuc_numbers_have_decimal_point():
    assert cam_post.num(200) == "200.0" and cam_post.num(35.3) == "35.3" and cam_post.num(-0.0001) == "0.0"


def test_limits_and_spindle_checks():
    g = "G21 G17 G90 G94\nT1 M06\nG54\nS9000 M03\nG00 X500.0 Y0.0\nG43 Z50.0 H01\nG01 Z-5.0 F100.0\nM30\n"
    ch = cam_sim.machine_checks(cam_sim.parse(g, "VMC-01"), "VMC-01")
    txt = " ".join(c["text"] for c in ch)
    assert "X 超程" in txt and "超过机床最高转速" in txt
    g2 = "G21 G18 G99\nT0101\nG96 S200 M03\nG00 X40.0 Z2.0\nG01 X0.0 F0.1\nM30\n"
    txt2 = " ".join(c["text"] for c in cam_sim.machine_checks(cam_sim.parse(g2, "CNC-L01"), "CNC-L01"))
    assert "G50" in txt2
    g3 = "G21 G17 G90 G94\nT1 M06\nG00 X0.0 Y0.0 Z5.0\nG01 Z-1.0 F100.0\nM30\n"
    assert any("M03" in c["text"] for c in cam_sim.machine_checks(cam_sim.parse(g3, "VMC-01"), "VMC-01"))


def test_time_matches_hand_calculation():
    # 车：G97 恒转速 800 r/min，f 0.2 mm/r，车外圆 100 mm → 100 / (0.2×800) min
    g = "G21 G18 G99\nT0101\nG97 S800 M03\nG00 X40.0 Z2.0\nG01 Z-98.0 F0.2\nM30\n"
    p = cam_sim.parse(g, "CNC-L01")
    t = cam_sim.timing(p, "CNC-L01")
    assert abs(t["cut_s"] - 60 * 100 / (0.2 * 800)) / t["cut_s"] < 0.02
    # 车：G96 恒线速 150 m/min，从 Ø40 车端面到 Ø10，G50 限速 3000。
    #   t = ∫ dr / (f·n)，n = 1000·vc/(π·D)：D ≥ D* 时 t = π(D₁² − D*²)/(4000·vc·f)；D* = 1000·vc/(π·3000) 以下转速被限在 3000，t = (D* − D₀)/2/(f·3000)
    g = "G21 G18 G99\nT0101\nG50 S3000\nG96 S150 M03\nG00 X40.0 Z0.0\nG01 X10.0 F0.1\nM30\n"
    t = cam_sim.timing(cam_sim.parse(g, "CNC-L01"), "CNC-L01")
    Ds = 1000 * 150 / (math.pi * 3000)
    hand = 60 * (math.pi * (40 ** 2 - Ds ** 2) / (4000 * 150 * 0.1) + (Ds - 10) / 2 / (0.1 * 3000))
    assert abs(t["cut_s"] - hand) / hand < 0.02
    # 铣：G94 F300 走 3 段共 150 mm → 30 s；快移 Z 50 mm
    g = "G21 G17 G90 G94\nT1 M06\nS2000 M03\nG00 X0.0 Y0.0 Z5.0\nG01 Z-5.0 F300.0\nX50.0\nY40.0\nM30\n"
    t = cam_sim.timing(cam_sim.parse(g, "VMC-01"), "VMC-01")
    assert abs(t["cut_s"] - 60 * 100 / 300) < 1e-6
    assert t["tool_changes"] == 1


def test_peck_drill_expands():
    g = "G21 G17 G90 G94\nT3 M06\nS1200 M03\nG00 X0.0 Y0.0 Z5.0\nG98 G83 X10.0 Y0.0 Z-15.0 R2.0 Q5.0 F120.0\nX20.0\nG80\nM30\n"
    p = cam_sim.parse(g, "VMC-01")
    feeds = [m for m in p["moves"] if m["t"] == "feed"]
    assert len(feeds) == 2 * 4                                           # 17 mm 每次 5 → 4 次，两个孔
    assert min(m["b"][2] for m in feeds) == -15.0
    assert p["moves"][-1]["b"][2] == 5.0                                 # G98 回初始平面


def test_arc_interpolation():
    """G03 逆时针、G02 顺时针（从 +Z 往下看）；圆心用 I、J 或半径 R 给"""
    g = ("G21 G17 G90 G94\nT1 M06\nS1000 M03\nG00 X10.0 Y0.0 Z-1.0\n"
         "G03 X-10.0 Y0.0 I-10.0 J0.0 F200.0\n"      # 第 5 行：(10,0) 逆时针到 (-10,0)，走上半圆
         "G03 X10.0 Y0.0 R10.0\n"                     # 第 6 行：(-10,0) 逆时针回 (10,0)，走下半圆
         "G02 X-10.0 Y0.0 I-10.0 J0.0\n"              # 第 7 行：(10,0) 顺时针到 (-10,0)，走下半圆
         "M30\n")
    p = cam_sim.parse(g, "VMC-01")
    arcs = {}
    for m in p["moves"]:
        if m.get("arc"):
            arcs.setdefault(m["line"], []).append(m["b"])
    assert all(abs(math.hypot(x, y) - 10) < 1e-6 for pts in arcs.values() for x, y, _ in pts)
    assert max(y for _, y, _ in arcs[5]) == pytest.approx(10, abs=0.02)
    assert min(y for _, y, _ in arcs[6]) == pytest.approx(-10, abs=0.02)
    assert min(y for _, y, _ in arcs[7]) == pytest.approx(-10, abs=0.02)


def test_rpm_and_feed_formulas():
    assert cam.spindle_rpm(120, 50, 4000) == pytest.approx(763.94, rel=1e-4)
    assert cam.spindle_rpm(120, 5, 3000) == 3000
    assert cam.mill_feed(0.05, 4, 2000) == pytest.approx(400)
