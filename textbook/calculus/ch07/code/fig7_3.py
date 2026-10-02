"""图 7.3.1：乘积法则的面积解释；图 7.3.2：五次多项式运动的角速度、角加速度和功率。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _traj import quintic

fig, ax = plt.subplots(figsize=(5.6, 4.4))
u, v, du, dv = 3.0, 2.0, 0.8, 0.6
ax.add_patch(plt.Rectangle((0, 0), u, v, fc="#d9e6f2", ec=INK))
ax.add_patch(plt.Rectangle((u, 0), du, v, fc="#f6d6b8", ec=INK))
ax.add_patch(plt.Rectangle((0, v), u, dv, fc="#d5ecd4", ec=INK))
ax.add_patch(plt.Rectangle((u, v), du, dv, fc="#bbbbbb", ec=INK))
ax.text(u / 2, v / 2, "$uv$", ha="center", va="center", fontsize=16)
ax.text(u + du / 2, v / 2, r"$v\,\Delta u$", ha="center", va="center", fontsize=13, rotation=90)
ax.text(u / 2, v + dv / 2, r"$u\,\Delta v$", ha="center", va="center", fontsize=13)
ax.text(u + du / 2, v + dv / 2, r"$\Delta u\Delta v$", ha="center", va="center", fontsize=9)
ax.text(u / 2, -0.25, "$u$", ha="center", fontsize=13)
ax.text(u + du / 2, -0.25, r"$\Delta u$", ha="center", fontsize=12)
ax.text(-0.25, v / 2, "$v$", va="center", fontsize=13)
ax.text(-0.35, v + dv / 2, r"$\Delta v$", va="center", fontsize=12)
ax.set_xlim(-0.6, u + du + 0.3)
ax.set_ylim(-0.6, v + dv + 0.3)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title(T("面积的增量 = 两条长边 + 一个小角", "Increase of area = two long strips + a small corner"), fontsize=12)
fig.tight_layout()
figure(fig, "fig7_3_1")

I, T2, D = 2.0, 2.0, math.pi / 2
t = np.linspace(0, T2, 500)
_, w, a, _ = quintic(t, T2, D)
P = I * a * w
ts = (0.5 - math.sqrt(7) / 14) * T2
fig, ax = plt.subplots(figsize=(6.6, 4.2))
ax.plot(t, w, color=BLUE, lw=1.8, label=T("角速度 ω / (rad/s)", "angular velocity ω / (rad/s)"))
ax.plot(t, a, color=GREEN, lw=1.8, label=T("角加速度 α / (rad/s²)", "angular acceleration α / (rad/s²)"))
ax.plot(t, P, color=RED, lw=2.2, label=T("功率 P = Iαω / W", "power P = Iαω / W"))
Ps = I * float(quintic(ts, T2, D)[2]) * float(quintic(ts, T2, D)[1])
ax.plot([ts], [Ps], "o", color=RED, ms=7, mec=INK)
ax.axvline(ts, color=MUTED, ls=":", lw=1)
ax.text(ts + 0.04, Ps + 0.2, T("最大功率", "peak power"), color=RED)
ax.set_xlabel(T("时间 t / s", "time t / s"))
ax.legend(frameon=False, fontsize=9, loc="lower left")
clean(ax)
fig.tight_layout()
figure(fig, "fig7_3_2")
