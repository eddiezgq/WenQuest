"""G8.1 第四步：几个由多个实体组成的零件（螺钉组、转子磁钢、抬牙摆轴）parts.json 里没有转动惯量，这里用 FreeCAD 按各实体合成补上。

    WQ_DIR=<整机目录> freecadcmd -c "exec(open('tools/wqls/cad/inertia_fix.py').read())"   → <整机目录>/inertia_fix.json（g81_dyn.py 读）
"""
import json
import os

import FreeCAD
import Part
d = os.environ["WQ_DIR"]
pj = json.load(open(os.path.join(d, "parts.json")))
out = {}
for k in [k for k, v in pj["parts"].items() if "Ixx_kgmm2" not in v and os.path.exists(os.path.join(d, k + ".step"))]:
    sh = Part.read(os.path.join(d, k + ".step"))
    Ixx = Iyy = Izz = 0
    m = pj["parts"][k]["mass_kg"]; vols = [s.Volume for s in sh.Solids]; V = sum(vols); rho = m / V
    cs = [s.CenterOfMass for s in sh.Solids]
    com = sum((cs[i] * vols[i] for i in range(len(vols))), FreeCAD.Vector()) / V
    for s in sh.Solids:
        M = s.MatrixOfInertia   # 关于该实体质心，体积单位 mm^5
        cc = s.CenterOfMass - com
        Ixx += (M.A11 + s.Volume * (cc.y ** 2 + cc.z ** 2)) * rho
        Iyy += (M.A22 + s.Volume * (cc.x ** 2 + cc.z ** 2)) * rho
        Izz += (M.A33 + s.Volume * (cc.x ** 2 + cc.y ** 2)) * rho
    out[k] = dict(Ixx_kgmm2=Ixx, Iyy_kgmm2=Iyy, Izz_kgmm2=Izz)
json.dump(out, open(os.path.join(d, "inertia_fix.json"), "w"))
print(out)
