"""Round 64 step 5 part 4: roundness and waviness, chart constants, Nelson's rules, capability."""

import math

import numpy as np
import pytest

from bearingkit import quality as Q


def test_chart_constants_closed_forms_and_familiar_values():
    assert Q.d2(2) == pytest.approx(2 / math.sqrt(math.pi), rel=1e-9)  # E|X1 − X2|, X1 − X2 ~ N(0, 2)
    assert Q.d3(2) == pytest.approx(math.sqrt(2 - 4 / math.pi), rel=1e-6)  # its standard deviation
    assert Q.c4(2) == pytest.approx(math.sqrt(2 / math.pi), rel=1e-12)
    assert round(Q.d2(5), 3) == 2.326 and round(Q.d3(5), 3) == 0.864 and round(Q.c4(5), 4) == 0.9400


def test_harmonics_recovered_and_roundness():
    n = 360
    th = np.arange(n) * 2 * np.pi / n
    r = 5 * np.cos(th - 0.3) + 0.8 * np.cos(2 * th) + 0.1 * np.cos(30 * th + 1)
    p = Q.profile({"r": r.tolist(), "bands": [[2, 15, "roundness"], [16, 100, "waviness"]]})
    assert p["eccentricity"] == pytest.approx(5, rel=1e-9)
    assert p["amp"][2] == pytest.approx(0.8, rel=1e-9) and p["amp"][30] == pytest.approx(0.1, rel=1e-9)
    band = {b["name"]: b for b in p["bands"]}
    assert (
        band["waviness"]["rms"] == pytest.approx(0.1 / math.sqrt(2), rel=1e-9) and band["waviness"]["peak_order"] == 30
    )
    oval = Q.profile({"r": (0.8 * np.cos(2 * th) + 5 * np.cos(th)).tolist()})
    assert oval["roundness"] == pytest.approx(1.6, rel=1e-9)  # 2 × amplitude, eccentricity removed


def test_profile_from_angle_points():
    pts = [[a, 0.5 * math.cos(math.radians(3 * a))] for a in range(0, 360, 5)]
    p = Q.profile({"points": pts})
    assert p["amp"][3] == pytest.approx(0.5, rel=2e-3)


def test_nelson_rules_each_found():
    base = [0.1, -0.1] * 10
    assert {h["rule"] for h in Q.nelson(base[:5] + [3.5] + base[:5], 0, 1)} >= {1}
    assert 2 in {h["rule"] for h in Q.nelson([0.5] * 9, 0, 1)}
    assert 3 in {h["rule"] for h in Q.nelson([-0.5, -0.3, -0.1, 0.1, 0.3, 0.5], 0, 1)}
    assert 4 in {h["rule"] for h in Q.nelson([0.2 * (-1) ** i for i in range(14)], 0, 1)}
    assert 5 in {h["rule"] for h in Q.nelson([2.5, 0, 2.5], 0, 1)}
    assert 6 in {h["rule"] for h in Q.nelson([1.5, 1.5, 0, 1.5, 1.5], 0, 1)}
    assert 7 in {h["rule"] for h in Q.nelson([0.1 * (-1) ** i for i in range(15)], 0, 1)}
    assert 8 in {h["rule"] for h in Q.nelson([1.5, -1.5] * 4, 0, 1)}
    assert Q.nelson([0.3, -0.8, 1.2, -0.2, 0.6], 0, 1) == []


def test_xbar_r_limits_and_capability():
    d = Q.synthetic_spc(k=30, n=5, mean=10, sd=0.01, shift_at=None)
    r = Q.spc({**d, "lsl": 9.97, "usl": 10.03})
    X = np.array(d["data"])
    rbar = np.ptp(X, axis=1).mean()
    sigma = rbar / Q.d2(5)
    assert r["main"]["ucl"] - r["main"]["cl"] == pytest.approx(3 * sigma / math.sqrt(5), rel=1e-12)
    assert r["capability"]["Cp"] == pytest.approx(0.06 / (6 * sigma), rel=1e-12)
    assert r["capability"]["Cpk"] <= r["capability"]["Cp"]


def test_shift_is_caught_and_charts():
    d = Q.synthetic_spc(k=30, n=5, mean=0, sd=1, shift_at=15, shift=2.0, seed=2)
    r = Q.spc(d)
    assert r["chart"] == "xbar_r" and r["rules"]  # the step shows up
    s = Q.spc({**d, "chart": "xbar_s"})
    assert s["spread"]["name"] == "s"
    i = Q.spc({"data": [[v] for v in np.random.default_rng(1).normal(0, 1, 40).round(4)]})
    assert i["chart"] == "i_mr" and i["spread"]["points"][0] is None


@pytest.mark.parametrize(
    "bad, msg",
    [
        ({"data": [[1, 2]]}, "at least 2"),
        ({"data": [[1, 2], [1]]}, "same number"),
        ({"data": [[1], [2]], "chart": "xbar_r"}, "2 or more"),
    ],
)
def test_bad_spc(bad, msg):
    with pytest.raises(Q.QualityError, match=msg):
        Q.spc(bad)
