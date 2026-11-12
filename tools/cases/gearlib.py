"""第 161 轮：齿轮类案例共用——渐开线齿廓（标准齿条展成的近似：渐开线齿面 + 基圆以下径向线 + 齿根圆角）、
轮齿有限元（几个齿的薄片，Gmsh 二阶四面体 + CalculiX，和数字工厂“仿真与分析”同一套求解代码）、build123d 三维齿轮、齿轮零件图。

齿根过渡曲线：真实的展成齿根是延伸渐开线的等距线（次摆线），这里用一段圆弧（半径 ρ_f = 0.38 m，齿条刀具齿顶圆角）代替，
与径向线、齿根圆相切。齿根应力因此和 ISO 6336 的 Y_Fa·Y_Sa 有几个百分点的出入，案例里照实对照。
"""
from __future__ import annotations

import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "factory" / "digital"))
os.environ.setdefault("WQ_CCX_SOLVER", "SPOOLES")
from cae import solve as S  # noqa: E402


def inv(a):
    return math.tan(a) - a


def _info(m, z, alpha=20.0, ha=1.0, c=0.25, rho=0.38):
    al = math.radians(alpha)
    r = m * z / 2
    return dict(r=r, rb=r * math.cos(al), ra=r + ha * m, rf=r - (ha + c) * m, rho_f=rho * m, alpha=alpha)


