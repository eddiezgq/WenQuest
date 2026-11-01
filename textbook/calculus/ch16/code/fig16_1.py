"""图 16.1.1：左：割草机器人的草坪，上下边界与每隔 2 m 的测量线，面积 = ∫(上 − 下)dx；
右：摆线（车轮上一点的轨迹）一拱下的面积是车轮面积的 3 倍。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

top = lambda x: 12 + 2 * np.sin(np.pi * x / 20) + 0.8 * np.sin(3 * np.pi * x / 20)
bot = lambda x: 1.5 * np.sin(np.pi * x / 10) ** 2 + 0.05 * x
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
x = np.linspace(0, 20, 400)
a1.fill_between(x, bot(x), top(x), color=GREEN, alpha=0.18)
a1.plot(x, top(x), color=GREEN, lw=2, label=T("上边界 y = g(x)", "upper edge y = g(x)"))
a1.plot(x, bot(x), color=INK, lw=2, label=T("下边界 y = f(x)", "lower edge y = f(x)"))
for k in range(11):
    xk = 2 * k
    a1.plot([xk, xk], [bot(xk), top(xk)], color=RED, lw=1, ls="--")
    a1.plot([xk, xk], [bot(xk), top(xk)], "o", color=RED, ms=3)
a1.set_xlabel("x / m")
a1.set_ylabel("y / m")
a1.set_aspect("equal")
a1.set_ylim(-1, 16)
a1.legend(fontsize=9, frameon=False, loc="upper center", ncol=2)
a1.set_title(T("测量线（红）每隔 2 m 一条：面积 ≈ Σ 宽度 × 间距", "Survey lines every 2 m: area ≈ Σ width × spacing"), fontsize=10)
clean(a1, zero=False)
r = 1.0
t = np.linspace(0, 2 * np.pi, 400)
cx, cy = r * (t - np.sin(t)), r * (1 - np.cos(t))
a2.fill_between(cx, 0, cy, color=BLUE, alpha=0.18)
a2.plot(cx, cy, color=BLUE, lw=2, label=T("摆线一拱：面积 3πr²", "one cycloid arch: area 3πr²"))
th = np.linspace(0, 2 * np.pi, 200)
a2.fill(np.pi * r + r * np.cos(th), r + r * np.sin(th), color=ACC, alpha=0.25)
a2.plot(np.pi * r + r * np.cos(th), r + r * np.sin(th), color=ACC, lw=1.5, label=T("车轮：面积 πr²", "wheel: area πr²"))
a2.axhline(0, color=MUTED, lw=0.8)
a2.set_aspect("equal")
a2.set_xlabel("x / r")
a2.set_ylabel("y / r")
a2.legend(fontsize=9, frameon=False, loc="upper right")
a2.set_ylim(-0.2, 2.9)
a2.set_title(T("轮缘上一点转一圈画出的拱，下方面积是车轮的 3 倍", "The arch traced in one turn encloses 3 wheels' area"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig16_1_1")
