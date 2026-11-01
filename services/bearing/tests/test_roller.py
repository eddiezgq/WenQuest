"""Round 64 step 4: cylindrical roller bearings by slices, against Palmgren, Hertz and Stribeck."""

import math

import numpy as np
import pytest

from bearingkit import roller as R

NU = {"D": 10.0, "L": 10.0, "Z": 14, "dm": 52.5, "Pd": 0.0}


def test_uniform_slice_is_palmgren():
    b = R.bearing(NU)
    q = R.slice_loads(b, np.full(b.k, 0.004))  # 4 µm total closing on a straight roller
    Q = q.sum() * b.L / b.k
    assert np.ptp(q) == 0
    assert 2 * R.PALMGREN * Q**0.9 / b.L**0.8 == pytest.approx(0.004, rel=1e-12)  # two contacts in series


def test_line_contact_hertz():
    b = R.bearing(NU)
    s = R.stresses(b, np.array([500.0]))
    for ring in ("inner", "outer"):
        p, hb = s[ring]["p"][0], s[ring]["b"][0]
        assert p == pytest.approx(2 * 500 / (math.pi * hb), rel=1e-12)  # p0 = 2q / (π b)
    assert s["inner"]["p"][0] > s["outer"]["p"][0]  # the convex raceway is harder


def test_stribeck_line_contact_zero_clearance():
    b = R.bearing(NU)
    r = R.distribute(b, 10000)
    c = np.cos(np.radians(r["psi_deg"]))
    s = np.sum(np.where(c > 0, c, 0) ** (1 + 10 / 9))  # Q(ψ) = Q_max cos^(10/9) ψ
    assert r["Qmax"] == pytest.approx(10000 / s, rel=1e-9)
    assert np.sum(r["Q"] * c) == pytest.approx(10000, rel=1e-10)
    assert abs(r["M"]) < 1e-6


def test_clearance_fewer_rollers_more_load():
    tight = R.distribute(R.bearing(NU), 10000)
    loose = R.distribute(R.bearing(NU | {"Pd": 0.03}), 10000)
    assert loose["loaded"] < tight["loaded"] and loose["Qmax"] > tight["Qmax"]


def test_crown_moves_load_to_the_middle_and_tilt_to_one_end():
    arc = R.bearing(NU | {"profile": {"kind": "arc", "R": 2000}})
    r = R.distribute(arc, 10000)
    j = int(np.argmax(r["Q"]))
    q = r["q"][j]
    assert q[arc.k // 2] == q.max() and q[0] == pytest.approx(q[-1])  # symmetric, peak in the middle
    t = R.distribute(arc, 10000, theta=math.radians(4 / 60))  # 4′ misalignment
    qt = t["q"][int(np.argmax(t["Q"]))]
    assert qt[-1] > qt[0] and t["M"] > 0
    assert np.sum(t["Q"] * np.cos(np.radians(t["psi_deg"]))) == pytest.approx(10000, rel=1e-10)


def test_partial_crown_and_table_agree():
    part = R.bearing(NU | {"profile": {"kind": "partial", "R": 500, "flat": 6}})
    x = np.linspace(-5, 5, 11)
    d = part.drop(x)
    assert d[5] == 0 and d[3] == 0 and d[0] == pytest.approx(500 - math.sqrt(500**2 - 2**2))
    pts = [[a, b] for a, b in zip(np.linspace(0, 5, 51), part.drop(np.linspace(0, 5, 51)), strict=True)]
    tab = R.bearing(NU | {"profile": {"kind": "table", "points": pts}})
    assert tab.drop(x) == pytest.approx(d, abs=1e-6)


def test_bad_rollers():
    with pytest.raises(R.RollerError, match="fit round"):
        R.bearing(NU | {"Z": 17})
    with pytest.raises(R.RollerError, match="crown radius"):
        R.bearing(NU | {"profile": {"kind": "arc", "R": 3}})
