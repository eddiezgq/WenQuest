"""图 12.4.1：左：积分中值定理——sin x 在 [0, π] 下的面积等于高为平均值 2/π 的矩形面积，ξ 有两个；右：估值不等式——
∫₀¹ e^{−x²} dx 夹在 1 − x² 与 1 下的面积之间。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
x = np.linspace(0, np.pi, 300)
m = 2 / np.pi
a1.fill_between(x, 0, np.sin(x), color=BLUE, alpha=0.2)
a1.add_patch(plt.Rectangle((0, 0), np.pi, m, facecolor="none", edgecolor=RED, lw=1.5))
a1.plot(x, np.sin(x), color=INK, lw=2)
for xi in (math.asin(m), math.pi - math.asin(m)):
    a1.plot([xi], [m], "o", color=ACC, ms=7)
a1.text(0.15, m + 0.04, "2/π", color=RED, fontsize=10)
a1.set_title(T("面积 2 = 平均高度 2/π × 宽度 π", "Area 2 = mean height 2/π × width π"), fontsize=10)
clean(a1, zero=False)
x = np.linspace(0, 1, 300)
a2.fill_between(x, 1 - x ** 2, np.exp(-x * x), color=GREEN, alpha=0.25)
a2.plot(x, np.exp(-x * x), color=INK, lw=2, label="$e^{-x^2}$")
a2.plot(x, 1 - x ** 2, color=BLUE, lw=1.4, ls="--", label="$1 - x^2$")
a2.plot(x, 1 - x ** 2 + x ** 4 / 2, color=ACC, lw=1.4, ls=":", label="$1 - x^2 + x^4/2$")
a2.axhline(1, color=RED, lw=1.2, ls="--", label="1")
a2.set_ylim(0, 1.1)
a2.legend(fontsize=9, frameon=False, loc="lower left")
a2.set_title(T("被积函数夹在中间，积分也夹在中间", "Squeeze the integrand, squeeze the integral"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig12_4_1")
