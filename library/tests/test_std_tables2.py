# -*- coding: utf-8 -*-
"""第 5 轮第 5 步：滚珠丝杠、直线导轨、同步带轮、梅花联轴器、压缩弹簧——尺寸表自洽、公式、抽查值、造型。"""
import math

import pytest
import yaml

import wqlib

T = wqlib.ROOT / "std_tables"


def specs(eid):
    e = next(x for x in wqlib.entries([eid]) if x["id"] == eid)
    return e, {str(r["size"]): r for r in wqlib.specs(e)}


def f(r, k):
    return float(r[k])


def test_ball_screw_table():
    e, rows = specs("A-BSC-SFU")
    assert len(rows) == 11
    for s, r in rows.items():
        assert f(r, "D_mm") < f(r, "D5_mm") < f(r, "D1_mm"), s          # 本体 < 孔分布圆 < 法兰
        assert f(r, "W_mm") < f(r, "D1_mm") and f(r, "L1_mm") < f(r, "L_mm"), s
        assert f(r, "C0a_N") > f(r, "Ca_N") > 0, s
        assert r["src_url"].startswith("https://")
    r = rows["25x10"]                                                   # 抽查：TBI SFNU02510-4（2954 / 7295 kgf）
    assert (f(r, "D_mm"), f(r, "D1_mm"), f(r, "L1_mm"), f(r, "L_mm"), f(r, "Dw_mm")) == (40, 62, 12, 85, 4.762)
    assert f(r, "Ca_N") == pytest.approx(2954 * 9.80665, abs=1) and f(r, "C0a_N") == pytest.approx(7295 * 9.80665, abs=1)


def test_linear_guide_table():
    t = yaml.safe_load((T / "lgd_rail.yaml").read_text(encoding="utf-8"))
    for r in t["rows"]:
        assert r["N_mm"] == pytest.approx((r["W_mm"] - r["rail_W_mm"]) / 2), r["size"]
        assert r["B1_mm"] == pytest.approx((r["W_mm"] - r["B_mm"]) / 2), r["size"]
        assert r["L1_mm"] < r["L_mm"] and r["H1_mm"] < r["rail_H_mm"] < r["H_mm"], r["size"]
    _, rows = specs("A-LGD-RAIL")
    r = rows["HGH25CA"]
    assert (f(r, "H_mm"), f(r, "W_mm"), f(r, "B_mm"), f(r, "C_mm"), r["rail_bolt"]) == (40, 48, 35, 35, "M6x20")


def test_pulley_formula_matches_gates():
    t = yaml.safe_load((T / "pul_htd.yaml").read_text(encoding="utf-8"))
    const = {c["size"]: c for c in t["rows"]}
    for c in t["check_rows"]:
        k = const[c["profile"]]
        PD = c["z"] * k["p_mm"] / math.pi
        assert PD == pytest.approx(c["PD_mm"], abs=0.011), c
        assert PD - 2 * k["delta_mm"] == pytest.approx(c["OD_mm"], abs=0.011), c
    _, rows = specs("A-PUL-HTD")
    assert len(rows) == 52
    r = rows["3M-40-9"]
    assert f(r, "PD_mm") == pytest.approx(38.2, abs=0.01) and f(r, "OD_mm") == pytest.approx(37.44, abs=0.01)


def test_jaw_coupling_table():
    _, rows = specs("A-CPL-JAW")
    names = sorted(rows, key=lambda s: int(s[2:]))
    assert "LM13" not in rows                                             # 原表 Tn_b 漏位，不收
    prev = None
    for s in names:
        r = rows[s]
        assert f(r, "Tn_b_Nm") > f(r, "Tn_a_Nm"), s
        assert f(r, "L0_mm") > 2 * f(r, "L_mm") and f(r, "d_max_mm") < f(r, "D_mm"), s
        if prev:
            assert f(r, "Tn_a_Nm") > f(prev, "Tn_a_Nm") and f(r, "D_mm") > f(prev, "D_mm"), s
        prev = r
    r = rows["LM8"]
    assert (f(r, "Tn_a_Nm"), f(r, "Tn_b_Nm"), f(r, "L_mm"), f(r, "L0_mm"), f(r, "D_mm")) == (1120, 2240, 70, 181, 170)


def test_spring_rate_formula():
    """k = G·d⁴/(8·D³·n)，表值按 G ≈ 79 000 N/mm²；误差在 4% 或表值末位取整之内"""
    _, rows = specs("A-SPR-CMP")
    assert len(rows) >= 200
    for s, r in rows.items():
        k = 79000 * f(r, "d_mm") ** 4 / (8 * f(r, "D_mm") ** 3 * f(r, "n"))
        txt = str(r["k_N_per_mm"])
        last = 10 ** -(len(txt.split(".")[1]) if "." in txt else 0)          # 表值只给 2～3 位有效数字：容差取末位的一半与 4% 中的大者
        assert abs(f(r, "k_N_per_mm") - k) <= max(0.04 * k, 0.5 * last + 1e-9), s
        assert f(r, "H0_mm") - f(r, "fs_mm") >= (f(r, "n") + 1.5) * f(r, "d_mm") - 1e-6, s      # 最大变形时不压并
    assert f(rows["6x30x38"], "k_N_per_mm") == 190 and f(rows["6x30x38"], "Fs_N") == 1605


@pytest.mark.parametrize("eid", ["A-BSC-SFU", "A-LGD-RAIL", "A-PUL-HTD", "A-CPL-JAW", "A-SPR-CMP"])
def test_generators_make_solids(eid):
    from generators import get_builder
    e, rows = specs(eid)
    parts = get_builder(e)(e, rows[e["default"]])
    assert parts and all(s.volume > 0 for _, s in parts)
    if eid == "A-SPR-CMP":                                                # 弹簧高度 ≈ 自由高度（两端磨平）
        bb = parts[0][1].bounding_box()
        assert bb.size.Z == pytest.approx(f(rows[e["default"]], "H0_mm"), rel=0.06)
