"""Round 64 step 1: standard problems for the bearing kernel, each against a closed form or a published formula.

  - Hertz: sphere on flat reduces to a³ = 3QR/(4E*), δ = a²/R, p = 3Q/(2πa²) (Johnson, Contact Mechanics, §3.4/4.2)
  - Hertz: ball–groove ellipticity within 3 % of Hamrock & Brewe's fit k = 1.0339 (R_y/R_x)^0.636; δ ∝ Q^(2/3)
  - Load distribution, zero clearance, radial only: Q_max = F_r / Σ cos^2.5 ψ (Stribeck's discrete sum; Z·Q_max/F_r
    near 4.37 for nine balls)
  - Pure thrust: every ball equal and Harris's equilibrium F_a / (Z K A^1.5) = sin α (cos α₀/cos α − 1)^1.5 holds
  - Equilibrium of combined loads and of a moment; clearance unloads balls
  - Fits: Lamé displacement compatibility; temperature change of the clearance
  - EHL: Hamrock–Dowson exponents (h_min ∝ u^0.68, ∝ Q^−0.073)
  - Fault frequencies: BPFO + BPFI = Z·f_r (inner ring turning); FTF = f_r (1 − γ)/2
"""

import math

import numpy as np
import pytest

from bearingkit import ball as B
from bearingkit import clearance as C
from bearingkit import ehl as L
from bearingkit import hertz as H

ES = H.e_star(206000, 0.3, 206000, 0.3)
B209 = {"D": 12.7, "Z": 9, "dm": 65.0, "fi": 0.52, "fo": 0.52}  # sizes of a 209-size deep groove bearing


def test_hertz_sphere_on_flat():
    R, Q = 10.0, 1000.0
    c = H.solve(Q, (1 / R, 1 / R, 0, 0), ES)
    a = (3 * Q * R / (4 * ES)) ** (1 / 3)
    assert c.a == pytest.approx(a, rel=1e-12) and c.b == pytest.approx(a, rel=1e-12)
    assert c.delta == pytest.approx(a * a / R, rel=1e-12)
    assert c.p_max == pytest.approx(3 * Q / (2 * math.pi * a * a), rel=1e-12)


@pytest.mark.parametrize("ring", ["inner", "outer"])
def test_hertz_ellipse_against_hamrock_brewe(ring):
    rho = H.curvatures(12.7, 65.0, 0.0, 0.52, ring)
    Rx, Ry = 1 / (rho[0] + rho[2]), 1 / (rho[1] + rho[3])
    c = H.solve(5000, rho, ES)
    assert c.kappa == pytest.approx(1.0339 * (Ry / Rx) ** 0.636, rel=0.03)
    c2 = H.solve(5000 * 8, rho, ES)
    assert c2.delta / c.delta == pytest.approx(8 ** (2 / 3), rel=1e-9)        # δ ∝ Q^(2/3)
    assert c2.p_max / c.p_max == pytest.approx(8 ** (1 / 3), rel=1e-9)        # p ∝ Q^(1/3)
    assert c.a * c.b * c.p_max * 2 * math.pi / 3 == pytest.approx(5000, rel=1e-12)


def test_stribeck_zero_clearance():
    b = B.bearing(B209 | {"Pd": 0.0})
    r = B.distribute(b, Fr=8900)
    c = np.cos(np.radians(r["psi_deg"]))
    assert r["Qmax"] == pytest.approx(8900 / np.sum(np.where(c > 0, c, 0) ** 2.5), rel=1e-9)
    assert 4.3 < b.Z * r["Qmax"] / 8900 < 4.45


def test_pure_thrust():
    b = B.bearing(B209 | {"Pd": 0.0152})
    r = B.distribute(b, Fa=5000)
    assert np.ptp(r["Q"]) < 1e-9 * r["Qmax"]
    a, a0 = math.radians(r["alpha_deg"][0]), b.alpha0
    assert r["Q"][0] == pytest.approx(5000 / (b.Z * math.sin(a)), rel=1e-9)
    lhs = 5000 / (b.Z * b.Kn(a) * b.A**1.5)
    assert lhs == pytest.approx(math.sin(a) * (math.cos(a0) / math.cos(a) - 1) ** 1.5, rel=1e-9)
    assert a > a0                                                              # the load raises the contact angle


