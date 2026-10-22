"""Globoidal cam as an exact solid (round 39, step 5a; plan section 十.1).

The cam is defined by the machining method: a cutter the size of a roller, its axis along a roller, its flat end at
the groove bottom (distance ρ_r = ρ2 + clearance from the turret centre), follows every roller's path relative to the
blank and takes away what it passes through. The solid is built as the blank minus the volumes the cutter sweeps,
and every swept volume is bounded exactly:

- its two side walls are the envelopes of the cutter's cylinder, i.e. the rib flanks: points from the condition of
  meshing (camkit.globoidal.contact), interpolated by B-spline surfaces over (cam angle, distance along the roller);
- its bottom is ruled through the cutter end's diameter across the feed (where the flat end meets the two walls);
- its top and its two ends lie outside the blank (the top at a distance ρ_t < ρ1 from the turret centre, the ends
  where the roller has turned away from the cam), so their shape does not reach the part.

The cutter's walls are tangent to nothing on the blank, so the subtraction is a plain transversal boolean; no
cutter-by-cutter subtraction (tangent, slow, step-limited) is done. The machining simulation of step 4 (the program
read back) checks the result independently.

One groove per roller passage: a roller enters where it turns towards the cam and leaves where it turns away; over
one cam turn the turret advances `advance / (2π/n)` roller pitches, so that many grooves (starts) are cut, each found
once by taking the passages that begin within one cam turn.

This module is plain numpy except build_ocp(), which needs OpenCASCADE through OCP (tests and the local check); the
FreeCAD workbench builds the same faces with FreeCAD's Part module from the same grids.
"""

from __future__ import annotations

import math

import numpy as np

from camkit import globoidal as G
from camkit.program import Program


class GloboidSolidError(ValueError):
    pass


def top_rho(g: G.Globoid) -> float:
    """Distance from the turret centre of the swept volume's top: the cutter's wall points there, ρ_t·u ± r_r·n, stay
    outside the blank (|·| < ρ1) with half a millimetre to spare."""
    r = math.sqrt(max(g.rho1**2 - g.rr**2, 0.0)) - 0.5
    if r <= 0.2 * g.rho1:
        raise GloboidSolidError("the rollers are too thick for their inner end radius to build the solid")
    return r


def bottom_rho(g: G.Globoid) -> float:
    return g.rho2 + g.clearance


def _section_outside(g: G.Globoid, prog: Program, roller: int, theta: np.ndarray, margin: float = 0.3) -> np.ndarray:
    """True at cam angles where the whole cross-section of the cutter's swept volume (both walls from ρ_t to ρ_r and
    the top and bottom across) lies outside the blank by at least margin: beyond an end face, or above the globoid."""
    rho = np.linspace(top_rho(g), bottom_rho(g), 17)
    a, da = angles(g, prog, roller, theta)
    pts = []
    for side in (1, -1):
        A = a[None, :] * np.ones((len(rho), 1))
        D = da[None, :] * np.ones((len(rho), 1))
        R = rho[:, None] * np.ones((1, len(theta)))
        P, _, _, _ = G.contact(g, A, D, R, side)
        pts.append(P)
    P = np.concatenate(pts, axis=1)  # (3, 2·len(rho), m)
    for f in (0.25, 0.5, 0.75):  # across the top and the bottom
        P = np.concatenate([P, (1 - f) * pts[0][:, [0, -1]] + f * pts[1][:, [0, -1]]], axis=1)
    x, y, z = P
    rc = np.hypot(x - g.C, y)
    zc = np.clip(np.abs(z), 0, g.rho1)
    surf = g.C - np.sqrt(np.maximum(g.rho1**2 - zc * zc, 0.0))
    out = (np.abs(z) > g.L / 2 + margin) | (rc > surf + margin)
    return out.all(axis=0)


