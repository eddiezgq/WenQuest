"""Flexible bearings of harmonic reducers (round 64, plan section 十八, H1): standard problems.

The bearing here is made up (a thin ball bearing of the usual proportions), not a maker's."""

import math

import numpy as np
import pytest

from bearingkit import ball as BL
from bearingkit import flex as FX

G = dict(
    d=25.0,
    D=34.0,
    B=6.4,
    Dw=2.4,
    Z=26,
    dm=29.5,
    fi=0.52,
    fo=0.53,
    Pd=0.01,
    E=206000.0,
    nu=0.3,
    cam={"kind": "cosine", "w0": 0.2},
)


def test_ring_series_and_the_textbook_ring():
    th = np.array([0.0, 0.3, 1.0, 2.5, math.pi, 4.0, 6.0])
    n = np.arange(2, 200001)
    for t in th:
        assert FX.S1(t) == pytest.approx(np.sum(np.cos(n * t) / (n * n - 1.0)), abs=2e-5)
        assert FX.S2(t) == pytest.approx(np.sum(np.cos(n * t) / (n * n - 1.0) ** 2), abs=1e-12)
    # two opposite inward loads P on a thin ring (inextensional): the diameter shortens by (π² − 8)/(4π) P R³/EI,
    # the bending moment is P R/π under the loads and P R (1/2 − 1/π) half way between
    R = FX.Ring(30.0, 2.0, 6.0, 206000.0)
    P = 100.0
    dd = 2 * P * R.R**3 / (math.pi * R.EI) * (FX.S2(0) + FX.S2(math.pi))
    assert dd == pytest.approx((math.pi**2 - 8) / (4 * math.pi) * P * R.R**3 / R.EI, rel=1e-12)
    M = lambda t: R.EI * P * (R.dk_point(t) + R.dk_point(t - math.pi))  # noqa: E731
    assert abs(M(0.0)) == pytest.approx(P * R.R / math.pi, rel=1e-12)
    assert abs(M(math.pi / 2)) == pytest.approx(P * R.R * (0.5 - 1 / math.pi), rel=1e-12)
    # N equal loads equally spaced (α = π/N): moment (P R/2)(1/α − cot α) under a load, (P R/2)(1/sin α − 1/α)
    # between (by Castigliano, the same way as two loads)
    for N in (3, 4, 6):
        a = math.pi / N
        Mk = lambda t: R.EI * P * sum(R.dk_point(t - 2 * a * k) for k in range(N))  # noqa: E731, B023
        assert abs(Mk(0.0)) == pytest.approx(P * R.R / 2 * (1 / a - 1 / math.tan(a)), rel=1e-12)
        assert abs(Mk(a)) == pytest.approx(P * R.R / 2 * (1 / math.sin(a) - 1 / a), rel=1e-12)


def test_zone_load_series_is_the_sum_of_point_loads():
    R = FX.Ring(17.0, 1.0, 6.4, 206000.0)
    F, beta = 250.0, math.radians(25)
    th = np.linspace(0, 2 * math.pi, 37)
    u, dk, N0 = R.zones(F, beta, th)
    m = 4000
    s = np.concatenate([np.linspace(-beta, beta, m, endpoint=False) + beta / m])
    p0 = F / (2 * R.R * math.sin(beta))
    w = -p0 * R.R * (2 * beta / m)  # each piece: an inward point load
    up = sum(w * (R.u_point(th - x) + R.u_point(th - x - math.pi)) for x in s)
    kp = sum(w * (R.dk_point(th - x) + R.dk_point(th - x - math.pi)) for x in s)
    assert np.abs(u - up).max() <= 1e-5 * np.abs(up).max()
    assert np.abs(dk - kp).max() <= 1e-3 * np.abs(kp).max()
    assert N0 == pytest.approx(-2 * p0 * beta * R.R / math.pi)


def test_a_rigid_outer_ring_gives_hertz_directly():
    """With a stiff outer ring the balls take up exactly what the cam pushes them out by: Q = K (w − P_d/2)^1.5."""
    bb = BL.bearing({"D": 2.4, "Z": 26, "dm": 29.5, "fi": 0.52, "fo": 0.53, "Pd": 0.01})
    cam = FX.Cam("cosine", 12.5, w0=0.01)
    stiff = FX.Ring(16.5, 1.0, 6.4, 206000.0 * 1e9)
    s = FX.solve(bb, cam, stiff, 0.0)
    want = bb.Kn(0.0) * np.maximum(cam.w(s["phi"]) - bb.Pd / 2, 0) ** 1.5
    assert s["Q"] == pytest.approx(want, rel=1e-6, abs=1e-9)


@pytest.mark.parametrize("w0", [0.05, 0.2])
@pytest.mark.parametrize("F", [0.0, 300.0])
def test_balance_and_contact_law(w0, F):
    g = dict(G, cam={"kind": "cosine", "w0": w0}, F=F, beta_deg=30)
    r = FX.analyse(g)
    for s in r["runs"]:
        Q, ph = s["Q"], s["phi"]
        assert abs(np.cos(ph) @ Q) <= 1e-8 * Q.max() and abs(np.sin(ph) @ Q) <= 1e-8 * Q.max()
        ld = Q > 0
        assert np.abs(s["delta"][ld] - (Q[ld] / s["K"]) ** (2 / 3)).max() <= 1e-8 * w0
        assert (s["delta"][~ld] <= 1e-12).all()
    # the bending of the inner ring forced to w0 cos 2φ: σ = E (t/2) · 3 w0 / R²
    i = r["inner"]
    assert r["sig_i_max"] == pytest.approx(206000 * i.t / 2 * 3 * w0 / i.R**2, rel=1e-9)
    assert r["sig_o_amp"] > 0 and r["sig_o_min"] < 0 < r["sig_o_max"]


