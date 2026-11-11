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
        if hole and r <= R_SOLID + 1e-6:
            adds.append(Part.makeCylinder(r + 0.02, L + 0.2, p0 - ax * 0.1, ax))
            log["filled_holes"] += 1
        elif f.hashCode() in mf_ids and hole:
            adds.append(Part.makeCylinder(r + 0.02, L, p0, ax).cut(Part.makeCylinder(r - A_BORE, L + 2, p0 - ax, ax)))
            log["bores"].append(dict(d=round(2 * r, 2), allowance=A_BORE, at=[round(x, 1) for x in p0]))
        elif f.hashCode() in mf_ids and not hole:
            adds.append(Part.makeCylinder(r + A_BORE, L, p0, ax).cut(Part.makeCylinder(r - 0.02, L + 2, p0 - ax, ax)))
            log["bores"].append(dict(d=round(2 * r, 2), allowance=A_BORE, outer=True, at=[round(x, 1) for x in p0]))
    elif name == "Plane" and f.hashCode() in mf_ids:
        n = face_normal(f)
        a = A_TOP if n.dot(UP) > 0.7 else A_SIDE
        try:
            adds.append(f.extrude(n * a))
            log["pads"].append(dict(area_cm2=round(f.Area / 100, 1), normal=[round(x, 2) for x in n], allowance=a))
        except Exception as e:  # noqa: BLE001
            print("pad 失败", e)

blank = part
for i in range(0, len(adds), 25):                       # 分批合并，OCC 一次合太多会慢
    blank = blank.fuse(Part.makeCompound(adds[i:i + 25]) if len(adds[i:i + 25]) > 1 else adds[i])
blank = blank.removeSplitter()
if len(blank.Solids) == 1:
    blank = blank.Solids[0]
log.update(part=PART, valid=blank.isValid(), mass_part_kg=round(part.Volume * RHO, 2), mass_blank_kg=round(blank.Volume * RHO, 2),
           allowance=dict(side=A_SIDE, top=A_TOP, bore_radial=A_BORE, solid_holes_r_max=R_SOLID),
           bbox=[round(x, 1) for x in (blank.BoundBox.XMin, blank.BoundBox.YMin, blank.BoundBox.ZMin,
                                        blank.BoundBox.XMax, blank.BoundBox.YMax, blank.BoundBox.ZMax)])
blank.exportStep(os.path.join(OUT, f"blank_{PART}.step"))
import MeshPart  # noqa: E402
MeshPart.meshFromShape(Shape=blank, LinearDeflection=0.1, AngularDeflection=0.3).write(os.path.join(OUT, f"blank_{PART}.stl"))
json.dump(log, open(os.path.join(OUT, f"blank_{PART}.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in log.items() if k not in ("pads", "bores")}, ensure_ascii=False))