def angles(g: G.Globoid, prog: Program, roller: int, theta) -> tuple[np.ndarray, np.ndarray]:
    """Angle of one roller and its rate dφ_i/dθ at cam angles theta (any, continued over turns)."""
    th = np.asarray(theta, dtype=float)
    _, dphi, _, _ = prog.eval(np.mod(th, 2 * math.pi))
    phi = prog.position(th)
    a = g.hand * phi + g.phase + 2 * math.pi * roller / g.n
    return a, g.hand * dphi


def passages(g: G.Globoid, prog: Program, step_deg: float = 0.25) -> list[dict]:
    """Roller passages through the cam that begin within one cam turn: (roller, θ0, θ1), θ in rad, where θ0 and θ1 are
    the last and first cam angles with the whole cross-section of the cutter's swept volume outside the blank."""
    if prog.unit != "rad":
        raise GloboidSolidError("a globoidal cam needs an angular (turret) program")
    turns = 6
    th = np.radians(np.arange(-360.0 * turns, 360.0 * turns + 1e-9, step_deg))
    out = []
    for i in range(g.n):
        near = ~_section_outside(g, prog, i, th)
        k = 0
        while k < len(th):
            if not near[k]:
                k += 1
                continue
            j = k
            while j + 1 < len(th) and near[j + 1]:
                j += 1
            if k == 0 or j == len(th) - 1:  # cut off by the window: begins outside the turn looked at
                k = j + 1
                continue
            t0, t1 = th[k - 1], th[j + 1]
            if t1 - t0 > 2 * math.pi * (turns - 1):
                raise GloboidSolidError("a roller stays in the cam for many turns: the program does not index")
            if 0 <= t0 < 2 * math.pi - 1e-12:
                out.append({"roller": i, "theta0": float(t0), "theta1": float(t1)})
            k = j + 1
    if not out:
        raise GloboidSolidError("no roller passes through the cam")
    return out


def wall_grid(g: G.Globoid, prog: Program, roller: int, side: int, theta: np.ndarray, rho: np.ndarray) -> np.ndarray:
    """Points of the cutter's side wall (= rib flank) in the cam frame, shape (len(theta), len(rho), 3)."""
    a, da = angles(g, prog, roller, theta)
    A = a[:, None] * np.ones((1, len(rho)))
    D = da[:, None] * np.ones((1, len(rho)))
    R = np.ones((len(theta), 1)) * np.asarray(rho)[None, :]
    P, _, _, _ = G.contact(g, A, D, R, side)
    Q = G.cam_frame(g, P, np.asarray(theta)[:, None])
    return np.moveaxis(Q, 0, -1)


def wall_normal_check(g: G.Globoid, prog: Program, roller: int, side: int, theta, rho) -> dict:
    """Relative velocity of the cutter's axis point and the wall normal (cam frame) at (theta, rho) pairs, for the
    meshing check of a built surface: n·v = 0 on the envelope."""
    theta, rho = np.asarray(theta, float), np.asarray(rho, float)
    a, da = angles(g, prog, roller, theta)
    P, n, _, _ = G.contact(g, a, da, rho, side)
    c, s = np.cos(a), np.sin(a)
    v = np.stack([-rho * da * s, g.C - rho * c, rho * da * c])
    return {"P": G.cam_frame(g, P, theta), "n": G.cam_frame_vec(n, theta), "v": G.cam_frame_vec(v, theta)}


def _interp(theta: np.ndarray, rho: np.ndarray, P: np.ndarray) -> dict:
    """Cubic tensor B-spline through the grid P (len θ, len ρ, 3), parameters θ (rad) and ρ (mm) themselves, not-a-knot
    ends. Returns knots (full vectors) and poles (nu, nv, 3)."""
    from scipy.interpolate import make_interp_spline

    s1 = make_interp_spline(theta, P, k=3, axis=0)
    s2 = make_interp_spline(rho, s1.c, k=3, axis=1)
    return {"tu": s1.t, "tv": s2.t, "poles": np.moveaxis(s2.c, 0, 1), "deg": 3}


