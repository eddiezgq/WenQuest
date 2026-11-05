"""Tapered roller bearings in pairs and adjusted at mounting (round 64, plan section 十六): standard problems."""

import copy
import json
import math
from pathlib import Path

import numpy as np
import pytest

from bearingkit import scenarios as SC
from bearingkit import taper as TP
from bearingkit import taper_check as TC
from bearingkit import taper_pair as PP
from bearingkit.analyze import ProjectError, analyse

EX = Path(__file__).resolve().parents[1] / "examples"
TAPER = json.loads((EX / "scene-tapered.json").read_text(encoding="utf-8"))
PAIR = json.loads((EX / "scene-tapered-pair.json").read_text(encoding="utf-8"))
B, _G = TC.build(TAPER)


def resid(p, u, P):
    r = p.forces(u) - np.asarray(P, float)
    return max(np.abs(r[:3]).max(), np.abs(r[3:]).max() / p.R)


def test_preload_alone_is_shared_equally_and_inverts():
    e = PP.endplay_for_preload(B, 2000.0)
    assert e < 0
    for arr in ("DB", "DF"):
        p = PP.Pair(B, arr, 40, e)
        assert p.preload_force() == pytest.approx(2000.0, rel=1e-9)
        u = p.solve([0, 0, 0, 0, 0])
        rows = PP.rows_of(p, u)
        assert np.abs(u).max() < 1e-12
        assert [r["Fa"] for r in rows] == pytest.approx(
            [2000.0, -2000.0] if arr == "DB" else [-2000.0, 2000.0], rel=1e-9
        )
        assert all(r["loaded"] == B.Z for r in rows)
    assert PP.endplay_for_preload(B, 0.0) == 0.0 and PP.Pair(B, "DB", 40, 0.01).preload_force() == 0.0


def test_back_to_back_holds_tilt_better_and_radial_is_the_same():
    e = PP.endplay_for_preload(B, 1500.0)
    k = {arr: PP.stiffness(PP.Pair(B, arr, 40, e), [0, 0, 0, 0, 0]) for arr in ("DB", "DF")}
    assert k["DB"]["radial"] == pytest.approx(k["DF"]["radial"], rel=1e-6)
    assert k["DB"]["axial"] == pytest.approx(k["DF"]["axial"], rel=1e-6)
    assert k["DB"]["tilt"] > 2 * k["DF"]["tilt"]
    # the pressure centres: tilting stiffness of the back-to-back pair grows with the row distance
    assert PP.stiffness(PP.Pair(B, "DB", 80, e), [0, 0, 0, 0, 0])["tilt"] > k["DB"]["tilt"]


def test_with_enough_end_play_one_row_is_the_single_row():
    p = PP.Pair(B, "DB", 40, 0.2)
    for Fa in (1500.0, 4000.0):
        u = p.solve([0, 0, Fa, 0, 0])
        rows = PP.rows_of(p, u)
        single = TP.distribute(B, 0.0, Fa)
        loaded = [r for r in rows if r["Qmax"] > 0]
        assert len(loaded) == 1 and loaded[0]["Qmax"] == pytest.approx(single["Qmax"], rel=1e-8)
        assert abs(loaded[0]["Fa"]) == pytest.approx(Fa, rel=1e-9)


@pytest.mark.parametrize("arr", ["DB", "DF"])
@pytest.mark.parametrize("e_um", [-30.0, 0.0, 25.0])
def test_combined_loads_balance(arr, e_um):
    p = PP.Pair(B, arr, 50, e_um / 1000)
    P = [4200.0, -1300.0, 2500.0, 3.0e4, -1.5e4]
    u = p.solve(P)
    assert resid(p, u, P) <= 1e-8 * 4200
    rows = PP.rows_of(p, u)
    assert sum(r["Fa"] for r in rows) == pytest.approx(2500.0, rel=1e-8)


def test_less_end_play_more_stiffness_and_preload():
    p = PP.Pair(B, "DF", 160, 0.0)
    P = [3000.0, 1000.0, 800.0, 0.0, 0.0]
    curve = TC.setting_curve(p, B, P, -50, 50, 11)
    k = [x for x in curve["k_axial"] if x is not None]
    # less end play, stiffer; rollers coming into or out of contact one by one leave ripples under 1 %
    assert len(k) == 11 and all(a >= b * (1 - 0.01) for a, b in zip(k, k[1:], strict=False)) and k[0] > 2 * k[-1]
    pre = curve["preload"]
    assert all(a >= b for a, b in zip(pre, pre[1:], strict=False)) and pre[-1] == 0.0 and pre[0] > 0


