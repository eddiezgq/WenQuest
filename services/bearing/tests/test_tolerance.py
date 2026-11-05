"""Clearance and groove position dimension chain (round 64, plan section 二十, part 2): standard problems. Sizes and
deviations are made up."""

import copy
import json
import math
from pathlib import Path

import numpy as np
import pytest

from bearingkit import ball as BB
from bearingkit import tolerance as TL
from bearingkit.analyze import geometry_of

EX = Path(__file__).resolve().parents[1] / "examples"


def spec(dev=True, pos=False):
    def it(nom, es, ei):
        return {"nom": nom, "es": es if dev else 0.0, "ei": ei if dev else 0.0}

    s = {
        "di": it(35.5, 0.004, -0.004),
        "do": it(52.53, 0.004, -0.004),
        "Dw": it(8.5, 0.0005, -0.0005),
        "ri": it(4.3775, 0.01, -0.01),
        "ro": it(4.4625, 0.01, -0.01),
    }
    if pos:
        s["ai"] = it(8.0, 0.02, -0.02)
        s["ao"] = it(8.0, 0.02, -0.02)
    return s


def test_no_deviation_is_the_nominal_and_matches_the_ball_kernel():
    r = TL.analyse(spec(dev=False, pos=True), n=2000)
    Pd = 52.53 - 35.5 - 17.0
    A = 4.3775 + 4.4625 - 8.5
    assert r["nominal"]["Pd"] == pytest.approx(Pd, abs=1e-12)
    b = BB.bearing({"D": 8.5, "Z": 10, "dm": 44.0, "fi": 4.3775 / 8.5, "fo": 4.4625 / 8.5, "Pd": Pd})
    assert r["nominal"]["alpha0"] == pytest.approx(math.degrees(b.alpha0), rel=1e-12)
    assert r["nominal"]["Ga"] == pytest.approx(2 * math.sqrt(A * A - (A - Pd / 2) ** 2), rel=1e-12)
    assert r["nominal"]["s"] == pytest.approx(A * math.sin(b.alpha0), rel=1e-12)
    for o in TL.OUT:
        e = r["extremes"][o]
        assert e["min"] == pytest.approx(e["max"]) == pytest.approx(r["nominal"][o])
        assert r["statistical"][o]["sd"] == pytest.approx(0.0, abs=1e-12)


def test_extremes_hold_the_statistics_and_the_samples():
    r = TL.analyse(spec(pos=True), n=100_000)
    for o in TL.OUT:
        e, st, mc = r["extremes"][o], r["statistical"][o], r["montecarlo"][o]
        assert e["min"] <= st["lo"] <= st["hi"] <= e["max"]
        assert e["min"] - 1e-12 <= mc["p_lo"] <= mc["p_hi"] <= e["max"] + 1e-12
    # P_d is linear in the sizes: the sampled mean and spread agree with the statistical ones (sampling error
    # of 1e5 normal samples: below 1 % of σ for the mean, 1 % for σ)
    st, mc = r["statistical"]["Pd"], r["montecarlo"]["Pd"]
    assert mc["mean"] == pytest.approx(st["mean"], abs=0.01 * st["sd"])
    assert mc["sd"] == pytest.approx(st["sd"], rel=0.01)
    # P_d by hand: worst cases and the root sum of squares (σ = tolerance / 6)
    assert r["extremes"]["Pd"]["max"] == pytest.approx(0.03 + 0.004 + 0.004 + 0.001, abs=1e-12)
    assert st["sd"] == pytest.approx(math.sqrt(0.008**2 + 0.008**2 + (2 * 0.001) ** 2) / 6, rel=1e-6)
    # each size's share of the variance sums to one; the derivatives agree with the formula
    sh = r["sensitivity"]["Pd"]
    assert sum(v["share"] for v in sh.values()) == pytest.approx(1.0)
    assert sh["do"]["dfdx"] == pytest.approx(1.0, rel=1e-6) and sh["Dw"]["dfdx"] == pytest.approx(-2.0, rel=1e-6)


def test_same_input_same_result_and_a_target():
    a = TL.analyse(spec(), n=20_000, target={"Pd": {"min": 0.025, "max": 0.035}})
    b = TL.analyse(spec(), n=20_000, target={"Pd": {"min": 0.025, "max": 0.035}})
    assert a == b
    out = a["montecarlo"]["Pd"]["outside"]
    assert 0 < out < 1
    u = TL.analyse(spec(), n=20_000, dist="uniform")
    assert u["montecarlo"]["Pd"]["sd"] > a["montecarlo"]["Pd"]["sd"]  # uniform over the tolerance spreads more


def test_interference_is_counted_not_computed():
    s = spec()
    s["do"]["nom"] = 52.5  # clearance 0 at the middle: half the bearings are tight
    r = TL.analyse(s, n=20_000)
    assert r["interference_possible"] and 0.3 < r["montecarlo"]["interference"] < 0.7
    assert np.isfinite(r["montecarlo"]["alpha0"]["p_hi"])


def test_from_a_design_and_errors():
    g = geometry_of(json.loads((EX / "demo-deep-groove.json").read_text(encoding="utf-8")))
    n = TL.nominal_from(g)
    assert n["do"]["nom"] - n["di"]["nom"] - 2 * n["Dw"]["nom"] == pytest.approx(0.015)
    with pytest.raises(ValueError, match="deviations"):
        TL.analyse(n)  # deviations not given: not taken as zero
    s = spec(pos=True)
    del s["ao"]
    with pytest.raises(ValueError, match="both groove positions"):
        TL.analyse(s)
    s = copy.deepcopy(spec())
    s["Dw"]["es"] = -0.01
    with pytest.raises(ValueError, match="upper deviation"):
        TL.analyse(s)
    with pytest.raises(ValueError, match="ball bearings"):
        TL.nominal_from({"type": "tapered"})


def test_the_service():
    from fastapi.testclient import TestClient

    import app as service

    c = TestClient(service.app)
    r = c.post("/api/tolerance", json={"project": {"spec": spec(pos=True), "n": 5000, "target": {"Pd": {"max": 0.04}}}})
    assert r.status_code == 200 and r.json()["montecarlo"]["n"] == 5000
    assert r.json()["nominal"]["s"] is not None
    s = spec()
    s["ri"]["es"] = None
    e = c.post("/api/tolerance", json={"project": {"spec": s}})
    assert e.status_code == 422 and e.json()["detail"]["zh"].startswith("请填 ri 的上下偏差")
    e = c.post("/api/tolerance", json={"project": {"spec": spec(), "n": 10}})
    assert e.status_code == 422 and "抽样次数" in e.json()["detail"]["zh"]
