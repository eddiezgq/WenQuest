"""三维动画 51.3.2（配图 51.3.2）：3–2–1 定位——工件先落到底面三个支承钉上，再推向侧面两个，最后推向端面一个；
每接触一组，右上角的“还能动的方式”就少几个。模型：factory/digital/models3d（elements.support_pin），逐帧渲染（render3d.Video）。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, elements as E, shapes as S  # noqa: E402

BL, BB, BH = 160.0, 90.0, 50.0
blue, orange, red = "#4f7fb8", "#d98c3a", "#c0504d"
a = C.Assembly("六点定位")
a.add(C.Part("夹具体", S.box(-30, BL + 20, -20, BB + 10, -30, -10) + S.box(-30, -14, -20, BB + 10, -10, 70) + S.box(-30, BL + 20, BB + 10, BB + 26, -30, 70), "cast"))
for i, (x, y) in enumerate([(25, 18), (BL - 25, 18), (BL / 2, BB - 18)]):
    a.add(C.Part(f"底{i}", E.support_pin("A", 12, 10, at=(x, y, 0)), blue))
for i, x in enumerate((25, BL - 25)):
    a.add(C.Part(f"侧{i}", S.move(S.rot(E.support_pin("A", 12, 10), 90, 0, 0), x, BB, 25), orange))
a.add(C.Part("端", S.move(S.rot(E.support_pin("A", 12, 10), 0, -90, 0), 0, BB / 2, 25), red))
a.add(C.Part("工件", S.box(0, BL, 0, BB, 0, BH), "work_cut", opacity=0.6))
CAM = {"dir": [0.75, -1.3, 0.9], "fit": [[-30, -40, -30], [BL + 30, BB + 26, 140]]}
v = R.Video(a, width=1280, height=720, fps=20)
ALL = ["沿 x 移动", "沿 y 移动", "沿 z 移动", "绕 x 转动", "绕 y 转动", "绕 z 转动"]


def st(pos, rz, free, cap):
    x, y, z = pos
    s = {"parts": {"工件": {"move": [x, y, z], "rot": [0, 0, 1, rz, BL / 2 + x, BB / 2 + y, 0]}}, "camera": CAM,
         "texts": [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
                   {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"},
                   {"pos": [0.74, 0.22], "text": f"还能动的方式：{len(free)} 个", "fontSize": 24, "bold": True}]}
    for i, n in enumerate(ALL):
        s["texts"].append({"pos": [0.76, 0.28 + 0.045 * i], "text": ("○ " if n in free else "● ") + n, "fontSize": 19,
                           "color": "#1d2327" if n in free else "#9aa3ab"})
    return s


def go(n, f, hold=0.0):
    for i in range(n):
        v.add(f(R.ease(i / max(1, n - 1))))
    if hold:
        v.add(f(1.0), hold=hold)


free = list(ALL)
c0 = ("自由的工件：六个自由度", "A free part: six degrees of freedom")
go(20, lambda t: st((14, -14, 60), 6 * (1 - t) + 6 * t, free, c0), hold=0.5)
c1 = ("1  落到底面三个支承钉上", "1  Set it down on three pins below")
go(20, lambda t: st((14, -14, 60 * (1 - t)), 6, free, c1))
free = [f for f in free if f not in ("沿 z 移动", "绕 x 转动", "绕 y 转动")]
v.add(st((14, -14, 0), 6, free, ("1  底面三点：限制 z、绕 x、绕 y", "Three points: z and rotations about x and y")), hold=1.2)
c2 = ("2  推向侧面两个支承钉，转正", "2  Push it against the two side pins; it turns square")
go(22, lambda t: st((14, -14 * (1 - t), 0), 6 * (1 - t), free, c2))
free = [f for f in free if f not in ("沿 y 移动", "绕 z 转动")]
v.add(st((14, 0, 0), 0, free, ("2  侧面两点：限制 y、绕 z", "Two points: y and rotation about z")), hold=1.2)
c3 = ("3  推向端面一个支承钉", "3  Push it against the end pin")
go(16, lambda t: st((14 * (1 - t), 0, 0), 0, free, c3))
free = []
v.add(st((0, 0, 0), 0, free, ("3  端面一点：限制 x——六个自由度全部限制", "One point: x — all six are fixed")), hold=1.5)
v.add(st((0, 0, 0), 0, free, ("然后夹紧：夹紧力压向这三个面，不破坏定位", "Then clamp toward these faces without disturbing the location")), hold=2.0)
v.save("v51_3_2")
