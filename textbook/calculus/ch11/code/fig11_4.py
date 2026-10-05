"""图 11.4.1：左：AGV 从地毯区（0.6 m/s）到地砖区（1.2 m/s）的最短时间路径（折线），与直线路径比较；右：总时间随穿越点 x 的变化。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

v1, v2 = 0.6, 1.2
A, B = (0.0, 3.0), (6.0, -2.0)
Tf = lambda x: np.hypot(x - A[0], A[1]) / v1 + np.hypot(B[0] - x, B[1]) / v2
xs = 1.5382155
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4))
a1.axhspan(0, 3.6, color=ACC, alpha=0.12, lw=0)
a1.axhspan(-2.6, 0, color=BLUE, alpha=0.08, lw=0)
a1.axhline(0, color=MUTED, lw=1)
a1.plot([A[0], xs, B[0]], [A[1], 0, B[1]], color=RED, lw=2, label=T("最短时间", "least time"))
a1.plot([A[0], B[0]], [A[1], B[1]], color=MUTED, lw=1.4, ls="--", label=T("直线", "straight line"))
a1.plot(*A, "o", color=INK)
a1.plot(*B, "o", color=INK)
a1.text(0.2, 3.2, T("地毯 0.6 m/s", "carpet 0.6 m/s"), fontsize=9)
a1.text(3.4, -2.3, T("地砖 1.2 m/s", "tile 1.2 m/s"), fontsize=9)
a1.set_aspect("equal")
a1.set_xlim(-0.5, 6.5)
a1.set_ylim(-2.6, 3.6)
a1.set_xlabel("x / m")
a1.set_ylabel("y / m")
a1.legend(fontsize=9, frameon=False, loc="upper right")
a1.set_title(T("在慢的区域少走，在快的区域多走", "Spend less distance where slow"), fontsize=10)
clean(a1, zero=False)
x = np.linspace(0, 6, 300)
a2.plot(x, Tf(x), color=INK, lw=2)
a2.plot([xs], [Tf(xs)], "o", color=ACC, ms=7)
a2.plot([3.6], [Tf(3.6)], "s", color=MUTED, ms=6)
a2.set_xlabel(T("穿越点 x / m", "crossing point x / m"))
a2.set_ylabel(T("总时间 / s", "total time / s"))
a2.set_title(T("T(x) 是凸函数，最小值处满足斯涅耳定律", "T(x) is convex; Snell's law at the minimum"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig11_4_1")