def surface_eval(sf: dict, theta, rho) -> np.ndarray:
    """Points of a fitted wall at the grid theta × rho, (len θ, len ρ, 3)."""
    from scipy.interpolate import BSpline

    Bu = BSpline.design_matrix(np.clip(theta, sf["tu"][0], sf["tu"][-1]), sf["tu"], 3).toarray()
    Bv = BSpline.design_matrix(np.clip(rho, sf["tv"][0], sf["tv"][-1]), sf["tv"], 3).toarray()
    return np.einsum("ai,ijk,bj->abk", Bu, sf["poles"], Bv)


def fit_walls(g: G.Globoid, prog: Program, p: dict, tol: float = 0.25e-3, k: int = 5, step_deg: float = 1.0) -> dict:
    """Both walls of one passage as B-spline surfaces over the same (θ, ρ) sites. The sites start every step_deg and
    are halved where a wall misses the exact envelope by more than tol (mm) between them (the laws' jerk jumps)."""
    rho = np.linspace(top_rho(g), bottom_rho(g), k)
    n = max(8, int(math.ceil(math.degrees(p["theta1"] - p["theta0"]) / step_deg)))
    th = np.linspace(p["theta0"], p["theta1"], n + 1)
    for _ in range(12):
        fits = {sd: _interp(th, rho, wall_grid(g, prog, p["roller"], sd, th, rho)) for sd in (1, -1)}
        rm = np.linspace(rho[0], rho[-1], 3 * (k - 1) + 1)
        bad = np.zeros(len(th) - 1, dtype=bool)
        for f in (0.25, 0.5, 0.75):
            q = th[:-1] + f * np.diff(th)
            for sd in (1, -1):
                e = np.linalg.norm(surface_eval(fits[sd], q, rm) - wall_grid(g, prog, p["roller"], sd, q, rm),
                                   axis=2).max(axis=1)
                bad |= e > tol
        if not bad.any():
            break
        mid = (th[:-1] + th[1:]) / 2
        th = np.sort(np.concatenate([th, mid[bad]]))
    else:
        raise GloboidSolidError("the rib flanks could not be fitted within the tolerance")
    # certify on a finer check: quarter points in θ, thirds in ρ
    q = np.concatenate([th[:-1] + f * np.diff(th) for f in (0.25, 0.5, 0.75)])
    rq = np.linspace(rho[0], rho[-1], 3 * (k - 1) + 1)
    err = 0.0
    for sd in (1, -1):
        err = max(err, float(np.linalg.norm(surface_eval(fits[sd], q, rq) - wall_grid(g, prog, p["roller"], sd, q, rq),
                                            axis=2).max()))
    return dict(p, theta=th, rho=rho, plus=fits[1], minus=fits[-1], fit_err=err)


def grids(g: G.Globoid, prog: Program, tol: float = 0.25e-3) -> list[dict]:
    """Everything the builders need: per passage, the two walls as B-spline surfaces (same sites) and the fit error."""
    return [fit_walls(g, prog, p, tol) for p in passages(g, prog)]


def blank_profile(g: G.Globoid) -> dict:
    """The blank in the cam frame (axis z): a solid of revolution between z = ±L/2 whose outer generator is the arc
    of radius ρ1 about the turret centre, r(z) = C − √(ρ1² − z²)."""
    return {"centre_r": g.C, "radius": g.rho1, "half_length": g.L / 2}


# ----------------------------------------------------------------------------------- OpenCASCADE (OCP) builder


def knots_mults(t: np.ndarray) -> tuple[list[float], list[int]]:
    """A full knot vector as distinct knots and their multiplicities (what CAD kernels take)."""
    ks, ms = [], []
    for x in t:
        if ks and abs(x - ks[-1]) < 1e-12:
            ms[-1] += 1
        else:
            ks.append(float(x))
            ms.append(1)
    return ks, ms


