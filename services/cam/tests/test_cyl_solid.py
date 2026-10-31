"""Cylindrical cam as an exact solid and as a mesh (round 39, step 8d). The groove ring is bounded by the flanks as
made (fitted to the condition of meshing), a bottom at the depth the cutter's flat end reaches, and a top outside the
blank. Checked: the fit, the seam, the mesh against the machining height field where it applies (translating
follower), the overhang an off-axis cutter leaves (oscillating follower), and with OpenCASCADE (when installed) a valid
solid that has the exact flank points on its surface and the same volume as the mesh."""

import json
import math
from pathlib import Path

import numpy as np
import pytest

from camkit import cyl_mfg as M
from camkit import cyl_solid as S

EX = Path(__file__).resolve().parents[1] / "examples"


def load(eid, **kw):
    p = json.loads((EX / f"{eid}.json").read_text(encoding="utf-8"))
    p["cylindrical"] |= kw
    return S.build(p)


@pytest.mark.parametrize("eid", ["barrel-feed", "barrel-fork"])
def test_walls_fit_the_flanks_and_close_round(eid):
    c, prog = load(eid)
    sfs, gr = S.faces(c, prog)
    assert gr["fit_err"] < 0.25e-3                                       # within 0.25 µm of the exact flanks
    for sf in sfs:
        assert np.allclose(sf["poles"][0], sf["poles"][-1])             # the seam: first row = last row
    assert gr["seam_deg"] % 10 == 0 and 0 < gr["seam_deg"] < 360        # in the middle of the longest dwell


def test_mesh_matches_the_machining_height_field_for_a_translating_follower():
    c, prog = load("barrel-feed")
    V, F, vol = S.mesh_part(c, prog)
    tc, zs, top = M.height_field(c, M.program(c, prog, {}), d_theta=0.25, dz=0.1)
    w = np.ones(len(zs))
    w[0] = w[-1] = 0.5
    hv = float((top**2 / 2 * w[None, :]).sum() * math.radians(0.25) * 0.1)
    groove = math.pi * c.x2**2 * c.length - hv
    assert abs(vol - hv) / groove < 0.002


def test_an_off_axis_cutter_leaves_overhanging_walls():
    # oscillating follower: the cutter axis is off the cam axis, so the groove is wider at depth than at the rim. A
    # height field (one surface radius per ray) keeps the material under the overhang that the cutter removes: it has
    # clearly more volume than the mesh of the exact groove ring, while for the translating follower the two agree
    c, prog = load("barrel-fork")
    _, _, vol = S.mesh_part(c, prog)
    tc, zs, top = M.height_field(c, M.program(c, prog, {}), d_theta=0.25, dz=0.1)
    w = np.ones(len(zs))
    w[0] = w[-1] = 0.5
    hv = float((top**2 / 2 * w[None, :]).sum() * math.radians(0.25) * 0.1)
    groove = math.pi * c.x2**2 * c.length - vol
    assert (hv - vol) / groove > 0.005


def test_stl_endpoint_uses_the_mesh():
    from fastapi.testclient import TestClient

    from app import app

    p = json.loads((EX / "barrel-fork.json").read_text(encoding="utf-8"))
    r = TestClient(app).post("/api/cyl/stl", json={"project": p})
    assert r.status_code == 200
    n = int.from_bytes(r.content[80:84], "little")
    assert len(r.content) == 84 + 50 * n and n > 50000


@pytest.mark.parametrize("eid", ["barrel-feed", "barrel-fork"])
def test_exact_solid_with_opencascade(eid):
    pytest.importorskip("OCP")
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    from OCP.BRepGProp import BRepGProp
    from OCP.gp import gp_Pnt
    from OCP.GProp import GProp_GProps

    c, prog = load(eid)
    shape, info = S.build_ocp(c, prog)
    assert info["valid"] and info["fit_err_um"] < 0.25
    d = []
    th = np.radians(np.arange(3, 360, 29))
    for sd in (1, -1):
        for q in S.wall_grid(c, prog, sd, th, np.array([c.x1 + 0.5, c.Rp, c.x2 - 0.5])).reshape(-1, 3):
            if abs(q[2]) < c.length / 2 - 0.5:
                v = BRepBuilderAPI_MakeVertex(gp_Pnt(*map(float, q))).Vertex()
                d.append(BRepExtrema_DistShapeShape(v, shape).Value())
    assert max(d) < 1e-4                                                 # exact flank points on the surface (0.1 µm)
    vp = getattr(BRepGProp, "VolumeProperties_s", None) or BRepGProp.VolumeProperties
    g = GProp_GProps()
    vp(shape, g, 1e-7, False, False)
    _, _, vol = S.mesh_part(c, prog)
    groove = math.pi * c.x2**2 * c.length - g.Mass()
    assert abs(vol - g.Mass()) / groove < 0.001                          # mesh = solid (tessellation only)
