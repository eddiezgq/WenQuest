"""图 15.2.1：左：∫₀¹ e^{−x²} dx 的误差随函数求值次数的变化（双对数）——梯形（斜率 −2）、辛普森（−4）、龙贝格、高斯；
右：周期函数 1/(1 + 0.5 cos θ) 在一个周期上的梯形公式，误差按指数衰减。"""
import math

import numpy as np

from _quad import gauss, romberg, simpson, trap
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

f = lambda x: math.exp(-x * x)
ex = 0.5 * math.sqrt(math.pi) * math.erf(1.0)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4))
ns = [2, 4, 8, 16, 32, 64, 128, 256]
a1.loglog([n + 1 for n in ns], [abs(trap(f, 0, 1, n) - ex) for n in ns], "o-", color=BLUE, label=T("梯形", "trapezoid"))
a1.loglog([n + 1 for n in ns], [abs(simpson(f, 0, 1, n) - ex) for n in ns], "s-", color=GREEN, label=T("辛普森", "Simpson"))
R = romberg(f, 0, 1, 7)
a1.loglog([2 ** k + 1 for k in range(7)], [max(abs(R[k][k] - ex), 1e-17) for k in range(7)], "^-", color=RED, label=T("龙贝格", "Romberg"))
gn = [2, 3, 4, 5, 6, 7, 8]
a1.loglog(gn, [max(abs(gauss(f, 0, 1, n) - ex), 1e-17) for n in gn], "d-", color=ACC, label=T("高斯", "Gauss"))
a1.set_ylim(1e-17, 1)
a1.set_xlabel(T("函数求值次数", "function evaluations"))
a1.set_ylabel(T("误差", "error"))
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("阶越高，同样的运算量误差越小", "Higher order, less error for the same work"), fontsize=10)
clean(a1, zero=False)
g = lambda t: 1 / (1 + 0.5 * math.cos(t))
exg = 2 * math.pi / math.sqrt(0.75)
nn = [2, 4, 6, 8, 12, 16, 20, 24, 28, 32]
a2.semilogy(nn, [max(abs(trap(g, 0, 2 * math.pi, n) - exg), 1e-17) for n in nn], "o-", color=BLUE, label=T("梯形", "trapezoid"))
a2.semilogy(nn, [max(abs(simpson(g, 0, 2 * math.pi, n) - exg), 1e-17) for n in nn], "s-", color=GREEN, label=T("辛普森", "Simpson"))
a2.set_xlabel(T("分点数 n", "number of points n"))
a2.legend(fontsize=9, frameon=False)
a2.set_title(T("周期函数整周期：梯形公式指数收敛", "Periodic, full period: trapezoid converges exponentially"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig15_2_1")
