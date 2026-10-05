"""三维动画 53.1.2（配图 53.1.2）：铣完键槽再磨齿轮位——砂轮磨去一层，下母线向轴心移动，槽底不动，d − t₁ 变小（键槽相对变深）。
先按工序卡的 H = 35.15（−0.03/−0.20）铣：取公差中间值，磨后 d − t₁ ≈ 34.885，合格；再演示照图纸尺寸 35（0/−0.2）铣：中间值磨后约 34.75，低于下限 34.8，整批偏深。
截面过键槽中部；磨削余量放大画出（画成 2 mm），右侧读数按真实尺寸（单边 0.15 mm）折算。模型：factory/digital/models3d，逐帧渲染（render3d.Video）。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, shapes as S  # noqa: E402

b, z_bot = 12.0, 15.0
RX0, RX1 = 22.0, 20.0                         # 画出来的磨前、磨后半径（放大）
N = 9
a = C.Assembly("磨削后键槽变深")
for i in range(N):
    r = RX0 - (RX0 - RX1) * i / (N - 1)
    a.add(C.Part(f"轴{i}", S.cyl("x", (0, 0), r, -15, 15) - S.box(-16, 16, -b / 2, b / 2, z_bot, 40), "work"))
a.add(C.Part("砂轮", S.cyl("x", (0, -80), 55, -18, 18), "#9aa3ab"))
CAM = {"dir": [-1, 0, 0], "fit": [[0, -45, -30], [0, 45, 30]]}
v = R.Video(a, width=1280, height=720, fps=20)


def st(i, H_real, cap, wheel_dy=0.0):
    t = i / (N - 1)
    r_draw = RX0 - (RX0 - RX1) * t
    r_real = 20.15 - 0.15 * t
    a0 = H_real - 20.15 + r_real
    ok = a0 >= 34.8 - 1e-9
    parts = {f"轴{j}": {"visible": j == i} for j in range(N)}
    parts["砂轮"] = {"move": [0, 0, 25.0 - r_draw]}
    # 砂轮放在 −y 一侧，磨削点在 −y 方向；下母线在 −z
    return {"parts": parts, "camera": CAM,
            "dims": [{"a": (16, 2, -r_draw), "b": (16, 2, z_bot), "off": (0, 0, 0), "text": "d − t₁", "color": "#c0504d"}],
            "points": [{"at": (16, 0, -r_draw), "r": 5, "color": "#c0504d"}, {"at": (16, 0, -RX0), "r": 4, "color": "#4f7fb8", "text": "磨前下母线", "dx": -150, "dy": -6}],
            "texts": [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
                      {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"},
                      {"pos": [0.68, 0.3], "text": f"铣键槽 H = {H_real:.3f}（取公差中间）", "fontSize": 22},
                      {"pos": [0.68, 0.36], "text": f"齿轮位半径 {r_real:.3f}（磨去单边 0.15）", "fontSize": 22},
                      {"pos": [0.68, 0.44], "text": (f"d − t₁ = {a0:.3f}" if i > 0 else "d − t₁ 还没形成（磨削后才有）"), "fontSize": 30 if i > 0 else 22, "bold": True, "color": ("#5a9e6f" if ok else "#c0504d") if i > 0 else "#5b6770"},
                      {"pos": [0.68, 0.5], "text": "图纸 35（0/−0.2），即 34.8–35.0", "fontSize": 18, "color": "#5b6770"}]}


HC = 35.15 - (0.03 + 0.20) / 2          # 工序卡 35.15（−0.03/−0.20）的中间值
HN = 35.0 - 0.1                          # 照图纸 35（0/−0.2）铣的中间值


def grind(H, cap):
    for i in range(N):
        v.add(st(i, H, cap), hold=0.25)


v.add(st(0, HC, ("按工序卡 H = 35.15（−0.03/−0.20）铣键槽", "Keyway milled: H = 35.15 from the turned bottom line")), hold=1.5)
grind(HC, ("磨齿轮位：下母线向轴心移动，槽底不动", "Grinding moves the bottom line in; the slot bottom stays"))
v.add(st(N - 1, HC, ("磨后 d − t₁ 在 34.8–35.0 之内：合格（余量放大画出）", "After grinding d − t₁ is within 34.8–35.0")), hold=2.0)
v.add(st(0, HN, ("换一种做法：照图纸尺寸 35 铣键槽", "Now mill to the drawing size 35 instead")), hold=1.5)
grind(HN, ("同样磨去 0.15", "Grind the same 0.15"))
v.add(st(N - 1, HN, ("磨后 d − t₁ 低于下限：键槽相对变深，没法返修", "Below the lower limit: the keyway is too deep")), hold=2.5)
v.save("v53_1_2")
