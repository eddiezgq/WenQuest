"""图 15.3.1：左：2～5 点高斯–勒让德求积的节点（圆点位置）与权（竖线高度）；右：∫₀¹ e^{−x²} dx 在同样的求值次数下，
高斯与辛普森的误差。"""
import math

import numpy as np

from _quad import gauss, gauss_nodes, simpson
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
for row, n in enumerate((2, 3, 4, 5)):
    xs, ws = gauss_nodes(n)
    y0 = 4 - row
    a1.hlines(y0, -1, 1, color=MUTED, lw=0.8)
    for x, w in zip(xs, ws):
        a1.vlines(x, y0, y0 + 0.8 * w, color=BLUE, lw=3)
        a1.plot([x], [y0], "o", color=RED, ms=5)
    a1.text(-1.25, y0, f"n = {n}", va="center", fontsize=10)
a1.set_xlim(-1.35, 1.1)
a1.set_ylim(0.6, 5.2)
a1.set_yticks([])
a1.set_xlabel("x")
a1.set_title(T("节点不等距，向两端加密；竖线高度为权", "Nodes crowd toward the ends; bar height = weight"), fontsize=10)
clean(a1, zero=False)
a1.spines["left"].set_visible(False)
f = lambda x: math.exp(-x * x)
ex = 0.5 * math.sqrt(math.pi) * math.erf(1.0)
ns = [3, 5, 7, 9, 11]
a2.semilogy(ns, [abs(simpson(f, 0, 1, n - 1) - ex) for n in ns], "s-", color=GREEN, label=T("辛普森", "Simpson"))
a2.semilogy(ns[:4], [max(abs(gauss(f, 0, 1, n) - ex), 1e-17) for n in ns[:4]], "d-", color=ACC, label=T("高斯", "Gauss"))
a2.set_xlabel(T("函数求值次数", "function evaluations"))
a2.set_ylabel(T("误差", "error"))
a2.legend(fontsize=9, frameon=False)
a2.set_title(T("同样 9 次求值：高斯误差小到舍入误差", "With 9 evaluations Gauss reaches round-off"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig15_3_1")
