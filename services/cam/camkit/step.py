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


def plate(name: str, outline: np.ndarray, thickness: float, bores: tuple[float, ...] = (),
          tol: float = 0.002) -> tuple[str, dict]:
    """A flat part: the closed counter-clockwise outline (2, N, dense) extruded by thickness, with round through
    holes centred on the origin (radii in bores). Used for the tool-changer arm (round 39, step 4c)."""
    if not thickness or thickness <= 0:
        raise StepError("give the thickness of the part")
    w = Writer()
    k, c, dev = fit(outline, tol)
    b, t = Loop(w, "bspline", 0.0, k, c), Loop(w, "bspline", thickness, k, c)
    holes = [(Loop(w, "circle", 0.0, R=r), Loop(w, "circle", thickness, R=r)) for r in bores]
    faces = [_plane_face(w, 0.0, False, [(b, False)] + [(hb, True) for hb, _ in holes]),
             _plane_face(w, thickness, True, [(t, True)] + [(ht, False) for _, ht in holes]),
             _side_face(w, b, t, True)]
    faces += [_side_face(w, hb, ht, False) for hb, ht in holes]
    shell = w.add(f"CLOSED_SHELL('',({','.join(faces)}))")
    brep = w.add(f"MANIFOLD_SOLID_BREP('{_esc(name)}',{shell})")
    area = _area(outline) - sum(math.pi * r * r for r in bores)
    return _wrap(w, name, brep), {"fit_dev": {"outline": dev}, "ctrl": {"outline": c.shape[1]},
                                  "volume": area * thickness}


# ----------------------------------------------------------------------------------- outlines made of pieces
# A flat part whose outline is a chain of exact circular arcs and B-spline pieces, so that the faces a finite-element
# set-up needs (a fork, a bore) come out as true cylinders (round 39, step 4d).


def fit_open(P: np.ndarray, tol: float = FIT_TOL):
    """Clamped cubic B-spline through an open chain of points (2, N), refined until within tol of the polyline."""
    N = P.shape[1]
    m = min(N, 24)
    while True:
        idx = np.unique(np.linspace(0, N - 1, m).round().astype(int))
        pts = P[:, idx]
        k = 3 if len(idx) > 3 else len(idx) - 1
        tck, u = splprep([pts[0], pts[1]], s=0, k=k)
        um = 0.5 * (u[:-1] + u[1:])
        q = np.array(splev(um, tck))
        j = cKDTree(P.T).query(q.T)[1]
        dev = float(np.max(_seg_dist_open(P, q, j))) if q.size else 0.0
        if dev <= tol or m >= N:
            t, c, kk = tck
            n = len(t) - kk - 1
            return np.asarray(t), np.array([c[0][:n], c[1][:n]]), kk, dev
        m = min(N, m * 2)


def _seg_dist_open(P, q, j):
    N = P.shape[1]
    best = np.full(q.shape[1], np.inf)
    for o in (-1, 0):
        a = P[:, np.clip(j + o, 0, N - 1)]
        b = P[:, np.clip(j + o + 1, 0, N - 1)]
        ab = b - a
        L2 = np.sum(ab * ab, axis=0)
        t = np.clip(np.sum((q - a) * ab, axis=0) / np.where(L2 > 0, L2, 1), 0, 1)
        d = q - (a + ab * t)
        best = np.minimum(best, np.hypot(d[0], d[1]))
    return best


def _knots_mult(t):
    ks, ms = [], []
    for v in t:
        if ks and abs(v - ks[-1]) < 1e-14:
            ms[-1] += 1
        else:
            ks.append(float(v))
            ms.append(1)
    return ks, ms


