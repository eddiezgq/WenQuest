"""A tapered pair from the end play as set to the end play at work (round 64, plan section 二十一): standard problems.
The bearing and the temperatures are made up (the scene-tapered examples)."""

import copy
import json
import math
from pathlib import Path

import numpy as np
import pytest

from bearingkit import clearance as CL
from bearingkit import taper_check as TC
from bearingkit import taper_pair as PP
from bearingkit import taper_thermal as TT
from bearingkit.analyze import ProjectError, analyse

EX = Path(__file__).resolve().parents[1] / "examples"
TAPER = json.loads((EX / "scene-tapered.json").read_text(encoding="utf-8"))
PAIR = json.loads((EX / "scene-tapered-pair.json").read_text(encoding="utf-8"))
B, G = TC.build(TAPER)
A = B.ao
DO = B.dm + B.D * math.cos(B.ao)


def closing(arr, s, eps_ax, eps_rad, x):
    """The closing along the cup normal of points along each row's cup raceway line when the inner side (shaft,
    cones, rollers) grows against the outer side by eps_ax axially (about the middle) and eps_rad radially: worked
    from the coordinates, independently of the formulas in taper_thermal."""
    out = []
    for sig, z in zip(PP.ARRANGEMENTS[arr], (-s / 2, s / 2), strict=True):
        n = np.array([sig * math.sin(A), math.cos(A)])  # (z, r)
        tau = np.array([math.cos(A), -sig * math.sin(A)])  # along the cup raceway
        pts = np.array([z, DO / 2])[None, :] + x[:, None] * tau[None, :]
        disp = pts * np.array([eps_ax, eps_rad])[None, :]
        out.append(disp @ n)
    return out


def test_nothing_taken_and_nothing_changes():
    c = TT.operating(0.02, "DB", 100, A, DO)
    assert c["operating"] is None and c["mounted"] == 0.02 and c["fit"] == 0.0
    T = dict(T_ref=20, T_i=20, T_o=20, T_shaft=20, T_house=20, a_ring=1.15e-5, a_shaft=1.15e-5, a_house=2.3e-5)
    for arr in ("DB", "DF"):
        assert TT.operating(0.02, arr, 100, A, DO, temps=T)["operating"] == pytest.approx(0.02, abs=1e-15)
    with pytest.raises(ValueError, match="DB or DF"):
        TT.operating(0.0, "DT", 100, A, DO)


@pytest.mark.parametrize("arr", ["DB", "DF"])
@pytest.mark.parametrize("s", [40.0, 160.0, 400.0])
def test_the_formulas_against_the_coordinates(arr, s):
    """Δe = −2 δ / sin α with δ the closing at the middle of the contact, for the axial and radial terms apart."""
    T = dict(T_ref=20, T_i=60, T_o=45, T_shaft=55, T_house=35, a_ring=1.15e-5, a_shaft=1.2e-5, a_house=2.3e-5)
    c = TT.operating(0.0, arr, s, A, DO, temps=T)
    e_ax = T["a_shaft"] * (T["T_shaft"] - 20) - T["a_house"] * (T["T_house"] - 20)
    e_rad = T["a_ring"] * ((T["T_i"] - 20) - (T["T_o"] - 20))
    x0 = np.array([0.0])
    for d in closing(arr, s, e_ax, 0.0, x0):
        assert c["axial"] == pytest.approx(-2 * d[0] / math.sin(A), rel=1e-12)
    for d in closing(arr, s, 0.0, e_rad, x0):
        assert c["radial"] == pytest.approx(-2 * d[0] / math.sin(A), rel=1e-12)
    # the closing goes through the pair model the same way as the end play: a row closed by δ is the end play −2δ/sin α
    p = PP.Pair(B, arr, s, c["operating"])
    G_, d0 = p._row(0)
    assert d0[0, 0] + B.cyl.drop(B.cyl.x())[0] * 2 == pytest.approx(-c["operating"] / 2 * math.sin(A), rel=1e-12)


def test_apexes_coincide_back_to_back():
    """One steel, shaft and cones at one temperature, cups and housing at another: a DB pair whose cup raceway cones
    meet on the axis keeps its end play (every point of the contact line, not only the middle); DF loses end play."""
    s0 = TT.apex_distance(A, DO)
    eps = 1.15e-5 * 30
    x = np.linspace(-B.L / 2, B.L / 2, 7)
    for d in closing("DB", s0, eps, eps, x):
        assert np.abs(d).max() <= 1e-15
    T = dict(T_ref=20, T_i=50, T_o=20, T_shaft=50, T_house=20, a_ring=1.15e-5, a_shaft=1.15e-5, a_house=1.15e-5)
    assert TT.operating(0.01, "DB", s0, A, DO, temps=T)["operating"] == pytest.approx(0.01, abs=1e-15)
    assert TT.operating(0.01, "DB", 2 * s0, A, DO, temps=T)["operating"] > 0.01  # the shaft's growth wins
    assert TT.operating(0.01, "DB", s0 / 2, A, DO, temps=T)["operating"] < 0.01  # the rings' growth wins
    for s in (s0 / 2, s0, 2 * s0):
        assert TT.operating(0.01, "DF", s, A, DO, temps=T)["operating"] < 0.01
    # the axial term flips sign with the arrangement, the radial one does not
    a, b = (TT.operating(0, k, 120, A, DO, temps=T) for k in ("DB", "DF"))
    assert a["axial"] == pytest.approx(-b["axial"]) and a["radial"] == pytest.approx(b["radial"])


