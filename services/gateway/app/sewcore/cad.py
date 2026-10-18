# -*- coding: utf-8 -*-
"""平缝机机构的参数化三维模型（第 39 轮）。

先算出一份“中性零件清单”（每个零件是圆柱、方块或“若干圆的凸包拉伸板”），再由三个出口照它生成：
  - to_step()：服务器用 build123d 出 STEP（没装 build123d 返回 None，同数字工厂设计台的做法）；
  - freecad_build()：FreeCAD 里用 Part 模块生成（工作台、宏都调它），所以网页导出与 FreeCAD 里看到的是同一套零件；
  - to_dxf()：平板零件（曲柄、连杆、挑线杆、摇杆、偏心轮）的轮廓，给数控下料/线切割。
坐标（FreeCAD 习惯）：原点 = 上轴中心，X 向右（机头方向）、Z 向上、Y 向机身后方为负；长度 mm。
教材挑线机构的坐标（z 向右、y 向上）对应这里的 X、Z。
"""
import json
import math

from .design import clean, mech_of

DEG = math.pi / 180


def _hull(pts):
    p = sorted(set((round(x, 6), round(y, 6)) for x, y in pts))
    if len(p) < 3:
        return p

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for q in p:
        while len(lo) >= 2 and cr(lo[-2], lo[-1], q) <= 0:
            lo.pop()
        lo.append(q)
    for q in reversed(p):
        while len(up) >= 2 and cr(up[-2], up[-1], q) <= 0:
            up.pop()
        up.append(q)
    return lo[:-1] + up[:-1]


def outline(circles, seg=48):
    """若干圆 (x, z, r) 的凸包轮廓，逆时针多边形"""
    pts = []
    for x, z, r in circles:
        for i in range(seg):
            a = 2 * math.pi * i / seg
            pts.append((x + r * math.cos(a), z + r * math.sin(a)))
    return _hull(pts)


def hull_path(circles):
    """若干圆的凸包边界，逆时针：[("arc", (cx, cz), r, a0, a1)（度，a1 > a0）, ("line", (x0, z0), (x1, z1)), …]。
    先用细采样找出凸包上圆的先后次序，再按外公切线精确求切点，所以轮廓是真正的圆弧加直线（数控可直接用）。"""
    cs = [tuple(map(float, c)) for c in circles]
    if len(cs) == 1:
        (x, z, r), = cs
        return [("arc", (x, z), r, 0.0, 360.0)]
    pts, owner = [], {}
    for k, (x, z, r) in enumerate(cs):
        for i in range(720):
            a = 2 * math.pi * i / 720
            q = (round(x + r * math.cos(a), 6), round(z + r * math.sin(a), 6))
            pts.append(q)
            owner.setdefault(q, k)
    hull = _hull(pts)
    seq = []
    for q in hull:
        k = owner.get(q)
        if k is not None and (not seq or seq[-1] != k):
            seq.append(k)
    while len(seq) > 1 and seq[0] == seq[-1]:
        seq.pop()
    if len(seq) == 1:
        x, z, r = cs[seq[0]]
        return [("arc", (x, z), r, 0.0, 360.0)]
    tang = []                                   # 每段 i→j 的外公切线切点
    for a, b in zip(seq, seq[1:] + seq[:1]):
        (x1, z1, r1), (x2, z2, r2) = cs[a], cs[b]
        dx, dz = x2 - x1, z2 - z1
        L = math.hypot(dx, dz)
        ux, uz = dx / L, dz / L
        rx, rz = uz, -ux                        # 逆时针走时，外侧在右手边
        sb = max(-1.0, min(1.0, (r1 - r2) / L))
        cb = math.sqrt(1 - sb * sb)
        nx, nz = cb * rx + sb * ux, cb * rz + sb * uz
        tang.append(((x1 + r1 * nx, z1 + r1 * nz), (x2 + r2 * nx, z2 + r2 * nz)))
    out = []
    for i, k in enumerate(seq):
        x, z, r = cs[k]
        arrive = tang[i - 1][1]
        leave = tang[i][0]
        a0 = math.degrees(math.atan2(arrive[1] - z, arrive[0] - x))
        a1 = math.degrees(math.atan2(leave[1] - z, leave[0] - x))
        while a1 <= a0 + 1e-9:
            a1 += 360
        if a1 - a0 > 1e-6 and abs(a1 - a0 - 360) > 1e-6:
            out.append(("arc", (x, z), r, a0, a1))
        out.append(("line", leave, tang[i][1]))
    return out