def build_ocp(g: G.Globoid, prog: Program, bore: float = 0.0, tol: float = 0.25e-3):
    """The exact solid with OpenCASCADE (OCP), cam frame (axis z). Returns (shape, info). bore: shaft hole diameter,
    0 for none."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepBuilderAPI import (BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeSolid,
                                    BRepBuilderAPI_MakeWire, BRepBuilderAPI_Sewing)
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.BRepFill import BRepFill
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeRevol
    from OCP.GC import GC_MakeArcOfCircle
    from OCP.Geom import Geom_BSplineSurface
    from OCP.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt
    from OCP.ShapeFix import ShapeFix_Solid
    from OCP.TopAbs import TopAbs_SHELL
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    try:
        from OCP.TColgp import TColgp_Array2OfPnt as A2P
        from OCP.TColStd import TColStd_Array1OfInteger as A1I
        from OCP.TColStd import TColStd_Array1OfReal as A1R
    except ImportError:  # OCP 7.9+: the collections live in OCP.OCP.collections
        from OCP.OCP.collections import Array1_double as A1R
        from OCP.OCP.collections import Array1_int as A1I
        from OCP.OCP.collections import Array2_gp_Pnt as A2P

    def static(cls, name):  # OCP ≤ 7.8 names static methods Name_s, 7.9+ Name
        return getattr(cls, name + "_s", None) or getattr(cls, name)

    def arr1(cls, vals):
        a = cls(1, len(vals))
        for i, v in enumerate(vals):
            a.SetValue(i + 1, v)
        return a

    def bspline(sf):
        P = sf["poles"]
        nu, nv, _ = P.shape
        poles = A2P(1, nu, 1, nv)
        for i in range(nu):
            for j in range(nv):
                poles.SetValue(i + 1, j + 1, gp_Pnt(*map(float, P[i, j])))
        ku, mu = knots_mults(sf["tu"])
        kv, mv = knots_mults(sf["tv"])
        return Geom_BSplineSurface(poles, arr1(A1R, ku), arr1(A1R, kv), arr1(A1I, mu), arr1(A1I, mv), 3, 3)

    info = {"grooves": []}
    h = g.L / 2
    r0 = g.C - math.sqrt(g.rho1**2 - h * h)
    arc = GC_MakeArcOfCircle(gp_Pnt(r0, 0, -h), gp_Pnt(g.C - g.rho1, 0, 0), gp_Pnt(r0, 0, h)).Value()
    w = BRepBuilderAPI_MakeWire()
    w.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, -h), gp_Pnt(r0, 0, -h)).Edge())
    w.Add(BRepBuilderAPI_MakeEdge(arc).Edge())
    w.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(r0, 0, h), gp_Pnt(0, 0, h)).Edge())
    w.Add(BRepBuilderAPI_MakeEdge(gp_Pnt(0, 0, h), gp_Pnt(0, 0, -h)).Edge())
    prof = BRepBuilderAPI_MakeFace(w.Wire()).Face()
    shape = BRepPrimAPI_MakeRevol(prof, gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 2 * math.pi).Shape()
    if bore > 0:
        cyl = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, -h - 1), gp_Dir(0, 0, 1)), bore / 2, g.L + 2).Shape()
        shape = BRepAlgoAPI_Cut(shape, cyl).Shape()

    for gr in grids(g, prog, tol):
        sp, sm = bspline(gr["plus"]), bspline(gr["minus"])
        faces = [BRepBuilderAPI_MakeFace(sp, 1e-7).Face(), BRepBuilderAPI_MakeFace(sm, 1e-7).Face()]
        u0, u1, v0, v1 = sp.Bounds()
        edges = {}
        for name, s in (("p", sp), ("m", sm)):
            edges[name + "top"] = BRepBuilderAPI_MakeEdge(s.VIso(v0)).Edge()
            edges[name + "bot"] = BRepBuilderAPI_MakeEdge(s.VIso(v1)).Edge()
            edges[name + "in"] = BRepBuilderAPI_MakeEdge(s.UIso(u0)).Edge()
            edges[name + "out"] = BRepBuilderAPI_MakeEdge(s.UIso(u1)).Edge()
        for e in ("top", "bot", "in", "out"):
            faces.append(static(BRepFill, "Face")(edges["p" + e], edges["m" + e]))
        sew = BRepBuilderAPI_Sewing(1e-5)
        for f in faces:
            sew.Add(f)
        sew.Perform()
        ex = TopExp_Explorer(sew.SewedShape(), TopAbs_SHELL)
        if not ex.More():
            raise GloboidSolidError("the swept volume of a roller did not close")
        solid = BRepBuilderAPI_MakeSolid(static(TopoDS, "Shell")(ex.Current())).Solid()
        fix = ShapeFix_Solid(solid)
        fix.Perform()
        cut = BRepAlgoAPI_Cut(shape, fix.Solid())
        if not cut.IsDone():
            raise GloboidSolidError(f"cutting the groove of roller {gr['roller'] + 1} failed")
        shape = cut.Shape()
        info["grooves"].append({"roller": gr["roller"], "deg0": math.degrees(gr["theta0"]),
                                "deg1": math.degrees(gr["theta1"]), "sites": len(gr["theta"]),
                                "fit_err_um": gr["fit_err"] * 1000, "plus": gr["plus"], "minus": gr["minus"]})
    info["valid"] = bool(BRepCheck_Analyzer(shape).IsValid())
    return shape, info


# ----------------------------------------------------------------------------------- checks of a built solid


def in_part(g: G.Globoid, P: np.ndarray, margin: float = 0.2) -> np.ndarray:
    """Cam-frame points (…, 3) inside the blank by at least margin (so on the finished part if on a wall)."""
    z = P[..., 2]
    rc = np.hypot(P[..., 0], P[..., 1])
    surf = g.C - np.sqrt(np.maximum(g.rho1**2 - np.minimum(np.abs(z), g.rho1) ** 2, 0.0))
    return (np.abs(z) < g.L / 2 - margin) & (rc < surf - margin)


def wall_samples(g: G.Globoid, gr: dict, side: int, n_theta: int = 400, n_rho: int = 7, bottom: float = 0.0) -> tuple:
    """(θ, ρ) pairs on one fitted wall whose points lie inside the part, and the points (N, 3); bottom: keep this far
    (mm) above the groove bottom edge."""
    th = np.linspace(gr["theta"][0], gr["theta"][-1], n_theta)
    rho = np.linspace(gr["rho"][0], gr["rho"][-1] - bottom, n_rho)
    S = surface_eval(gr["plus"] if side == 1 else gr["minus"], th, rho)
    m = in_part(g, S)
    T, R = np.meshgrid(th, rho, indexing="ij")
    return T[m], R[m], S[m]



def meshing_check(g: G.Globoid, prog: Program, gr: dict, side: int, theta, rho) -> dict:
    """On a fitted wall at parameter pairs (θ, ρ): distance to the exact envelope point (mm) and the angle (deg)
    between the fitted surface's normal and the plane ⟂ to the relative velocity (the condition of meshing: n·v = 0)."""
    from scipy.interpolate import BSpline

    sf = gr["plus"] if side == 1 else gr["minus"]
    theta, rho = np.asarray(theta, float), np.asarray(rho, float)
    tu, tv, Pl = sf["tu"], sf["tv"], sf["poles"]

    def d(t, x, kder):
        return BSpline(t, np.eye(len(t) - 4), 3)(np.clip(x, t[0], t[-1]), nu=kder)

    Bu, Bu1 = d(tu, theta, 0), d(tu, theta, 1)
    Bv, Bv1 = d(tv, rho, 0), d(tv, rho, 1)
    S = np.einsum("ai,ijk,aj->ak", Bu, Pl, Bv)
    Su = np.einsum("ai,ijk,aj->ak", Bu1, Pl, Bv)
    Sv = np.einsum("ai,ijk,aj->ak", Bu, Pl, Bv1)
    n = np.cross(Su, Sv)
    n /= np.linalg.norm(n, axis=1)[:, None]
    ex = wall_normal_check(g, prog, gr["roller"], side, theta, rho)
    v = ex["v"].T / np.linalg.norm(ex["v"].T, axis=1)[:, None]
    ang = np.degrees(np.arcsin(np.clip(np.abs((n * v).sum(1)), 0, 1)))
    dist = np.linalg.norm(S - ex["P"].T, axis=1)
    return {"dist": dist, "angle_deg": ang}


