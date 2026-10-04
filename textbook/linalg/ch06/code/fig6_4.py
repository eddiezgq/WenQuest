"""图 6.4.1：计算 n 阶行列式所需的乘法次数（对数坐标）：排列公式约 n·n!，消元约 n³/3。"""
import math

import numpy as np

from _fig import BLUE, RED, T, figure, plt

n = np.arange(2, 26)
fig, ax = plt.subplots(figsize=(6.4, 4.0))
ax.semilogy(n, [float(k) * float(math.factorial(int(k))) for k in n], "o-", color=RED, ms=4, label=T("排列公式 n·n!", "permutation formula n·n!"))
ax.semilogy(n, n ** 3 / 3, "s-", color=BLUE, ms=4, label=T("消元 n³/3", "elimination n³/3"))
ax.axhline(8.64e15, color="#999999", lw=0.8, ls="--")
ax.text(2.3, 2e16, T("每秒 10¹¹ 次的计算机一天约 8.6×10¹⁵ 次", "10¹¹ per second: about 8.6×10¹⁵ per day"), fontsize=9, color="#666666")
ax.set_xlabel("n")
ax.set_ylabel(T("乘法次数", "multiplications"))
ax.legend(frameon=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig6_4_1")
