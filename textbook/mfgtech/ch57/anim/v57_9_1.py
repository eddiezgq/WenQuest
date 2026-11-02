"""三维动画 57.9.1（配图 57.9.4）：首件检验——磨后的 SH-101 放在偏摆检查仪的两顶尖上，工件转一圈，千分表依次测两处轴承位的
径向圆跳动（要求 0.010，示意读数），再用杠杆千分尺测直径（Ø25 k6：25.002–25.015，示意读数）。全部合格，首件检验签字后才继续生产。"""
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, shapes as S, route3d as X  # noqa: E402

A = C.Assembly("首件检验")
A.add(C.Part("工件", X.sh101("op70", "#b8bcc2").shape, "#b8bcc2"))
cone = [(-55.0, 0.0), (-55.0, 9.0), (-14.0, 9.0), (2.0, 0.0)]
A.add(C.Part("左顶尖", S.revolve(cone), "steel"))
A.add(C.Part("右顶尖", S.revolve([(136 - x, r) for x, r in cone]), "steel"))
A.add(C.Part("底座", S.box(-60, 196, -40, 40, -60, -48), "#8f9aa5"))
A.add(C.Part("表座", S.box(-8, 8, 26, 42, -48, 30), "#7a8089"))
A.add(C.Part("千分表", S.cyl("y", (0, 30), 14, 14, 22) + S.cyl("z", (0, 0), 1.2, 12.5, 30), "#d9dde1"))
CAM = {"dir": [0.3, -1.0, 0.55], "fit": [[-60, -45, -60], [200, 45, 60]]}
v = R.Video(A, width=1280, height=720, fps=20)


def st(x, deg, cap, read):
    tx = [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
          {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"}]
    tx += [{"pos": [0.55, 0.20 + 0.06 * i], "text": t, "fontSize": 24, "bold": True, "color": c} for i, (t, c) in enumerate(read)]
    return {"parts": {"工件": {"rot": [1, 0, 0, float(deg)]}, "表座": {"move": [float(x), 0.0, 0.0]}, "千分表": {"move": [float(x), 0.0, 0.0]}},
            "camera": CAM, "texts": tx}


GOOD = "#2f8f5b"
for k in range(37):
    tir = 0.004 * abs(math.sin(math.radians(k * 10)))
    v.add(st(64.5, k * 10, ("左轴承位：工件转一圈，读千分表的最大与最小值", "Left seat: one turn, max − min"),
             [(f"跳动 {tir * 1000:.1f} µm（要求 ≤ 10）", GOOD)]), hold=0.07)
for k in range(21):
    v.add(st(64.5 + (127.5 - 64.5) * k / 20, 360, ("移到右轴承位", "Move to the right seat"), [("左轴承位跳动 4 µm 合格", GOOD)]), hold=0.05)
for k in range(37):
    tir = 0.006 * abs(math.sin(math.radians(k * 10)))
    v.add(st(127.5, 360 + k * 10, ("右轴承位", "Right seat"), [("左轴承位跳动 4 µm 合格", GOOD), (f"右轴承位 {tir * 1000:.1f} µm", GOOD)]), hold=0.07)
v.add(st(127.5, 720, ("杠杆千分尺测直径（示意读数）：Ø25.008、Ø25.010", "Diameters 25.008, 25.010 (illustr.)"),
         [("跳动 4、6 µm 合格", GOOD), ("直径在 25.002–25.015 内，合格", GOOD), ("首件合格，签字后继续生产", "#b5523b")]), hold=3.0)
v.save("v57_9_1")
