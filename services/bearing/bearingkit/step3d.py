"""STEP (ISO 10303-21, AP214) solids of bearing parts, written directly (round 64, step 5, part 1).

Rings and rollers are solids of revolution. A part is given as a closed profile in its own (r, z) half plane,
counter-clockwise (material on the left), made of straight segments and circular arcs; it is turned a full turn
about its own z axis, which a frame places in the bearing. Each segment becomes one face:
    z constant → PLANE (an annulus or a disk);   r constant → CYLINDRICAL_SURFACE;   other lines → CONICAL_SURFACE;
    arcs → TOROIDAL_SURFACE (SPHERICAL_SURFACE when the arc's centre is on the axis).
A turned face is bounded by the circles at the segment's two ends and a seam along the segment (the way
OpenCASCADE writes them); a ball is one spherical face with a vertex loop. Several solids go into one file as
one product (the bearing as assembled).

Orientation: the loop [start circle, seam up, end circle back, seam down] runs counter-clockwise about the
outward normal of a counter-clockwise profile, so every face takes its surface's normal or its reverse
(same_sense) by comparing the surface normal with the outward one.

Plain code: no geometry kernel on the server. Checked locally with OpenCASCADE (valid solids, volumes equal to the
analytic ones).
"""

from __future__ import annotations

import datetime as _dt
import math

import numpy as np


class StepError(ValueError):
    pass


def _r(v: float) -> str:
    v = float(v)
    if abs(v) < 1e-15:
        v = 0.0
    s = repr(v)
    if "e" in s or "E" in s:
        mant, ex = s.lower().split("e")
        if "." not in mant:
            mant += "."
        return f"{mant}E{int(ex)}"
    return s if "." in s else s + "."


class Frame:
    """Where a part's own axes sit in the bearing: origin, z axis (the part's axis) and x axis."""

    def __init__(self, origin=(0.0, 0.0, 0.0), z=(0.0, 0.0, 1.0), x=(1.0, 0.0, 0.0)):
        self.o = np.array(origin, float)
        self.z = np.array(z, float) / np.linalg.norm(z)
        x = np.array(x, float)
        x = x - self.z * np.dot(x, self.z)
        self.x = x / np.linalg.norm(x)
        self.y = np.cross(self.z, self.x)

    def p(self, r, y, z):  # a point given in part coordinates (x = r on the seam half plane)
        return self.o + r * self.x + y * self.y + z * self.z

    def d(self, a, b, c):
        return a * self.x + b * self.y + c * self.z


class Writer:
    def __init__(self):
        self.rows: list[str] = []

    def add(self, text: str) -> str:
        self.rows.append(text)
        return f"#{len(self.rows)}"

    def pt(self, P) -> str:
        return self.add(f"CARTESIAN_POINT('',({_r(P[0])},{_r(P[1])},{_r(P[2])}))")

    def dir(self, D) -> str:
        return self.add(f"DIRECTION('',({_r(D[0])},{_r(D[1])},{_r(D[2])}))")

    def ax(self, P, Z, X) -> str:
        return self.add(f"AXIS2_PLACEMENT_3D('',{self.pt(P)},{self.dir(Z)},{self.dir(X)})")


def _outward(t):
    """Outward normal (r, z) of a counter-clockwise profile travelling along t."""
    return np.array([t[1], -t[0]])


