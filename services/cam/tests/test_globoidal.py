"""Standard problems for indexing programs and the globoidal (roller gear) cam, step 4a of round 39.

The envelope is checked against itself by independent means: the normal of the generated surface, found by numerical
differentiation of the surface grid, must equal the roller's normal at every contact point (the condition of meshing,
Litvin & Fuentes, Gear Geometry and Applied Theory, ch. 6); the pressure angle then follows from that normal. Closed
forms written out here:
  - pressure angle of a roller gear cam: tan α = ρ φ′ / (C − ρ cos φ)
  - rib thickness across the bisector of two rollers at the foot of radius ρ: 2ρ sin(π/n) − 2 r_r / cos(π/n)
  - in a dwell the roller stands still, so the flank across the contact line is a circle about the cam axis:
    normal curvature = (1/R₀)·cos(angle between the normal and the direction to the axis)
"""

import math

import numpy as np
import pytest

from camkit import globoidal as G
from camkit.program import Program, ProgramError

ATC = {"unit": "rad", "advance_deg": 180, "segments": [
    {"kind": "rise", "deg": 60, "h_deg": 65, "law": "mod_sine"}, {"kind": "dwell", "deg": 50},
    {"kind": "rise", "deg": 120, "h_deg": 180, "law": "mod_sine"}, {"kind": "dwell", "deg": 50},
    {"kind": "return", "deg": 60, "h_deg": 65, "law": "mod_sine"}, {"kind": "dwell", "deg": 20}]}
GEO = {"C": 170, "n": 8, "Rp": 40, "rr": 9, "b": 15, "L": 56, "phase_deg": 22.5}


def test_indexing_program():
    p = Program.from_dict(ATC)
    s0 = p.eval(np.array([0.0]))[0][0]
    s_end = p.eval(np.array([2 * math.pi - 1e-9]))[0][0]
    assert abs(s0) < 1e-12 and abs(s_end - math.pi) < 1e-6
    assert p.joints() == []  # modified sine everywhere: smooth to the acceleration, also from cycle to cycle
    with pytest.raises(ProgramError):
        Program.from_dict(ATC | {"advance_deg": 120})  # the segments move 180°, not 120°
    # a table with an advance: the steady part is added back, derivatives continuous across 360°
    th = np.arange(0, 360, 5.0)
    s = np.radians(th / 2) + 0.05 * np.sin(np.radians(2 * th))
    t = Program.from_dict({"unit": "rad", "advance_deg": 180, "table": {"deg": th.tolist(), "s": s.tolist()}})
    x = np.radians(np.array([2.5, 182.5, 357.5]))
    assert np.allclose(t.eval(x)[0], x / 2 + 0.05 * np.sin(2 * x), atol=2e-5)
    assert np.allclose(t.eval(x)[1], 0.5 + 0.1 * np.cos(2 * x), atol=2e-4)


def _flank(prog, geo, m=1440, k=21):
    g = G.globoid(geo)
    return g, G.surfaces(g, Program.from_dict(prog), m=m, k=k)


def test_envelope_normal_equals_roller_normal():
    g, sfs = _flank(ATC, GEO)
    worst, count = 0.0, 0
    for sf in sfs:
        Q, N, on = sf["Q"], sf["N"], sf["on"]
        dt, dr = sf["theta"][1] - sf["theta"][0], sf["rho"][1] - sf["rho"][0]
        St = (np.roll(Q, -1, axis=1) - np.roll(Q, 1, axis=1)) / (2 * dt)
        Sr = np.gradient(Q, dr, axis=2)
        n_num = np.cross(St, Sr, axis=0)
        n_num /= np.linalg.norm(n_num, axis=0)
        ok = on & np.roll(on, 1, axis=0) & np.roll(on, -1, axis=0)
        ok[:, [0, -1]] = False
        if not ok.any():
            continue
        cosang = np.abs((n_num * N).sum(0))[ok]
        worst = max(worst, float(np.max(1 - cosang)))
        count += int(ok.sum())
    assert count > 5000
    assert worst < 1e-5  # normals agree to about 0.25°


