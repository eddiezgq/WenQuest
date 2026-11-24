"""A cam outline in, the follower motion out (第 179 轮): the inverse of camkit.disk.

The user has a drawn disk cam (CAD DXF, an XY point table, or a FreeCAD sketch) and the follower it drives, but no
motion law. For every 0.1° of cam angle the drawn outline is turned and the follower is put where it just touches it:

- translating knife / roller: the line x = e (fixed frame) meets the outline (knife) or the outline grown by the
  roller radius (roller: the boundary of the outline ⊕ a disc is the locus of a roller centre that touches without
  cutting in); the highest crossing is the follower;
- oscillating knife / roller: the same with the circle of radius L about the pivot O2 = (a, 0); the crossing with the
  largest swing ψ (farthest from the cam centre) is the follower;
- flat faces: the support function of the outline's convex hull (translating: the highest point; oscillating: the
  swing ψ where the face line through O2 just touches, by Newton's method).

Same frames and signs as camkit.disk: the cam turns by σθ about the origin O1; a point P of the cam frame is at
R(σθ)P in the fixed frame. The lowest position gives the base circle (rb is an output, not an input).

The lift s(θ) is exact to the outline's accuracy, but its second derivative magnifies the last hundredth of a
micrometre, so the acceleration is taken from a smoothing spline whose strength follows the outline's own accuracy
(generalised cross-validation). Both the unsmoothed and the smoothed acceleration are reported. The motion is
checked by making the outline again with camkit.disk and measuring
the distance between the two outlines.

Plain code: no AI, no network. DXF needs ezdxf (imported only when a DXF is read). Lengths mm, angles degrees at the
edge, radians inside.
"""

from __future__ import annotations

import io
import math
import re

import numpy as np
from scipy.interpolate import CubicSpline, make_smoothing_spline

from camkit import disk as D
from camkit.program import Program

N = 3600  # cam angles over a turn (0.1°)
STEP_OUT = 0.25  # the program table handed to the rest of the kernel, degrees
SPACING = 0.02  # densified outline, mm between points (sagitta ≈ c²/8R, far below a micrometre)
MAX_POINTS = 60000
TOL_CHECK = 0.005  # mm, outline made again vs the imported one


ERR_ZH = [  # the messages below in Chinese (patterns over the English text); the web service and FreeCAD use them
    (r"^importing an outline is for an external disk cam.*$", "导入廓线目前只做盘形凸轮外廓，槽凸轮以后再做"),
    (r"^reading DXF needs the Python package ezdxf", "读 DXF 需要 Python 包 ezdxf"),
    (r"^the DXF file cannot be read$", "读不了这个 DXF 文件"),
    (r"^the DXF has no lines, arcs or curves$", "DXF 里没有直线、圆弧或曲线"),
    (r"^the lines in the DXF do not close into an outline$", "DXF 里的线连不成一条封闭的廓线"),
    (r"^the outline is not closed: a gap of (.*) mm at \((.*)\)$", r"廓线没有封闭：在 (\2) 处断开 \1 mm"),
    (r"^the outline crosses itself$", "廓线自己和自己相交"),
    (r"^the centre of rotation is not inside the outline$", "回转中心不在廓线里面：请检查回转中心坐标"),
    (r"^the outline needs at least 12 points of x, y$", "廓线至少要 12 个点，每个点有 x、y"),
    (r"^the outline is a DXF file or a table of x, y points$", "廓线是 DXF 文件或 x、y 点表"),
    (r"^the outline is a circle about the centre", "廓线是绕回转中心的圆：从动件不动"),
    (r"^the smoothing is between 0 and 1000$", "平滑程度在 0 到 1000 之间"),
    (r"^the follower line misses the outline", "从动件导路碰不到廓线：偏距太大"),
    (r"^the follower would pass the cam centre", "从动件会越过凸轮中心：请检查偏距和回转中心"),
    (r"^the arm's circle misses the outline", "摆杆转不到廓线上：请检查中心距和摆杆长度"),
    (r"^the flat face cannot clear the cam", "平底摆杆让不开凸轮：中心距比凸轮最大半径还短"),
    (r"^the flat face does not settle on the outline", "平底找不到贴住廓线的位置：请检查中心距"),
    (r"^the follower is translating or oscillating$", "从动件是直动或摆动"),
    (r"^the cam turns counter-clockwise \(\+1\) or clockwise", "凸轮转向是逆时针（+1）或顺时针（−1）"),
    (r"^the contact is a roller, a flat face or a knife edge$", "接触形式是滚子、平底或尖顶"),
    (r"^give the roller radius$", "请填滚子半径"),
    (r"^an oscillating follower needs the centre distance$", "摆动从动件要填中心距"),
    (r"^an oscillating roller or knife follower needs the arm length$", "摆动滚子或尖顶从动件要填摆杆长度"),
    (r"^numbers must be finite$", "数值必须是有限数"),
]