def _frame(d):
    """平板的局部坐标：点 (a, b) → o + a·u + b·v，沿 n 拉伸 t。没写 frame 的是平缝机的老写法（XZ 平面、沿 +Y）。"""
    f = d.get("frame")
    if f:
        return tuple(f["o"]), tuple(f["u"]), tuple(f["v"]), tuple(f["n"])
    return (0.0, d["y0"], 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0), (0.0, 1.0, 0.0)


def _P(fr, a, b, h=0.0):
    o, u, v, n = fr
    return (o[0] + a * u[0] + b * v[0] + h * n[0], o[1] + a * u[1] + b * v[1] + h * n[1], o[2] + a * u[2] + b * v[2] + h * n[2])


def parts3d(params=None, phi=0.0, machine="lockstitch"):
    if machine == "overlock":
        return _parts_overlock(params, phi)
    return _parts_lockstitch(params, phi)


def _parts_lockstitch(params=None, phi=0.0):
    """主轴转角 phi 时的零件清单"""
    p = clean(params)
    M = mech_of(p)
    r, l = p["r"], p["l"]
    a = phi * DEG
    # 刺布：曲柄销在 (r sinφ, r cosφ)，针杆在 X = 0 竖直，连杆下端（针杆接头）高度 zj
    pin = (r * math.sin(a), r * math.cos(a))
    zj = r * math.cos(a) - math.sqrt(l * l - (r * math.sin(a)) ** 2)
    NB = 105.0                       # 针杆接头到针杆下端（装针处）
    NEEDLE = 38.0                    # 机针露出针夹的长度
    z_tip_tdc = (r - l) - NB - NEEDLE
    z_plate = z_tip_tdc - M.TIP0     # 针板上面
    z_tip = zj - NB - NEEDLE
    z_hook = z_plate - M.YP          # 旋梭中心（教材：针板上面高出旋梭中心 YP）
    out = []

    def plate(name, zh, circles, y0, t, holes=(), color=(0.75, 0.77, 0.80)):
        out.append(dict(type="plate", name=name, zh=zh, circles=[list(c) for c in circles], y0=y0, t=t,
                        holes=[list(h) for h in holes], color=color))

    def cyl(name, zh, rad, h, base, d, color=(0.62, 0.64, 0.68)):
        out.append(dict(type="cyl", name=name, zh=zh, r=rad, h=h, base=list(base), dir=list(d), color=color))

    def box(name, zh, size, base, color=(0.55, 0.58, 0.62)):
        out.append(dict(type="box", name=name, zh=zh, size=list(size), base=list(base), color=color))

    # 上轴、下轴
    cyl("UpperShaft", "上轴", 7, 160, (0, 4, 0), (0, -1, 0))
    # 刺布机构
    cw = max(6.0, 4 + 60 * (0.06 + p["k"] * p["mr"]))          # 平衡块半径随平衡块质量示意
    plate("NeedleCrank", "针杆曲柄", [(0, 0, 11), (pin[0], pin[1], 7), (-math.sin(a) * cw * 0.9, -math.cos(a) * cw * 0.9, cw)], 4, 8,
          holes=[(0, 0, 7)], color=(0.80, 0.55, 0.20))
    plate("ConnectingRod", "针杆连杆", [(pin[0], pin[1], 6.5), (0, zj, 5.5)], 12, 6, holes=[(pin[0], pin[1], 3.5), (0, zj, 3)],
          color=(0.85, 0.70, 0.30))
    cyl("CrankPin", "曲柄销", 3.5, 16, (pin[0], 4, pin[1]), (0, 1, 0), color=(0.5, 0.5, 0.5))
    cyl("NeedleBar", "针杆", 3.5, NB + 6, (0, 15, zj + 6), (0, 0, -1), color=(0.70, 0.72, 0.75))
    cyl("Needle", "机针", 0.45 * p["d"] / 0.9, NEEDLE, (0, 15, zj - NB), (0, 0, -1), color=(0.9, 0.9, 0.92))
    # 挑线机构（教材坐标 z→X，y→Z），装在曲柄后面的平面里
    L = M.link_pose(phi, M.LK0) or M.link_pose(0, M.LK0)
    if L:
        P, Mm, E, Q = L["P"], L["M"], L["E"], L["Q"]
        plate("TakeupCrank", "挑线曲柄", [(0, 0, 10), (P[0], P[1], 6)], -14, 6, holes=[(0, 0, 7)], color=(0.35, 0.55, 0.80))
        plate("TakeupLever", "挑线杆", [(P[0], P[1], 6), (Mm[0], Mm[1], 5), (E[0], E[1], 3.5)], -8, 5,
              holes=[(P[0], P[1], 3), (Mm[0], Mm[1], 2.5), (E[0], E[1], 1.2)], color=(0.30, 0.65, 0.85))
        plate("TakeupRocker", "挑线摇杆", [(Mm[0], Mm[1], 5), (Q[0], Q[1], 6)], -3, 4, holes=[(Mm[0], Mm[1], 2.5), (Q[0], Q[1], 3)],
              color=(0.30, 0.50, 0.70))
        cyl("RockerPivot", "摇杆支点轴", 3, 20, (Q[0], -14, Q[1]), (0, 1, 0), color=(0.5, 0.5, 0.5))
    # 钩线：旋梭（下轴转 2 倍），梭尖在主轴 phc 时到机针
    ah = 2 * (phi - M.PHC0 - p["psi"] / 2) * DEG + math.pi / 2
    tipx, tipz = 13.5 * math.cos(ah), z_hook + 13.5 * math.sin(ah)
    cyl("LowerShaft", "下轴", 6, 150, (0, -10, z_hook), (0, -1, 0))
    plate("RotaryHook", "旋梭", [(0, z_hook, 12.5), (tipx, tipz, 1.0)], -10, 9, holes=[(0, z_hook, 6)], color=(0.80, 0.80, 0.84))
    # 送布：抬牙偏心与送布偏心（装在下轴上）
    F = M.feed_model(fab=p["fab"], mode=p["mode"], s=p["s"], dT=p["dT"], dP=p["dP"], h=p["h"], P=p["P"])
    eL = 1.1
    eF = F["S"] / 2
    aL, aF = (phi - F["phL"]) * DEG, (phi - F["phF"]) * DEG
    plate("LiftEccentric", "抬牙偏心轮", [(eL * math.sin(aL), z_hook + eL * math.cos(aL), 13)], -60, 8, holes=[(0, z_hook, 6)],
          color=(0.45, 0.70, 0.45))
    plate("FeedEccentric", "送布偏心轮", [(eF * math.cos(aF), z_hook + eF * math.sin(aF), 13)], -78, 8, holes=[(0, z_hook, 6)],
          color=(0.40, 0.62, 0.40))
    # 针板与送布牙
    box("NeedlePlate", "针板", (90, 50, 2), (-45, -20, z_plate - 2), color=(0.70, 0.72, 0.74))
    dx, dy = F["X"](phi), F["Y"](phi)
    box("FeedDog", "送布牙", (16, 6, 4), (-8 - dx, 6, z_plate + dy - 4), color=(0.30, 0.30, 0.32))
    return dict(parts=out, phi=phi, z_plate=z_plate, z_hook=z_hook, z_tip=z_tip, params=p)


