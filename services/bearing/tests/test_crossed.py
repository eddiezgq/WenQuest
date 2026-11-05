"""Crossed roller bearings (round 64, plan section 十九, X1): standard problems. The bearing is made up."""

import math

import numpy as np
import pytest

from bearingkit import crossed as CX

SPEC = dict(Dw=8.0, L=7.5, Z=30, dm=100.0, alpha_deg=45.0)


def make(Gr=0.0, profile=None, **kw):
    return CX.Crossed(**(SPEC | kw), Gr=Gr, profile=profile or {"kind": "straight"})


def test_preload_alone_is_shared_equally_and_inverts():
    Gr = CX.clearance_for_preload(make(), 1500.0)
    b = make(Gr)
    assert Gr < 0 and b.preload_force() == pytest.approx(1500.0, rel=1e-9)
    u = b.solve([0, 0, 0, 0, 0])
    r = b.rollers(u)
    assert np.abs(u).max() < 1e-12
    assert r["Fa_plus"] == pytest.approx(1500.0, rel=1e-9) and r["Fa_minus"] == pytest.approx(1500.0, rel=1e-9)
    assert r["loaded"] == 30 and np.ptp(r["Q"]) <= 1e-9 * r["Qmax"]
    assert make(0.01).preload_force() == 0.0 and CX.clearance_for_preload(make(), 0) == 0.0


def test_axial_load_one_set_only_without_preload():
    b = make(0.0)
    u = b.solve([0, 0, 2500.0, 0, 0])
    r = b.rollers(u)
    assert r["loaded_plus"] == 15 and r["loaded_minus"] == 0
    assert r["Fa_plus"] == pytest.approx(2500.0, rel=1e-9)
    assert np.ptp(r["Q"][b.sig > 0]) <= 1e-9 * r["Qmax"]


@pytest.mark.parametrize("Gr", [-0.006, 0.0, 0.004])
@pytest.mark.parametrize("P", [[3000.0, 0, 0, 0, 0], [1500.0, -400.0, 900.0, 1.2e5, -4e4], [0, 0, 0, 2e5, 0]])
def test_balance(Gr, P):
    b = make(Gr, {"kind": "partial", "R": 500.0, "flat": 4.0})
    u = b.solve(P)
    r = b.forces(u) - np.asarray(P)
    scale = max(np.abs(P[:3]).max(), np.abs(P[3:]).max() / 50, 1.0)
    assert np.abs(r[:3]).max() <= 1e-8 * scale and np.abs(r[3:]).max() <= 1e-8 * scale * 50


