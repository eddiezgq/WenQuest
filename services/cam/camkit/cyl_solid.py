"""Cylindrical cam as an exact solid (round 39, step 8d; plan section 十三).

As for the globoidal cam (camkit.globoid_solid), the cam is defined by the machining method: a cutter the size of the
roller (tapered for a tapered roller), its axis along the roller's, its flat end at the groove bottom, runs round the
blank and takes away what it passes through. The groove is one closed ring round the cam, bounded exactly by:

- its two side walls, the flanks as made (camkit.cylindrical.flank: the cutter's envelope by the condition of meshing,
  half the side clearance away from the roller), interpolated by B-spline surfaces over (cam angle, distance x along
  the roller axis from the cam axis), from the groove bottom x = core to above the blank;
- its bottom, ruled across the cutter end's diameter between the two walls' bottom curves;
- its top, ruled between the walls' top curves, outside the blank.

The ring has no ends: the walls run once round the cam from θ0 to θ0 + 2π and their first and last site curves are the
same points, so the seam edges are sewn together. θ0 is in the middle of the longest dwell, where the walls are
simplest. The blank (a cylinder of the outer radius and the cam length, with an optional bore) minus the ring is a plain
transversal boolean. The machining simulation (camkit.cyl_mfg) checks the cut independently.

Plain numpy except build_ocp() (OpenCASCADE through OCP, for tests and the local check) and build_part() (FreeCAD's
Part module, passed in).
"""

from __future__ import annotations

import math

import numpy as np

from camkit import cylindrical as C
from camkit.globoid_solid import _interp, knots_mults, surface_eval
from camkit.program import Program


class CylSolidError(ValueError):
    pass


def x_top(c: C.Cyl) -> float:
    """Where the walls end above the blank: high enough that the ruled top stays outside the outer radius."""
    w = 2 * max(c.rr, c.k * c.x2) + c.gap + 2
    return c.x2 + max(2.0, w * w / (4 * c.x2))


def seam(prog: Program) -> float:
    """θ0 (rad): the middle of the longest dwell, or 0."""
    best, a, out = 0.0, 0.0, 0.0
    for s in prog.segments or []:
        if s.kind == "dwell" and s.beta > best:
            best, out = s.beta, a + s.beta / 2
        a += s.beta
    return out


def wall_grid(c: C.Cyl, prog: Program, side: int, theta: np.ndarray, xs: np.ndarray) -> np.ndarray:
    """Points (len θ, len x, 3) of one wall in the cam frame."""
    ps = C.pose(c, prog, theta[:, None])
    P, _ = C.flank(c, ps, xs[None, :], side)
    return np.moveaxis(C.cam_frame(c, P, theta[:, None]), 0, -1)


def fit_walls(c: C.Cyl, prog: Program, tol: float = 0.25e-3, k: int = 6, step_deg: float = 2.0) -> dict:
    """Both walls as B-spline surfaces over the same (θ, x) sites, θ once round from the seam; sites halved where a
    wall misses the exact flank by more than tol (mm) between them."""
    xs = np.linspace(c.core, x_top(c), k)
    t0 = seam(prog)
    n = int(math.ceil(360 / step_deg))
    th = t0 + np.linspace(0, 2 * math.pi, n + 1)
    for _ in range(12):
        fits = {sd: _interp(th, xs, wall_grid(c, prog, sd, th, xs)) for sd in (1, -1)}
        xm = np.linspace(xs[0], xs[-1], 3 * (k - 1) + 1)
        bad = np.zeros(len(th) - 1, dtype=bool)
        for f in (0.25, 0.5, 0.75):
            q = th[:-1] + f * np.diff(th)
            for sd in (1, -1):
                e = np.linalg.norm(surface_eval(fits[sd], q, xm) - wall_grid(c, prog, sd, q, xm), axis=2).max(axis=1)
                bad |= e > tol
        if not bad.any():
            break
        th = np.sort(np.concatenate([th, ((th[:-1] + th[1:]) / 2)[bad]]))
    else:
        raise CylSolidError("the groove flanks could not be fitted within the tolerance")
    q = np.concatenate([th[:-1] + f * np.diff(th) for f in (0.25, 0.5, 0.75)])
    xq = np.linspace(xs[0], xs[-1], 3 * (k - 1) + 1)
    err = max(float(np.linalg.norm(surface_eval(fits[sd], q, xq) - wall_grid(c, prog, sd, q, xq), axis=2).max())
              for sd in (1, -1))
    return {"theta": th, "x": xs, "plus": fits[1], "minus": fits[-1], "fit_err": err, "seam_deg": math.degrees(t0)}


