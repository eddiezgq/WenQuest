"""三维动画 55.7.2（配图 55.7.3）：喷丸——喷嘴沿工件来回移动，弹丸一颗颗打在表面上，弹坑（放大画出，深色）逐渐布满朝向喷嘴的这一片表面。
弹坑随机落下，实际盖住的比例由画面里的弹坑算出，与式 (55.7.1) C = 1 − e^(−kt) 一致：k 取算例 55.7.1 的 0.230 /s，
约 17 s 达到 98%（全覆盖），34 s 为 200% 覆盖率。模型：factory/digital/models3d/surface3d.py 的 shot_peening。"""
import math
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import numpy as np  # noqa: E402
import render3d as R  # noqa: E402
from models3d import core as C, shapes as S, surface3d as X  # noqa: E402

RW, L = 30.0, 60.0
K, T1 = math.log(10) / 10.0, 10.0                  # 算例 55.7.1：10 s 覆盖 90%
T98, T200 = math.log(50) / K, 2 * math.log(50) / K
A0, A1, X0, X1 = math.radians(-65), math.radians(65), 3.0, L - 3.0   # 朝向喷嘴（−y）的一片表面
AREA = RW * (A1 - A0) * (X1 - X0)
RD = 2.5                                          # 弹坑半径（放大画出）
a_pit = math.pi * RD ** 2
STAGES = 20
b = S.bd()
rng = random.Random(552)
a = X.shot_peening(r_work=RW, L=L)
pits_all = []
prev = 0
for s in range(1, STAGES + 1):
    t = T200 * s / STAGES
    n = round(K * t * AREA / a_pit)                 # 平均每单位面积落下的弹坑数 = k·t / a_pit
    kids = []
    for _ in range(n - prev):
        x, th = rng.uniform(X0, X1), rng.uniform(A0, A1)
        pits_all.append((x, th))
        kids.append(b.Pos(x, -(RW + 0.6) * math.cos(th), (RW + 0.6) * math.sin(th)) * b.Sphere(RD))   # th 从 −y 方向量起
    prev = n
    a.add(C.Part(f"弹坑{s}", b.Compound(children=kids), "#6f7880"))

# 画面里的覆盖率：在这片表面上取网格点，数被弹坑盖住的比例
gx = np.linspace(X0 + RD, X1 - RD, 120)
gt = np.linspace(A0 + RD / RW, A1 - RD / RW, 120)
GX, GT = np.meshgrid(gx, gt)
P = np.array(pits_all)
cover = []
hit = np.zeros(GX.shape, bool)
start = 0
counts = [round(K * T200 * s / STAGES * AREA / a_pit) for s in range(1, STAGES + 1)]
for n in counts:
    for x, th in P[start:n]:
        hit |= (GX - x) ** 2 + (RW * (GT - th)) ** 2 < (RD * 0.97) ** 2
    start = n
    cover.append(hit.mean())

CAM = {"dir": [0.55, -1.0, 0.35], "fit": [[-5, -RW - 95, -RW - 5], [L + 5, RW, RW + 5]]}
v = R.Video(a, width=1280, height=720, fps=20)


def st(stage, sweep, spray, cap):
    parts = {f"弹坑{s}": {"visible": s <= stage} for s in range(1, STAGES + 1)}
    for n in ("喷嘴", "弹丸"):
        parts[n] = {"move": [sweep, 0, 0]}
    parts["弹丸"]["visible"] = spray
    t = T200 * stage / STAGES
    tx = [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
          {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"},
          {"pos": [0.03, 0.82], "text": f"喷丸时间 {t:4.1f} s：式 (55.7.1) C = {(1 - math.exp(-K * t)) * 100:4.1f}%"
           + (f"（{t / T98 * 100:.0f}% 覆盖率）" if t >= T98 - 0.01 else ""), "fontSize": 24, "bold": True},
          {"pos": [0.03, 0.88], "text": f"画面里弹坑实际盖住 {cover[stage - 1] * 100 if stage else 0:4.1f}%", "fontSize": 22, "color": "#4f7fb8"}]
    return {"parts": parts, "camera": CAM, "texts": tx}


v.add(st(0, 0, False, ("喷丸：弹丸以几十米每秒打在表面上", "Shot peening: shot hits the surface at tens of m/s")), hold=1.5)
for s in range(1, STAGES + 1):
    t = T200 * s / STAGES
    cap = (("弹坑越来越多：每个弹坑都是一处塑性变形", "More and more dimples, each a spot of plastic deformation") if t < T98 - 0.1 else
           ("98%：全覆盖——最后几个百分点最费时间", "98%: full coverage — the last few percent take longest") if t < T98 + 1.8 else
           ("再喷一倍时间：200% 覆盖率，表层压应力更均匀", "Twice as long: 200% coverage, a more uniform compressive layer"))
    for j in range(3):
        v.add(st(s, 18 * math.sin((3 * s + j) * 0.9), True, cap), hold=0.2)
    if abs(t - T98) < 0.9:
        v.add(st(s, 0, False, cap), hold=1.5)
v.add(st(STAGES, 0, False, ("覆盖率用放大镜或荧光示踪检查；喷丸强度用阿尔门试片的弧高控制", "Coverage is checked under a magnifier; intensity with Almen strips")), hold=3.0)
v.save("v55_7_2")