def zh(msg: str) -> str:
    for pat, rep in ERR_ZH:
        if re.search(pat, msg):
            return re.sub(pat, rep, msg)
    return msg


class ImportError_(ValueError):  # noqa: N801  (not the builtin ImportError)
    pass


# --------------------------------------------------------------------------------------------- reading the outline


def read_xy(text: str) -> np.ndarray:
    """Columns x, y (comma, semicolon, tab or spaces), in the order of the outline; the last point need not repeat
    the first. With a header line naming the columns (x, y, or profile_x, profile_y as in this software's point
    table) those columns are used; otherwise the first two numbers of each line."""
    rows, ix, iy = [], 0, 1
    num = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"
    for line in (text or "").splitlines():
        body = line.split("#")[0].strip()
        if not body:
            continue
        if re.search(r"[A-DF-Za-df-z]", body):  # a header: find the x and y columns
            names = [w.strip().lower() for w in re.split(r"[,;\t ]+", body) if w.strip()]
            for cx, cy in (("profile_x", "profile_y"), ("x", "y"), ("x_mm", "y_mm")):
                if cx in names and cy in names:
                    ix, iy = names.index(cx), names.index(cy)
                    break
            continue
        nums = re.findall(num, body)
        if len(nums) > max(ix, iy):
            rows.append((float(nums[ix]), float(nums[iy])))
    if len(rows) < 12:
        raise ImportError_("the outline needs at least 12 points of x, y")
    P = np.array(rows).T
    if np.hypot(*(P[:, 0] - P[:, -1])) < 1e-9:
        P = P[:, :-1]
    return P


def _arc_pts(c, r, a0, a1, chord=SPACING):
    """Points on an arc from a0 to a1 (rad, counter-clockwise), ends included."""
    while a1 <= a0:
        a1 += 2 * math.pi
    n = max(2, int(math.ceil((a1 - a0) * r / chord)) + 1)
    t = np.linspace(a0, a1, n)
    return np.stack([c[0] + r * np.cos(t), c[1] + r * np.sin(t)])