FRACS = (-0.97, -0.85, -0.6, -0.3, 0.0, 0.3, 0.6, 0.85, 0.97)


def bottom_rows(c: C.Cyl, prog: Program, theta: np.ndarray) -> np.ndarray:
    """Rows across the groove bottom (cam frame, (len θ, len FRACS, 3)), ordered from the −z wall to the +z wall: along
    the chord between the two walls' feet at the same site, each point at the depth the cutter's flat end really
    reaches there. The end is the disk x = core of the fixed frame round the cutter axis; at a point of the cam
    (azimuth α, height z) a cutter position θ′ reaches down to the radius core / cos(α + σθ′) when the end covers it,
    (core·tan(α + σθ′) − y′)² + (z − z′)² ≤ r_end²; the depth is the least over the program's positions (the same
    tool path as camkit.cyl_mfg: along the roller axis, or one pass per flank with a side clearance)."""
    from camkit import cyl_mfg as CM

    xs = np.array([c.core])
    A, B = wall_grid(c, prog, 1, theta, xs)[:, 0], wall_grid(c, prog, -1, theta, xs)[:, 0]
    lo, hi = (B, A) if A[:, 2].mean() > B[:, 2].mean() else (A, B)
    sides = (0,) if c.gap == 0 else (1, -1)
    paths = [CM.tool_path(c, prog, sd, c.rr, dense=14400) for sd in sides]
    th_p = np.concatenate([p_[0][:-1] for p_ in paths])
    y_p = np.concatenate([p_[1][:-1] for p_ in paths])
    z_p = np.concatenate([p_[2][:-1] for p_ in paths])
    r_end = c.k * c.core if c.roller == "cone" else c.rr
    rows = np.zeros((len(theta), len(FRACS), 3))
    for i, f in enumerate(FRACS):
        q = lo + (f + 1) / 2 * (hi - lo)
        al, zq = np.arctan2(q[:, 1], q[:, 0]), q[:, 2]
        for j in range(len(theta)):
            beta = np.angle(np.exp(1j * (al[j] + c.sigma * th_p)))
            near = np.abs(beta) < 0.35
            tb = np.tan(beta[near])
            cover = (c.core * tb - y_p[near]) ** 2 + (zq[j] - z_p[near]) ** 2 <= r_end * r_end
            if cover.any():
                d = float(np.min(c.core / np.cos(beta[near][cover])))
            else:  # not reached by the end (cannot happen inside the groove; keep the chord point)
                d = float(np.hypot(q[j, 0], q[j, 1]))
            rows[j, i] = (d * math.cos(al[j]), d * math.sin(al[j]), zq[j])
    return rows


def ruled_patches(gr: dict, rows: np.ndarray | None = None) -> list[dict]:
    """Bottom (x = core) and top (above the blank) of the ring between the walls' boundary curves, built from the walls'
    own poles so the edges coincide exactly. The top is ruled; the bottom, given rows across it (bottom_rows at the
    sites), is a cubic B-spline across through them."""
    from scipy.interpolate import BSpline, make_interp_spline

    a, b = gr["plus"], gr["minus"]
    out = []
    for v in (a["tv"][0], a["tv"][-1]):
        w = BSpline.design_matrix(np.array([v]), a["tv"], 3).toarray()[0]
        ca, cb = np.einsum("ijk,j->ik", a["poles"], w), np.einsum("ijk,j->ik", b["poles"], w)
        if v == a["tv"][0] and rows is not None:
            cr = make_interp_spline(gr["theta"], rows, k=3, axis=0).c  # the rows on the walls' sites and knots
            cr[-1] = cr[0]
            lo, hi = (cb, ca) if ca[:, 2].mean() > cb[:, 2].mean() else (ca, cb)  # −z wall first, as the rows
            stack = np.concatenate([lo[:, None], cr, hi[:, None]], axis=1)  # (nu, R + 2, 3)
            s = np.concatenate([[0.0], (np.array(FRACS) + 1) / 2, [1.0]])
            sp = make_interp_spline(s, stack, k=3, axis=1)
            out.append({"tu": a["tu"], "tv": sp.t, "poles": np.moveaxis(sp.c, 0, 1), "deg": (3, 3)})
        else:
            out.append({"tu": a["tu"], "tv": np.array([0.0, 0.0, 1.0, 1.0]), "poles": np.stack([ca, cb], axis=1),
                        "deg": (3, 1)})
    return out


