"""STEP (ISO 10303-21, AP214) solids of disk and groove cams, written directly (round 39, step 3).

The cam outline is a periodic cubic B-spline interpolating the design curve; the fit is checked against the dense
design curve between every two interpolation points and refined until the deviation is within the tolerance.
- External cam: the outline extruded by the thickness.
- Groove cam: a disk blank (radius and thickness given by the user) with the groove cut from the top face.
No bore or keyway: there are no data for them, so they are not drawn.

Plain code: no geometry kernel on the server. Checked locally with OpenCASCADE (round 39 plan, step 3 acceptance).
"""

from __future__ import annotations

import datetime as _dt
import math

import numpy as np
from scipy.interpolate import splev, splprep
from scipy.spatial import cKDTree

FIT_TOL = 0.0005  # mm


class StepError(ValueError):
    pass


def fit(P: np.ndarray, tol: float = FIT_TOL):
    """Periodic cubic B-spline through points of the closed counter-clockwise curve P (2, N, dense).
    Returns (knots, control points (2, n), deviation)."""
    N = P.shape[1]
    tree = cKDTree(P.T)
    m = 180
    while True:
        idx = np.linspace(0, N, m, endpoint=False).astype(int)
        pts = P[:, idx]
        pts = np.concatenate([pts, pts[:, :1]], axis=1)
        tck, u = splprep([pts[0], pts[1]], s=0, per=1, k=3)
        um = 0.5 * (u[:-1] + u[1:])
        q = np.array(splev(np.concatenate([um, u]), tck))
        d, j = tree.query(q.T)
        # distance to the dense polyline, not just its vertices: project on the two neighbouring segments
        dev = float(np.max(_seg_dist(P, q, j)))
        if dev <= tol or m >= N:
            t, c, k = tck
            n = len(t) - k - 1
            ctrl = np.array([c[0][:n], c[1][:n]])
            return np.asarray(t), ctrl, dev
        m = min(N, m * 2)


def _seg_dist(P, q, j):
    N = P.shape[1]
    best = np.full(q.shape[1], np.inf)
    for o in (-1, 0):
        a = P[:, (j + o) % N]
        b = P[:, (j + o + 1) % N]
        ab = b - a
        L2 = np.sum(ab * ab, axis=0)
        t = np.clip(np.sum((q - a) * ab, axis=0) / np.where(L2 > 0, L2, 1), 0, 1)
        d = q - (a + ab * t)
        best = np.minimum(best, np.hypot(d[0], d[1]))
    return best


class Writer:
    def __init__(self):
        self.rows: list[str] = []

    def add(self, text: str) -> str:
        self.rows.append(text)
        return f"#{len(self.rows)}"

    # geometry -------------------------------------------------------------------------------------------------
    def pt(self, x, y, z) -> str:
        return self.add(f"CARTESIAN_POINT('',({_r(x)},{_r(y)},{_r(z)}))")

    def dir(self, x, y, z) -> str:
        return self.add(f"DIRECTION('',({_r(x)},{_r(y)},{_r(z)}))")

    def axis(self, z=0.0, up=1.0) -> str:
        return self.add(f"AXIS2_PLACEMENT_3D('',{self.pt(0, 0, z)},{self.dir(0, 0, up)},{self.dir(1, 0, 0)})")

    def bspline(self, knots, ctrl, z) -> str:
        n = ctrl.shape[1]
        cps = ",".join(self.pt(ctrl[0, i], ctrl[1, i], z) for i in range(n))
        ks = ",".join(_r(k) for k in knots)
        ms = ",".join("1" for _ in knots)
        return self.add(f"B_SPLINE_CURVE_WITH_KNOTS('',3,({cps}),.UNSPECIFIED.,.T.,.F.,({ms}),({ks}),.UNSPECIFIED.)")

    def circle(self, R, z) -> str:
        return self.add(f"CIRCLE('',{self.axis(z)},{_r(R)})")


def _r(v: float) -> str:
    s = repr(float(v))
    if "e" in s or "E" in s:
        mant, ex = s.lower().split("e")
        if "." not in mant:
            mant += "."
        return f"{mant}E{int(ex)}"
    return s if "." in s else s + "."


