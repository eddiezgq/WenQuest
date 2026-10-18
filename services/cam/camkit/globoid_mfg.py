"""Globoidal cam: the model made the way it is machined, a 4-axis program and its simulation (round 39, step 4c).

Model by the machining method (round 39 plan, section 三.2): a cutter the size of a roller follows every roller's
path relative to the blank (cam turned by θ, the cutter's axis along roller i at φ_i(θ)), and takes away what it
passes through. The blank is the globoid: around the cam axis, between the surfaces of revolution of the arcs of radius
ρ_o = ρ1 (outer, where the rollers enter) and ρ_r = ρ2 + clearance (groove bottom) about the turret centre. The cam is
kept as a height field over (cam angle, z): the radius of the material along each ray from the cam axis.

4-axis program (FANUC style, machine settings are examples): A turns the blank about the cam axis, B turns the rotary
table that carries the spindle about the turret axis, so the tool axis lies along a roller axis; X is set to the
centre distance at set-up; the tool's end is at the groove bottom. Finishing with a cutter of the roller's diameter
copies each roller exactly; points by chord tolerance on B(A) at the outer end of the roller.

Simulation reads the program text back and measures, along the normal at points of the exact flanks (from the
envelope, camkit.globoidal), where the cutter really leaves material.

Plain code: no AI, no network. Lengths mm, angles degrees at the edge.
"""

from __future__ import annotations

import math
import re
import struct

import numpy as np

from camkit import globoidal as G
from camkit.program import Program


class GloboidMfgError(ValueError):
    pass


# --------------------------------------------------------------------------------------------- model


def blank_radius(g: G.Globoid, z, rho):
    """Radius from the cam axis of the surface of revolution of an arc of radius rho about the turret centre."""
    return g.C - np.sqrt(np.maximum(rho * rho - z * z, 0.0))


def height_field(g: G.Globoid, prog: Program, d_theta: float = 0.25, dz: float = 0.5, steps: int = 1440):
    """Radius of the material along rays from the cam axis over cam angle (deg) and z (mm)."""
    tc = np.radians(np.arange(0, 360, d_theta))
    zs = np.arange(-g.L / 2, g.L / 2 + 1e-9, dz)
    rho_o, rho_r = g.rho1, g.rho2 + g.clearance
    top = np.tile(blank_radius(g, zs, rho_o)[None, :], (len(tc), 1))
    th = np.linspace(0, 2 * math.pi, steps, endpoint=False)
    phi, _, _, _ = prog.eval(th)
    ang = G.roller_angles(g, phi)
    r_cut = g.rr
    nt = len(tc)
    dt = tc[1] - tc[0]
    for j in range(steps):
        for i in range(g.n):
            a = ang[i, j]
            if not G.engaged(g, np.array([a]))[0]:
                continue
            u = np.array([math.cos(a), 0.0, math.sin(a)])
            # the roller axis in the cam frame: points ρ·u, turned back by θ about the cam axis
            p0 = G.cam_frame(g, np.zeros((3, 1)), th[j])[:, 0]  # turret centre
            uc = G.cam_frame_vec(u[:, None], th[j])[:, 0]
            # window of rays the cutter can reach: around the roller's middle
            mid = p0 + uc * (g.Rp)
            pol = math.atan2(mid[1], mid[0])
            rmid = math.hypot(mid[0], mid[1])
            half = (g.rr + g.b) / max(rmid - g.b, 1.0) + 2 * dt
            k0, k1 = int(math.floor((pol - half) / dt)), int(math.ceil((pol + half) / dt))
            ks = np.mod(np.arange(k0, k1 + 1), nt)
            zsel = np.flatnonzero(np.abs(zs - mid[2]) <= g.rr + g.b / 2 * abs(uc[2]) + g.b + dz)
            if not len(zsel):
                continue
            ct, st = np.cos(tc[ks])[:, None], np.sin(tc[ks])[:, None]
            Z = zs[zsel][None, :]
            # ray: X(r) = (r ct, r st, Z); inside the cutter if |(X − p0) × uc| < r_cut and (X − p0)·uc ≤ ρ_r
            dvec = np.stack([ct * np.ones_like(Z), st * np.ones_like(Z), np.zeros_like(Z) + 0 * ct])
            w0 = np.stack([-p0[0] * np.ones_like(Z * ct), -p0[1] * np.ones_like(Z * ct), Z - p0[2] + 0 * ct])
            du = dvec[0] * uc[0] + dvec[1] * uc[1] + dvec[2] * uc[2]
            wu = w0[0] * uc[0] + w0[1] * uc[1] + w0[2] * uc[2]
            # |w0 + r d − ((w0 + r d)·u) u|² = r_cut²  →  quadratic in r
            dd = 1 - du * du
            wd = (w0[0] * dvec[0] + w0[1] * dvec[1] + w0[2] * dvec[2]) - wu * du
            ww = (w0 * w0).sum(0) - wu * wu - r_cut * r_cut
            disc = wd * wd - dd * ww
            ok = (disc >= 0) & (dd > 1e-12)
            sq = np.sqrt(np.where(ok, disc, 0))
            r1 = np.where(ok, (-wd - sq) / np.where(dd > 1e-12, dd, 1), np.inf)
            r2 = np.where(ok, (-wd + sq) / np.where(dd > 1e-12, dd, 1), -np.inf)
            # the cutter's end: (X − p0)·u ≤ ρ_r, i.e. wu + r du ≤ ρ_r
            with np.errstate(divide="ignore", invalid="ignore"):
                r_end = (rho_r - wu) / du
            # du < 0: points farther out along the ray are nearer the turret (inside the cutter's length)
            lo = np.where(du < 0, np.maximum(r1, r_end), r1)
            hi = np.where(du > 0, np.minimum(r2, r_end), r2)
            cut = ok & (hi > lo)
            cur = top[np.ix_(ks, zsel)]
            reach = cut & (hi >= cur - 1e-9)  # the cut opens to the outside of the material
            top[np.ix_(ks, zsel)] = np.where(reach, np.minimum(cur, np.maximum(lo, 0.0)), cur)
    return np.degrees(tc), zs, top