def faces(c: C.Cyl, prog: Program, tol: float = 0.25e-3) -> tuple[list[dict], dict]:
    gr = fit_walls(c, prog, tol)
    # the seam: the walls' first and last pole rows must be the same points (periodic data, not-a-knot ends)
    for sf in (gr["plus"], gr["minus"]):
        d = float(np.abs(sf["poles"][0] - sf["poles"][-1]).max())
        if d > 1e-9:
            sf["poles"][-1] = sf["poles"][0]
    return [gr["plus"], gr["minus"], *ruled_patches(gr, bottom_rows(c, prog, gr["theta"]))], gr


# ----------------------------------------------------------------------------------- OpenCASCADE (OCP) builder


def build_ocp(c: C.Cyl, prog: Program, bore: float = 0.0, tol: float = 0.25e-3):
    """The exact solid with OpenCASCADE (OCP), cam frame (axis z, the cam between z = ±length/2). Returns (shape,
    info)."""
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeSolid, BRepBuilderAPI_Sewing
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.Geom import Geom_BSplineSurface
    from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
    from OCP.ShapeFix import ShapeFix_Solid
    from OCP.TopAbs import TopAbs_SHELL
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    try:
        from OCP.TColgp import TColgp_Array2OfPnt as A2P
        from OCP.TColStd import TColStd_Array1OfInteger as A1I
        from OCP.TColStd import TColStd_Array1OfReal as A1R
    except ImportError:  # OCP 7.9+
        from OCP.OCP.collections import Array1_double as A1R
        from OCP.OCP.collections import Array1_int as A1I
        from OCP.OCP.collections import Array2_gp_Pnt as A2P

    def static(cls, name):
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
        du, dv = sf["deg"] if isinstance(sf.get("deg"), tuple) else (3, 3)
        return Geom_BSplineSurface(poles, arr1(A1R, ku), arr1(A1R, kv), arr1(A1I, mu), arr1(A1I, mv), du, dv)

    h = c.length / 2
    shape = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, -h), gp_Dir(0, 0, 1)), c.x2, c.length).Shape()
    if bore > 0:
        hole = BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(0, 0, -h - 1), gp_Dir(0, 0, 1)), bore / 2, c.length + 2).Shape()
        shape = BRepAlgoAPI_Cut(shape, hole).Shape()
    sfs, gr = faces(c, prog, tol)
    sew = BRepBuilderAPI_Sewing(1e-5)
    for sf in sfs:
        sew.Add(BRepBuilderAPI_MakeFace(bspline(sf), 1e-7).Face())
    sew.Perform()
    ex = TopExp_Explorer(sew.SewedShape(), TopAbs_SHELL)
    if not ex.More():
        raise CylSolidError("the groove ring did not close")
    ring = BRepBuilderAPI_MakeSolid(static(TopoDS, "Shell")(ex.Current())).Solid()
    fix = ShapeFix_Solid(ring)
    fix.Perform()
    cut = BRepAlgoAPI_Cut(shape, fix.Solid())
    if not cut.IsDone():
        raise CylSolidError("cutting the groove failed")
    shape = cut.Shape()
    info = {"sites": len(gr["theta"]), "fit_err_um": gr["fit_err"] * 1000, "seam_deg": gr["seam_deg"],
            "valid": bool(BRepCheck_Analyzer(shape).IsValid()), "walls": (gr["plus"], gr["minus"])}
    return shape, info


def build_part(c: C.Cyl, prog: Program, Part, Vector, bore: float = 0.0, tol: float = 0.25e-3):
    """The same solid with FreeCAD's Part module (passed in, so camkit does not import FreeCAD). Cam frame, axis z."""
    h = c.length / 2
    shape = Part.makeCylinder(c.x2, c.length, Vector(0, 0, -h), Vector(0, 0, 1))
    if bore > 0:
        shape = shape.cut(Part.makeCylinder(bore / 2, c.length + 2, Vector(0, 0, -h - 1), Vector(0, 0, 1)))

    def bspline(sf):
        ku, mu = knots_mults(sf["tu"])
        kv, mv = knots_mults(sf["tv"])
        P = sf["poles"]
        du, dv = sf["deg"] if isinstance(sf.get("deg"), tuple) else (3, 3)
        poles = [[Vector(*map(float, P[i, j])) for j in range(P.shape[1])] for i in range(P.shape[0])]
        s = Part.BSplineSurface()
        s.buildFromPolesMultsKnots(poles, mu, mv, ku, kv, False, False, du, dv)
        return s

    sfs, gr = faces(c, prog, tol)
    sh = Part.Shell([bspline(sf).toShape() for sf in sfs])
    sh.sewShape()
    ring = Part.Solid(sh)
    if ring.Volume < 0:
        ring.reverse()
    shape = shape.cut(ring)
    return shape, {"sites": len(gr["theta"]), "fit_err_um": gr["fit_err"] * 1000, "valid": bool(shape.isValid())}