def test_pure_moment_is_antisymmetric():
    """Under a moment about y the set facing +z at ψ carries what the other set carries at ψ + π."""
    b = make(-0.004)
    r = b.rollers(b.solve([0, 0, 0, 1.5e5, 0]))
    Q, Z = r["Q"], b.Z
    for j in range(Z):
        k = (j + Z // 2) % Z  # ψ + π: Z/2 = 15 is odd, so the facing flips
        assert b.sig[k] == -b.sig[j]
        assert Q[k] == pytest.approx(Q[j], rel=1e-7, abs=1e-9 * r["Qmax"])
    # the moment equals the sum over the rollers (the load's own balance, checked another way)
    u = b.solve([0, 0, 0, 1.5e5, 0])
    assert b.forces(u)[3] == pytest.approx(1.5e5, rel=1e-9)


def test_stiffness_from_the_slices_by_hand():
    """At a uniform preload (straight rollers, every slice closed by δ) each slice is a spring of slope
    (10/9) w k δ^(1/9): axial stiffness Σ slope·sin²α, radial Σ slope·cos²α cos²ψ, tilt Σ slope·G_β² (decoupled by
    the alternating facing)."""
    b = make(-0.006)
    u = np.zeros(5)
    st = b.stiffness(u)
    d = b.closing(u)
    slope = (10 / 9) * b.w * b.k * d ** (1 / 9)
    assert st["axial"] * 1000 == pytest.approx((slope * b.G[2] ** 2).sum(), rel=1e-6)
    assert st["radial"] * 1000 == pytest.approx((slope * b.G[0] ** 2).sum(), rel=1e-6)
    assert st["tilt"] * 1e6 == pytest.approx((slope * b.G[3] ** 2).sum(), rel=1e-6)
    assert st["axial"] == pytest.approx(2 * st["radial"], rel=1e-6)  # 45°: Z/2 against Z/4


def test_more_preload_more_tilt_stiffness():
    P = CX.load(Fr=1000.0, Fa=500.0, M=5e4)
    c = CX.setting_curve(lambda g: make(g, {"kind": "arc", "R": 400.0}), P, 10.0, -15.0, 11)
    k = [x for x in c["k_tilt"] if x is not None]
    assert len(k) == 11 and all(b >= a * (1 - 0.01) for a, b in zip(k, k[1:], strict=False)) and k[-1] > 1.3 * k[0]
    pre = c["preload"]
    assert all(b >= a for a, b in zip(pre, pre[1:], strict=False)) and pre[0] == 0.0 and pre[-1] > 0


def test_geometry_errors():
    for bad, msg in (
        (dict(alpha_deg=None), "contact angle"),
        (dict(alpha_deg=80.0), "contact angle"),
        (dict(Z=3), "at least 4"),
        (dict(Z=40, Dw=8.0), "do not fit"),
    ):
        with pytest.raises(ValueError, match=msg):
            make(**bad)
    with pytest.raises(ValueError, match="crown radius"):
        make(profile={"kind": "arc"})
    assert math.isclose(make().ca, math.sqrt(0.5))


def test_the_project_and_its_checks():
    import copy
    import json
    from pathlib import Path

    from fastapi.testclient import TestClient

    import app as service
    from bearingkit import parts as PT
    from bearingkit.analyze import analyse, geometry_of

    ex = json.loads((Path(__file__).resolve().parents[1] / "examples" / "scene-crossed.json").read_text("utf-8"))
    r = analyse(ex)
    ids = {c["id"]: c for c in r["checks"]}
    assert r["type"] == "crossed" and r["status"] == "unknown"  # the ratings wait for the standard
    assert {"p_inner", "p_outer", "x_both", "k_tilt", "k_axial", "k_radial", "x_fit", "x_lands"} <= set(ids)
    assert ids["x_both"]["status"] == "pass" and ids["x_gr"]["value"] == pytest.approx(-10.0)
    # the joint with a horizontal axis and one bearing: the overhung weight is the moment W·x
    assert r["crossed"]["P"] == pytest.approx([1200.0, 0, 0, 1200.0 * 60, 0])
    assert r["scenario"]["cases"][0]["M"] == pytest.approx(72000.0)
    assert len(r["setting_curve"]["e_um"]) == 21 and r["profile"]["inner"]
    # preload given as a force: the same as the clearance that gives it
    q = copy.deepcopy(ex)
    q["pair"].update({"setting": "preload", "preload": ids["preload"]["value"]})
    assert [c["value"] for c in analyse(q)["checks"] if c["id"] in ("p_inner", "k_tilt")] == pytest.approx(
        [ids["p_inner"]["value"], ids["k_tilt"]["value"]], rel=1e-6
    )
    # too little preload for a large moment: a set unloads, the check fails
    q = copy.deepcopy(ex)
    q["pair"]["endplay"] = -0.5
    q["scenario"]["W"] = 6000
    assert {c["id"]: c for c in analyse(q)["checks"]}["x_both"]["status"] == "fail"
    # rollers longer than Dw·tan α would hit the other face
    q = copy.deepcopy(ex)
    q["inner"]["Lw"] = 8.5
    assert {c["id"]: c for c in analyse(q)["checks"]}["x_fit"]["status"] == "fail"
    # the rings for drawings and 3D: closed V-groove profiles, the rollers alternating
    g = geometry_of(ex)
    pr = PT.parts(g)
    fr = PT._elements(g, pr)
    assert pr["element_kind"] == "crossed" and len(fr) == 32
    for k, sg in ((0, 1), (1, -1)):  # each axis in its own meridian plane, the two sets turned opposite ways
        er = np.asarray(fr[k].o, float) / np.linalg.norm(fr[k].o)
        assert np.dot(fr[k].z, [0, 0, 1]) == pytest.approx(math.sqrt(0.5)) and np.dot(fr[k].z, er) == pytest.approx(
            -sg * math.sqrt(0.5)
        )
    # errors in Chinese
    c = TestClient(service.app)
    q = copy.deepcopy(ex)
    q["inner"]["alpha0_deg"] = None
    e = c.post("/api/analyse", json=q)
    assert e.status_code == 422 and "接触角" in e.json()["detail"]["zh"]
    q = copy.deepcopy(ex)
    q["pair"]["endplay"] = None
    e = c.post("/api/analyse", json=q)
    assert e.status_code == 422 and "径向游隙" in e.json()["detail"]["zh"]
