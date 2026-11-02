"""三维动画 57.5.1（配图 57.5.4）：两顶尖之间半精车 SH-101 轴承位时的让刀——车刀从尾座走向头架，背向力使头架、尾座、刀架和工件
让开，车出的直径比调刀尺寸大 2y（第 54 章 hub/accuracy.py compliance_between_centers；头架、尾座 20 000 N/mm，刀架 50 000 N/mm）。
工件的让开量放大 800 倍画出（只画头架、尾座让开使工件平移和转动的部分）；读数是真实值。先用工艺规程的 ap 0.55、f 0.15，
再用 ap 1.1、f 0.3 比较。"""
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from hub import accuracy as AC  # noqa: E402
from models3d import core as C, shapes as S, route3d as X  # noqa: E402

L, KH, KT, KK, MAG = 136.0, 20000.0, 20000.0, 50000.0, 800.0
A = C.Assembly("让刀")
A.add(C.Part("工件", X.sh101("op30").shape, "work"))
cone = [(-55.0, 0.0), (-55.0, 9.0), (-14.0, 9.0), (2.0, 0.0)]
A.add(C.Part("前顶尖", S.revolve(cone), "steel"))
A.add(C.Part("后顶尖", S.revolve([(136 - x, r) for x, r in cone]), "steel"))
A.add(C.Part("车刀", S.box(-4, 4, 0, 30, -4, 4), "steel_dark"))
CAM = {"dir": [0.15, -0.5, 1.2], "fit": [[-60, -60, -30], [200, 60, 30]]}
v = R.Video(A, width=1280, height=720, fps=20)


def frame(x, ap, f, cap):
    Fp = AC.kienzle_turning(ap, f)["Fp"]
    head = Fp * (L - x) / L / KH                # 头架让开（mm）
    tail = Fp * x / L / KT                      # 尾座让开
    y = 2 * Fp * AC.compliance_between_centers(x, L, 25.4, KH, KT, KK)["total"]
    ang = math.degrees(math.atan((tail - head) * MAG / L))
    yc = head * MAG
    return {"parts": {"工件": {"move": [0.0, float(-yc), 0.0], "rot": [0, 0, 1, float(-ang)]},
                      "前顶尖": {"move": [0.0, float(-head * MAG), 0.0]}, "后顶尖": {"move": [0.0, float(-tail * MAG), 0.0]},
                      "车刀": {"move": [float(x), 13.2, 0.0]}},
            "camera": CAM, "texts": [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
                                     {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"},
                                     {"pos": [0.55, 0.82], "text": f"背向力 Fp ≈ {Fp:.0f} N", "fontSize": 24, "bold": True},
                                     {"pos": [0.55, 0.88], "text": f"车刀在 x = {x:.0f} mm：直径误差 2y ≈ {y * 1000:.1f} µm", "fontSize": 24, "bold": True, "color": "#b5523b"}]}


for ap, f, cap in ((0.55, 0.15, ("工艺规程：ap 0.55、f 0.15（让开量放大 800 倍画出）", "Plan: ap 0.55, f 0.15 (deflection ×800)")),
                   (1.1, 0.3, ("改成 ap 1.1、f 0.3：背向力加倍，让刀接近工序公差", "ap 1.1, f 0.3: twice the force")),):
    for k in range(51):
        v.add(frame(136 - 136 * k / 50, ap, f, cap), hold=0.08)
    v.add(frame(0, ap, f, cap), hold=1.0)
v.add(frame(68, 0.55, 0.15, ("两头靠近顶尖处让刀大、中间小（短而粗的轴，工件本身几乎不弯）", "Larger near the centres")), hold=2.5)
v.save("v57_5_1")
