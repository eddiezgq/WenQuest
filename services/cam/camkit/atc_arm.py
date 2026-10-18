"""The tool-changer arm (round 39, step 4c): a flat double gripper made from a few sizes, as an outline, mass
properties and a STEP solid for the finite-element analysis in the digital factory.

Outline: hub circle and two gripper rings at ±R_tip joined by tapering arms; each gripper has a fork (a circle of the
tool flange's radius opening sideways, the two openings facing opposite ways so the arm grips both tools when it
turns); edges rounded with a fillet radius. A bore for the output shaft. All sizes come from the user (the example's
are fictional). Steel density 7850 kg/m³ unless given.

Plain code: no AI, no network. Lengths mm.
"""

from __future__ import annotations

import math

import numpy as np
from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

from camkit import step as S
from camkit.analyze import _num

KEYS = ("R_tip", "R_hub", "bore", "w_root", "w_tip", "R_grip", "r_fork", "thickness", "fillet",
        "density")
NAMES = {"R_tip": "gripper centre radius", "R_hub": "hub radius", "bore": "bore radius",
         "w_root": "arm width at the hub", "w_tip": "arm width at the gripper", "R_grip": "gripper outer radius",
         "r_fork": "fork radius", "thickness": "thickness"}


class ArmError(ValueError):
    pass


def sizes(d: dict) -> dict:
    d = d or {}
    bad = set(d) - set(KEYS)
    if bad:
        raise ArmError(f"unknown arm field: {sorted(bad)[0]}")
    out = {k: _num(d.get(k)) for k in KEYS}
    for k, name in NAMES.items():
        if not (out[k] and out[k] > 0):
            raise ArmError(f"give the arm's {name}")
    out["fillet"] = out["fillet"] or 0.0
    out["density"] = out["density"] or 7850.0
    if out["bore"] >= out["R_hub"] or out["r_fork"] >= out["R_grip"] or out["R_hub"] + out["R_grip"] >= out["R_tip"]:
        raise ArmError("the arm's sizes do not fit together: bore < hub, fork < gripper, hub + gripper < tip radius")
    return out


def outline(d: dict, res: int = 64):
    s = sizes(d)
    R, q = s["R_tip"], res
    hub = Point(0, 0).buffer(s["R_hub"], quad_segs=q)
    parts = [hub]
    for sgn in (1, -1):
        c = (sgn * R, 0.0)
        grip = Point(c).buffer(s["R_grip"], quad_segs=q)
        arm = Polygon([(0, s["w_root"] / 2), (sgn * R, s["w_tip"] / 2), (sgn * R, -s["w_tip"] / 2),
                       (0, -s["w_root"] / 2)])
        parts += [grip, arm]
    shape = unary_union(parts)
    for sgn in (1, -1):
        c = (sgn * R, 0.0)
        fork = unary_union([Point(c).buffer(s["r_fork"], quad_segs=q),
                            box(c[0] - s["r_fork"], 0, c[0] + s["r_fork"], 2 * s["R_grip"])])
        if sgn < 0:
            fork = affinity.scale(fork, 1, -1, origin=c)  # the other gripper opens the other way
        shape = shape.difference(fork)
    f = s["fillet"]
    if f > 0:
        shape = shape.buffer(f, quad_segs=q).buffer(-2 * f, quad_segs=q).buffer(f, quad_segs=q)
    if shape.geom_type != "Polygon":
        raise ArmError("the arm falls apart into pieces: check its sizes")
    ring = np.asarray(shape.exterior.coords)[:-1].T
    if 0.5 * np.sum(ring[0] * np.roll(ring[1], -1) - np.roll(ring[0], -1) * ring[1]) < 0:
        ring = ring[:, ::-1]
    return s, shape, _densify(ring, 0.25)


def _densify(P, step):
    Q = np.concatenate([P, P[:, :1]], axis=1)
    seg = np.hypot(*np.diff(Q, axis=1))
    out = []
    for i in range(P.shape[1]):
        n = max(1, int(math.ceil(seg[i] / step)))
        t = np.arange(n) / n
        out.append(Q[:, i: i + 1] + (Q[:, i + 1: i + 2] - Q[:, i: i + 1]) * t)
    return np.concatenate(out, axis=1)


def mass_properties(d: dict) -> dict:
    """Mass (kg) and moment of inertia about the hub axis (kg·m²), bore taken out."""
    s, shape, _ = outline(d)
    shape = shape.difference(Point(0, 0).buffer(s["bore"], quad_segs=128))
    t, rho = s["thickness"] * 1e-3, s["density"]
    area = shape.area * 1e-6
    # polar second moment of area of a polygon with holes, by the shoelace sums (exact for the polygon)
    def polar(ring):
        x, y = np.asarray(ring.coords).T * 1e-3
        x1, y1 = np.roll(x, -1), np.roll(y, -1)
        cr = x * y1 - x1 * y
        ix = np.sum(cr * (y * y + y * y1 + y1 * y1)) / 12
        iy = np.sum(cr * (x * x + x * x1 + x1 * x1)) / 12
        return ix + iy
    J = abs(polar(shape.exterior)) - sum(abs(polar(r)) for r in shape.interiors)
    return {"mass": rho * t * area, "J": rho * t * J, "area_mm2": shape.area}


def step(d: dict, name: str = "atc-arm") -> tuple[str, dict]:
    s, _, ring = outline(d)
    return S.plate(name, ring, s["thickness"], (s["bore"],))
