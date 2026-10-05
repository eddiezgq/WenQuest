"""图 12.6.1：无穷维的两个现象。(a) 连续函数 tanh(nx) 在 L² 距离下越来越接近，极限 sign x 却不连续：连续函数的空间“有洞”，不完备；
(b) 帕塞瓦尔等式：方波的傅里叶系数平方和 π Σ b_k² 随项数增加逼近 ‖f‖² = 2π，剩余部分约按 1/N 减小。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

x = np.linspace(-1, 1, 2001)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 3.9))
for n, c in ((1, BLUE), (5, GREEN), (25, ACC)):
    a1.plot(x, np.tanh(n * x), color=c, lw=1.5, label=f"tanh({n}x)")
a1.plot([-1, 0], [-1, -1], color=RED, lw=2.2, label="sign x")
a1.plot([0, 1], [1, 1], color=RED, lw=2.2)
a1.plot([0], [0], "o", color=RED, ms=4)
a1.axhline(0, color=MUTED, lw=0.6); a1.axvline(0, color=MUTED, lw=0.6)
a1.legend(frameon=False, fontsize=9, loc="upper left")
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.set_title(T("(a) 连续函数的极限可以不连续", "(a) A limit of continuous functions need not be continuous"), fontsize=11)
N = np.arange(1, 2002, 2)
s = np.cumsum(16 / (N ** 2 * np.pi ** 2)) * np.pi
a2.loglog(N, 2 * np.pi - s, color=BLUE, lw=1.6, label=r"$2\pi - \pi\sum_{k\leq N} b_k^2$")
a2.loglog(N, 8 / (np.pi * N), color=MUTED, lw=1, ls="--", label=r"$8/(\pi N)$")
a2.set_xlabel(T("取到第 N 次谐波", "harmonics up to N"))
a2.legend(frameon=False, fontsize=9)
for sp in ("top", "right"):
    a2.spines[sp].set_visible(False)
a2.set_title(T("(b) 帕塞瓦尔等式：系数平方和趋于 ‖f‖²", "(b) Parseval: the sum of squares tends to ‖f‖²"), fontsize=11)
fig.tight_layout()
figure(fig, "fig12_6_1")
