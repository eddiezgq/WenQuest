"""52.2 节：夹紧的原则。图 52.2.1 夹紧力方向与作用点的正误对照；
算例 52.2.1 薄壁套用三爪卡盘夹紧车内孔：松开后孔的圆度误差（薄圆环的傅里叶级数解），比较硬爪、软爪（扇形爪）、六爪；图 52.2.5。"""
import math

import numpy as np

import _mfg as M
from bookout import T, figure, out, style

FX = M.fx()
plt = style()

# ---------------- 图 52.2.1：四组正误对照
fig, axs = plt.subplots(2, 4, figsize=(7.6, 3.6))
ok_c, bad_c = M.GREEN, M.RED


def block(ax, x, y, w, h, **k):
    k.setdefault("fc", "#e4ecf5"); k.setdefault("ec", M.INK); k.setdefault("lw", 1.0)
    ax.add_patch(plt.Rectangle((x, y), w, h, **k))


def tri(ax, x, y, s=0.35, col=M.INK):          # 支承（三角形）
    ax.add_patch(plt.Polygon([(x - s, y - s * 1.2), (x + s, y - s * 1.2), (x, y)], closed=True, fc=col, ec=col))


def force(ax, x, y, dx, dy, col):
    ax.annotate("", xy=(x, y), xytext=(x - dx, y - dy), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6))


cases = [
    (T("(a) 方向：压向主要定位面", "(a) Direction: toward the main datum"),
     lambda ax: (block(ax, 0, 0, 4, 2.2), tri(ax, 0.8, 0), tri(ax, 3.2, 0), ax.add_patch(plt.Polygon([(-0.4, 0.7), (-0.4, 1.5), (0, 1.1)], closed=True, fc=M.INK)),
                 force(ax, 2, 2.2, 0, -1.2, ok_c)),
     lambda ax: (block(ax, 0, 0, 4, 2.2), tri(ax, 0.8, 0), tri(ax, 3.2, 0),
                 ax.add_patch(plt.Polygon([(-0.4, 0.7), (-0.4, 1.5), (0, 1.1)], closed=True, fc=M.INK)),
                 force(ax, 4.0, 1.6, -1.4, 0.6, bad_c))),
    (T("(b) 作用点：正对支承", "(b) Point: over the supports"),
     lambda ax: (block(ax, 0, 0, 5, 0.6), tri(ax, 0.7, 0), tri(ax, 4.3, 0), force(ax, 0.7, 0.6, 0, -1.2, ok_c), force(ax, 4.3, 0.6, 0, -1.2, ok_c)),
     lambda ax: (block(ax, 0, 0, 5, 0.6), tri(ax, 0.7, 0), tri(ax, 4.3, 0), force(ax, 2.5, 0.6, 0, -1.2, bad_c),
                 ax.plot(np.linspace(0, 5, 40), 0.6 - 0.25 * np.sin(np.linspace(0, math.pi, 40)), color=bad_c, lw=0.8, ls="--"))),
    (T("(c) 薄壁件：分散夹紧力", "(c) Thin wall: spread the force"),
     lambda ax: (ax.add_patch(plt.Circle((2, 1.2), 1.1, fc="none", ec=M.INK, lw=3)),
                 ax.add_patch(plt.Circle((2, 1.2), 1.32, fc="none", ec=ok_c, lw=2.5)),
                 [force(ax, 2 + 1.32 * math.cos(a), 1.2 + 1.32 * math.sin(a), -0.6 * math.cos(a), -0.6 * math.sin(a), ok_c) for a in np.radians([90, 210, 330])]),
     lambda ax: (ax.add_patch(plt.Circle((2, 1.2), 1.1, fc="none", ec=M.INK, lw=3)),
                 [force(ax, 2 + 1.1 * math.cos(a), 1.2 + 1.1 * math.sin(a), -0.8 * math.cos(a), -0.8 * math.sin(a), bad_c) for a in np.radians([90, 210, 330])])),
    (T("(d) 靠近加工面，必要时加辅助支承", "(d) Near the cut; add an auxiliary support"),
     lambda ax: (block(ax, 0, 0, 1.0, 2.6), block(ax, 1.0, 1.9, 3.4, 0.7), tri(ax, 0.5, 0), ax.add_patch(plt.Rectangle((3.5, 0.9), 0.3, 1.0, fc=ok_c)),
                 force(ax, 3.65, 2.6, 0, -1.0, ok_c), ax.plot([3.0, 4.4], [2.75, 2.75], color=M.WARM, lw=3)),
     lambda ax: (block(ax, 0, 0, 1.0, 2.6), block(ax, 1.0, 1.9, 3.4, 0.7), tri(ax, 0.5, 0), force(ax, 0.5, 2.6, 0, -1.0, bad_c),
                 ax.plot([3.0, 4.4], [2.75, 2.75], color=M.WARM, lw=3), ax.text(3.7, 1.3, T("振、让刀", "chatter"), fontsize=6.5, color=bad_c, ha="center"))),
]
for j, (title, good, bad) in enumerate(cases):
    for i, (fn, mark, col) in enumerate(((good, T("好", "good"), ok_c), (bad, T("差", "poor"), bad_c))):
        ax = axs[i, j]
        fn(ax)
        ax.text(0.02, 0.98, mark, transform=ax.transAxes, fontsize=8, color=col, va="top", fontweight="bold")
        ax.set_xlim(-0.8, 5.4); ax.set_ylim(-0.8, 3.4); ax.set_aspect("equal"); ax.axis("off")
    axs[0, j].set_title(title, fontsize=7.2)
