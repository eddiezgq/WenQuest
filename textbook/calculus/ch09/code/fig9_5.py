"""图 9.5.1：左：sin x 与它的 1、3、5、7、9 次泰勒多项式；右：腕心距离 r(θ₂) 在 60° 处的一次、二次、三次泰勒多项式的误差
（双对数坐标），斜率分别为 2、3、4。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _traj import ur5e_links

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
x = np.linspace(-2 * np.pi, 2 * np.pi, 600)
a1.plot(x, np.sin(x), color=INK, lw=2.4, label="sin x")
cols = [BLUE, GREEN, ACC, RED, MUTED]
for n, c in zip((1, 3, 5, 7, 9), cols):
    p = sum((-1) ** k * x ** (2 * k + 1) / math.factorial(2 * k + 1) for k in range((n + 1) // 2))
    a1.plot(x, p, color=c, lw=1.2, label=f"$P_{n}$")
a1.set_ylim(-2, 2)
a1.set_title(T("次数越高，贴合的范围越宽", "Higher degree, wider agreement"), fontsize=10)
a1.legend(fontsize=8, frameon=False, ncol=3, loc="lower left")
clean(a1)
l1, l2 = ur5e_links()
a, b = l1 * l1 + l2 * l2, 2 * l1 * l2
r = lambda t: np.sqrt(a + b * np.cos(t)) * 1000
t0 = math.radians(60)
R = r(t0) / 1000
R1 = -b * math.sin(t0) / (2 * R)
R2 = (-b * math.cos(t0) / 2 - R1 * R1) / R
R3 = (b * math.sin(t0) / 2 - 3 * R1 * R2) / R
h = 10.0 ** np.linspace(-3, -0.5, 40)
p1 = (R + R1 * h) * 1000
p2 = p1 + R2 / 2 * h ** 2 * 1000
p3 = p2 + R3 / 6 * h ** 3 * 1000
for p, c, lab in ((p1, BLUE, T("一次", "degree 1")), (p2, GREEN, T("二次", "degree 2")), (p3, RED, T("三次", "degree 3"))):
    a2.loglog(h, np.abs(r(t0 + h) - p), "o", color=c, ms=3.5, label=lab)
a2.set_xlabel("h / rad")
a2.set_ylabel(T("误差 / mm", "error / mm"))
a2.set_title(T("n 次多项式的误差 ∝ hⁿ⁺¹", "Error of degree n ∝ hⁿ⁺¹"), fontsize=10)
a2.legend(fontsize=9, frameon=False)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig9_5_1")