def read_dxf(text: str) -> tuple[np.ndarray, dict]:
    """The outline from a DXF: lines, arcs, circles, polylines (with bulges), splines and ellipses joined end to end
    into closed loops; the loop with the largest area is the cam (a bore or a keyway inside is left out).
    A loop made only of straight pieces with many vertices is taken as points on a smooth curve (a CAD export of a
    curve); a loop with arcs or splines is kept exactly as drawn."""
    try:
        import ezdxf  # noqa: PLC0415
        from ezdxf import recover  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover - the service has it
        raise ImportError_("reading DXF needs the Python package ezdxf") from exc
    try:
        doc = ezdxf.read(io.StringIO(text))
    except Exception:  # noqa: BLE001 - a damaged file: try the recover reader on the bytes
        try:
            doc, _ = recover.read(io.BytesIO(text.encode("utf-8", "replace")))
        except Exception as exc:  # noqa: BLE001
            raise ImportError_("the DXF file cannot be read") from exc
    pieces, ignored, closed = [], {}, []  # pieces: (points 2×n, straight?)

    def add_entity(e):
        k = e.dxftype()
        if k == "LINE":
            a, b = e.dxf.start, e.dxf.end
            pieces.append((np.array([[a.x, b.x], [a.y, b.y]]), True))
        elif k == "ARC":
            c = e.dxf.center
            pieces.append((_arc_pts((c.x, c.y), e.dxf.radius, math.radians(e.dxf.start_angle),
                                    math.radians(e.dxf.end_angle)), False))
        elif k == "CIRCLE":
            c = e.dxf.center
            closed.append((_arc_pts((c.x, c.y), e.dxf.radius, 0.0, 2 * math.pi)[:, :-1], False))
        elif k in ("LWPOLYLINE", "POLYLINE"):
            if k == "POLYLINE" and not (e.is_2d_polyline or e.is_3d_polyline):
                ignored[k] = ignored.get(k, 0) + 1
                return
            parts = list(e.virtual_entities())
            if all(p.dxftype() == "LINE" for p in parts):
                pts = [(v.x, v.y) for v in e.points()] if k == "LWPOLYLINE" else \
                    [(v.dxf.location.x, v.dxf.location.y) for v in e.vertices]
                P = np.array(pts, dtype=float).T
                shut = e.closed if k == "LWPOLYLINE" else e.is_closed
                if shut or (P.shape[1] > 2 and np.hypot(*(P[:, 0] - P[:, -1])) < 1e-9):
                    if np.hypot(*(P[:, 0] - P[:, -1])) < 1e-9:
                        P = P[:, :-1]
                    closed.append((P, True))
                else:
                    pieces.append((P, True))
            else:
                for p in parts:
                    add_entity(p)
        elif k in ("SPLINE", "ELLIPSE"):
            pts = np.array([(v.x, v.y) for v in e.flattening(1e-4)], dtype=float).T
            if pts.shape[1] > 2 and np.hypot(*(pts[:, 0] - pts[:, -1])) < 1e-9:
                closed.append((pts[:, :-1], False))
            else:
                pieces.append((pts, False))
        elif k == "INSERT":
            for p in e.virtual_entities():
                add_entity(p)
        else:
            ignored[k] = ignored.get(k, 0) + 1

    for e in doc.modelspace():
        add_entity(e)
    if not pieces and not closed:
        raise ImportError_("the DXF has no lines, arcs or curves")
    size = max(float(np.ptp(np.concatenate([p[0] for p in pieces + closed], axis=1), axis=1).max()), 1.0)
    chained, opens = _chain(pieces, 1e-4 * size)
    loops = closed + chained
    # chains that do not close: straight lines on their own are centre lines and marks (left out); a chain with
    # curves in it is an outline with a gap
    broken = [o for o in opens if not o[1] or o[0].shape[1] > 3]
    if broken:
        P, _, gap = max(broken, key=lambda o: o[0].shape[1])
        raise ImportError_(f"the outline is not closed: a gap of {gap:.4g} mm at ({P[0, -1]:.3f}, {P[1, -1]:.3f})")
    if not loops:
        raise ImportError_("the lines in the DXF do not close into an outline")
    if opens:
        ignored["open lines"] = len(opens)
    areas = [abs(_area(P)) for P, _ in loops]
    k = int(np.argmax(areas))
    P, straight = loops[k]
    info = {"pieces": len(pieces) + len(closed), "loops": len(loops), "ignored": ignored,
            "straight": bool(straight)}
    return P, info


def _chain(pieces, tol):
    """Join open pieces end to end into closed loops (either direction). Returns the loops [(points, all straight?)]
    and the chains that do not close [(points, all straight?, gap)]."""
    left = list(pieces)
    loops, opens = [], []
    while left:
        P, straight = left.pop(0)
        P = P.copy()
        grew = True
        while grew and np.hypot(*(P[:, 0] - P[:, -1])) > tol:
            grew = False
            for i, (Q, st) in enumerate(left):
                if np.hypot(*(P[:, -1] - Q[:, 0])) <= tol:
                    P = np.concatenate([P, Q[:, 1:]], axis=1)
                elif np.hypot(*(P[:, -1] - Q[:, -1])) <= tol:
                    P = np.concatenate([P, Q[:, ::-1][:, 1:]], axis=1)
                else:
                    continue
                straight = straight and st
                left.pop(i)
                grew = True
                break
        gap = float(np.hypot(*(P[:, 0] - P[:, -1])))
        if gap <= tol and P.shape[1] > 3:
            loops.append((P[:, :-1], straight))
        else:
            opens.append((P, straight, gap))
    return loops, opens