class Loop:
    """A closed curve at height z: one edge, one vertex."""

    def __init__(self, w: Writer, kind: str, z: float, knots=None, ctrl=None, R=None):
        self.w, self.z = w, z
        if kind == "bspline":
            self.curve = w.bspline(knots, ctrl, z)
            x, y = splev(knots[3], (knots, [ctrl[0], ctrl[1]], 3))
            self.start = (float(x), float(y))
        else:
            self.curve = w.circle(R, z)
            self.start = (R, 0.0)
        self.vertex = w.add(f"VERTEX_POINT('',{w.pt(self.start[0], self.start[1], z)})")
        self.edge = w.add(f"EDGE_CURVE('',{self.vertex},{self.vertex},{self.curve},.T.)")

    def oe(self, forward: bool) -> str:
        return self.w.add(f"ORIENTED_EDGE('',*,*,{self.edge},{'.T.' if forward else '.F.'})")


def _plane_face(w: Writer, z: float, up: bool, loops: list[tuple[Loop, bool]]) -> str:
    """loops: (loop, forward); the first is the outer bound."""
    bounds = []
    for i, (lp, fwd) in enumerate(loops):
        el = w.add(f"EDGE_LOOP('',({lp.oe(fwd)}))")
        kind = "FACE_OUTER_BOUND" if i == 0 else "FACE_BOUND"
        bounds.append(w.add(f"{kind}('',{el},.T.)"))
    plane = w.add(f"PLANE('',{w.axis(z, 1.0 if up else -1.0)})")
    return w.add(f"ADVANCED_FACE('',({','.join(bounds)}),{plane},.T.)")


def _side_face(w: Writer, bot: Loop, top: Loop, outward: bool) -> str:
    """The wall between two copies of one counter-clockwise curve; outward: material inside the curve."""
    p0 = w.pt(bot.start[0], bot.start[1], bot.z)
    h = top.z - bot.z
    line = w.add(f"LINE('',{p0},{w.add(f'VECTOR({chr(39)}{chr(39)},{w.dir(0, 0, 1)},{_r(h)})')})")
    seam = w.add(f"EDGE_CURVE('',{bot.vertex},{top.vertex},{line},.T.)")
    s_up = w.add(f"ORIENTED_EDGE('',*,*,{seam},.T.)")
    s_dn = w.add(f"ORIENTED_EDGE('',*,*,{seam},.F.)")
    if outward:
        edges = [bot.oe(True), s_up, top.oe(False), s_dn]
    else:
        edges = [s_up, top.oe(True), s_dn, bot.oe(False)]
    el = w.add(f"EDGE_LOOP('',({','.join(edges)}))")
    vec = w.add(f"VECTOR('',{w.dir(0, 0, 1)},{_r(h)})")
    surf = w.add(f"SURFACE_OF_LINEAR_EXTRUSION('',{bot.curve},{vec})")
    bound = w.add(f"FACE_OUTER_BOUND('',{el},.T.)")
    return w.add(f"ADVANCED_FACE('',({bound}),{surf},{'.T.' if outward else '.F.'})")


