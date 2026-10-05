"""图 12.3.1：左：一般的黎曼和——分点不等距、每个小区间里任意取一点；右：随机分割、随机取点的黎曼和随分点数增加而收敛（e^{−x²}，[0, 2]）。"""
import math
import random

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

f = lambda x: np.exp(-x * x)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
rnd = random.Random(7)
cuts = sorted([0.0, 2.0] + [rnd.uniform(0, 2) for _ in range(7)])
x = np.linspace(0, 2, 300)
for a, b in zip(cuts, cuts[1:]):
    xi = rnd.uniform(a, b)
    a1.add_patch(plt.Rectangle((a, 0), b - a, f(xi), facecolor=BLUE, alpha=0.25, edgecolor=BLUE, lw=0.8))
    a1.plot([xi], [f(xi)], "o", color=RED, ms=4)
    a1.axvline(a, color=MUTED, lw=0.5)
a1.plot(x, f(x), color=INK, lw=2)
a1.set_title(T("分点 xᵢ 任意，取点 ξᵢ（红点）任意", "Arbitrary partition and tags ξᵢ (red)"), fontsize=10)
clean(a1, zero=False)
ref = 0.5 * math.sqrt(math.pi) * math.erf(2.0)
rnd = random.Random(123)
for n in (5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000):
    for _ in range(20):
        c = sorted([0.0, 2.0] + [rnd.uniform(0, 2) for _ in range(n - 1)])
        s = sum(float(f(rnd.uniform(a, b))) * (b - a) for a, b in zip(c, c[1:]))
        a2.semilogx([n], [s], ".", color=BLUE, ms=3)
a2.axhline(ref, color=RED, lw=1)
a2.set_xlabel(T("小区间个数 n", "number of subintervals n"))
a2.set_ylabel(T("黎曼和", "Riemann sum"))
a2.set_title(T("分得越细，各种取法的黎曼和越聚拢", "Finer partitions: all sums close in"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig12_3_1")