def mesh(tc_deg, zs, top):
    """Triangles of the cam (outer surface from the height field, two flat end faces). Returns (vertices, faces)."""
    tc = np.radians(tc_deg)
    nt, nz = top.shape
    X = top * np.cos(tc)[:, None]
    Y = top * np.sin(tc)[:, None]
    Z = np.tile(zs[None, :], (nt, 1))
    V = np.stack([X.ravel(), Y.ravel(), Z.ravel()], axis=1)
    idx = np.arange(nt * nz).reshape(nt, nz)
    a = idx
    b = np.roll(idx, -1, axis=0)
    F = []
    for k in range(nz - 1):
        F.append(np.stack([a[:, k], b[:, k], b[:, k + 1]], axis=1))
        F.append(np.stack([a[:, k], b[:, k + 1], a[:, k + 1]], axis=1))
    F = np.concatenate(F)
    # end faces: fans to the centre points on the cam axis
    c0 = len(V)
    V = np.vstack([V, [[0, 0, zs[0]], [0, 0, zs[-1]]]])
    F0 = np.stack([np.full(nt, c0), b[:, 0], a[:, 0]], axis=1)
    F1 = np.stack([np.full(nt, c0 + 1), a[:, -1], b[:, -1]], axis=1)
    return V, np.concatenate([F, F0, F1])


