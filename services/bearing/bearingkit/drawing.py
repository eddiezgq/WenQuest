"""Part drawings and operation sketches as SVG (round 64, step 6): the full section of a ring or rolling element drawn
from the very profile the solids are revolved from (so the drawing and the model cannot disagree), with dimension
lines, a parameter table and a title block; and for each grinding or superfinishing operation a sketch of the ring
section with the surfaces worked in that operation drawn heavy and their operation sizes written on.

Tolerances, chamfers, roughness and heat treatment are the company's: blank or "unknown", never made up.

Plain code: no AI, no network. mm; the sheet is A3 (drawings) or A4 (sketches) landscape, in mm.
"""

from __future__ import annotations

import datetime as dt
import math
from xml.sax.saxutils import escape

from bearingkit import parts as PT

FONT = "Noto Sans SC, Microsoft YaHei, PingFang SC, sans-serif"
SCALES = (0.2, 0.25, 0.5, 1, 2, 2.5, 4, 5, 10)  # sheet mm per model mm is 1/k ... k < 1 means enlarged (2:1)
THIN = 'fill="none" stroke="#000" stroke-width="0.18"'
NAMES = {"inner": ("内圈", "Inner ring"), "outer": ("外圈", "Outer ring"), "element": ("滚动体", "Rolling element")}


def _f(v, nd=3):
    return "—" if v is None else f"{v:.{nd}f}".rstrip("0").rstrip(".")


# ------------------------------------------------------------------------------------------------ geometry helpers


def _arc_points(s, n=32):
    rc, zc = s["arc"]["c"]
    rho = s["arc"]["rho"]
    a0 = math.atan2(s["a"][1] - zc, s["a"][0] - rc)
    a1 = math.atan2(s["b"][1] - zc, s["b"][0] - rc)
    if s["arc"]["ccw"] and a1 <= a0:
        a1 += 2 * math.pi
    if not s["arc"]["ccw"] and a1 >= a0:
        a1 -= 2 * math.pi
    return [
        (rc + rho * math.cos(a0 + (a1 - a0) * k / n), zc + rho * math.sin(a0 + (a1 - a0) * k / n)) for k in range(n + 1)
    ]


def _seg_points(s):
    return _arc_points(s) if s.get("arc") else [s["a"], s["b"]]


def _bounds(segs):
    pts = [p for s in segs for p in _seg_points(s)]
    rs, zs = [p[0] for p in pts], [p[1] for p in pts]
    return min(rs), max(rs), min(zs), max(zs)


def feature_segments(segs: list[dict], ring: str, fid: str, kind: str) -> list[int]:
    """Indices of the profile segments that make a machined feature (process.features ids)."""
    rmin, rmax, zmin, zmax = _bounds(segs)
    tol = 1e-6

    def const_r(s):
        return not s.get("arc") and abs(s["a"][0] - s["b"][0]) < tol and abs(s["a"][1] - s["b"][1]) > tol

    def const_z(s):
        return not s.get("arc") and abs(s["a"][1] - s["b"][1]) < tol and abs(s["a"][0] - s["b"][0]) > tol

    def inclined(s):
        return not s.get("arc") and abs(s["a"][0] - s["b"][0]) > tol and abs(s["a"][1] - s["b"][1]) > tol

    idx = list(range(len(segs)))
    if fid == "width":
        return [i for i in idx if const_z(segs[i]) and abs(abs(segs[i]["a"][1]) - zmax) < tol]
    if fid in ("bore", "land_bore"):
        r = min(s["a"][0] for s in segs if const_r(s))
        return [i for i in idx if const_r(segs[i]) and abs(segs[i]["a"][0] - r) < tol]
    if fid in ("od", "land", "rib"):
        r = max(s["a"][0] for s in segs if const_r(s))
        return [i for i in idx if const_r(segs[i]) and abs(segs[i]["a"][0] - r) < tol]
    if fid == "race":
        arcs = [i for i in idx if segs[i].get("arc")]
        if arcs:
            return arcs
        if kind == "tapered":
            inc = [i for i in idx if inclined(segs[i])]
            return [max(inc, key=lambda i: math.dist(segs[i]["a"], segs[i]["b"]))] if inc else []
        r_side = max if ring == "inner" else min
        r = r_side(s["a"][0] for s in segs if const_r(s))
        return [i for i in idx if const_r(segs[i]) and abs(segs[i]["a"][0] - r) < tol]
    return []


