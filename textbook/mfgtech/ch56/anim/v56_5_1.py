"""三维动画 56.5.1（配图 56.5.2）：型芯偏了的铸件套筒，分别以外圆（不加工面）和以毛坯内孔为粗基准装夹，镗刀镗出内孔。
(a) 以外圆为粗基准：孔与外圆同轴，壁厚均匀，镗孔余量一边大一边小；(b) 以毛坯内孔为粗基准：余量均匀，壁厚一边厚一边薄。
示意零件：外圆 Ø80，毛坯孔 Ø38，镗到 Ø52；型芯偏移放大到 6 mm 画出（算例 56.5.1 取 2 mm）。从端面看。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, shapes as S  # noqa: E402

E, DY = 6.0, 110.0                       # 型芯偏移（放大）、两件的间距
A = C.Assembly("粗基准")
for tag, dy, hole_c in (("a", 0.0, 0.0), ("b", DY, E)):
    out = S.cyl("x", (dy, 0), 40, 0, 60)
    A.add(C.Part(f"毛坯{tag}", out - S.cyl("x", (dy + E, 0), 19, -1, 61), "#b9aa98"))
    A.add(C.Part(f"镗后{tag}", out - S.cyl("x", (dy + hole_c, 0), 26, -1, 61), "#b9aa98"))
    A.add(C.Part(f"已镗{tag}", S.tube("x", (dy + hole_c, 0), 26, 25.2, 0, 60), "#7f9cbf"))
    A.add(C.Part(f"镗杆{tag}", S.cyl("x", (dy + hole_c, 0), 9, 66, 190) + S.box(60, 66, dy + hole_c - 3, dy + hole_c + 3, 0, 26), "steel_dark"))
CAM = {"dir": [-1.0, -0.06, 0.1], "fit": [[0, -50, -45], [60, DY + 50, 45]]}
v = R.Video(A, width=1280, height=720, fps=20)


def st(depth, done, cap, note=False):
    parts = {}
    for t in "ab":
        parts[f"毛坯{t}"] = {"visible": not done}
        parts[f"镗后{t}"] = {"visible": bool(done)}
        parts[f"已镗{t}"] = {"visible": False}
        parts[f"镗杆{t}"] = {"move": [float(-depth), 0.0, 0.0], "visible": depth < 125}
    tx = [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
          {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"},
          {"pos": [0.08, 0.30], "text": "(a) 以外圆为粗基准", "fontSize": 22, "bold": True},
          {"pos": [0.58, 0.30], "text": "(b) 以毛坯内孔为粗基准", "fontSize": 22, "bold": True}]
    if note:
        tx += [{"pos": [0.08, 0.84], "text": "壁厚处处 14；余量一边 1、一边 13", "fontSize": 22, "color": "#2f6f4f", "bold": True},
               {"pos": [0.58, 0.84], "text": "余量处处 7；壁厚 8–20", "fontSize": 22, "color": "#b5523b", "bold": True},
               {"pos": [0.03, 0.92], "text": "（示意：偏移放大到 6 mm）要壁厚均匀选 (a)，要余量均匀选 (b)", "fontSize": 18, "color": "#5b6770"}]
    return {"parts": parts, "camera": CAM, "texts": tx}


c0 = ("铸件套筒：型芯偏了，毛坯孔与外圆不同轴", "Cast sleeve: the core shifted, the cored hole is off-centre")
v.add(st(0, False, c0), hold=2.5)
c1 = ("两种装夹：(a) 按外圆找正，(b) 按毛坯孔找正，镗刀进给", "Two set-ups; the boring bar feeds in")
for k in range(31):
    v.add(st(62 * R.ease(k / 30), False, c1), hold=0.07)
c2 = ("镗出 Ø52 的孔", "Bored to Ø52")
for k in range(21):
    v.add(st(62 + 70 * R.ease(k / 20), True, c2), hold=0.07)
v.add(st(130, True, ("结果：壁厚均匀与余量均匀不能兼得", "Uniform wall or uniform stock — not both"), note=True), hold=4.0)
v.save("v56_5_1")
