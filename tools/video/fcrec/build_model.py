import os
import FreeCAD as App, Part, Mesh, glob, os, sys
D = os.environ["WQLS_TE"]  # 整机 STEP 目录（tools/wqls 出的 b_s3_down_TE）
OUT = os.environ.get("WQ_REC", ".") + "/model/WQ-LS.FCStd"
GROUPS = [("机壳", "Housing", ["bed", "head"]),
          ("主轴与挑线", "Upper shaft & take-up", ["shaft", "crank", "crank_pin", "crank_screws", "rod", "lever", "rocker", "cage_", "needle", "nb_", "link_screws", "pin_M", "stud_Q", "slide_", "rail_screws", "bush_mid", "bearing_front", "handwheel", "pulley_upper", "encoder", "thread_guide", "check_spring", "tension_", "clamp_screw"]),
          ("勾线与下轴", "Hook & lower shaft", ["hook", "lower_shaft", "gear_", "bearings_lower", "bushes_hook", "bobbin", "pulley_lower", "belt"]),
          ("送布与抬牙", "Feed & lift", ["feed_", "lift_", "regulator", "reg_slider", "reverse_button", "knee_"]),
          ("压脚", "Presser", ["presser_", "hand_lifter", "release_"]),
          ("剪线与拨线", "Trimmer & wiper", ["trim_", "knife", "moving_knife", "fixed_knife", "wiper"]),
          ("电机", "Motor", ["motor_", "rotor", "stator", "estep_"]),
          ("润滑", "Lubrication", ["oil_"])]
doc = App.newDocument("WQ_LS")
doc.Label = "WQ-LS 平缝机"
grp = {}
for zh, en, keys in GROUPS:
    g = doc.addObject("App::DocumentObjectGroup", "G_" + en.split()[0].replace("&", ""))
    g.Label = zh
    grp[zh] = (g, keys)
def group_of(n):
    for zh, (g, keys) in grp.items():
        if any(n == k or n.startswith(k) for k in keys):
            return g
    return grp["主轴与挑线"][0]
names = sorted(os.path.basename(p)[:-5] for p in glob.glob(D + "/*.step"))
for n in names:
    s = Part.read(f"{D}/{n}.step")
    o = doc.addObject("Part::Feature", n); o.Shape = s
    group_of(n).addObject(o)
for n in ("bed", "head"):
    mm = Mesh.Mesh(f"{D}/{n}.stl")
    mm.harmonizeNormals(); mm.removeDuplicatedPoints(); mm.removeDuplicatedFacets(); mm.fixDegenerations(1e-6); mm.removeNonManifolds(); mm.fixIndices()
    m = doc.addObject("Mesh::Feature", n); m.Mesh = mm
    grp["机壳"][0].addObject(m)
doc.recompute()
doc.saveAs(OUT)
print("OBJS", len(doc.Objects), os.path.getsize(OUT) // 1024, "KB")
