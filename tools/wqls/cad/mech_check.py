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
if os.environ.get("WQ_HOUSING_LOWER"):                                        # G4.5：机座（旋梭组装在里面）、立柱脚（同步带穿过）
    low = Part.read(os.environ["WQ_HOUSING_LOWER"])
    near = near.fuse(low.common(Part.makeBox(520, 200, 64, V(-110, -70, -63))))
    MeshPart.meshFromShape(Shape=low, LinearDeflection=0.08, AngularDeflection=0.25).write(os.path.join(D, "bed.stl"))   # 网页三维的机座
    near = near.fuse(cast.common(Part.makeBox(110, 200, 220, V(300, -80, 0))))

parts = {k: Part.read(os.path.join(D, f"{k}.step")) for k in info["parts"]}
JOINT = {frozenset(p) for p in [
    ("crank", "crank_pin"), ("crank", "shaft"), ("rod", "crank_pin"), ("lever", "crank_pin"), ("rod", "nb_link"),
    ("lever", "pin_M"), ("rocker", "pin_M"), ("rocker", "stud_Q"), ("needle_bar", "nb_link"), ("needle_bar", "needle_clamp"),
    ("needle_clamp", "needle"), ("needle", "needle_bar"), ("shaft", "bearing_front"), ("crank", "bearing_front"),
    ("casting", "bearing_front"), ("casting", "stud_Q"), ("casting", "shaft"),
    ("casting", "motor_cap"), ("casting", "motor_bolts"), ("motor_cap", "motor_bolts"), ("motor_cap", "motor_housing"),
    ("motor_rods", "motor_housing"), ("motor_rods", "motor_cap"), ("stator_core", "motor_housing"), ("stator_winding", "stator_core"),
    ("rotor", "shaft"), ("rotor_magnets", "rotor"), ("encoder_disc", "shaft"), ("encoder_disc", "rotor"), ("handwheel", "shaft"),
    ("handwheel_ring", "handwheel"),
    # G4.5 旋梭组
    ("pulley_upper", "shaft"), ("pulley_lower", "lower_shaft"), ("belt", "pulley_upper"), ("belt", "pulley_lower"),
    ("lower_shaft", "bearings_lower"), ("casting", "bearings_lower"), ("gear_lower", "lower_shaft"),
    ("hook_shaft", "bushes_hook"), ("casting", "bushes_hook"), ("gear_hook", "hook_shaft"), ("hook", "hook_shaft"),
    ("gear_hook", "gear_lower"),          # 啮合（齿侧间隙另算）
    ("hook", "bobbin_case"),              # 梭芯套装在旋梭里（梭床导轨配合）
    ("needle", "hook"),                   # 梭尖与机针的间隙是设计的 0.08，单独核对（G4.5 计算书），不按 1 mm 要求
    # G4.6 送布组：偏心与轴、连杆大头与偏心；同一根销上的几件（P：送布连杆小头、调节器滑块、L2；C：L2、摆轴曲柄；T：摆轴摆杆、牙架）；
    # 滑块在调节器槽里；牙架前端滑块销在抬牙叉槽里；抬牙偏心与下轴、抬牙连杆，抬牙连杆与抬牙曲柄
    ("feed_ecc", "shaft"), ("feed_ecc", "feed_rod"), ("feed_rod", "reg_slider"), ("feed_rod", "feed_link"), ("reg_slider", "feed_link"),
    ("regulator", "reg_slider"), ("feed_link", "feed_rock"), ("feed_rock", "feed_bar"), ("feed_bar", "lift_rock"),
    ("lift_ecc", "lower_shaft"), ("lift_ecc", "lift_link"), ("lift_link", "lift_rock"),
    ("motor_housing", "stator_winding"),   # 定子绕组端部贴着电机壳（G4.3 的电机实体，绝缘纸隔开），不是运动副
    ("oil_ecc", "lower_shaft"), ("oil_ecc", "oil_plunger"), ("oil_plunger", "oil_pump"), ("casting", "oil_pump"),
    # G4.7 压脚与操纵件：导套、销孔、螺纹、弹簧座、凸轮和钩的接触（cad/ctrl.py）
    ("presser_bar", "presser_bushes"), ("presser_bar", "presser_foot"), ("presser_bar", "presser_collar"), ("presser_bar", "lift_bracket"),
    ("presser_collar", "presser_spring"), ("presser_spring", "presser_screw"), ("presser_screw", "casting"), ("presser_spring", "casting"),
    ("presser_bushes", "casting"), ("presser_foot", "feed_bar"), ("hand_lifter", "casting"), ("hand_lifter", "lift_bracket"),
    ("knee_c2", "casting"), ("knee_c1", "casting"), ("knee_rod", "knee_c2"), ("knee_rod", "knee_c1"), ("knee_link", "knee_c2"),
    ("knee_link", "lift_bracket"), ("knee_push", "knee_c1"), ("knee_push", "casting"),
    ("release_shaft", "casting"), ("release_shaft", "lift_bracket"), ("release_shaft", "release_rod"), ("release_rod", "release_lever"),
    ("release_lever", "casting"), ("release_lever", "release_pin"), ("release_pin", "tension_post"), ("tension_post", "casting"),
    ("tension_post", "tension_discs"), ("tension_discs", "release_pin"), ("tension_discs", "tension_spring"), ("tension_spring", "tension_nut"),
    ("tension_nut", "tension_post"), ("check_spring", "tension_post"), ("tension_spring", "tension_post"),
    ("stitch_dial", "casting"), ("stitch_dial", "pull_rod"), ("pull_rod", "regulator"), ("pull_rod", "reverse_lever"), ("reverse_lever", "casting"),
    ("reverse_spring", "pull_rod"), ("reverse_spring", "casting")]}


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
ONLY = set(x for x in os.environ.get("WQ_ONLY", "").split(",") if x)    # 只查和这些零件有关的组合（G4.5：只查旋梭组，机头部分 G4.1–4.3 查过）
# G4.7：某个状态下由控制器联锁排除的组合（例如膝抬 13 mm 时只在针杆上面停针，针夹和压脚不会相遇），用 WQ_SKIP="a|b;c|d" 给出
SKIP = {frozenset(p.split("|")) for p in os.environ.get("WQ_SKIP", "").split(";") if "|" in p}
worst = {}
t0 = time.time()
first = True
for f in FR[::max(1, STEP // 2)]:
    sh = {k: placed(k, f) for k in parts}
    sh["casting"] = near
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if frozenset((a, b)) in JOINT or frozenset((a, b)) in SKIP:
                continue
            if ONLY and a not in ONLY and b not in ONLY:
                continue
            if not first and not f["M"].get(a) and not f["M"].get(b):
                continue                                        # 两个都不动（机壳也不动），只在第一帧算
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
    first = False
res = sorted(([k, v[0], v[1]] for k, v in worst.items()), key=lambda x: x[1])
bad = [r for r in res if r[1] < LIMIT]
out = dict(limit_mm=LIMIT, step_deg=STEP, frames=len(FR[::max(1, STEP // 2)]), seconds=round(time.time() - t0), pairs=res, too_close=bad)
json.dump(out, open(os.path.join(D, "clearance.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(dict(too_close=bad, closest=res[:8], seconds=out["seconds"]), ensure_ascii=False))
