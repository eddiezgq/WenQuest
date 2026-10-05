"""三维动画 52.6.1（配图 52.6.7）：回转式钻模的分度——钻孔、退刀、拔出对定销、转 60°、插入对定销，再钻下一个孔。
三维模型取自数字工厂（factory/digital/models3d/typical.py 的 drill_indexing），逐帧渲染（textbook/tools/render3d.py 的 Video）。"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, typical as TY, shapes as S  # noqa: E402

H = 80.0
a = TY.drill_indexing(6)
work = next(p for p in a.parts if p.name.startswith("工件"))
a.parts.remove(work)
N = 3
for k in range(N + 1):                    # 钻好 k 个孔的工件（孔在钻孔时的位置是正上方，之后随工件转）
    s = TY.sleeve_part(50, 30, 60, at=(0, 0, H))
    for j in range(k):                    # 第 j 个孔钻的时候工件已转过 60·j 度：在工件自身的坐标里，它在 −60·j 度处
        s = s - S.rot(S.cyl("z", (30, 0), 4, H, H + 30), -60 * j, 0, 0, about=(0, 0, H))
    a.add(C.Part(f"工件{k}", s, "work"))
a.add(C.Part("钻头", S.cyl("z", (30, 0), 4, 0, 90) + S.cyl("z", (30, 0), 9, 90, 150), "tool", tags=("nocut",)))
ROT = ["分度盘", "心轴", "螺母"] + [f"工件{k}" for k in range(N + 1)]
CAM = {"dir": [-0.9, -1.3, 0.75], "fit": [[-160, -70, -20], [130, 70, 250]], "zoom": 1.05}
v = R.Video(a, width=1280, height=720, fps=20)


def st(k, ang, drill_z, pin_out, cap):
    parts = {}
    for n in ROT:
        parts[n] = {"rot": [1, 0, 0, ang, 0, 0, H]}
    for j in range(N + 1):
        parts[f"工件{j}"]["visible"] = j == k
    parts["对定销"] = {"move": [-24 * pin_out, 0, 0]}
    parts["钻头"] = {"move": [0, 0, drill_z]}
    return {"parts": parts, "camera": CAM, "texts": [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
                                                     {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"}]}


def go(n, f, hold=0.0):
    for i in range(n):
        v.add(f(R.ease(i / max(1, n - 1))))
    if hold:
        v.add(f(1.0), hold=hold)


top = H + 25 + 30                         # 钻头底端在钻套上方
down = H + 25 - 12                        # 钻穿套筒壁
ang = 0.0
for k in range(N):
    capd = (f"{k + 1}  钻第 {k + 1} 个径向孔：钻套引导钻头", f"Drill radial hole {k + 1}, guided by the bushing")
    go(16, lambda t, k=k: st(k, ang, top + (down - top) * t, 0, capd))
    go(10, lambda t, k=k: st(k + 1, ang, down + (top - down) * t, 0, capd), hold=0.4)
    if k == N - 1:
        break
    capi = ("拔出对定销，分度盘连同心轴、工件转 60°，再插入对定销", "Pull the plunger, index 60°, push the plunger back in")
    go(8, lambda t, k=k: st(k + 1, ang, top, t, capi))
    go(20, lambda t, k=k, a0=ang: st(k + 1, a0 + 60 * t, top, 1, capi))
    ang += 60
    go(8, lambda t, k=k: st(k + 1, ang, top, 1 - t, capi), hold=0.6)
v.add(st(N, ang, top, 0, ("分度误差来自分度孔的位置误差、对定销与孔的间隙、回转轴的间隙", "Indexing error: hole position, plunger clearance, spindle clearance")), hold=2.5)
v.save("v52_6_1")