def _area(P):
    x, y = P
    return 0.5 * float(np.sum(x * np.roll(y, -1) - np.roll(x, -1) * y))


def densify(P: np.ndarray, smooth: bool) -> np.ndarray:
    """The closed outline at about SPACING mm, counter-clockwise. smooth: a periodic spline through the points
    (points on a curve); otherwise straight between them (lines and finely sampled arcs as drawn)."""
    if _area(P) < 0:
        P = P[:, ::-1]
    d = np.hypot(*np.diff(np.concatenate([P, P[:, :1]], axis=1), axis=1))
    keep = d > 1e-9
    P, d = P[:, keep], d[keep]
    L = float(d.sum())
    n = int(min(MAX_POINTS, max(2000, math.ceil(L / SPACING))))
    u = np.concatenate([[0.0], np.cumsum(d)])
    t = np.linspace(0, L, n, endpoint=False)
    if smooth:
        cs = CubicSpline(u, np.concatenate([P, P[:, :1]], axis=1), axis=1, bc_type="periodic")
        return cs(t)
    return np.stack([np.interp(t, u, np.concatenate([P[0], P[0, :1]])),
                     np.interp(t, u, np.concatenate([P[1], P[1, :1]]))])


# --------------------------------------------------------------------------------------------- the follower


def _rot(P, ang):
    c, s = math.cos(ang), math.sin(ang)
    return np.stack([c * P[0] - s * P[1], s * P[0] + c * P[1]])


def _grown(Q: np.ndarray, r: float) -> np.ndarray:
    """The outline grown by the roller radius (the roller centre's limit), as a closed ring of points."""
    if r <= 0:
        return Q
    from shapely.geometry import Polygon  # noqa: PLC0415

    poly = Polygon(Q.T)
    if not poly.is_valid:
        raise ImportError_("the outline crosses itself")
    g = poly.buffer(r, quad_segs=32)
    if g.geom_type != "Polygon":
        g = max(g.geoms, key=lambda x: x.area)
    R = np.asarray(g.exterior.coords).T[:, :-1]
    return densify(R, smooth=False)


def _crossings(f, t):
    """Where f changes sign along the closed ring: the value t linearly between the two points, per row (angle).
    Returns the largest crossing per row (nan if none)."""
    f2 = np.roll(f, -1, axis=1)
    t2 = np.roll(t, -1, axis=1)
    hit = (f <= 0) & (f2 > 0) | (f > 0) & (f2 <= 0)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        w = f / (f - f2)
        tc = np.where(hit, t + w * (t2 - t), -np.inf)
    out = tc.max(axis=1)
    return np.where(np.isfinite(out), out, np.nan)


def _sweep(fn, n=N, chunk=60):
    th = np.arange(n) * 2 * math.pi / n
    out = np.empty(n)
    for i in range(0, n, chunk):
        out[i:i + chunk] = fn(th[i:i + chunk])
    return th, out


def _support_track(H, dirs):
    """Support h = max_i dirs_k · H_i of a convex polygon H (counter-clockwise) for slowly turning directions,
    by walking from the previous support vertex (exact on a convex polygon). Returns (h, index)."""
    m = H.shape[1]
    k = int(np.argmax(dirs[0, 0] * H[0] + dirs[1, 0] * H[1]))
    hs, ks = np.empty(dirs.shape[1]), np.empty(dirs.shape[1], dtype=int)
    for j in range(dirs.shape[1]):
        ux, uy = dirs[0, j], dirs[1, j]
        v = ux * H[0, k] + uy * H[1, k]
        for step in (1, -1):
            while True:
                k2 = (k + step) % m
                v2 = ux * H[0, k2] + uy * H[1, k2]
                if v2 > v:
                    k, v = k2, v2
                else:
                    break
        # between polygon vertices: the top of a parabola through the support vertex and its neighbours (the hull
        # is a polygon on the curve, so its own support is short of the curve's by up to a sagitta)
        vm = ux * H[0, k - 1] + uy * H[1, k - 1]
        vp = ux * H[0, (k + 1) % m] + uy * H[1, (k + 1) % m]
        den = vm - 2 * v + vp
        hs[j] = v - (vm - vp) ** 2 / (8 * den) if den < 0 else v
        ks[j] = k
    return hs, ks