def machined_check(g: G.Globoid, pts: np.ndarray, text: str, cutter_r: float | None = None) -> np.ndarray:
    """For cam-frame points on the solid's flanks (N, 3): how far each lies outside the nearest cutter position of
    the 4-axis program read back (mm, + material the program would leave, − the program cuts into the solid). The
    cutter is a cylinder of the roller's radius on the roller axis, its end at the groove bottom."""
    from camkit import globoid_mfg as GM

    r_c = g.rr if cutter_r is None else cutter_r
    pos = []
    for p in GM.parse(text):
        for (a0, b0), (a1, b1) in zip(p[:-1], p[1:], strict=True):
            m = max(1, int(math.ceil(abs(a1 - a0) / 0.02)))
            t = np.linspace(0, 1, m, endpoint=False)
            pos.append(np.stack([np.radians(a0 + (a1 - a0) * t), np.radians(b0 + (b1 - b0) * t)]))
    pos = np.concatenate(pos, axis=1)
    rho_r = bottom_rho(g)
    out = np.full(len(pts), np.inf)
    for q, P in enumerate(pts):
        X = np.cos(pos[0]) * P[0] - np.sin(pos[0]) * P[1] + g.C
        Y = np.sin(pos[0]) * P[0] + np.cos(pos[0]) * P[1]
        Z = np.full_like(X, P[2])
        ux, uz = np.cos(pos[1]), np.sin(pos[1])
        along = X * ux + Z * uz
        rad = np.sqrt(np.maximum(X * X + Y * Y + Z * Z - along * along, 0.0))
        ok = (along <= rho_r + 1e-9) & (along >= top_rho(g) - 5)
        if ok.any():
            out[q] = float(np.min(rad[ok] - r_c))
    return out


