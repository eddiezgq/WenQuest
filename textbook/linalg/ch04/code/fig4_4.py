"""图 4.4.1：坐标系链——车间坐标系 W、AGV 坐标系 A（在车间中转 30°、位于 (5, 3) m）、机械臂基座坐标系 B（在 AGV 前方 0.2 m、相对 AGV 转 90°）、
末端点 p（在 B 中位于 (0.6, 0.1) m）。齐次变换连乘 T_WB = T_WA T_AB 把 p 换算到车间坐标系。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt


def T2(th, tx, ty):
    t = math.radians(th)
    return np.array([[math.cos(t), -math.sin(t), tx], [math.sin(t), math.cos(t), ty], [0.0, 0.0, 1.0]])


def frame(ax, Tm, name, L=0.5):
    o = Tm[:2, 2]
    for k, col in ((0, RED), (1, GREEN)):
        d = Tm[:2, k] * L
        ax.annotate("", xy=o + d, xytext=o, arrowprops=dict(arrowstyle="-|>", color=col, lw=2, mutation_scale=12))
    ax.text(o[0] - 0.25, o[1] - 0.3, name, fontsize=12)


TWA = T2(30, 5.0, 3.0)
TWB = TWA @ T2(90, 0.2, 0.0)
p = TWB @ np.array([0.6, 0.1, 1.0])
fig, (ax0, ax) = plt.subplots(1, 2, figsize=(10.4, 4.6), gridspec_kw={"width_ratios": [1.3, 1]})
for a in (ax0, ax):
    for x in range(0, 8):
        a.axvline(x, color=MUTED, lw=0.4, alpha=0.4)
    for y in range(0, 6):
        a.axhline(y, color=MUTED, lw=0.4, alpha=0.4)
frame(ax0, np.eye(3), "W", 1.0)
ax0.add_patch(plt.Rectangle((3.9, 2.3), 2.2, 1.8, fill=False, ec=RED, ls="--"))
ax0.plot(5, 3, "s", color=INK, ms=6)
ax0.text(5.1, 2.5, T("AGV（右图放大）", "AGV (enlarged right)"), fontsize=9)
ax0.set_xlim(-0.5, 7.5)
ax0.set_ylim(-0.5, 5.2)
ax0.set_aspect("equal")
ax0.set_xlabel("x / m")
ax0.set_ylabel("y / m")
c = TWA[:2, 2]
R = TWA[:2, :2]
body = np.array([[-0.45, -0.3], [0.45, -0.3], [0.45, 0.3], [-0.45, 0.3], [-0.45, -0.3]]).T
B = (R @ body).T + c
ax.fill(B[:, 0], B[:, 1], color="#c8d6e5", ec=INK, lw=1)
frame(ax, TWA, "A", 0.6)
frame(ax, TWB, "B", 0.35)
ax.plot(*zip(TWB[:2, 2], p[:2]), color=ACC, lw=4)
ax.plot(*p[:2], "o", color=RED, ms=7)
ax.text(p[0] - 0.55, p[1] + 0.08, T("末端 p", "tool point p"), color=RED, fontsize=11)
ax.set_xlim(3.9, 6.1)
ax.set_ylim(2.3, 4.1)
ax.set_aspect("equal")
ax.set_xlabel("x / m")
ax.set_ylabel("y / m")
for a in (ax0, ax):
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig4_4_1")
