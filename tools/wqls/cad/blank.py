"""WQ-LS 机壳铸件毛坯（第 138 轮 G5.1）：由机加工零件（housing_upper/lower.step）倒推出铸件毛坯。在 FreeCAD 里运行：

    WQ_PART=upper WQ_SRC=<housing 目录> WQ_OUT=<输出目录> freecadcmd -c "exec(open('tools/wqls/cad/blank.py').read())"

做法（砂型灰铸铁的通常做法）：
  ① 不铸出的孔：半径 ≤ 10 mm 的孔（螺孔、销孔、针杆孔 Ø12、锪孔、过线小孔）铸成实心，全部由机加工钻出；
  ② 加工面加余量：平面朝铸型下面和侧面的加 3 mm，朝上（浇注位置的上表面，夹渣、气孔多）的加 4 mm；
  ③ 铸出的加工孔（轴承孔 Ø35、Ø32 等）单边留 2.5 mm；电机止口外圆 Ø52 单边加 2.5 mm。
浇注位置：上件分型面 y = 0，后面（+y）朝上；下件分型面在机座顶面，整件在下型、开口朝下（内腔由下型自带砂芯形成，不用芯子），+z 朝上。
输出：blank_<part>.step / .stl，blank_<part>.json（余量清单、填实的孔、毛坯重量）。
"""
import json
import os

import FreeCAD as App
import Part

V = App.Vector
ROOT = os.getcwd()
PART = os.environ.get("WQ_PART", "upper")
SRC = os.environ["WQ_SRC"]
OUT = os.environ.get("WQ_OUT", SRC)
os.makedirs(OUT, exist_ok=True)
UP = {"upper": V(0, 1, 0), "lower": V(0, 0, 1)}[PART]        # 浇注位置的“上”
A_SIDE, A_TOP, A_BORE, R_SOLID = 3.0, 4.0, 2.5, 10.0
RHO = 7.2e-6                                                   # HT250 kg/mm³

os.environ["WQ_NOMAIN"] = "1"
exec(open(os.path.join(ROOT, "tools/wqls/cad/housing.py")).read())   # 拿 machined_faces 和尺寸常数（不建模）

part = Part.read(os.path.join(SRC, f"housing_{PART}.step"))
part = part.Solids[0] if len(part.Solids) == 1 else part
mfaces = machined_faces(part)
mf_ids = {f.hashCode() for f in mfaces}


def face_normal(f):
    u0, u1, v0, v1 = f.ParameterRange
    return f.normalAt((u0 + u1) / 2, (v0 + v1) / 2)


def cyl_extent(f):
    """圆柱面的轴线、半径、轴向范围（沿轴的起点和长度）、是不是孔（法向指向轴线）"""
    s = f.Surface
    ax = V(s.Axis).normalize()
    c = V(s.Center)
    ts = [(v.Point - c).dot(ax) for v in f.Vertexes] or [0.0]
    bb = f.BoundBox
    pts = [V(bb.XMin, bb.YMin, bb.ZMin), V(bb.XMax, bb.YMax, bb.ZMax)]
    ts += [(p - c).dot(ax) for p in pts]
    t0, t1 = min(ts), max(ts)
    u0, u1, v0, v1 = f.ParameterRange
    p = f.valueAt((u0 + u1) / 2, (v0 + v1) / 2)
    n = f.normalAt((u0 + u1) / 2, (v0 + v1) / 2)
    radial = p - (c + ax * (p - c).dot(ax))
    hole = n.dot(radial) < 0
    return c + ax * t0, ax, s.Radius, t1 - t0, hole