def revolve(w: Writer, F: Frame, segs: list[dict], name: str = "") -> str:
    """One solid of revolution. segs: closed loop of {"a": (r, z), "b": (r, z), "arc": None | {"c": (r, z),
    "rho": ρ, "ccw": bool}} with every r ≥ 0; returns the MANIFOLD_SOLID_BREP reference."""
    n = len(segs)
    for k in range(n):
        if np.hypot(*np.subtract(segs[k]["b"], segs[(k + 1) % n]["a"])) > 1e-9:
            raise StepError("the profile is not closed")
    # vertices and circles at every profile corner off the axis
    verts, circ = [], []
    for s in segs:
        r, z = s["a"]
        v = w.add(f"VERTEX_POINT('',{w.pt(F.p(r, 0, z))})")
        verts.append(v)
        if r > 1e-12:
            c = w.add(f"CIRCLE('',{w.ax(F.p(0, 0, z), F.z, F.x)},{_r(r)})")
            circ.append(w.add(f"EDGE_CURVE('',{v},{v},{c},.T.)"))
        else:
            circ.append(None)

    def oe(edge, fwd):
        return w.add(f"ORIENTED_EDGE('',*,*,{edge},{'.T.' if fwd else '.F.'})")

    faces = []
    for k, s in enumerate(segs):
        (r0, z0), (r1, z1) = s["a"], s["b"]
        k1 = (k + 1) % n
        if r0 < 1e-12 and r1 < 1e-12:
            continue  # along the axis: no face
        arc = s.get("arc")
        if arc is None and abs(z1 - z0) < 1e-12:
            # annulus or disk normal to the axis
            out_up = r1 < r0  # travelling towards the axis on a CCW profile: the material is below (outward +z)
            nz = 1.0 if out_up else -1.0
            plane = w.add(f"PLANE('',{w.ax(F.p(0, 0, z0), F.z * nz, F.x)})")
            big, small = (k, k1) if r0 > r1 else (k1, k)
            bounds = [
                w.add(f"FACE_OUTER_BOUND('',{w.add(f'EDGE_LOOP({chr(39)}{chr(39)},({oe(circ[big], out_up)}))')},.T.)")
            ]
            if circ[small] is not None:
                el = w.add(f"EDGE_LOOP('',({oe(circ[small], not out_up)}))")
                bounds.append(w.add(f"FACE_BOUND('',{el},.T.)"))
            faces.append(w.add(f"ADVANCED_FACE('',({','.join(bounds)}),{plane},.T.)"))
            continue
        # a turned face: its surface, the meridian (seam) curve and the outward normal at the segment's middle
        if arc is None:
            t = np.array([r1 - r0, z1 - z0])
            t /= np.linalg.norm(t)
            mid = ((r0 + r1) / 2, (z0 + z1) / 2)
            out = _outward(t)
            line = w.add(
                f"LINE('',{w.pt(F.p(r0, 0, z0))},{w.add(f'VECTOR({chr(39)}{chr(39)},{w.dir(F.d(t[0], 0, t[1]))},1.)')})"
            )
            if abs(r1 - r0) < 1e-12:
                surf = w.add(f"CYLINDRICAL_SURFACE('',{w.ax(F.p(0, 0, z0), F.z, F.x)},{_r(r0)})")
                snorm = np.array([1.0, 0.0])
            else:
                # cone: placed at z0 with radius r0, semi-angle between the generatrix and the axis; STEP puts the
                # apex on the −axis side of the placement, so the placement axis points the way the radius grows
                up = 1.0 if (r1 - r0) * (z1 - z0) > 0 else -1.0
                semi = math.atan(abs(r1 - r0) / abs(z1 - z0))
                surf = w.add(f"CONICAL_SURFACE('',{w.ax(F.p(0, 0, z0), F.z * up, F.x)},{_r(r0)},{_r(semi)})")
                snorm = np.array([math.cos(semi), -up * math.sin(semi)])  # away from the axis
            seam_curve = line
            sense = float(np.dot(out, snorm)) > 0
        else:
            rc, zc = arc["c"]
            rho = float(arc["rho"])
            ccw = bool(arc["ccw"])
            a0 = math.atan2(z0 - zc, r0 - rc)
            a1 = math.atan2(z1 - zc, r1 - rc)
            if ccw and a1 <= a0:
                a1 += 2 * math.pi
            if not ccw and a1 >= a0:
                a1 -= 2 * math.pi
            am = (a0 + a1) / 2
            mid = (rc + rho * math.cos(am), zc + rho * math.sin(am))
            t = np.array([-math.sin(am), math.cos(am)]) * (1 if ccw else -1)
            out = _outward(t)
            # the meridian circle in the seam half plane; axis −y so its parameter runs counter-clockwise in (r, z)
            mc = w.add(f"CIRCLE('',{w.ax(F.p(rc, 0, zc), F.d(0, -1, 0), F.x)},{_r(rho)})")
            seam_curve = mc
            radial = np.array([math.cos(am), math.sin(am)])  # away from the tube centre
            if abs(rc) < 1e-12:
                surf = w.add(f"SPHERICAL_SURFACE('',{w.ax(F.p(0, 0, zc), F.z, F.x)},{_r(rho)})")
            else:
                if rc < rho:
                    raise StepError("a groove arc reaches past the axis")
                surf = w.add(f"TOROIDAL_SURFACE('',{w.ax(F.p(0, 0, zc), F.z, F.x)},{_r(rc)},{_r(rho)})")
            sense = float(np.dot(out, radial)) > 0
        seam = w.add(
            f"EDGE_CURVE('',{verts[k]},{verts[k1]},{seam_curve},{'.T.' if (arc is None or arc['ccw']) else '.F.'})"
        )
        loop = []
        if circ[k] is not None:
            loop.append(oe(circ[k], True))
        loop.append(oe(seam, True))
        if circ[k1] is not None:
            loop.append(oe(circ[k1], False))
        loop.append(oe(seam, False))
        el = w.add(f"EDGE_LOOP('',({','.join(loop)}))")
        b = w.add(f"FACE_BOUND('',{el},.T.)")
        faces.append(w.add(f"ADVANCED_FACE('',({b}),{surf},{'.T.' if sense else '.F.'})"))
        del mid
    shell = w.add(f"CLOSED_SHELL('',({','.join(faces)}))")
    return w.add(f"MANIFOLD_SOLID_BREP('{_esc(name)}',{shell})")