def plate_pieces(name: str, pieces: list[dict], thickness: float, bores: tuple[float, ...] = (),
                 tol: float = 0.002) -> tuple[str, dict]:
    """pieces, in order around the outline (counter-clockwise, material on the left):
         {"arc": (cx, cy, r), "start": (x, y), "end": (x, y), "ccw": bool}  — an exact circular arc
         {"pts": (2, N) array}                                             — a smooth piece (B-spline)
       each piece ends where the next begins. bores: round holes on the origin."""
    if not thickness or thickness <= 0:
        raise StepError("give the thickness of the part")
    w = Writer()
    zs = (0.0, thickness)
    n = len(pieces)
    starts = [tuple(pc["start"]) if "arc" in pc else (float(pc["pts"][0, 0]), float(pc["pts"][1, 0])) for pc in pieces]
    vtx = {z: [w.add(f"VERTEX_POINT('',{w.pt(x, y, z)})") for x, y in starts] for z in zs}
    edges = {z: [] for z in zs}
    surfs, devs = [], []
    for i, pc in enumerate(pieces):
        a, b = i, (i + 1) % n
        if "arc" in pc:
            cx, cy, r = pc["arc"]
            for z in zs:
                place = w.add(f"AXIS2_PLACEMENT_3D('',{w.pt(cx, cy, z)},{w.dir(0, 0, 1)},{w.dir(1, 0, 0)})")
                circ = w.add(f"CIRCLE('',{place},{_r(r)})")
                sense = ".T." if pc["ccw"] else ".F."
                edges[z].append(w.add(f"EDGE_CURVE('',{vtx[z][a]},{vtx[z][b]},{circ},{sense})"))
            ax = w.add(f"AXIS2_PLACEMENT_3D('',{w.pt(cx, cy, 0)},{w.dir(0, 0, 1)},{w.dir(1, 0, 0)})")
            surfs.append((w.add(f"CYLINDRICAL_SURFACE('',{ax},{_r(r)})"), bool(pc["ccw"])))
        else:
            P = np.asarray(pc["pts"], float)
            t, c, k, dev = fit_open(P, tol)
            devs.append(dev)
            ks, ms = _knots_mult(t)
            curves = {}
            for z in zs:
                cps = ",".join(w.pt(c[0, j], c[1, j], z) for j in range(c.shape[1]))
                curves[z] = w.add(f"B_SPLINE_CURVE_WITH_KNOTS('',{k},({cps}),.UNSPECIFIED.,.F.,.F.,"
                                  f"({','.join(str(x) for x in ms)}),({','.join(_r(x) for x in ks)}),.UNSPECIFIED.)")
                edges[z].append(w.add(f"EDGE_CURVE('',{vtx[z][a]},{vtx[z][b]},{curves[z]},.T.)"))
            vec = w.add(f"VECTOR('',{w.dir(0, 0, 1)},{_r(thickness)})")
            surfs.append((w.add(f"SURFACE_OF_LINEAR_EXTRUSION('',{curves[0.0]},{vec})"), True))
    seams = []
    for i in range(n):
        x, y = starts[i]
        vec = w.add(f"VECTOR('',{w.dir(0, 0, 1)},{_r(thickness)})")
        line = w.add(f"LINE('',{w.pt(x, y, 0)},{vec})")
        seams.append(w.add(f"EDGE_CURVE('',{vtx[0.0][i]},{vtx[thickness][i]},{line},.T.)"))

    def oe(e, fwd):
        return w.add(f"ORIENTED_EDGE('',*,*,{e},{'.T.' if fwd else '.F.'})")

    faces = []
    for i, (surf, sense) in enumerate(surfs):
        b = (i + 1) % n
        el = w.add(f"EDGE_LOOP('',({oe(edges[0.0][i], True)},{oe(seams[b], True)},{oe(edges[thickness][i], False)},"
                   f"{oe(seams[i], False)}))")
        faces.append(w.add(f"ADVANCED_FACE('',({w.add(f'FACE_OUTER_BOUND({chr(39)}{chr(39)},{el},.T.)')}),{surf},"
                           f"{'.T.' if sense else '.F.'})"))
    holes = [(Loop(w, "circle", 0.0, R=r), Loop(w, "circle", thickness, R=r)) for r in bores]
    for z, up in ((0.0, False), (thickness, True)):
        order = [oe(e, up) for e in (edges[z] if up else edges[z][::-1])]
        bounds = [w.add(f"FACE_OUTER_BOUND('',{w.add(f'EDGE_LOOP({chr(39)}{chr(39)},({chr(44).join(order)}))')},.T.)")]
        for hb, ht in holes:
            lp = ht if up else hb
            bounds.append(w.add(f"FACE_BOUND('',{w.add(f'EDGE_LOOP({chr(39)}{chr(39)},({lp.oe(not up)}))')},.T.)"))
        plane = w.add(f"PLANE('',{w.axis(z, 1.0 if up else -1.0)})")
        faces.append(w.add(f"ADVANCED_FACE('',({','.join(bounds)}),{plane},.T.)"))
    for hb, ht in holes:
        p0 = w.pt(hb.start[0], hb.start[1], 0.0)
        line = w.add(f"LINE('',{p0},{w.add(f'VECTOR({chr(39)}{chr(39)},{w.dir(0, 0, 1)},{_r(thickness)})')})")
        seam = w.add(f"EDGE_CURVE('',{hb.vertex},{ht.vertex},{line},.T.)")
        el = w.add(f"EDGE_LOOP('',({oe(seam, True)},{ht.oe(True)},{oe(seam, False)},{hb.oe(False)}))")
        cyl = w.add(f"CYLINDRICAL_SURFACE('',{w.axis(0.0)},{_r(abs(hb.start[0]))})")
        faces.append(w.add(f"ADVANCED_FACE('',({w.add(f'FACE_OUTER_BOUND({chr(39)}{chr(39)},{el},.T.)')}),{cyl},.F.)"))
    shell = w.add(f"CLOSED_SHELL('',({','.join(faces)}))")
    brep = w.add(f"MANIFOLD_SOLID_BREP('{_esc(name)}',{shell})")
    return _wrap(w, name, brep), {"fit_dev": {"outline": max(devs) if devs else 0.0}, "pieces": n}
