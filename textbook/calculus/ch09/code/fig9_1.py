"""图 9.1.1：罗尔定理一层层往下用——往返轨迹 q(t) = Δ·16s²(1 − s)²：两端位置相同 ⇒ 速度在内部有零点；
速度有三个零点 ⇒ 加速度在内部有两个零点 ⇒ 加加速度在内部有一个零点。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

Tt, D = 2.0, 60.0
t = np.linspace(0, Tt, 400)
s = t / Tt
q = D * 16 * s ** 2 * (1 - s) ** 2
w = 32 * D * s * (1 - s) * (1 - 2 * s) / Tt
a = 32 * D * (1 - 6 * s + 6 * s ** 2) / Tt ** 2
j = 32 * D * (12 * s - 6) / Tt ** 3
fig, ax = plt.subplots(1, 4, figsize=(13, 3.3))
ta = Tt * (3 - math.sqrt(3)) / 6
items = [(q, "q / (°)", T("位置：两端相同", "position: equal at both ends"), [0, Tt], INK),
         (w, "q′ / (°/s)", T("速度：0、T/2、T 为零", "velocity: zero at 0, T/2, T"), [0, Tt / 2, Tt], BLUE),
         (a, "q″ / (°/s²)", T("加速度：两个内部零点", "acceleration: two interior zeros"), [ta, Tt - ta], RED),
         (j, "q‴ / (°/s³)", T("加加速度：一个零点", "jerk: one zero"), [Tt / 2], GREEN)]
for k, (y, lab, title, zs, c) in enumerate(items):
    ax[k].plot(t, y, color=c, lw=2)
    yz = np.interp(zs, t, y)
    ax[k].plot(zs, yz, "o", color=ACC if k else MUTED, ms=6, zorder=3)
    ax[k].set_xlabel("t / s")
    ax[k].set_ylabel(lab)
    ax[k].set_title(title, fontsize=10)
    clean(ax[k])
fig.tight_layout()
figure(fig, "fig9_1_1")
