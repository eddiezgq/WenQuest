"""图 1.1.1：微积分的两个古老问题——左：切线；右：曲边梯形的面积，用矩形逼近。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.2))
x = np.linspace(-0.2, 2.1, 300)
a1.plot(x, x**2, color=INK, lw=2)
for h, c in ((0.9, MUTED), (0.45, BLUE)):
    m = 2 + h
    a1.plot(x, 1 + m * (x - 1), color=c, lw=1.2, ls="--")
    a1.plot([1 + h], [(1 + h) ** 2], "o", color=c, ms=5)
a1.plot(x, 1 + 2 * (x - 1), color=RED, lw=2)
a1.plot([1], [1], "o", color=RED, mec=INK, ms=7)
a1.text(1.05, 0.55, "$P(1,1)$")
a1.text(1.35, 1.05, T("切线：斜率 2", "tangent: slope 2"), color=RED)
a1.set_xlim(-0.2, 2.1)
a1.set_ylim(-0.5, 4.2)
a1.set_title(T("切线问题：曲线在一点朝哪个方向", "Tangent problem: which way does the curve go?"), fontsize=11)
clean(a1)
n = 8
xs = np.linspace(0, 1, n + 1)
for k in range(n):
    a2.add_patch(plt.Rectangle((xs[k], 0), 1 / n, xs[k + 1] ** 2, fc="#d9e6f2", ec=BLUE, lw=0.8))
xx = np.linspace(0, 1.15, 300)
a2.fill_between(np.linspace(0, 1, 200), np.linspace(0, 1, 200) ** 2, color=ACC, alpha=0.25)
a2.plot(xx, xx**2, color=INK, lw=2)
a2.axvline(1, color=MUTED, lw=0.8, ls=":")
a2.text(0.25, 0.7, T("面积 = ?", "area = ?"), fontsize=13)
a2.set_xlim(-0.05, 1.2)
a2.set_ylim(-0.05, 1.3)
a2.set_title(T("面积问题：曲线下方有多大（8 个矩形）", "Area problem: how much lies under the curve (8 boxes)"), fontsize=11)
clean(a2)
fig.tight_layout()
figure(fig, "fig1_1_1")
