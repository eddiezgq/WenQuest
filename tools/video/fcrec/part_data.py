"""从 WQ-LS 整机的真零件（STEP）取课程用的数据：尺寸 + 三维网格（网页里转着看）。

    WQLS_TE=… freecadcmd part_data.py     → docs/帮助/问渠CAD帮助/parts.json
"""
import json
import os

import Part

D = os.environ["WQLS_TE"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "docs", "帮助", "问渠CAD帮助", "parts.json")


def mesh(shape, tol=0.03):
    v, f = shape.tessellate(tol)
    c = shape.BoundBox.Center
    return {"v": [round(x, 3) for p in v for x in (p.x - c.x, p.y - c.y, p.z - c.z)], "f": [i for t in f for i in t]}


def cyl(shape):
    return sorted({round(f.Surface.Radius, 3) for f in shape.Faces if f.Surface.TypeId == "Part::GeomCylinder"})


out = {}
s = Part.read(f"{D}/presser_collar.step")
b = s.BoundBox
out["presser_collar"] = {"name": "压脚杆套环", "od": round(2 * max(cyl(s)), 3), "id": round(2 * min(cyl(s)), 3), "t": round(b.ZLength, 3),
                         "volume": round(s.Volume, 2), "mesh": mesh(s)}
s = Part.read(f"{D}/needle_clamp.step")
b = s.BoundBox
r = cyl(s)
out["needle_clamp"] = {"name": "针夹", "R": 5.5 if 5.5 in r else max(r), "bore": 8.0 if 4.0 in r else None,
                       "tab_w": round(b.XLength if b.XLength < 11 else 7.0, 3), "tab_d": round(-b.YMin, 3), "t": round(b.ZLength, 3),
                       "holes": [x for x in r if x < 2], "volume": round(s.Volume, 2), "mesh": mesh(s)}
# 针夹耳朵宽：看平面 x=±3.5
xs = sorted({round(f.Surface.Position.x, 3) for f in s.Faces if f.Surface.TypeId == "Part::GeomPlane" and abs(abs(f.Surface.Axis.x) - 1) < 1e-6})
out["needle_clamp"]["tab_w"] = round(xs[-1] - xs[0], 3)
s = Part.read(f"{D}/needle_bar.step")
out["needle_bar"] = {"name": "针杆", "volume": round(s.Volume, 2)}       # 第 2 课：导出 STEP 再导入，体积对得上
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("OK", json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "mesh"} for k, v in out.items()}), os.path.getsize(OUT))