# ---------- 出口 1：STEP（build123d） ----------
def to_step(params=None, phi=0.0, machine="lockstitch"):
    try:
        import build123d as bd
    except Exception:
        return None
    import os
    import tempfile
    model = parts3d(params, phi, machine)
    solids = []
    for d in model["parts"]:
        s = _bd_solid(bd, d)
        if s is not None:
            s.label = d["name"]
            solids.append(s)
    comp = bd.Compound(children=solids, label="WenQuest-" + machine)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "lockstitch.step")
        bd.export_step(comp, path)
        with open(path, "rb") as f:
            return f.read()


def _bd_solid(bd, d):
    if d["type"] == "cyl":
        return bd.Solid.make_cylinder(d["r"], d["h"], bd.Plane(origin=tuple(d["base"]), z_dir=tuple(d["dir"])))
    if d["type"] == "box":
        return bd.Solid.make_box(*d["size"], bd.Plane(origin=tuple(d["base"])))
    if d["type"] == "sphere":
        return bd.Solid.make_sphere(d["r"], bd.Plane(origin=tuple(d["c"])))
    if d["type"] == "plate":
        fr = _frame(d)
        n = fr[3]
        edges = []
        for seg in hull_path(d["circles"]):
            if seg[0] == "line":
                (x0, z0), (x1, z1) = seg[1], seg[2]
                if math.hypot(x1 - x0, z1 - z0) > 1e-6:
                    edges.append(bd.Edge.make_line(_P(fr, x0, z0), _P(fr, x1, z1)))
            else:
                (cx, cz), r, a0, a1 = seg[1], seg[2], seg[3], seg[4]
                P = lambda a: _P(fr, cx + r * math.cos(math.radians(a)), cz + r * math.sin(math.radians(a)))  # noqa: E731
                if a1 - a0 >= 359.999:
                    edges.append(bd.Edge.make_circle(r, bd.Plane(origin=_P(fr, cx, cz), z_dir=n)))
                else:
                    edges.append(bd.Edge.make_three_point_arc(P(a0), P((a0 + a1) / 2), P(a1)))
        face = bd.Face(bd.Wire(edges))
        sol = bd.Solid.extrude(face, bd.Vector(n[0] * d["t"], n[1] * d["t"], n[2] * d["t"]))
        for hx, hz, hr in d["holes"]:
            hole = bd.Solid.make_cylinder(hr, d["t"] + 2, bd.Plane(origin=_P(fr, hx, hz, -1), z_dir=n))
            sol = sol - hole
        return sol
    return None