def solid(name: str, profile: np.ndarray, thickness: float, outer: np.ndarray | None = None,
          blank_r: float | None = None, plate: float | None = None) -> tuple[str, dict]:
    """STEP text and fit report. profile/outer: dense counter-clockwise closed curves (2, N)."""
    if not thickness or thickness <= 0:
        raise StepError("give the thickness (the contact width) for the 3D model")
    w = Writer()
    kp, cp, dev_p = fit(profile)
    report = {"fit_dev": {"profile": dev_p}, "ctrl": {"profile": cp.shape[1]}}
    faces = []
    if outer is None:
        b, t = Loop(w, "bspline", 0.0, kp, cp), Loop(w, "bspline", thickness, kp, cp)
        faces += [_plane_face(w, 0.0, False, [(b, False)]), _plane_face(w, thickness, True, [(t, True)]),
                  _side_face(w, b, t, True)]
        report["volume"] = _area(profile) * thickness
    else:
        if not blank_r or not plate:
            raise StepError("give the blank radius and plate thickness of the groove cam")
        if plate <= thickness:
            raise StepError("the plate must be thicker than the groove depth")
        if blank_r <= float(np.max(np.hypot(outer[0], outer[1]))):
            raise StepError("the blank radius must be larger than the groove's outer flank")
        ko, co, dev_o = fit(outer)
        report["fit_dev"]["outer"] = dev_o
        report["ctrl"]["outer"] = co.shape[1]
        zf = plate - thickness
        cb, ct = Loop(w, "circle", 0.0, R=blank_r), Loop(w, "circle", plate, R=blank_r)
        it, if_ = Loop(w, "bspline", plate, kp, cp), Loop(w, "bspline", zf, kp, cp)
        ot, of = Loop(w, "bspline", plate, ko, co), Loop(w, "bspline", zf, ko, co)
        faces += [
            _plane_face(w, 0.0, False, [(cb, False)]),
            _side_face(w, cb, ct, True),
            _plane_face(w, plate, True, [(ct, True), (ot, False)]),
            _plane_face(w, plate, True, [(it, True)]),
            _plane_face(w, zf, True, [(of, True), (if_, False)]),
            _side_face(w, if_, it, True),
            _side_face(w, of, ot, False),
        ]
        report["volume"] = math.pi * blank_r**2 * plate - (_area(outer) - _area(profile)) * thickness
    shell = w.add(f"CLOSED_SHELL('',({','.join(faces)}))")
    brep = w.add(f"MANIFOLD_SOLID_BREP('{_esc(name)}',{shell})")
    return _wrap(w, name, brep), report


def _area(P):
    return 0.5 * abs(float(np.sum(P[0] * np.roll(P[1], -1) - np.roll(P[0], -1) * P[1])))


def _esc(s: str) -> str:
    s = "".join(ch if 32 <= ord(ch) < 127 else "_" for ch in (s or "cam"))
    return s.replace("'", "''")[:60] or "cam"


def _wrap(w: Writer, name: str, brep: str) -> str:
    rows = list(w.rows)
    n0 = len(rows)

    def add(t):
        rows.append(t)
        return f"#{len(rows)}"

    mm = add("( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) )")
    rad = add("( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) )")
    sr = add("( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() )")
    unc = add(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),{mm},'distance_accuracy_value',"
              "'confusion accuracy')")
    ctx = add(f"( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT(({unc})) "
              f"GLOBAL_UNIT_ASSIGNED_CONTEXT(({mm},{rad},{sr})) REPRESENTATION_CONTEXT('Context #1','3D') )")
    o = add("CARTESIAN_POINT('',(0.,0.,0.))")
    zd, xd = add("DIRECTION('',(0.,0.,1.))"), add("DIRECTION('',(1.,0.,0.))")
    ax = add(f"AXIS2_PLACEMENT_3D('',{o},{zd},{xd})")
    rep = add(f"ADVANCED_BREP_SHAPE_REPRESENTATION('',({ax},{brep}),{ctx})")
    app = add("APPLICATION_CONTEXT('core data for automotive mechanical design processes')")
    add(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,{app})")
    pc = add(f"PRODUCT_CONTEXT('',{app},'mechanical')")
    prod = add(f"PRODUCT('{_esc(name)}','{_esc(name)}','',({pc}))")
    pdf = add(f"PRODUCT_DEFINITION_FORMATION('','',{prod})")
    pdc = add(f"PRODUCT_DEFINITION_CONTEXT('part definition',{app},'design')")
    pd = add(f"PRODUCT_DEFINITION('design','',{pdf},{pdc})")
    pds = add(f"PRODUCT_DEFINITION_SHAPE('','',{pd})")
    add(f"SHAPE_DEFINITION_REPRESENTATION({pds},{rep})")
    del n0
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    head = ["ISO-10303-21;", "HEADER;", "FILE_DESCRIPTION(('WenQuest Cam design model'),'2;1');",
            f"FILE_NAME('{_esc(name)}.step','{stamp}',('WenQuest'),(''),'camkit','camkit','');",
            "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));", "ENDSEC;", "DATA;"]
    body = [f"#{i + 1}={r};" for i, r in enumerate(rows)]
    return "\n".join(head + body + ["ENDSEC;", "END-ISO-10303-21;"]) + "\n"
