"""Round 64 step 3: loads from typical application scenarios, checked against statics by hand."""

import json
import math
from pathlib import Path

import pytest

from bearingkit import scenarios as SC
from bearingkit.analyze import ProjectError, analyse

EX = Path(__file__).resolve().parents[1] / "examples"


def gear(**kw):
    s = {
        "kind": "gearbox",
        "mn": 3,
        "z": 40,
        "alpha_n_deg": 20,
        "beta_deg": 0,
        "x": 100,
        "L": 200,
        "fixed": "A",
        "cases": [{"P": 5, "n": 1000, "share": 1}],
    }
    s.update(kw)
    return s


def test_spur_gear_midspan_closed_form():
    d = 3 * 40
    Ft = 2 * 9.549e6 * 5 / 1000 / d
    for me in "AB":
        c = SC.loads(gear(this=me))["cases"][0]
        assert c["Fr"] == pytest.approx(Ft / (2 * math.cos(math.radians(20))), rel=1e-12)
        assert c["Fa"] == 0.0


def test_helical_gear_reactions_balance():
    s = gear(beta_deg=15, x=60, axial_to="B")
    A, B = (SC.loads({**s, "this": me})["cases"][0] for me in "AB")
    cb = math.cos(math.radians(15))
    d = 3 * 40 / cb
    Ft = 2 * 9.549e6 * 5 / 1000 / d
    Fr, Fa = Ft * math.tan(math.radians(20)) / cb, Ft * math.tan(math.radians(15))
    # tangential plane: R_A + R_B = F_t, moments about A: R_B L = F_t x
    tA, tB = Ft * 140 / 200, Ft * 60 / 200
    # radial plane: the couple F_a d/2 shifts load from B to A
    rA, rB = Fr * 140 / 200 + Fa * d / 2 / 200, Fr * 60 / 200 - Fa * d / 2 / 200
    assert rA + rB == pytest.approx(Fr) and rB * 200 + Fa * d / 2 == pytest.approx(Fr * 60)
    assert A["Fr"] == pytest.approx(math.hypot(tA, rA), rel=1e-12)
    assert B["Fr"] == pytest.approx(math.hypot(tB, rB), rel=1e-12)
    assert A["Fa"] == pytest.approx(Fa) and B["Fa"] == 0.0  # A is the fixed bearing


def test_spindle_overhang():
    s = {"kind": "spindle", "a": 80, "L": 240, "cases": [{"Fr": 1200, "Fa": 300, "n": 6000}]}
    A = SC.loads({**s, "this": "A"})["cases"][0]
    B = SC.loads({**s, "this": "B"})["cases"][0]
    assert A["Fr"] - B["Fr"] == pytest.approx(1200)  # front pushed one way, rear the other
    assert B["Fr"] * 240 == pytest.approx(1200 * 80)  # moments about the front bearing
    assert A["Fa"] == 300 and B["Fa"] == 0


def test_hub_rows_share_the_wheel_load():
    s = {"kind": "hub", "W": 4000, "ay": 0.5, "R": 300, "L": 60, "e": 0, "n": 800}
    out_row = SC.loads({**s, "row": "outboard"})
    in_row = SC.loads({**s, "row": "inboard"})
    assert out_row["outer_turns"] is True
    st_o, out_o, in_o = out_row["cases"]
    st_i, out_i, in_i = in_row["cases"]
    assert st_o["Fr"] == pytest.approx(2000) and st_i["Fr"] == pytest.approx(2000) and st_o["Fa"] == 0
    # turning: the couple W·ay·R moves load between the rows; the sum of signed reactions is still W
    assert out_o["Fr"] == pytest.approx(2000 + 2000 * 300 / 60)
    assert out_i["lift"] and out_i["Fr"] == pytest.approx(abs(2000 - 2000 * 300 / 60))
    assert out_o["Fa"] == pytest.approx(2000) and out_i["Fa"] == 0 and in_i["Fa"] == pytest.approx(2000)


