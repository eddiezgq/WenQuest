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


def parts3d(params=None, phi=0.0):
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
def to_step(params=None, phi=0.0):
    try:
        import build123d as bd
    except Exception:
        return None
    import os
    import tempfile
    model = parts3d(params, phi)
    solids = []
    for d in model["parts"]:
        s = _bd_solid(bd, d)
        if s is not None:
            s.label = d["name"]
            solids.append(s)
    comp = bd.Compound(children=solids, label="WenQuest-Lockstitch")
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
    if d["type"] == "plate":
        pts = outline(d["circles"])
        face = bd.Face(bd.Wire.make_polygon([(x, d["y0"], z) for x, z in pts], close=True))
        sol = bd.Solid.extrude(face, bd.Vector(0, d["t"], 0))
        for hx, hz, hr in d["holes"]:
            hole = bd.Solid.make_cylinder(hr, d["t"] + 2, bd.Plane(origin=(hx, d["y0"] - 1, hz), z_dir=(0, 1, 0)))
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
        else:
            pts = outline(d["circles"])
            poly = Part.makePolygon([V(x, d["y0"], z) for x, z in pts] + [V(pts[0][0], d["y0"], pts[0][1])])
            sh = Part.Face(poly).extrude(V(0, d["t"], 0))
            for hx, hz, hr in d["holes"]:
                sh = sh.cut(Part.makeCylinder(hr, d["t"] + 2, V(hx, d["y0"] - 1, hz), V(0, 1, 0)))
        res.append((d["name"], d["zh"], sh, tuple(d["color"])))
    return res


def freecad_macro(params=None, phi=0.0):
    """独立的 FreeCAD 宏：不用装工作台，打开 FreeCAD → 宏 → 执行，就生成这一组参数的机构零件（可再存成 FCStd、导出 STEP）。"""
    import inspect
    model = parts3d(params, phi)
    src = "\n".join([
        "# -*- coding: utf-8 -*-",
        "# 问渠缝纫机设计软件导出的 FreeCAD 宏（平缝机机构零件）。FreeCAD：宏 → 宏… → 执行。",
        "import math",
        "import FreeCAD as App",
        "import Part",
        "DEG = math.pi / 180",
        inspect.getsource(_hull), inspect.getsource(outline),
        "MODEL = " + json.dumps(model, ensure_ascii=False),
        inspect.getsource(freecad_shapes).replace("    import FreeCAD as App\n    import Part\n", ""),
        "doc = App.newDocument('WenQuestLockstitch')",
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
FLAT = ("NeedleCrank", "ConnectingRod", "TakeupCrank", "TakeupLever", "TakeupRocker", "LiftEccentric", "FeedEccentric", "RotaryHook")


def to_dxf(params=None):
    model = parts3d(params, 0.0)
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
        for i in range(len(pts)):
            (ax, az), (bx, bz) = pts[i], pts[(i + 1) % len(pts)]
            ents += ["0", "LINE", "8", lay, "10", f"{ax + sx:.4f}", "20", f"{az + sz:.4f}", "11", f"{bx + sx:.4f}", "21", f"{bz + sz:.4f}"]
        for hx, hz, hr in d["holes"]:
            ents += ["0", "CIRCLE", "8", lay, "10", f"{hx + sx:.4f}", "20", f"{hz + sz:.4f}", "40", f"{hr:.4f}"]
        ents += ["0", "TEXT", "8", lay, "10", f"{x0:.2f}", "20", f"{-8:.2f}", "40", "3", "1", f"{d['name']} t={d['t']:g}"]
        x0 += (maxx - minx) + 15
    body = ["0", "SECTION", "2", "HEADER", "9", "$INSUNITS", "70", "4", "0", "ENDSEC", "0", "SECTION", "2", "ENTITIES"] + ents + ["0", "ENDSEC", "0", "EOF"]
    return ("\n".join(body) + "\n").encode("ascii")