def follower_lift(Q: np.ndarray, m: D.Mechanism) -> dict:
    """The follower position over a turn for the outline Q (cam frame, around the origin): raw lift s (mm or rad),
    the base circle and, for checking, the position before the lowest point is taken off."""
    sg = m.sigma
    if m.contact == "flat":
        from shapely.geometry import MultiPoint  # noqa: PLC0415

        H = np.asarray(MultiPoint(Q.T).convex_hull.exterior.coords).T[:, :-1]
        if _area(H) < 0:
            H = H[:, ::-1]
        th = np.arange(N) * 2 * math.pi / N
        if m.follower == "translating":
            # face normal +y in the fixed frame is R(−σθ)(0, 1) in the cam frame
            dirs = np.stack([np.sin(sg * th), np.cos(sg * th)])
            d, _ = _support_track(H, dirs)
            rb = float(d.min())
            return {"theta": th, "s": d - rb, "rb": rb, "unit": "mm"}
        # oscillating: face through O2 = (a, 0), normal nf(ψ) = (sin ψ, −cos ψ); touching when h(nf) = a sin ψ
        if not m.a > 0:
            raise D.GeometryError("an oscillating follower needs the centre distance")
        rmax = float(np.hypot(H[0], H[1]).max())
        if not m.a > rmax:
            raise ImportError_("the flat face cannot clear the cam: the centre distance is shorter than the cam")
        psi = np.full(N, math.asin(min(0.99, float(np.hypot(H[0], H[1]).min()) / m.a)))
        for _ in range(30):
            nf = np.stack([np.sin(psi), -np.cos(psi)])
            # the face normal seen from the cam: R(−σθ) nf
            dirs = np.stack([np.cos(sg * th) * nf[0] + np.sin(sg * th) * nf[1],
                             -np.sin(sg * th) * nf[0] + np.cos(sg * th) * nf[1]])
            h, ks = _support_track(H, dirs)
            X = H[:, ks]  # support point (cam frame); in the fixed frame Xf = R(σθ) X
            Xf = np.stack([np.cos(sg * th) * X[0] - np.sin(sg * th) * X[1],
                           np.sin(sg * th) * X[0] + np.cos(sg * th) * X[1]])
            g = m.a * np.sin(psi) - h
            dg = m.a * np.cos(psi) - (np.cos(psi) * Xf[0] + np.sin(psi) * Xf[1])  # envelope theorem
            dpsi = -g / np.where(np.abs(dg) > 1e-12, dg, 1e-12)
            psi = np.clip(psi + np.clip(dpsi, -0.2, 0.2), 1e-6, math.pi / 2 - 1e-9)
            if np.max(np.abs(dpsi)) < 1e-13:
                break
        if np.max(np.abs(g)) > 1e-7:
            raise ImportError_("the flat face does not settle on the outline: check the centre distance")
        psi0 = float(psi.min())
        rb = m.a * math.sin(psi0)
        return {"theta": th, "s": psi - psi0, "rb": rb, "unit": "rad"}

    r = m.rr if m.contact == "roller" else 0.0
    G = _grown(Q, r)  # roller centre limit (knife: the outline itself)
    if m.follower == "translating":
        e = m.e

        def fn(th):  # line x = e, upward, seen from the cam: point R(−σθ)(e, 0), direction R(−σθ)(0, 1)
            c, s_ = np.cos(sg * th)[:, None], np.sin(sg * th)[:, None]
            # fixed-frame coordinates of the ring points: X = c x − s y, Y = s x + c y
            X = c * G[0] - s_ * G[1]
            Y = s_ * G[0] + c * G[1]
            return _crossings(X - e, Y)

        th, y = _sweep(fn)
        if np.any(np.isnan(y)):
            raise ImportError_("the follower line misses the outline: the offset is too large")
        y0 = float(y.min())
        rp = math.hypot(y0, e)
        if y0 <= 0:
            raise ImportError_("the follower would pass the cam centre: check the offset and the centre")
        return {"theta": th, "s": y - y0, "rb": rp - r, "unit": "mm"}

    if not (m.a > 0 and m.L > 0):
        raise D.GeometryError("an oscillating roller or knife follower needs the arm length")
    a, L = m.a, m.L

    def fn(th):
        c, s_ = np.cos(sg * th)[:, None], np.sin(sg * th)[:, None]
        X = c * G[0] - s_ * G[1]
        Y = s_ * G[0] + c * G[1]
        f = np.hypot(X - a, Y) - L
        psi = np.arctan2(-Y, a - X)  # F = (a − L cos ψ, −L sin ψ)
        psi = np.where(psi > 0, psi, -np.inf)  # only the side the arm swings on (0 < ψ < π)
        return _crossings(np.where(np.isfinite(psi), f, 1.0), np.where(np.isfinite(psi), psi, -1e9))

    th, psi = _sweep(fn)
    if np.any(np.isnan(psi)) or np.any(psi <= 0):
        raise ImportError_("the arm's circle misses the outline: check the centre distance and the arm length")
    psi0 = float(psi.min())
    rp = math.sqrt(a * a + L * L - 2 * a * L * math.cos(psi0))
    return {"theta": th, "s": psi - psi0, "rb": rp - r, "unit": "rad"}