def stl(V, F, name="cam") -> bytes:
    """Binary STL."""
    tri = V[F]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    ln = np.linalg.norm(n, axis=1)
    n = n / np.where(ln > 0, ln, 1)[:, None]
    head = (f"WenQuest Cam {name}"[:80]).encode("ascii", "replace").ljust(80, b" ")
    out = bytearray(head + struct.pack("<I", len(F)))
    rec = np.zeros(len(F), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = n, tri
    out += rec.tobytes()
    return bytes(out)


# --------------------------------------------------------------------------------------------- program


def a_b_path(g: G.Globoid, prog: Program, roller: int, tol: float, dense: int = 14400):
    """A (cam, deg) and B (turret, deg) program points for one roller over the angles where it is in the cam,
    so that B interpolated linearly in A stays within tol at the roller's outer end (radius ρ_r)."""
    th = np.linspace(0, 2 * math.pi, dense, endpoint=False)
    phi, _, _, _ = prog.eval(th)
    ang = G.roller_angles(g, phi)[roller]
    on = G.engaged(g, ang)
    if not on.any():
        return []
    # runs of engagement (around the turn)
    runs = []
    idx = np.flatnonzero(on)
    start = idx[0]
    prev = idx[0]
    for k in idx[1:]:
        if k != prev + 1:
            runs.append((start, prev))
            start = k
        prev = k
    runs.append((start, prev))
    if len(runs) > 1 and runs[0][0] == 0 and runs[-1][1] == dense - 1:
        runs = [(runs[-1][0] - dense, runs[0][1])] + runs[1:-1]
    R = g.rho2 + g.clearance
    out = []
    for a0, a1 in runs:
        ks = np.arange(a0 - 2, a1 + 3)
        A = np.degrees(th[0]) + ks * 360.0 / dense
        Bv = np.degrees(G.roller_angles(g, prog.position(np.radians(A)))[roller])
        sel = [0]
        i = 0
        n = len(A)
        while i < n - 1:
            j = n - 1
            lo, hi = i + 1, n - 1
            best = i + 1
            while lo <= hi:
                mid = (lo + hi) // 2
                lin = Bv[i] + (Bv[mid] - Bv[i]) * (A[i: mid + 1] - A[i]) / (A[mid] - A[i])
                err = np.max(np.abs(np.radians(lin - Bv[i: mid + 1]))) * R
                if err <= tol:
                    best = mid
                    lo = mid + 1
                else:
                    hi = mid - 1
            i = best
            sel.append(i)
            del j
        out.append((A[sel], Bv[sel]))
    return out


def program(g: G.Globoid, prog: Program, st: dict, title: str = "") -> str:
    tol = float(st.get("chord_tol") or 0.002)
    feed_rpm = float(st.get("work_rpm") or 2.0)  # cam turns per minute while cutting (example)
    out = ["%", f"O{int(st.get('prog_no') or 3903):04d} (WENQUEST CAM GLOBOIDAL 4-AXIS)", f"({_ascii(title)})",
           "(A: CAM BLANK ABOUT ITS AXIS - B: ROTARY TABLE ABOUT THE TURRET AXIS, TOOL AXIS ALONG A ROLLER)",
           f"(SET X = CENTRE DISTANCE {g.C:.4f} MM, TOOL END AT THE GROOVE BOTTOM {g.rho2 + g.clearance:.4f} MM)",
           f"(CUTTER RADIUS {g.rr:.4f} MM = ROLLER RADIUS, FINISHING)",
           f"(CHORD TOL {tol:.5f} MM AT THE ROLLER END - CAMKIT)", "(EXAMPLE SETTINGS - SET TO YOUR MACHINE)",
           "G21 G90 G40", "G94"]
    for i in range(g.n):
        for A, B in a_b_path(g, prog, i, tol):
            out.append(f"(ROLLER {i + 1}, {len(A)} POINTS)")
            out.append("G94")
            out.append(f"G00 A{A[0]:.4f} B{B[0]:.4f}")
            out.append("(PLUNGE ALONG THE TOOL AXIS TO THE GROOVE BOTTOM - SHOP PRACTICE)")
            out.append("G93")
            for k in range(1, len(A)):
                dtm = (A[k] - A[k - 1]) / (360.0 * feed_rpm)
                out.append(f"G01 A{A[k]:.4f} B{B[k]:.4f} F{1 / dtm:.2f}")
            out.append("(RETRACT ALONG THE TOOL AXIS)")
    out += ["G94", "M30", "%"]
    return "\n".join(out) + "\n"


def _ascii(s):
    t = re.sub(r"[^A-Za-z0-9 .,:+=/-]", "", s or "").strip().upper()
    return t[:60] or "CAM"


def parse(text: str):
    """Cutting passes of a globoidal program: lists of (A°, B°)."""
    passes, cur, mode = [], [], "G00"
    pos = {"A": None, "B": None}
    for raw in text.splitlines():
        line = re.sub(r"\(.*?\)", "", raw).strip().upper()
        if not line or line in ("%", "M30") or line.startswith("O"):
            continue
        words = dict(re.findall(r"([A-Z])([-+]?\d*\.?\d+)", line))
        gs = re.findall(r"G(\d+)", line)
        for gg in gs:
            if gg in ("0", "00"):
                mode = "G00"
            elif gg in ("1", "01"):
                mode = "G01"
        if "A" in words or "B" in words:
            new = {"A": float(words.get("A", pos["A"])), "B": float(words.get("B", pos["B"]))}
            if mode == "G01":
                if not cur:
                    cur.append((pos["A"], pos["B"]))
                cur.append((new["A"], new["B"]))
            elif cur:
                passes.append(np.array(cur))
                cur = []
            pos = new
    if cur:
        passes.append(np.array(cur))
    return passes


def simulate(g: G.Globoid, prog: Program, text: str, cutter_r: float | None = None, step_deg: float = 2.0, k: int = 5):
    """Normal deviation (mm) of the machined flanks from the envelope: + material left, − overcut; per flank point.
    Points every step_deg of cam angle where a roller is in the cam, k points along the roller."""
    r_c = g.rr if cutter_r is None else cutter_r
    passes = parse(text)
    if not passes:
        raise GloboidMfgError("the program has no cutting moves")
    # cutter positions (θ rad, turret angle rad), finely subdivided as the machine interpolates
    pos = []
    for p in passes:
        for (a0, b0), (a1, b1) in zip(p[:-1], p[1:], strict=True):
            n = max(1, int(math.ceil(abs(a1 - a0) / 0.02)))
            t = np.linspace(0, 1, n, endpoint=False)
            pos.append(np.stack([np.radians(a0 + (a1 - a0) * t), np.radians(b0 + (b1 - b0) * t)]))
    pos = np.concatenate(pos, axis=1)
    sfs = G.surfaces(g, prog, m=int(round(360 / step_deg)), k=k)
    devs, where = [], []
    for sf in sfs:
        on = sf["on"]
        if not on.any():
            continue
        Q = sf["Q"][:, on]  # cam frame
        Nin = sf["N"][:, on]  # into the cam
        thg = np.broadcast_to(sf["theta"][:, None], on.shape)[on]
        ng = -Nin  # out of the material, into the groove
        dev = np.full(Q.shape[1], np.nan)
        bins = np.floor(np.degrees(thg)).astype(int)
        for bval in np.unique(bins):
            qs = np.flatnonzero(bins == bval)
            c = math.radians(bval + 0.5)
            dth = np.angle(np.exp(1j * (pos[0] - c)))
            sel = np.abs(dth) < math.radians(6)
            if not sel.any():
                continue
            th_s, b_s = pos[0][sel], pos[1][sel]
            ct, st = np.cos(th_s), np.sin(th_s)
            u = np.stack([np.cos(b_s), np.zeros_like(b_s), np.sin(b_s)])  # (3, M)
            for q in qs:
                # the line P + t·ng, in the fixed frame of every cutter position
                X = ct * Q[0, q] - st * Q[1, q] + g.C
                Y = st * Q[0, q] + ct * Q[1, q]
                P = np.stack([X, Y, np.full_like(X, Q[2, q])])
                D = np.stack([ct * ng[0, q] - st * ng[1, q], st * ng[0, q] + ct * ng[1, q],
                              np.full_like(X, ng[2, q])])
                pu, du = (P * u).sum(0), (D * u).sum(0)
                pp = P - u * pu
                dp = D - u * du
                aa = (dp * dp).sum(0)
                bb = 2 * (pp * dp).sum(0)
                cc = (pp * pp).sum(0) - r_c * r_c
                disc = bb * bb - 4 * aa * cc
                ok = (disc >= 0) & (aa > 1e-12)
                sq = np.sqrt(np.where(ok, disc, 0))
                den = 2 * np.where(aa > 1e-12, aa, 1)
                t1 = np.where(ok, (-bb - sq) / den, np.inf)
                t2 = np.where(ok, (-bb + sq) / den, -np.inf)
                valid = ok & (t2 > 0)
                if valid.any():
                    dev[q] = float(np.min(t1[valid]))
        devs.append(dev)
        where.append({"roller": sf["roller"], "side": sf["side"], "deg": np.degrees(thg)})
    allv = np.concatenate(devs) if devs else np.array([])
    return {"dev": devs, "where": where, "max_over": float(np.nanmin(allv)) if allv.size else None,
            "max_under": float(np.nanmax(allv)) if allv.size else None,
            "unreached": int(np.isnan(allv).sum()), "points": int(allv.size)}
