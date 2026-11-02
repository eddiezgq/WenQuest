"""图 23.4.1：左：1 − 1/2 + 1/3 − … 的部分和锯齿形地逼近 ln 2，误差不超过下一项；右：绝对值级数 Σ1/k 发散。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

n = np.arange(1, 31)
S = np.cumsum((-1.0) ** (n + 1) / n)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
a1.plot(n, S, "o-", color=BLUE, ms=4, lw=1.2, label=T("部分和 Sₙ", "partial sums Sₙ"))
a1.axhline(math.log(2), color=RED, lw=1.5, label="ln 2")
a1.fill_between(n, math.log(2) - 1 / (n + 1), math.log(2) + 1 / (n + 1), color=RED, alpha=0.1, label=T("|Sₙ − ln 2| ≤ 1/(n + 1)", "|Sₙ − ln 2| ≤ 1/(n + 1)"))
a1.set_ylim(0.3, 1.05)
a1.set_xlabel(T("项数 n", "terms n")); a1.set_ylabel("Sₙ")
a1.set_title(T("交错级数：部分和在极限两侧跳动", "Alternating series: partial sums straddle the limit"), fontsize=10)
a1.legend(fontsize=9, frameon=False); clean(a1, zero=False)
N = np.arange(1, 2001)
a2.semilogx(N, np.cumsum((-1.0) ** (N + 1) / N), color=BLUE, lw=1.5, label="Σ(−1)ᵏ⁺¹/k")
a2.semilogx(N, np.cumsum(1.0 / N), color=RED, lw=2, label="Σ1/k")
a2.semilogx(N, np.cumsum((-1.0) ** (N + 1) / N ** 2), color=GREEN, lw=1.5, label="Σ(−1)ᵏ⁺¹/k²")
a2.semilogx(N, np.cumsum(1.0 / N ** 2), color=ACC, lw=2, label="Σ1/k²")
a2.set_xlabel(T("项数 n（对数坐标）", "terms n (log scale)")); a2.set_ylabel(T("部分和", "partial sum"))
a2.set_title(T("条件收敛（蓝）与绝对收敛（绿）", "Conditional (blue) vs absolute (green) convergence"), fontsize=10)
a2.legend(fontsize=9, frameon=False, loc="upper left"); clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig23_4_1")
