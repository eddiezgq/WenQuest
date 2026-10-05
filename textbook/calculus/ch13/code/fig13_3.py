"""图 13.3.1：f(x) = cos x 的原函数族 sin x + C：每条曲线在同一个 x 处的斜率都相同（短线段），
它们互相平移；初始条件 F(0) = 0.5 从中选出一条。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, ax = plt.subplots(figsize=(7, 4.4))
x = np.linspace(-np.pi, 2 * np.pi, 400)
for C in np.arange(-2, 2.01, 0.5):
    ax.plot(x, np.sin(x) + C, color=MUTED if abs(C - 0.5) > 1e-9 else RED, lw=0.9 if abs(C - 0.5) > 1e-9 else 2.2)
for xs in np.linspace(-np.pi, 2 * np.pi, 13):
    for ys in np.arange(-2.5, 3.01, 0.5):
        k = np.cos(xs)
        d = 0.18 / np.hypot(1, k)
        ax.plot([xs - d, xs + d], [ys - k * d, ys + k * d], color=BLUE, lw=0.8, alpha=0.6)
ax.plot([0], [0.5], "o", color=RED, ms=6)
ax.set_xlabel("x")
ax.set_title(T("cos x 的原函数 sin x + C；红线满足 F(0) = 0.5", "Antiderivatives sin x + C of cos x; red: F(0) = 0.5"), fontsize=10)
clean(ax)
fig.tight_layout()
figure(fig, "fig13_3_1")
