"""WQ-LS G4.7 压脚与操纵件剖视：四个剖面，零件摆在指定转角 φ 的位置。在 FreeCAD 里运行：

    WQ_MECH=<零件目录> WQ_HOUSING=<上件 STEP> WQ_HOUSING_LOWER=<下件 STEP> [WQ_PHI=90] \
        freecadcmd -c "exec(open('tools/wqls/render/ctrl_section.py').read())"

剖面：x −16（压脚杆、压脚、压脚弹簧、调压螺钉、抬压脚块），y 18（手抬偏心凸轮、抬压脚块的凸轮臂），
y −47（针距旋钮的槽轮、拉杆上端的销），y −20（针距拉杆、调节器臂）。
输出 <零件目录>/ctrl_section.json：{剖面: {名字: [[(u, v), ...] 每个环]}}，x 剖面 (u, v) = (y, z)，y 剖面 = (x, z)；
画图 python3 tools/wqls/render/ctrl_section_fig.py <零件目录> <输出 PNG>。
"""
import json
import os

import FreeCAD as App
import Part

V = App.Vector
D = os.environ["WQ_MECH"]
PHI = int(os.environ.get("WQ_PHI", "90"))
CUTS = (("x", -16.0), ("y", 18.0), ("y", -47.0), ("y", -20.0))
with open(os.path.join(D, "frames.json")) as fh:
    FR = json.load(fh)["frames"]
f = min(FR, key=lambda x: abs(x["phi"] - PHI))

up = Part.read(os.environ["WQ_HOUSING"])
low = Part.read(os.environ["WQ_HOUSING_LOWER"])
NAMES = ("presser_bar", "presser_foot", "presser_spring", "presser_screw", "presser_collar", "lift_bracket", "presser_bushes",
         "hand_lifter", "knee_c2", "knee_link", "release_shaft", "stitch_dial", "pull_rod", "reverse_lever", "reverse_spring",
         "regulator", "reg_slider", "needle_bar", "needle_clamp", "needle", "shaft", "lower_shaft", "feed_bar")
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
for ax, c in CUTS:
    if ax == "x":
        plane = Part.makePlane(500, 500, V(c, -250, -150), V(1, 0, 0), V(0, 1, 0))
    else:
        plane = Part.makePlane(800, 500, V(-200, c, -150), V(0, 1, 0), V(1, 0, 0))
    lo, hi = ("XMin", "XMax") if ax == "x" else ("YMin", "YMax")
    sec = {}
    for k, s in [("casting_upper", up), ("casting_lower", low)] + list(parts.items()):
        b = s.BoundBox
        if getattr(b, lo) > c or getattr(b, hi) < c:
            continue
        cm = s.common(plane)
        rings = []
        for fc in cm.Faces:
            for w in fc.Wires:
                pts = [((round(p.y, 2) if ax == "x" else round(p.x, 2)), round(p.z, 2)) for p in w.discretize(Deflection=0.05)]
                if len(pts) > 2:
                    rings.append(pts)
        if rings:
            sec.setdefault("casting" if k.startswith("casting") else k, []).extend(rings)
    out[f"{ax}{c:g}"] = sec
    print(ax, c, sorted(sec))
with open(os.path.join(D, "ctrl_section.json"), "w") as fh:
    json.dump({"phi": f["phi"], "cuts": out}, fh)
print('{"ok": true}')