fig.tight_layout()
figure(fig, "fig52_2_1")

# ---------------- 算例 52.2.1：薄壁套 Ø80 × 3（中径半径 38.5），宽 20，45 钢；车内孔时三爪夹紧外圆，总夹紧力 600 N
R, E, b, t, W = 38.5, 210000.0, 20.0, 3.0, 600.0
two = FX.ring_clamp(2, 2 * 200.0, R, E, b, t)
k_roark = 0.1488                                     # Roark 手册：两点受压薄圆环沿载荷方向直径的减小系数
roark = k_roark * 200 * R ** 3 / two["EI"]
assert abs(2 * two["w"][0] - roark) / roark < 0.01, "级数解与 Roark 的两点受压结果不一致"
cases = {"hard3": (3, 0), "soft3": (3, 60), "six": (6, 0), "soft6": (6, 40)}
res = {k: FX.ring_clamp(n, W, R, E, b, t, a) for k, (n, a) in cases.items()}
full = 0.0          # 整圈胀套 / 开缝套筒：径向均匀受压，只有 0 阶分量，圆度误差为零（不计开缝）
# 圆度误差与夹紧力成正比：允许圆度 0.01 mm 时，硬三爪最多能夹多大的力
Wmax = W * 0.01 / res["hard3"]["roundness"]

fig, ax = plt.subplots(figsize=(5.0, 3.0), subplot_kw={"projection": "polar"})
mag = 0.6 / res["hard3"]["roundness"]               # 位移放大画出
for k, col, lab in (("hard3", M.RED, T("硬三爪", "3 hard jaws")), ("soft3", M.WARM, T("三个 60° 扇形软爪", "3 soft jaws, 60° each")),
                    ("six", M.ACCENT, T("六爪", "6 jaws"))):
    r = res[k]
    th = np.array(r["theta"] + [r["theta"][0]])
    w = np.array(r["w"] + [r["w"][0]])
    ax.plot(th, 1 - mag * (w - np.mean(w)), color=col, lw=1.3, label=f"{lab}: {r['roundness'] * 1000:.0f} µm")
ax.plot(np.linspace(0, 2 * math.pi, 200), np.ones(200), color=M.MUTED, lw=0.6, ls="--")
ax.set_ylim(0, 1.6); ax.set_yticks([]); ax.set_xticks([]); ax.spines["polar"].set_visible(False); ax.grid(False)
ax.legend(loc="center left", bbox_to_anchor=(1.05, 0.5), fontsize=7.5, frameon=False,
          title=T("夹紧时外圆的变形（放大）", "OD under clamping (magnified)"), title_fontsize=7.5)
figure(fig, "fig52_2_5")

out(R=R, t=t, b=b, W=W, roark=roark, k_roark=k_roark, dD2=2 * two["w"][0], r_hard3=res["hard3"]["roundness"], r_soft3=res["soft3"]["roundness"],
    r_six=res["six"]["roundness"], r_soft6=res["soft6"]["roundness"], ratio_soft=res["hard3"]["roundness"] / res["soft3"]["roundness"],
    ratio_six=res["hard3"]["roundness"] / res["six"]["roundness"], Wmax=Wmax, full=full)