# ---------- 出口 2：FreeCAD（工作台与宏共用；在 FreeCAD 里运行） ----------
def freecad_shapes(model):
    """返回 [(name, zh, Part.Shape, color)]。只在 FreeCAD 里调用。"""
    import FreeCAD as App
    import Part
    V = App.Vector
    res = []
    for d in model["parts"]:
        if d["type"] == "cyl":
            sh = Part.makeCylinder(d["r"], d["h"], V(*d["base"]), V(*d["dir"]))
        elif d["type"] == "box":
            sh = Part.makeBox(*d["size"], V(*d["base"]))
        elif d["type"] == "sphere":
            sh = Part.makeSphere(d["r"], V(*d["c"]))
        else:
            fr = _frame(d)
            n = V(*fr[3])
            edges = []
            for seg in hull_path(d["circles"]):
                if seg[0] == "line":
                    (x0, z0), (x1, z1) = seg[1], seg[2]
                    if math.hypot(x1 - x0, z1 - z0) > 1e-6:
                        edges.append(Part.LineSegment(V(*_P(fr, x0, z0)), V(*_P(fr, x1, z1))).toShape())
                else:
                    (cx, cz), r, a0, a1 = seg[1], seg[2], seg[3], seg[4]
                    if a1 - a0 >= 359.999:
                        edges.append(Part.makeCircle(r, V(*_P(fr, cx, cz)), n))
                    else:
                        P = lambda a: V(*_P(fr, cx + r * math.cos(math.radians(a)), cz + r * math.sin(math.radians(a))))  # noqa: E731
                        edges.append(Part.Arc(P(a0), P((a0 + a1) / 2), P(a1)).toShape())
            sh = Part.Face(Part.Wire(Part.__sortEdges__(edges))).extrude(n * d["t"])
            for hx, hz, hr in d["holes"]:
                sh = sh.cut(Part.makeCylinder(hr, d["t"] + 2, V(*_P(fr, hx, hz, -1)), n))
        res.append((d["name"], d["zh"], sh, tuple(d["color"])))
    return res


