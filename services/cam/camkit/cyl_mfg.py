"""Cylindrical cam: 4-axis program, its simulation, and the model made the way it is machined (round 39, step 8c).

Machine (a machining centre with a rotary table, FANUC style; settings are examples): A turns the blank about the cam
axis, X runs along the cam axis, Y across it, the tool axis is Z (radial to the cam, like the roller axis). Translating
follower: the roller axis always passes through the cam axis, so Y stays 0 (A + X); oscillating follower: the roller
axis moves sideways with the arm, so Y moves too (A + X + Y). The tool's end is at the groove bottom.

Finishing with a cutter of the roller's size (a tapered cutter, apex on the cam axis, for a tapered roller) along the
roller axis copies the roller exactly. A smaller cylindrical cutter (cylindrical roller only) cuts each flank in its own
pass, its axis moved towards that flank by (r_r − r_t) along the flank normal at the pitch radius; the simulation shows
what this leaves. Points by chord tolerance: X and Y interpolated linearly in A stay within the tolerance.

Simulation reads the program text back, sweeps the cutter through the program's positions and measures, along the normal
at points of the exact flanks (camkit.cylindrical), how far the machined surface is: + material left, − overcut.
Model: the STL is the blank minus the groove ring the cutter sweeps (camkit.cyl_solid). height_field() below is an
independent check for translating followers: everything the cutter passes through removed from the blank, kept as the
radius of the material along each ray from the cam axis (it cannot hold the overhanging walls an off-axis cutter
leaves with an oscillating follower).

Plain code: no AI, no network. Lengths mm, angles degrees at the edge.
"""

from __future__ import annotations

import math
import re

import numpy as np

from camkit import cylindrical as C
from camkit.globoid_mfg import mesh, stl  # noqa: F401  (same height-field mesh and STL writer)
from camkit.program import Program


class CylMfgError(ValueError):
    pass


def settings(c: C.Cyl, st: dict | None) -> dict:
    st = dict(st or {})
    rt = C._num(st.get("tool_r"))
    rt = c.rr if rt is None else rt
    if c.roller == "cone" and abs(rt - c.rr) > 1e-9:
        raise CylMfgError("a tapered roller is copied by a tapered cutter of its own size: "
                          "leave the cutter radius empty")
    if not 0 < rt <= c.rr + 1e-9:
        raise CylMfgError("the cutter radius is more than 0 and not more than the roller radius")
    tol = C._num(st.get("chord_tol")) or 0.002
    if not 1e-5 <= tol <= 0.1:
        raise CylMfgError("the chord tolerance is between 0.00001 and 0.1 mm")
    return {"tool_r": rt, "chord_tol": tol, "work_rpm": C._num(st.get("work_rpm")) or 2.0,
            "prog_no": int(C._num(st.get("prog_no")) or 3904)}


# --------------------------------------------------------------------------------------------- tool path


def tool_path(c: C.Cyl, prog: Program, side: int, rt: float, dense: int = 14400):
    """Cutter axis (Y, X machine = y, z of the kernel's fixed frame) over the turn, and the cam angle θ (rad). side 0
    = along the roller axis (cutter the roller's size); ±1 = towards that flank (smaller cutter)."""
    th = np.linspace(0, 2 * math.pi, dense + 1)
    ps = C.pose(c, prog, th[:, None])
    y, z = ps["cy"][:, 0].copy(), ps["cz"][:, 0].copy()
    if side:
        _, n, *_ = C.contact(c, ps, np.array([[c.Rp]]), side)
        ny, nz = n[1][:, 0], n[2][:, 0]
        ln = np.hypot(ny, nz)
        # n points from the roller into the cam: move towards that flank. A cone's normal leans by its taper, so a
        # sideways shift s moves its surface s / √(1 + k²) along the normal: shift by √(1 + k²) · gap/2
        d = (c.rr - rt) + c.gap / 2 * math.sqrt(1 + c.k * c.k)
        y += d * ny / ln
        z += d * nz / ln
    return th, y, z


