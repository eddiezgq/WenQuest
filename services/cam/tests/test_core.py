"""Standard problems for the cam kernel, step 1 of round 39.

Each test states where its reference comes from. References (see docs/实施细则/第39轮):
  [N]  R. L. Norton, Cam Design and Manufacturing Handbook, 3rd ed., 2020
  [C]  F. Y. Chen, Mechanics and Design of Cam Mechanisms, Pergamon, 1982
  [AL] J. Angeles, C. S. López-Cajún, Optimization of Cam Mechanisms, Kluwer, 1991
  [S]  孙桓《机械原理》（凸轮机构一章）
Where a closed form is used it is written out here, so the check does not rest on remembered page numbers.
"""

from math import asin, degrees, pi, radians, sqrt

import numpy as np
import pytest

from camkit import analyse, min_base_radius
from camkit import disk as D
from camkit import dynamics as Y
from camkit.laws import LAWS, coefficients
from camkit.program import Program, ProgramError

RDR = {
    "unit": "mm",
    "segments": [
        {"kind": "rise", "deg": 120, "h": 20, "law": "cycloidal"},
        {"kind": "dwell", "deg": 60},
        {"kind": "return", "deg": 120, "h": 20, "law": "poly345"},
        {"kind": "dwell", "deg": 60},
    ],
}


# ---------------------------------------------------------------- motion laws


@pytest.mark.parametrize(
    ("key", "cv", "ca"),
    [
        ("parabolic", 2.0, 4.0),  # [N][S] constant acceleration
        ("harmonic", pi / 2, pi**2 / 2),  # [N][S] simple harmonic
        ("cycloidal", 2.0, 2 * pi),  # [N][S] cycloidal
        ("mod_trapezoid", 2.0, 8 * pi / (pi + 2)),  # [N][C] modified trapezoid: Ca = 8π/(π+2)
        ("mod_sine", None, 4 * pi**2 / (pi + 4)),  # [N][C] modified sine: Ca = 4π²/(π+4)
        ("poly345", 15 / 8, 10 / sqrt(3)),  # [N] 3-4-5: Cv = 15/8, Ca = 10/√3
        ("poly4567", 35 / 16, None),  # [N] 4-5-6-7: Cv = 35/16
    ],
)
def test_law_coefficients(key, cv, ca):
    c = coefficients(key, 20001)
    if cv is not None:
        assert c["Cv"] == pytest.approx(cv, rel=1e-6)
    if ca is not None:
        assert c["Ca"] == pytest.approx(ca, rel=1e-6)


@pytest.mark.parametrize("key", list(LAWS))
def test_laws_are_consistent(key):
    """f(0)=0, f(1)=1, and each derivative is the slope of the one before (numerically)."""
    u = np.linspace(0, 1, 40001)
    f, v, a, _ = LAWS[key].eval(u)
    assert f[0] == pytest.approx(0, abs=1e-12) and f[-1] == pytest.approx(1, abs=1e-9)
    h = u[1] - u[0]
    assert np.max(np.abs(np.gradient(f, h)[1:-1] - v[1:-1])) < 1e-4
    if key != "uniform":
        inner = slice(2, -2)
        da = np.abs(np.gradient(v, h)[inner] - a[inner])
        assert np.percentile(da, 99) < 1e-2  # piecewise laws: away from their few kinks


# ---------------------------------------------------------------- programs


def test_program_rules():
    with pytest.raises(ProgramError, match="not 360°"):
        Program.from_dict(
            {"segments": [{"kind": "rise", "deg": 100, "h": 10}, {"kind": "return", "deg": 100, "h": 10}]}
        )
    with pytest.raises(ProgramError, match="does not come back"):
        Program.from_dict({"segments": [{"kind": "rise", "deg": 180, "h": 10}, {"kind": "return", "deg": 180, "h": 9}]})
    with pytest.raises(ProgramError, match="below its lowest"):
        Program.from_dict({"segments": [{"kind": "return", "deg": 180, "h": 5}, {"kind": "rise", "deg": 180, "h": 5}]})
    with pytest.raises(ProgramError, match="unknown motion law"):
        Program.from_dict(
            {"segments": [{"kind": "rise", "deg": 180, "h": 5, "law": "magic"}, {"kind": "return", "deg": 180, "h": 5}]}
        )
    p = Program.from_dict(RDR)
    s, s1, s2, _ = p.eval(np.radians([0, 60, 120, 150, 240, 330]))
    assert s.tolist() == pytest.approx([0, 10, 20, 20, 10, 0], abs=1e-9)
    assert s1[1] == pytest.approx(20 * 2 / radians(120))  # cycloidal peak velocity h·Cv/β at mid-rise


