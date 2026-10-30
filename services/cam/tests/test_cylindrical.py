"""Cylindrical (barrel) cam, round 39 step 8 (plan section 十三). Standard problems against closed forms:

- translating follower, cylindrical roller: tan α = s′ / x at radius x (Norton, barrel cams), largest at the bottom
- oscillating follower at the middle of a symmetric swing (arm square to the cam): tan α = L ψ′ / x
- the flanks satisfy the condition of meshing (n · v_rel = 0) and lie on the roller surface
- where s′ = 0 the flank across the contact line is the developed pitch curve offset by the roller radius:
  radius x² / s″ ∓ r_r (the convex one undercuts when x² / s″ < r_r)
- a cone roller with its apex on the cam axis rolls without sliding in the dwells; a cylindrical roller slides
  by (b/2) / R_p there
- an undercut case is caught; a groove that runs out of the cam is caught
"""

import json
import math
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app import app
from camkit import analyse
from camkit import cylindrical as C
from camkit.globoidal import flank_curvature
from camkit.program import Program

EX = Path(__file__).resolve().parents[1] / "examples"
STEEL = {"E1": 206000, "nu1": 0.3, "E2": 206000, "nu2": 0.3}


def prog_mm(law="cycloidal", h=40, rise=120, ret=120):
    return {
        "unit": "mm",
        "segments": [
            {"kind": "rise", "deg": rise, "h": h, "law": law},
            {"kind": "dwell", "deg": (360 - rise - ret) / 2},
            {"kind": "return", "deg": ret, "h": h, "law": law},
            {"kind": "dwell", "deg": (360 - rise - ret) / 2},
        ],
    }


def cam(**kw):
    d = {"follower": "translating", "roller": "cylinder", "Rp": 60, "rr": 10, "b": 12, "length": 120} | kw
    return d


def check(r, cid):
    return next(c for c in r["checks"] if c["id"] == cid)


def test_translating_pressure_angle_is_the_closed_form():
    r = analyse({"type": "cylindrical", "program": prog_mm(), "cylindrical": cam()})
    smax = 2 * 40 / math.radians(120)  # cycloidal: s′max = 2h/β
    assert check(r, "phi_rise")["value"] == pytest.approx(math.degrees(math.atan(smax / 54)), abs=1e-6)  # bottom
    assert max(r["curves"]["phi_pitch_deg"]) == pytest.approx(math.degrees(math.atan(smax / 60)), abs=1e-5)
    assert check(r, "phi_rise")["status"] == "unknown"  # no limit given: never a pass


def test_oscillating_pressure_angle_at_the_middle_of_the_swing():
    prog = Program.from_dict(
        {
            "unit": "rad",
            "segments": [
                {"kind": "rise", "deg": 120, "h_deg": 30, "law": "cycloidal"},
                {"kind": "dwell", "deg": 60},
                {"kind": "return", "deg": 120, "h_deg": 30, "law": "cycloidal"},
                {"kind": "dwell", "deg": 60},
            ],
        }
    )
    c = C.cyl(cam(follower="oscillating", arm=100), "rad")
    ps = C.pose(c, prog, np.array([[math.radians(60)]]))  # mid-rise: ψ = 0, ψ′ = 2h/β
    assert float(ps["psi"][0, 0]) == pytest.approx(0, abs=1e-12)
    for x in (54, 60, 66):
        for side in (1, -1):
            _, _, _, a, _ = C.contact(c, ps, np.array([[x]]), side)
            assert math.degrees(float(a[0, 0])) == pytest.approx(math.degrees(math.atan(100 * 0.5 / x)), abs=1e-9)


@pytest.mark.parametrize(
    "follower,roller",
    [("translating", "cylinder"), ("translating", "cone"), ("oscillating", "cylinder"), ("oscillating", "cone")],
)
def test_flanks_satisfy_meshing_and_touch_the_roller(follower, roller):
    unit = "mm" if follower == "translating" else "rad"
    p = (
        prog_mm()
        if unit == "mm"
        else {
            "unit": "rad",
            "segments": [
                {"kind": "rise", "deg": 120, "h_deg": 25, "law": "poly345"},
                {"kind": "dwell", "deg": 60},
                {"kind": "return", "deg": 120, "h_deg": 25, "law": "poly345"},
                {"kind": "dwell", "deg": 60},
            ],
        }
    )
    prog = Program.from_dict(p)
    c = C.cyl(cam(follower=follower, roller=roller, arm=120), unit)
    ps = C.pose(c, prog, np.linspace(0, 2 * math.pi, 720, endpoint=False)[:, None])
    for side in (1, -1):
        P, n, _, _, v = C.contact(c, ps, np.linspace(c.x1, c.x2, 7)[None, :], side)
        assert np.max(np.abs((n * v).sum(0))) < 1e-9
        r = np.hypot(P[1] - ps["cy"], P[2] - ps["cz"])
        assert np.max(np.abs(r - c.rho(P[0]))) < 1e-9


