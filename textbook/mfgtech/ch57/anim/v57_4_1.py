"""三维动画 57.4.1（配图 57.4.2）：SH-101 依次在数控车床（两顶尖精车）、滚齿机（心轴架上下顶尖）、键槽铣床（V 形块）、
外圆磨床（两顶尖）上装夹和加工。刀具、砂轮、顶尖、V 形块为示意；工件各工序的状态按 std/SH-101_process.yaml（route3d.sh101）。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, shapes as S, route3d as X  # noqa: E402

A = C.Assembly("装夹")
ST = {"op30": "work", "op40": "work", "op50": "work", "op70": "#9aa0a6"}
for s, col in ST.items():
    p = X.sh101(s, col)
    p.name = s
    A.add(p)
cone = [(-55.0, 0.0), (-55.0, 9.0), (-14.0, 9.0), (2.0, 0.0)]
A.add(C.Part("前顶尖", S.revolve(cone), "steel"))
A.add(C.Part("后顶尖", S.revolve([(136 - x, r) for x, r in cone]), "steel"))
A.add(C.Part("车刀", S.box(-4, 4, -4, 4, 0, 30), "steel_dark"))
A.add(C.Part("滚刀", S.cyl("y", (0, 0), 31.5, -30, 30), "#5f7e9c"))
A.add(C.Part("V 形块", S.prism("yz", [(-22, -26), (22, -26), (22, -6), (14.4, -6), (0, -14.4), (-14.4, -6), (-22, -6)], 4, 32), "#8f9aa5"))
A.add(C.Part("键槽铣刀", S.cyl("z", (0, 0), 3, 0, 40), "steel_dark"))
A.add(C.Part("砂轮", S.cyl("x", (0, 0), 70, -8, 8), "#c8c1b4"))
TOOLS = ("车刀", "滚刀", "键槽铣刀", "砂轮")
CAM = {"dir": [0.35, -1.1, 0.5], "fit": [[-60, -45, -45], [200, 160, 75]]}
v = R.Video(A, width=1280, height=720, fps=20)
SEG = X._segments("op30")[0]


def r_at(x):
    x0 = 0.0
    for d, L, _ in SEG:
        if x0 <= x <= x0 + L:
            return d / 2
        x0 += L
    return SEG[-1][0] / 2


def st(shaft, tool=None, pos=(0, 0, 0), deg=0.0, centres=True, vb=False, cap=("", "")):
    parts = {s: {"visible": s == shaft, "rot": [1, 0, 0, float(deg)]} for s in ST}
    for t in TOOLS:
        parts[t] = {"visible": t == tool, "move": [float(c) for c in pos]}
    if tool == "滚刀":
        parts["滚刀"]["rot"] = [0, 1, 0, float(deg * 2)]
    for c in ("前顶尖", "后顶尖"):
        parts[c] = {"visible": centres}
    parts["V 形块"] = {"visible": vb}
    return {"parts": parts, "camera": CAM, "texts": [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
                                                      {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"}]}


c30 = ("工序 30 精车：数控车床，两顶尖，ap 0.55、f 0.15、vc 150", "Op 30: between centres, ap 0.55, f 0.15, vc 150")
for k in range(41):
    x = 136 - 136 * k / 40
    v.add(st("op30", "车刀", (x, 0, r_at(x)), deg=k * 9, cap=c30), hold=0.06)
c40 = ("工序 40 滚齿：心轴架上下顶尖，m2 单头滚刀", "Op 40: hobbing between centres")
for k in range(41):
    v.add(st("op40", "滚刀", (96, 0, 26 + 31.5 - 4.5), deg=k * 6, cap=c40), hold=0.06)
c50 = ("工序 50 铣键槽：轴伸放在 V 形块上，Ø6 键槽铣刀分 5 层", "Op 50: V-block, Ø6 cutter, 5 layers")
for k in range(41):
    v.add(st("op50", "键槽铣刀", (8.5 + 19 * (k % 10) / 9, 0, 6.5 - 0.74 * (k // 10)), centres=False, vb=True, cap=c50), hold=0.06)
c70 = ("工序 70 磨外圆：修研中心孔后两顶尖装夹，砂轮 35 m/s", "Op 70: grinding between centres")
for k in range(41):
    x = 64.5 if k < 20 else 127.5
    v.add(st("op70", "砂轮", (x, 12.5 + 70, 0), deg=k * 9, cap=c70), hold=0.06)
v.add(st("op70", cap=("除铣键槽外，都顶在工序 20 钻出的同一对中心孔上", "All but the keyway on the same centre holes")), hold=2.5)
v.save("v57_4_1")
