"""Thin-section ball bearings (round 64, plan section 二十一, part 2): standard problems. The bearings are made up."""

import copy
import json
import math
from pathlib import Path

import numpy as np
import pytest

from bearingkit import ball as BB
from bearingkit import thin as TH

EX = Path(__file__).resolve().parents[1] / "examples"
SPEC = dict(Dw=6.35, Z=40, dm=120.0, fi=0.52, fo=0.53)


def make(section, **kw):
    return TH.Thin(**SPEC, section=section, **kw)


def resid(b, u, P):
    r = b.forces(u) - np.asarray(P, float)
    sc = b.scales(P)["Q"]
    return max(np.abs(r[:3]).max() / sc, np.abs(r[3:]).max() / (sc * b.dm / 2))


@pytest.mark.parametrize("Fr, Fa", [(3000.0, 0.0), (3000.0, 1500.0), (500.0, 2500.0)])
def test_deep_groove_against_the_ball_kernel(Fr, Fa):
    """C with the balls free gives what the two-force-member kernel (ball.py) gives, the contact stiffness held at
    the same constant (the only difference in the models)."""
    t = make("C", Gr=0.02)
    b = BB.bearing(dict(D=6.35, Z=40, dm=120, fi=0.52, fo=0.53, Pd=0.02))
    b.Kn = lambda a, K=t.Kn: K
    r = BB.distribute(b, Fr, Fa)
    c = t.contacts(t.solve([Fr, 0, Fa, 0, 0]))
    assert np.abs(c["Q"][:, 0] - r["Q"]).max() <= 1e-7 * r["Qmax"]
    on = r["Q"] > 0
    assert np.abs(np.degrees(np.abs(c["angle"][on, 0])) - r["alpha_deg"][on]).max() <= 1e-6


@pytest.mark.parametrize("Fr, Fa", [(3000.0, 1500.0), (500.0, 2500.0)])
def test_angular_against_the_ball_kernel(Fr, Fa):
    """A single row; ball.py takes the radial force at the plane of the inner groove's curvature centre, so the same
    force here comes with the moment Fr·z of that plane."""
    t = make("A", alpha_deg=25)
    b = BB.bearing(dict(D=6.35, Z=40, dm=120, fi=0.52, fo=0.53, alpha0_deg=25))
    b.Kn = lambda a, K=t.Kn: K
    z = (0.52 * 6.35 - 6.35 / 2) * math.sin(math.radians(25))
    r = BB.distribute(b, Fr, Fa)
    c = t.contacts(t.solve([Fr, 0, Fa, Fr * z, 0]))
    assert np.abs(c["Q"][:, 0] - r["Q"]).max() <= 1e-7 * r["Qmax"]


@pytest.mark.parametrize("section, kw", [("X", dict(alpha_deg=30, Gr=0.012)), ("C", dict(Gr=0.02))])
def test_free_play_by_the_closed_form(section, kw):
    """No load until the ring has moved the radial play G_r/2 (each way) or the axial play G_a/2 of the closed form
    G_a = 2 (√(A² − (A cos α₀ − G_r/2)²) − A sin α₀); the balls free to find their way."""
    b = make(section, **kw)
    fp = b.free_play()
    assert fp["radial"] == pytest.approx(kw["Gr"])
    for k, half in ((0, fp["radial"] / 2), (2, fp["axial"] / 2)):
        u = np.zeros(5)
        u[k] = half * (1 + 1e-3)
        on = b.forces(u)[k]
        u[k] = half * (1 - 1e-3)
        # below the play only the holding spring of the balls (10⁻¹⁰ of the contact scale) is felt
        assert on > 0 and np.abs(b.forces(u)).max() <= 1e-4 * on
    if section == "C":  # the deep groove case is the familiar G_a = 2 √(A² − (A − P_d/2)²)
        A = b.A
        assert fp["axial"] == pytest.approx(2 * math.sqrt(A * A - (A - 0.01) ** 2), rel=1e-12)