def select(A, Y, X, tol):
    """Indices of the points kept so that Y and X, linear in A between kept points, stay within tol."""
    sel, i, n = [0], 0, len(A)
    while i < n - 1:
        lo, hi, best = i + 1, n - 1, i + 1
        while lo <= hi:
            mid = (lo + hi) // 2
            f = (A[i: mid + 1] - A[i]) / (A[mid] - A[i])
            e = np.hypot(Y[i] + (Y[mid] - Y[i]) * f - Y[i: mid + 1], X[i] + (X[mid] - X[i]) * f - X[i: mid + 1])
            if np.max(e) <= tol:
                best, lo = mid, mid + 1
            else:
                hi = mid - 1
        i = best
        sel.append(i)
    return np.array(sel)


def joints(prog: Program, dense: int) -> list[int]:
    """Indices (on the dense grid of tool_path) where one motion segment ends and the next begins: points are kept
    there, so a dwell is one exact straight move."""
    out, a = [], 0.0
    for s in prog.segments or []:
        a += s.beta
        out.append(int(round(a / (2 * math.pi) * dense)))
    return sorted({0, dense, *[min(max(k, 0), dense) for k in out]})


def select_with_joints(A, Y, X, tol, brk):
    keep = []
    for a, b in zip(brk[:-1], brk[1:], strict=True):
        if b <= a:
            continue
        part = select(A[a: b + 1], Y[a: b + 1], X[a: b + 1], tol) + a
        keep.extend(part.tolist() if not keep else part[1:].tolist())
    return np.array(keep)


def program(c: C.Cyl, prog: Program, st: dict, title: str = "") -> str:
    s = settings(c, st)
    rt, tol = s["tool_r"], s["chord_tol"]
    sides = (0,) if abs(rt - c.rr) < 1e-9 and c.gap == 0 else (1, -1)  # a side clearance: one pass per flank
    useY = c.follower == "oscillating" or len(sides) > 1
    tool = (f"TAPERED CUTTER, APEX ON THE CAM AXIS, RADIUS {c.rr:.4f} MM AT {c.Rp:.4f} MM" if c.roller == "cone"
            else f"CUTTER RADIUS {rt:.4f} MM" + (" = ROLLER RADIUS" if abs(rt - c.rr) < 1e-9 else "")
            + ("" if not sides[0] else " - ONE PASS PER FLANK"))
    if c.gap:
        tool += f") (SIDE CLEARANCE {c.gap:.4f} MM: EACH FLANK {c.gap / 2:.4f} MM AWAY FROM THE ROLLER"
    out = ["%", f"O{s['prog_no']:04d} (WENQUEST CAM CYLINDRICAL 4-AXIS)", f"({_ascii(title)})",
           "(A: BLANK ABOUT THE CAM AXIS - X: ALONG THE CAM AXIS - Y: ACROSS - TOOL AXIS Z RADIAL)",
           f"(X0 AT THE MIDDLE OF THE CAM LENGTH {c.length:.4f} MM, Y0 ON THE CAM AXIS)",
           f"(TOOL END AT THE GROOVE BOTTOM: RADIUS {c.core:.4f} MM FROM THE CAM AXIS)", f"({tool})",
           f"(CHORD TOL {tol:.5f} MM - CAMKIT)", "(EXAMPLE SETTINGS - SET TO YOUR MACHINE)", "G21 G90 G40", "G94"]
    for side in sides:
        th, y, z = tool_path(c, prog, side, rt)
        A = np.degrees(c.sigma * th)
        keep = select_with_joints(A, y, z, tol, joints(prog, len(th) - 1))
        A, y, z = A[keep], y[keep], z[keep]
        out.append(f"(PASS {'ALONG THE ROLLER AXIS' if side == 0 else 'FLANK ' + ('+' if side > 0 else '-')}, "
                   f"{len(A)} POINTS)")
        out.append("G94")
        out.append(f"G00 A{A[0]:.4f} X{z[0]:.4f}" + (f" Y{y[0]:.4f}" if useY else ""))
        out.append("(PLUNGE ALONG Z TO THE GROOVE BOTTOM - SHOP PRACTICE)")
        out.append("G93")
        for k in range(1, len(A)):
            dtm = abs(A[k] - A[k - 1]) / (360.0 * s["work_rpm"])
            out.append(f"G01 A{A[k]:.4f} X{z[k]:.4f}" + (f" Y{y[k]:.4f}" if useY else "") + f" F{1 / dtm:.2f}")
        out.append("(RETRACT ALONG Z)")
    out += ["G94", "M30", "%"]
    return "\n".join(out) + "\n"


