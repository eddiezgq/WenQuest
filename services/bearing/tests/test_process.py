"""Process routes (round 64, step 5, part 2): operation sizes worked back by hand, stock checks, unknowns."""

import json
import math
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from bearingkit import process as P
from bearingkit.analyze import geometry_of

EX = Path(__file__).resolve().parents[1] / "examples"


def geo(name="demo-deep-groove"):
    return geometry_of(json.loads((EX / f"{name}.json").read_text(encoding="utf-8")))


def chain(feature, finish=None, blank_T=0.4, **over):
    """blank → turn → heat → grind → superfinish on one feature of the inner ring."""
    vals = {
        "turn": {"Z": 1.0, "T": 0.1, "Zreq": 0.4},
        "heat": {"change": 0.05, "scatter": 0.04, "distortion": 0.06},
        "grind": {"Z": 0.3, "T": 0.012, "Zreq": 0.08, "Zmax": 0.45, "setup": 0.01},
        "fin": {"Z": 0.006, "dz": 0.003, "Zreq": 0.003},
    }
    for k, v in over.items():
        vals[k] = {**vals[k], **v}
    return {
        "rings": {
            "inner": {
                "ops": [
                    {"no": 10, "kind": "turn", "features": {feature: vals["turn"]}},
                    {"no": 20, "kind": "heat", "features": {feature: vals["heat"]}},
                    {"no": 30, "kind": "grind", "features": {feature: vals["grind"]}},
                    {"no": 40, "kind": "superfinish", "features": {feature: vals["fin"]}},
                    {"no": 50, "kind": "wash"},
                ],
                "finish": {feature: finish or {"es": None, "ei": None}},
                "blank": {feature: {"T": blank_T}},
            }
        }
    }


def rows(r, feature):
    return {x["no"]: x for x in r["rings"]["inner"]["table"][feature]["rows"]}


def checks(r):
    return {(c["op"], c["feature"], c["id"]): c for c in r["rings"]["inner"]["checks"]}


def test_external_feature_worked_back_by_hand():
    g = geo()
    race = next(f for f in P.features(g)["inner"] if f["id"] == "race")
    assert race["side"] == "ext"
    r = P.run(g, chain("race", {"es": 0.005, "ei": -0.020}))
    R = rows(r, "race")
    fin = race["size"] + 0.005  # max-material limit of the finished race
    sf_in = fin + (0.006 - 0.0015)  # superfinishing removes 0.006 ± 0.0015
    gr_in = sf_in + 0.3
    ht_in = gr_in - 0.05 - 0.02  # growth 0.05, scatter ±0.02 on the max-material side
    blank = ht_in + 1.0
    assert R[40]["mm"] == pytest.approx(fin, abs=1e-9)
    assert R[30]["mm"] == pytest.approx(sf_in, abs=1e-9)
    assert R[20]["mm_after"] == pytest.approx(gr_in, abs=1e-9) and R[20]["mm_before"] == pytest.approx(ht_in, abs=1e-9)
    assert R[10]["mm"] == pytest.approx(ht_in, abs=1e-9)
    tb = r["rings"]["inner"]["table"]["race"]["blank"]
    assert tb["size"] == pytest.approx(blank, abs=1e-9) and tb["lower"] == pytest.approx(-0.4)
    # stock removed by the grind: preceding tolerance 0.1 + scatter 0.04, distortion 0.06, setup 0.01
    assert R[30]["Zmin"] == pytest.approx(0.3 - 0.14 - 0.06 - 0.01, abs=1e-12)
    assert R[30]["Zmax"] == pytest.approx(0.3 + 0.012, abs=1e-12)
    assert R[10]["Zmin"] == pytest.approx(1.0 - 0.4, abs=1e-12)
    assert R[40]["Zmin"] == pytest.approx(0.0045, abs=1e-12)
    # finished tolerance: grinding 0.012 + superfinishing scatter 0.003 within 0.025
    c = checks(r)
    assert (
        c[(3, "race", "finish_tol")]["value"] == pytest.approx(0.015)
        and c[(3, "race", "finish_tol")]["status"] == "pass"
    )
    assert c[(2, "race", "stock_min")]["status"] == "pass" and c[(2, "race", "stock_max")]["status"] == "pass"
    assert r["status"] == "pass"


def test_internal_feature_worked_back_by_hand():
    g = geo()
    r = P.run(g, chain("bore", {"es": 0.0, "ei": -0.010}))
    R = rows(r, "bore")
    fin = 30.0 - 0.010  # max-material limit of a bore is its lower limit
    sf_in = fin - (0.006 - 0.0015)
    gr_in = sf_in - 0.3
    ht_in = gr_in - 0.05 + 0.02
    assert R[40]["mm"] == pytest.approx(fin, abs=1e-9)
    assert R[20]["mm_before"] == pytest.approx(ht_in, abs=1e-9)
    assert r["rings"]["inner"]["table"]["bore"]["blank"]["size"] == pytest.approx(ht_in - 1.0, abs=1e-9)
    assert R[40]["size"]["lower"] == 0.0 and R[40]["size"]["upper"] == pytest.approx(0.015)


def test_extreme_parts_remove_exactly_the_stock_range():
    """Forward check: the largest incoming part and the smallest outgoing one bound the stock."""
    g = geo()
    r = P.run(g, chain("race", {"es": 0.0, "ei": -0.03}, heat={"distortion": 0.0}, grind={"setup": None}))
    R = rows(r, "race")
    hi_in = R[20]["mm_after"]  # external: the largest part after heat treatment
    lo_in = hi_in - (0.1 + 0.04)
    hi_out, lo_out = R[30]["mm"], R[30]["mm"] - 0.012
    assert R[30]["Zmin"] == pytest.approx(lo_in - hi_out, abs=1e-12)
    assert R[30]["Zmax"] == pytest.approx(hi_in - lo_out, abs=1e-12)


