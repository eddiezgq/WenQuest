"""三维动画 54.3.1（配图 54.3.5）：外圆磨床尾座偏移磨出锥度。先两顶尖连线与工作台运动方向平行，砂轮相对工件走一遍，磨出圆柱；
再把尾座向离开砂轮的方向偏移 e，同样走一遍，磨出尾座端大的锥形。俯视；偏移与锥度放大 500 倍画出，读数按真实值
（e = 0.008 mm，SH-301 左右轴承位相距 78.5 mm：直径差 2e·78.5/167，hub/accuracy.py taper_from_offset）。"""
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from hub import accuracy as A  # noqa: E402
from models3d import core as C, errors3d as X, machines as MA, shapes as S  # noqa: E402

L, XW, K, E_REAL = 167.0, 124.5, 500.0, 0.008
r_head = 18.0
e = K * E_REAL
g = MA.cylindrical_grinder(L=L, wheel_x=XW, r_work=r_head, tail_offset=0.0)
off = MA.cylindrical_grinder(L=L, wheel_x=XW, r_work=r_head, tail_offset=-e)
a = C.Assembly("尾座偏移")
MOVING = ("砂轮", "砂轮罩", "砂轮架", "横进给拖板")
for p in g.parts:
    if p.name in ("尾座", "后顶尖"):
        a.add(C.Part(p.name + "（正）", p.shape, p.color))
    else:
        a.add(p)
for p in off.parts:
    if p.name in ("尾座", "后顶尖"):
        a.add(C.Part(p.name + "（偏）", p.shape, p.color))
xs = [L * i / 24 for i in range(25)]
a.add(C.Part("工件（圆柱）", X.profile_shaft(xs, [r_head] * 25), "work"))
ang = math.degrees(math.atan2(e, L))
a.add(C.Part("工件（锥形）", S.rot(X.profile_shaft(xs, [r_head + e * x / L for x in xs]), az=-ang), "work"))
CAM = {"dir": [0, 0, 1], "up": [0, 1, 0], "fit": [[-70, -70, -30], [L + 70, 110, 30]]}
v = R.Video(a, width=1280, height=720, fps=20)
dd = A.taper_from_offset(E_REAL, L, 46.0, 124.5) * 1000


def st(dx, tail_off, taper, cap, extra=()):
    parts = {n: {"move": [dx - XW, 0, 0]} for n in MOVING}
    parts.update({"尾座（正）": {"visible": not tail_off}, "后顶尖（正）": {"visible": not tail_off},
                  "尾座（偏）": {"visible": tail_off}, "后顶尖（偏）": {"visible": tail_off},
                  "工件（圆柱）": {"visible": not taper}, "工件（锥形）": {"visible": taper}})
    arrows = [{"from": (-30, -50, 40), "to": (L + 30, -50, 40), "color": "#5a9e6f", "text": "工作台运动方向", "textAt": "start", "dy": 26}]
    if tail_off:
        arrows.append({"from": (-30, 30 * e / L, 40), "to": (L + 30, -(L + 30) * e / L, 40), "color": "#c0504d", "text": "两顶尖连线",
                       "textAt": "end", "dx": -10, "dy": -12, "anchor": "end"})
    return {"parts": parts, "camera": CAM, "arrows": arrows,
            "texts": [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
                      {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"}, *extra]}


def traverse(tail_off, taper, cap):
    for i in range(16):
        v.add(st(25 + (145 - 25) * i / 15, tail_off, taper, cap), hold=0.12)


v.add(st(30, False, False, ("两顶尖连线与工作台运动方向平行", "Centre line parallel to the table travel")), hold=1.5)
traverse(False, False, ("砂轮相对工件走直线：磨出圆柱", "The wheel travels straight: a cylinder"))
v.add(st(140, True, False, ("尾座向离开砂轮的方向偏了 e（放大 500 倍）", "The tailstock is off by e, away from the wheel (×500)")), hold=2.0)
traverse(True, True, ("工件绕倾斜的连线转，砂轮仍走直线：尾座端磨得少", "The work turns about a tilted line: less is ground at the tail end"))
v.add(st(140, True, True, ("磨出锥形：尾座端大", "Ground to a taper: larger at the tailstock end"),
         extra=[{"pos": [0.45, 0.94], "text": f"e = 0.008 mm → 右轴承位比左大 {dd:.1f} µm", "fontSize": 24, "bold": True, "color": "#c0504d"}]), hold=3.0)
v.save("v54_3_1")