def test_impacts_at_the_joints():
    """[S]: constant velocity jumps in velocity at the ends (rigid impact); simple harmonic between dwells jumps in
    acceleration (soft impact); cycloidal is continuous to acceleration."""

    def prog(law):
        return Program.from_dict(
            {
                "segments": [
                    {"kind": "rise", "deg": 150, "h": 10, "law": law},
                    {"kind": "dwell", "deg": 30},
                    {"kind": "return", "deg": 150, "h": 10, "law": law},
                    {"kind": "dwell", "deg": 30},
                ]
            }
        )

    assert {j["kind"] for j in prog("uniform").joints()} == {"velocity"} and len(prog("uniform").joints()) == 4
    assert [j["deg"] for j in prog("harmonic").joints()] == pytest.approx([150, 180, 330, 0])
    assert {j["kind"] for j in prog("harmonic").joints()} == {"acceleration"}
    assert prog("cycloidal").joints() == [] and prog("mod_sine").joints() == []


# ---------------------------------------------------------------- geometry


def eccentric(R=40.0, eps=8.0, rr=10.0):
    """An eccentric circular disk with a central roller follower: the roller centre runs on a circle of radius
    R + rr about the disk centre, so the pitch curve's radius of curvature is R + rr everywhere and the largest
    pressure angle is asin(eps/(R + rr)) (pure geometry)."""
    deg = np.arange(0, 360, 1.0)
    th = np.radians(deg)
    yc = -eps * np.cos(th) + np.sqrt((R + rr) ** 2 - (eps * np.sin(th)) ** 2)
    prog = Program.from_dict({"unit": "mm", "table": {"deg": deg.tolist(), "s": (yc - yc.min()).tolist()}})
    return prog, yc.min() - rr


@pytest.mark.parametrize("sigma", [1, -1])
def test_eccentric_circle(sigma):
    prog, rb = eccentric()
    g = D.analyse(D.Mechanism(rb=rb, rr=10, sigma=sigma), prog)
    assert g["rho_pitch"] == pytest.approx(np.full_like(g["rho_pitch"], 50.0), abs=2e-3)
    assert g["rho_profile"] == pytest.approx(np.full_like(g["rho_pitch"], 40.0), abs=2e-3)
    assert degrees(np.max(g["phi"])) == pytest.approx(degrees(asin(8 / 50)), abs=1e-4)
    r = np.hypot(*g["profile"])  # the profile is the 40 mm disk itself
    assert np.ptp(r) == pytest.approx(2 * 8, abs=1e-3)


@pytest.mark.parametrize("sigma", [1, -1])
def test_offset_translating_pressure_angle(sigma):
    """[S][N]: tan φ = |s' − σe| / (√(r_p² − e²) + s) for an offset translating roller follower; the offset on the
    right side (σe > 0) lowers the pressure angle of the rise."""
    p = Program.from_dict(RDR)
    g = D.analyse(D.Mechanism(rb=40, rr=10, e=8, sigma=sigma), p)
    s0 = sqrt(50**2 - 8**2)
    ref = np.arctan(np.abs(g["s1"] - sigma * 8) / (s0 + g["s"]))
    assert np.max(np.abs(g["phi"] - ref)) < 1e-12
    up = g["s1"] > 0
    rise = {sg: np.max(D.analyse(D.Mechanism(rb=40, rr=10, e=8, sigma=sg), p)["phi"][up]) for sg in (1, -1)}
    assert rise[1] < rise[-1]