def test_too_little_stock_fails_and_missing_numbers_are_unknown():
    g = geo()
    r = P.run(g, chain("race", grind={"Z": 0.2}))  # 0.2 − 0.14 − 0.06 − 0.01 < 0
    c = checks(r)
    assert c[(2, "race", "stock_min")]["status"] == "fail" and r["status"] == "fail"
    r = P.run(g, chain("race", grind={"Zreq": 0.15}))  # positive but below what the company needs
    assert checks(r)[(2, "race", "stock_min")]["status"] == "fail"
    r = P.run(g, chain("race", heat={"distortion": None}))
    c = checks(r)
    assert c[(2, "race", "stock_min")]["status"] == "unknown" and "变形" in c[(2, "race", "stock_min")]["note_zh"]
    r = P.run(g, chain("race", heat={"change": None}))
    assert rows(r, "race")[10]["mm"] is None and r["rings"]["inner"]["table"]["race"]["blank"] is None
    r = P.run(g, chain("race", grind={"Zreq": None}))
    assert checks(r)[(2, "race", "stock_min")]["status"] == "unknown"
    r = P.run(g, chain("race"))  # finished tolerance not given: sizes from the nominal, the check unknown
    assert checks(r)[(3, "race", "finish_tol")]["status"] == "unknown"
    assert rows(r, "race")[40]["mm"] == pytest.approx(
        next(f["size"] for f in P.features(g)["inner"] if f["id"] == "race")
    )
    assert r["status"] != "pass"


def test_unground_feature_carries_the_heat_treatment_scatter():
    """A surface only turned keeps the turning tolerance plus the heat-treatment scatter."""
    g = geo()
    proc = {
        "rings": {
            "inner": {
                "ops": [
                    {"no": 10, "kind": "turn", "features": {"land": {"Z": 1, "T": 0.1, "Zreq": 0.3}}},
                    {
                        "no": 20,
                        "kind": "heat",
                        "features": {"land": {"change": 0.06, "scatter": 0.04, "distortion": 0}},
                    },
                ],
                "finish": {"land": {"es": 0, "ei": -0.12}},
            }
        }
    }
    c = checks(P.run(g, proc))
    assert (
        c[(1, "land", "finish_tol")]["value"] == pytest.approx(0.14)
        and c[(1, "land", "finish_tol")]["status"] == "fail"
    )


def test_every_type_has_a_blank_chain_without_numbers():
    for name, n_in in (("demo-deep-groove", 4), ("demo-angular", 4), ("scene-cylindrical", 3), ("scene-tapered", 4)):
        g = geo(name)
        fs = P.features(g)
        assert len(fs["inner"]) == n_in and all(f["size"] > 0 for r in fs.values() for f in r)
        t = P.blank_template(g)
        nums = [v for r in t["rings"].values() for o in r["ops"] for d in o["features"].values() for v in d.values()]
        assert nums and all(v is None for v in nums)
        r = P.run(g, t)
        assert r["status"] == "unknown"  # nothing is a pass without the company's numbers
        for ring in r["rings"].values():
            assert all(c["status"] in ("unknown", "info") for c in ring["checks"])
    taper = P.features(geo("scene-tapered"))
    g = geo("scene-tapered")
    # the cone raceway's mid diameter lies between the bore and the rib
    cone = {f["id"]: f["size"] for f in taper["inner"]}
    assert g["d"] < cone["race"] < cone["rib"] and math.isfinite(cone["race"])


def test_the_example_is_fictional_and_runs():
    t = json.loads((EX / "process" / "demo-deep-groove.json").read_text(encoding="utf-8"))
    assert t["fictional"] is True and "虚构" in t["title"]["zh"] and "虚构" in t["note"]["zh"]
    r = P.run(geo(t["design"]), t)
    assert r["fictional"] and len(r["rings"]) == 2
    assert all(len(ring["cards"]) >= 8 for ring in r["rings"].values())
    # the unground land bore of the outer ring: turning tolerance + heat scatter exceeds the finished tolerance
    bad = [c for ring in r["rings"].values() for c in ring["checks"] if c["status"] == "fail"]
    assert [c["feature"] for c in bad] == ["land_bore"]


def test_bad_input():
    g = geo()
    with pytest.raises(P.ProcessError, match="kind"):
        P.run(g, {"rings": {"inner": {"ops": [{"kind": "weld"}]}}})
    with pytest.raises(P.ProcessError, match="deviation"):
        P.run(g, chain("race", {"es": -0.01, "ei": 0.0}))
    with pytest.raises(P.ProcessError, match="finite"):
        P.run(g, chain("race", grind={"Z": "abc"}))
    with pytest.raises(P.ProcessError, match="inner or the outer"):
        P.run(g, {"rings": {}})


def test_api():
    from app import app

    c = TestClient(app)
    design = json.loads((EX / "demo-deep-groove.json").read_text(encoding="utf-8"))
    t = c.post("/api/process/template", json={"project": design}).json()
    assert {f["id"] for f in t["features"]["outer"]} == {"od", "land_bore", "width", "race"}
    lst = c.get("/api/process/examples").json()
    assert lst[0]["id"] == "demo-deep-groove"
    ex = c.get("/api/process/examples/demo-deep-groove").json()
    r = c.post("/api/process", json={"project": {"design": design, "process": ex}})
    assert r.status_code == 200 and r.json()["status"] == "fail"
    bad = c.post("/api/process", json={"project": {"design": design, "process": {"rings": {}}}})
    assert bad.status_code == 422 and bad.json()["detail"]["zh"] == "请给出内圈或外圈的工序"
    assert c.get("/api/process/examples/../x").status_code == 404