def test_pressure_angle_formula():
    g = G.globoid(GEO)
    rng = np.random.default_rng(0)
    ang = rng.uniform(-0.8, 0.8, 200)
    dang = rng.uniform(-3, 3, 200)
    rho = rng.uniform(g.rho1, g.rho2, 200)
    for side in (1, -1):
        _, N, t, alpha = G.contact(g, ang, dang, rho, side)
        geo_alpha = np.arccos(np.clip(np.abs((N * t).sum(0)), 0, 1))  # angle between the normal and the motion
        assert np.allclose(geo_alpha, np.arctan(np.abs(rho * dang) / (g.C - rho * np.cos(ang))), atol=1e-12)
        assert np.allclose(alpha, geo_alpha, atol=1e-12)


def test_rib_thickness():
    """Across the bisector of two neighbouring rollers, at the foot of radius ρ: the material between the cylinders,
    found by sampling points and measuring their distance to both roller axes."""
    g = G.globoid(GEO)
    h = math.pi / g.n
    ua = np.array([math.cos(-h), 0.0, math.sin(-h)])
    ub = np.array([math.cos(h), 0.0, math.sin(h)])
    for rho in (g.rho1, g.Rp, g.rho2):
        d = rho * math.cos(h)
        x = np.linspace(-20, 20, 400001)
        pts = np.stack([np.full_like(x, d), np.zeros_like(x), x])
        da = np.linalg.norm(np.cross(pts.T, ua), axis=1)
        db = np.linalg.norm(np.cross(pts.T, ub), axis=1)
        width = (x[1] - x[0]) * np.count_nonzero((da >= g.rr) & (db >= g.rr))
        expect = 2 * rho * math.sin(h) - 2 * g.rr / math.cos(h)
        assert abs(width - expect) < 2e-4
    assert abs(G.thickness(g)["root"] - (2 * g.rho1 * math.sin(h) - 2 * g.rr / math.cos(h))) < 1e-12


def test_dwell_flank_curvature():
    prog = {"unit": "rad", "advance_deg": 45, "segments": [
        {"kind": "dwell", "deg": 120}, {"kind": "rise", "deg": 120, "h_deg": 45, "law": "cycloidal"},
        {"kind": "dwell", "deg": 120}]}
    g, sfs = _flank(prog, GEO, m=2880, k=21)
    sf = next(s for s in sfs if s["roller"] == 0 and s["side"] == 1)  # roller at 22.5°, in the cam during the dwell
    kap = G.flank_curvature(sf)
    j = 240  # 30° into the first dwell
    th = sf["theta"][j]
    P = G.fixed_frame(g, sf["Q"][:, j, :], th)
    Nf = G.fixed_frame(g, sf["N"][:, j, :], th) - G.fixed_frame(g, np.zeros((3, 1)), th)
    R0 = np.hypot(P[0] - g.C, P[1])
    to_axis = np.stack([g.C - P[0], -P[1], np.zeros_like(P[0])]) / R0
    expect = (to_axis * Nf).sum(0) / R0  # curvature vector of the circle about the axis, along the normal into the cam
    assert sf["on"][j].all()
    # convex towards the roller counts positive: curvature vector · normal into the cam
    assert np.allclose(kap[j, 2:-2], expect[2:-2], rtol=2e-3)


def test_undercut_found_only_when_too_fast():
    good = G.analyse({"program": ATC, "globoidal": GEO, "limits": {"phi_rise_deg": 40}})
    ck = {c["id"]: c for c in good["checks"]}
    assert ck["undercut"]["status"] == "pass" and ck["pressure"]["status"] == "pass"
    assert ck["engage"]["status"] == "pass" and ck["rib"]["value"] > 0
    fast = {"unit": "rad", "advance_deg": 180,
            "segments": [{"kind": "rise", "deg": 30, "h_deg": 180, "law": "mod_sine"}, {"kind": "dwell", "deg": 330}]}
    bad = G.analyse({"program": fast, "globoidal": GEO | {"C": 90}})  # (pressure: no limit given → unknown)
    ck = {c["id"]: c for c in bad["checks"]}
    assert ck["undercut"]["status"] == "fail" and ck["pressure"]["status"] == "unknown"


def test_refusals():
    with pytest.raises(G.GloboidError):
        G.globoid(GEO | {"C": 40})  # rollers reach the cam axis
    with pytest.raises(G.GloboidError):
        G.globoid(GEO | {"n": 2})
    with pytest.raises(G.GloboidError):
        G.globoid(GEO | {"L": 70})  # longer than the arc of the rollers' inner ends
    with pytest.raises(G.GloboidError):
        G.analyse({"program": {"unit": "mm", "segments": [{"kind": "dwell", "deg": 360}]}, "globoidal": GEO})
