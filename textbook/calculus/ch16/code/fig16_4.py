"""图 16.4.1：左：弧长的定义——曲线 y = x² 的内接折线，分点加密时长度增大，趋于弧长；小三角形 ds² = dx² + dy²；
右：AGV 换道（横移 1 m、长 4 m）的三种路径，标出各自的长度，与直线斜穿比较。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.3))
x = np.linspace(0, 1, 300)
a1.plot(x, x * x, color=INK, lw=2.4, label=T("曲线 y = x²", "curve y = x²"))
for n, c in ((2, RED), (4, ACC)):
    xs = np.linspace(0, 1, n + 1)
    a1.plot(xs, xs * xs, "o-", color=c, lw=1.4, ms=4, label=T(f"{n} 段折线", f"{n}-segment polyline"))
x0, dx = 0.55, 0.2
a1.plot([x0, x0 + dx], [x0 ** 2, x0 ** 2], color=BLUE, lw=1)
a1.plot([x0 + dx, x0 + dx], [x0 ** 2, (x0 + dx) ** 2], color=BLUE, lw=1)
a1.plot([x0, x0 + dx], [x0 ** 2, (x0 + dx) ** 2], color=BLUE, lw=1.6)
a1.text(x0 + dx / 2, x0 ** 2 - 0.05, "dx", color=BLUE, ha="center", fontsize=10)
a1.text(x0 + dx + 0.02, x0 ** 2 + 0.07, "dy", color=BLUE, fontsize=10)
a1.text(x0 + 0.02, x0 ** 2 + 0.16, "ds", color=BLUE, fontsize=10)
a1.set_xlabel("x")
a1.set_ylabel("y")
a1.set_aspect("equal")
a1.legend(fontsize=9, frameon=False, loc="upper left")
a1.set_title(T("内接折线越分越细，长度增大并趋于弧长", "Inscribed polylines lengthen towards the arc length"), fontsize=10)
clean(a1, zero=False)
d, L = 1.0, 4.0
u = np.linspace(0, 1, 300)
paths = [(T("三次多项式", "cubic"), d * (3 * u ** 2 - 2 * u ** 3), BLUE), (T("余弦", "cosine"), d * (1 - np.cos(np.pi * u)) / 2, GREEN),
         (T("五次多项式", "quintic"), d * (10 * u ** 3 - 15 * u ** 4 + 6 * u ** 5), RED)]
for name, y, c in paths:
    ln = float(np.sum(np.hypot(np.diff(u * L), np.diff(y))))
    a2.plot(u * L, y, color=c, lw=2, label=f"{name}：{ln:.3f} m" if T("x", "") == "x" else f"{name}: {ln:.3f} m")
a2.plot([0, L], [0, d], color=MUTED, lw=1, ls="--", label=(T("直线斜穿：", "straight diagonal: ") + f"{math.hypot(L, d):.3f} m"))
a2.plot([-1, 0], [0, 0], color=INK, lw=2)
a2.plot([L, L + 1], [d, d], color=INK, lw=2)
a2.set_xlabel("x / m")
a2.set_ylabel("y / m")
a2.set_ylim(-0.4, 1.6)
a2.legend(fontsize=9, frameon=False, loc="upper left")
a2.set_title(T("换道路径的长度：曲率连续的五次路径最长，但只多几厘米", "Path lengths: the curvature-continuous quintic is longest, by only centimetres"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig16_4_1")
