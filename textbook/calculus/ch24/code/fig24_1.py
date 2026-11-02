"""图 24.1.1：左：1/(1 + x²) 与它的幂级数的部分和，|x| > 1 时部分和发散；右：复平面上的收敛圆，奇点 ±i 决定半径 1。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

x = np.linspace(-1.5, 1.5, 600)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
a1.plot(x, 1 / (1 + x * x), color=INK, lw=2.5, label="1/(1 + x²)")
for n, col in ((2, RED), (5, ACC), (10, GREEN), (20, BLUE)):
    S = sum((-x * x) ** k for k in range(n + 1))
    sup = str(2 * n).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))
    a1.plot(x, S, color=col, lw=1.3, label=T(f"部分和到 x{sup}", f"partial sum to x{sup}"))
a1.axvspan(-1, 1, color=GREEN, alpha=0.06)
a1.axvline(-1, color=MUTED, ls=":", lw=1); a1.axvline(1, color=MUTED, ls=":", lw=1)
a1.set_ylim(-1, 2); a1.set_xlabel("x"); a1.set_ylabel("y")
a1.set_title(T("函数处处光滑，级数却只在 |x| < 1 收敛", "Smooth everywhere, yet the series converges only for |x| < 1"), fontsize=10)
a1.legend(fontsize=8.5, frameon=False, loc="upper right", ncol=1); clean(a1)
th = np.linspace(0, 2 * np.pi, 300)
a2.fill(np.cos(th), np.sin(th), color=GREEN, alpha=0.12)
a2.plot(np.cos(th), np.sin(th), color=GREEN, lw=2, label=T("收敛圆 |z| = 1", "circle of convergence |z| = 1"))
a2.plot([0, 0], [1, -1], "x", color=RED, ms=12, mew=3, label=T("奇点 z = ±i（分母为零）", "singularities z = ±i"))
a2.axhline(0, color=MUTED, lw=0.8); a2.axvline(0, color=MUTED, lw=0.8)
a2.plot([-1.5, 1.5], [0, 0], color=INK, lw=3, alpha=0.4)
a2.text(1.05, 0.08, T("实轴：处处光滑", "real axis: smooth"), fontsize=9)
a2.set_xlim(-1.8, 1.8); a2.set_ylim(-1.5, 1.5); a2.set_aspect("equal")
a2.set_xlabel("Re z"); a2.set_ylabel("Im z")
a2.set_title(T("收敛半径 = 到最近奇点的距离", "Radius = distance to the nearest singularity"), fontsize=10)
a2.legend(fontsize=8.5, frameon=False, loc="lower right")
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig24_1_1")