def test_flank_curvature_is_the_offset_development_where_the_follower_stops():
    # harmonic rise straight into a harmonic return: at the top s′ = 0 and s″ = −h/2·(π/β)² on both sides
    prog = Program.from_dict(
        {
            "unit": "mm",
            "segments": [
                {"kind": "rise", "deg": 180, "h": 40, "law": "harmonic"},
                {"kind": "return", "deg": 180, "h": 40, "law": "harmonic"},
            ],
        }
    )
    c = C.cyl(cam(), "mm")
    m = 2880
    sfs = C.surfaces(c, prog, m=m, k=9)
    s2 = 40 / 2
    for j, x in enumerate(sfs[0]["rho"]):
        rp = x * x / s2
        got = sorted(float(flank_curvature(s)[m // 2, j]) for s in sfs)
        assert got == pytest.approx(sorted([1 / (rp - 10), -1 / (rp + 10)]), rel=1e-4)


def test_a_cone_rolls_in_the_dwells_a_cylinder_slides():
    prog = Program.from_dict(prog_mm("harmonic"))
    th = np.linspace(0, 2 * math.pi, 720, endpoint=False)
    dwell = (np.degrees(th) > 125) & (np.degrees(th) < 175)
    out = {}
    for roller in ("cylinder", "cone"):
        c = C.cyl(cam(roller=roller), "mm")
        sl = C.sliding(c, C.pose(c, prog, th[:, None]), np.linspace(c.x1, c.x2, 9)[None, :], 1)
        out[roller] = (float(np.nanmax(sl[dwell])), float(np.nanmax(sl)))
    assert out["cone"][0] < 1e-12  # pure rolling while the follower stands
    assert out["cylinder"][0] == pytest.approx(6 / 60, rel=1e-9)  # (b/2)/R_p
    assert out["cone"][1] < out["cylinder"][1]  # and less sliding while it moves


def test_undercut_and_a_groove_out_of_the_cam_are_caught():
    p = {
        "type": "cylindrical",
        "program": prog_mm("harmonic", h=40, rise=40, ret=40),
        "cylindrical": cam(Rp=25, rr=12, b=10, length=150),
    }
    assert check(analyse(p), "undercut")["status"] == "fail"
    p = {"type": "cylindrical", "program": prog_mm(), "cylindrical": cam(length=50)}
    assert check(analyse(p), "end_wall")["status"] == "fail"


def test_wrong_inputs_are_said_plainly():
    with pytest.raises(C.CylError, match="program is in mm"):
        C.cyl(cam(follower="oscillating", arm=100), "mm")
    with pytest.raises(C.CylError, match="arm length"):
        C.cyl(cam(follower="oscillating"), "rad")
    with pytest.raises(C.CylError, match="reaches the cam axis"):
        C.cyl(cam(Rp=8, b=7, bottom=5), "mm")
    with pytest.raises(C.CylError, match="unknown cylindrical"):
        C.cyl(cam(colour="red"), "mm")


def test_min_pitch_radius_meets_the_limit():
    p = {
        "type": "cylindrical",
        "program": prog_mm(),
        "cylindrical": cam(),
        "limits": {"phi_rise_deg": 30, "phi_return_deg": 30},
    }
    rp = C.min_pitch_radius(p)["Rp"]
    r = analyse(dict(p, cylindrical=cam(Rp=rp)))
    assert check(r, "phi_rise")["status"] == "pass"
    assert check(analyse(dict(p, cylindrical=cam(Rp=rp - 0.5))), "phi_rise")["status"] == "fail"
    # closed form at the groove bottom: x1 = s′max / tan 30°, Rp = x1 + b/2
    assert rp == pytest.approx(2 * 40 / math.radians(120) / math.tan(math.radians(30)) + 6, abs=0.02)


@pytest.mark.parametrize("eid", ["barrel-feed", "barrel-fork"])
def test_examples_pass_and_unknowns_stay_unknown(eid):
    p = json.loads((EX / f"{eid}.json").read_text(encoding="utf-8"))
    r = analyse(p)
    assert r["type"] == "cylindrical" and not [c for c in r["checks"] if c["status"] == "fail"]
    assert {c["id"] for c in r["checks"]} >= {"phi_rise", "undercut", "stress", "torque", "sliding", "end_wall"}
    assert check(r, "phi_rise")["status"] == "pass" and check(r, "stress")["status"] == "unknown"  # no allowed stress
    assert check(r, "stress")["value"] > 0  # computed, not judged
    q = dict(p, loads={}, material={})
    r = analyse(q)
    assert check(r, "stress")["status"] == "unknown" and check(r, "torque")["status"] == "unknown"
    assert r["status"] == "unknown"


def test_api_and_a_system_with_a_cylindrical_cam():
    c = TestClient(app)
    p = json.loads((EX / "barrel-feed.json").read_text(encoding="utf-8"))
    r = c.post("/api/analyse", json={"project": p}).json()
    assert r["type"] == "cylindrical" and r["geometry"]["development"]["outer"][0]["u"]
    r = c.post("/api/min-pitch-radius", json={"project": p}).json()
    assert 60 < r["Rp"] < 75
    r = c.post(
        "/api/analyse", json={"project": dict(p, cylindrical=dict(p["cylindrical"], follower="oscillating", arm=100))}
    )
    assert r.status_code == 422 and "直动从动件的运动程序用毫米" in r.json()["detail"]["zh"]
    from camkit import system as S

    sysp = json.loads((EX / "atc-globoidal.json").read_text(encoding="utf-8"))
    sysp["cams"].append(
        {
            "id": "barrel",
            "name": {"zh": "送料", "en": "Feed"},
            "type": "cylindrical",
            "program": p["program"],
            "cylindrical": p["cylindrical"],
            "material": STEEL,
            "limits": p["limits"],
            "output": {"m": 3.5, "load": 120},
        }
    )
    out = S.analyse(sysp, quick=True)
    assert any(x.get("id") == "barrel" for x in out["cams"])


def test_ai_drafting_reads_the_cylindrical_follower():
    import ai_api

    p = json.loads((EX / "barrel-fork.json").read_text(encoding="utf-8"))
    p["mechanism"] = {"follower": "translating"}  # the page also keeps disk fields; they are not this cam's
    follower, put, run = ai_api._target(p, "")
    assert follower == "oscillating"
    assert run(put(p["program"]))["type"] == "cylindrical"
    s = ai_api._summary(p)
    assert s["type"] == "cylindrical" and "cylindrical" in s and "mechanism" not in s
