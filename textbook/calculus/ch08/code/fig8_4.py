"""图 8.4.1：牛顿法求 t₉₅——切线逐次逼近；误差随迭代次数的变化（牛顿法与二分法）。
图 8.4.2：牛顿法的失效——arctan x 从 x₀ = 1.5 出发发散；x³ − 2x + 2 从 0 出发在 0 与 1 之间循环。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

zeta, wn = 0.6, 10.0
wd = wn * math.sqrt(1 - zeta ** 2)
c = zeta / math.sqrt(1 - zeta ** 2)
q = lambda t: 1 - np.exp(-zeta * wn * t) * (np.cos(wd * t) + c * np.sin(wd * t))
dq = lambda t: np.exp(-zeta * wn * t) * (wn ** 2 / wd) * np.sin(wd * t)
f = lambda t: q(t) - 0.95
root = 0.2537398611108357
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
t = np.linspace(0.12, 0.34, 300)
a1.plot(t, f(t), color=INK, lw=2)
x = 0.2
for k in range(3):
    xn = x - f(x) / dq(x)
    a1.plot([x, xn], [f(x), 0], color=RED, lw=1.2)
    a1.plot([x, x], [0, f(x)], color=MUTED, lw=0.8, ls=":")
    a1.plot([x], [f(x)], "o", color=RED, ms=4)
    a1.text(xn, 0.02 + 0.03 * k, f"$t_{k + 1}$", color=RED, ha="center", fontsize=9)
    x = xn
a1.text(0.2, -0.03, "$t_0$", ha="center", fontsize=9)
a1.set_xlabel(T("时间 t / s", "time t / s"))
a1.set_ylabel("q(t) − 0.95")
a1.set_title(T("牛顿法：沿切线走到与横轴的交点", "Newton: follow the tangent to the axis"), fontsize=10)
clean(a1)
x, en = 0.2, []
for _ in range(5):
    x = x - f(x) / dq(x)
    en.append(max(abs(x - root), 1e-17))
lo, hi, eb = 0.0, math.pi / wd, []
for _ in range(50):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if f(m) < 0 else (lo, m)
    eb.append(max(abs((lo + hi) / 2 - root), 1e-17))
a2.semilogy(range(1, 6), en, "o-", color=RED, label=T("牛顿法", "Newton"))
a2.semilogy(range(1, 51), eb, ".-", color=BLUE, ms=3, label=T("二分法", "bisection"))
a2.set_ylim(1e-17, 1)
a2.set_xlabel(T("迭代次数", "iterations"))
a2.set_ylabel(T("误差 / s", "error / s"))
a2.legend(fontsize=9, frameon=False)
a2.set_title(T("牛顿法 5 步达到机器精度，二分法约需 50 步", "Newton: 5 steps to machine precision; bisection: ~50"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig8_4_1")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.8))
x = np.linspace(-6, 6, 400)
a1.plot(x, np.arctan(x), color=INK, lw=2)
xk = 1.5
for k in range(3):
    xn = xk - math.atan(xk) * (1 + xk * xk)
    a1.plot([xk, xn], [math.atan(xk), 0], color=RED, lw=1.2)
    a1.plot([xk, xk], [0, math.atan(xk)], color=MUTED, lw=0.8, ls=":")
    a1.text(xn, -0.25 if k % 2 == 0 else 0.15, f"$x_{k + 1}$", color=RED, ha="center", fontsize=9)
    xk = xn
a1.text(1.5, 0.15, "$x_0$", ha="center", fontsize=9)
a1.set_xlim(-6, 6)
a1.set_title(T("arctan x，x₀ = 1.5：越跳越远", "arctan x from x₀ = 1.5: jumps farther and farther"), fontsize=10)
clean(a1)
x = np.linspace(-2.2, 1.6, 400)
p = lambda x: x ** 3 - 2 * x + 2
a2.plot(x, p(x), color=INK, lw=2)
for x0, x1 in ((0.0, 1.0), (1.0, 0.0)):
    a2.plot([x0, x1], [p(x0), 0], color=RED, lw=1.2)
    a2.plot([x0, x0], [0, p(x0)], color=MUTED, lw=0.8, ls=":")
a2.plot([0, 1], [p(0), p(1)], "o", color=RED, ms=5)
a2.set_ylim(-3, 6)
a2.set_title(T("x³ − 2x + 2，x₀ = 0：在 0 与 1 之间循环", "x³ − 2x + 2 from x₀ = 0: cycles between 0 and 1"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig8_4_2")