def _ascii(s):
    t = re.sub(r"[^A-Za-z0-9 .,:+=/-]", "", s or "").strip().upper()
    return t[:60] or "CAM"


def parse(text: str):
    """Cutting passes: arrays of (A°, X, Y)."""
    passes, cur, mode = [], [], "G00"
    pos = {"A": None, "X": None, "Y": 0.0}
    for raw in text.splitlines():
        line = re.sub(r"\(.*?\)", "", raw).strip().upper()
        if not line or line in ("%", "M30") or line.startswith("O"):
            continue
        words = dict(re.findall(r"([A-Z])([-+]?\d*\.?\d+)", line))
        for g in re.findall(r"G(\d+)", line):
            if g in ("0", "00"):
                mode = "G00"
            elif g in ("1", "01"):
                mode = "G01"
        if any(k in words for k in "AXY"):
            new = {k: float(words[k]) if k in words else pos[k] for k in "AXY"}
            if mode == "G01":
                if not cur:
                    cur.append((pos["A"], pos["X"], pos["Y"]))
                cur.append((new["A"], new["X"], new["Y"]))
            elif cur:
                passes.append(np.array(cur))
                cur = []
            pos = new
    if cur:
        passes.append(np.array(cur))
    return passes


def positions(c: C.Cyl, text: str, step_deg: float = 0.02):
    """Cutter positions as the machine interpolates: cam angle θ (rad), Y, X; finely subdivided."""
    passes = parse(text)
    if not passes:
        raise CylMfgError("the program has no cutting moves")
    out = []
    for p in passes:
        for a, b in zip(p[:-1], p[1:], strict=True):
            n = max(1, int(math.ceil(abs(b[0] - a[0]) / step_deg)))
            t = np.linspace(0, 1, n, endpoint=False)[:, None]
            out.append(a + (b - a) * t)
    q = np.concatenate(out)
    return np.radians(q[:, 0]) * c.sigma, q[:, 2], q[:, 1]


def _cutter_hit(c: C.Cyl, rt, P, D, Y, X):
    """Entry and exit t of the line P + tD (fixed frame, arrays (3, M)) into the cutter, axis x̂ through (·, Y, X)."""
    py, pz, dy, dz = P[1] - Y, P[2] - X, D[1], D[2]
    if c.roller == "cone":
        k2 = c.k * c.k
        aa = dy * dy + dz * dz - k2 * D[0] * D[0]
        bb = 2 * (py * dy + pz * dz - k2 * P[0] * D[0])
        cc = py * py + pz * pz - k2 * P[0] * P[0]
    else:
        aa = dy * dy + dz * dz
        bb = 2 * (py * dy + pz * dz)
        cc = py * py + pz * pz - rt * rt
    disc = bb * bb - 4 * aa * cc
    ok = (disc >= 0) & (np.abs(aa) > 1e-12)
    sq = np.sqrt(np.where(ok, disc, 0))
    den = 2 * np.where(np.abs(aa) > 1e-12, aa, 1)
    r1, r2 = (-bb - sq) / den, (-bb + sq) / den
    t1, t2 = np.where(ok, np.minimum(r1, r2), np.inf), np.where(ok, np.maximum(r1, r2), -np.inf)
    return t1, t2