# --------------------------------------------------------------------------------------------- smoothing


def _noise(s):
    """Scatter of s from its third differences (a smooth curve has almost none; each sample's own error gives
    var(Δ³) = 20 σ²). Used for finding where a dwell ends."""
    d3 = np.diff(np.concatenate([s, s[:3]]), n=3)
    med = float(np.median(np.abs(d3 - np.median(d3))))
    return max(1.4826 * med / math.sqrt(20.0), 1e-9)


def smooth(theta, s, level: float = 1.0, cap: float = 1e-3, wrap_deg: float = 40.0):
    """Periodic smoothing spline of s(θ) (a cubic spline with the bending ∫s''² weighed against the fit).

    Auto (level 1): the weight by generalised cross-validation, which follows the outline's own accuracy — a CAD
    curve exported as a few hundred fit points carries errors of a few hundredths of a micrometre that repeat every
    fit point, and these become large swings of the acceleration; cross-validation smooths them out while keeping
    the real motion (round trips of this software's own outlines keep the acceleration within 2 %). It is never
    allowed to move the lift by more than cap (1 µm, or 1 µm at the arm for an oscillating follower): a sharp but
    real feature of the outline stays.
    Other levels: the residual RMS is that of the auto fit times level, and the cap is times level too (0: no
    smoothing, an interpolating spline). Returns (spline over θ in [0, 2π), residual RMS, largest residual)."""
    w = int(round(len(theta) * wrap_deg / 360.0))
    x = np.concatenate([theta[-w:] - 2 * math.pi, theta, theta[:w] + 2 * math.pi])
    y = np.concatenate([s[-w:], s, s[:w]])
    if level <= 0:
        return CubicSpline(np.concatenate([theta, [2 * math.pi]]), np.concatenate([s, s[:1]]),
                           bc_type="periodic"), 0.0, 0.0

    def res(sp):
        r = sp(theta) - s
        return float(np.sqrt(np.mean(r**2))), float(np.abs(r).max())

    def largest_lam(ok):  # the largest λ (log10 between −16 and 6) for which ok(rms, max) holds
        lo, hi = -16.0, 6.0
        while hi - lo > 0.02:
            mid = 0.5 * (lo + hi)
            if ok(*res(make_smoothing_spline(x, y, lam=10.0**mid))):
                lo = mid
            else:
                hi = mid
        return make_smoothing_spline(x, y, lam=10.0**lo)

    auto = make_smoothing_spline(x, y)  # λ by generalised cross-validation
    r_auto, m_auto = res(auto)
    lim = cap * level
    if abs(level - 1.0) < 1e-9 and m_auto <= lim:
        return auto, r_auto, m_auto
    target = r_auto * level
    sp = largest_lam(lambda r, m: r <= target and m <= lim)
    return (sp, *res(sp))


# --------------------------------------------------------------------------------------------- the whole import


