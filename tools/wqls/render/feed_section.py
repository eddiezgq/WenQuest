"""WQ-LS G4.6 送布组剖视：三个垂直于 x 的剖面（y–z 平面），零件摆在指定转角 φ 的位置。在 FreeCAD 里运行：

    WQ_MECH=<零件目录> WQ_HOUSING=<上件 STEP> WQ_HOUSING_LOWER=<下件 STEP> [WQ_PHI=34] \
        freecadcmd -c "exec(open('tools/wqls/render/feed_section.py').read())"

剖面：x 25.5（牙架、送布牙、旋梭、针板下开口），x 316（送布调节器、送布摆轴曲柄），x 331（送布偏心、送布连杆、上轴、下轴）。
输出 <零件目录>/feed_section.json：{剖面 x: {名字: [[(y, z), ...] 每个环]}}；画图 python3 tools/wqls/render/feed_section_fig.py <零件目录> <输出 PNG>。
"""
import json
import os

import FreeCAD as App
import Part

V = App.Vector
D = os.environ["WQ_MECH"]
PHI = int(os.environ.get("WQ_PHI", "34"))
CUTS = (25.5, 316.0, 331.0)
FR = json.load(open(os.path.join(D, "frames.json")))["frames"]
f = min(FR, key=lambda x: abs(x["phi"] - PHI))

low = Part.read(os.environ["WQ_HOUSING_LOWER"])
up = Part.read(os.environ["WQ_HOUSING"]).common(Part.makeBox(130, 200, 250, V(300, -80, -10)))
casting = low.fuse(up)
NAMES = ("feed_bar", "feed_rock", "lift_rock", "hook", "hook_shaft", "bobbin_case", "feed_ecc", "feed_rod", "regulator", "reg_slider",
         "feed_link", "shaft", "lower_shaft", "pulley_upper", "pulley_lower", "belt", "oil_ecc", "oil_plunger", "oil_pump", "lift_link",
         "lift_ecc")
parts = {}
for k in NAMES:
    p = os.path.join(D, f"{k}.step")
    if not os.path.exists(p):
        continue
    s = Part.read(p)
    m = f["M"].get(k)
    if m:
        s.transformShape(App.Matrix(*m), True)
    parts[k] = s

out = {}
for x in CUTS:
    plane = Part.makePlane(400, 400, V(x, -200, -100), V(1, 0, 0), V(0, 1, 0))
    sec = {}
    for k, s in [("casting", casting)] + list(parts.items()):
        if s.BoundBox.XMin > x or s.BoundBox.XMax < x:
            continue
        c = s.common(plane)
        rings = []
        for fc in c.Faces:
            for w in fc.Wires:
                pts = [(round(p.y, 2), round(p.z, 2)) for p in w.discretize(Deflection=0.05)]
                if len(pts) > 2:
                    rings.append(pts)
        if rings:
            sec[k] = rings
    out[str(x)] = sec
    print(x, sorted(sec))
json.dump(dict(phi=f["phi"], cuts=out), open(os.path.join(D, "feed_section.json"), "w"))
print('{"ok": true}')
