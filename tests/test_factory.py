# -*- coding: utf-8 -*-
"""虚拟工厂数据的一致性检查，以及导入脚本对照 ERPNext v16 定义的模拟运行。运行：py -m pytest tests"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from factory import data as D  # noqa: E402
import seed  # noqa: E402
from mock_erpnext import MockERPNext  # noqa: E402


# ---------- 传动设计
def test_center_distances_and_ratio():
    assert D.center_distance(2, 24, 72) == 96
    assert D.center_distance(3, 20, 70) == 135
    assert math.isclose(D.ratio(), 10.5)
    assert math.isclose(D.INPUT_SPEED_RPM / D.ratio(), 138.095, rel_tol=1e-4)


def test_span_teeth_follow_the_standard_table():
    # 常用表格：z = 9–18 跨 2 齿，19–27 跨 3 齿，……，64–72 跨 8 齿，73–81 跨 9 齿
    for z, k in [(9, 2), (18, 2), (19, 3), (27, 3), (28, 4), (64, 8), (72, 8), (73, 9)]:
        assert D.span_teeth(z) == k, z


def test_base_tangent_length_equals_base_pitch_plus_base_tooth_thickness():
    # 另一条推导路线：W = (k − 1)·基圆齿距 + 基圆齿厚
    for m, z in [(2, 24), (2, 72), (3, 20), (3, 70)]:
        k, w = D.base_tangent_length(m, z)
        pb = math.pi * m * math.cos(D.ALPHA)
        sb = m * math.cos(D.ALPHA) * (math.pi / 2 + z * D.inv(D.ALPHA))
        assert math.isclose(w, (k - 1) * pb + sb, rel_tol=1e-12)


def test_gear_mesh_pairs_use_same_module():
    for a, b in D.STAGES:
        assert D.GEARS[a]["m"] == D.GEARS[b]["m"]


# ---------- 主数据一致性
def test_every_bom_component_is_an_item_and_boms_are_bottom_up():
    seen = set()
    for parent, (routing, lines) in D.BOMS.items():
        assert parent in D.ITEMS and routing in D.ROUTINGS
        for code, qty in lines:
            assert code in D.ITEMS, code
            assert qty > 0
            if code in D.BOMS:
                assert code in seen, "{} 的 BOM 要排在 {} 前面".format(code, parent)
            if D.ITEMS[code][2] == "Nos":
                assert float(qty).is_integer(), "{} 按件计，用量须为整数".format(code)
        seen.add(parent)


def test_every_made_item_has_a_bom_and_every_purchased_item_has_price_and_supplier():
    for code, (name, kind, uom, price, sup, qit, note) in D.ITEMS.items():
        if kind in ("make", "sub", "fg"):
            assert code in D.BOMS, code
            assert price is None
        else:
            assert price and price > 0 and sup in D.SUPPLIERS, code


def test_every_item_is_used():
    used = {c for _, lines in D.BOMS.values() for c, _ in lines}
    for code, v in D.ITEMS.items():
        if v[1] != "fg":
            assert code in used, "{} 没有出现在任何 BOM 里".format(code)


def test_operations_and_workstations_are_defined():
    for ops in D.ROUTINGS.values():
        for op, minutes in ops:
            assert op in D.OPERATIONS and minutes > 0
    for ws in D.OPERATIONS.values():
        assert ws in D.WORKSTATIONS


def test_templates_are_referenced_and_ranges_are_sane():
    templates = D.inspection_templates()
    for v in D.ITEMS.values():
        if v[5]:
            assert v[5] in templates, v[5]
    for t, params in templates.items():
        for p in params:
            if p["numeric"]:
                assert p["min"] < p["max"], (t, p)


def test_standard_cost_rollup_is_plausible():
    rate = {c: v[3] for c, v in D.ITEMS.items() if v[3]}
    minute_cost = {ws: sum(c) / 60 for ws, (_, c) in D.WORKSTATIONS.items()}

    def cost(code):
        if code in rate:
            return rate[code]
        routing, lines = D.BOMS[code]
        mat = sum(cost(c) * q for c, q in lines)
        op = sum(minute_cost[D.OPERATIONS[o]] * m for o, m in D.ROUTINGS[routing])
        return mat + op

    total = cost("WQR-105")
    assert 700 < total < 1300, total           # 标准成本约一千美元
    assert D.FG_SELLING_PRICE > total * 1.2      # 售价留有毛利


def test_holiday_calendar():
    days = seed.holidays(2026, 2027)
    dates = [d["holiday_date"] for d in days]
    assert len(dates) == len(set(dates))
    assert "2026-11-26" in dates and "2026-10-03" in dates   # 感恩节、周六
    assert "2026-10-05" not in dates                          # 周一上班


# ---------- 对照 ERPNext v16 定义模拟导入
def test_seed_against_erpnext_v16_schemas():
    mock = MockERPNext()
    client = seed.Client.__new__(seed.Client)
    client.base, client.s = "http://mock", mock
    s = seed.Seeder(client, log=lambda *a: None)
    s.run(opening_stock=True)
    assert mock.errors == [], "\n".join(mock.errors)
    assert len(mock.db["Item"]) == len(D.ITEMS)
    assert len([b for b in mock.db["BOM"].values() if b["docstatus"] == 1]) == len(D.BOMS)
    fg_bom = next(b for b in mock.db["BOM"].values() if b["item"] == "WQR-105")
    assert all(r.get("bom_no") for r in fg_bom["items"] if r["item_code"] in D.BOMS)

    # 再运行一次：全部跳过，不重复创建
    before = {k: len(v) for k, v in mock.db.items()}
    s2 = seed.Seeder(client, log=lambda *a: None)
    s2.run()
    assert s2.created == 0
    assert {k: len(v) for k, v in mock.db.items()} == before