def freecad_macro(params=None, phi=0.0, machine="lockstitch"):
    """独立的 FreeCAD 宏：不用装工作台，打开 FreeCAD → 宏 → 执行，就生成这一组参数的机构零件（可再存成 FCStd、导出 STEP）。"""
    import inspect
    model = parts3d(params, phi, machine)
    src = "\n".join([
        "# -*- coding: utf-8 -*-",
        "# 问渠缝纫机设计软件导出的 FreeCAD 宏（{}机构零件）。FreeCAD：宏 → 宏… → 执行。".format({"overlock": "包缝机"}.get(machine, "平缝机")),
        "import math",
        "import FreeCAD as App",
        "import Part",
        "DEG = math.pi / 180",
        inspect.getsource(_hull), inspect.getsource(outline), inspect.getsource(hull_path), inspect.getsource(_frame), inspect.getsource(_P),
        "MODEL = " + json.dumps(model, ensure_ascii=False),
        inspect.getsource(freecad_shapes).replace("    import FreeCAD as App\n    import Part\n", ""),
        "doc = App.newDocument('WenQuest_{}')".format(machine),
        "for name, zh, sh, color in freecad_shapes(MODEL):",
        "    o = doc.addObject('Part::Feature', name)",
        "    o.Label = zh",
        "    o.Shape = sh",
        "    try:",
        "        o.ViewObject.ShapeColor = color",
        "    except Exception:",
        "        pass",
        "doc.recompute()",
        "try:",
        "    import FreeCADGui",
        "    FreeCADGui.SendMsgToActiveView('ViewFit')",
        "    FreeCADGui.activeDocument().activeView().viewIsometric()",
        "except Exception:",
        "    pass",
        "",
    ])
    return src


# ---------- 出口 3：DXF（平板零件轮廓，R12 格式，单位 mm） ----------
FLAT = ("NeedleCrank", "ConnectingRod", "TakeupCrank", "TakeupLever", "TakeupRocker", "LiftEccentric", "FeedEccentric", "RotaryHook",
        "OL_NeedleCrank", "OL_NeedleRod", "LL_Eccentric", "LL_Rocker", "LL_Looper", "UL_Eccentric", "UL_Rocker", "FeedArmMain", "FeedArmDiff")


def to_dxf(params=None, machine="lockstitch"):
    model = parts3d(params, 0.0, machine)
    ents, x0 = [], 0.0
    for d in model["parts"]:
        if d["type"] != "plate" or d["name"] not in FLAT:
            continue
        pts = outline(d["circles"], seg=96)
        minx = min(x for x, _ in pts)
        maxx = max(x for x, _ in pts)
        minz = min(z for _, z in pts)
        sx, sz = x0 - minx, -minz
        lay = d["name"]
        for seg in hull_path(d["circles"]):
            if seg[0] == "line":
                (ax, az), (bx, bz) = seg[1], seg[2]
                ents += ["0", "LINE", "8", lay, "10", f"{ax + sx:.4f}", "20", f"{az + sz:.4f}", "11", f"{bx + sx:.4f}", "21", f"{bz + sz:.4f}"]
            elif seg[4] - seg[3] >= 359.999:
                ents += ["0", "CIRCLE", "8", lay, "10", f"{seg[1][0] + sx:.4f}", "20", f"{seg[1][1] + sz:.4f}", "40", f"{seg[2]:.4f}"]
            else:
                ents += ["0", "ARC", "8", lay, "10", f"{seg[1][0] + sx:.4f}", "20", f"{seg[1][1] + sz:.4f}", "40", f"{seg[2]:.4f}",
                         "50", f"{seg[3] % 360:.4f}", "51", f"{seg[4] % 360:.4f}"]
        for hx, hz, hr in d["holes"]:
            ents += ["0", "CIRCLE", "8", lay, "10", f"{hx + sx:.4f}", "20", f"{hz + sz:.4f}", "40", f"{hr:.4f}"]
        ents += ["0", "TEXT", "8", lay, "10", f"{x0:.2f}", "20", f"{-8:.2f}", "40", "3", "1", f"{d['name']} t={d['t']:g}"]
        x0 += max(maxx - minx, 2.1 * len(d["name"]) + 10) + 15
    body = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"] + ents + ["0", "ENDSEC", "0", "EOF"]
    return ("\n".join(body) + "\n").encode("ascii")