# ------------------------------------------------------------------------------------------------ SVG pieces


class View:
    """Model (z axial, r radial) → sheet (x right, y down), centred in a box at scale 1:k."""

    def __init__(self, box, zr, k):
        x, y, w, h = box
        z0, z1, r0, r1 = zr
        self.k, self.cx, self.cy = k, x + w / 2, y + h / 2
        self.zc, self.rc = (z0 + z1) / 2, (r0 + r1) / 2

    def __call__(self, z, r):
        return self.cx + (z - self.zc) / self.k, self.cy - (r - self.rc) / self.k


def _path(view, segs, sign=1.0):
    pts = []
    for s in segs:
        for r, z in _seg_points(s):
            pts.append(view(z, sign * r))
    return "M " + " L ".join(f"{x:.3f},{y:.3f}" for x, y in pts) + " Z"


def _seg_path(view, s, sign=1.0):
    pts = [view(z, sign * r) for r, z in _seg_points(s)]
    return "M " + " L ".join(f"{x:.3f},{y:.3f}" for x, y in pts)


def _arrow(x, y, ang, size=2.2):
    a1, a2 = ang + math.radians(160), ang - math.radians(160)
    return (
        f'<path d="M {x:.3f},{y:.3f} L {x + size * math.cos(a1):.3f},{y + size * math.sin(a1):.3f} '
        f'L {x + size * math.cos(a2):.3f},{y + size * math.sin(a2):.3f} Z" fill="#000"/>'
    )


def dim(p1, p2, text, offset=(0, 0), fs=3.0):
    """A linear dimension between sheet points p1, p2, its line moved by offset, with extension lines."""
    (x1, y1), (x2, y2) = p1, p2
    ox, oy = offset
    a, b = (x1 + ox, y1 + oy), (x2 + ox, y2 + oy)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    out = []
    if ox or oy:
        out.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{a[0]:.3f}" y2="{a[1]:.3f}" {THIN}/>')
        out.append(f'<line x1="{x2:.3f}" y1="{y2:.3f}" x2="{b[0]:.3f}" y2="{b[1]:.3f}" {THIN}/>')
    out.append(f'<line x1="{a[0]:.3f}" y1="{a[1]:.3f}" x2="{b[0]:.3f}" y2="{b[1]:.3f}" {THIN}/>')
    out.append(_arrow(a[0], a[1], ang + math.pi))
    out.append(_arrow(b[0], b[1], ang))
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    deg = math.degrees(ang)
    if deg > 90 or deg < -90:
        deg += 180
    out.append(
        f'<text x="{mx:.3f}" y="{my - 1:.3f}" font-size="{fs}" text-anchor="middle" '
        f'transform="rotate({deg:.2f} {mx:.3f} {my:.3f})">{escape(text)}</text>'
    )
    return "\n".join(out)


def _hatch(view, segs, sign, pid):
    return (
        f'<clipPath id="{pid}"><path d="{_path(view, segs, sign)}"/></clipPath>'
        f'<g clip-path="url(#{pid})" stroke="#000" stroke-width="0.13">'
        + "".join(f'<line x1="{x:.1f}" y1="0" x2="{x - 400:.1f}" y2="400"/>' for x in range(0, 900, 2))
        + "</g>"
    )