def _zero_shift(s, lift, sigma):
    """Index of the start of the rise: the end of the longest run at the lowest position (or the lowest point).
    "At the lowest position" is within the outline's own scatter (a smooth law leaves a dwell gradually, so the
    found start can be a fraction of a degree late; "drawing" keeps the drawing's own zero)."""
    low = s <= s.min() + max(20 * sigma, 1e-7 * lift)
    n = len(s)
    if low.all():
        return 0
    k0 = int(np.argmin(low))  # a non-low index
    best, best_end, run = 0, int(np.argmin(s)), 0
    for j in range(1, n + 1):
        i = (k0 + j) % n
        if low[i]:
            run += 1
            if run > best:
                best, best_end = run, i
        else:
            run = 0
    return (best_end + 1) % n if best else int(np.argmin(s))


def _follower(d: dict) -> D.Mechanism:
    """The follower without a base circle (that comes from the outline)."""
    from camkit.analyze import MECH_KEYS, _num  # noqa: PLC0415

    bad = set(d) - set(MECH_KEYS)
    if bad:
        raise D.GeometryError(f"unknown mechanism field: {sorted(bad)[0]}")
    m = D.Mechanism(follower=d.get("follower", "translating"), contact=d.get("contact", "roller"), rb=1.0,
                    rr=_num(d.get("rr")) or 0.0, e=_num(d.get("e")) or 0.0, a=_num(d.get("a")) or 0.0,
                    L=_num(d.get("L")) or 0.0, sigma=int(d.get("sigma", 1)), width=_num(d.get("width")) or 0.0)
    if m.follower not in D.FOLLOWERS:
        raise D.GeometryError("the follower is translating or oscillating")
    if m.contact not in D.CONTACTS:
        raise D.GeometryError("the contact is a roller, a flat face or a knife edge")
    if m.sigma not in (1, -1):
        raise D.GeometryError("the cam turns counter-clockwise (+1) or clockwise (-1)")
    if m.contact == "roller" and not m.rr > 0:
        raise D.GeometryError("give the roller radius")
    if m.follower == "oscillating":
        if not m.a > 0:
            raise D.GeometryError("an oscillating follower needs the centre distance")
        if m.contact != "flat" and not m.L > 0:
            raise D.GeometryError("an oscillating roller or knife follower needs the arm length")
    return m


