"""三维动画 52.8.1（配图 52.8.2）：零点定位系统换托盘——卸下这一批的托盘，把机外装好、测好的下一批托盘落到卡盘上，
拉钉被锁住拉下，定位和夹紧一次完成。三维模型取自数字工厂（factory/digital/models3d/elements.py），逐帧渲染。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, elements as E, typical as TY, shapes as S  # noqa: E402

a = C.Assembly("换托盘")
a.add(C.Part("工作台（局部）", S.box(-240, 240, -180, 180, -60, -40), "steel_dark"))
PIN = [(-120, -100), (120, -100), (-120, 100), (120, 100)]
for k, (x, y) in enumerate(PIN):
    a.add(C.Part(f"零点卡盘{k}", E.zero_point_chuck(at=(x, y, 0), D=110, H=40), "steel_dark"))
for tag, color in (("旧", "work"), ("新", "#9cc3a8")):
    pal = S.box(-180, 180, -150, 150, 0, 30)
    for x, y in PIN:
        pal = pal + E.pull_stud(at=(x, y, 0))
    pal = pal + S.box(-60, 60, -40, 40, 30, 130)
    a.add(C.Part(f"托盘{tag}", pal, "steel"))
    a.add(C.Part(f"工件{tag}", S.box(-50, 50, -60, 60, 130, 200), color))
CAM = {"dir": [0.9, -1.3, 0.7], "fit": [[-240, -180, -60], [240, 180, 360]]}
v = R.Video(a, width=1280, height=720, fps=20)


def st(old_z, old_vis, new_z, new_vis, cap, lock=False):
    parts = {"托盘旧": {"move": [0, 0, old_z], "visible": old_vis}, "工件旧": {"move": [0, 0, old_z], "visible": old_vis},
             "托盘新": {"move": [0, 0, new_z], "visible": new_vis}, "工件新": {"move": [0, 0, new_z], "visible": new_vis}}
    tx = [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True}, {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"}]
    if lock:
        tx.append({"pos": [0.62, 0.9], "text": "锁紧：重复定位精度几微米（以产品样本为准）", "fontSize": 20, "color": "#c0504d"})
    return {"parts": parts, "camera": CAM, "texts": tx}


def go(n, f, hold=0.0):
    for i in range(n):
        v.add(f(R.ease(i / max(1, n - 1))))
    if hold:
        v.add(f(1.0), hold=hold)


c1 = ("1  这一批加工完：卡盘通气松开，托盘连同工件吊走", "Batch done: air releases the chucks; lift the pallet away")
v.add(st(0, True, 0, False, c1), hold=1.0)
go(24, lambda t: st(220 * t, True, 0, False, c1))
c2 = ("2  下一批的托盘在机外已装好、测好，对准落下", "The next pallet, loaded and measured outside the machine, comes down")
go(24, lambda t: st(220, False, 220 * (1 - t) + 4, True, c2))
c3 = ("3  拉钉插进卡盘，钢球把拉钉拉下：定位、夹紧一次完成", "Studs enter the chucks; balls pull them down: located and clamped at once")
go(10, lambda t: st(220, False, 4 * (1 - t), True, c3, lock=t > 0.9), hold=2.5)
v.save("v52_8_1")