def test_combined_load_moment_and_clearance():
    b = B.bearing(B209 | {"alpha0_deg": 25.0})
    r = B.distribute(b, Fr=3000, Fa=4000, M=20000)
    psi = np.radians(r["psi_deg"])
    al = np.radians(r["alpha_deg"])
    Ri = b.dm / 2 + (b.fi - 0.5) * b.D * math.cos(b.alpha0)
    assert np.sum(r["Q"] * np.sin(al)) == pytest.approx(4000, rel=1e-8)
    assert np.sum(r["Q"] * np.cos(al) * np.cos(psi)) == pytest.approx(3000, rel=1e-8)
    assert np.sum(r["Q"] * np.sin(al) * Ri * np.cos(psi)) == pytest.approx(20000, rel=1e-8)
    tight = B.distribute(B.bearing(B209 | {"Pd": 0.0}), Fr=8900)
    loose = B.distribute(B.bearing(B209 | {"Pd": 0.05}), Fr=8900)
    assert loose["loaded"] < tight["loaded"] and loose["Qmax"] > tight["Qmax"]


def test_bad_bearings_are_refused():
    with pytest.raises(B.BallError, match="fit round"):
        B.bearing(B209 | {"Z": 17})
    with pytest.raises(B.BallError, match="between 0.5 and 0.6"):
        B.bearing(B209 | {"fi": 0.5})


def test_fits_and_temperature():
    r = C.fit_inner(0.02, 45, 52, 0)
    a, b = 22.5, 26.0
    p = r["p"]
    compat = p * a / 206000 * ((b * b + a * a) / (b * b - a * a) + 0.3) + p * a / 206000 * (1 - 0.3)
    assert compat == pytest.approx(0.01, rel=1e-12) and 0 < r["growth"] < 0.02
    o = C.fit_outer(0.02, 100, 88)
    assert 0 < o["shrink"] < 0.02
    ch = C.chain(0.015, 52.3, 77.7, inner={"interference": 0.02, "d": 45, "d_ie": 52.3}, T_i=40, T_o=40)
    assert ch["mounted"] == pytest.approx(0.015 - C.fit_inner(0.02, 45, 52.3)["growth"])
    assert ch["thermal"] == pytest.approx(11.5e-6 * 20 * (77.7 - 52.3))       # same temperature: grows with size


def test_film_thickness_exponents():
    rho = H.curvatures(12.7, 65.0, 0.0, 0.52, "inner")
    f1 = L.film(2000, rho, ES, 0.04, 2e-8, 1000.0)
    f2 = L.film(2000, rho, ES, 0.04, 2e-8, 2000.0)
    f3 = L.film(4000, rho, ES, 0.04, 2e-8, 1000.0)
    assert f2["h_min"] / f1["h_min"] == pytest.approx(2**0.68, rel=1e-12)
    assert f3["h_min"] / f1["h_min"] == pytest.approx(2**-0.073, rel=1e-12)
    assert f2["h_c"] / f1["h_c"] == pytest.approx(2**0.67, rel=1e-12)
    assert 0 < f1["h_min"] < f1["h_c"]


def test_fault_frequencies():
    b = B.bearing(B209 | {"Pd": 0.0})
    f = B.frequencies(b, 1800)
    g = b.D / b.dm
    assert f["BPFO"] + f["BPFI"] == pytest.approx(b.Z * 30.0, rel=1e-12)
    assert f["FTF"] == pytest.approx(30 * (1 - g) / 2, rel=1e-12)
    assert f["BSF"] == pytest.approx(b.dm / (2 * b.D) * 30 * (1 - g * g), rel=1e-12)


def test_radial_load_with_clearance_sits_at_groove_bottom():
    b = B.bearing(B209 | {"Pd": 0.05})
    r = B.distribute(b, Fr=8900)
    assert np.max(np.abs(r["alpha_deg"])) < 1e-12                               # balls at the groove bottoms
    c = np.cos(np.radians(r["psi_deg"]))
    dl = np.maximum(r["dr"] * c - 0.05 / 2, 0)                                 # δ(ψ) = δ_r cos ψ − P_d/2
    assert r["Q"] == pytest.approx(b.Kn(0.0) * dl**1.5, rel=1e-9, abs=1e-9)
    assert np.sum(r["Q"] * c) == pytest.approx(8900, rel=1e-9)


def test_fixed_tilt_keeps_ring_square():
    b = B.bearing(B209 | {"alpha0_deg": 25.0})
    r = B.distribute(b, Fr=3000, Fa=4000, tilt="fixed")
    al, psi = np.radians(r["alpha_deg"]), np.radians(r["psi_deg"])
    assert r["theta"] == 0.0
    assert np.sum(r["Q"] * np.sin(al)) == pytest.approx(4000, rel=1e-8)
    assert np.sum(r["Q"] * np.cos(al) * np.cos(psi)) == pytest.approx(3000, rel=1e-8)
    assert r["M"] > 0                                                           # it pushes a moment on the shaft
    free = B.distribute(b, Fr=3000, Fa=4000, M=r["M"])                          # given that moment, it stays square
    assert abs(free["theta"]) < 1e-9 and free["Qmax"] == pytest.approx(r["Qmax"], rel=1e-6)
