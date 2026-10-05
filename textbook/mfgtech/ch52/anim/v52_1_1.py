"""三维动画 52.1.1（配图 52.1.3）：在键槽铣夹具 JJ-301-50 上装夹 SH-301、对刀后铣键槽、松开取件的全过程。
三维模型取自数字工厂（factory/digital/models3d/jj30150.py），逐帧渲染（textbook/tools/render3d.py 的 Video）。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, jj30150 as J, workpiece as W, shapes as S  # noqa: E402

g = J.geometry()
a = J.assembly("op40", with_work=False)
k = W.plan()["part"]["keyway"]
x_end = 52.0 + float(k["offset_mm"]) + float(k["L"]) - 6 + g["work_x0"]       # 键槽右端的铣刀中心
x_start = x_end - (float(k["L"]) - 12)
w40, w50 = W.sh301("op40"), W.sh301("op50")
for w, n in ((w40, "工件（铣前）"), (w50, "工件（铣后）")):
    w.shape = S.move(w.shape, g["work_x0"], 0, g["zc"])
    w.name = n
    a.add(w)
zk = g["zc"] + 15.0                                       # 槽底（磨前 H 对应的高度）
a.add(C.Part("键槽铣刀", J.cutter(0.0, 0.0), "tool", tags=("nocut",)))
CAM = {"dir": [0.95, -1.3, 0.9], "fit": [[-95, -70, -40], [190, 110, 150]], "zoom": 1.12, "pan": [0, -0.04]}
FPS = 20
v = R.Video(a, width=1280, height=720, fps=FPS)
straps = [p.name for p in a.parts if p.name.startswith(("压板", "垫圈螺母"))]


def state(work=None, work_move=(0, 0, 0), retract=1.0, cutter=None, keyway=False, cap=("", ""), arrows=()):
    parts = {}
    for n in straps:
        parts[n] = {"move": [0, 28 * retract, 2 * retract if n.startswith("压板") else 0]}
    parts["工件（铣前）"] = {"visible": work == "op40", "move": list(work_move)}
    parts["工件（铣后）"] = {"visible": work == "op50", "move": list(work_move)}
    if cutter is None:
        parts["键槽铣刀"] = {"visible": False}
    else:
        parts["键槽铣刀"] = {"move": list(cutter)}
    texts = [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
             {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"}]
    return {"parts": parts, "camera": CAM, "texts": texts, "arrows": list(arrows)}


def move(n, f, hold=0.0):
    for i in range(n):
        v.add(f(R.ease(i / max(1, n - 1))))
    if hold:
        v.add(f(1.0), hold=hold)


cap1 = ("1  清理 V 形块和挡板上的切屑，压板退在后面", "Clean chips off the V-block and stop plate; straps pulled back")
v.add(state(cap=cap1), hold=2.6)
cap2 = ("2  放工件：齿轮位落在 V 形块上", "Load: the gear seat drops into the V-block")
move(26, lambda t: state("op40", (8, 0, 90 * (1 - t)), cap=cap2), hold=1.2)
cap3 = ("3  向左推，左轴肩靠紧挡板（限制轴向移动）", "Push left until the left shoulder seats on the stop plate")
move(16, lambda t: state("op40", (8 * (1 - t), 0, 0), cap=cap3, arrows=[{"from": (110, -40, g["zc"]), "to": (70, -40, g["zc"]), "color": "#4f7fb8"}]), hold=1.6)
cap4 = ("4  推出压板，压在左轴端和右轴承位上", "Slide the straps forward onto the left journal and right bearing seat")
move(22, lambda t: state("op40", retract=1 - t, cap=cap4), hold=1.4)
cap5 = ("5  定扭矩扳手拧到 5 N·m：每件夹紧力一样", "Torque wrench to 5 N·m: the same clamping force every time")
arrows5 = [{"from": (sx, g["stud_y"], g["zc"] + 50), "to": (sx, g["stud_y"], g["zc"] + 32), "color": "#c0504d", "text": "W"} for sx in J.STRAP_X]
v.add(state("op40", retract=0, cap=cap5, arrows=arrows5), hold=2.6)
cap6 = ("6  铣刀朝挡板方向进给，分层铣出键槽（每层单向切削、抬刀返回）", "Cut toward the stop plate in layers, one way, lifting to return")
layers = 5
for L in range(layers):
    depth = (L + 1) / layers
    zt = zk + (1 - depth) * 5.15
    move(6, lambda t, zt=zt: state("op40", retract=0, cutter=(x_end, 0, zt + 20 * (1 - t)), cap=cap6))
    move(14, lambda t, zt=zt: state("op40" if L < layers - 1 or t < 1 else "op50", retract=0, cutter=(x_end - (x_end - x_start) * t, 0, zt), cap=cap6,
                                    arrows=[{"from": (x_end + 30, -30, zt + 40), "to": (x_end - 10, -30, zt + 40), "color": "#c0504d", "text": "进给"}]))
    move(6, lambda t, zt=zt: state("op40" if L < layers - 1 else "op50", retract=0, cutter=(x_start + (x_end - x_start) * t, 0, zt + 20), cap=cap6))
cap7 = ("7  松开、退回压板，取下工件（键槽已铣出）", "Unclamp, pull the straps back and lift the part out")
move(18, lambda t: state("op50", retract=t, cap=cap7))
move(24, lambda t: state("op50", (0, 0, 90 * t), retract=1, cap=cap7), hold=2.5)
v.save("v52_1_1")
