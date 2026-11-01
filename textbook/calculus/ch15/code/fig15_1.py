"""图 15.1.1：左：同一段曲线上，梯形公式用折线（直线段）、辛普森公式用两段抛物线逼近；右：关节五次多项式运动中电机电流
（实线）与 5 Hz 采样点，曲线下的带符号面积是电荷量。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

f = lambda x: 0.6 + 0.8 * np.sin(1.7 * x) + 0.15 * x * x
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
x = np.linspace(0, 2, 400)
a1.plot(x, f(x), color=INK, lw=2.2, label=T("被积函数", "integrand"))
xs = np.linspace(0, 2, 5)
a1.plot(xs, f(xs), "o-", color=BLUE, lw=1.4, ms=5, label=T("梯形：折线", "trapezoid: polyline"))
for k in range(2):
    a, b = xs[2 * k], xs[2 * k + 2]
    m = (a + b) / 2
    c = np.polyfit([a, m, b], [f(a), f(m), f(b)], 2)
    xx = np.linspace(a, b, 100)
    a1.plot(xx, np.polyval(c, xx), color=RED, lw=1.6, ls="--", label=T("辛普森：抛物线", "Simpson: parabolas") if k == 0 else None)
a1.set_xlabel("x")
a1.legend(fontsize=9, frameon=False, loc="lower right")
a1.set_title(T("同样 5 个点：折线与两段抛物线", "Same 5 points: polyline vs two parabolas"), fontsize=10)
clean(a1, zero=False)
Tm, D = 2.0, np.pi / 2
t = np.linspace(0, Tm, 400)
u = t / Tm
om = D / Tm * 30 * u * u * (1 - u) ** 2
al = D / Tm ** 2 * 60 * u * (1 - u) * (1 - 2 * u)
i = 0.5 + 0.8 * al + 0.6 * om
a2.plot(t, i, color=INK, lw=2)
a2.fill_between(t, 0, i, where=i >= 0, color=BLUE, alpha=0.2)
a2.fill_between(t, 0, i, where=i < 0, color=RED, alpha=0.2)
ts = np.linspace(0, Tm, 11)
us = ts / Tm
is_ = 0.5 + 0.8 * D / Tm ** 2 * 60 * us * (1 - us) * (1 - 2 * us) + 0.6 * D / Tm * 30 * us * us * (1 - us) ** 2
a2.plot(ts, is_, "o", color=RED, ms=5)
a2.set_xlabel("t / s")
a2.set_ylabel("i / A")
a2.set_title(T("电流采样（5 Hz）；面积 = 电荷量", "Current samples (5 Hz); area = charge"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig15_1_1")
