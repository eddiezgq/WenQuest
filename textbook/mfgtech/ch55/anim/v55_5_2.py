"""三维动画 55.5.2（配图 55.5.7）：外圆磨床磨一批 SH-301，仿真车间注入“砂轮修整不锋利”（磨平面积倍数 2.5）：每 10 件修整一次，
砂轮逐件变钝，精磨区最高温度（示意的颜色，读数按 hub/surface.py 的 grinding_temperature，同算例 55.5.4）逐件升高，
修整周期后几件超过 Ac1，轴承位出现烧伤带（放大画出）；修整以后温度回落。尺寸、粗糙度照样合格。模型：factory/digital/models3d。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from hub import surface as SU  # noqa: E402
from models3d import core as C, machines as MA, shapes as S, workpiece as W  # noqa: E402
from sim import errors as ER  # noqa: E402

G = ER.GRIND
m45 = SU.STEELS[G["mat"]]
de = SU.equivalent_diameter(G["dw"], G["ds"])
DULL = ER.PROBLEMS["wheel_dull"]["default"]


def theta(i):
    wear = (i % 10) / 30                      # 每 10 件修整（与 sim 的 dress_every=10、图 55.5.7 一致）
    return float(SU.grinding_temperature(m45, G["vs"], G["vw"], G["ap"], de, 0.5 + DULL * (1 + 3 * wear))["theta"])   # float：numpy 的布尔量传给渲染页会被当成“真”


L, XG, RW = 167.0, 124.5, 17.5
g = MA.cylindrical_grinder(L=L, wheel_x=XG, r_work=RW)
g.add(W.sh301("op60"))
GLOW = [("#4f7fb8", 0), ("#e0a030", 500), ("#e06030", 650), ("#d02020", 724)]   # 颜色分档（示意）
for k, (col, _) in enumerate(GLOW):
    g.add(C.Part(f"磨削区{k}", S.tube("x", (0, 0), RW + 0.35, RW - 0.3, XG - 24, XG + 24), col))   # 被磨的一圈表面（示意的温度颜色）
g.add(C.Part("烧伤带", S.tube("x", (0, 0), RW + 0.25, RW - 0.3, XG - 14, XG + 14), "#6b4a2e"))
# 修整笔：砂轮退回 40 mm 后，笔尖碰在砂轮前侧上方 30° 处的外圆上，沿 x 走过砂轮宽度
import math  # noqa: E402
YC = RW + 200 + 40
PY, PZ = YC - 200 * math.cos(math.radians(30)), 200 * math.sin(math.radians(30))
g.add(C.Part("修整笔", S.cyl("z", (XG, PY), 2.5, PZ, PZ + 12) + S.cyl("z", (XG, PY), 6, PZ + 12, PZ + 70), "steel_dark"))
MOV = ("砂轮", "砂轮罩", "砂轮架", "横进给拖板")
CAM = {"dir": [0.35, -1, 0.5], "fit": [[30, -70, -70], [L + 60, 110, 130]]}
v = R.Video(g, width=1280, height=720, fps=20)


def st(back, i, th, glow, burnt, cap, dress=None):
    parts = {n: {"move": [0, back, 0]} for n in MOV}
    lvl = max(k for k, (_, t) in enumerate(GLOW) if th >= t)
    for k in range(len(GLOW)):
        parts[f"磨削区{k}"] = {"visible": glow and k == lvl}
    parts["烧伤带"] = {"visible": bool(burnt)}
    parts["修整笔"] = {"visible": dress is not None, "move": [dress or 0, 0, 0]}
    col = "#c0504d" if th >= m45["Ac1"] else "#1d2327"
    tx = [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
          {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"}]
    if i is not None:
        tx += [{"pos": [0.60, 0.78], "text": f"第 {i + 1} 件（修整后第 {i % 10 + 1} 件）", "fontSize": 24, "bold": True},
               {"pos": [0.60, 0.84], "text": f"精磨区最高温度 {th:4.0f} ℃（Ac1 {m45['Ac1']} ℃）", "fontSize": 24, "bold": True, "color": col},
               {"pos": [0.60, 0.90], "text": "磨削中……" if burnt is None else "尺寸、Ra 合格" + ("；酸洗：烧伤！" if burnt else "；酸洗：无烧伤"),
                "fontSize": 22, "color": "#5b6770" if burnt is None else ("#c0504d" if burnt else "#5a9e6f")}]
    return {"parts": parts, "camera": CAM, "texts": tx}


CAPS = [("刚修整：温度最低（修整笔钝了，也比正常修整的高）", "Just dressed: coolest of the cycle (yet hotter than normal)"),
        ("砂轮逐件变钝：磨粒磨平，摩擦热增加", "The wheel dulls part by part: more rubbing, more heat"),
        ("修整周期的后几件超过 Ac1：二次淬火烧伤", "Late in the cycle the zone passes Ac1: re-hardening burn")]
v.add(st(30, None, 0, False, False, ("仿真车间：修整用的金刚石笔磨钝了，砂轮修不锋利", "Simulated shop: a blunt dressing diamond")), hold=2.0)
for i in range(20):
    th = theta(i)
    cap = CAPS[0] if i % 10 < 3 else (CAPS[2] if th >= m45["Ac1"] else CAPS[1])
    v.add(st(12, i, th, False, None, cap), hold=0.25)
    v.add(st(0, i, th, True, None, cap), hold=0.6)
    v.add(st(12, i, th, False, th >= m45["Ac1"], cap), hold=0.9 if th >= m45["Ac1"] else 0.5)
    if i % 10 == 9:
        for k in range(9):
            v.add(st(40, None, 0, False, False, ("每 10 件修整一次砂轮：温度回落", "Dress every 10 parts: the temperature drops back"), dress=-30 + 60 * k / 8), hold=0.12)
v.add(st(30, None, 0, False, False, ("烧伤件尺寸、粗糙度都合格——只有酸洗、巴克豪森才查得出", "Burnt parts pass size and Ra: only etching or Barkhausen finds them")), hold=3.0)
v.save("v55_5_2")
