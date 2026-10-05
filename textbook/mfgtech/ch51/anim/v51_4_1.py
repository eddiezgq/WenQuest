"""三维动画 51.4.1（配图 51.4.2）：一面两孔装到两个圆柱销上装不进去，换成一个圆柱销加一个削边销就装得上。
孔距比销距大（放大画出），过两孔中心剖开。模型：factory/digital/models3d（elements.locating_pin、locating.plate_with_holes）。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, elements as E, locating as L, shapes as S  # noqa: E402

a = C.Assembly("一面两销")
a.add(C.Part("支承板", S.box(-120, 120, -70, 70, -20, 0), "cast"))
a.add(C.Part("圆柱销1", E.locating_pin(12, 14, "cyl", at=(-80, 0, 0)), "hardened"))
a.add(C.Part("圆柱销2", E.locating_pin(12, 14, "cyl", at=(80, 0, 0)), "hardened"))
a.add(C.Part("削边销2", E.locating_pin(12, 14, "dia", at=(80, 0, 0), b=4, flat_dir="x"), "#4f7fb8"))
a.add(C.Part("工件", L.plate_with_holes(L=220, B=110, t=18, holes=((-80, 0), (81.6, 0)), D=12.4, at=(0, 0, 0)), "work_cut", opacity=0.75))
CAM = {"dir": [0.2, -1.2, 0.6], "fit": [[-120, -70, -20], [120, 70, 70]]}
v = R.Video(a, width=1280, height=720, fps=20, section=((0, 0, 0), (0, -1, 0)))


def st(z, tilt, diamond, cap, bad=False):
    parts = {"工件": {"move": [0, 0, z], "rot": [0, 1, 0, -tilt, -80, 0, z]}, "圆柱销2": {"visible": not diamond}, "削边销2": {"visible": diamond}}
    if bad:
        parts["工件"]["color"] = "#c0504d"
    return {"parts": parts, "camera": CAM, "texts": [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
                                                      {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"}]}


def go(n, f, hold=0.0):
    for i in range(n):
        v.add(f(R.ease(i / max(1, n - 1))))
    if hold:
        v.add(f(1.0), hold=hold)


c1 = ("1  两个圆柱销：孔距比销距大一点（放大画出）", "Two round pins: the hole spacing is a little larger (exaggerated)")
go(20, lambda t: st(60 - 46 * t, 0, False, c1))
c2 = ("2  第一个孔套进去了，第二个孔压在销头上", "The first hole goes on; the second sits on top of its pin")
go(14, lambda t: st(14 * (1 - t), 5.0 * t, False, c2), hold=1.0)
c3 = ("装不上：沿两销连线方向被重复限制——过定位", "It will not go on: x is located twice — over-constraint")
v.add(st(0, 5.0, False, c3), hold=1.5)
go(14, lambda t: st(60 * t, 5.0 * (1 - t), False, ("3  抬起工件，准备换销：沿连线方向削去两边", "3  Lift the part to change the pin")))
v.add(st(60, 0, True, ("换成削边销：沿两销连线方向削去两边", "A diamond pin, relieved along the line of the pins")), hold=1.2)
go(24, lambda t: st(60 * (1 - t), 0, True, ("4  再装：削边销让开孔距误差，工件落到底", "4  Now it goes on: the diamond pin clears the spacing error")), hold=1.0)
v.add(st(0, 0, True, ("圆柱销定 x、y，削边销只定转角", "The round pin fixes x and y; the diamond pin fixes only rotation")), hold=2.0)
v.save("v51_4_1")
