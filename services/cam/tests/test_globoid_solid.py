"""Globoidal cam as an exact solid (round 39, step 5a; plan section 十).

Checks written out:
  - every roller passage through the cam is found once: over one cam turn the turret moves `advance` and all the
    rollers that pass in that time do so; a passage begins and ends with the cutter's whole cross-section outside
    the blank
  - the B-spline rib flanks miss the exact envelope (the condition of meshing, camkit.globoidal.contact) by at most
    0.25 µm anywhere (quarter points between the fit sites), and their normal is perpendicular to the relative
    velocity within 0.01° — the condition of meshing holds on the surfaces themselves
  - machining check: flank points of the part lie on the cutter's wall within the program's chord tolerance, for the
    4-axis program read back (independent of how the solid was built)
  - the groove bottom (non-working, 1 mm below the roller ends) keeps at most a fraction of the clearance more
    material than the flat end really leaves
  - with OpenCASCADE (OCP) installed: the solid is valid, its outer radius along rays from the cam axis matches the
    machining height field of step 4c on the flanks
"""

import json
import math
from pathlib import Path

import numpy as np
import pytest

from camkit import globoid_mfg as M
from camkit import globoid_solid as GS
from camkit import globoidal as G
from camkit.program import Program

EX = Path(__file__).resolve().parents[1] / "examples"


@pytest.fixture(scope="module")
def cam():
    c = json.loads((EX / "atc-globoidal.json").read_text(encoding="utf-8"))["cams"][0]
    g, prog = G.globoid(c["globoidal"]), Program.from_dict(c["program"])
    return g, prog, GS.grids(g, prog)


def test_passages(cam):
    g, prog, grs = cam
    ps = GS.passages(g, prog)
    assert all(0 <= p["theta0"] < 2 * math.pi and p["theta1"] > p["theta0"] for p in ps)
    # every cam angle at which any roller reaches into the blank is inside a passage: of that roller, or of the roller
    # that stands in the same place k turns later (the turret has advanced k·advance meanwhile)
    th = np.radians(np.arange(0, 360, 0.5))
    for i in range(g.n):
        inside = ~GS._section_outside(g, prog, i, th)
        ai, _ = GS.angles(g, prog, i, th)
        cover = np.zeros_like(inside)
        for p in ps:
            for k in range(-3, 4):
                aj, _ = GS.angles(g, prog, p["roller"], th + 2 * math.pi * k)
                same = np.abs(np.angle(np.exp(1j * (aj - ai)))) < 1e-9
                t = th + 2 * math.pi * k
                cover |= same & (t > p["theta0"]) & (t < p["theta1"])
        assert cover[inside].all(), f"roller {i}: angles in the blank outside any passage"


def test_flanks_fit_and_meshing(cam):
    g, prog, grs = cam
    assert max(gr["fit_err"] for gr in grs) <= 0.25e-3
    n = 0
    for gr in grs:
        for side in (1, -1):
            T, R, _ = GS.wall_samples(g, gr, side, 300, 7)
            if not len(T):
                continue
            mc = GS.meshing_check(g, prog, gr, side, T, R)
            assert mc["dist"].max() <= 0.25e-3
            assert mc["angle_deg"].max() < 0.01
            n += len(T)
    assert n > 5000


def test_flanks_against_the_program(cam):
    g, prog, grs = cam
    tol = 0.002
    text = M.program(g, prog, {"chord_tol": tol})
    vals = []
    for gr in grs:
        for side in (1, -1):
            _, _, P = GS.wall_samples(g, gr, side, 200, 5, bottom=0.05)
            if len(P):
                sel = np.linspace(0, len(P) - 1, min(len(P), 60)).astype(int)
                vals.append(GS.machined_check(g, P[sel], text))
    v = np.concatenate(vals)
    assert len(v) > 300
    assert np.abs(v).max() <= tol + 1e-4


def test_groove_bottom_keeps_less_than_the_clearance(cam):
    g, prog, grs = cam
    extra = max(GS.bottom_check(g, prog, gr) for gr in grs)
    assert 0 <= extra < 0.8 * g.clearance


def test_refusals():
    g = G.globoid({"C": 170, "n": 8, "Rp": 40, "rr": 9, "b": 15, "L": 56, "clearance": 1, "phase_deg": 22.5})
    with pytest.raises(GS.GloboidSolidError):
        GS.passages(g, Program.from_dict({"unit": "mm", "segments": [{"kind": "rise", "deg": 180, "h": 5},
                                                                     {"kind": "return", "deg": 180, "h": 5}]}))


def test_exact_solid_with_occ(cam):
    pytest.importorskip("OCP")
    from OCP.gp import gp_Dir, gp_Lin, gp_Pnt
    from OCP.IntCurvesFace import IntCurvesFace_ShapeIntersector

    g, prog, _ = cam
    shape, info = GS.build_ocp(g, prog)
    assert info["valid"]
    tc, zs, top = M.height_field(g, prog, d_theta=0.25, dz=0.5, steps=2880)
    X = IntCurvesFace_ShapeIntersector()
    X.Load(shape, 1e-6)
    diffs = []
    for i in range(0, len(tc), 24):
        th = math.radians(tc[i])
        for j in range(4, len(zs) - 4, 6):
            X.Perform(gp_Lin(gp_Pnt(0, 0, float(zs[j])), gp_Dir(math.cos(th), math.sin(th), 0)), 0, 1e4)
            ws = [X.WParameter(k + 1) for k in range(X.NbPnt())]
            if ws:
                diffs.append(max(ws) - top[i, j])
    d = np.array(diffs)
    # on the blank and the flanks the two agree; where the ray meets the groove bottom the model keeps up to the
    # bottom_check amount more (never less)
    assert np.median(np.abs(d)) < 1e-3
    assert np.percentile(d, 1) > -0.01  # rays grazing a flank between the height field's samples aside
