"""图 5.1.1：AGV 航向的读数在 ±π 处跳变，差商估计的角速度出现尖峰；图 5.1.2：在一点连续的三个条件。"""
import math

import numpy as np

from _fig import ACC, BLUE, INK, MUTED, RED, T, clean, figure, plt

w, Ts = 0.5, 0.02
t = np.arange(0, 16, Ts)
th = 2.5 + w * t
rd = np.arctan2(np.sin(th), np.cos(th))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8))
a1.plot(t, th, color=MUTED, lw=1.5, ls="--", label=T("真实航向（连续）", "true heading (continuous)"))
a1.plot(t, rd, color=BLUE, lw=2, label=T("读数（主值）", "reading (principal value)"))
for y in (math.pi, -math.pi):
    a1.axhline(y, color=MUTED, lw=0.6, ls=":")
a1.set_xlabel(T("时间 t / s", "time t / s"))
a1.set_ylabel(T("航向 / rad", "heading / rad"))
a1.legend(fontsize=9, frameon=False, loc="upper left")
a1.set_title(T("读数每转过 ±π 跳变一次", "The reading jumps at ±π"), fontsize=10)
clean(a1)
a2.plot(t[1:], np.diff(rd) / Ts, color=RED, lw=1.5)
a2.set_xlabel(T("时间 t / s", "time t / s"))
a2.set_ylabel(T("差商估计的角速度 / (rad/s)", "estimated rate / (rad/s)"))
a2.set_title(T("跳变处的差商约为 −314 rad/s（真值 0.5）", "At a jump the difference quotient is about −314 rad/s (true: 0.5)"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig5_1_1")

fig, axs = plt.subplots(1, 4, figsize=(13, 3.2))
x = np.linspace(-1, 1, 400)
f = lambda x: 0.5 * x ** 2 + 0.3 * x + 1
titles = [T("连续", "continuous"), T("f(a) 无定义", "f(a) undefined"), T("极限 ≠ f(a)", "limit ≠ f(a)"), T("极限不存在", "no limit")]
for k, ax in enumerate(axs):
    if k < 3:
        ax.plot(x, f(x), color=BLUE, lw=2)
    else:
        ax.plot(x[x < 0], f(x[x < 0]), color=BLUE, lw=2)
        ax.plot(x[x > 0], f(x[x > 0]) + 0.6, color=BLUE, lw=2)
        ax.plot([0], [f(0) + 0.6], "o", mfc="white", mec=BLUE, ms=6, zorder=5)
    if k == 0:
        ax.plot([0], [f(0)], "o", color=BLUE, ms=6, zorder=5)
    if k in (1, 2):
        ax.plot([0], [f(0)], "o", mfc="white", mec=BLUE, ms=6, zorder=5)
    if k == 2:
        ax.plot([0], [1.6], "o", color=RED, ms=6, zorder=5)
    if k == 3:
        ax.plot([0], [f(0)], "o", color=BLUE, ms=6, zorder=5)
    ax.set_xticks([0])
    ax.set_xticklabels(["$a$"])
    ax.set_ylim(0.4, 2.2)
    ax.set_yticks([])
    ax.set_title(titles[k], fontsize=10)
    clean(ax, zero=False)
fig.tight_layout()
figure(fig, "fig5_1_2")
