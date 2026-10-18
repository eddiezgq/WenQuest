"""Manufacturing of disk and groove cams (round 39, step 3): tool paths, programs, exports and program simulation.

- Tool centre path: the machined surface offset along its normal by the tool radius, on the side the tool works from
  (outside an external cam; inside the groove for both flanks of a groove cam).
- Gouging: where the surface is concave towards the tool, its radius of curvature must exceed the tool radius.
- Points by chord tolerance: greedy on a dense path, measuring the deviation the machine's own interpolation would make
  (X and C linear for a cam grinder, straight lines for a machining centre).
- Programs in FANUC style. Machine settings are configuration (defaults are examples, to be set to the shop's machine).
- Simulation reads the program text back (not the data that made it), sweeps the tool through the blank and compares
  the material left with the design surface, degree by degree.

Plain code: no AI, no network. Lengths mm, angles degrees at the edge.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

import numpy as np
from scipy.spatial import cKDTree

from camkit import disk as D
from camkit.analyze import _num, mechanism
from camkit.program import Program

PASS, FAIL, UNKNOWN, NA, INFO = "pass", "fail", "unknown", "na", "info"
DENSE = 14400  # cam angles for the dense design curves (0.025°)
SIM_RAYS = 3600  # simulation: one ray per 0.1°

# Example machine and process settings: configuration, not data about any real machine. The web app shows them as
# "example, set to your machine".
DEFAULTS = {
    "process": "grind",
    "chord_tol": 0.001,
    "grind": {"x_mode": "radius", "work_rpm": 10.0, "allowances": [0.05, 0.02, 0.0], "sparkout": 1, "prog_no": 3901,
              "clear": 2.0, "decimals": 4},
    "mill": {"spindle_rpm": 3000.0, "feed": 300.0, "plunge_feed": 60.0, "step_down": 2.0, "safe_z": 5.0, "clear": 2.0,
             "climb": True, "prog_no": 3902, "decimals": 4},
}


class MfgError(ValueError):
    pass


def settings(d: dict | None) -> dict:
    d = dict(d or {})
    out = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAULTS.items()}
    for k, v in d.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = out[k] | {kk: vv for kk, vv in v.items() if vv not in (None, "")}
        elif v not in (None, ""):
            out[k] = v
    if out["process"] not in ("grind", "mill", "wire"):
        raise MfgError("the process is grinding, milling or wire EDM")
    out["tool_r"] = _num(d.get("tool_r"))
    out["chord_tol"] = float(out["chord_tol"])
    if not 1e-5 <= out["chord_tol"] <= 0.1:
        raise MfgError("the chord tolerance is between 0.00001 and 0.1 mm")
    if out["process"] != "wire" and not (out["tool_r"] and out["tool_r"] > 0):
        raise MfgError("give the tool radius (grinding wheel or end mill)")
    return out


# --------------------------------------------------------------------------------------------- design surfaces


@dataclass
class Surface:
    name: str  # "profile" (external cam or the inner flank of a groove) or "outer" (outer flank of a groove)
    zh: str
    P: np.ndarray  # (2, N) closed, counter-clockwise, from cam angle 0 at index 0 (as the design is sampled)
    n: np.ndarray  # outward normal of the closed curve
    side: int  # +1 tool on the outward side, -1 inside
    kappa: np.ndarray  # signed curvature (counter-clockwise: convex > 0)

    @property
    def wall(self) -> np.ndarray:
        """Normal pointing out of the material, towards the tool."""
        return self.side * self.n


def _closed_geometry(P: np.ndarray):
    """Orient counter-clockwise; outward normal and signed curvature by periodic differences on the cam angle."""
    area = 0.5 * np.sum(P[0] * np.roll(P[1], -1) - np.roll(P[0], -1) * P[1])
    flipped = area < 0
    if flipped:
        P = P[:, ::-1]
    h = 2 * math.pi / P.shape[1]
    P1 = (np.roll(P, -1, axis=1) - np.roll(P, 1, axis=1)) / (2 * h)
    P2 = (np.roll(P, -1, axis=1) - 2 * P + np.roll(P, 1, axis=1)) / h**2
    sp = np.hypot(P1[0], P1[1])
    if np.any(sp < 1e-9):
        raise MfgError("the cam outline has a point that does not move (a sharp corner)")
    T = P1 / sp
    n = np.stack([T[1], -T[0]])  # right of the direction of travel = outward for a counter-clockwise curve
    kappa = (P1[0] * P2[1] - P1[1] * P2[0]) / sp**3
    return P, n, kappa, flipped


def design(project: dict, prog: Program | None = None, n: int = DENSE):
    """Dense design surfaces of the project (prog overrides the project's program, used for compensation)."""
    m = mechanism(project.get("mechanism"))
    prog = prog or Program.from_dict(project.get("program") or {})
    geo = D.analyse(m, prog, n)
    out = []
    P, nn, k, flipped = _closed_geometry(np.asarray(geo["profile"]))
    out.append(Surface("profile", "内侧壁" if m.groove else "廓线", P, nn, +1, k))
    if m.groove:
        P, nn, k, _ = _closed_geometry(np.asarray(geo["outer"]))
        out.append(Surface("outer", "外侧壁", P, nn, -1, k))
    return m, geo, out, flipped


# --------------------------------------------------------------------------------------------- tool paths


def _gouge(sf: Surface, R: float) -> dict:
    risky = sf.side * sf.kappa < 0  # curvature centre on the tool's side
    if not np.any(risky):
        return {"min_concave": None, "deg": None, "ok": True}
    rad = np.where(risky, 1 / np.maximum(np.abs(sf.kappa), 1e-15), np.inf)
    i = int(np.argmin(rad))
    return {"min_concave": float(rad[i]), "deg": _deg_at(sf, i), "ok": bool(rad[i] > R)}


def _deg_at(sf: Surface, i: int) -> float:
    """Polar angle of point i of a surface, degrees in [0, 360)."""
    return float(np.degrees(np.arctan2(sf.P[1, i], sf.P[0, i])) % 360)


def tool_centre(sf: Surface, R: float) -> np.ndarray:
    return sf.P + sf.side * R * sf.n


def _select_xy(Q: np.ndarray, tol: float) -> np.ndarray:
    """Indices of a closed dense polyline so that each chord stays within tol of the points it skips."""
    N = Q.shape[1]
    QQ = np.concatenate([Q, Q[:, :1]], axis=1)

    def dev(i, j):
        a, b = QQ[:, i], QQ[:, j]
        seg = b - a
        L2 = float(seg @ seg)
        pts = QQ[:, i + 1: j] - a[:, None]
        if pts.shape[1] == 0:
            return 0.0
        if L2 == 0:
            return float(np.max(np.hypot(pts[0], pts[1])))
        t = np.clip((seg @ pts) / L2, 0, 1)
        d = pts - np.outer(seg, t)
        return float(np.max(np.hypot(d[0], d[1])))

    return _greedy(N, dev, tol)


def _greedy(N: int, dev, tol: float) -> np.ndarray:
    idx, i = [0], 0
    while i < N:
        step = 1
        while i + step * 2 <= N and dev(i, i + step * 2) <= tol:
            step *= 2
        lo, hi = i + step, min(N, i + step * 2)  # lo is known good (or i+1)
        if dev(i, lo) > tol:
            lo = i + 1
            hi = i + 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if dev(i, mid) <= tol:
                lo = mid
            else:
                hi = mid
        if hi <= N and hi > lo and dev(i, hi) <= tol:
            lo = hi
        i = lo
        idx.append(i)
    return np.array(idx[:-1] if idx[-1] == N else idx)


def xc_path(Q: np.ndarray, tol: float):
    """Polar (X, C) program points for a cam grinder: the wheel centre on the +X axis, the cam turned by C.
    Returns (X, C) with C rising from 0 to 360 (last point closes the turn) or raises if X–C cannot follow the path."""
    alpha = np.arctan2(Q[1], Q[0])
    C = np.unwrap(-alpha[::-1])  # traverse clockwise so that C rises
    X = np.hypot(Q[0], Q[1])[::-1]
    if not np.all(np.diff(C) > 0):
        raise MfgError("the tool centre path is not star-shaped about the cam centre: X–C grinding cannot follow it; "
                       "use milling")
    C = np.degrees(C)
    # start at C = 0: rotate the arrays and insert the interpolated point at 0
    C = np.mod(C - 0.0, 360.0)
    k = int(np.argmin(C))
    C, X = np.roll(C, -k), np.roll(X, -k)
    C = np.concatenate([C, C[:1] + 360])
    X = np.concatenate([X, X[:1]])
    if C[0] > 0:  # interpolate the point at C = 0 (= 360) from the last and first samples
        c_prev, x_prev = C[-2] - 360, X[-2]
        x0 = x_prev + (X[0] - x_prev) * (0 - c_prev) / (C[0] - c_prev)
        C = np.concatenate([[0.0], C[:-1], [360.0]])
        X = np.concatenate([[x0], X[:-1], [x0]])
    N = len(C) - 1

    def dev(i, j):
        if j - i < 2:
            return 0.0
        c, x = C[i: j + 1], X[i: j + 1]
        lin = x[0] + (x[-1] - x[0]) * (c - c[0]) / (c[-1] - c[0])
        return float(np.max(np.abs(x - lin)))

    sel = _greedy(N, dev, tol)
    sel = np.concatenate([sel, [N]])
    return X[sel], C[sel]


# --------------------------------------------------------------------------------------------- programs


def _f(v: float, d: int) -> str:
    s = f"{v:.{d}f}"
    if s.startswith("-0.") and float(s) == 0:
        s = s[1:]
    return s


def grind_program(paths: list[tuple[str, np.ndarray, np.ndarray, int]], st: dict, title: str, groove: bool = False,
                  single: bool = False) -> str:
    """paths: (flank, X, C, sign) with sign +1 when stock lies at larger X (external cam, inner flank of a groove)."""
    g, R, d = st["grind"], st["tool_r"], int(st["grind"]["decimals"])
    dia = g["x_mode"] == "diameter"
    k = 2.0 if dia else 1.0
    rpm_c = float(g["work_rpm"])
    allow = [float(a) for a in g["allowances"]] or [0.0]
    if allow[-1] != 0:
        allow.append(0.0)
    if single:  # a tool as wide as the groove finishes both flanks at once: no stock can be left on one side only
        allow = [0.0]
    x_max = max(float(np.max(X)) for _, X, _, _ in paths)
    safe = x_max + max(allow) + float(g["clear"])
    out = ["%", f"O{int(g['prog_no']):04d} (WENQUEST CAM X-C GRIND)", f"({_ascii(title)})",
           f"(WHEEL RADIUS {R:.4f} MM - X IS THE WHEEL CENTRE)", f"(XMODE {'DIAMETER' if dia else 'RADIUS'})",
           f"(CHORD TOL {st['chord_tol']:.5f} MM - CAMKIT)",
           "(C: CAM TURN, DEGREES; G92 C0 RESETS C AFTER EACH TURN)",
           f"(WORK SPEED {rpm_c:g} R/MIN, G93 INVERSE TIME FEED)",
           "(EXAMPLE SETTINGS - SET TO YOUR MACHINE)",
           "G21 G90 G40", f"G00 X{_f(safe * k, d)} C0.", "G92 C0."]
    if groove:
        out.append("(GROOVE: THE WHEEL ENTERS THE ROUGHED GROOVE AXIALLY BEFORE THIS PROGRAM - SHOP PRACTICE)")
    for name, X, C, sign in paths:
        out.append(f"(FLANK {name.upper()}, {len(X) - 1} POINTS PER TURN)")
        passes = list(allow) + [0.0] * int(g["sparkout"])
        for p, a0 in enumerate(passes):
            a = sign * a0
            label = "SPARK-OUT" if p >= len(allow) else f"ALLOWANCE {a0:.4f}"
            out.append(f"(PASS {p + 1}: {label})")
            out.append("G94")
            if groove:
                out.append(f"G00 X{_f((X[0] + a) * k, d)} C0.")
            else:
                out.append(f"G00 X{_f((X[0] + a + float(g['clear'])) * k, d)} C0.")
                out.append(f"G01 X{_f((X[0] + a) * k, d)} F50.")
            out.append("G93")
            for i in range(1, len(X)):
                dt = (C[i] - C[i - 1]) / (360.0 * rpm_c)  # minutes
                out.append(f"G01 X{_f((X[i] + a) * k, d)} C{_f(C[i], d)} F{_f(1 / dt, 2)}")
            out.append("G94")
            out.append("G92 C0.")
        out.append(f"G00 X{_f(safe * k, d)}")
    out += ["M30", "%"]
    return "\n".join(out) + "\n"


def mill_program(paths: list[tuple[str, np.ndarray, int, np.ndarray]], st: dict, title: str, depth: float,
                 groove: bool) -> str:
    g, R, d = st["mill"], st["tool_r"], int(st["mill"]["decimals"])
    step = float(g["step_down"])
    if not step > 0:
        raise MfgError("the depth per pass is more than 0")
    levels = [-min(depth, step * (i + 1)) for i in range(math.ceil(depth / step - 1e-9))]
    out = ["%", f"O{int(g['prog_no']):04d} (WENQUEST CAM XY MILL)", f"({_ascii(title)})",
           f"(END MILL RADIUS {R:.4f} MM - PROGRAMMED AT THE TOOL CENTRE, NO G41/G42)",
           f"(CHORD TOL {st['chord_tol']:.5f} MM - CAMKIT)", "(CAM CENTRE = X0 Y0, TOP FACE = Z0)",
           "(EXAMPLE SETTINGS - SET TO YOUR MACHINE)",
           "G17 G21 G90 G40 G49 G80 G94", "G54", f"S{int(float(g['spindle_rpm']))} M03",
           f"G00 Z{_f(float(g['safe_z']), d)}"]
    for name, Q, side, nrm in paths:
        out.append(f"(FLANK {name.upper()}, {Q.shape[1]} POINTS)")
        x0, y0 = Q[0, 0], Q[1, 0]
        ax, ay = x0 + side * float(g["clear"]) * nrm[0], y0 + side * float(g["clear"]) * nrm[1]
        for z in levels:
            if groove:
                out.append("(PLUNGE INSIDE THE GROOVE: PRE-DRILLED HOLE OR HELICAL RAMP PER SHOP PRACTICE)")
                out.append(f"G00 X{_f(x0, d)} Y{_f(y0, d)}")
                out.append(f"G01 Z{_f(z, d)} F{_f(float(g['plunge_feed']), 1)}")
            else:
                out.append(f"G00 X{_f(ax, d)} Y{_f(ay, d)}")
                out.append(f"G01 Z{_f(z, d)} F{_f(float(g['plunge_feed']), 1)}")
                out.append(f"G01 X{_f(x0, d)} Y{_f(y0, d)} F{_f(float(g['feed']), 1)}")
            first = True
            for i in list(range(1, Q.shape[1])) + [0]:
                f = f" F{_f(float(g['feed']), 1)}" if first and groove else ""
                out.append(f"G01 X{_f(Q[0, i], d)} Y{_f(Q[1, i], d)}{f}")
                first = False
            if not groove:
                out.append(f"G01 X{_f(ax, d)} Y{_f(ay, d)}")
            out.append(f"G00 Z{_f(float(g['safe_z']), d)}")
    out += ["M05", "M30", "%"]
    return "\n".join(out) + "\n"


def _ascii(s: str) -> str:
    """Program comments in ASCII (controllers differ on other characters)."""
    t = re.sub(r"[^A-Za-z0-9 .,:+=/-]", "", s or "").strip().upper()
    return t[:60] or "CAM"


# --------------------------------------------------------------------------------------------- exports


def dxf(surfaces: list[Surface], tol: float) -> str:
    """AutoCAD R12 DXF: one closed polyline per surface, points by chord tolerance."""
    out = ["0", "SECTION", "2", "ENTITIES"]
    for sf in surfaces:
        sel = _select_xy(sf.P, tol)
        out += ["0", "POLYLINE", "8", sf.name.upper(), "66", "1", "10", "0.0", "20", "0.0", "30", "0.0", "70", "1"]
        for i in sel:
            out += ["0", "VERTEX", "8", sf.name.upper(), "10", f"{sf.P[0, i]:.6f}", "20", f"{sf.P[1, i]:.6f}", "30",
                    "0.0"]
        out += ["0", "SEQEND", "8", sf.name.upper()]
    out += ["0", "ENDSEC", "0", "EOF"]
    return "\n".join(out) + "\n"


def point_table(project: dict, step_deg: float = 0.5) -> str:
    """CSV by cam angle: lift and the contact points of each flank (cam frame)."""
    m = mechanism(project.get("mechanism"))
    prog = Program.from_dict(project.get("program") or {})
    n = int(round(360 / step_deg))
    if n < 8 or abs(n * step_deg - 360) > 1e-9:
        raise MfgError("the table step divides 360°")
    geo = D.analyse(m, prog, n)
    lift = geo["s"] if prog.unit == "mm" else np.degrees(geo["s"])
    head = ["cam_deg", "lift_" + ("mm" if prog.unit == "mm" else "deg"), "profile_x", "profile_y", "profile_r"]
    cols = [np.degrees(geo["theta"]), lift, geo["profile"][0], geo["profile"][1], np.hypot(*geo["profile"])]
    if geo["outer"] is not None:
        head += ["outer_x", "outer_y", "outer_r"]
        cols += [geo["outer"][0], geo["outer"][1], np.hypot(*geo["outer"])]
    lines = [",".join(head)]
    for row in zip(*cols, strict=True):
        lines.append(",".join(f"{v:.6f}" for v in row))
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------------------------- simulation


def parse_program(text: str) -> dict:
    """Read a program back: X–C (grinder) or XY (machining centre) cutting moves. Only what we write is understood:
    G00/G01, G90 absolute, G92 C (C reset), X in radius or diameter (from the XMODE comment)."""
    dia = "(XMODE DIAMETER)" in text
    mode = "xc" if "X-C GRIND" in text else "xy"
    pos = {"X": None, "Y": None, "Z": 0.0, "C": 0.0}
    c_off = 0.0
    motion = "G00"
    moves = []  # list of polylines (each a run of consecutive G01 cutting moves)
    run = []
    for raw in text.splitlines():
        line = re.sub(r"\(.*?\)", "", raw).strip().upper()
        if not line or line in ("%", "M30", "M05") or line.startswith("O"):
            continue
        words = dict(re.findall(r"([A-Z])([-+]?\d*\.?\d+)", line))
        gs = re.findall(r"G(\d+)", line)
        if "92" in gs:  # G92 C0: current C becomes 0
            if "C" in words:
                c_off += pos["C"] - float(words["C"])
                pos["C"] = float(words["C"])
            continue
        for gg in gs:
            if gg in ("0", "00"):
                motion = "G00"
            elif gg in ("1", "01"):
                motion = "G01"
        new = dict(pos)
        for ax in ("X", "Y", "Z", "C"):
            if ax in words and not (ax == "C" and "92" in gs):
                v = float(words[ax])
                new[ax] = v / 2 if (ax == "X" and dia) else v
        if motion == "G01" and new != pos and _cutting(mode, new):
            if not run:
                run.append(_pt(mode, pos, c_off))
            run.append(_pt(mode, new, c_off))
        elif run:
            moves.append(np.array(run))
            run = []
        pos = new
    if run:
        moves.append(np.array(run))
    return {"mode": mode, "runs": moves}


def _cutting(mode, p):
    return p["X"] is not None and (mode == "xc" or (p["Y"] is not None and p["Z"] < 0))


def _pt(mode, p, c_off):
    if mode == "xc":
        return (p["X"], p["C"] + c_off, 0.0)
    return (p["X"], p["Y"], p["Z"])


def tool_positions(parsed: dict, R: float = 1.0) -> np.ndarray:
    """Tool centres in the cam frame along every cutting move, finely subdivided as the machine interpolates."""
    pts = []
    step = math.sqrt(8 * R * 2e-6)  # spacing of the tool positions: scallop between two of them s²/(8R) ≤ 2e-6 mm
    xy = parsed["mode"] == "xy"
    zmin = min(r[:, 2].min() for r in parsed["runs"]) if (xy and parsed["runs"]) else 0.0
    for run in parsed["runs"]:
        for a, b in zip(run[:-1], run[1:], strict=True):
            if not xy:
                arc = abs(b[1] - a[1]) * math.pi / 180 * max(a[0], b[0]) + abs(b[0] - a[0])
                n = max(1, int(math.ceil(arc / step)))
                t = np.linspace(0, 1, n, endpoint=False)
                X = a[0] + (b[0] - a[0]) * t
                C = np.radians(a[1] + (b[1] - a[1]) * t)
                pts.append(np.stack([X * np.cos(C), -X * np.sin(C)]))
            else:
                if a[2] > zmin + 1e-9 or b[2] > zmin + 1e-9:
                    continue  # only the full-depth passes shape the finished flank
                L = math.hypot(b[0] - a[0], b[1] - a[1])
                n = max(1, int(math.ceil(L / step)))
                t = np.linspace(0, 1, n, endpoint=False)
                pts.append(np.stack([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]))
    if not pts:
        raise MfgError("the program has no cutting moves")
    return np.concatenate(pts, axis=1)


def sweep(Qs: np.ndarray, R: float, rays: int = SIM_RAYS, chunk: int = 1024, ray_chunk: int = 60):
    """Along each ray from the cam centre: the nearest and farthest points the tool reaches (inf / -inf: none).
    Tool positions are sorted by polar angle and swept in blocks; a block is tried only on the rays its circles can
    reach (polar angle ± asin(R/|q|)), which keeps a small end mill as cheap as a large wheel."""
    phi = np.linspace(0, 2 * math.pi, rays, endpoint=False)
    u = np.stack([np.cos(phi), np.sin(phi)])
    near = np.full(rays, np.inf)
    far = np.full(rays, -np.inf)
    Qs = np.unique(np.round(Qs, 7), axis=1)  # a spark-out turn repeats the last one
    r = np.hypot(Qs[0], Qs[1])
    ang = np.mod(np.arctan2(Qs[1], Qs[0]), 2 * math.pi)
    half = np.where(R < r, np.arcsin(np.minimum(1.0, R / np.maximum(r, 1e-12))), math.pi)
    order = np.argsort(ang)
    Qs, ang, half = Qs[:, order], ang[order], half[order]
    dphi = 2 * math.pi / rays
    for k in range(0, Qs.shape[1], chunk):
        q, a, h = Qs[:, k: k + chunk], ang[k: k + chunk], half[k: k + chunk]
        hw = float(h.max())
        if hw >= math.pi - 1e-9:
            idx = np.arange(rays)
        else:
            lo, hi = float(a.min()) - hw, float(a.max()) + hw
            i0, i1 = int(math.floor(lo / dphi)) - 1, int(math.ceil(hi / dphi)) + 1
            idx = np.mod(np.arange(i0, i1 + 1), rays)
            idx = np.unique(idx)
        for j in range(0, len(idx), ray_chunk):
            rj = idx[j: j + ray_chunk]
            uu = u[:, rj]
            uq = uu.T @ q
            d2 = (q[0] ** 2 + q[1] ** 2)[None, :] - uq**2
            disc = R * R - d2
            ok = (disc >= 0) & (uq > 0)
            if not ok.any():
                continue
            sq = np.sqrt(np.where(ok, disc, 0.0))
            near[rj] = np.minimum(near[rj], np.where(ok, uq - sq, np.inf).min(axis=1))
            far[rj] = np.maximum(far[rj], np.where(ok, uq + sq, -np.inf).max(axis=1))
    return phi, u, near, far


def compare(sf: Surface, B: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Signed normal deviation of the machined boundary points B from a design surface: + material left (undercut),
    − material removed beyond the design (overcut); nan where the tool never reached."""
    tree = cKDTree(sf.P.T)
    out = np.full(B.shape[1], np.nan)
    if np.any(valid):
        _, j = tree.query(B[:, valid].T)
        diff = B[:, valid] - sf.P[:, j]
        out[valid] = np.sum(diff * sf.wall[:, j], axis=0)
    return out


def simulate(text: str, surfaces: list[Surface], R: float, groove: bool) -> dict:
    parsed = parse_program(text)
    Qs = tool_positions(parsed, R)
    phi, u, near, far = sweep(Qs, R)
    res = {"deg": np.degrees(phi), "flanks": []}
    for sf in surfaces:
        if sf.name == "profile":
            t = near
        else:
            t = far
        valid = np.isfinite(t) & (t > 0)
        B = u * np.where(valid, t, 0.0)
        dev = compare(sf, B, valid)
        res["flanks"].append({"name": sf.name, "dev": dev, "boundary": B, "valid": valid})
    del groove
    return res


# --------------------------------------------------------------------------------------------- one call


def manufacture(project: dict, mfg: dict | None = None, prog: Program | None = None, sim_R: float | None = None):
    """Tool paths, program, checks and simulation for a project. prog: a corrected program (compensation);
    sim_R: simulate with another tool radius (a dressed wheel whose radius was not updated)."""
    st = settings(mfg)
    m, geo, surfaces, _ = design(project, prog)
    R = st["tool_r"]
    title = (project.get("title") or {}).get("en") or (project.get("title") or {}).get("zh") or ""
    checks = []
    if st["process"] == "wire":
        return {"settings": st, "surfaces": surfaces, "checks": [], "program": None, "mechanism": m, "geo": geo,
                "paths": [], "sim": None}
    if m.groove and R > m.rr + 1e-9:
        raise MfgError("the tool is wider than the groove: its radius must not exceed the roller radius")
    gouges = []
    for sf in surfaces:
        gg = _gouge(sf, R)
        gouges.append(gg)
    worst = min((g for g in gouges if g["min_concave"] is not None), key=lambda g: g["min_concave"], default=None)
    checks.append(_ck("gouge", "不过切（凹处曲率半径大于刀具半径）", "No gouging (concave radius > tool radius)",
                      None if worst is None else worst["min_concave"], R,
                      PASS if all(g["ok"] for g in gouges) else FAIL, "mm",
                      "" if worst is None else f"at {worst['deg']:.1f}°", deg=None if worst is None else worst["deg"]))
    tol = st["chord_tol"]
    single = m.groove and abs(R - m.rr) < 1e-9
    use = surfaces[:1] if single else surfaces
    paths, prog_paths = [], []
    for sf in use:
        Q = tool_centre(sf, R)
        if st["process"] == "grind":
            try:
                X, C = xc_path(Q, tol)
            except MfgError as err:
                checks.append(_ck("xc", "X–C 磨削能走（刀心轨迹对凸轮中心呈星形）", "X–C grinding can follow the path",
                                  None, None, FAIL, "", str(err)))
                return {"settings": st, "surfaces": surfaces, "checks": checks, "program": None, "mechanism": m,
                        "geo": geo, "paths": [], "sim": None, "over": None, "under": None}
            paths.append({"name": sf.name, "points": len(X) - 1, "xc": (X, C), "Q": Q})
            prog_paths.append((sf.name, X, C, 1 if sf.name == "profile" else -1))
        else:
            # climb milling with M03: outside a contour clockwise, inside counter-clockwise
            idx = _select_xy(Q, tol)
            Qp, nn = Q[:, idx], sf.n[:, idx]
            cw = (sf.side > 0) == bool(st["mill"]["climb"])
            if cw:
                Qp, nn = Qp[:, ::-1], nn[:, ::-1]
                Qp, nn = np.roll(Qp, 1, axis=1), np.roll(nn, 1, axis=1)
            paths.append({"name": sf.name, "points": Qp.shape[1], "Q": Q})
            prog_paths.append((sf.name, Qp, sf.side, nn[:, 0]))
    if st["process"] == "grind":
        text = grind_program(prog_paths, st, title, m.groove, single)
    else:
        depth = _num((mfg or {}).get("depth")) or m.width
        if not depth or depth <= 0:
            raise MfgError("give the milling depth (or the contact width)")
        text = mill_program(prog_paths, st, title, depth, m.groove)
    sim = simulate(text, surfaces, sim_R or R, m.groove)
    lim = tol + 1e-4
    worst_over, worst_under = _extremes(sim)
    sim_ok = all(np.all(np.isfinite(f["dev"])) for f in sim["flanks"])
    mx = max(abs(worst_over[0]), abs(worst_under[0]))
    checks.append(_ck("sim", "程序仿真偏差", "Program simulation deviation", mx, lim,
                      FAIL if not sim_ok else (PASS if mx <= lim else FAIL), "mm",
                      "" if sim_ok else "the tool does not reach part of the flank"))
    pts = sum(p["points"] for p in paths)
    checks.append(_ck("points", "程序点数", "Program points", pts, None, INFO, ""))
    if st["process"] == "grind":
        t_turn = 1 / float(st["grind"]["work_rpm"])
        checks.append(_ck("turn_time", "每圈磨削时间", "Grinding time per turn", t_turn * 60, None, INFO, "s"))
    return {"settings": st, "surfaces": surfaces, "checks": checks, "program": text, "mechanism": m, "geo": geo,
            "paths": paths, "sim": sim, "over": worst_over, "under": worst_under}


def _extremes(sim):
    over, under = (0.0, None, None), (0.0, None, None)
    for f in sim["flanks"]:
        d = f["dev"]
        if np.all(np.isnan(d)):
            continue
        i = int(np.nanargmin(d))
        if d[i] < over[0]:
            over = (float(d[i]), float(sim["deg"][i]), f["name"])
        i = int(np.nanargmax(d))
        if d[i] > under[0]:
            under = (float(d[i]), float(sim["deg"][i]), f["name"])
    return over, under


def _ck(cid, zh, en, value, limit, status, unit, note="", deg=None):
    zh_note = (note.replace("at ", "在 ").replace("the tool does not reach part of the flank", "刀具没有走到部分侧壁")
               .replace("the tool centre path is not star-shaped about the cam centre: X–C grinding cannot follow it; "
                        "use milling", "刀心轨迹对凸轮中心不是星形，X–C 磨削走不了，请改用铣削（或换小砂轮）"))
    return {"id": cid, "zh": zh, "en": en, "value": value, "limit": limit, "status": status, "unit": unit,
            "note": note, "note_zh": zh_note, "deg": deg}
