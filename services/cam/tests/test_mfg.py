"""Standard problems for manufacturing and measurement, step 3 of round 39 (see docs/实施细则/第39轮, step 3).

Closed forms used here are written out:
  - grinding an eccentric circle (radius R, eccentricity e) with a wheel of radius R_w, wheel centre on the X axis:
        X(C) = e·cos C + √((R + R_w)² − e²·sin²C)
  - chord height of a chord c on an arc of radius ρ: δ = c² / (8ρ)
  - acceleration from a profile error A·cos kθ at ω: peak = A·k²·ω²
"""

import json
import math
import re
from pathlib import Path

import numpy as np
import pytest
from scipy.interpolate import splev

from camkit import measure as Me
from camkit import mfg as M
from camkit import step as S

EX = Path(__file__).resolve().parents[1] / "examples"


def ex(name):
    return json.loads((EX / f"{name}.json").read_text(encoding="utf-8"))


def circle_surface(R=40.0, e=8.0, n=M.DENSE):
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    P = np.stack([e + R * np.cos(t), R * np.sin(t)])
    P, nn, k, _ = M._closed_geometry(P)
    return M.Surface("profile", "廓线", P, nn, +1, k)


def x_exact(C_deg, R, Rw, e):
    C = np.radians(C_deg)
    return e * np.cos(C) + np.sqrt((R + Rw) ** 2 - e**2 * np.sin(C) ** 2)


# ---------------------------------------------------------------- tool paths and programs


def test_eccentric_circle_grinding_closed_form():
    R, e, Rw, tol = 40.0, 8.0, 150.0, 0.001
    sf = circle_surface(R, e)
    X, C = M.xc_path(M.tool_centre(sf, Rw), tol)
    assert C[0] == 0 and C[-1] == 360 and np.all(np.diff(C) > 0)
    assert np.max(np.abs(X - x_exact(C, R, Rw, e))) < 1e-6  # every program point is on the exact path
    # between program points the machine interpolates X linearly in C: stays within the chord tolerance
    Cd = np.linspace(0, 360, 200001)
    lin = np.interp(Cd, C, X)
    assert np.max(np.abs(lin - x_exact(Cd, R, Rw, e))) <= tol * 1.02


def test_chord_height():
    rho, tol = 50.0, 0.001
    t = np.linspace(0, 2 * math.pi, 40000, endpoint=False)
    Q = rho * np.stack([np.cos(t), np.sin(t)])
    idx = M._select_xy(Q, tol)
    P = Q[:, idx]
    c = np.hypot(*(np.roll(P, -1, axis=1) - P))
    sag = c**2 / (8 * rho)
    assert np.all(sag <= tol * 1.0001)
    assert np.mean(c) >= 0.97 * math.sqrt(8 * rho * tol)  # chords as long as the tolerance allows


def test_grinding_program_simulates_back_to_the_design():
    R, e, Rw, tol = 40.0, 8.0, 150.0, 0.001
    sf = circle_surface(R, e)
    for mode in ("radius", "diameter"):
        st = M.settings({"tool_r": Rw, "chord_tol": tol, "grind": {"x_mode": mode}})
        X, C = M.xc_path(M.tool_centre(sf, Rw), tol)
        text = M.grind_program([("profile", X, C, 1)], st, "eccentric circle")
        assert ("(XMODE DIAMETER)" in text) == (mode == "diameter")
        sim = M.simulate(text, [sf], Rw, False)
        dev = sim["flanks"][0]["dev"]
        assert np.all(np.isfinite(dev))
        assert np.max(np.abs(dev)) <= tol + 1e-4


def test_wheel_dressed_smaller_leaves_material():
    """A wheel 0.01 mm smaller than programmed: about 0.01 mm of material left all round (normal direction)."""
    R, e, Rw, tol = 40.0, 8.0, 150.0, 0.0005
    sf = circle_surface(R, e)
    st = M.settings({"tool_r": Rw, "chord_tol": tol})
    X, C = M.xc_path(M.tool_centre(sf, Rw), tol)
    text = M.grind_program([("profile", X, C, 1)], st, "")
    dev = M.simulate(text, [sf], Rw - 0.01, False)["flanks"][0]["dev"]
    assert abs(np.mean(dev) - 0.01) < 3e-4 and np.min(dev) > 0.0095 - tol


