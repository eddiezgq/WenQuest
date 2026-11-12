"""WQ-LS G4.5 旋梭组剖视：用过旋梭轴、下轴两条轴线的平面剖开机座和旋梭组零件（φ = 0 位置），导出剖面多边形。在 FreeCAD 里运行：

    WQ_MECH=<零件目录> WQ_HOUSING=<上件 STEP> WQ_HOUSING_LOWER=<下件 STEP> freecadcmd -c "exec(open('tools/wqls/render/hook_section.py').read())"

输出 <零件目录>/section.json：{名字: [[(u, v), ...] 每个环], ...}，u 沿 x，v 在剖面里垂直于 x（从旋梭轴往下轴方向为正）。
画图：python3 tools/wqls/render/hook_section_fig.py <零件目录> <输出 PNG>。
"""
import json
import os

import FreeCAD as App
import Part

V = App.Vector
D = os.environ["WQ_MECH"]
exec(open(os.path.join(os.getcwd(), "tools/wqls/spec.py"), encoding="utf-8").read(), S := {})
ZH, YL, ZL = S["ZH"], S["YL"], S["ZL"]
A = V(0, 0, ZH)
e = V(0, YL, ZL - ZH)
e.normalize()
n = V(1, 0, 0).cross(e)
n.normalize()
plane = Part.makePlane(800, 400, A + V(-200, 0, 0) - e * 150, n, V(1, 0, 0))

shapes = {}
low = Part.read(os.environ["WQ_HOUSING_LOWER"])
up = Part.read(os.environ["WQ_HOUSING"]).common(Part.makeBox(130, 200, 80, V(300, -80, 0)))
shapes["casting"] = low.fuse(up)
info = json.load(open(os.path.join(D, "parts.json")))
for k in ("pulley_upper", "pulley_lower", "belt", "lower_shaft", "bearings_lower", "gear_hook", "gear_lower", "hook_shaft",
          "bushes_hook", "hook", "bobbin_case"):
    shapes[k] = Part.read(os.path.join(D, f"{k}.step"))


def uv(p):
    d = p - A
    return (round(d.x, 2), round(d.dot(e), 2))


out = {}
for k, s in shapes.items():
    c = s.common(plane)
    rings = []
    for f in c.Faces:
        for w in f.Wires:
            pts = [uv(p) for p in w.discretize(Deflection=0.05)]
            if len(pts) > 2:
                rings.append(pts)
    out[k] = rings
    print(k, len(c.Faces), "faces")
json.dump(dict(rings=out, axis_v=dict(hook=0.0, lower=round((V(0, YL, ZL) - A).dot(e), 3))), open(os.path.join(D, "section.json"), "w"))
print('{"ok": true}')