@pytest.mark.parametrize("sigma", [1, -1])
def test_oscillating_roller_pressure_angle(sigma):
    """[C][S]: for an oscillating roller follower (pivot at distance a, arm L, ψ = ψ0 + s) the relative-velocity
    construction gives tan φ = |L s' − σ(L − a cos ψ)| / (a sin ψ); cos ψ0 = (a² + L² − r_p²)/(2aL)."""
    p = Program.from_dict(
        {
            "unit": "rad",
            "segments": [
                {"kind": "rise", "deg": 120, "h_deg": 20, "law": "cycloidal"},
                {"kind": "dwell", "deg": 60},
                {"kind": "return", "deg": 120, "h_deg": 20, "law": "mod_sine"},
                {"kind": "dwell", "deg": 60},
            ],
        }
    )
    g = D.analyse(D.Mechanism(follower="oscillating", rb=40, rr=10, a=100, L=80, sigma=sigma), p)
    assert g["psi0"] == pytest.approx(np.arccos((100**2 + 80**2 - 50**2) / (2 * 100 * 80)))
    psi = g["psi0"] + g["s"]
    ref = np.arctan(np.abs(80 * g["s1"] - sigma * (80 - 100 * np.cos(psi))) / (100 * np.sin(psi)))
    assert np.max(np.abs(g["phi"] - ref)) < 1e-12
    # pitch curve: every point is r from the cam centre where r² = a² + L² − 2aL cos ψ
    assert np.hypot(*g["pitch"]) == pytest.approx(np.sqrt(100**2 + 80**2 - 2 * 100 * 80 * np.cos(psi)))


def test_flat_faced_followers():
    """[N][S]: translating flat face: ρ = r_b + s + s''; the envelope computed numerically agrees. An oscillating
    flat face through its pivot has pressure angle 0."""
    p = Program.from_dict(RDR)
    g = D.analyse(D.Mechanism(contact="flat", rb=40), p, n=7200)
    err = np.abs(g["rho_numeric"] - g["rho_profile"])
    assert np.percentile(err, 99) < 1e-3 and np.max(err) < 0.05  # finite differences, worst where jerk jumps
    assert np.max(np.abs(np.abs(g["face_contact"]) - np.abs(g["s1"]))) < 1e-9  # contact sits |s'| off the axis
    po = Program.from_dict(
        {
            "unit": "rad",
            "segments": [
                {"kind": "rise", "deg": 180, "h_deg": 10, "law": "cycloidal"},
                {"kind": "return", "deg": 180, "h_deg": 10, "law": "cycloidal"},
            ],
        }
    )
    go = D.analyse(D.Mechanism(follower="oscillating", contact="flat", rb=40, a=120), po)
    assert np.max(go["phi"]) < 1e-6
    # every contact point lies on the face line through the pivot
    psi = go["psi0"] + go["s"]
    assert np.max(np.abs(np.sin(psi) * go["F"][0] - np.cos(psi) * go["F"][1] - 120 * np.sin(psi))) < 1e-6


def test_geometry_refusals():
    p = Program.from_dict(RDR)
    for m, msg in (
        (D.Mechanism(rb=10, rr=5, e=20), "offset is larger"),
        (D.Mechanism(rb=10), "roller radius"),
        (D.Mechanism(follower="oscillating", rb=10, rr=5, a=200, L=50), "cannot touch"),
        (D.Mechanism(contact="flat", groove=True, rb=10), "groove cam drives a roller"),
    ):
        with pytest.raises(D.GeometryError, match=msg):
            D.analyse(m, p)
    with pytest.raises(D.GeometryError, match="program is in angle"):
        D.analyse(D.Mechanism(follower="oscillating", rb=40, rr=10, a=100, L=80), p)


# ---------------------------------------------------------------- forces