def simulate(c: C.Cyl, prog: Program, text: str, tool_r: float | None = None, step_deg: float = 1.0, k: int = 5):
    """Normal deviation (mm) of the machined flanks from the exact ones: + material left, − overcut."""
    rt = c.rr if tool_r is None else tool_r
    th_c, Yc, Xc = positions(c, text)
    sfs = C.surfaces(c, prog, m=int(round(360 / step_deg)), k=k)
    out = []
    for sf in sfs:
        Q, N = sf["Q"], sf["N"]  # (3, m, k) cam frame; N into the cam
        m = Q.shape[1]
        dev = np.full((m, k), np.nan)
        for j in range(m):
            t0 = sf["theta"][j]
            near = np.abs(np.angle(np.exp(1j * (th_c - t0)))) < math.radians(8)
            if not near.any():
                continue
            ths, ys, xs = th_c[near], Yc[near], Xc[near]
            for i in range(k):
                ng = -N[:, j, i:i + 1]  # out of the material, into the groove
                q = Q[:, j, i:i + 1] - (c.gap / 2) * ng  # the flank as made: half the clearance away from the roller
                P = C.fixed_frame(c, q, ths)
                D = C.fixed_frame(c, ng, ths)
                t1, t2 = _cutter_hit(c, rt, P, D, ys, xs)
                valid = t2 > 0
                if valid.any():
                    dev[j, i] = float(np.min(t1[valid]))
        out.append({"side": sf["side"], "deg": np.degrees(sf["theta"]), "dev": dev})
    allv = np.concatenate([o["dev"].ravel() for o in out])
    return {"flanks": out, "max_over": float(np.nanmin(allv)), "max_under": float(np.nanmax(allv)),
            "unreached": int(np.isnan(allv).sum()), "points": int(allv.size)}


# --------------------------------------------------------------------------------------------- model


def height_field(c: C.Cyl, text: str, d_theta: float = 0.5, dz: float = 0.5, step_deg: float = 0.25):
    """Radius of the material along rays from the cam axis over cam-frame azimuth (deg) and z (mm), after the cutter of
    the program has passed (the cutter the program was made for: radius in its header, or the roller's)."""
    m = re.search(r"CUTTER RADIUS ([\d.]+)", text)
    rt = float(m.group(1)) if m else c.rr
    th_c, Yc, Xc = positions(c, text, step_deg=step_deg)
    tc = np.radians(np.arange(0, 360, d_theta))
    zs = np.arange(-c.length / 2, c.length / 2 + 1e-9, dz)
    R = c.x2
    top = np.full((len(tc), len(zs)), R)
    nt, dt = len(tc), tc[1] - tc[0]
    reach = max(c.rr, c.k * c.x2) + 1.0
    half = math.asin(min(1.0, (reach + abs(c.arm * 0.5)) / c.core)) + 2 * dt if c.follower == "oscillating" else \
        math.asin(min(1.0, reach / c.core)) + 2 * dt
    # a cut counts once it opens to the outside; with the cutter axis off the cam axis (oscillating follower) a cut
    # can come before the one that opens the column above it, so the sweep is repeated until nothing changes
    for _sweep in range(4):
        before = top.copy()
        for j in range(len(th_c)):
            th, Y, X = th_c[j], Yc[j], Xc[j]
            pol = -c.sigma * th  # the cutter's axis direction (x̂) seen in the cam frame
            k0, k1 = int(math.floor((pol - half) / dt)), int(math.ceil((pol + half) / dt))
            ks = np.mod(np.arange(k0, k1 + 1), nt)
            zsel = np.flatnonzero(np.abs(zs - X) <= reach + dz)
            if not len(zsel):
                continue
            beta = tc[ks][:, None] + c.sigma * th  # the ray's direction in the fixed frame
            cb, sb = np.cos(beta), np.sin(beta)
            dzz = zs[zsel][None, :] - X
            if c.roller == "cone":
                a2 = sb * sb - c.k * c.k * cb * cb
                a1 = -2 * sb * Y
                a0 = Y * Y + dzz * dzz
            else:
                a2 = sb * sb + 0 * dzz
                a1 = -2 * sb * Y + 0 * dzz
                a0 = Y * Y + dzz * dzz - rt * rt
            disc = a1 * a1 - 4 * a2 * a0
            with np.errstate(divide="ignore", invalid="ignore"):
                sq = np.sqrt(np.maximum(disc, 0))
                ra, rb = (-a1 - sq) / (2 * a2), (-a1 + sq) / (2 * a2)
            lo_r, hi_r = np.minimum(ra, rb), np.maximum(ra, rb)
            # inside the cutter where a2 r² + a1 r + a0 < 0: between the roots (a2 > 0), beyond them (a2 < 0)
            small = np.abs(a2) < 1e-12
            lo = np.where(a2 > 0, lo_r, hi_r)
            hi = np.where(a2 > 0, hi_r, np.inf)
            lo = np.where(small, np.where(a0 < 0, 0.0, np.inf), lo)
            hi = np.where(small, np.where(a0 < 0, np.inf, -np.inf), hi)
            lo = np.where((disc < 0) & (a2 < 0), 0.0, lo)  # always inside (cone, ray near its axis)
            hi = np.where((disc < 0) & (a2 > 0), -np.inf, hi)
            # the cutter's end at the groove bottom: r cos β ≥ core
            with np.errstate(divide="ignore", invalid="ignore"):
                r_end = np.where(cb > 1e-9, c.core / cb, np.inf)
            lo = np.maximum(lo, r_end)
            cur = top[np.ix_(ks, zsel)]
            cut = (hi > lo) & (hi >= cur - 1e-9)  # opens to the outside of the material
            top[np.ix_(ks, zsel)] = np.where(cut, np.minimum(cur, np.maximum(lo, 0.0)), cur)
        if np.array_equal(before, top):
            break
    return np.degrees(tc), zs, top


