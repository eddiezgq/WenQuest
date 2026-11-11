"""WQ-LS G4.1：刺布、挑线机构一转的干涉检查，并导出给三维动画用的机头网格。在 FreeCAD 里运行：

    WQ_MECH=<零件目录> WQ_HOUSING=<机壳 housing.step> WQ_STEP=2 freecadcmd -c "exec(open('tools/wqls/cad/mech_check.py').read())"

每一帧按 frames.json 的变换摆好零件，零件两两之间、零件与机壳之间求最小距离（FreeCAD distToShape，精确到实体表面）。
本来就相连的（销与孔、轴与轴承、针与针杆等）不算。结果：<零件目录>/clearance.json；机头网格 <零件目录>/head.stl（去掉面板一片，看得见里面）。
"""
import json
import os
import time

import FreeCAD as App
import MeshPart
import Part

V = App.Vector
D = os.environ.get("WQ_MECH", "/tmp/wqls_mech")
STEP = int(os.environ.get("WQ_STEP", "2"))
LIMIT = float(os.environ.get("WQ_CLEAR", "1.0"))        # 最小间隙要求 mm
info = json.load(open(os.path.join(D, "parts.json")))
FR = json.load(open(os.path.join(D, "frames.json")))["frames"]

cast = Part.read(os.environ["WQ_HOUSING"])
head = cast.common(Part.makeBox(130, 300, 260, V(-55, -150, 30)))          # 机头一段（x −55…75），面板那 7 mm 不要
head = head.Solids[0] if head.ShapeType != "Solid" and len(head.Solids) == 1 else head
MeshPart.meshFromShape(Shape=head, LinearDeflection=0.08, AngularDeflection=0.25).write(os.path.join(D, "head.stl"))
near = head.common(Part.makeBox(110, 200, 230, V(-50, -100, 40)))          # 干涉检查只用机构附近这一块
near = near.fuse(cast.common(Part.makeBox(120, 200, 160, V(360, -100, 120))))   # 加上立柱右端（后轴承座、电机座）

parts = {k: Part.read(os.path.join(D, f"{k}.step")) for k in info["parts"]}
JOINT = {frozenset(p) for p in [
    ("crank", "crank_pin"), ("crank", "shaft"), ("rod", "crank_pin"), ("lever", "crank_pin"), ("rod", "nb_link"),
    ("lever", "pin_M"), ("rocker", "pin_M"), ("rocker", "stud_Q"), ("needle_bar", "nb_link"), ("needle_bar", "needle_clamp"),
    ("needle_clamp", "needle"), ("needle", "needle_bar"), ("shaft", "bearing_front"), ("crank", "bearing_front"),
    ("casting", "bearing_front"), ("casting", "stud_Q"), ("casting", "shaft"),
    ("casting", "motor_cap"), ("casting", "motor_bolts"), ("motor_cap", "motor_bolts"), ("motor_cap", "motor_housing"),
    ("motor_rods", "motor_housing"), ("motor_rods", "motor_cap"), ("stator_core", "motor_housing"), ("stator_winding", "stator_core"),
    ("rotor", "shaft"), ("rotor_magnets", "rotor"), ("encoder_disc", "shaft"), ("encoder_disc", "rotor"), ("handwheel", "shaft"),
    ("handwheel_ring", "handwheel")]}


def mat(m):
    M = App.Matrix(*m)
    return M


def placed(k, f):
    s = parts[k].copy()
    m = f["M"].get(k)
    if m:
        s.transformShape(mat(m), True)
    return s


names = list(parts) + ["casting"]
worst = {}
t0 = time.time()
for f in FR[::max(1, STEP // 2)]:
    sh = {k: placed(k, f) for k in parts}
    sh["casting"] = near
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if frozenset((a, b)) in JOINT:
                continue
            if a != "casting" and b != "casting" and not f["M"].get(a) and not f["M"].get(b):
                continue                                        # 两个都不动，不用每帧算
            A, B = sh[a], sh[b]
            if A.BoundBox.isValid() and B.BoundBox.isValid():
                bb = App.BoundBox(A.BoundBox)
                bb.enlarge(LIMIT + 3)
                if not bb.intersect(B.BoundBox):
                    continue
            d = A.distToShape(B)[0]
            key = f"{a} | {b}"
            if key not in worst or d < worst[key][0]:
                worst[key] = (round(d, 3), f["phi"])
res = sorted(([k, v[0], v[1]] for k, v in worst.items()), key=lambda x: x[1])
bad = [r for r in res if r[1] < LIMIT]
out = dict(limit_mm=LIMIT, step_deg=STEP, frames=len(FR[::max(1, STEP // 2)]), seconds=round(time.time() - t0), pairs=res, too_close=bad)
json.dump(out, open(os.path.join(D, "clearance.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(dict(too_close=bad, closest=res[:8], seconds=out["seconds"]), ensure_ascii=False))
