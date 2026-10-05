"""三维动画 52.7.1（配图 52.7.3）：翻转式钻模——钻完一个面上的孔，把钻模连同工件绕底边翻转 90°，再钻下一个面。
三维模型取自数字工厂（factory/digital/models3d/typical.py 的 drill_tumble），逐帧渲染（textbook/tools/render3d.py 的 Video）。
几何：夹具体 x、y 为 −55…55，z 为 0…110，支脚底面 z = −10。绕 +x 底边（55, 0, −10）沿 +y 轴转 90°，原来的左侧面（−x）朝上，
它上面的钻套轴心转到 x = 120；回正后绕 −y 底边（0, −55, −10）沿 +x 轴转 90°，原来的后面（+y）朝上，钻套轴心转到 y = −120。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, typical as TY, shapes as S  # noqa: E402

L = 110.0
a = TY.drill_tumble()
a.add(C.Part("钻头", S.cyl("z", (0, 0), 4, 0, 80) + S.cyl("z", (0, 0), 9, 80, 140), "tool", tags=("nocut",)))
a.add(C.Part("钻床工作台", S.box(-170, 250, -220, 130, -32, -10), "steel_dark", tags=("nocut",)))
JIG = [p.name for p in a.parts if p.name not in ("钻头", "钻床工作台")]
CAM = {"dir": [0.9, -1.3, 0.8], "fit": [[-120, -190, -30], [200, 90, 250]]}
v = R.Video(a, width=1280, height=720, fps=20)
TOP_Y = (0.0, 1.0, 0.0, 55.0, 0.0, -10.0)      # 绕 +y 轴、过 +x 底边
TOP_X = (1.0, 0.0, 0.0, 0.0, -55.0, -10.0)     # 绕 +x 轴、过 −y 底边


def st(rot, deg, drill, cap):
    parts = {}
    for n in JIG:
        if rot and deg:
            ax, ay, az, px, py, pz = rot
            parts[n] = {"rot": [ax, ay, az, deg, px, py, pz]}
    parts["钻头"] = {"move": list(drill)}
    return {"parts": parts, "camera": CAM, "texts": [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
                                                     {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"}]}


def go(n, f, hold=0.0):
    for i in range(n):
        v.add(f(R.ease(i / max(1, n - 1))))
    if hold:
        v.add(f(1.0), hold=hold)


def drill(rot, deg, x, y, z_top, z_down, cap):
    go(8, lambda t: st(rot, deg, (x, y, z_top + 40 * (1 - t)), cap))
    go(14, lambda t: st(rot, deg, (x, y, z_top + (z_down - z_top) * t), cap))
    go(10, lambda t: st(rot, deg, (x, y, z_down + (z_top + 40 - z_down) * t), cap), hold=0.3)


c1 = ("1  钻顶面上的孔：钻套引导钻头", "Drill the top-face hole through its bushing")
drill(None, 0, 0, 0, L + 10, L - 20, c1)
c2 = ("2  绕底边翻转 90°：原来的左侧面朝上", "Tumble 90° about the bottom edge: the left face comes up")
go(24, lambda t: st(TOP_Y, 90 * t, (0, 0, L + 50), c2), hold=0.4)
c3 = ("3  钻左侧面上的孔：每个面都有自己的钻套", "Drill the left-face hole: every face has its own bushing")
drill(TOP_Y, 90, 120, 0, 110, 80, c3)
c4 = ("4  翻回来，再绕前底边翻转 90°：后面朝上", "Tumble back, then 90° about the front edge: the back face comes up")
go(18, lambda t: st(TOP_Y, 90 * (1 - t), (60 * (1 - t), -60 * t, L + 50), c4))
go(24, lambda t: st(TOP_X, 90 * t, (0, -60 - 60 * t, L + 50), c4), hold=0.4)
c5 = ("5  钻后面上的孔：一次装夹钻完三个方向的孔", "Drill the back-face hole: three directions in one clamping")
drill(TOP_X, 90, 0, -120, 110, 80, c5)
v.add(st(TOP_X, 90, (0, -120, 170), ("翻转式钻模适合小件：钻模连同工件一般不超过十来千克", "Tumble jigs suit small parts: jig plus part around ten kilograms or less")), hold=2.2)
v.save("v52_7_1")
