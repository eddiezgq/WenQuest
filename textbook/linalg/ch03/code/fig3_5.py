"""图 3.5.1：二元方程组解的三种情形——两直线相交（唯一解）、平行（无解）、重合（无穷多解）。
图 3.5.2：冗余三连杆臂。末端速度相同的两组关节速度：θ̇₃ = 0 与 θ̇₃ = 0.5 rad/s，按各自的关节速度转 0.6 s 后的姿态（虚线）不同，末端几乎到达同一点（只差二阶小量）。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow, figure, plt

fig, axs = plt.subplots(1, 3, figsize=(11.0, 3.6))
x = np.linspace(-1, 5, 2)
cases = [((1, 1, 4), (1, -1, 0), T("相交：唯一解", "intersect: one solution")),
         ((1, 1, 4), (1, 1, 2), T("平行：无解", "parallel: no solution")),
         ((1, 1, 4), (2, 2, 8), T("重合：无穷多解", "coincide: infinitely many"))]
for ax, (e1, e2, name) in zip(axs, cases):
    ax.plot(x, (e1[2] - e1[0] * x) / e1[1], color=BLUE, lw=2.6)
    ax.plot(x, (e2[2] - e2[0] * x) / e2[1], color=GREEN, lw=1.6, ls="--" if e2 == (2, 2, 8) else "-")
    if e2 == (1, -1, 0):
        ax.plot(2, 2, "o", color=RED, ms=7)
    ax.set_xlim(-1, 5)
    ax.set_ylim(-1, 5)
    ax.set_aspect("equal")
    ax.axhline(0, color=MUTED, lw=0.5)
    ax.axvline(0, color=MUTED, lw=0.5)
    ax.set_title(name, fontsize=11)
    fmt = lambda e: f"{'' if e[0] == 1 else e[0]}x {'−' if e[1] < 0 else '+'} {'' if abs(e[1]) == 1 else abs(e[1])}y = {e[2]}"
    ax.text(2.6, 4.5, fmt(e1), color=BLUE, fontsize=10)
    ax.text(2.6, 4.0, fmt(e2), color=GREEN, fontsize=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig3_5_1")

l = [0.425, 0.392, 0.1]
th = np.radians([30, 45, -60])


def pts(t):
    c = np.cumsum(t)
    p = [np.zeros(2)]
    for k in range(3):
        p.append(p[-1] + l[k] * np.array([math.cos(c[k]), math.sin(c[k])]))
    return np.array(p)


qa = np.array([0.18539, -0.52995, 0.0])
qb = np.array([0.02646, -0.31954, 0.5])
fig, ax = plt.subplots(figsize=(6.4, 4.6))
P0 = pts(th)
ax.plot(P0[:, 0], P0[:, 1], "-o", color=INK, lw=4, ms=6, mfc="white", zorder=3, label=T("当前姿态", "current pose"))
for q, col, name in ((qa, BLUE, T("θ̇₃ = 0", "θ̇₃ = 0")), (qb, ACC, T("θ̇₃ = 0.5 rad/s", "θ̇₃ = 0.5 rad/s"))):
    P = pts(th + 0.6 * q)
    ax.plot(P[:, 0], P[:, 1], "--o", color=col, lw=2, ms=4, label=name + T("：0.6 s 后", ": after 0.6 s"))
arrow(ax, np.array([0.06, 0.0]), RED, None, start=P0[-1], lw=2.4)
ax.text(P0[-1][0] + 0.07, P0[-1][1] + 0.01, T("末端速度 0.1 m/s", "tool velocity 0.1 m/s"), color=RED, fontsize=10)
ax.set_aspect("equal")
ax.set_xlim(-0.05, 0.85)
ax.set_ylim(-0.05, 0.7)
ax.legend(frameon=False, loc="upper left", fontsize=9)
ax.set_xlabel("x / m")
ax.set_ylabel("y / m")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig3_5_2")
