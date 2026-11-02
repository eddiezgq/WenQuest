"""图 23.5.1：黎曼重排：1 − 1/2 + 1/3 − … 的项重新排列，部分和可以趋于 π、趋于 −1，或按“两正一负”趋于 (3/2) ln 2。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt


def greedy(target, n):
    s, p, q, out = 0.0, 1, 2, []
    for _ in range(n):
        if s <= target:
            s += 1 / p; p += 2
        else:
            s -= 1 / q; q += 2
        out.append(s)
    return np.array(out)


def two_one(nblk):
    s, p, q, out = 0.0, 1, 2, []
    for _ in range(nblk):
        for _k in range(2):
            s += 1 / p; p += 2; out.append(s)
        s -= 1 / q; q += 2; out.append(s)
    return np.array(out)


N = 3000
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
k = np.arange(1, N + 1)
a1.plot(k, np.cumsum((-1.0) ** (k + 1) / k), color=INK, lw=1.2, label=T("原来的顺序 → ln 2", "original order → ln 2"))
a1.plot(k, two_one(N // 3), color=GREEN, lw=1.2, label=T("两正一负 → (3/2) ln 2", "two +, one − → (3/2) ln 2"))
a1.plot(k, greedy(math.pi, N), color=BLUE, lw=1.2, label=T("贪心 → π", "greedy → π"))
a1.plot(k, greedy(-1.0, N), color=RED, lw=1.2, label=T("贪心 → −1", "greedy → −1"))
for v, c in ((math.log(2), INK), (1.5 * math.log(2), GREEN), (math.pi, BLUE), (-1, RED)):
    a1.axhline(v, color=c, ls=":", lw=0.8)
a1.set_xscale("log")
a1.set_xlabel(T("项数（对数坐标）", "terms (log scale)")); a1.set_ylabel(T("部分和", "partial sum"))
a1.set_title(T("同样的项，不同的顺序，不同的和", "Same terms, different order, different sums"), fontsize=10)
a1.legend(fontsize=8.5, frameon=False, loc="center right", bbox_to_anchor=(1.0, 0.62)); clean(a1)
g = greedy(1.0, 60)
a2.step(np.arange(1, 61), g, where="post", color=BLUE, lw=1.5)
a2.plot(np.arange(1, 61), g, "o", color=BLUE, ms=3)
a2.axhline(1.0, color=RED, ls="--", lw=1)
a2.set_xlabel(T("项数", "terms")); a2.set_ylabel(T("部分和", "partial sum"))
a2.set_title(T("构造：低于目标就加正项，高于目标就加负项（目标 1）", "Construction: add positives below the target, negatives above (target 1)"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig23_5_1")
