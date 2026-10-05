"""三维动画 52.10.1（配图 52.10.2）：JJ-301-50 装上铣床后用检验棒找正——千分表吸在主轴上、测杆压在检验棒侧母线，
工作台带着夹具沿 x 移动，看读数变化；超差就松开 T 形槽螺栓，轻敲夹具一端，再测，直到 60 mm 长度上读数变化不超过 0.006（0.01/100）。
三维模型取自数字工厂（factory/digital/models3d/jj30150.py），逐帧渲染（textbook/tools/render3d.py 的 Video）。读数为教学示例。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, jj30150 as J, machines as MA, shapes as S  # noqa: E402

g = J.geometry()
zc, rb = g["zc"], g["d_g"] / 2
a = J.assembly("op40", with_work=False, with_table=True)
a.add(C.Part("检验棒 Ø40.3", S.cyl("x", (0, zc), rb, -30, 90), "glass"))
MOVE = [p.name for p in a.parts]                      # 工作台、夹具、检验棒一起移动
x_tip = 0.0
a.add(C.Part("铣床主轴（局部）", S.cyl("z", (x_tip, -rb - 64), 40, zc + 110, zc + 220), "steel_dark", tags=("nocut",)))
a.add(C.Part("磁力表座", S.cyl("z", (x_tip, -rb - 64), 24, zc + 70, zc + 110), "rubber"))
for p in MA.dial_indicator(tip=(x_tip, -rb, zc), stem_dir=(0, -1, 0), base_at=(x_tip, -rb - 64, zc + 110)).parts:
    if p.name != "表座":
        a.add(p)
CAM = {"dir": [0.85, -1.25, 0.65], "fit": [[-150, -170, -80], [220, 120, 250]]}
v = R.Video(a, width=1280, height=720, fps=20)
L = 60.0                                              # 测量长度（检验棒在 V 形块上的一段）


def st(dx, reading, cap, col="#1d2327"):
    parts = {n: {"move": [dx, 0, 0]} for n in MOVE}
    return {"parts": parts, "camera": CAM,
            "texts": [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
                      {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"},
                      {"pos": [0.72, 0.3], "text": f"千分表读数 {reading:+.3f} mm", "fontSize": 26, "bold": True, "color": col}]}


def sweep(slope, cap, n=30, col="#1d2327"):
    for i in range(n):
        t = R.ease(i / (n - 1))
        v.add(st(-L * t, slope * L * t, cap, col))       # 工作台向 −x 移，测点沿检验棒从 x=0 走到 x=60
    v.add(st(-L, slope * L, cap, col), hold=0.8)


def back(slope, cap, n=14):
    for i in range(n):
        t = R.ease(i / (n - 1))
        v.add(st(-L * (1 - t), slope * L * (1 - t), cap))


c1 = ("1  表在检验棒左端对零，摇工作台", "Zero the indicator at the left end, then traverse the table")
v.add(st(0, 0.0, c1), hold=0.8)
sweep(0.014 / L, ("2  走过 60 mm，读数变了 0.014", "Over 60 mm the reading changes by 0.014"), col="#c0504d")
v.add(st(-L, 0.014, ("超过 0.006（0.01/100）：夹具歪了", "More than 0.006 (0.01/100): the fixture is skewed"), "#c0504d"), hold=1.2)
back(0.014 / L, ("3  松开 T 形槽螺栓，轻敲夹具右端，再拧紧", "Loosen the T-bolts, tap the right end, tighten again"))
v.add(st(0, 0.0, ("3  松开 T 形槽螺栓，轻敲夹具右端，再拧紧", "Loosen the T-bolts, tap the right end, tighten again")), hold=1.0)
sweep(0.004 / L, ("4  再测：60 mm 上变化 0.004，合格", "Re-check: 0.004 over 60 mm — within limits"), col="#5a9e6f")
v.add(st(-L, 0.004, ("找正结果记入夹具使用记录", "Record the alignment in the fixture log"), "#5a9e6f"), hold=2.0)
v.save("v52_10_1")
