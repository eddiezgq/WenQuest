"""Globoidal cam model, 4-axis program and simulation; the tool-changer arm (round 39, step 4c).

Checks written out:
  - in a dwell a flat-ended cutter of the roller's size, its end at ρ_r from the turret centre, leaves the groove
    bottom at radius C − √(ρ_r² + r_r²) under the cutter's rim and C − ρ_r on its axis
  - the program's B(A) points are on the exact turret path; between them the error at ρ_r stays within the chord
    tolerance, and the simulated flanks are within it too
  - a cutter 0.01 mm smaller than the roller leaves about 0.01 mm all over the flanks
  - the arm's polar moment of inertia against a fine numerical integration of the outline
"""

import json
import math
from pathlib import Path

import numpy as np
import pytest
from shapely.geometry import Point

from camkit import atc_arm as AR
from camkit import globoid_mfg as M
from camkit import globoidal as G
from camkit.program import Program

EX = Path(__file__).resolve().parents[1] / "examples"
ARM = {"R_tip": 150, "R_hub": 48, "bore": 20, "w_root": 60, "w_tip": 44, "R_grip": 46, "r_fork": 32, "thickness": 28,
       "fillet": 4}


@pytest.fixture(scope="module")
def cam():
    c = json.loads((EX / "atc-globoidal.json").read_text(encoding="utf-8"))["cams"][0]
    return G.globoid(c["globoidal"]), Program.from_dict(c["program"])


def test_height_field_groove_bottom(cam):
    g, prog = cam
    tc, zs, top = M.height_field(g, prog, d_theta=0.25, dz=0.25)
    rho_r = g.rho2 + g.clearance
    assert top.min() >= g.C - math.sqrt(rho_r**2 + g.rr**2) - 1e-6
    assert abs(top.min() - (g.C - math.sqrt(rho_r**2 + g.rr**2))) < 0.05
    # the uncut blank: the globoid's own radius at the ends of the cam
    assert abs(top.max() - M.blank_radius(g, zs[-1], g.rho1)) < 1e-9
    V, F = M.mesh(tc, zs, top)
    data = M.stl(V, F)
    assert len(data) == 84 + 50 * len(F)


def test_program_and_simulation(cam):
    g, prog = cam
    tol = 0.002
    text = M.program(g, prog, {"chord_tol": tol})
    passes = M.parse(text)
    assert passes and all(len(p) > 10 for p in passes)
    rho_r = g.rho2 + g.clearance
    for p in passes:
        A, B = p[:, 0], p[:, 1]
        # every program point lies on one roller's exact path
        phi = np.degrees(G.roller_angles(g, prog.position(np.radians(A))))
        d = np.min(np.abs((phi - B[None, :] + 180) % 360 - 180), axis=0)
        assert d.max() < 1e-3
        # between the points the error at the roller end stays within the tolerance
        Ad = np.linspace(A[0], A[-1], 20001)
        lin = np.interp(Ad, A, B)
        ex = np.degrees(G.roller_angles(g, prog.position(np.radians(Ad))))
        err = np.min(np.abs((ex - lin[None, :] + 180) % 360 - 180), axis=0)
        assert np.radians(err).max() * rho_r <= tol * 1.05
    sim = M.simulate(g, prog, text)
    assert sim["unreached"] == 0 and sim["points"] > 1000
    assert max(-sim["max_over"], sim["max_under"]) <= tol + 1e-4
    small = M.simulate(g, prog, text, cutter_r=g.rr - 0.01)
    allv = np.concatenate(small["dev"])
    assert abs(np.median(allv) - 0.01) < 0.002 and allv.min() > 0.01 - tol - 1e-4


def test_arm_mass_properties_and_step():
    mp = AR.mass_properties(ARM)
    s, shape, ring = AR.outline(ARM)
    solid = shape.difference(Point(0, 0).buffer(ARM["bore"], quad_segs=128))
    # fine grid integration of r² over the outline
    h = 0.25
    xs = np.arange(-210, 210, h) + h / 2
    ys = np.arange(-60, 60, h) + h / 2
    X, Y = np.meshgrid(xs, ys)
    from shapely import contains_xy

    inside = contains_xy(solid, X, Y)
    J_num = 7850 * 0.028 * np.sum((X[inside] ** 2 + Y[inside] ** 2) * 1e-6) * (h * 1e-3) ** 2
    assert abs(mp["J"] - J_num) / J_num < 2e-3
    assert abs(mp["mass"] - 7850 * 0.028 * solid.area * 1e-6) < 1e-9
    text, rep = AR.step(ARM)
    # each piece of the outline is a face (the forks exact cylinders), plus the two flat faces and the bore
    assert text.count("ADVANCED_FACE") == rep["pieces"] + 3 and text.count("CYLINDRICAL_SURFACE") == 3
    assert rep["fit_dev"]["outline"] <= 0.01



def test_arm_refusals():
    with pytest.raises(AR.ArmError):
        AR.sizes(ARM | {"bore": 60})
    with pytest.raises(AR.ArmError):
        AR.sizes({k: v for k, v in ARM.items() if k != "thickness"})
