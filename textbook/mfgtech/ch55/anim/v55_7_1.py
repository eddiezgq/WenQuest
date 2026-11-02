"""三维动画 55.7.1（配图 55.7.1）：滚压 SH-301 左轴承位旁的轴肩圆角——滚压头沿滚压力方向靠近、压上圆角，工件转几圈，
被压过的圆角表面（示意的颜色）逐圈形成压平的表面和下面的残余压应力层。读数是示意值（Ra、压应力层深度取 55.7 节的常见范围）。
模型：factory/digital/models3d/surface3d.py 的 rolling_fillet。"""
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, shapes as S, surface3d as X  # noqa: E402

a = X.rolling_fillet()
rx, ry, _ = a.anchors["roll"]
px, py, _ = a.anchors["push"]
n = math.hypot(rx - px, ry - py)
ux, uy = (px - rx) / n, (py - ry) / n                       # 退回的方向（与滚压力相反）
a.add(C.Part("滚压层", S.tube("x", (0, 0), 17.62, 16.9, rx - 6, rx), "#4f7fb8"))
TOOL = ("滚轮", "滚压头")
CAM = {"dir": [0.35, -1.0, 0.55], "fit": [[5, -80, -30], [125, 30, 30]]}
v = R.Video(a, width=1280, height=720, fps=20)


def st(back, deg, layer, cap, ra=None, depth=None):
    parts = {t: {"move": [ux * back, uy * back, 0]} for t in TOOL}
    parts["SH-301"] = {"rot": [1, 0, 0, deg]}
    parts["滚压层"] = {"visible": layer > 0.01, "opacity": max(0.55, min(1.0, layer)), "rot": [1, 0, 0, deg]}
    tx = [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
          {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"}]
    if ra is not None:
        tx += [{"pos": [0.58, 0.80], "text": f"圆角表面 Ra ≈ {ra:.1f} µm", "fontSize": 24, "bold": True},
               {"pos": [0.58, 0.86], "text": f"压应力层深度 ≈ {depth:.1f} mm（示意）", "fontSize": 24, "bold": True, "color": "#4f7fb8"}]
    return {"parts": parts, "camera": CAM, "texts": tx}


v.add(st(30, 0, 0, ("轴肩圆角：应力集中、疲劳的薄弱环节", "The shoulder fillet: a stress raiser, a fatigue weak spot"), 1.6, 0.0), hold=2.0)
for k in range(11):
    v.add(st(30 * (1 - R.ease(k / 10)), 0, 0, ("滚压头沿滚压力的方向压上圆角", "The rolling head presses onto the fillet"), 1.6, 0.0), hold=0.1)
TURNS = 5
for k in range(TURNS * 12 + 1):
    t = k / (TURNS * 12)
    v.add(st(0, 30 * k, t, ("工件转动，滚轮把峰压平、填进谷里：表层塑性变形", "The work turns; the roller flattens the peaks into the valleys"),
             1.6 - 1.3 * (1 - math.exp(-4 * t)), 0.8 * (1 - math.exp(-4 * t))), hold=0.08)
for k in range(11):
    v.add(st(30 * R.ease(k / 10), TURNS * 360, 1, ("滚压完成：表面变光、硬化，下面是残余压应力层", "Done: a smoother, harder surface over a layer in compression"), 0.3, 0.8), hold=0.1)
v.add(st(30, TURNS * 360, 1, ("滚压纠正不了形状误差：滚压前的尺寸要留出滚压后直径的少量变化", "Rolling cannot fix form errors; allow for the small diameter change"), 0.3, 0.8), hold=3.0)
v.save("v55_7_1")