def test_supports_give_the_gear_forces_on_the_shaft():
    s = copy.deepcopy(PAIR["scenario"])
    sp = SC.supports(s)
    c, L = sp["cases"][0], sp["L"]
    d = s["mn"] * s["z"] / math.cos(math.radians(s["beta_deg"]))
    Ft = 2 * 9.549e6 * 18 / 960 / d
    Fr = Ft * math.tan(math.radians(s["alpha_n_deg"])) / math.cos(math.radians(s["beta_deg"]))
    Fa = Ft * math.tan(math.radians(s["beta_deg"]))
    P = SC.shaft_load(c, L)
    zg = s["x"] - L / 2
    assert P[0] == pytest.approx(Fr) and P[1] == pytest.approx(Ft) and P[2] == pytest.approx(-Fa)  # axial to A
    # moments about the middle: the gear forces at z_g, and the axial force at the pitch radius (the couple)
    assert P[4] == pytest.approx(zg * Ft)
    assert P[3] == pytest.approx(zg * Fr + Fa * d / 2)
    # every kind with two bearings gives reactions; the generic kind needs the distance
    for kind in ("motor", "spindle", "camshaft", "hub", "joint"):
        ex = next(
            json.loads(f.read_text(encoding="utf-8"))
            for f in EX.glob("scene-*.json")
            if json.loads(f.read_text(encoding="utf-8"))["scenario"]["kind"] == kind
        )
        assert SC.supports(ex["scenario"])["cases"]
    with pytest.raises(SC.ScenarioError):
        SC.supports({"kind": "generic"}, {"Fr": 1000})


def test_the_example_and_the_project_errors():
    r = analyse(PAIR)
    ids = {c["id"]: c for c in r["checks"]}
    assert {"endplay", "preload", "pair_loaded", "k_axial", "k_radial", "k_tilt"} <= set(ids)
    assert "moment_in" not in ids and ids["endplay"]["value"] == pytest.approx(20.0)
    assert len(r["pair_rows"]) == 2 and {x["z"] for x in r["pair_rows"]} == {-80.0, 80.0}
    assert len(r["setting_curve"]["e_um"]) == 21 and r["status"] != "fail"
    # preload given as a force: the same as the end play that gives it
    q = copy.deepcopy(PAIR)
    q["pair"].update({"setting": "preload", "preload": 1200})
    e = PP.endplay_for_preload(B, 1200) * 1000
    q2 = copy.deepcopy(PAIR)
    q2["pair"].update({"setting": "endplay", "endplay": e})
    a, b = analyse(q), analyse(q2)
    assert [c["value"] for c in a["checks"]] == pytest.approx([c["value"] for c in b["checks"]], rel=1e-6) or all(
        (x["value"] == y["value"])
        or abs(float(x["value"]) - float(y["value"])) <= 1e-6 * max(1, abs(float(y["value"])))
        for x, y in zip(a["checks"], b["checks"], strict=True)
        if isinstance(x["value"], float)
    )
    # a preloaded pair whose row unloads under the load fails the preload check: a side-by-side pair with a small
    # preload and a large axial force
    q3 = copy.deepcopy(TAPER)
    q3["scenario"] = {"kind": "generic"}
    q3["loads"] = {"Fr": 0, "Fa": 6000, "M": None, "n": 960}
    q3["pair"] = {"arrangement": "DB", "mount": "pair", "spacing": 40, "setting": "preload", "preload": 200}
    assert {c["id"]: c for c in analyse(q3)["checks"]}["pair_loaded"]["status"] == "fail"
    q3["pair"]["preload"] = 4000
    assert {c["id"]: c for c in analyse(q3)["checks"]}["pair_loaded"]["status"] == "pass"
    for bad, msg in (
        ({"arrangement": "DT"}, "DB"),
        ({"setting": "endplay", "endplay": None}, "end play"),
        ({"mount": "pair", "spacing": None}, "distance"),
    ):
        q4 = copy.deepcopy(PAIR)
        q4["pair"].update(bad)
        with pytest.raises(ProjectError, match=msg):
            analyse(q4)
    # a single row is unchanged by all this
    assert analyse(TAPER)["checks"] and "pair_rows" not in analyse(TAPER)
