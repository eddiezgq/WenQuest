"""第 138 轮 G6.1：给网页三维重新划网格（比出图用的粗一些，网页加载快）。在 FreeCAD 里运行：

    WQ_DIRS=<目录1>:<目录2>… [WQ_LIN=0.05 WQ_ANG=0.35] freecadcmd -c "exec(open('tools/wqls/render/web_tess.py').read())"

每个目录里的 <零件>.step → <目录>/web/<零件>.stl，体积写进 <目录>/web/vol.json（mm³，给没有 parts.json 的机壳算质量）。
"""
import json
import os

import MeshPart
import Part

LIN = float(os.environ.get("WQ_LIN", 0.05))
ANG = float(os.environ.get("WQ_ANG", 0.35))
for d in os.environ["WQ_DIRS"].split(":"):
    out = os.path.join(d, "web")
    os.makedirs(out, exist_ok=True)
    vol = {}
    for f in sorted(os.listdir(d)):
        if not f.endswith(".step"):
            continue
        k = f[:-5]
        s = Part.read(os.path.join(d, f))
        vol[k] = s.Volume
        MeshPart.meshFromShape(Shape=s, LinearDeflection=LIN, AngularDeflection=ANG).write(os.path.join(out, k + ".stl"))
    json.dump(vol, open(os.path.join(out, "vol.json"), "w"))
    print("TESS", d, len(vol))
