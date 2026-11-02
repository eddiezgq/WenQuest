"""三维动画 56.2.1（配图 56.2.2）：SH-101 输入轴组件——依次装上平键、油封和两个 6205 轴承；组件转动，逐一指出每个表面在装配中起什么作用。
模型：factory/digital/models3d/route3d.py 的 sh101_assembly（尺寸按 std/SH-101_part.yaml）；轴承、油封、平键为示意。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, shapes as S, route3d as X  # noqa: E402

A = C.Assembly("输入轴组件")
sh = X.sh101_assembly("op70")
SHAFT = sh.parts[0].name
A.add(sh.parts[0])
XL, XR = 36 + 20 + 8.5, 136 - 8.5                      # 两个轴承位的中点
A.add(C.Part("左轴承", S.tube("x", (0, 0), 26, 12.5, XL - 7.5, XL + 7.5), "steel"))
A.add(C.Part("右轴承", S.tube("x", (0, 0), 26, 12.5, XR - 7.5, XR + 7.5), "steel"))
A.add(C.Part("平键", S.box(5.5, 30.5, -3, 3, 6.5, 12.5), "steel_dark"))
A.add(C.Part("油封", S.tube("x", (0, 0), 20, 12.05, 44, 51), "#3d3d3d"))
CAM = {"dir": [0.45, -1.15, 0.55], "fit": [[-65, -30, -30], [200, 30, 30]]}
v = R.Video(A, width=1280, height=720, fps=20)
OUT = {"平键": [0, 0, 40], "油封": [-55, 0, 0], "左轴承": [-110, 0, 0], "右轴承": [55, 0, 0]}


def st(off, deg=0.0, cap=("", ""), note=None):
    parts = {n: {"move": [float(c * off.get(n, 0.0)) for c in OUT[n]], "rot": [1, 0, 0, float(deg)]} for n in OUT}
    parts[SHAFT] = {"rot": [1, 0, 0, float(deg)]}
    tx = [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
          {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"}]
    if note:
        tx.append({"pos": [0.03, 0.86], "text": note, "fontSize": 22, "bold": True, "color": "#b5523b"})
    return {"parts": parts, "camera": CAM, "texts": tx}


off = {n: 1.0 for n in OUT}
v.add(st(off, cap=("SH-101 输入齿轮轴：齿轮与轴一体，20CrMnTi 渗碳淬火", "SH-101 input pinion shaft, gear integral, case-hardened")), hold=2.0)
for n, cap in (("平键", ("装平键：轴伸 Ø20 j6 的键槽 6 N9 传递转矩", "Key: the 6 N9 keyway on the Ø20 j6 extension carries torque")),
               ("油封", ("装油封：唇口压在密封轴颈 Ø24 上，Ra 0.8、不得有螺旋纹", "Seal: the lip runs on the Ø24 seal journal, Ra 0.8, no lead")),
               ("左轴承", ("装左轴承 6205：轴承位 Ø25 k6，靠在轴肩上定轴向位置", "Left 6205 bearing on Ø25 k6 against the shoulder")),
               ("右轴承", ("装右轴承 6205：两处轴承位的公共轴线 A–B 是全轴的基准", "Right bearing: the common axis A–B is the datum of the shaft"))):
    for k in range(13):
        off[n] = 1 - R.ease(k / 12)
        v.add(st(off, cap=cap), hold=0.07)
    v.add(st(off, cap=cap), hold=1.2)
caps = [("齿轮 m2 z24、8 级：齿顶圆对 A–B 的跳动 0.03", "Gear m2 z24, grade 8; tip runout to A–B 0.03", "齿轮"),
        ("轴承位要磨：IT6、Ra 0.8，淬硬 58–62 HRC", "Bearing seats: IT6, Ra 0.8, ground after hardening", "轴承位"),
        ("这些要求决定了路线：哪些在淬火前做完，哪些淬火后磨", "These requirements decide the route", "路线")]
for i, (c0, c1, _) in enumerate(caps):
    for k in range(25):
        v.add(st(off, deg=(i * 24 + k) * 5, cap=(c0, c1)), hold=0.06)
    v.add(st(off, deg=(i * 24 + 24) * 5, cap=(c0, c1)), hold=1.0)
v.add(st(off, deg=360, cap=caps[-1][:2], note="工艺审查要从零件在装配里的作用读起"), hold=2.5)
v.save("v56_2_1")
