"""Round 64 step 4 part 3: angular contact ball bearings at speed and in pairs."""

import math

import numpy as np
import pytest

from bearingkit import ball as BB
from bearingkit import highspeed as HS

ACB = {"D": 9.0, "Z": 13, "dm": 54.0, "fi": 0.52, "fo": 0.53, "alpha0_deg": 25.0}


@pytest.fixture(scope="module")
def row():
    return HS.Row(BB.bearing(ACB))


def test_zero_speed_is_the_static_model(row):
    st = BB.distribute(row.b, Fr=1500, Fa=2000, tilt="fixed")
    hs = HS.single(row, 1500, 2000, n_rpm=0.0)
    assert hs["Qi"] == pytest.approx(st["Q"], rel=1e-3, abs=1e-6)  # tabulated stiffness: within 0.1 %
    assert np.degrees(hs["ai"]) == pytest.approx(st["alpha_deg"], abs=0.05)


def test_centrifugal_force_splits_the_contact_angles(row):
    hs = HS.single(row, 0.0, 2000, n_rpm=30000)
    psi = np.radians(hs["psi_deg"])
    Fa, Fr, _ = row.forces(hs, psi)
    assert Fa == pytest.approx(2000, rel=1e-6) and abs(Fr) < 1e-3
    assert np.all(hs["ao"] < hs["ai"])  # the outer angle falls, the inner rises
    assert np.all(hs["Qo"] > hs["Qi"])  # the outer contact carries F_c too
    # each ball balances: radial Q_o cos α_o − Q_i cos α_i = F_c, axial Q_o sin α_o = Q_i sin α_i
    assert hs["Qo"] * np.cos(hs["ao"]) - hs["Qi"] * np.cos(hs["ai"]) == pytest.approx(hs["Fc"], rel=1e-6)
    assert hs["Qo"] * np.sin(hs["ao"]) == pytest.approx(hs["Qi"] * np.sin(hs["ai"]), rel=1e-6)
    m = 7.85e-6 * math.pi * 9**3 / 6
    w = 30000 * 2 * math.pi / 60
    g = 9 * math.cos(hs["ao"][0]) / 54
    assert hs["Fc"][0] == pytest.approx(0.5 * m * 0.054 * (w / 2 * (1 - g)) ** 2, rel=1e-9)


def test_pair_preload_shares_and_balances(row):
    p = HS.pair(row, "DB", 500, 30, 0.0, 0.0)
    assert sorted(r["Fa"] for r in p["rows"]) == pytest.approx([-500, 500], rel=1e-6)  # each row holds the preload
    q = HS.pair(row, "DB", 500, 30, 1200, 800)
    assert sum(r["Fa"] for r in q["rows"]) == pytest.approx(800, rel=1e-6)
    assert sum(r["Fr"] for r in q["rows"]) == pytest.approx(1200, rel=1e-6)


def test_back_to_back_resists_tilt_better(row):
    th = {}
    for arr in ("DB", "DF"):
        th[arr] = HS.pair(row, arr, 500, 30, 0.0, 0.0, M=20000)["theta"]
    assert abs(th["DB"]) < abs(th["DF"])


def test_preload_raises_stiffness_and_too_little_unloads(row):
    lo = HS.stiffness(row, "DB", 200, 30, 500, 300)
    hi = HS.stiffness(row, "DB", 1000, 30, 500, 300)
    assert hi["axial"] > lo["axial"] and hi["radial"] > lo["radial"]
    p = HS.pair(row, "DB", 100, 30, 0.0, 1500)  # far more axial load than preload
    assert min(np.max(r["Qi"]) for r in p["rows"]) == 0.0  # the back row has let go
