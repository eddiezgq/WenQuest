"""图 9.6.1：左：ln(1 + x) 与它的 5、10、20 次泰勒多项式：|x| < 1 时越来越贴近，x > 1 时越来越离谱；
右：用 15 次泰勒多项式加区间约化计算 sin x，与库函数之差随 |x| 增大而增大（约化时 π/2 的舍入误差被放大）。"""
import math
import random

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
x = np.linspace(-0.95, 2.0, 500)
a1.plot(x, np.log1p(x), color=INK, lw=2.4, label="ln(1 + x)")
for n, c in ((5, BLUE), (10, GREEN), (20, RED)):
    p = sum((-1) ** (k + 1) * x ** k / k for k in range(1, n + 1))
    a1.plot(x, p, color=c, lw=1.2, label=f"$P_{{{n}}}$")
a1.axvline(1, color=MUTED, lw=0.8, ls="--")
a1.set_ylim(-3, 3)
a1.set_title(T("x > 1 时，次数越高越离谱", "Beyond x = 1, higher degree is worse"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="lower right")
clean(a1)


def psin(r):
    return sum((-1) ** k * r ** (2 * k + 1) / math.factorial(2 * k + 1) for k in range(8))


def pcos(r):
    return sum((-1) ** k * r ** (2 * k) / math.factorial(2 * k) for k in range(9))


def mysin(v):
    k = round(v / (math.pi / 2))
    r = v - k * (math.pi / 2)
    return [psin(r), pcos(r), -psin(r), -pcos(r)][k % 4]


random.seed(96)
xs = np.array([random.uniform(-100, 100) for _ in range(6000)])
err = np.array([abs(mysin(v) - math.sin(v)) for v in xs])
a2.semilogy(xs, np.maximum(err, 1e-18), ".", color=BLUE, ms=2)
a2.set_ylim(1e-18, 1e-13)
a2.set_xlabel("x")
a2.set_ylabel(T("与 math.sin 之差", "difference from math.sin"))
a2.set_title(T("多项式本身已到机器精度；误差来自区间约化", "Polynomial at machine precision; error from range reduction"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig9_6_1")