@pytest.mark.parametrize(("name", "process", "R"), [
    ("packaging-plate", "grind", 150), ("packaging-plate", "mill", 8),
    ("sewing-feed", "grind", 100), ("sewing-feed", "mill", 6),
    ("sewing-takeup-groove", "grind", 4), ("sewing-takeup-groove", "grind", 3), ("sewing-takeup-groove", "mill", 3),
])
def test_examples_programs_pass_simulation(name, process, R):
    out = M.manufacture(ex(name), {"process": process, "tool_r": R})
    ck = {c["id"]: c for c in out["checks"]}
    assert ck["gouge"]["status"] == "pass"
    assert ck["sim"]["status"] == "pass", ck["sim"]
    assert out["program"].startswith("%\nO39")
    if "groove" in name:
        assert len(out["sim"]["flanks"]) == 2  # both flanks compared with the design


def test_gouging_is_reported_and_seen_in_the_simulation():
    p = ex("packaging-plate")
    p["mechanism"]["rb"] = 30  # concave flank of radius about 87 mm
    out = M.manufacture(p, {"process": "grind", "tool_r": 150})
    ck = {c["id"]: c for c in out["checks"]}
    assert ck["gouge"]["status"] == "fail"
    assert 80 < ck["gouge"]["value"] < 95
    assert ck["xc"]["status"] == "fail" and out["program"] is None  # the wheel centre path folds over
    out = M.manufacture(p, {"process": "mill", "tool_r": 100})  # an over-large cutter: the program is made ...
    ck = {c["id"]: c for c in out["checks"]}
    assert ck["gouge"]["status"] == "fail"
    assert ck["sim"]["status"] == "fail" and out["over"][0] < -0.01  # ... and the simulation shows it cutting in
    ok = M.manufacture(p, {"process": "grind", "tool_r": 60})
    assert {c["id"]: c for c in ok["checks"]}["gouge"]["status"] == "pass"


def test_settings_refusals():
    with pytest.raises(M.MfgError):
        M.settings({"process": "grind"})  # no tool radius
    with pytest.raises(M.MfgError):
        M.manufacture(ex("sewing-takeup-groove"), {"process": "mill", "tool_r": 5})  # wider than the groove


# ---------------------------------------------------------------- exports


def test_dxf_points_on_the_profile():
    p = ex("packaging-plate")
    _, _, sfs, _ = M.design(p)
    text = M.dxf(sfs, 0.001)
    lines = text.splitlines()
    assert lines[:4] == ["0", "SECTION", "2", "ENTITIES"] and lines[-2:] == ["0", "EOF"]
    pairs = list(zip(lines[0::2], lines[1::2], strict=True))
    verts, cur = [], None
    for code, val in pairs:
        if code == "0":
            cur = [] if val == "VERTEX" else None
            if cur is not None:
                verts.append(cur)
        elif cur is not None and code in ("10", "20"):
            cur.append(float(val))
    Q = np.array(verts).T
    assert Q.shape[1] > 50 and text.count("POLYLINE") == 1
    d = S._seg_dist(sfs[0].P, Q, M.cKDTree(sfs[0].P.T).query(Q.T)[1])
    assert d.max() < 1e-5


def test_point_table():
    text = M.point_table(ex("sewing-takeup-groove"), 1.0)
    rows = text.strip().splitlines()
    assert rows[0].startswith("cam_deg,lift_deg,profile_x") and "outer_r" in rows[0]
    assert len(rows) == 361


