"""图 18.2.1：左：托马伊函数（黎曼函数）在 [0, 1] 上的图像：x = p/q 处高 1/q，无理数处为 0；
右：振幅和 U − L 随等分数 n 的变化（双对数）：连续函数与阶梯函数按 1/n 下降，托马伊函数下降得慢，狄利克雷函数始终为 1。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.1))
pts = set()
for q in range(1, 60):
    for p in range(0, q + 1):
        if math.gcd(p, q) == 1:
            pts.add((p / q, 1 / q))
xs, ys = zip(*sorted(pts))
a1.vlines(xs, 0, ys, color=BLUE, lw=0.4, alpha=0.5)
a1.plot(xs, ys, "o", color=BLUE, ms=2)
a1.set_xlabel("x")
a1.set_title(T("托马伊函数：在每个有理数处间断，在每个无理数处连续", "Thomae's function: discontinuous at every rational, continuous at every irrational"), fontsize=10)
clean(a1)


def thomae_upper(n):
    s = 0.0
    for k in range(n):
        for q in range(1, n + 1):
            if math.ceil(k * q / n) <= math.floor((k + 1) * q / n):
                s += 1 / q / n
                break
    return s


ns = [5, 10, 20, 50, 100, 200, 500, 1000]
a2.loglog(ns, [1 / n for n in ns], "o-", color=INK, label=T("x²（连续）", "x² (continuous)"))
a2.loglog(ns, [1 / n for n in ns], "s--", color=GREEN, ms=4, label=T("阶梯函数（5 个跳跃，振幅和恰为 1/n）", "step function (5 jumps; sum exactly 1/n)"))
a2.loglog(ns, [thomae_upper(n) for n in ns], "^-", color=BLUE, label=T("托马伊函数", "Thomae's function"))
a2.loglog(ns, [1 for n in ns], "x-", color=RED, label=T("狄利克雷函数：恒为 1", "Dirichlet function: always 1"))
a2.set_xlabel(T("等分数 n", "number of pieces n"))
a2.set_ylabel(T("振幅和 Σωᵢ Δxᵢ = U − L", "oscillation sum Σωᵢ Δxᵢ = U − L"))
a2.legend(fontsize=8, frameon=False)
a2.set_title(T("可积 ⇔ 振幅和能任意小", "Integrable ⇔ the oscillation sum can be made small"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig18_2_1")