# ---------- 包缝机（第 40 轮）：教材坐标（x 沿主轴，z 向上，y 前后），与 overlock.py 的 RSSR 同一套 ----------
def _parts_overlock(params=None, phi=0.0):
    from . import overlock as O
    p = O.clean(params)
    out = []

    def plate(name, zh, circles, frame, t, holes=(), color=(0.75, 0.77, 0.80)):
        out.append(dict(type="plate", name=name, zh=zh, circles=[list(c) for c in circles], frame=frame, t=t,
                        holes=[list(h) for h in holes], color=color))

    def cyl(name, zh, rad, h, base, d, color=(0.62, 0.64, 0.68)):
        out.append(dict(type="cyl", name=name, zh=zh, r=rad, h=h, base=list(base), dir=list(d), color=color))

    def rod(name, zh, a, b, rad, color):
        d = [b[i] - a[i] for i in range(3)]
        L = math.sqrt(sum(x * x for x in d))
        cyl(name, zh, rad, L, a, [x / L for x in d], color)

    def sphere(name, zh, c, rad, color=(0.5, 0.5, 0.52)):
        out.append(dict(type="sphere", name=name, zh=zh, c=list(c), r=rad, color=color))

    def yz(x0):                      # 垂直于主轴的平面，局部坐标就是 (y, z)
        return dict(o=[x0, 0, 0], u=[0, 1, 0], v=[0, 0, 1], n=[1, 0, 0])

    Cy, Cz = O.M0[1], O.M0[2]
    cyl("OL_MainShaft", "主轴", 6, 120, (-45, Cy, Cz), (1, 0, 0))
    # 斜向引针（机头里的上轴驱动）：曲柄、连杆、针杆在 x = −35 的平面里，针杆沿 20° 斜线向下
    Cy, Cz = O.M0[1], O.M0[2] + 110
    cyl("OL_UpperShaft", "上轴（引针）", 6, 30, (-45, Cy, Cz), (1, 0, 0))
    a = phi * DEG
    en = (0.0, math.sin(O.INCLINE * DEG), math.cos(O.INCLINE * DEG))
    w = (0.0, en[2], -en[1])
    r, l = p["r"], p["l"]
    pin = (Cy + r * (math.cos(a) * en[1] + math.sin(a) * w[1]), Cz + r * (math.cos(a) * en[2] + math.sin(a) * w[2]))
    s = r * math.cos(a) - math.sqrt(l * l - (r * math.sin(a)) ** 2)
    jn = (Cy + s * en[1], Cz + s * en[2])
    plate("OL_NeedleCrank", "引针曲柄", [(Cy, Cz, 10), (pin[0], pin[1], 6)], yz(-38), 6, holes=[(Cy, Cz, 6)], color=(0.80, 0.55, 0.20))
    plate("OL_NeedleRod", "引针连杆", [(pin[0], pin[1], 5.5), (jn[0], jn[1], 4.5)], yz(-32), 5, holes=[(pin[0], pin[1], 3), (jn[0], jn[1], 2.5)],
          color=(0.85, 0.70, 0.30))
    cyl("OL_NeedleBar", "针杆", 3.5, 70, (-29.5, jn[0], jn[1]), (0, -en[1], -en[2]), color=(0.70, 0.72, 0.75))
    Cy, Cz = O.M0[1], O.M0[2]
    # 两套 RSSR
    for tag, pre, rr_, bb, cc, zh, col in (("LL", O.LL, p["ll_r"], p["ll_b"], p["ll_c"], "下弯针", (0.35, 0.55, 0.80)),
                                           ("UL", O.UL, p["ul_r"], p["ul_b"], p["ul_c"], "上弯针", (0.55, 0.40, 0.75))):
        P = O.rssr_pose(rr_, bb, cc, pre, phi) or O.rssr_pose(rr_, bb, cc, pre, 0)
        if not P:
            continue
        A, B, Q, C, e, v0, v1, th = P["A"], P["B"], P["Q"], P["C"], P["e"], P["v0"], P["v1"], P["th"]
        plate(f"{tag}_Eccentric", f"{zh}偏心轮", [(A[1], A[2], rr_ + 9)], yz(C[0] - 4), 8, holes=[(C[1], C[2], 6)], color=(0.45, 0.70, 0.45))
        sphere(f"{tag}_BallA", f"{zh}连杆球头（偏心端）", A, 3.2)
        sphere(f"{tag}_BallB", f"{zh}连杆球头（摆杆端）", B, 3.2)
        rod(f"{tag}_Link", f"{zh}球头连杆", A, B, 2.2, col)
        fr = dict(o=[Q[i] - 2 * e[i] for i in range(3)], u=list(v0), v=list(v1), n=list(e))
        plate(f"{tag}_Rocker", f"{zh}摆杆", [(0, 0, 6), (cc * math.cos(th), cc * math.sin(th), 4)], fr, 4, holes=[(0, 0, 3)], color=col)
        cyl(f"{tag}_Shaft", f"{zh}摆轴", 3, 55 if tag == "LL" else 35, [Q[i] - 8 * e[i] for i in range(3)], e)
        if tag == "LL":
            top = [Q[i] + 44 * e[i] for i in range(3)]
            fr2 = dict(o=top, u=list(v0), v=list(v1), n=list(e))
            R = p["ll_R"]
            plate("LL_Looper", "下弯针", [(0, 0, 6), (R * math.cos(th + math.pi), R * math.sin(th + math.pi), 1.2)], fr2, 2,
                  holes=[(0, 0, 3)], color=(0.85, 0.85, 0.88))
    # 差动送布：主送布臂与差动臂同摆，摆角幅值 = 针距 / 主臂长
    fy, fz = Cy - 25, Cz + 30
    al = (p["s"] / p["lm"]) / 2 * math.cos(a)
    for nm, zh, L_, x0 in (("FeedArmMain", "主送布臂", p["lm"], 30), ("FeedArmDiff", "差动送布臂", p["D"] * p["lm"], 40)):
        plate(nm, zh, [(fy, fz, 5), (fy + L_ * math.sin(al), fz + L_ * math.cos(al), 3)], yz(x0), 4, holes=[(fy, fz, 2.5)],
              color=(0.40, 0.62, 0.40))
    cyl("FeedShaft", "送布摆轴", 2.5, 25, (25, fy, fz), (1, 0, 0))
    # 切刀：上刀在 kn_ph 时最低（越过下刀 kn_ov）
    zk = Cz + 55
    up = 3 * (1 - math.cos((phi - p["kn_ph"]) * DEG)) - p["kn_ov"]
    out.append(dict(type="box", name="LowerKnife", zh="下刀", size=[8, 3, 10], base=[-4, Cy + p["w"] + 6, zk - 10], color=(0.6, 0.6, 0.65)))
    out.append(dict(type="box", name="UpperKnife", zh="上刀", size=[8, 3, 14], base=[-4, Cy + p["w"] + 9, zk + up], color=(0.5, 0.5, 0.55)))
    return dict(parts=out, phi=phi, params=p)
