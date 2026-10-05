"""图 10.5.1：左：AGV 换道（横移 1 m、长 4 m）的三种路径，五次多项式路径上画出最大曲率处的曲率圆；
右：三种路径的曲率随 x 的变化：三次与余弦路径在入口和出口处曲率从 0 突变，五次路径连续地从 0 开始。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _path import lane

d, L = 1.0, 4.0
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
x = np.linspace(0, L, 801)
for kind, c, lab in (("cubic", BLUE, T("三次", "cubic")), ("cos", GREEN, T("余弦", "cosine")), ("quintic", RED, T("五次", "quintic"))):
    y, yp, ypp = lane(kind, d, L)
    Y = np.array([y(v) for v in x])
    k = np.array([abs(ypp(v)) / (1 + yp(v) ** 2) ** 1.5 for v in x])
    xe = np.concatenate([[-1.2, 0], x, [L, L + 1.2]])
    a1.plot(xe, np.concatenate([[0, 0], Y, [d, d]]), color=c, lw=1.8, label=lab)
    a2.plot(np.concatenate([[-1.2, 0], x, [L, L + 1.2]]), np.concatenate([[0, 0], k, [0, 0]]), color=c, lw=1.8, label=lab)
    if kind == "quintic":
        i = int(np.argmax(k))
        R = 1 / k[i]
        nx, ny = -yp(x[i]), 1.0
        n = math.hypot(nx, ny)
        cx, cy = x[i] + R * nx / n, Y[i] + R * ny / n
        tt = np.linspace(0, 2 * np.pi, 300)
        a1.plot(cx + R * np.cos(tt), cy + R * np.sin(tt), color=RED, lw=0.8, ls=":")
        a1.plot([x[i]], [Y[i]], "o", color=ACC, ms=6)
a1.set_aspect("equal")
a1.set_xlim(-1.2, L + 1.2)
a1.set_ylim(-0.6, 4.0)
a1.set_xlabel("x / m")
a1.set_ylabel("y / m")
a1.set_title(T("换道路径与最大曲率处的曲率圆", "Lane-change paths; circle of curvature at the sharpest point"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="upper left")
clean(a1, zero=False)
a2.set_xlabel("x / m")
a2.set_ylabel("κ / (1/m)")
a2.set_title(T("曲率：三次、余弦路径在入口处跳变", "Curvature: jumps at entry for cubic and cosine"), fontsize=10)
a2.legend(fontsize=9, frameon=False)
clean(a2)
fig.tight_layout()
figure(fig, "fig10_5_1")
