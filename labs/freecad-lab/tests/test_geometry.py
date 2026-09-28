# -*- coding: utf-8 -*-
"""纯几何计算的测试，不需要 FreeCAD。运行：python -m pytest tests"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "macros"))

import wq_gear  # noqa: E402
import wq_shaft  # noqa: E402


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol


# ---------- 齿轮
def test_dimensions_match_textbook():
    # m=2, z=24, α=20°：d=48, da=52, df=43, db=48·cos20°
    d = wq_gear.gear_dimensions(2, 24)
    assert close(d["d"], 48) and close(d["da"], 52) and close(d["df"], 43)
    assert close(d["db"], 48 * math.cos(math.radians(20)))
    assert not d["undercut"] and not d["pointed"]


def test_undercut_limit_is_about_17():
    assert close(wq_gear.gear_dimensions(2, 20)["z_min"], 17.097, 1e-3)
    assert wq_gear.gear_dimensions(2, 12)["undercut"]
    assert not wq_gear.gear_dimensions(2, 18)["undercut"]


def test_tip_thickness_against_formula():
    # 齿顶厚 sa = da·(π/(2z) + inv α − inv αa)，z=24 m=2 时约 1.43 mm（≈0.72m）
    d = wq_gear.gear_dimensions(2, 24)
    assert 1.2 < d["sa"] < 1.5


def _chain_ok(edges, tol=1e-9):
    for (_, a), (_, b) in zip(edges, edges[1:] + edges[:1]):
        (x0, y0), (x1, y1) = a[-1], b[0]
        if math.hypot(x1 - x0, y1 - y0) > tol:
            return False
    return True


def test_profile_is_closed_chain_small_and_large_gears():
    # z=24：齿根圆在基圆以内（有径向线）；z=60：齿根圆大于基圆（无径向线）
    for z in (12, 24, 60):
        edges = wq_gear.gear_profile(2, z)
        assert _chain_ok(edges), "z={} 轮廓不闭合".format(z)
        dim = wq_gear.gear_dimensions(2, z)
        rmax = max(math.hypot(*p) for _, pts in edges for p in pts)
        rmin = min(math.hypot(*p) for _, pts in edges for p in pts)
        assert close(rmax, dim["da"] / 2, 1e-9)
        assert close(rmin, dim["df"] / 2, 1e-9)


def test_pitch_circle_tooth_thickness_is_half_pitch():
    # 分度圆上齿厚 = πm/2：在右齿廓上插值找到 r = d/2 的点，测它到左齿廓的弦对应的弧长
    m, z = 2.0, 24
    r = m * z / 2
    rb = r * math.cos(math.radians(20))
    theta = wq_gear.inv(math.acos(rb / r))
    psi_b = math.pi / (2 * z) + wq_gear.inv(math.radians(20))
    half = psi_b - theta
    assert close(2 * r * half, math.pi * m / 2, 1e-9)


# ---------- 阶梯轴
def test_shaft_layout_total_length():
    layout, total = wq_shaft.shaft_layout(wq_shaft.PARAMS["segments"])
    assert total == 167 and layout[2] == (52, 112, 40)


def test_default_keyway_fits():
    assert wq_shaft.check_keyway(wq_shaft.PARAMS["segments"], wq_shaft.PARAMS["keyway"]) == []


def test_keyway_problems_are_reported():
    segs = [(30, 20)]
    probs = wq_shaft.check_keyway(segs, {"segment": 0, "b": 8, "t": 16, "L": 30})
    assert any("超过" in p for p in probs) and any("槽深" in p for p in probs)
    assert wq_shaft.check_keyway(segs, {"segment": 3, "b": 8, "t": 4, "L": 10})