def test_hertz_by_hand():
    """Hertz line contact of two steel cylinders, r1 = 10 mm, r2 = 40 mm, b = 10 mm, F = 1000 N, E = 206 GPa,
    ν = 0.3 ([N] stress chapter; any machine-design text):  σ = √(F(1/r1 + 1/r2) / (π b · 2(1 − ν²)/E))."""
    mat = Y.Material(206000, 0.3, 206000, 0.3)
    sig = Y.hertz(np.array([1000.0]), 10.0, np.array([40.0]), 10.0, mat)[0]
    ref = sqrt(1000 * (1 / 10 + 1 / 40) / (pi * 10 * 2 * (1 - 0.09) / 206000))
    assert sig == pytest.approx(ref, rel=1e-12)
    concave = Y.hertz(np.array([1000.0]), 10.0, np.array([-40.0]), 10.0, mat)[0]
    assert concave < sig  # a concave profile conforms: lower stress
    assert Y.hertz(np.array([1.0]), 10.0, np.array([40.0]), None, mat) is None


def test_jump_speed_harmonic():
    """[N][C] follower jump: contact holds while k(s + δ0) + F_w + m s''ω² > 0. For simple harmonic rise and return
    of h over β between dwells the deepest deceleration −hπ²/(2β²) occurs at s = h, so
    ω_jump = √((k(h + δ0) + F_w) / (m · 1e-3 · hπ²/(2β²)))."""
    h, beta, k, d0, fw, m = 12.0, radians(140), 4.0, 8.0, 15.0, 0.6
    p = Program.from_dict(
        {
            "segments": [
                {"kind": "rise", "deg": 140, "h": h, "law": "harmonic"},
                {"kind": "dwell", "deg": 40},
                {"kind": "return", "deg": 140, "h": h, "law": "harmonic"},
                {"kind": "dwell", "deg": 40},
            ]
        }
    )
    g = D.analyse(D.Mechanism(rb=30, rr=8), p, 7200)
    got = Y.jump_speed("translating", g, Y.Loads(mass=m, k=k, preload=d0, load=fw))
    w = sqrt((k * (h + d0) + fw) / (m * 1e-3 * h * pi**2 / (2 * beta**2)))
    assert got == pytest.approx(w * 60 / (2 * pi), rel=1e-6)
    assert Y.jump_speed("translating", g, Y.Loads(mass=None)) is None


def test_torque_balances_over_a_turn():
    """Power balance (frictionless): T = F_ax · s'. Spring, inertia and a constant load are conservative over a full
    turn, so ∮ T dθ = 0."""
    p = Program.from_dict(RDR)
    g = D.analyse(D.Mechanism(rb=40, rr=10, e=4), p, 7200)
    f = Y.forces("translating", g, Y.Loads(rpm=900, mass=1.2, k=6, preload=5, load=30))
    work = np.sum(f["torque"]) * (2 * pi / 7200)
    assert abs(work) < 1e-6 * np.max(np.abs(f["torque"])) * 2 * pi


# ---------------------------------------------------------------- checks and design

PROJECT = {
    "program": RDR,
    "mechanism": {"rb": 40, "rr": 10, "e": 5, "width": 12},
    "loads": {"rpm": 600, "mass": 0.8, "k": 5, "preload": 10, "load": 20},
    "material": {"E1": 206000, "nu1": 0.3, "E2": 206000, "nu2": 0.3},
    "limits": {"phi_rise_deg": 30, "phi_return_deg": 45, "stress": 1200},
}


def test_checks_pass_fail_unknown():
    r = analyse(PROJECT)
    st = {c["id"]: c["status"] for c in r["checks"]}
    assert st == {
        "rigid_impact": "pass",
        "soft_impact": "pass",
        "phi_rise": "pass",
        "phi_return": "pass",
        "undercut": "pass",
        "rho_min": "info",
        "jump": "pass",
        "stress": "pass",
        "torque": "info",
    }
    assert r["status"] == "pass" and len(r["curves"]["deg"]) == 360 and r["curves"]["s"][120] == pytest.approx(20)
    bare = analyse({"program": RDR, "mechanism": {"rb": 40, "rr": 10}})
    st = {c["id"]: c["status"] for c in bare["checks"]}
    assert st["phi_rise"] == st["jump"] == st["stress"] == st["torque"] == "unknown" and bare["status"] == "unknown"
    fast = analyse(PROJECT | {"loads": PROJECT["loads"] | {"rpm": 1500}})
    assert {c["id"]: c["status"] for c in fast["checks"]}["jump"] == "fail" and fast["status"] == "fail"