def manufacture(project: dict) -> dict:
    """The program, its simulation and the checks for a cylindrical cam project ({"mfg": {"tool_r", "chord_tol",
    "work_rpm", "prog_no"}} with the usual fields)."""
    prog = Program.from_dict(project.get("program") or {})
    c = C.cyl(project.get("cylindrical"), prog.unit)
    st = settings(c, (project.get("mfg") or {}).get("four") or {})
    title = (project.get("title") or {}).get("en") or ""
    text = program(c, prog, st, title)
    sim = simulate(c, prog, text, st["tool_r"])
    tol = st["chord_tol"]
    over_um, under_um = -sim["max_over"] * 1000, sim["max_under"] * 1000
    checks = [
        {"id": "overcut", "zh": "不过切（仿真）", "en": "No overcut (simulation)", "value": round(max(over_um, 0), 3),
         "limit": round(tol * 1000, 3), "unit": "µm", "status": "pass" if over_um <= tol * 1000 + 0.5 else "fail",
         "note": "", "note_zh": ""},
        {"id": "left", "zh": "残留（仿真，槽侧面法向）", "en": "Material left (simulation, along the flank normal)",
         "value": round(max(under_um, 0), 3), "limit": None, "unit": "µm", "status": "info",
         "note": "" if abs(st["tool_r"] - c.rr) < 1e-9 else "a smaller cutter leaves material where the flank turns",
         "note_zh": "" if abs(st["tool_r"] - c.rr) < 1e-9 else "小刀在槽侧面转弯处会留下余量"},
        {"id": "reached", "zh": "槽侧面各点都被刀具走到", "en": "Every flank point reached by the cutter",
         "value": sim["unreached"], "limit": 0, "unit": "", "status": "pass" if sim["unreached"] == 0 else "fail",
         "note": "", "note_zh": ""},
    ]
    step = 2
    return {"program": text, "lines": text.count("\n"), "settings": st, "checks": checks,
            "sim": {"deg": sim["flanks"][0]["deg"][::step].round(2).tolist(),
                    "flanks": [{"side": f["side"],
                                "dev_um": (np.nanmax(f["dev"], axis=1)[::step] * 1000).round(3).tolist(),
                                "dev_min_um": (np.nanmin(f["dev"], axis=1)[::step] * 1000).round(3).tolist()}
                               for f in sim["flanks"]],
                    "over_um": round(over_um, 3), "under_um": round(under_um, 3)}}


def model_stl(project: dict, fine: bool = True) -> bytes:
    """The cam as machined, as STL: the blank minus the groove ring the cutter sweeps (camkit.cyl_solid, the same faces
    as the exact solid). Not the height field above: with an oscillating follower the cutter axis is off the cam axis
    and the groove walls overhang, which a height field cannot hold."""
    from camkit import cyl_solid as CS

    prog = Program.from_dict(project.get("program") or {})
    c = C.cyl(project.get("cylindrical"), prog.unit)
    settings(c, (project.get("mfg") or {}).get("four") or {})
    V, F, _ = CS.mesh_part(c, prog, segments=720 if fine else 360)
    return stl(V, F, "cylindrical")
