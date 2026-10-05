"""三维动画 51.1.1（配图 51.1.3）：机器人放料——手爪把板形工件放到一个圆柱销、一个削边销上。机器人放的位置偏了 1.5 mm，
工件孔口的倒角先碰到销头的导向锥面，工件一边下落一边被推到正确的位置；手爪是柔性的（随动），放到位后松开、抬起。
过圆柱销中心剖开。模型：factory/digital/models3d（elements.locating_pin、locating.plate_with_holes），逐帧渲染（textbook/tools/render3d.py）。
运动学是简化的：偏移量在工件下落经过导向锥面的那 3 mm 里线性减到零。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, elements as E, locating as L, shapes as S  # noqa: E402

pins = ((-70, -35), (70, 35))
H_PIN = 14.0
a = C.Assembly("机器人放料")
a.add(C.Part("夹具底板", S.box(-120, 120, -80, 80, -20, 0), "cast"))
for k, (px, py) in enumerate(pins):
    pin = E.locating_pin(12, H_PIN, "cyl" if k == 0 else "dia", at=(0, 0, 0), flat_dir="x")      # 削边方向沿两销连线
    a.add(C.Part(f"定位销{k + 1}", S.move(S.rot(pin, 0, 0, 26.565), px, py, 0), "hardened"))
a.add(C.Part("工件", L.plate_with_holes(holes=pins, D=12.02, at=(0, 0, 0)), "work"))
GRIP = ["手指左", "手指右", "手爪体"]
for sx, n in ((-1, "手指左"), (1, "手指右")):
    a.add(C.Part(n, S.box(sx * 100 + (0 if sx > 0 else -10), sx * 100 + (10 if sx > 0 else 0), -15, 15, 4, 50), "hardened"))
a.add(C.Part("手爪体", S.box(-122, 122, -20, 20, 50, 75) + S.cyl("z", (0, 0), 26, 75, 130), "steel"))
WIDE = {"dir": [0.8, -1.3, 0.6], "fit": [[-130, -80, -20], [130, 80, 200]]}
CLOSE = {"dir": [0.15, -1.0, 0.12], "fit": [[-96, -35, -6], [-44, -35, 52]]}
v = R.Video(a, width=1280, height=720, fps=20, section=((0, -35, 0), (0, -1, 0)))
OFF = 1.5


def offset(zb):
    """工件底面高 zb 时的横向偏移：底面在销顶以上时保持 1.5 mm；经过导向锥面（销顶以下 3 mm）时线性减到零。"""
    if zb >= H_PIN:
        return OFF
    return OFF * max(0.0, (zb - (H_PIN - 3.0)) / 3.0)


def st(zb, open_mm, cam, cap, extra=None):
    dx = offset(zb)
    parts = {"工件": {"move": [dx, 0, zb]}}
    for n in GRIP:
        mv = [dx, 0, zb]
        if n == "手指左":
            mv = [dx - open_mm, 0, zb]
        if n == "手指右":
            mv = [dx + open_mm, 0, zb]
        parts[n] = {"move": mv}
    texts = [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
             {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"},
             {"pos": [0.72, 0.9], "text": f"工件偏离正确位置 {dx:.2f} mm", "fontSize": 24, "bold": True,
              "color": "#c0504d" if dx > 0.05 else "#5a9e6f"}]
    return {"parts": parts, "camera": cam, "texts": texts + (extra or [])}


def go(n, f, hold=0.0):
    for i in range(n):
        v.add(f(R.ease(i / max(1, n - 1))))
    if hold:
        v.add(f(1.0), hold=hold)


c1 = ("1  机器人把工件送到夹具上方：位置偏了 1.5 mm", "The robot brings the part over the fixture, 1.5 mm off")
go(24, lambda t: st(110 - 80 * t, 0, WIDE, c1), hold=0.6)
c2 = ("2  放大看圆柱销：孔口倒角碰到销头的导向锥面", "Close-up: the hole chamfer meets the lead-in cone of the pin")
go(20, lambda t: st(30 - (30 - H_PIN) * t, 0, CLOSE, c2), hold=0.6)
c3 = ("3  手爪随动，工件一边下落一边被推正", "The compliant gripper lets the part slide into place")
go(24, lambda t: st(H_PIN - 6 * t, 0, CLOSE, c3), hold=0.6)
c4 = ("4  落到底面上：圆柱销定两个移动，削边销定转角", "Seated: the round pin fixes x and y, the diamond pin fixes rotation")
go(16, lambda t: st(H_PIN - 6 - (H_PIN - 6) * t, 0, CLOSE, c4), hold=0.8)
c5 = ("5  手爪松开、抬起；夹紧后开始加工", "The gripper opens and withdraws; clamp and machine")
go(12, lambda t: st(0, 12 * t, WIDE, c5))
for i in range(16):
    t = R.ease(i / 15)
    s = st(0, 12, WIDE, c5)
    for n in GRIP:
        s["parts"][n]["move"][2] = 120 * t
    v.add(s)
v.add(s, hold=2.0)
v.save("v51_1_1")