def build(project: dict, bore: float = 0.0):
    prog = Program.from_dict(project.get("program") or {})
    return C.cyl(project.get("cylindrical"), prog.unit), prog


# ----------------------------------------------------------------------------------- mesh (STL) from the same faces


def _eval(sf: dict, u: np.ndarray, v: np.ndarray) -> np.ndarray:
    """Points (len u, len v, 3) of a B-spline face dict at parameters u × v."""
    from scipy.interpolate import BSpline

    du, dv = sf["deg"] if isinstance(sf.get("deg"), tuple) else (3, 3)
    Bu = BSpline.design_matrix(np.clip(u, sf["tu"][0], sf["tu"][-1]), sf["tu"], du).toarray()
    Bv = BSpline.design_matrix(np.clip(v, sf["tv"][0], sf["tv"][-1]), sf["tv"], dv).toarray()
    return np.einsum("ai,ijk,bj->abk", Bu, sf["poles"], Bv)


def ring_mesh(c: C.Cyl, prog: Program, n_u: int = 1440, n_v: int = 12, tol: float = 0.25e-3):
    """The groove ring (what the cutter takes away) as a closed triangle mesh (V, F), from the same four faces as the
    solid, sampled at the same u on every face so the edges match. Outward orientation."""
    sfs, gr = faces(c, prog, tol)
    plus, minus, bottom, top = sfs
    u = np.linspace(gr["theta"][0], gr["theta"][-1], n_u + 1)[:-1]  # the seam closes round
    vw = np.linspace(plus["tv"][0], plus["tv"][-1], n_v)
    Wp, Wm = _eval(plus, u, vw), _eval(minus, u, vw)  # (n_u, n_v, 3), v from the bottom (core) to the top
    Bt = _eval(bottom, u, np.linspace(0, 1, n_v))  # across, from the −z wall to the +z wall
    Tp = _eval(top, u, np.linspace(0, 1, 4))  # from the +1 wall's top to the −1 wall's top
    lo_is_plus = Wp[:, 0, 2].mean() < Wm[:, 0, 2].mean()
    lo_w, hi_w = (Wp, Wm) if lo_is_plus else (Wm, Wp)
    # one closed loop of cross-section points per u: up the low wall, across the top, down the high wall, back
    # across the bottom (the shared corner points come from the walls)
    top_seq = Tp if lo_is_plus else Tp[:, ::-1]
    loop = np.concatenate([lo_w, top_seq[:, 1:-1], hi_w[:, ::-1], Bt[:, ::-1][:, 1:-1]], axis=1)  # (n_u, m, 3)
    nu, m, _ = loop.shape
    V = loop.reshape(-1, 3)
    idx = np.arange(nu * m).reshape(nu, m)
    a, b = idx, np.roll(idx, -1, axis=0)
    a1, b1 = np.roll(a, -1, axis=1), np.roll(b, -1, axis=1)
    F = np.concatenate([np.stack([a, b, b1], -1).reshape(-1, 3), np.stack([a, b1, a1], -1).reshape(-1, 3)])
    return V, F


def mesh_part(c: C.Cyl, prog: Program, bore: float = 0.0, segments: int = 720):
    """The cam as a watertight triangle mesh: the blank minus the ring (robust mesh boolean, manifold3d). Returns
    (V, F, volume)."""
    import manifold3d as mf

    V, F = ring_mesh(c, prog)
    ring = mf.Manifold(mf.Mesh(vert_properties=V.astype(np.float32), tri_verts=F.astype(np.uint32)))
    if ring.status() != mf.Error.NoError:
        raise CylSolidError("the groove ring mesh is not closed")
    if ring.volume() < 0:
        ring = mf.Manifold(mf.Mesh(vert_properties=V.astype(np.float32), tri_verts=F[:, ::-1].astype(np.uint32)))
    blank = mf.Manifold.cylinder(c.length, c.x2, c.x2, segments).translate((0, 0, -c.length / 2))
    if bore > 0:
        blank = blank - mf.Manifold.cylinder(c.length + 2, bore / 2, bore / 2, 96).translate((0, 0, -c.length / 2 - 1))
    part = blank - ring
    out = part.to_mesh()
    return np.asarray(out.vert_properties, dtype=float)[:, :3], np.asarray(out.tri_verts, dtype=int), part.volume()
