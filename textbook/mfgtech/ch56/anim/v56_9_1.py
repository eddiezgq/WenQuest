"""三维动画 56.9.1（配图 56.9.3）：SH-101 逐工序变化——下料、粗车、精车、滚齿、铣键槽、渗碳淬火、磨外圆；
每一步写出这道工序的定位基准和加工内容（std/SH-101_route.yaml）。模型：factory/digital/models3d/route3d.py 的 sh101。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, route3d as X  # noqa: E402

STEPS = [("blank", "work", "工序 10 下料：锯 Ø60 × 142", "Op 10 saw Ø60 × 142", "毛坯：热轧圆钢"),
         ("op20", "work", "工序 20 粗车：车端面、钻中心孔，粗车各外圆", "Op 20 rough turning, centre holes", "基准：棒料外圆（粗基准，只用一次）"),
         ("op30", "work", "工序 30 精车：轴承位等留磨量，齿顶圆车到尺寸", "Op 30 finish turning, grind stock left", "基准：两端中心孔"),
         ("op40", "work", "工序 40 滚齿 m2 z24：按 7 级加工", "Op 40 hobbing to grade 7", "基准：两端中心孔"),
         ("op50", "work", "工序 50 铣键槽 6 N9", "Op 50 keyway", "基准：轴伸外圆（V 形块）"),
         ("op60", "#8a8f96", "工序 60 渗碳淬火：表面 58–62 HRC", "Op 60 carburize and harden", "从此只能磨"),
         ("op70", "#b8bcc2", "工序 70 修研中心孔，粗磨、精磨", "Op 70 lap centres, grind", "基准：修研后的中心孔")]
A = C.Assembly("SH-101 路线")
for s, col, *_ in STEPS:
    p = X.sh101(s if s != "op60" else "op50", col)
    p.name = s
    A.add(p)
CAM = {"dir": [0.4, -1.1, 0.5], "fit": [[-10, -32, -32], [146, 32, 32]]}
v = R.Video(A, width=1280, height=720, fps=20)
deg = 0.0
for i, (s, _, c0, c1, note) in enumerate(STEPS):
    for k in range(30):
        deg += 4
        parts = {x[0]: {"visible": x[0] == s, "rot": [1, 0, 0, deg]} for x in STEPS}
        bar = "  →  ".join(("■" if j <= i else "□") for j in range(len(STEPS)))
        v.add({"parts": parts, "camera": CAM, "texts": [
            {"pos": [0.03, 0.08], "text": c0, "fontSize": 26, "bold": True},
            {"pos": [0.03, 0.13], "text": c1, "fontSize": 18, "color": "#5b6770"},
            {"pos": [0.03, 0.86], "text": note, "fontSize": 24, "bold": True, "color": "#b5523b"},
            {"pos": [0.60, 0.86], "text": bar, "fontSize": 18, "color": "#5b6770"}]}, hold=0.08)
v.save("v56_9_1")
