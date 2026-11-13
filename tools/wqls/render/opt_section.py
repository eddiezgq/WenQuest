"""WQ-LS G4.8 针板下面的剖面：在动刀刀片平面（z −5.4）横着切，动刀在最后（φ 120°）和最前（φ 0°）两个位置；定刀在 z −3.7、旋梭在 z −7 另切一层。在 FreeCAD 里运行：

    WQ_MECH=<剪线那一转的零件目录> WQ_HOUSING_LOWER=<下件 STEP> freecadcmd -c "exec(open('tools/wqls/render/opt_section.py').read())"

输出 <零件目录>/opt_section.json：{φ: {零件: [[(x, y), ...] 每个环]}}；画图 python3 tools/wqls/render/opt_section_fig.py <零件目录> <PNG>。
"""
import json
import os

import FreeCAD as App
import Part

V = App.Vector
D = os.environ["WQ_MECH"]
Z = float(os.environ.get("WQ_Z", "-5.4"))
FR = {f["phi"]: f for f in json.load(open(os.path.join(D, "frames.json")))["frames"]}
NAMES = ("moving_knife", "fixed_knife", "feed_bar", "hook", "bobbin_case", "knife_shaft", "trim_base")
low = Part.read(os.environ["WQ_HOUSING_LOWER"])
ZK = {"fixed_knife": -3.7, "hook": -7.0, "bobbin_case": -11.0}    # 不在刀片平面上的件，在它自己那一层切（画虚线框）
out = {}
for phi in (120, 0):
    f = FR[phi]
    sec = {}
    for k in NAMES + ("casting",):
        if k == "casting":
            s = low
        else:
            p = os.path.join(D, k + ".step")
            if not os.path.exists(p):
                continue
            s = Part.read(p)
            m = f["M"].get(k)
            if m:
                s.transformShape(App.Matrix(*m), True)
        zc = ZK.get(k, Z)
        if s.BoundBox.ZMin > zc or s.BoundBox.ZMax < zc:
            continue
        cm = s.common(Part.makePlane(300, 300, V(-150, -150, zc), V(0, 0, 1)))
        rings = [[(round(q.x, 2), round(q.y, 2)) for q in w.discretize(Deflection=0.03)] for fc in cm.Faces for w in fc.Wires]
        if rings:
            sec[k] = rings
    out[str(phi)] = sec
    print(phi, sorted(sec))
json.dump(dict(z=Z, cuts=out), open(os.path.join(D, "opt_section.json"), "w"))