def test_four_point_axial_load_one_diagonal():
    """Pure axial force with clearance: every ball on the one diagonal (inner arc +, outer arc +), all equal; the
    other diagonal off; the contact angle above the free one."""
    b = make("X", alpha_deg=30, Gr=0.01)
    c = b.contacts(b.solve([0, 0, 4000.0, 0, 0]))
    Q = c["Q"]
    assert np.all(Q[:, 0] > 0) and np.all(Q[:, 2] > 0) and not Q[:, 1].any() and not Q[:, 3].any()
    assert np.ptp(Q[:, 0]) <= 1e-9 * Q[:, 0].max()
    assert (Q[:, 0] * np.sin(c["angle"][:, 0])).sum() == pytest.approx(4000.0, rel=1e-10)
    assert np.all(np.degrees(c["angle"][:, 0]) > 30)


@pytest.mark.parametrize("P", [[3000.0, 0, 0, 0, 0], [1500.0, -400.0, 900.0, 1.2e5, -4e4], [0, 0, 0, 2e5, 0]])
@pytest.mark.parametrize(
    "section, kw",
    [
        ("X", dict(alpha_deg=30, Gr=0.008)),
        ("X", dict(alpha_deg=30, Gr=-0.006)),
        ("C", dict(Gr=0.015)),
        ("A", dict(alpha_deg=30, arrangement="DB", spacing=12.0, endplay=-0.008)),
        ("A", dict(alpha_deg=30, arrangement="DF", spacing=12.0, endplay=0.004)),
    ],
)
def test_balance(section, kw, P):
    b = make(section, **kw)
    u = b.solve(P)
    assert resid(b, u, P) <= 1e-8
    st = b.state(u)
    # each ball in balance by itself (the holding spring of an idle ball is far below this)
    d = st["B"][:, None, :] - (b.C0 + np.einsum("nmij,j->nmi", b.J, u))
    nh = d / np.linalg.norm(d, axis=2)[:, :, None]
    fb = (st["Q"][:, :, None] * nh).sum(axis=1)
    assert np.abs(fb).max() <= 1e-8 * max(st["Q"].max(), 1.0)