def test_robot_joint_vertical_axis():
    pair = SC.loads({"kind": "joint", "axis": "vertical", "W": 500, "r": 400, "L": 50, "fixed": "A", "this": "A"})
    c = pair["cases"][0]
    assert pair["motion"] == "oscillating" and c["Fr"] == pytest.approx(500 * 400 / 50) and c["Fa"] == 500
    one = SC.loads({"kind": "joint", "axis": "vertical", "W": 500, "r": 400})["cases"][0]
    assert one["M"] == pytest.approx(200000) and one["Fa"] == 500 and one["Fr"] == 0


def test_motor_unbalance_turns_round():
    s = {"kind": "motor", "m": 20, "U": 2000, "x": 100, "L": 200, "n": 3000, "this": "A"}
    out = SC.loads(s)
    W = 20 * 9.80665
    Fu = 2000e-6 * (3000 * 2 * math.pi / 60) ** 2
    fr = [c["Fr"] for c in out["cases"]]
    assert len(fr) == 36 and out["curve"] == "angle"
    assert max(fr) == pytest.approx((W + Fu) / 2) and min(fr) == pytest.approx(abs(W - Fu) / 2)
    assert out["notes"]


def test_camshaft_table():
    tab = "\n".join(
        f"{a}, {100 * math.cos(math.radians(a))}, {100 * math.sin(math.radians(a))}" for a in range(0, 360, 30)
    )
    out = SC.loads({"kind": "camshaft", "x": 50, "L": 200, "n": 600, "table": tab, "this": "B"})
    assert all(c["Fr"] == pytest.approx(25.0) for c in out["cases"])  # 100 N at a quarter span: B takes 1/4
    with pytest.raises(SC.ScenarioError):
        SC.loads({"kind": "camshaft", "x": 50, "L": 200, "n": 600, "table": "0, 1"})


def demo():
    return json.loads((EX / "demo-deep-groove.json").read_text(encoding="utf-8"))


def by_id(r):
    return {c["id"]: c for c in r["checks"]}


def test_load_spectrum_peak_case_and_fatigue():
    p = demo()
    p["scenario"] = gear(
        beta_deg=12,
        x=60,
        this="A",
        cases=[
            {"label": "light", "P": 2, "n": 3000, "share": 0.7},
            {"label": "full", "P": 7.5, "n": 1500, "share": 0.3},
        ],
    )
    p["limits"] = {"p_static": 4000, "p_fatigue": 2000}
    r = analyse(p)
    sc = r["scenario"]
    assert [c["label"] for c in sc["cases"]] == ["light", "full"]
    assert sc["cases"][1]["p_inner"] > sc["cases"][0]["p_inner"]
    c = by_id(r)
    assert "full" in c["p_inner"]["zh"] and c["p_inner"]["value"] == pytest.approx(sc["cases"][1]["p_inner"])
    assert c["pf_inner"]["status"] == "unknown"  # no load factor yet
    p["scenario"]["fp"] = 1.5
    c2 = by_id(analyse(p))
    assert c2["pf_inner"]["value"] > c["p_inner"]["value"]  # the load factor raises the stress
    # the same as running the full case at 1.5 × its loads
    q = demo()
    full = sc["cases"][1]
    q["loads"] = {"Fr": 1.5 * full["Fr"], "Fa": 1.5 * full["Fa"], "n": 1500}
    assert c2["pf_inner"]["value"] == pytest.approx(by_id(analyse(q))["p_inner"]["value"], rel=1e-9)


def test_oscillating_joint_static_only():
    p = demo()
    p["scenario"] = {"kind": "joint", "axis": "horizontal", "W": 1500, "x": 20, "L": 60, "this": "A"}
    p["limits"] = {"p_static": 4000, "p_fatigue": 2000}
    c = by_id(analyse(p))
    assert c["pf_inner"]["status"] == "na" and c["p_inner"]["status"] == "pass"


def test_scenario_errors_are_project_errors():
    p = demo()
    p["scenario"] = {"kind": "gearbox"}
    with pytest.raises(ProjectError):
        analyse(p)
