"""图 6.5.1：有限覆盖——机械臂末端轨迹与障碍；每个时刻的安全邻域（半径 d(t)/K），有限个就盖住 [0, 1]。"""
import math

import numpy as np

from _arm import L1, L2
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _traj import A, B, K, OBS, W1, W2, clearance, ee

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2), gridspec_kw={"width_ratios": [1, 1.4]})
ts = np.linspace(0, 1, 300)
P = np.array([ee(t) for t in ts])
a1.plot(P[:, 0], P[:, 1], color=BLUE, lw=2, label=T("末端轨迹", "end-effector path"))
for t, c in ((0, MUTED), (0.5, MUTED), (1, MUTED)):
    t1, t2 = A[0] + W1 * t, A[1] + W2 * t
    e = (L1 * math.cos(t1), L1 * math.sin(t1))
    p = ee(t)
    a1.plot([0, e[0], p[0]], [0, e[1], p[1]], "-o", color=c, lw=2, ms=4)
a1.plot(*OBS, "s", color=RED, ms=8, label=T("障碍", "obstacle"))
a1.set_aspect("equal")
a1.legend(fontsize=9, frameon=False, loc="upper right")
a1.set_title(T("两节连杆的运动与障碍", "Arm motion and obstacle"), fontsize=10)
clean(a1, zero=False)
d = np.array([clearance(t) for t in ts])
a2.plot(ts, d, color=INK, lw=2, label=T("距离 d(t)", "clearance d(t)"))
t, k = 0.0, 0
while True:
    r = clearance(t) / K
    y = -0.02 - 0.012 * (k % 3)
    a2.plot([max(0, t - r), min(1, t + r)], [y, y], color=GREEN, lw=3)
    a2.plot([t], [y], "o", color=GREEN, ms=3)
    a2.plot([t, t], [y, clearance(t)], color=GREEN, lw=0.5, ls=":")
    k += 1
    if t + r > 1:
        break
    t += 0.9 * r
a2.set_xlabel(T("时间 t / s", "time t / s"))
a2.set_ylabel("d / m")
a2.set_title(T(f"{k} 个安全邻域（绿）盖住 [0, 1]", f"{k} safe neighbourhoods (green) cover [0, 1]"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig6_5_1")