def test_fits_by_the_clearance_chain():
    """Set before mounting: the fits take what the radial clearance chain takes, turned by tan α."""
    gi, so = TT.fits("bench", 35, 72, G["di"], G["do"], 0.02, 0.015, 206000, 0.3)
    ch = CL.chain(
        0.0,
        G["di"],
        G["do"],
        {"interference": 0.02, "d": 35, "d_ie": G["di"]},
        {"interference": 0.015, "D": 72, "d_oe": G["do"]},
    )
    assert gi + so == pytest.approx(-ch["mounted"], rel=1e-12)
    c = TT.operating(0.05, "DF", 100, A, DO, gi, so)
    assert c["fit"] * math.tan(A) == pytest.approx(ch["mounted"], rel=1e-12) and c["mounted"] < 0.05
    assert TT.fits("mounted", 35, 72, G["di"], G["do"], 0.02, 0.015, 206000, 0.3) == (0.0, 0.0)
    with pytest.raises(ValueError, match="mounted rings or before mounting"):
        TT.fits("hot", 35, 72, G["di"], G["do"], 0, 0, 206000, 0.3)


def test_a_radial_interference_is_the_end_play_it_turns_into():
    """Close every slice by Δr cos α directly in the pair model: the same as the end play reduced by 2 Δr / tan α."""
    dr, e = 0.004, 0.01

    class Grown(PP.Pair):
        def _row(self, j):
            g, d0 = super()._row(j)
            return g, d0 + dr * math.cos(A)

    for arr in ("DB", "DF"):
        P = [3000.0, 0, 1500.0, 0, 0]
        a = Grown(B, arr, 80, e)
        b = PP.Pair(B, arr, 80, e - 2 * dr / math.tan(A))
        ra, rb = PP.rows_of(a, a.solve(P)), PP.rows_of(b, b.solve(P))
        assert [r["Fa"] for r in ra] == pytest.approx([r["Fa"] for r in rb], rel=1e-7)
        assert [r["Qmax"] for r in ra] == pytest.approx([r["Qmax"] for r in rb], rel=1e-7)


def test_the_example_runs_at_work():
    r = analyse(PAIR)
    ids = {c["id"]: c for c in r["checks"]}
    c = r["pair"]["chain"]
    T = PAIR["pair"]
    e_ax = 1e-6 * (T["a_shaft"] * (T["T_shaft"] - 20) - T["a_house"] * (T["T_house"] - 20))
    want = 0.020 - 160 * e_ax - DO / math.tan(A) * 11.5e-6 * (50 - 45)  # DF, span 160
    assert ids["endplay"]["value"] == pytest.approx(20.0) and ids["endplay_work"]["value"] == pytest.approx(want * 1000)
    assert c["operating"] < 0 and ids["preload_work"]["value"] > 0 and ids["preload"]["value"] == 0.0  # cold play,
    assert "轴与轴承座轴向热伸长" in ids["endplay_work"]["note_zh"]  # warm preload
    # the cases run at the end play at work: the same as a pair set to it without heat
    q = copy.deepcopy(PAIR)
    for k in TC.THERMAL_KEYS:
        q["pair"][k] = None
    q["pair"]["endplay"] = want * 1000
    rq = analyse(q)
    assert [x["Qmax"] for x in r["pair_rows"]] == pytest.approx([x["Qmax"] for x in rq["pair_rows"]], rel=1e-9)
    # the curve sweeps the end play as set: at the setting it is the run
    q = copy.deepcopy(PAIR)
    q["pair"].update(sweep_from=20, sweep_to=40)
    cv = analyse(q)["setting_curve"]
    assert cv["e_um"][0] == 20.0 and cv["preload"][0] == pytest.approx(ids["preload_work"]["value"], rel=1e-9)
    # heat asked but a coefficient missing: unknown, and the cases at the end play as set
    q = copy.deepcopy(PAIR)
    q["pair"]["a_house"] = None
    rq = analyse(q)
    w = {c["id"]: c for c in rq["checks"]}["endplay_work"]
    assert w["status"] == "unknown" and w["value"] is None and "轴承座线膨胀系数" in w["note_zh"]
    assert rq["pair"]["work_um"] == pytest.approx(20.0)
    # nothing asked: said so, nothing assumed
    q = copy.deepcopy(PAIR)
    for k in TC.THERMAL_KEYS:
        q["pair"][k] = None
    w = {c["id"]: c for c in analyse(q)["checks"]}["endplay_work"]
    assert w["value"] is None and "未计温度" in w["note_zh"]
    # blank shaft and housing temperatures are the rings'
    q = copy.deepcopy(PAIR)
    q["pair"].update(T_shaft=None, T_house=None)
    assert analyse(q)["pair"]["chain"]["axial"] == pytest.approx(-160 * 1e-6 * (11.5 * 30 - 10.5 * 25))
    # set before mounting: the fits come in
    q = copy.deepcopy(PAIR)
    q["pair"]["basis"] = "bench"
    q["fits"].update(shaft_I=0.02, housing_I=0.0)
    assert analyse(q)["pair"]["chain"]["fit"] < 0
    q["pair"]["basis"] = "x"
    with pytest.raises(ProjectError, match="before mounting"):
        analyse(q)


def test_the_service_says_it_in_chinese():
    from fastapi.testclient import TestClient

    import app as service

    q = copy.deepcopy(PAIR)
    q["pair"]["basis"] = "x"
    e = TestClient(service.app).post("/api/analyse", json=q)
    assert e.status_code == 422 and "装前调好" in e.json()["detail"]["zh"]
