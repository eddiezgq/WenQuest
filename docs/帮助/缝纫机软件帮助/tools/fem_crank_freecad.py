# 用 FreeCAD 自带的 Gmsh + CalculiX 给针杆曲柄做一次有限元（第 49 轮帮助的算例，也是帮助里给用户的控制台命令的验证）
import os, sys, json, math
sys.path.insert(0, os.path.expanduser("~/.local/share/FreeCAD/Mod/WenQuestSewing"))
import FreeCAD as App, Part, ObjectsFem
from sewcore import cad
case = json.load(open("/home/claude/fc/case.json"))
doc = App.newDocument("crank")
name, zh, shape, color = cad.freecad_shapes({"parts": [case["descriptor"]]})[0]
part = doc.addObject("Part::Feature", "NeedleCrank"); part.Shape = shape
doc.recompute()
def hole_face(h):
    for i, f in enumerate(part.Shape.Faces):
        if f.Surface.__class__.__name__ == "Cylinder" and abs(f.Surface.Radius - h["r"]) < 0.05:
            c = f.Surface.Center
            if math.hypot(c.x - h["center"][0], c.z - h["center"][2]) < 0.05:
                return "Face%d" % (i + 1)
fs, fl = hole_face(case["support"]), hole_face(case["load"])
an = ObjectsFem.makeAnalysis(doc, "Analysis")
sol = ObjectsFem.makeSolverCalculiXCcxTools(doc); an.addObject(sol)
mat = ObjectsFem.makeMaterialSolid(doc, "Steel45"); mat.Material = {"Name": "45 steel", "YoungsModulus": "210000 MPa", "PoissonRatio": "0.3", "Density": "7850 kg/m^3"}; an.addObject(mat)
fix = ObjectsFem.makeConstraintFixed(doc, "Shaft"); fix.References = [(part, fs)]; an.addObject(fix)
ln = doc.addObject("Part::Line", "Down"); ln.X1, ln.Y1, ln.Z1, ln.X2, ln.Y2, ln.Z2 = 0, 0, 0, 0, 0, -10
doc.recompute()
fo = ObjectsFem.makeConstraintForce(doc, "RodForce"); fo.References = [(part, fl)]; fo.Force = "%.3f N" % case["ref_load"]; fo.Direction = (ln, ["Edge1"]); an.addObject(fo)
me = ObjectsFem.makeMeshGmsh(doc, "Mesh"); me.Shape = part; me.CharacteristicLengthMax = 1.2; me.ElementOrder = "2nd"; an.addObject(me)
doc.recompute()
from femmesh.gmshtools import GmshTools
print("gmsh:", GmshTools(me).create_mesh())
from femtools import ccxtools
fea = ccxtools.FemToolsCcx(an, sol)
fea.purge_results(); fea.update_objects(); fea.setup_working_dir("/home/claude/fc/run"); fea.setup_ccx()
msg = fea.check_prerequisites(); print("check:", msg or "ok")
fea.write_inp_file(); fea.ccx_run(); fea.load_results()
res = [o for o in doc.Objects if o.isDerivedFrom("Fem::FemResultObject")][0]
vm = list(res.vonMises); print("nodes", len(vm), "max vonMises MPa", round(max(vm), 1), "max disp mm", round(max(res.DisplacementLengths), 5))
# 网页动画用：零件上表面（y 最大的那一面）的节点与三角形、每个节点的等效应力
fm = me.FemMesh
ids = list(res.NodeNumbers); vmap = dict(zip(ids, vm))
ymax = max(p.y for p in fm.Nodes.values())
tris = []
for fid in fm.Faces:
    ns = fm.getElementNodes(fid)[:3]
    if all(abs(fm.Nodes[n].y - ymax) < 1e-6 for n in ns):
        tris.append(ns)
used = sorted({n for t in tris for n in t}); ix = {n: i for i, n in enumerate(used)}
out = {"x": [round(fm.Nodes[n].x, 3) for n in used], "z": [round(fm.Nodes[n].z, 3) for n in used], "s": [round(vmap[n], 2) for n in used],
       "t": [[ix[n] for n in t] for t in tris], "max": round(max(vm), 1), "force": case["ref_load"], "nodes": len(vm), "elements": fm.VolumeCount,
       "ccx": "CalculiX", "series": case["series"], "n": case["n"]}
json.dump(out, open("/home/claude/fc/crank_fea.json", "w"))
print("surface tris", len(tris), "elements", fm.VolumeCount)