def test_step_written_curves_match_the_design():
    p = ex("packaging-plate")
    m, _, sfs, _ = M.design(p)
    text, rep = S.solid("cam", sfs[0].P, m.width)
    ids = set(re.findall(r"^#(\d+)=", text, re.M))
    refs = set(re.findall(r"#(\d+)", text))
    assert refs <= ids  # every reference is defined
    assert text.count("ADVANCED_FACE") == 3 and "MANIFOLD_SOLID_BREP" in text
    assert rep["fit_dev"]["profile"] <= S.FIT_TOL
    # read the bottom B-spline back from the text and check it against the design
    pat = r"B_SPLINE_CURVE_WITH_KNOTS\('',3,\(([^)]*)\),\.UNSPECIFIED\.,\.T\.,\.F\.,\(([^)]*)\),\(([^)]*)\)"
    m0 = re.search(pat, text)
    pts = {i: tuple(map(float, c.split(","))) for i, c in re.findall(r"^#(\d+)=CARTESIAN_POINT\('',\(([^)]*)\)\)", text,
                                                                      re.M)}
    ctrl = np.array([pts[r.strip("#")][:2] for r in m0.group(1).split(",")]).T
    knots = np.array(list(map(float, m0.group(3).split(","))))
    u = np.linspace(knots[3], knots[-4], 5000)
    q = np.array(splev(u, (knots, [ctrl[0], ctrl[1]], 3)))
    d = S._seg_dist(sfs[0].P, q, M.cKDTree(sfs[0].P.T).query(q.T)[1])
    assert d.max() <= S.FIT_TOL


def test_step_groove_needs_blank_data():
    p = ex("sewing-takeup-groove")
    m, _, sfs, _ = M.design(p)
    with pytest.raises(S.StepError):
        S.solid("g", sfs[0].P, m.width, sfs[1].P)
    text, rep = S.solid("g", sfs[0].P, m.width, sfs[1].P, blank_r=90, plate=m.width + 8)
    assert text.count("ADVANCED_FACE") == 7 and rep["volume"] > 0


# ---------------------------------------------------------------- measurement and compensation

HL = [(1, 0.004, 30.0), (3, 0.002, -60.0), (17, 0.0008, 10.0)]


def test_harmonics_recovered_with_the_zero_known():
    p = ex("packaging-plate")
    data = Me.synthetic(p, HL, shift_deg=0.0, offset=0.003, noise=0.0)
    r = Me.measure(p, {"format": "lift", "data": data, "align": False})
    A, ph = r["harm"]["A"], np.degrees(r["harm"]["phase"])
    for k, a, phase in HL:
        assert abs(A[k - 1] - a) < 2e-6
        assert abs((ph[k - 1] - phase + 180) % 360 - 180) < 0.1
    assert abs(r["offset"] - 0.003) < 1e-6
    others = np.delete(A, [k - 1 for k, _, _ in HL])
    assert others.max() < 2e-6


def test_alignment_finds_the_shift():
    """Best-fit alignment: the shift and offset come back; the part of the error that looks like s'·Δ is taken into
    the shift, so amplitudes within 1 % and phases within 3° (see measure.py)."""
    p = ex("packaging-plate")
    data = Me.synthetic(p, HL, shift_deg=1.5, offset=0.003, noise=0.0002)
    r = Me.measure(p, {"format": "lift", "data": data})
    assert abs(r["shift_deg"] - 1.5) < 0.005 and abs(r["offset"] - 0.003) < 1e-4
    A, ph = r["harm"]["A"], np.degrees(r["harm"]["phase"])
    for k, a, phase in HL:
        assert abs(A[k - 1] - a) < 0.01 * a + 2e-5
        assert abs((ph[k - 1] - phase + 180) % 360 - 180) < 3