def import_outline(project: dict) -> dict:
    """{"mechanism": {...}, "outline": {"format": "dxf"|"xy"|"points", "data": text (or [[x, y], ...]),
    "center": [x, y], "zero": "rise"|"drawing", "smooth": 1.0}} → a point-table program for the outline, the base
    circle, the check against the outline and both accelerations."""
    o = project.get("outline") or {}
    md = dict(project.get("mechanism") or {})
    if md.get("groove"):
        raise ImportError_("importing an outline is for an external disk cam (not a groove) in this version")
    m = _follower(md)
    fmt = o.get("format", "xy")
    info: dict = {"format": fmt}
    if fmt == "dxf":
        P, dinfo = read_dxf(o.get("data") or "")
        info.update(dinfo)
        smooth_pts = dinfo["straight"] and P.shape[1] >= 36
    elif fmt in ("xy", "points"):
        P = read_xy(o["data"]) if isinstance(o.get("data"), str) else np.asarray(o.get("data"), dtype=float).T
        if P.ndim != 2 or P.shape[0] != 2 or P.shape[1] < 12:
            raise ImportError_("the outline needs at least 12 points of x, y")
        smooth_pts = bool(o.get("spline", True))
    else:
        raise ImportError_("the outline is a DXF file or a table of x, y points")
    if not np.all(np.isfinite(P)):
        raise ImportError_("numbers must be finite")
    c = o.get("center") or [0.0, 0.0]
    P = P - np.array([[float(c[0])], [float(c[1])]])
    info["points"] = int(P.shape[1])
    info["spline"] = bool(smooth_pts)
    Q = densify(P, smooth_pts)
    from shapely.geometry import Point, Polygon  # noqa: PLC0415

    poly = Polygon(Q.T)
    if not poly.is_valid:
        raise ImportError_("the outline crosses itself")
    if not poly.contains(Point(0.0, 0.0)):
        raise ImportError_("the centre of rotation is not inside the outline")
    info["r_min"] = float(np.hypot(Q[0], Q[1]).min())
    info["r_max"] = float(np.hypot(Q[0], Q[1]).max())

    raw = follower_lift(Q, m)
    s, th = raw["s"], raw["theta"]
    lift = float(s.max() - s.min())
    if lift <= 0:
        raise ImportError_("the outline is a circle about the centre: the follower does not move")
    k0 = _zero_shift(s, lift, _noise(s)) if o.get("zero", "rise") == "rise" else 0
    s = np.roll(s, -k0)
    shift_deg = k0 * 360.0 / N
    level = float(o.get("smooth", 1.0) if o.get("smooth") not in (None, "", "auto") else 1.0)
    if not 0 <= level <= 1000:
        raise ImportError_("the smoothing is between 0 and 1000")
    arm = m.L if (m.follower == "oscillating" and m.contact != "flat") else m.a if m.follower == "oscillating" else 1.0
    sp, resid, rmax = smooth(th, s, level, cap=1e-3 / arm)

    # the program handed to the rest of the kernel: the smoothed lift every STEP_OUT degrees
    deg = np.arange(0, 360, STEP_OUT)
    st = sp(np.radians(deg))
    st = st - st.min() if level > 0 else st
    unit = raw["unit"]
    prog = {"unit": unit, "table": {"deg": deg.round(4).tolist()}}
    if unit == "rad":
        prog["table"]["s_deg"] = np.degrees(st).round(9).tolist()
    else:
        prog["table"]["s"] = st.round(9).tolist()
    mech = {k: v for k, v in (project.get("mechanism") or {}).items()}
    mech["rb"] = round(raw["rb"], 6)

    # accelerations (per rad² of cam angle), unsmoothed (central differences on 0.1°) and smoothed, on 1°
    h = 2 * math.pi / N
    a_raw = (np.roll(s, -1) - 2 * s + np.roll(s, 1)) / h**2
    a_s = sp(th, 2)
    every = N // 360
    scale = 180 / math.pi if unit == "rad" else 1.0  # oscillating: degrees per rad²
    acc = {"deg": list(range(360)), "raw": (a_raw[::every] * scale).tolist(), "smooth": (a_s[::every] * scale).tolist(),
           "raw_peak": float(np.abs(a_raw).max() * scale), "smooth_peak": float(np.abs(a_s).max() * scale)}

    # check: make the outline again from the motion and measure the distance both ways
    check = recheck(Q, m, mech, prog, shift_deg, P if smooth_pts else None)
    return {
        "program": prog,
        "mechanism": mech,
        "report": {
            "source": info,
            "rb": raw["rb"],
            "lift": lift * scale,
            "unit": "deg" if unit == "rad" else "mm",
            "zero": o.get("zero", "rise"),
            "shift_deg": shift_deg,
            "smooth": {"level": level, "residual": resid * scale, "largest": rmax * scale},
            "acc": acc,
            "check": check,
        },
    }


def recheck(Q, m, mech, prog, shift_deg, given=None, tol=TOL_CHECK) -> dict:
    """Largest distance between the imported outline and the one camkit.disk makes from the motion, both ways:
    the made outline to the imported one (at every cam angle), and the imported points (the user's own points when
    the outline was splined through them) to the made one, which also finds parts of the outline the follower
    never touches (a roller larger than a hollow, a flat face over a hollow)."""
    from shapely import distance, points  # noqa: PLC0415
    from shapely.geometry import LinearRing  # noqa: PLC0415

    from camkit.analyze import mechanism  # noqa: PLC0415

    geo = D.analyse(mechanism(mech), Program.from_dict(prog), N)
    Pn = np.asarray(geo["profile"])
    turn = m.sigma * math.radians(shift_deg)  # the drawing turned to the new zero
    Qr = _rot(Q, turn)
    G = _rot(given, turn) if given is not None else Qr[:, :: max(1, Qr.shape[1] // 20000)]
    d1 = distance(points(Pn.T), LinearRing(Qr.T))
    d2 = distance(points(G.T), LinearRing(Pn.T))
    if d2.max() > d1.max():
        k = int(np.argmax(d2))
        worst, where = float(d2[k]), "outline"
        ang = float(np.degrees(math.atan2(G[1, k], G[0, k]))) % 360
    else:
        k = int(np.argmax(d1))
        worst, where, ang = float(d1[k]), "angle", float(k * 360.0 / N)
    return {"max_dev": worst, "at_deg": ang, "where": where, "tol": tol, "ok": bool(worst <= tol)}