def sphere(w: Writer, centre, R: float, name: str = "") -> str:
    c = np.array(centre, float)
    v = w.add(f"VERTEX_POINT('',{w.pt(c - np.array([0, 0, R]))})")
    b = w.add(f"FACE_BOUND('',{w.add(f'VERTEX_LOOP({chr(39)}{chr(39)},{v})')},.T.)")
    s = w.add(f"SPHERICAL_SURFACE('',{w.ax(c, (0, 0, 1), (1, 0, 0))},{_r(R)})")
    f = w.add(f"ADVANCED_FACE('',({b}),{s},.T.)")
    return w.add(f"MANIFOLD_SOLID_BREP('{_esc(name)}',{w.add(f'CLOSED_SHELL({chr(39)}{chr(39)},({f}))')})")


def _esc(s: str) -> str:
    s = "".join(ch if 32 <= ord(ch) < 127 else "_" for ch in (s or "part"))
    return s.replace("'", "''")[:60] or "part"


def wrap(w: Writer, name: str, breps: list[str]) -> str:
    rows = list(w.rows)

    def add(t):
        rows.append(t)
        return f"#{len(rows)}"

    mm = add("( LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.) )")
    rad = add("( NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.) )")
    sr = add("( NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT() )")
    unc = add(
        f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),{mm},'distance_accuracy_value','confusion accuracy')"
    )
    ctx = add(
        f"( GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT(({unc})) "
        f"GLOBAL_UNIT_ASSIGNED_CONTEXT(({mm},{rad},{sr})) REPRESENTATION_CONTEXT('Context #1','3D') )"
    )
    o = add("CARTESIAN_POINT('',(0.,0.,0.))")
    zd, xd = add("DIRECTION('',(0.,0.,1.))"), add("DIRECTION('',(1.,0.,0.))")
    ax = add(f"AXIS2_PLACEMENT_3D('',{o},{zd},{xd})")
    rep = add(f"ADVANCED_BREP_SHAPE_REPRESENTATION('',({ax},{','.join(breps)}),{ctx})")
    app = add("APPLICATION_CONTEXT('core data for automotive mechanical design processes')")
    add(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,{app})")
    pc = add(f"PRODUCT_CONTEXT('',{app},'mechanical')")
    prod = add(f"PRODUCT('{_esc(name)}','{_esc(name)}','',({pc}))")
    pdf = add(f"PRODUCT_DEFINITION_FORMATION('','',{prod})")
    pdc = add(f"PRODUCT_DEFINITION_CONTEXT('part definition',{app},'design')")
    pd = add(f"PRODUCT_DEFINITION('design','',{pdf},{pdc})")
    pds = add(f"PRODUCT_DEFINITION_SHAPE('','',{pd})")
    add(f"SHAPE_DEFINITION_REPRESENTATION({pds},{rep})")
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    head = [
        "ISO-10303-21;",
        "HEADER;",
        "FILE_DESCRIPTION(('WenQuest Bearing design model'),'2;1');",
        f"FILE_NAME('{_esc(name)}.step','{stamp}',('WenQuest'),(''),'bearingkit','bearingkit','');",
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));",
        "ENDSEC;",
        "DATA;",
    ]
    body = [f"#{i + 1}={r};" for i, r in enumerate(rows)]
    return "\n".join(head + body + ["ENDSEC;", "END-ISO-10303-21;"]) + "\n"


def volume(segs: list[dict], steps: int = 2000) -> float:
    """Volume of the solid of revolution, V = π ∮ r² dz over the counter-clockwise profile (Green's theorem),
    straight segments exact and arcs integrated finely."""
    V = 0.0
    for s in segs:
        (r0, z0), (r1, z1) = s["a"], s["b"]
        arc = s.get("arc")
        if arc is None:
            # ∫ r² dz along a straight piece: (r0² + r0 r1 + r1²)/3 · Δz
            V += (r0 * r0 + r0 * r1 + r1 * r1) / 3 * (z1 - z0)
        else:
            rc, zc = arc["c"]
            rho = arc["rho"]
            a0 = math.atan2(z0 - zc, r0 - rc)
            a1 = math.atan2(z1 - zc, r1 - rc)
            if arc["ccw"] and a1 <= a0:
                a1 += 2 * math.pi
            if not arc["ccw"] and a1 >= a0:
                a1 -= 2 * math.pi
            a = np.linspace(a0, a1, steps + 1)
            r = rc + rho * np.cos(a)
            dz = rho * np.cos(a)
            f = r * r * dz
            V += float(np.sum((f[1:] + f[:-1]) / 2 * np.diff(a)))
    return math.pi * V
