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
    ("bush_mid", "shaft"), ("bush_mid", "casting"),   # G8.0 F 版中间含油轴套
    # G8.0 第 6 步：滑块套在连接销上、在导轨里滑；导轨和螺钉装在机壳竖筋上；针杆在上下导套里；橡胶塞在机头顶孔里
    ("slide_block", "nb_link"), ("slide_block", "slide_rail"), ("slide_rail", "casting"), ("rail_screws", "slide_rail"),
    ("rail_screws", "casting"), ("needle_bar", "nb_bushes"), ("nb_bushes", "casting"), ("nb_plug", "casting"),
    # G8.0 第 7 步：SM 螺钉拧在各自的零件里（紧针螺钉顶住机针，线钩螺钉穿过针夹拧进针杆，连接块紧定螺钉顶住针杆，曲柄销螺钉、曲柄紧定螺钉）
    ("clamp_screw", "needle_clamp"), ("clamp_screw", "needle_bar"), ("clamp_screw", "needle"),
    ("link_screws", "nb_link"), ("link_screws", "needle_bar"),
    ("crank_screws", "crank"), ("crank_screws", "crank_pin"), ("crank_screws", "shaft"),
    # G8.0 第 7 步 润滑：分油块和油毡盒用螺钉装在机壳上；油芯压在中间轴套上、插进油毡杯；油毡杯坐在导套座上、贴着针杆；
    # 铜管、尼龙管插在分油块、油毡盒、油泵的接头里。管子穿机壳的地方（过管孔）不算接触，要查间隙
    ("oil_block", "casting"), ("oil_screws", "casting"), ("oil_screws", "oil_block"), ("oil_screws", "oil_box"),
    ("oil_box", "casting"), ("oil_wicks", "casting"), ("oil_wicks", "oil_block"), ("oil_wicks", "oil_box"),
    ("oil_wicks", "oil_cups"), ("oil_wicks", "bush_mid"), ("oil_cups", "casting"), ("oil_cups", "needle_bar"),
    ("oil_cups", "nb_bushes"), ("oil_line", "oil_block"), ("oil_line", "oil_box"), ("oil_tubes", "oil_block"),
    ("oil_tubes", "oil_pump"), ("oil_screws", "oil_wicks"),
    ("cage_rod", "rod"), ("cage_rod", "crank_pin"), ("cage_lever", "lever"), ("cage_lever", "crank_pin"),   # G8.0 滚针组件
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
    ("reverse_spring", "pull_rod"), ("reverse_spring", "casting"), ("thread_guide", "casting"),
    # G4.8 选配件（cad/opt.py）：轴和轴套、球头、滚子在凸轮槽里、动刀贴着定刀剪、电磁铁推杆、支架螺在机壳上
    ("moving_knife", "knife_shaft"), ("moving_knife", "fixed_knife"), ("knife_shaft", "trim_base"), ("moving_knife", "trim_base"),
    ("trim_base", "casting"), ("trim_link", "knife_shaft"), ("trim_link", "trim_rock"), ("trim_rock", "trim_lever"),
    ("trim_lever", "trim_roller"), ("trim_roller", "trim_cam"), ("trim_cam", "lower_shaft"), ("trim_rock", "trim_brackets"),
    ("trim_brackets", "casting"), ("trim_solenoid", "trim_brackets"), ("trim_solenoid", "trim_lever"),
    ("wiper", "casting"), ("wiper", "wiper_solenoid"), ("wiper_solenoid", "casting"), ("release_arm_t", "release_lever"),
    ("release_solenoid", "release_arm_t"), ("release_solenoid", "casting"), ("estep_motor", "estep_bracket"),
    ("estep_bracket", "casting"), ("estep_pulley_m", "estep_motor"), ("estep_pulley_m", "estep_belt"), ("estep_pulley_r", "estep_belt"),
    ("estep_pulley_r", "regulator"), ("estep_pulley_r", "casting"), ("reverse_button", "casting"), ("estep_pulley_m", "estep_bracket")]}
# G4.8：动刀在针板和旋梭之间，和旋梭、梭壳、送布牙排的间隙按 0.5 mm 查（真机这里也只有零点几毫米）
TIGHT = {frozenset(p): 0.5 for p in [("moving_knife", "hook"), ("moving_knife", "bobbin_case"), ("moving_knife", "feed_bar")]}


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
# G8.1：全机检查一次跑不完，按组合编号分片：WQ_SHARD="i/n" 只查编号 % n == i 的组合；结果写到 WQ_CLOUT（默认 <零件目录>/clearance.json）
SLOW = float(os.environ.get("WQ_SLOW", "0"))                         # >0：单对距离计算超过这么多秒就打出来（找拖慢分片的零件对）
# G8.1：整齿的齿轮对机壳一帧要算 30 s，绕自身轴转、机壳不动，每 k 帧算一次就够（WQ_SPARSE="gear_lower|casting:6;…"）
SPARSE = {frozenset(p.split(":")[0].split("|")): int(p.split(":")[1]) for p in os.environ.get("WQ_SPARSE", "").split(";") if ":" in p}
SH_I, SH_N = (int(x) for x in os.environ.get("WQ_SHARD", "0/1").split("/"))
worst = {}
t0 = time.time()
first = True
for n_fr, f in enumerate(FR[::max(1, STEP // 2)]:
    sh = {k: placed(k, f) for k in parts}
    sh["casting"] = near
    pidx = -1
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            pidx += 1
            if SH_N > 1 and pidx % SH_N != SH_I:
                continue
            if frozenset((a, b)) in JOINT or frozenset((a, b)) in SKIP:
                continue
            k_sp = SPARSE.get(frozenset((a, b)))
            if k_sp and not first and n_fr % k_sp:
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
            tp = time.time()
            d = A.distToShape(B)[0]
            if SLOW and time.time() - tp > SLOW:
                print(f"SLOW {a} | {b} phi {f['phi']} {time.time() - tp:.0f}s", flush=True)
            key = f"{a} | {b}"
            if key not in worst or d < worst[key][0]:
                worst[key] = (round(d, 3), f["phi"])
    first = False
res = sorted(([k, v[0], v[1]] for k, v in worst.items()), key=lambda x: x[1])
bad = [r for r in res if r[1] < TIGHT.get(frozenset(r[0].split(" | ")), LIMIT)]
out = dict(limit_mm=LIMIT, step_deg=STEP, frames=len(FR[::max(1, STEP // 2)]), seconds=round(time.time() - t0), pairs=res, too_close=bad)
json.dump(out, open(os.environ.get("WQ_CLOUT") or os.path.join(D, "clearance.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(dict(too_close=bad, closest=res[:8], seconds=out["seconds"]), ensure_ascii=False))