def _cutter(m, alpha, ha, c, rho, n=7):
    """基本齿条刀具（GB/T 1356：α 20°、齿顶高 1.25m 切入、齿顶圆角 ρ）在刀具坐标里：u 沿节线，v 向齿轮外（节线 v = 0）。
    刀齿向齿轮中心伸出到 v = −(ha + c)m。返回 n 个刀齿的多边形（shapely）。"""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union
    al = math.radians(alpha)
    H = (ha + c) * m
    w0 = math.pi * m / 4                               # 节线上刀齿半宽（刀齿厚 = 齿槽宽 = πm/2）
    top = 3 * m
    teeth = []
    for k in range(-(n // 2), n // 2 + 1):
        uc = k * math.pi * m
        # 刀齿：节线处半宽 w0，往下（v 负）变窄：u = ±(w0 − (−v)·tanα)
        def flank(v, sgn):
            return uc + sgn * (w0 + v * math.tan(al))
        # 齿顶圆角：与侧面、齿顶线 v = −H 都相切的圆
        cy = -H + rho
        # 圆心到侧面距离 ρ：侧面直线 u = uc + sgn(w0 + v tanα)，法向距离 = |u − line(v)|·cosα
        pts = []
        for sgn in (-1, 1):
            cx = flank(cy, sgn) - sgn * rho / math.cos(al)
            a_side = math.pi + sgn * (math.pi / 2 - al) if sgn < 0 else -al
            # 圆弧：从侧面切点到底部切点
            if sgn < 0:
                arc = [(cx + rho * math.cos(t), cy + rho * math.sin(t)) for t in np.linspace(math.pi - al, 1.5 * math.pi, 12)]
                pts += [(flank(top, -1), top)] + arc
            else:
                arc = [(cx + rho * math.cos(t), cy + rho * math.sin(t)) for t in np.linspace(1.5 * math.pi, 2 * math.pi + al, 12)]
                pts += arc + [(flank(top, 1), top)]
            del a_side
        teeth.append(Polygon(pts))
    return unary_union(teeth)


@__import__("functools").lru_cache(maxsize=16)
def _tooth_slice(m, z, alpha=20.0, ha=1.0, c=0.25, rho=0.38, steps=900):
    """用齿条刀具展成一个齿（数值包络：齿坯减去刀具在各个滚动位置的并集），返回以 90°+π/z 为齿中线、两边到齿槽中线的扇形片（shapely）。"""
    from shapely import affinity
    from shapely.geometry import Point, Polygon
    from shapely.ops import unary_union
    info = _info(m, z, alpha, ha, c, rho)
    r = info["r"]
    cutter = _cutter(m, alpha, ha, c, rho)
    span = 4 * math.pi * m / r                          # 滚过约 4 个齿距
    cuts = []
    for ph in np.linspace(-span, span, steps):
        g = affinity.translate(cutter, xoff=-r * ph, yoff=r)             # 刀具节线与分度圆相切于 (0, r)；齿轮逆时针转 φ，刀具纯滚动平移 −rφ
        cuts.append(affinity.rotate(g, -ph, origin=(0, 0), use_radians=True))   # 换到齿轮坐标：齿轮转过 φ
    blank = Point(0, 0).buffer(info["ra"], quad_segs=256)
    gear = blank.difference(unary_union(cuts))
    th = math.pi / z
    c0 = math.pi / 2 + th                                # 这个齿的中线（刀齿居中 → 90° 是齿槽中线）
    R = info["ra"] * 1.5
    wedge = Polygon([(0, 0)] + [(R * math.cos(t), R * math.sin(t)) for t in np.linspace(c0 - th, c0 + th, 40)])
    sl = gear.intersection(wedge)
    if sl.geom_type != "Polygon":
        sl = max(sl.geoms, key=lambda x: x.area)
    return sl, c0, info


def tooth_shapes(m, z, n_teeth=None, center_deg=90.0, rim=None, **kw):
    """整圈（n_teeth=None）或中间对准 center_deg 的几个齿（再截去 rim 以内）。返回 (shapely 多边形, info, 第一个齿中线角, 齿距角)"""
    from shapely import affinity
    from shapely.geometry import Point
    from shapely.ops import unary_union
    sl, c_sl, info = _tooth_slice(m, z, **kw)
    pitch = 2 * math.pi / z
    n = n_teeth or z
    c0 = math.radians(center_deg) - (n - 1) / 2 * pitch
    parts = [affinity.rotate(sl, c0 + k * pitch - c_sl, origin=(0, 0), use_radians=True) for k in range(n)]
    shp = unary_union([p.buffer(1e-7) for p in parts]).buffer(-1e-7)
    if rim:
        shp = shp.difference(Point(0, 0).buffer(rim, quad_segs=128))
    shp = shp.simplify(0.002)
    return shp, info, c0, pitch


def outline(m, z, n_teeth=None, center_deg=90.0, **kw):
    """整圈外廓点（逆时针）"""
    shp, info, c0, pitch = tooth_shapes(m, z, n_teeth, center_deg, **kw)
    pts = np.array(shp.exterior.coords)[:-1]
    return pts, info, c0, pitch


def tooth_fea(m, z, Ft_per_mm, t=1.0, n_teeth=3, rim=None, h=None):
    """几个齿的薄片（厚 t），中间那个齿的齿顶受法向力（沿过齿顶的基圆切线，即啮合线方向），
    内圆（轮缘以下 rim）和两侧剖切面固定。返回齿根受拉侧最大主应力、名义 σF0 对照所需的量和网格信息。
    Ft_per_mm：分度圆上的圆周力 / 齿宽（N/mm）。"""
    import gmsh
    info0 = _info(m, z)
    rim = rim or info0["rf"] - 3.0 * m
    shp, info, c0, pitch = tooth_shapes(m, z, n_teeth, rim=rim)
    pts = np.array(shp.exterior.coords)[:-1]
    if not gmsh.isInitialized():
        gmsh.initialize(["-noenv"], readConfigFiles=False)
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.clear()
    gmsh.model.add("t")
    occ = gmsh.model.occ
    a0, a1 = c0 - pitch / 2, c0 + (n_teeth - 1) * pitch + pitch / 2
    P = [occ.addPoint(x, y, 0) for x, y in pts]
    L = [occ.addLine(P[i], P[(i + 1) % len(P)]) for i in range(len(P))]
    loop = occ.addCurveLoop(L)
    surf = occ.addPlaneSurface([loop])
    occ.extrude([(2, surf)], 0, 0, t, numElements=[2], recombine=False)
    occ.synchronize()
    h = h or m / 3
    gmsh.option.setNumber("Mesh.MeshSizeMax", h)
    gmsh.option.setNumber("Mesh.ElementOrder", 2)
    gmsh.option.setNumber("Mesh.MaxNumThreads3D", 1)
    # 中间齿的齿根圆角附近加密
    fld = gmsh.model.mesh.field
    mid = c0 + (n_teeth // 2) * pitch
    balls = []
    rp0 = np.hypot(pts[:, 0], pts[:, 1])
    ap0 = np.arctan2(pts[:, 1], pts[:, 0])
    for side in (-1, 1):
        sel = [(x, y) for (x, y), r_, a_ in zip(pts, rp0, ap0)
               if r_ < info["rf"] + 0.6 * m and 0 < side * (a_ - mid) < pitch / 2]
        cxy = np.mean(sel, axis=0) if sel else np.array([info["rf"] * math.cos(mid), info["rf"] * math.sin(mid)])
        b = fld.add("Ball")
        fld.setNumber(b, "Radius", 0.6 * m)
        fld.setNumber(b, "Thickness", 0.8 * m)
        fld.setNumber(b, "VIn", info["rho_f"] / 6)
        fld.setNumber(b, "VOut", h)
        fld.setNumber(b, "XCenter", float(cxy[0]))
        fld.setNumber(b, "YCenter", float(cxy[1]))
        fld.setNumber(b, "ZCenter", t / 2)
        balls.append(b)
    mn = fld.add("Min")
    fld.setNumbers(mn, "FieldsList", balls)
    fld.setAsBackgroundMesh(mn)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 0)
    gmsh.option.setNumber("Mesh.MeshSizeFromPoints", 0)
    gmsh.model.mesh.generate(3)
    et, _, en = gmsh.model.mesh.getElements(3)
    tets = np.asarray(en[list(et).index(11)], np.int64).reshape(-1, 10)
    ntags, xyz, _ = gmsh.model.mesh.getNodes()
    ntags = np.asarray(ntags, np.int64)
    xyz = np.asarray(xyz, float).reshape(-1, 3)
    R = np.hypot(xyz[:, 0], xyz[:, 1])
    ang = np.arctan2(xyz[:, 1], xyz[:, 0])
    fixed = {int(n) for n, r_, a_ in zip(ntags, R, ang)
             if r_ < rim + 1e-4 or (r_ < info["rf"] + 1e-3 and (abs(a_ - a0) < 1e-4 or abs(a_ - a1) < 1e-4))}
    # 齿顶受力点：中间齿受力一侧（θ < 齿中线）的齿顶角，取外廓上 r ≈ ra、角度最小的点，再取这一点沿厚度的一列节点
    rp = np.hypot(pts[:, 0], pts[:, 1])
    ap = np.arctan2(pts[:, 1], pts[:, 0])
    cand = [(a_, x, y) for (x, y), r_, a_ in zip(pts, rp, ap) if r_ > info["ra"] - 1e-3 and abs(a_ - mid) < pitch / 2]
    tip_th, tx, ty = min(cand)
    tip = np.array([tx, ty])
    d = np.hypot(xyz[:, 0] - tip[0], xyz[:, 1] - tip[1])
    tip_nodes = [int(n) for n, dd in zip(ntags, d) if dd < 1e-3]
    al_a = math.acos(info["rb"] / info["ra"])
    Fn = Ft_per_mm * t / math.cos(math.radians(20.0))              # 分度圆圆周力 → 法向力（作用线不变）
    e_t = np.array([-math.sin(tip_th), math.cos(tip_th)])            # +θ 方向
    e_r = np.array([math.cos(tip_th), math.sin(tip_th)])
    dirv = math.cos(al_a) * e_t - math.sin(al_a) * e_r                # 与切向成 α_a，向内
    forces = {n: np.array([dirv[0], dirv[1], 0.0]) * Fn / len(tip_nodes) for n in tip_nodes}
    mat = {"E_mpa": 206000.0, "nu": 0.3, "density_t_mm3": 7.85e-9}
    with tempfile.TemporaryDirectory() as dd:
        S.write_inp(os.path.join(dd, "job.inp"), ntags, xyz, tets, fixed, [], forces, mat)
        r = subprocess.run([S.CCX, "-i", "job"], cwd=dd, capture_output=True, text=True, timeout=280, env={**os.environ, "OMP_NUM_THREADS": "2"})
        if r.returncode != 0:
            raise RuntimeError("CalculiX 失败：" + (r.stdout + r.stderr)[-400:])
        _, stress = S.read_frd(os.path.join(dd, "job.frd"))
    # 中间齿齿根：受力那侧（θ < mid，力把齿推向 +θ）受拉，取最大主应力；另一侧受压，取最小主应力
    def principal(s_):
        sxx, syy, szz, sxy, syz, szx = s_[:6]
        return np.linalg.eigvalsh(np.array([[sxx, sxy, szx], [sxy, syy, syz], [szx, syz, szz]]))
    zone = (R < info["rf"] + 1.2 * m) & (R > info["rf"] - 0.05) & (np.abs(ang - mid) < pitch / 2)
    s1t, s3c, where = 0.0, 0.0, None
    for n, ok, a_, r_ in zip(ntags, zone, ang, R):
        if not ok or int(n) not in stress:
            continue
        p = principal(stress[int(n)])
        if a_ < mid and p[2] > s1t:
            s1t, where = p[2], (float(r_), float(a_ - mid))
        if a_ > mid:
            s3c = min(s3c, p[0])
    return dict(sigma1=float(s1t), sigma3=float(s3c), where=where, n_el=int(len(tets)), rim=rim, t=t, info=info, Fn=Fn,
                tip_nodes=len(tip_nodes), xyz=xyz, ntags=ntags, stress=stress, mid=mid, pitch=pitch)


def gear_solid(m, z, b, bore, key=None, hub=None, web=None):
    """build123d 直齿轮：外廓拉伸 b；孔 bore；键槽 key=(宽, 槽底离孔心)；hub=(毂外径, 毂长)（两边对称伸出）；web=(辐板厚, 轮缘内径)。"""
    import build123d as bd
    pts, info, _, _ = outline(m, z, None)
    face = bd.Face(bd.Wire.make_polygon([bd.Vector(float(x), float(y), 0) for x, y in pts], close=True))
    body = bd.extrude(face, amount=b / 2, both=True)
    if web:
        t_web, d_rim_in = web
        ring = bd.Cylinder(d_rim_in / 2, b) - bd.Cylinder(d_rim_in / 2, t_web)
        body = body - ring
    if hub:
        D_h, L_h = hub
        body = body + bd.Cylinder(D_h / 2, L_h)
    body = body - bd.Cylinder(bore / 2, (hub[1] if hub else b) + 2)
    if key:
        w, depth = key
        L_k = (hub[1] if hub else b) + 2
        body = body - bd.Pos(0, depth / 2, 0) * bd.Box(w, depth, L_k)        # 槽底离孔心 depth（= 孔径 + t2 − 孔半径）
    return body, info


def gear_drawing(*, item, title, material, rev, m, z, b, da, d, df, bore, bore_tol, key_w, key_depth_total, hub=None, web=None,
                 params, tech, plant="问渠减速器厂（示例设计）"):
    """齿轮零件图（SVG）：轴向全剖视（轮缘、辐板、轮毂、孔与键槽）+ 啮合参数表 + 技术要求 + 标题栏。
    hub=(毂外径, 毂长)；web=(辐板厚, 轮缘内径)；params=[(名称, 值)]。"""
    import datetime as dt
    W, H = 1120, 700
    s = min(3.0, 440 / da)                      # 像素 / mm
    cx, cy = 230, 330                            # 轴线在 y = cy，图在轴线上方画上半、下半对称
    L = max(b, hub[1] if hub else b)
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Noto Sans CJK SC, Noto Sans SC, sans-serif" font-size="12">',
         '<defs><pattern id="h" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#666" stroke-width="0.7"/></pattern>'
         '<marker id="a" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 2 L10 5 L0 8 z"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#fff"/><rect x="8" y="8" width="{W - 16}" height="{H - 16}" fill="none" stroke="#000" stroke-width="1.6"/>']
    X = lambda zz: cx + zz * s  # noqa: E731
    Y = lambda r: cy - r * s    # noqa: E731
    def poly(pts, fill="url(#h)"):
        return '<polygon points="{}" fill="{}" stroke="#000" stroke-width="1.3"/>'.format(" ".join(f"{X(a):.1f},{Y(r):.1f}" for a, r in pts), fill)
    for sgn in (1, -1):
        rr = lambda r: sgn * r  # noqa: E731
        kd = key_depth_total if sgn > 0 else bore / 2           # 键槽在上半
        if web:
            tw, d_rim = web
            Lh = hub[1] if hub else b
            Dh = hub[0] if hub else d_rim
            o.append(poly([(-b / 2, rr(da / 2)), (b / 2, rr(da / 2)), (b / 2, rr(d_rim / 2)), (tw / 2, rr(d_rim / 2)), (tw / 2, rr(Dh / 2)),
                           (Lh / 2, rr(Dh / 2)), (Lh / 2, rr(kd)), (-Lh / 2, rr(kd)), (-Lh / 2, rr(Dh / 2)), (-tw / 2, rr(Dh / 2)),
                           (-tw / 2, rr(d_rim / 2)), (-b / 2, rr(d_rim / 2))]))
        else:
            o.append(poly([(-b / 2, rr(da / 2)), (b / 2, rr(da / 2)), (b / 2, rr(kd)), (-b / 2, rr(kd))]))
        # 分度圆（点划线）、齿根圆（细实线）
        o.append(f'<line x1="{X(-b / 2 - 4):.1f}" y1="{Y(rr(d / 2)):.1f}" x2="{X(b / 2 + 4):.1f}" y2="{Y(rr(d / 2)):.1f}" stroke="#000" stroke-dasharray="10 3 2 3" stroke-width="0.6"/>')
        o.append(f'<line x1="{X(-b / 2):.1f}" y1="{Y(rr(df / 2)):.1f}" x2="{X(b / 2):.1f}" y2="{Y(rr(df / 2)):.1f}" stroke="#000" stroke-width="0.6"/>')
    o.append(f'<line x1="{X(-L / 2 - 15):.1f}" y1="{cy}" x2="{X(L / 2 + 15):.1f}" y2="{cy}" stroke="#000" stroke-dasharray="14 3 2 3" stroke-width="0.6"/>')
    # 尺寸
    xr = X(max(b, L) / 2) + 46
    for k, (dia, lab) in enumerate([(da, f"Ø{da:g} h11"), (bore, f"Ø{bore:g} {bore_tol}")] + ([(hub[0], f"Ø{hub[0]:g}")] if hub else [])):
        x = xr + k * 64
        o.append(f'<line x1="{x}" y1="{Y(dia / 2):.1f}" x2="{x}" y2="{Y(-dia / 2):.1f}" stroke="#000" stroke-width="0.6" marker-start="url(#a)" marker-end="url(#a)"/>'
                 f'<text x="{x + 4}" y="{cy - 6}" font-size="11" transform="rotate(-90 {x + 4} {cy - 6})">{lab}</text>')
    yb = Y(-da / 2) + 30
    o.append(f'<line x1="{X(-b / 2):.1f}" y1="{yb:.1f}" x2="{X(b / 2):.1f}" y2="{yb:.1f}" stroke="#000" stroke-width="0.6" marker-start="url(#a)" marker-end="url(#a)"/>'
             f'<text x="{X(0):.1f}" y="{yb - 4:.1f}" text-anchor="middle" font-size="11">{b:g}（齿宽）</text>')
    if hub:
        yb2 = yb + 26
        o.append(f'<line x1="{X(-hub[1] / 2):.1f}" y1="{yb2:.1f}" x2="{X(hub[1] / 2):.1f}" y2="{yb2:.1f}" stroke="#000" stroke-width="0.6" marker-start="url(#a)" marker-end="url(#a)"/>'
                 f'<text x="{X(0):.1f}" y="{yb2 - 4:.1f}" text-anchor="middle" font-size="11">{hub[1]:g}（轮毂）</text>')
    o.append(f'<text x="{X(-L / 2) - 8:.1f}" y="{Y(key_depth_total) + 4:.1f}" text-anchor="end" font-size="10.5">键槽 {key_w:g} JS9</text>'
             f'<text x="{X(-L / 2) - 8:.1f}" y="{Y(key_depth_total) + 18:.1f}" text-anchor="end" font-size="10.5">孔径 + t₂ = {bore / 2 + key_depth_total:g}</text>')
    # 参数表（右上）
    tx, ty, cw = 660, 150, 200
    o.append(f'<text x="{tx}" y="{ty - 8}" font-size="13" font-weight="bold">啮合参数</text>')
    for i, (k, v) in enumerate(params):
        y = ty + i * 22
        o.append(f'<rect x="{tx}" y="{y}" width="{cw}" height="22" fill="none" stroke="#000" stroke-width="0.6"/>'
                 f'<rect x="{tx + cw}" y="{y}" width="200" height="22" fill="none" stroke="#000" stroke-width="0.6"/>'
                 f'<text x="{tx + 6}" y="{y + 15}" font-size="11">{k}</text><text x="{tx + cw + 6}" y="{y + 15}" font-size="11">{v}</text>')
    ty2 = ty + len(params) * 22 + 34
    o.append(f'<text x="{tx}" y="{ty2}" font-size="13" font-weight="bold">技术要求</text>')
    for i, line in enumerate(tech):
        o.append(f'<text x="{tx}" y="{ty2 + 20 + i * 18}" font-size="11.5">{i + 1}. {line}</text>')
    bx, by, bw, bh = W - 430, H - 112, 410, 92
    o.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="none" stroke="#000" stroke-width="1.2"/>')
    rows = [("名称", title), ("图号 / 物料", item), ("版本", rev), ("材料", material), ("单位", plant), ("日期", dt.date.today().isoformat()),
            ("比例", f"{s:.2g} 像素 / mm"), ("生成", "tools/cases")]
    for i, (k, v) in enumerate(rows):
        x0, y0 = bx + (i % 2) * bw / 2, by + (i // 2) * bh / 4
        o.append(f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{bw / 2:.0f}" height="{bh / 4:.0f}" fill="none" stroke="#000" stroke-width="0.5"/>'
                 f'<text x="{x0 + 6:.0f}" y="{y0 + 16:.0f}" font-size="11">{k}：{v}</text>')
    o.append("</svg>")
    return "\n".join(o)