def _table(x, y, rows, col=(48, 40, 22), title=None, fs=2.8, head=None):
    out, ty = [], y
    if title:
        out.append(
            f'<text x="{x:.1f}" y="{ty + 4:.1f}" font-size="{fs + 0.6}" font-weight="bold">{escape(title)}</text>'
        )
        ty += 6
    for row in ([head] if head else []) + list(rows):
        cx = x
        for j, w in enumerate(col):
            out.append(f'<rect x="{cx:.1f}" y="{ty:.1f}" width="{w:.1f}" height="5.2" {THIN}/>')
            v = row[j] if j < len(row) else ""
            bold = ' font-weight="bold"' if head and row is head else ""
            out.append(f'<text x="{cx + 1.1:.1f}" y="{ty + 3.8:.1f}" font-size="{fs}"{bold}>{escape(str(v))}</text>')
            cx += w
        ty += 5.2
    return "\n".join(out), ty


def _frame(w, h, title_cells, source):
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}" '
        f'font-family="{FONT}">',
        f'<rect width="{w}" height="{h}" fill="#fff"/>',
        f'<rect x="10" y="10" width="{w - 20}" height="{h - 20}" fill="none" stroke="#000" stroke-width="0.6"/>',
    ]
    bx, by, bw, bh = w - 190, h - 40, 180, 30
    out.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="none" stroke="#000" stroke-width="0.45"/>')
    cells = list(title_cells) + [("日期", dt.date.today().isoformat()), ("来源", source)]
    for i, (a, b) in enumerate(cells[:6]):
        cx, cy = bx + (i % 2) * bw / 2, by + (i // 2) * bh / 3
        out.append(f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{bw / 2:.1f}" height="{bh / 3:.1f}" {THIN}/>')
        out.append(
            f'<text x="{cx + 2:.1f}" y="{cy + 6.4:.1f}" font-size="2.9">{escape(a)}：{escape(str(b))[:34]}</text>'
        )
    return out


def _scale(span_z, span_r, w, h):
    need = max(span_z / w, span_r / h)
    return next((k for k in SCALES if k >= need), SCALES[-1])


def _kstr(k):
    return f"{1 / k:g}:1" if k < 1 else f"1:{k:g}"


# ------------------------------------------------------------------------------------------------ part drawing


def _ring_dims(view, segs, which, g, fs):
    """Dimensions on the upper half of a ring section: width, bore / outside diameter, raceway, groove radius."""
    rmin, rmax, zmin, zmax = _bounds(segs)
    out = []
    out.append(dim(view(zmin, rmax), view(zmax, rmax), _f(zmax - zmin), (0, -9), fs))
    # diameters as vertical dimensions across the axis (from −r to +r), placed left of the section
    out.append(dim(view(zmin, -rmax), view(zmin, rmax), "φ" + _f(2 * rmax), (-10, 0), fs))
    out.append(dim(view(zmin, -rmin), view(zmin, rmin), "φ" + _f(2 * rmin), (-18, 0), fs))
    arcs = [s for s in segs if s.get("arc")]
    if arcs:
        s = arcs[0]
        rc, zc = s["arc"]["c"]
        rho = s["arc"]["rho"]
        r_bottom = rc - rho if which == "inner" else rc + rho
        out.append(dim(view(zmax, -r_bottom), view(zmax, r_bottom), "φ" + _f(2 * r_bottom), (12, 0), fs))
        bx, by = view(zc, r_bottom + (1.25 if which == "inner" else -1.25) * rho)
        out.append(f'<text x="{bx:.2f}" y="{by + 1:.2f}" font-size="{fs}" text-anchor="middle">R{_f(rho)}</text>')
    elif g["type"] == "tapered":
        inc = [
            s
            for s in segs
            if not s.get("arc") and abs(s["a"][0] - s["b"][0]) > 1e-6 and abs(s["a"][1] - s["b"][1]) > 1e-6
        ]
        if inc:
            s = max(inc, key=lambda s: math.dist(s["a"], s["b"]))
            dmid = s["a"][0] + s["b"][0]
            zm = (s["a"][1] + s["b"][1]) / 2
            out.append(dim(view(zm, -dmid / 2), view(zm, dmid / 2), "φ" + _f(dmid) + "（中点）", (0, 0), fs))
    else:  # cylindrical: the raceway is the land
        pass
    return "\n".join(out)


def part_rows(g: dict, which: str) -> list[tuple]:
    """(name, value, tolerance) for the parameter table: from the design, tolerance "unknown" until entered."""
    pr = PT.parts(g)
    segs = pr[which]
    rows = []
    if which == "element":
        if pr["element_kind"] == "ball":
            rows.append(("钢球直径 Dw", _f(g["Dw"], 4), "未知"))
        else:
            rows += [("直径 Dw", _f(g["Dw"], 4), "未知"), ("长度 Lw", _f(g["Lw"], 4), "未知")]
            if g.get("Lwe"):
                rows.append(("有效接触长度 Lwe", _f(g["Lwe"], 4), "—"))
            if pr["element_kind"] == "taper":
                rows.append(("半锥角", _f((g["alpha_o_deg"] - g["alpha_i_deg"]) / 2, 4) + "°", "—"))
                if g.get("R_end"):
                    rows.append(("大端球基面半径", _f(g["R_end"]), "—"))
        rows.append(("数量 Z", g["Z"], ""))
        return rows
    rmin, rmax, zmin, zmax = _bounds(segs)
    rows += [
        ("宽度", _f(zmax - zmin), "未知"),
        ("内径" if which == "inner" else "挡边内径", _f(2 * rmin), "未知"),
        ("挡边外径" if which == "inner" else "外径", _f(2 * rmax), "未知"),
    ]
    arcs = [s for s in segs if s.get("arc")]
    if arcs:
        s = arcs[0]
        rb = s["arc"]["c"][0] - s["arc"]["rho"] if which == "inner" else s["arc"]["c"][0] + s["arc"]["rho"]
        rows += [("沟底直径", _f(2 * rb), "未知"), ("沟曲率半径", _f(s["arc"]["rho"]), "未知")]
        if g["type"] == "angular":
            rows.append(("接触角", _f(g["alpha0_deg"], 2) + "°", "—"))
    elif g["type"] == "cylindrical":
        rows.append(("滚道直径", _f(g["di"] if which == "inner" else g["do"]), "未知"))
    elif g["type"] == "tapered":
        rows.append(("滚道角", _f(g["alpha_i_deg"] if which == "inner" else g["alpha_o_deg"], 4) + "°", "未知"))
    return rows


def part_sheet(g: dict, which: str, project_title: str = "", tolerances: dict | None = None) -> str:
    """A3 working drawing of one part: full section (both halves about the axis, hatched), dimensions, table."""
    pr = PT.parts(g)
    segs = pr[which]
    W, H = 420.0, 297.0
    rmin, rmax, zmin, zmax = _bounds(segs)
    ball = which == "element" and pr["element_kind"] == "ball"
    lo = -rmax
    box = (40, 30, 200, 200)
    k = _scale(zmax - zmin + 30, 2 * rmax + 30, box[2], box[3])
    view = View(box, (zmin, zmax, lo, rmax), k)
    fs = 3.0
    out = _frame(
        W,
        H,
        [("名称", NAMES[which][0]), ("比例", _kstr(k)), ("项目", project_title or "—"), ("材料", "（企业填写）")],
        "问渠轴承 · FreeCAD",
    )
    # axis
    ax0, ay = view(zmin - 8 * k, 0)
    ax1, _ = view(zmax + 8 * k, 0)
    out.append(
        f'<line x1="{ax0:.2f}" y1="{ay:.2f}" x2="{ax1:.2f}" y2="{ay:.2f}" stroke="#000" stroke-width="0.18" '
        'stroke-dasharray="8 1.5 1 1.5"/>'
    )
    if which == "element":
        if ball:
            cx, cy = view(0, 0)
            rr = g["Dw"] / 2 / k
            out.append(
                f'<circle cx="{cx:.3f}" cy="{cy:.3f}" r="{rr:.3f}" fill="none" stroke="#000" stroke-width="0.5"/>'
            )
            out.append(dim((cx - rr, cy), (cx + rr, cy), "Sφ" + _f(g["Dw"], 4), (0, -rr - 6), fs))
        else:
            for sign in (1.0, -1.0):
                out.append(f'<path d="{_path(view, segs, sign)}" fill="none" stroke="#000" stroke-width="0.5"/>')
            out.append(dim(view(zmin, -rmax), view(zmin, rmax), "φ" + _f(2 * rmax, 4), (-10, 0), fs))
            out.append(dim(view(zmin, rmax), view(zmax, rmax), _f(zmax - zmin, 4), (0, -9), fs))
    else:
        for n, sign in enumerate((1.0, -1.0)):
            out.append(_hatch(view, segs, sign, f"h{which}{n}"))
            out.append(f'<path d="{_path(view, segs, sign)}" fill="none" stroke="#000" stroke-width="0.5"/>')
        out.append(_ring_dims(view, segs, which, g, fs))
    rows = part_rows(g, which)
    tol = tolerances or {}
    rows = [(a, b, tol.get(a, c)) for a, b, c in rows]
    body, ty = _table(255, 30, rows, title="主要尺寸（mm）", head=("项目", "公称", "公差"))
    out.append(body)
    out.append(f'<text x="255" y="{ty + 8:.1f}" font-size="3.3" font-weight="bold">技术要求（由工程师填写）</text>')
    for j in range(4):
        out.append(
            f'<line x1="255" y1="{ty + 15 + j * 7:.1f}" x2="405" y2="{ty + 15 + j * 7:.1f}" {THIN} '
            'stroke-dasharray="1 1"/>'
        )
    notes = (
        "尺寸由问渠轴承按设计参数算出（确定性计算，未经 AI）。"
        "公差、倒角、粗糙度、热处理在企业填写前为“未知”，图上不编数。"
    )
    out.append(f'<text x="15" y="{H - 46:.1f}" font-size="2.6" fill="#333">{escape(notes)}</text>')
    if which != "element":
        missing = "倒角、退刀槽" + ("、挡边" if g["type"] == "cylindrical" else "") + "没有数据，未画。"
        out.append(f'<text x="15" y="{H - 41:.1f}" font-size="2.6" fill="#333">{escape(missing)}</text>')
    out.append("</svg>")
    return "\n".join(out)


# ------------------------------------------------------------------------------------------------ operation sketch


def _size_text(s):
    if not s:
        return "未知"
    up, lo = s["upper"], s["lower"]

    def dv(x):
        return "0" if abs(x) < 1e-12 else f"{x:+.3f}".replace("-", "−")

    return f"{s['size']:.4f} {dv(up)}/{dv(lo)}"


def op_sketch(
    g: dict, ring: str, card: dict, feature_names: dict, project_title: str = "", fictional: bool = False
) -> str:
    """A4 sketch of one operation: the ring section, the surfaces this operation works heavy, their sizes."""
    pr = PT.parts(g)
    segs = pr[ring]
    W, H = 297.0, 210.0
    rmin, rmax, zmin, zmax = _bounds(segs)
    box = (25, 40, 150, 100)
    k = _scale(zmax - zmin + 12, rmax - rmin + 12, box[2], box[3])
    view = View(box, (zmin, zmax, rmin, rmax), k)
    name = (card.get("name") or {}).get("zh") or card.get("kind")
    out = _frame(
        W,
        H,
        [
            ("工序", f"{card.get('no', '')} {name}"),
            ("零件", NAMES[ring][0]),
            ("项目", project_title or "—"),
            ("比例", _kstr(k)),
        ],
        "问渠轴承 · 工序简图",
    )
    out.append(
        f'<text x="15" y="20" font-size="5" font-weight="bold">工序简图　{escape(str(card.get("no", "")))} '
        f"{escape(name)}</text>"
    )
    if fictional:
        out.append('<text x="15" y="26" font-size="2.8" fill="#a15c00">示例模板的数是虚构的演示数，不是推荐值。</text>')
    out.append(f'<path d="{_path(view, segs)}" fill="#eef1f5" stroke="#000" stroke-width="0.35"/>')
    lines = card.get("lines") or []
    labels = []
    for ln in lines:
        idx = feature_segments(segs, ring, ln["feature"], g["type"])
        for i in idx:
            out.append(
                f'<path d="{_seg_path(view, segs[i])}" fill="none" stroke="#c0392b" stroke-width="1.4" '
                'stroke-linecap="round"/>'
            )
        if idx:
            s = segs[idx[0]]
            pts = _seg_points(s)
            r, z = pts[len(pts) // 2]
            labels.append((ln, view(z, r)))
    # leaders to a label column on the right of the section
    for j, (ln, (x, y)) in enumerate(labels):
        tx, ty = 185, 45 + j * 16
        out.append(
            f'<line x1="{x:.2f}" y1="{y:.2f}" x2="{tx - 2:.2f}" y2="{ty - 1:.2f}" '
            'stroke="#c0392b" stroke-width="0.25"/>'
        )
        out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="0.8" fill="#c0392b"/>')
        fname = feature_names.get(ln["feature"], ln["feature"])
        out.append(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="3.4" font-weight="bold">{escape(fname)}</text>')
        if card.get("kind") == "heat":
            sub = f"Δ {_f(ln.get('change'), 4)}　波动 {_f(ln.get('scatter'), 4)}　变形 {_f(ln.get('distortion'), 4)}"
        else:
            sub = f"工序尺寸 {_size_text(ln.get('size'))}"
            if ln.get("Z") is not None:
                sub2 = f"留量 {_f(ln['Z'], 4)}（实际 {_f(ln.get('Zmin'), 4)} – {_f(ln.get('Zmax'), 4)}）"
                out.append(f'<text x="{tx:.1f}" y="{ty + 9:.1f}" font-size="2.9">{escape(sub2)}</text>')
        out.append(f'<text x="{tx:.1f}" y="{ty + 4.5:.1f}" font-size="2.9">{escape(sub)}</text>')
    # axis below the section
    ax0, ay = view(zmin - 5 * k, rmin - 8 * k)
    ax1, _ = view(zmax + 5 * k, rmin - 8 * k)
    out.append(
        f'<line x1="{ax0:.2f}" y1="{ay:.2f}" x2="{ax1:.2f}" y2="{ay:.2f}" stroke="#000" stroke-width="0.18" '
        'stroke-dasharray="8 1.5 1 1.5"/>'
    )
    out.append(f'<text x="{ax1 + 1:.2f}" y="{ay + 1:.2f}" font-size="2.5">轴线（简图未按比例画到轴线）</text>')
    eq = card.get("equipment") or "（企业填写）"
    rows = [("设备", eq)] + [
        (p.get("k") or "", f"{p.get('v') or ''} {p.get('u') or ''}".strip()) for p in card.get("params") or []
    ]
    body, _ = _table(25, 146, rows[:3], col=(40, 80), title="设备与参数")
    out.append(body)
    out.append(
        '<text x="15" y="36" font-size="2.5" fill="#333">'
        "加粗红线为本道加工的面。尺寸 mm，按直径或宽度计，入体标注。沟曲率半径、沟位置本图不算。</text>"
    )
    out.append("</svg>")
    return "\n".join(out)


def sketches(g: dict, result: dict, project_title: str = "") -> list[tuple[str, str]]:
    """(file name, svg) for every grinding, superfinishing or other cutting operation after the turning, per ring."""
    out = []
    for ring, rr in (result.get("rings") or {}).items():
        names = {f["id"]: f["zh"] for f in rr["features"]}
        for c in rr["cards"]:
            if c["kind"] in ("grind", "superfinish", "cut") and c["lines"]:
                svg = op_sketch(g, ring, c, names, project_title, bool(result.get("fictional")))
                out.append((f"{ring}-op{c.get('no')}-sketch.svg", svg))
    return out
