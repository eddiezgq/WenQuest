"""图 4.5.1：基准与基准体系。(a) SH-301 B 版：两轴承位组成公共基准轴线 A–B，齿轮位、外伸段、密封段对它注径向圆跳动；
(b) 轴承座的三基面体系：底面 A（三点）、后端面 B（两点）、侧面 C（一点），六点定位。尺寸取第 33 章与第 3 章。"""
import math

from matplotlib.patches import Polygon, Rectangle

import _ch4 as H
from bookout import T, figure, out, style

S = H.S
lay = S.LAY_B
plt = style()
fig, (a0, a1) = plt.subplots(1, 2, figsize=(7.6, 3.2), gridspec_kw={"width_ratios": [1.45, 1.0]})

# ---------------------------------------------------------------- (a) SH-301
k = 1.0
for z0, z1, d, *_ in lay:
    a0.add_patch(Rectangle((z0, -d / 2), z1 - z0, d, fc="#eef2f7", ec=H.INK, lw=0.9))
a0.plot([-8, S.LEN_B + 8], [0, 0], color=H.MUTED, lw=0.6, ls=(0, (9, 2, 1.5, 2)))
TRI = 2.6


def datum(ax, x, y, name, up=False):
    """基准符号：涂黑三角形贴在要素上，连线到方框里的字母"""
    sg = 1 if up else -1
    ax.add_patch(Polygon([(x - TRI, y), (x + TRI, y), (x, y + sg * TRI * 1.2)], closed=True, fc=H.INK, ec=H.INK))
    ax.plot([x, x], [y + sg * TRI * 1.2, y + sg * 10], color=H.INK, lw=0.7)
    ax.add_patch(Rectangle((x - 4, y + sg * 10 - (0 if up else 8)), 8, 8, fc="white", ec=H.INK, lw=0.7))
    ax.text(x, y + sg * 10 + (4 if up else -4), name, ha="center", va="center", fontsize=7)


def frame(ax, x, y, cells, w=(8, 14, 14)):
    """几何公差框格：[符号, 公差值, 基准]"""
    xx = x
    for c, ww in zip(cells, w):
        ax.add_patch(Rectangle((xx, y), ww, 8, fc="white", ec=H.INK, lw=0.7))
        ax.text(xx + ww / 2, y + 4, c, ha="center", va="center", fontsize=6.6)
        xx += ww
    return x, y


zA = (lay[0][0] + 17 / 2)                  # 左轴承位（只取装轴承的 17 mm）
zB = (lay[4][0] + lay[4][1]) / 2           # 右轴承位
for z, nm in ((zA, "A"), (zB, "B")):
    # 基准是轴线：基准三角形与该段直径的尺寸线对齐（GB/T 1182），尺寸线上端画箭头，下端由基准三角形代替
    a0.annotate("", xy=(z, 35 / 2), xytext=(z, -35 / 2 + TRI * 1.2), arrowprops=dict(arrowstyle="-|>", lw=0.6, color=H.INK, mutation_scale=6))
    a0.text(z + 1.2, 2, "Ø35k6", rotation=90, fontsize=5.8, va="center", ha="left")
    datum(a0, z, -35 / 2, nm)
for (z0, z1, d, *_), lab in ((lay[1], "gear"), (lay[5], "seal"), (lay[6], "ext")):
    zm = (z0 + z1) / 2
    fx, fy = frame(a0, zm - 18, d / 2 + 12, ["↗", "0.015", "A–B"])
    a0.annotate("", xy=(zm, d / 2), xytext=(zm, d / 2 + 12), arrowprops=dict(arrowstyle="-|>", lw=0.6, color=H.INK, mutation_scale=6))
a0.text(lay[0][0] + 2, 20, T("左轴承位", "left seat"), fontsize=6.4, color=H.MUTED)
a0.text(lay[4][0] - 6, -45, T("右轴承位", "right seat"), fontsize=6.4, color=H.MUTED)
a0.set_xlim(-10, S.LEN_B + 10)
a0.set_ylim(-52, 52)
a0.set_aspect("equal")
a0.axis("off")
a0.set_title(T("(a) SH-301：公共基准轴线 A–B", "(a) SH-301: common datum axis A–B"), fontsize=8)

# ---------------------------------------------------------------- (b) 三基面体系（轴测示意）
cx, cy = 0.62, 0.36                 # 斜二测：y 方向缩短、斜 30°


def P(x, y, z):
    return (x + cx * y * math.cos(math.radians(30)), z + cy * y * math.sin(math.radians(30)) + 0.0)


Lb, Wb, tb = 100, 46, 16           # 示意尺寸（不按比例）
box = [(0, 0, 0), (Lb, 0, 0), (Lb, Wb, 0), (0, Wb, 0), (0, 0, tb), (Lb, 0, tb), (Lb, Wb, tb), (0, Wb, tb)]
faces = [(0, 1, 5, 4), (1, 2, 6, 5), (4, 5, 6, 7)]
for f in faces:
    a1.add_patch(Polygon([P(*box[i]) for i in f], closed=True, fc="#eef2f7", ec=H.INK, lw=0.8, alpha=0.55))
for i, j in ((0, 3), (3, 2), (3, 7)):                       # 看不见的棱：虚线
    a1.plot(*zip(P(*box[i]), P(*box[j])), color=H.MUTED, lw=0.6, ls=(0, (3, 2)))
# 三个基准平面（淡色）
pl = {"A": ([(-12, -10, 0), (Lb + 12, -10, 0), (Lb + 12, Wb + 12, 0), (-12, Wb + 12, 0)], "#1f77b4", (-8, -8, -7)),
      "B": ([(-12, Wb, -8), (Lb + 12, Wb, -8), (Lb + 12, Wb, tb + 30), (-12, Wb, tb + 30)], "#2ca02c", (Lb + 4, Wb, tb + 24)),
      "C": ([(0, -10, -8), (0, Wb + 12, -8), (0, Wb + 12, tb + 30), (0, -10, tb + 30)], "#ff7f0e", (0, -10, tb + 22))}
for name, (corners, col, lab) in pl.items():
    a1.add_patch(Polygon([P(*q) for q in corners], closed=True, fc=col, ec=col, alpha=0.10, lw=0.6, zorder=0))
    x, y = P(*lab)
    a1.text(x, y, name, fontsize=8, color=col, weight="bold", ha="center")
pts = {"A": [(15, 8, 0), (85, 8, 0), (50, 40, 0)], "B": [(20, Wb, 8), (80, Wb, 8)], "C": [(0, 23, 8)]}
for name, ps in pts.items():
    col = pl[name][1]
    for q in ps:
        x, y = P(*q)
        a1.plot(x, y, "o", ms=3.4, color=col, zorder=5)
a1.text(*P(Lb / 2, -18, -6), T("A 三点  B 两点  C 一点", "A: 3 points  B: 2  C: 1"), fontsize=6.8, ha="center", va="top")
a1.set_aspect("equal")
a1.axis("off")
a1.set_xlim(-25, 150)
a1.set_ylim(-25, 70)
a1.set_title(T("(b) 三基面体系：3–2–1 定位", "(b) Datum reference frame: 3–2–1"), fontsize=8)
fig.tight_layout()
figure(fig, "fig4_5_1")
out(runout=0.015)
