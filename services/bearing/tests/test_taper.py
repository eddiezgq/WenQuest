"""Round 64 step 4 part 2: tapered roller bearings: roller equilibrium (Lamy), pure thrust, combined load."""

import math

import numpy as np
import pytest

from bearingkit import taper as T

TRB = {"D": 9.0, "L": 12.0, "Z": 17, "dm": 52.0, "alpha_o_deg": 15.0, "alpha_i_deg": 12.0, "R_end": 40.0}


def test_roller_equilibrium_is_lamy():
    b = T.bearing(TRB)
    lam, mu = b.ratios()
    no = np.array([math.sin(b.ao), -math.cos(b.ao)])
    ni = np.array([-math.sin(b.ai), math.cos(b.ai)])
    nf = -np.array([math.cos(b.af), math.sin(b.af)])
    assert no + lam * ni + mu * nf == pytest.approx([0, 0], abs=1e-12)

    def ang(u, v):
        return math.acos(np.dot(u, v))

    # Lamy: each force over the sine of the angle between the other two is the same
    k = [1 / math.sin(ang(ni, nf)), lam / math.sin(ang(no, nf)), mu / math.sin(ang(no, ni))]
    assert k == pytest.approx([k[0]] * 3, rel=1e-12)
    assert 0 < mu < 0.2 and lam == pytest.approx(1, abs=0.05)


def test_rib_force_vanishes_as_the_taper_closes():
    mus = [T.bearing(TRB | {"alpha_i_deg": a}).ratios()[1] for a in (12.0, 14.0, 14.9)]
    assert mus[0] > mus[1] > mus[2] > 0 and mus[2] < 0.01


def test_pure_thrust():
    b = T.bearing(TRB)
    r = T.distribute(b, 0.0, 8000.0)
    assert np.ptp(r["Q"]) < 1e-9 * r["Qmax"]
    assert r["Q"][0] == pytest.approx(8000 / (17 * math.sin(math.radians(15))), rel=1e-9)
    assert r["dr"] == 0.0


def test_combined_load_balances():
    b = T.bearing(TRB | {"profile": {"kind": "arc", "R": 1500}})
    r = T.distribute(b, 6000.0, 4000.0)
    psi = np.radians(r["psi_deg"])
    assert np.sum(r["Q"]) * math.sin(b.ao) == pytest.approx(4000, rel=1e-8)
    assert np.sum(r["Q"] * np.cos(psi)) * math.cos(b.ao) == pytest.approx(6000, rel=1e-8)
    assert r["Q"][0] == r["Qmax"] and r["loaded"] <= 17
    s = T.stresses(b, r["q"])
    assert s["inner"]["p"].max() > s["outer"]["p"].max()  # the cone: more curved and slightly more load
    p = T.rib_stress(b, float(r["Qf"].max()))
    Es = b.Es
    a = (3 * float(r["Qf"].max()) * 40 / (4 * Es)) ** (1 / 3)  # sphere on flat: a³ = 3QR/(4E*), p = 3Q/(2πa²)
    assert p == pytest.approx(3 * float(r["Qf"].max()) / (2 * math.pi * a * a), rel=1e-12)


def test_single_row_needs_axial_force():
    with pytest.raises(ValueError, match="needs an axial force"):
        T.distribute(T.bearing(TRB), 5000.0, 0.0)
    with pytest.raises(ValueError, match="cone angle"):
        T.bearing(TRB | {"alpha_i_deg": 16})


def test_on_apex_cone_angle():
    ai = T.on_apex_cone_angle(9.0, 52.0, 15.0)
    am, ph = math.radians((15.0 + ai) / 2), math.radians((15.0 - ai) / 2)
    assert math.tan(ph) == pytest.approx(9.0 * math.sin(am) / 52.0, rel=1e-12)  # the roller's own apex on the axis
    # then the roller axis, the cup line and the cone line all meet the bearing axis at one point
    rc = 52.0 / 2                                                               # roller centre on the pitch circle
    z_axis = -rc / math.tan(am)
    for side, a in ((1, 15.0), (-1, ai)):
        r0 = rc + side * 4.5 * math.cos(am)
        z0 = -side * 4.5 * math.sin(am)
        assert z0 - r0 / math.tan(math.radians(a)) == pytest.approx(z_axis, rel=1e-9)