def bottom_check(g: G.Globoid, prog: Program, gr: dict, n_theta: int = 25, n_s: int = 11) -> float:
    """How much more material the model's groove bottom keeps than the flat end really leaves (mm, ≥ 0): the deepest
    any later or earlier position of the cutter reaches past points of the model's bottom (ruled through the end's
    diameter between the two wall contact points). Only points inside the part count."""
    rho_r = bottom_rho(g)
    T = np.linspace(gr["theta"][0], gr["theta"][-1], 20001)
    A, _ = angles(g, prog, gr["roller"], T)
    ux, uz = np.cos(A), np.sin(A)
    worst = 0.0
    for th in np.linspace(gr["theta"][0], gr["theta"][-1], n_theta + 2)[1:-1]:
        Pp = wall_grid(g, prog, gr["roller"], 1, np.array([th]), np.array([rho_r]))[0, 0]
        Pm = wall_grid(g, prog, gr["roller"], -1, np.array([th]), np.array([rho_r]))[0, 0]
        for f in np.linspace(0, 1, n_s):
            q = (1 - f) * Pp + f * Pm
            if not in_part(g, q[None, :])[0]:
                continue
            X = G.fixed_frame(g, np.repeat(q[:, None], len(T), axis=1), T)
            along = X[0] * ux + X[2] * uz
            rad = np.sqrt(np.maximum((X * X).sum(0) - along**2, 0.0))
            dr, de = rad - g.rr, along - rho_r
            inside = (dr < -1e-9) & (de < -1e-9)
            if inside.any():
                worst = max(worst, float(-np.maximum(dr, de)[inside].min()))
    return worst
