"""三维动画 54.8.1（配图 54.8.1）：误差的“指纹”——锥形、鼓形、鞍形、弯曲、椭圆、三棱形逐个出现并转动，字幕给出最常见的来源
（与 hub/accuracy.py 的 SHAPES 一致）。误差放大画出；模型：factory/digital/models3d/errors3d.py。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from hub import accuracy as Acc  # noqa: E402
from models3d import core as C, errors3d as X, shapes as S  # noqa: E402

L, r = 120.0, 20.0
items = [("taper", X.shape_shaft("taper", L=L, r=r, amount=5.0), "锥形", "Taper"),
         ("drum", X.shape_shaft("drum", L=L, r=r, amount=4.0), "鼓形（中间大）", "Barrel"),
         ("saddle", X.shape_shaft("saddle", L=L, r=r, amount=4.0), "鞍形（中间小）", "Saddle"),
         ("bent", S.rot(X.bent_shaft(L=L, r=r, bow=4.0), ax=90), "弯曲", "Bent"),
         ("ellipse", X.section_shaft(X.lobed(r, 2, 2.0), L=L), "椭圆（二阶）", "Oval (2 lobes)"),
         ("lobe3", X.section_shaft(X.lobed(r, 3, 1.6), L=L), "三棱形（三阶）", "Three lobes")]
CAUSE = {"taper": Acc.SHAPES["taper"]["causes"][0], "drum": Acc.SHAPES["drum"]["causes"][0], "saddle": Acc.SHAPES["saddle"]["causes"][0],
         "bent": "残余应力释放（铣键槽、淬火后）；工件热伸长被顶尖顶住", "ellipse": Acc.SHAPES["ellipse"]["causes"][0], "lobe3": Acc.SHAPES["lobe3"]["causes"][0]}
a = C.Assembly("误差的指纹")
for name, shp, *_ in items:
    a.add(C.Part(name, shp, "work"))
CAM = {"dir": [0.3, -1, 0.45], "fit": [[-10, -40, -40], [L + 10, 40, 40]]}
v = R.Video(a, width=1280, height=720, fps=20)
for k, (name, _, zh, en) in enumerate(items):
    for j in range(24):
        ang = 360.0 * j / 24
        parts = {n: {"visible": n == name, "rot": [1, 0, 0, ang, 0, 0, 0]} for n, *_ in items}
        v.add({"parts": parts, "camera": CAM,
               "texts": [{"pos": [0.03, 0.08], "text": f"{k + 1}/6  {zh}", "fontSize": 30, "bold": True},
                         {"pos": [0.03, 0.135], "text": en + "（误差放大画出）", "fontSize": 18, "color": "#5b6770"},
                         {"pos": [0.03, 0.9], "text": "常见来源：" + CAUSE[name], "fontSize": 22, "color": "#c0504d"}]}, hold=0.09)
v.save("v54_8_1")