adds, cuts, log = [], [], dict(filled_holes=0, pads=[], bores=[])
for f in part.Faces:
    name = type(f.Surface).__name__
    if name == "Cylinder":
        p0, ax, r, L, hole = cyl_extent(f)
        u0_, u1_, _, _ = f.ParameterRange
        if L < 0.05 or (u1_ - u0_) < 3.0:                # 只认完整的孔和外圆（OCC 把圆柱面分成两半，各 180°）；内外圆角面（90°）不算
            continue
        shaft_pass = PART == "upper" and abs(r - 10.0) < 0.05 and abs(ax.x) > 0.99 and abs(p0.y) < 0.5 and abs(p0.z - 200) < 0.5
        hook_bore = PART == "lower" and abs(r - 7.0) < 0.05 and abs(ax.x) > 0.99 and abs(p0.y) < 0.5 and abs(p0.z + 21.5) < 0.5
        feed_axes = json.load(open(os.path.join(ROOT, "docs/设计/WQ-LS/G4/送布机构.json"), encoding="utf-8"))["geo"] if PART == "lower" else {}
        feed_bore = None
        if PART == "lower" and abs(ax.x) > 0.99:
            for k_ in ("Fr", "Lr", "G"):
                if abs(p0.y - feed_axes[k_][0]) < 0.5 and abs(p0.z - feed_axes[k_][1]) < 0.5:
                    feed_bore = k_
        if hole and feed_bore:
            # G4.6 送布摆轴、抬牙摆轴、调节器轴的孔和端壁工艺孔都用砂芯铸出（否则凸台成了实心热节）：
            # 抬牙摆轴前孔 Ø16 铸出 Ø15（后孔的 Ø14 镗刀要从这里穿过去），调节器孔 Ø10 铸出 Ø6，其余比成品小 3
            dc = 15.0 if (feed_bore == "Lr" and abs(r - 8.0) < 0.05 and p0.x > 0) else (6.0 if (feed_bore == "G" and abs(r - 5.0) < 0.05) else 2 * r - 3.0)
            adds.append(Part.makeCylinder(r + 0.4, L + 0.2, p0 - ax * 0.1, ax).cut(Part.makeCylinder(dc / 2, L + 2, p0 - ax, ax)))
            log["bores"].append(dict(d=round(2 * r, 1), cast_d=dc, at=[round(x, 1) for x in p0], feed=feed_bore))
        elif hole and hook_bore:
            # G4.5 旋梭轴孔 Ø14：铸出 Ø9（砂芯），否则 Ø28 的座成了实心，凝固仿真里是热节（加冷铁也去不掉）
            adds.append(Part.makeCylinder(r + 0.4, L + 0.2, p0 - ax * 0.1, ax).cut(Part.makeCylinder(4.5, L + 2, p0 - ax, ax)))
            log["bores"].append(dict(d=14.0, cast_d=9.0, at=[round(x, 1) for x in p0]))
        elif hole and shaft_pass:
            # 电机座的轴过孔 Ø20：铸出 Ø16（与 6201 座孔 Ø27 一起由立柱内腔砂芯伸出的台阶芯头形成），
            # 否则 6201 座孔会成为封闭在铸件里的环形空腔，造不出型，也镗不到
            adds.append(Part.makeCylinder(r + 0.4, L + 0.2, p0 - ax * 0.1, ax).cut(Part.makeCylinder(8.0, L + 2, p0 - ax, ax)))
            log["bores"].append(dict(d=20.0, cast_d=16.0, at=[round(x, 1) for x in p0]))
        elif hole and r <= R_SOLID + 1e-6:
            adds.append(Part.makeCylinder(r + 0.4, L + 0.2, p0 - ax * 0.1, ax))     # 比孔大 0.4：与孔壁重叠，布尔运算不碰共面
            log["filled_holes"] += 1
        elif f.hashCode() in mf_ids and hole:
            adds.append(Part.makeCylinder(r + 0.4, L, p0, ax).cut(Part.makeCylinder(r - A_BORE, L + 2, p0 - ax, ax)))
            log["bores"].append(dict(d=round(2 * r, 2), allowance=A_BORE, at=[round(x, 1) for x in p0]))
        elif f.hashCode() in mf_ids and not hole:
            adds.append(Part.makeCylinder(r + A_BORE, L, p0, ax).cut(Part.makeCylinder(r - 0.4, L + 2, p0 - ax, ax)))
            log["bores"].append(dict(d=round(2 * r, 2), allowance=A_BORE, outer=True, at=[round(x, 1) for x in p0]))
    elif name == "Plane" and f.hashCode() in mf_ids:
        n = face_normal(f)
        a = A_TOP if n.dot(UP) > 0.7 else A_SIDE
        try:
            adds.append(f.extrude(n * a))
            log["pads"].append(dict(area_cm2=round(f.Area / 100, 1), normal=[round(x, 2) for x in n], allowance=a))
        except Exception as e:  # noqa: BLE001
            print("pad 失败", e)

# 逐个合并，每一步核对体积不减少（OCC 的布尔运算偶尔会丢掉一块实体：第一版就把前轴承座圈丢了，凝固仿真因此漏看了那里）
blank = part
for a_ in adds:
    v0 = blank.Volume
    nb = blank.fuse(a_)
    if nb.Volume < v0 - 1.0:
        nb = blank.fuse(a_, 0.01)                    # 模糊布尔
    if nb.Volume < v0 - 1.0:
        print("合并后体积减少，跳过这一块", round(v0 - nb.Volume, 1))
        continue
    blank = nb
blank = blank.removeSplitter()
if len(blank.Solids) == 1:
    blank = blank.Solids[0]
lost = part.cut(blank).Volume                        # 零件上有、毛坯上没有的材料，必须接近 0
log["part_outside_blank_mm3"] = round(lost, 1)
if lost > 50:
    raise SystemExit(f"毛坯没有包住零件：差 {lost:.0f} mm³")
log.update(part=PART, valid=blank.isValid(), mass_part_kg=round(part.Volume * RHO, 2), mass_blank_kg=round(blank.Volume * RHO, 2),
           allowance=dict(side=A_SIDE, top=A_TOP, bore_radial=A_BORE, solid_holes_r_max=R_SOLID),
           bbox=[round(x, 1) for x in (blank.BoundBox.XMin, blank.BoundBox.YMin, blank.BoundBox.ZMin,
                                        blank.BoundBox.XMax, blank.BoundBox.YMax, blank.BoundBox.ZMax)])
blank.exportStep(os.path.join(OUT, f"blank_{PART}.step"))
import MeshPart  # noqa: E402
MeshPart.meshFromShape(Shape=blank, LinearDeflection=0.1, AngularDeflection=0.3).write(os.path.join(OUT, f"blank_{PART}.stl"))
json.dump(log, open(os.path.join(OUT, f"blank_{PART}.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in log.items() if k not in ("pads", "bores")}, ensure_ascii=False))