def test_the_meshing_load_adds_to_the_long_axis_balls():
    a = FX.analyse(G)
    b = FX.analyse(dict(G, F=400.0, beta_deg=25))
    assert b["Qmax"] > a["Qmax"] and b["p_o_max"] > a["p_o_max"]
    # the zone load pushes the outer ring in at the long axis: the balls there carry it
    w = b["worst"]
    near = np.abs(np.cos(w["phi"])) > math.cos(math.radians(40))
    assert w["Q"][near].sum() > a["worst"]["Q"][near].sum()


def test_ellipse_and_points_agree_with_the_cosine_cam():
    w0, r0 = 0.05, 12.5
    cos = FX.analyse(dict(G, cam={"kind": "cosine", "w0": w0}))
    ell = FX.analyse(dict(G, cam={"kind": "ellipse", "a": r0 + w0, "b": r0 - w0}))
    pts = [[k, w0 * math.cos(math.radians(2 * k))] for k in range(0, 360, 10)]
    spl = FX.analyse(dict(G, cam={"kind": "points", "points": pts}))
    assert spl["Qmax"] == pytest.approx(cos["Qmax"], rel=1e-8)
    assert spl["sig_i_max"] == pytest.approx(cos["sig_i_max"], rel=1e-8)
    e = FX.Cam("ellipse", r0, a=r0 + w0, b=r0 - w0)
    epts = [[k, float(e.w(math.radians(k)))] for k in range(0, 360, 5)]
    assert FX.analyse(dict(G, cam={"kind": "points", "points": epts}))["Qmax"] == pytest.approx(ell["Qmax"], rel=1e-6)
    # the ellipse differs from the cosine by terms of order w0²/r0; the ball loads, set by a few µm of squeeze, move by
    # a few per cent, the ring bending hardly
    assert ell["Qmax"] == pytest.approx(cos["Qmax"], rel=0.06)
    assert ell["sig_i_max"] == pytest.approx(cos["sig_i_max"], rel=0.01)
    # an ellipse of the same semi-axes has a slightly shorter perimeter than the bore: reported, not hidden
    assert ell["stretch"] < 0 and abs(ell["stretch"]) < w0**2 / r0


def test_errors():
    for bad, msg in (
        ({"cam": {"kind": "cosine"}}, "w0"),
        ({"cam": {"kind": "ellipse", "a": 12, "b": 13}}, "semi-axes"),
        ({"cam": {"kind": "points", "points": [[0, 0.1], [90, -0.1]]}}, "4 cam points"),
        ({"cam": {"kind": "square"}}, "cosine, ellipse or points"),
        ({"F": 100.0}, "half-angle"),
        ({"dm": 27.0}, "no wall"),
    ):
        with pytest.raises(ValueError, match=msg):
            FX.analyse(dict(G, **bad))


def test_the_project_the_checks_and_the_mounted_shape():
    import json
    from pathlib import Path

    from fastapi.testclient import TestClient

    import app as service
    from bearingkit import flex_check as FC
    from bearingkit.analyze import analyse, geometry_of

    ex = json.loads((Path(__file__).resolve().parents[1] / "examples" / "demo-flex.json").read_text("utf-8"))
    r = analyse(ex)
    ids = {c["id"]: c for c in r["checks"]}
    assert r["type"] == "flex" and geometry_of(ex)["type"] == "deep_groove"  # as made: a thin deep groove bearing
    assert {"flex_sig_i", "flex_sig_a", "p_inner", "p_outer", "Qmax", "loaded", "flex_gap"} <= set(ids)
    assert ids["flex_sig_i"]["status"] == "pass" and ids["C"]["status"] == "unknown" and r["status"] == "unknown"
    assert len(r["flex"]["theta_deg"]) == 360 and len(r["flex"]["balls"]["Q"]) == 26
    # without the meshing load: the assembly bending only, and the loaded case is unknown (never a pass)
    q = json.loads(json.dumps(ex))
    q["flex"]["F"] = None
    ids2 = {c["id"]: c for c in analyse(q)["checks"]}
    assert ids2["flex_load"]["status"] == "unknown" and ids2["Qmax"]["value"] < ids["Qmax"]["value"]
    # no limits: the stress checks are unknown
    q["flex"]["sig_i_allow"] = None
    assert {c["id"]: c for c in analyse(q)["checks"]}["flex_sig_i"]["status"] == "unknown"
    # the mounted shape for FreeCAD: the inner ring's long axis grows by 2 w0, the balls lie between the rings
    m = FC.deformed(ex, n=72)
    xi = max(x for x, _y in m["inner"][0]) - min(x for x, _y in m["inner"][0])
    assert xi == pytest.approx(25.0 + 2 * 0.2, rel=1e-9)
    for x, y in m["balls"]:
        assert 12.5 + 1.05 - 0.25 < math.hypot(x, y) - 1.2 < 17.0
    # the service, in Chinese
    c = TestClient(service.app)
    q["flex"]["cam"] = "ellipse"
    e = c.post("/api/analyse", json=q)
    assert e.status_code == 422 and e.json()["detail"]["zh"].startswith("请填凸轮椭圆")
