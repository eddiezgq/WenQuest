# -*- coding: utf-8 -*-
"""花样机模板（第 42 轮）：针迹轨迹 + 槽宽 → 模板板上的通槽，出 STEP 送数字工厂数控编程。

模板缝纫：布夹在模板里，模板随 X–Y 工作台走花样，机针和压脚在模板的通槽里走。
- 槽 = 针迹折线向两边各让出“槽宽 / 2”（圆头、圆角），再把小于 1.6 mm 的缝隙填平（之字、套结这类花样合成一整块开口）。
- 封闭花样（圆、矩形、星……）槽会把板分成内外两块：在轨迹上均匀留几处“连接桥”（默认 3 mm），内岛靠它连着。
  连接桥处机针过不去，缝到桥要抬针跳过、或第二次装夹补缝——计算结果里会提示。
- 板：槽的外接矩形四周各放“边距”；左右各一个 Ø6 定位销孔。上表面在 Z0、外形中心在 X0 Y0（数控工件零点，同第 41 轮平板零件）。
"""
import math

from . import pattern as P

PIN_D = 6.0
GAP_FILL = 0.8          # 填平宽度小于 2 × 0.8 mm 的缝隙


def _dedupe(pts):
    out = []
    for q in pts:
        if not out or math.hypot(q[0] - out[-1][0], q[1] - out[-1][1]) > 1e-6:
            out.append([float(q[0]), float(q[1])])
    return out


def _geoms(g):
    return list(getattr(g, "geoms", [g]))


def geom(params, slot_w=5.0, t=3.0, margin=20.0, bridge_w=3.0):
    """模板的平面几何（mm，已移到工件坐标）：slots 槽的外轮廓（多块时每块一条）、plate 板尺寸、pins 定位销孔、bridges 连接桥数"""
    from shapely.geometry import LineString, Point, Polygon
    from shapely.ops import unary_union

    p = P.clean(params)
    pts = _dedupe(P.stitches(p))
    path = LineString(pts) if len(pts) > 1 else Point(pts[0])
    r = slot_w / 2
    slot = path.buffer(r, quad_segs=8).buffer(GAP_FILL, quad_segs=4).buffer(-GAP_FILL, quad_segs=4)
    bridges = []
    if any(g.interiors for g in _geoms(slot)) and path.length > 0:
        L = path.length
        for k in (2, 3, 4, 6, 8):
            cuts, at = [], []
            for j in range(k):
                d = L * (j + 0.5) / k
                c = path.interpolate(d)
                a, b = path.interpolate(max(0.0, d - 0.5)), path.interpolate(min(L, d + 0.5))
                ux, uy = b.x - a.x, b.y - a.y
                n = math.hypot(ux, uy) or 1.0
                ux, uy = ux / n, uy / n
                vx, vy = -uy, ux
                h, w = bridge_w / 2, r + 2.0
                cuts.append(Polygon([(c.x + ux * sx * h + vx * sy * w, c.y + uy * sx * h + vy * sy * w)
                                     for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]))
                at.append([round(c.x, 2), round(c.y, 2)])
            s2 = slot.difference(unary_union(cuts))
            if not any(g.interiors for g in _geoms(s2)):
                slot, bridges = s2, at
                break
        else:
            raise ValueError("花样太复杂，连接桥留不出来")
    x0, y0, x1, y1 = slot.bounds
    W, H = (x1 - x0) + 2 * margin, (y1 - y0) + 2 * margin
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    rings = []
    for g in _geoms(slot):
        if g.area < 0.5:
            continue
        g = g.simplify(0.02)
        rings.append([[round(x - cx, 4), round(y - cy, 4)] for x, y in list(g.exterior.coords)[:-1]])
    pins = [[round(-W / 2 + margin / 2, 3), 0.0, PIN_D / 2], [round(W / 2 - margin / 2, 3), 0.0, PIN_D / 2]]
    return {"slots": rings, "plate": [round(W, 3), round(H, 3), float(t)], "pins": pins, "bridges": len(bridges),
            "bridge_at": [[round(x - cx, 2), round(y - cy, 2)] for x, y in bridges], "bridge_w": bridge_w,
            "closed": bool(bridges), "slot_w": slot_w, "stitches": len(pts),
            "path": [[round(x - cx, 3), round(y - cy, 3)] for x, y in pts], "area_mm2": round(sum(Polygon(r).area for r in rings), 1)}


def step(g):
    """模板 STEP（build123d）；没有 build123d 返回 None"""
    try:
        import build123d as bd
    except Exception:
        return None
    import os
    import tempfile
    W, H, t = g["plate"]
    plate = bd.Solid.make_box(W, H, t, bd.Plane(origin=(-W / 2, -H / 2, -t)))
    for ring in g["slots"]:
        face = bd.Face(bd.Wire.make_polygon([bd.Vector(x, y, -t - 1) for x, y in ring], close=True))
        plate = plate - bd.Solid.extrude(face, bd.Vector(0, 0, t + 2))
    for x, y, r in g["pins"]:
        plate = plate - bd.Solid.make_cylinder(r, t + 2, bd.Plane(origin=(x, y, -t - 1)))
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "template.step")
        bd.export_step(plate, path)
        with open(path, "rb") as f:
            return f.read()
