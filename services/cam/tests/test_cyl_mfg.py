"""Cylindrical cam machining (round 39, step 8c): the 4-axis program copies the roller (deviation only the chord
error), a smaller cutter in two passes stays close, the program reads back, the model made by the cutter has the
groove where the kernel says, and the endpoints answer."""

import json
import math
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app import app
from camkit import cyl_mfg as M
from camkit import cylindrical as C
from camkit.program import Program

EX = Path(__file__).resolve().parents[1] / "examples"


def load(eid):
    p = json.loads((EX / f"{eid}.json").read_text(encoding="utf-8"))
    prog = Program.from_dict(p["program"])
    return p, prog, C.cyl(p["cylindrical"], prog.unit)


@pytest.mark.parametrize("eid", ["barrel-feed", "barrel-fork"])
def test_the_cutter_copies_the_roller_within_the_chord_tolerance(eid):
    p, prog, c = load(eid)
    for tol in (0.002, 0.0002):
        text = M.program(c, prog, {"chord_tol": tol})
        s = M.simulate(c, prog, text)
        assert s["unreached"] == 0
        floor = 1.5e-4  # the program keeps 4 decimals: 0.0001° of A at the outer radius is ~0.14 µm
        assert -s["max_over"] <= tol * 1.05 + floor and s["max_under"] <= tol * 1.05 + floor
    # a tighter tolerance needs more points
    fine, coarse = M.program(c, prog, {"chord_tol": 0.0002}), M.program(c, prog, {"chord_tol": 0.002})
    assert fine.count("G01") > 2 * coarse.count("G01")


def test_axes_follow_the_follower():
    p, prog, c = load("barrel-feed")
    t = M.program(c, prog, {})
    moves = [ln for ln in t.splitlines() if ln.startswith(("G00", "G01"))]
    assert not any(" Y" in ln for ln in moves) and all(" A" in ln for ln in moves)   # translating: A + X only
    assert "TAPERED CUTTER" in t
    p, prog, c = load("barrel-fork")
    t = M.program(c, prog, {})
    passes = M.parse(t)
    assert len(passes) == 1 and np.ptp(passes[0][:, 2]) > 1               # oscillating: Y moves with the arm
    # read back: the points are on the tool path
    th, y, z = M.tool_path(c, prog, 0, c.rr)
    A = passes[0][:, 0]
    assert np.allclose(np.interp(A, np.degrees(th), z), passes[0][:, 1], atol=1e-3)


def test_smaller_cutter_two_passes_and_wrong_cutters():
    p, prog, c = load("barrel-fork")
    t = M.program(c, prog, {"tool_r": c.rr - 2})
    assert len(M.parse(t)) == 2 and "ONE PASS PER FLANK" in t
    s = M.simulate(c, prog, t, c.rr - 2)
    assert s["unreached"] == 0 and -s["max_over"] < 0.003 and s["max_under"] < 0.01
    with pytest.raises(M.CylMfgError, match="not more than the roller"):
        M.settings(c, {"tool_r": c.rr + 1})
    _, _, cone = load("barrel-feed")
    with pytest.raises(M.CylMfgError, match="tapered cutter"):
        M.settings(cone, {"tool_r": 8})


@pytest.mark.parametrize("eid", ["barrel-feed", "barrel-fork"])
def test_model_has_the_groove_where_the_kernel_says(eid):
    p, prog, c = load(eid)
    tc, zs, top = M.height_field(c, M.program(c, prog, {}), d_theta=1.0, dz=0.25)
    rings = C.rings(c, prog)
    lo, hi = np.array(rings["outer"]["lo"]), np.array(rings["outer"]["hi"])
    checked = 0
    for j, a in enumerate(tc):
        k = int(round(a)) % 360
        inside = (zs > lo[k] + 1.0) & (zs < hi[k] - 1.0)
        outside = (zs < lo[k] - 1.0) | (zs > hi[k] + 1.0)
        assert np.all(top[j, inside] < c.x2 - 1e-6)                        # the groove is cut
        assert np.allclose(top[j, outside], c.x2)                          # the rest is the blank
        mid = np.abs(zs - (lo[k] + hi[k]) / 2) < 0.3
        assert np.allclose(top[j, mid], c.core, atol=0.05)                 # bottom at the groove-bottom radius
        checked += 1
    assert checked == len(tc)


def test_endpoints():
    cl = TestClient(app)
    p = json.loads((EX / "barrel-feed.json").read_text(encoding="utf-8"))
    r = cl.post("/api/cyl/manufacture", json={"project": p}).json()
    assert r["program"].startswith("%") and {c["id"] for c in r["checks"]} == {"overcut", "left", "reached"}
    assert all(c["status"] != "fail" for c in r["checks"])
    r = cl.post("/api/cyl/stl", json={"project": p})
    assert r.status_code == 200 and r.content[:12] == b"WenQuest Cam" and len(r.content) > 84
    bad = dict(p, mfg={"four": {"tool_r": 5}})
    r = cl.post("/api/cyl/manufacture", json={"project": bad})
    assert r.status_code == 422 and "锥形" in r.json()["detail"]["zh"]
    assert math.isfinite(r.status_code)


def test_dwells_are_cut_exactly():
    # a point is kept at every joint of the motion program, so a dwell is one exact move (only rounding left)
    p, prog, c = load("barrel-fork")
    s = M.simulate(c, prog, M.program(c, prog, {}))
    for f in s["flanks"]:
        deg = f["deg"]
        dwell = ((deg > 103) & (deg < 177)) | ((deg > 283) & (deg < 357))
        assert np.nanmax(np.abs(f["dev"][dwell])) < 2e-5