def test_pure_moment_is_antisymmetric():
    """Four-point under a moment about y: the ball at ψ carries on diagonal + what the ball at ψ + π carries on −."""
    b = make("X", alpha_deg=30, Gr=-0.004)
    c = b.contacts(b.solve([0, 0, 0, 1.5e5, 0]))
    Q, Z = c["Q"], b.Z
    for j in range(Z):
        k = (j + Z // 2) % Z
        assert Q[k, 1] == pytest.approx(Q[j, 0], rel=1e-7, abs=1e-9 * Q.max())
        assert Q[k, 3] == pytest.approx(Q[j, 2], rel=1e-7, abs=1e-9 * Q.max())


def test_pair_axial_stiffness_by_hand():
    """A preloaded pair at no load: each ball is a two-force member between its arc centres, stiffness k = 1.5 K_n δ^½
    along the line and Q/L across it; the axial stiffness is Σ (k sin²θ + Q/L cos²θ) (axial decouples by symmetry).
    The preload by the closed form equals the one from the solved balls."""
    b = make("A", alpha_deg=30, arrangement="DB", spacing=12.0, endplay=-0.008)
    u = b.solve([0, 0, 0, 0, 0])
    st = b.state(u)
    Q, th = st["Q"][:, 0], np.abs(st["angle"][:, 0])
    dl = st["delta"][:, 0] + st["delta"][:, 1]  # the closing of the line (inner and outer contacts in series)
    Ltot = b.A + dl
    k = 1.5 * b.Kn * dl**0.5
    want = (k * np.sin(th) ** 2 + Q / Ltot * np.cos(th) ** 2).sum()
    assert b.stiffness(u)["axial"] * 1000 == pytest.approx(want, rel=1e-6)
    assert b.preload_force() == pytest.approx((Q[: b.Z] * np.sin(th[: b.Z])).sum(), rel=1e-9)
    # back to back holds tilt better than face to face at the same preload
    f = make("A", alpha_deg=30, arrangement="DF", spacing=12.0, endplay=-0.008)
    assert b.stiffness(u)["tilt"] > 1.5 * f.stiffness(f.solve([0, 0, 0, 0, 0]))["tilt"]


def test_preload_given_as_a_force():
    for section, kw in (("X", dict(alpha_deg=30)), ("A", dict(alpha_deg=30, arrangement="DB", spacing=12.0))):
        b = TH.make({**SPEC, "section": section, **kw}, {"preload": 800.0})
        assert b.preload_force() == pytest.approx(800.0, rel=1e-8)
        assert (b.Gr if section == "X" else b.e) < 0
    with pytest.raises(ValueError, match="clearance, not a preload"):
        TH.make({**SPEC, "section": "C"}, {"preload": 100.0})
    with pytest.raises(ValueError, match="pair it"):
        TH.make({**SPEC, "section": "A", "alpha_deg": 30}, {"preload": 100.0})


def test_more_preload_more_tilt_stiffness():
    spec = {**SPEC, "section": "X", "alpha_deg": 30}
    c = TH.setting_curve(spec, TH.load(Fr=800.0, Fa=300.0, M=6e4), 10.0, -15.0, 6)
    k, pre = c["k_tilt"], c["preload"]
    assert all(x is not None for x in k) and pre[0] == 0.0 and pre[-1] > 0
    # once preloaded (both diagonals carrying), more preload gives more tilting stiffness
    kp = [x for x, f in zip(k, pre, strict=True) if f > 0]
    assert len(kp) >= 3 and all(b > a for a, b in zip(kp, kp[1:], strict=False)) and kp[-1] > 1.5 * kp[0]


def test_geometry_errors():
    for bad, msg in (
        (dict(section="Y"), "four-point contact X"),
        (dict(section="X", alpha_deg=None), "contact angle"),
        (dict(section="X", alpha_deg=70), "contact angle"),
        (dict(section="X", alpha_deg=30, arrangement="DB", spacing=10), "only the angular"),
        (dict(section="A", alpha_deg=30, arrangement="DB"), "distance between the two rows"),
    ):
        with pytest.raises(ValueError, match=msg):
            TH.Thin(**SPEC, **bad)
    with pytest.raises(ValueError, match="do not fit"):
        TH.Thin(6.35, 70, 120.0, 0.52, 0.53, "C")


def load(name):
    return json.loads((EX / f"{name}.json").read_text(encoding="utf-8"))


def test_the_examples_and_their_checks():
    from bearingkit.analyze import analyse

    for name, sec in (("demo-thin-x", "X"), ("demo-thin-a", "A"), ("demo-thin-c", "C")):
        r = analyse(load(name))
        ids = {c["id"]: c for c in r["checks"]}
        assert r["type"] == "thin" and r["thin"]["section"] == sec and r["status"] == "unknown"  # ratings: standard
        assert ids["C"]["status"] == "unknown" and ids["C0"]["status"] == "unknown"
        assert {"p_inner", "p_outer", "trunc_inner", "trunc_outer", "k_tilt", "thin_ratio"} <= set(ids)
        assert r["profile"]["inner"] and r["profile"]["outer"]
    x = {c["id"]: c for c in analyse(load("demo-thin-x"))["checks"]}
    assert x["x_both"]["status"] == "pass" and x["mid_inner"]["status"] == "pass" and x["preload"]["value"] > 0
    a = {c["id"]: c for c in analyse(load("demo-thin-a"))["checks"]}
    assert a["preload"]["value"] == pytest.approx(1500.0, rel=1e-8) and a["x_both"]["status"] == "pass"
    c = {c["id"]: c for c in analyse(load("demo-thin-c"))["checks"]}
    b = make("C", Gr=0.01)
    assert c["x_ga"]["value"] == pytest.approx(TH.Thin(5, 40, 88, 0.52, 0.53, "C", Gr=0.01).free_play()["axial"] * 1000)
    assert b.free_play()["radial"] == 0.01


def test_the_checks_say_what_goes_wrong():
    from bearingkit.analyze import ProjectError, analyse

    # too little preload under a large moment: diagonals unload
    q = load("demo-thin-x")
    q["pair"]["endplay"] = -2
    assert {c["id"]: c for c in analyse(q)["checks"]}["x_both"]["status"] == "fail"
    # a small contact angle and a big radial force with clearance: the contact runs to the middle of the arch
    q = load("demo-thin-x")
    q["inner"]["alpha0_deg"] = 12
    q["pair"]["endplay"] = 40
    q["loads"].update(Fr=6000, Fa=0, M=0)
    ids = {c["id"]: c for c in analyse(q)["checks"]}
    assert ids["mid_inner"]["status"] == "fail" or ids["mid_outer"]["status"] == "fail"
    # low shoulders: the ellipse runs over them
    q = load("demo-thin-x")
    q["inner"].update(h_i=0.3, h_o=0.3)
    q["loads"].update(Fa=3000)
    ids = {c["id"]: c for c in analyse(q)["checks"]}
    assert ids["trunc_inner"]["status"] == "fail"
    # no shoulder heights: unknown, never a pass
    q = load("demo-thin-c")
    q["inner"]["h_i"] = None
    ids = {c["id"]: c for c in analyse(q)["checks"]}
    assert ids["trunc_inner"]["status"] == "unknown"
    # a single angular row pushed the wrong way has nothing to hold it
    q = load("demo-thin-a")
    q["pair"]["arrangement"] = "single"
    q["loads"].update(Fa=-500)
    assert {c["id"]: c for c in analyse(q)["checks"]}["a_side"]["status"] == "fail"
    q = load("demo-thin-x")
    q["pair"]["endplay"] = None
    with pytest.raises(ProjectError, match="radial clearance"):
        analyse(q)


def test_parts_drawings_and_the_service():
    from fastapi.testclient import TestClient

    import app as service
    from bearingkit import drawing as DR
    from bearingkit import parts as PT
    from bearingkit import step3d as S
    from bearingkit.analyze import geometry_of

    g = geometry_of(load("demo-thin-x"))
    pr = PT.parts(g)
    assert g["type"] == "four_point" and pr["element_kind"] == "ball"
    # the gothic arch: two arcs meeting at the middle, at the diameter the geometry gives
    arcs = [s for s in pr["inner"] if s["arc"]]
    assert len(arcs) == 2 and arcs[0]["b"] == arcs[1]["a"] == (g["di"] / 2, 0.0)
    for s in arcs:  # every end of an arc is on its circle
        for pt in (s["a"], s["b"]):
            assert math.dist(pt, s["arc"]["c"]) == pytest.approx(s["arc"]["rho"], rel=1e-12)
    # the volume against the outline sampled finely (Pappus)
    for k in ("inner", "outer"):
        pts = np.array(PT.outline(pr[k], 400))
        z, r = pts[:, 0], pts[:, 1]
        cross = r * np.roll(z, -1) - np.roll(r, -1) * z
        A = 0.5 * cross.sum()
        cr = ((r + np.roll(r, -1)) * cross).sum() / (6 * A)
        assert S.volume(pr[k]) == pytest.approx(abs(2 * math.pi * cr * A), rel=1e-5)
    text, vol = PT.step(g)
    assert "ISO-10303-21" in text and vol["element"] == pytest.approx(g["Z"] * math.pi * g["Dw"] ** 3 / 6)
    assert "桃形沟中线直径" in DR.part_sheet(g, "inner", "示例")
    c = TestClient(service.app)
    for name in ("demo-thin-x", "demo-thin-a", "demo-thin-c"):
        assert c.post("/api/analyse", json=load(name)).status_code == 200
        assert c.post("/api/parts/bearing.step", json=load(name)).status_code == 200
    q = load("demo-thin-x")
    q["inner"]["alpha0_deg"] = None
    e = c.post("/api/analyse", json=q)
    assert e.status_code == 422 and "接触角" in e.json()["detail"]["zh"]
    q = copy.deepcopy(load("demo-thin-a"))
    q["pair"]["spacing"] = None
    e = c.post("/api/analyse", json=q)
    assert e.status_code == 422 and "两列中心距" in e.json()["detail"]["zh"]
