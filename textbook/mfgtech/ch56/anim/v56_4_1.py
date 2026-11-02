"""三维动画 56.4.1（配图 56.4.2）：基准统一——SH-101 依次装在数控车床（精车）、滚齿机、外圆磨床的两顶尖之间，
每台机床的顶尖都顶在工序 20 钻出的同一对中心孔上；渗碳淬火后先修研中心孔再磨。刀具、砂轮、顶尖为示意。
模型：factory/digital/models3d/route3d.py 的 sh101（各工序状态，尺寸按 std/SH-101_route.yaml）。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, shapes as S, route3d as X  # noqa: E402

A = C.Assembly("基准统一")
ST = {"op30": "work", "op40": "work", "op70": "#9aa0a6"}
for s, col in ST.items():
    p = X.sh101(s, col)
    p.name = s
    A.add(p)
cone = [(-55.0, 0.0), (-55.0, 9.0), (-14.0, 9.0), (2.0, 0.0)]
A.add(C.Part("前顶尖", S.revolve(cone), "steel"))
A.add(C.Part("后顶尖", S.revolve([(136 - x, r) for x, r in cone]), "steel"))
A.add(C.Part("车刀", S.box(-4, 4, -4, 4, 0, 30), "steel_dark"))
A.add(C.Part("滚刀", S.cyl("y", (0, 0), 25, -30, 30), "#5f7e9c"))
A.add(C.Part("砂轮", S.cyl("x", (0, 0), 70, -6, 6), "#c8c1b4"))
TOOLS = ("车刀", "滚刀", "砂轮")
CAM = {"dir": [0.35, -1.1, 0.5], "fit": [[-60, -45, -45], [200, 160, 75]]}
v = R.Video(A, width=1280, height=720, fps=20)
XG = 36 + 20 + 17 + 8 + 15                          # 齿轮中点
SEGS = X._segments("op30")[0]


def r_at(x):
    """精车后 x 处的半径（车刀刀尖贴着工件走）。"""
    x0 = 0.0
    for d, L, _ in SEGS:
        if x0 <= x <= x0 + L:
            return d / 2
        x0 += L
    return SEGS[-1][0] / 2


def st(shaft, tool=None, tx=0.0, tz=0.0, deg=0.0, cap=("", ""), note=None, ty=0.0):
    parts = {s: {"visible": s == shaft, "rot": [1, 0, 0, float(deg)]} for s in ST}
    for t in TOOLS:
        parts[t] = {"visible": t == tool, "move": [float(tx), float(ty), float(tz)]}
    if tool == "滚刀":
        parts[t] = parts["滚刀"]
        parts["滚刀"]["rot"] = [0, 1, 0, float(deg * 2)]
    texts = [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
             {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"},
             {"pos": [0.03, 0.88], "text": "两端中心孔：工序 20 钻出，一直用到磨削", "fontSize": 22, "bold": True, "color": "#b5523b"}]
    if note:
        texts.append({"pos": [0.55, 0.80], "text": note, "fontSize": 22, "bold": True})
    return {"parts": parts, "camera": CAM, "texts": texts}


v.add(st("op30", cap=("工序 30 精车：数控车床，两顶尖装夹", "Op 30 finish turning between centres")), hold=1.5)
for k in range(41):
    v.add(st("op30", "车刀", 136 - 136 * k / 40, r_at(136 - 136 * k / 40), deg=k * 9, cap=("工序 30 精车：数控车床，两顶尖装夹", "Op 30 finish turning between centres"),
             note="各外圆一次装夹车出，同轴"), hold=0.06)
for k in range(41):
    v.add(st("op40", "滚刀", XG, 21.5 + 25 - 2, deg=k * 6, cap=("工序 40 滚齿：滚齿机，仍顶在这对中心孔上", "Op 40 hobbing, the same centre holes"),
             note="齿圈与轴承位同一基准"), hold=0.06)
v.add(st("op70", cap=("工序 60 渗碳淬火后：先修研中心孔", "After carburizing: lap the centre holes first")), hold=2.0)
for k in range(41):
    x = 64.5 if k < 20 else 127.5
    v.add(st("op70", "砂轮", x, 0.0, ty=12.5 + 70, deg=k * 9, cap=("工序 70 磨外圆：外圆磨床，两顶尖", "Op 70 grinding between centres"),
             note="基准不变，误差不累积"), hold=0.06)
v.add(st("op70", cap=("车、滚、磨用同一组精基准：基准统一", "One set of datums for turning, hobbing, grinding")), hold=2.5)
v.save("v56_4_1")