def test_acceleration_error_single_harmonic():
    p = ex("packaging-plate")
    k, A, rpm = 12, 0.002, 600
    data = Me.synthetic(p, [(k, A, 0.0)], shift_deg=0, offset=0, noise=0)
    r = Me.measure(p, {"format": "lift", "data": data, "align": False, "rpm": rpm, "a_allow": 1.0})
    w = rpm * 2 * math.pi / 60
    peak = {c["id"]: c for c in r["checks"]}["acc_err"]["value"]
    assert abs(peak - A * k**2 * w**2 * 1e-3) / (A * k**2 * w**2 * 1e-3) < 0.01
    rpm_max = {c["id"]: c for c in r["checks"]}["rpm_max"]["value"]
    assert abs(rpm_max - math.sqrt(1.0 / (A * k**2 * 1e-3)) * 60 / (2 * math.pi)) / rpm_max < 0.01
    assert abs(r["allow_k"][k - 1] - 1.0 / (k**2 * w**2 * 1e-3)) < 1e-9


def test_missing_data_is_unknown():
    p = ex("packaging-plate")
    p["loads"].pop("rpm")
    r = Me.measure(p, {"format": "lift", "data": Me.synthetic(p)})
    assert {c["id"]: c for c in r["checks"]}["acc_err"]["status"] == "unknown"


def test_compensation_removes_the_selected_orders():
    p = ex("packaging-plate")
    data = Me.synthetic(p, HL, shift_deg=0.0, offset=0.0, noise=0.0001, seed=3)
    c = Me.compensate(p, {"format": "lift", "data": data, "align": False}, {"process": "grind", "tool_r": 150}, 1, 6)
    before, after = c["measure"]["harm"]["A"], c["harm_after"]["A"]
    assert after[0] < 2e-5 and after[2] < 2e-5  # orders 1 and 3 corrected down to the noise
    assert abs(after[16] - before[16]) < 1e-9  # order 17 not selected: left as it was
    # the corrected program makes the corrected cam: the design lift minus the selected error
    out = c["mfg"]
    assert {k["id"]: k for k in out["checks"]}["sim"]["status"] == "pass"


def test_compensated_profile_is_offset_by_the_error():
    """The corrected design lift is s − e_selected; its profile differs from the original by about e·cos φ."""
    p = ex("packaging-plate")
    data = Me.synthetic(p, [(2, 0.005, 0.0)], shift_deg=0.0, offset=0.0, noise=0.0)
    c = Me.compensate(p, {"format": "lift", "data": data, "align": False}, {"process": "mill", "tool_r": 8}, 2, 2)
    s0 = c["measure"]["geo"]["s"]
    s1 = c["mfg"]["geo"]["s"][::4]  # the program is made on the 0.025° grid, the measurement on 0.1°
    assert np.max(np.abs((s0 - s1) - c["e_sel"])) < 1e-6


def test_profile_points_measurement():
    """XY points on the profile pushed out by δn = A·cos 3θ (along the normal): lift error δn / cos φ."""
    p = ex("packaging-plate")
    from camkit import disk as D
    from camkit.analyze import mechanism
    from camkit.program import Program

    m = mechanism(p["mechanism"])
    geo = D.analyse(m, Program.from_dict(p["program"]), 3600)
    P = np.asarray(geo["profile"])
    _, nrm, _, flipped = M._closed_geometry(P)
    if flipped:
        nrm = nrm[:, ::-1]
    th = geo["theta"]
    dn = 0.003 * np.cos(3 * th)
    Q = P + nrm * dn
    data = "x,y\n" + "\n".join(f"{x:.7f},{y:.7f}" for x, y in zip(Q[0][::5], Q[1][::5], strict=True))
    r = Me.measure(p, {"format": "xy", "data": data, "align": False})
    expect = dn / np.cos(geo["phi"])
    expect -= expect.mean()
    assert np.max(np.abs(r["e"] - expect)) < 2e-5
    # the part turned by 2° on the measuring machine: the rotation comes back
    a = math.radians(2.0)
    Qr = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]]) @ Q
    data = "\n".join(f"{x:.7f},{y:.7f}" for x, y in zip(Qr[0][::5], Qr[1][::5], strict=True))
    r = Me.measure(p, {"format": "xy", "data": data})
    assert abs(r["shift_deg"] - 2.0) < 0.01