def test_undercut_inner_and_groove_outer():
    """[N][S]: a roller larger than the smallest convex radius of the pitch curve undercuts the profile; in a groove
    cam the outer flank undercuts where the pitch curve is concave with |ρ| below the roller radius."""
    sharp = {
        "unit": "mm",
        "segments": [
            {"kind": "rise", "deg": 60, "h": 25, "law": "cycloidal"},
            {"kind": "return", "deg": 60, "h": 25, "law": "cycloidal"},
            {"kind": "dwell", "deg": 240},
        ],
    }
    # same pitch curve (prime circle 34 mm), different rollers
    pitch = D.analyse(D.Mechanism(rb=30, rr=4), Program.from_dict(sharp))["rho_pitch"]
    worst = float(np.min(pitch[pitch > 0]))
    small = analyse({"program": sharp, "mechanism": {"rb": 34 - (worst - 1), "rr": worst - 1}})
    big = analyse({"program": sharp, "mechanism": {"rb": 34 - (worst + 1), "rr": worst + 1}})
    assert {c["id"]: c["status"] for c in small["checks"]}["undercut"] == "pass"
    assert {c["id"]: c["status"] for c in big["checks"]}["undercut"] == "fail"
    # groove: same pitch curve again; a roller wider than the tightest concave radius folds the outer flank
    concave = pitch < 0
    assert np.any(concave)
    tight = float(np.min(np.abs(pitch[concave])))
    assert tight < worst  # the concave side is the tighter one here
    rr = (tight + worst) / 2
    out = analyse({"program": sharp, "mechanism": {"rb": 34 - rr, "rr": rr, "groove": True}})
    c = {x["id"]: x for x in out["checks"]}["undercut"]
    assert c["status"] == "fail" and c["note"] == "outer flank undercut"
    plain = analyse({"program": sharp, "mechanism": {"rb": 34 - rr, "rr": rr}})
    assert {x["id"]: x for x in plain["checks"]}["undercut"]["status"] == "pass"


def test_min_base_radius():
    """[AL]: the smallest base circle meeting the pressure-angle limits; just below it the limit is exceeded."""
    pr = PROJECT | {"limits": {"phi_rise_deg": 30, "phi_return_deg": 40}}
    res = min_base_radius(pr)
    assert res["binding"]
    at = analyse(pr | {"mechanism": pr["mechanism"] | {"rb": res["rb"]}})
    below = analyse(pr | {"mechanism": pr["mechanism"] | {"rb": res["rb"] - 0.05}})
    assert {c["id"]: c["status"] for c in at["checks"]}["phi_rise"] == "pass"
    worst = {c["id"]: c for c in below["checks"]}
    assert "fail" in (worst["phi_rise"]["status"], worst["phi_return"]["status"])
    with pytest.raises(ValueError, match="allowed pressure angle"):
        min_base_radius({"program": RDR, "mechanism": {"rb": 40, "rr": 10}})


def test_examples_run():
    """The sample projects shipped with the kernel load and analyse; the feed cam is deliberately too fast for its
    spring (the jump check fails), and no example claims a contact-stress pass without an allowed value."""
    import json
    import pathlib

    res = {}
    for f in sorted(pathlib.Path(__file__).parent.parent.joinpath("examples").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        if d.get("kind") == "system" or f.name.endswith(".cae.json"):
            continue  # a cam system (tests/test_system.py)
        res[f.stem] = analyse(d)
    assert set(res) == {"packaging-plate", "sewing-feed", "sewing-takeup-groove"}
    assert {c["id"]: c["status"] for c in res["sewing-feed"]["checks"]}["jump"] == "fail"
    assert all({c["id"]: c["status"] for c in r["checks"]}["stress"] == "unknown" for r in res.values())
