"""三维动画 51.7.1（配图 51.7.2）：一批轴的直径在公差内变化，放在同一个 V 形块上——轴心沿对称面上下移动，
上母线、下母线移动得不一样；水平方向不动（对中）。直径变化放大画出（Ø46 → Ø40），右上角的读数按 SH-301 的真实公差折算。
模型：factory/digital/models3d（elements.vblock），逐帧渲染（render3d.Video）。"""
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
for p in (REPO / "factory" / "digital", REPO / "textbook" / "tools"):
    sys.path.insert(0, str(p))

import render3d as R  # noqa: E402
from models3d import core as C, elements as E, shapes as S  # noqa: E402

N = 13
DS = [46.0 - 6.0 * k / (N - 1) for k in range(N)]
a = C.Assembly("V 形块直径变化")
a.add(C.Part("V 形块", E.vblock(B=90, L=30, H=45, apex=10, at=(0, 0, 0)), "hardened"))
for k, d in enumerate(DS):
    a.add(C.Part(f"轴{k}", S.cyl("x", (0, E.v_axis_height(d, apex=10)), d / 2, -12, 12), "work"))
a.add(C.Part("铣刀（对刀后不动）", S.cyl("z", (0, 0), 6, 75, 110), "tool"))
CAM = {"dir": [1, 0, 0], "fit": [[0, -70, 0], [0, 70, 110]]}
v = R.Video(a, width=1280, height=720, fps=20)
Td, s45 = 0.039, math.sin(math.radians(45))
z_hi = E.v_axis_height(46, apex=10)


def st(k, cap):
    d = DS[k]
    zc = E.v_axis_height(d, apex=10)
    t = (46 - d) / 6.0                                  # 0 → 1：d_max → d_min
    parts = {f"轴{j}": {"visible": j == k} for j in range(N)}
    pts = [{"at": (13, 0, zc), "r": 6, "color": "#4f7fb8", "text": "轴心", "dx": 10, "dy": -8},
           {"at": (13, 0, zc + d / 2), "r": 5, "color": "#c0504d", "text": "上母线", "dx": 10, "dy": -6},
           {"at": (13, 0, zc - d / 2), "r": 5, "color": "#5a9e6f", "text": "下母线", "dx": 10, "dy": 18},
           {"at": (13, 0, z_hi), "r": 3, "color": "#9aa3ab"}]
    texts = [{"pos": [0.03, 0.08], "text": cap[0], "fontSize": 26, "bold": True},
             {"pos": [0.03, 0.13], "text": cap[1], "fontSize": 18, "color": "#5b6770"},
             {"pos": [0.66, 0.3], "text": "SH-301 齿轮位 Ø40.3（0/−0.039）折算：", "fontSize": 18, "color": "#5b6770"},
             {"pos": [0.66, 0.36], "text": f"轴心下移 {t * Td / (2 * s45) * 1000:5.1f} µm", "fontSize": 22, "color": "#4f7fb8", "bold": True},
             {"pos": [0.66, 0.42], "text": f"上母线下移 {t * (Td / (2 * s45) + Td / 2) * 1000:5.1f} µm", "fontSize": 22, "color": "#c0504d", "bold": True},
             {"pos": [0.66, 0.48], "text": f"下母线下移 {t * (Td / (2 * s45) - Td / 2) * 1000:5.1f} µm", "fontSize": 22, "color": "#5a9e6f", "bold": True},
             {"pos": [0.66, 0.54], "text": "水平方向：0（对中）", "fontSize": 22, "bold": True}]
    return {"parts": parts, "camera": CAM, "points": pts, "texts": texts}


c1 = ("一批轴的直径不同，放在同一个 V 形块上", "Shafts of different diameters in the same V-block")
v.add(st(0, c1), hold=1.0)
c2 = ("直径变小：轴心沿对称面下移，水平方向不动", "Smaller diameter: the axis drops along the symmetry plane, no sideways shift")
for k in range(N):
    v.add(st(k, c2), hold=0.18)
v.add(st(N - 1, ("槽深从下母线量起时，定位误差最小", "Measure the slot depth from the bottom line: the smallest error")), hold=2.0)
for k in reversed(range(N)):
    v.add(st(k, ("再变回来：只有沿对称面的移动", "And back: only along the symmetry plane")), hold=0.1)
v.add(st(0, ("V 形块“对中不对高”", "A V-block centres sideways but not in height")), hold=2.0)
v.save("v51_7_1")
