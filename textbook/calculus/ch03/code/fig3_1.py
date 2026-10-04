"""图 3.1.1：数列的图像是一串离散的点。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
n = np.arange(1, 31)
a1.plot(n, 1 / n, "o", color=BLUE, ms=4, label="$1/n$")
a1.plot(n, (-1.0) ** n / n, "s", color=RED, ms=4, label="$(-1)^n/n$")
a1.plot(n, (-1.0) ** n * 1.0, "^", color=MUTED, ms=4, label="$(-1)^n$")
a1.set_xlabel("n")
a1.set_ylim(-1.3, 1.3)
a1.legend(fontsize=9, frameon=False, loc="upper right", ncol=3)
a1.set_title(T("两个收敛于 0，一个发散", "Two converge to 0, one diverges"), fontsize=10)
clean(a1)
n = np.arange(1, 21)
a2.plot(n, (1 + 1 / n) ** n, "o", color=ACC, ms=4, label="$(1+1/n)^n$")
a2.axhline(np.e, color=ACC, lw=0.8, ls="--")
a2.text(15, np.e + 0.04, "$e$", color=ACC)
x = [2.0]
for _ in range(5):
    x.append((x[-1] + 2 / x[-1]) / 2)
a2.plot(range(1, 7), x, "s-", color=GREEN, ms=5, lw=1, label=T("求 √2 的迭代 (3.1.1)", "iteration (3.1.1) for √2"))
a2.axhline(np.sqrt(2), color=GREEN, lw=0.8, ls="--")
a2.set_xlabel("n")
a2.set_ylim(1.3, 2.9)
a2.legend(fontsize=9, frameon=False, loc="center right")
a2.set_title(T("复利数列与迭代数列", "Compound interest and an iteration"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig3_1_1")

# 图 3.1.2：刘徽割圆，正 6、12、24 边形
fig, axs = plt.subplots(1, 3, figsize=(10, 3.6))
t = np.linspace(0, 2 * np.pi, 400)
for ax, n in zip(axs, (6, 12, 24)):
    ax.fill(np.cos(t), np.sin(t), color=ACC, alpha=0.25)
    ax.plot(np.cos(t), np.sin(t), color=INK, lw=1.2)
    k = np.arange(n + 1)
    px, py = np.cos(2 * np.pi * k / n + np.pi / 2), np.sin(2 * np.pi * k / n + np.pi / 2)
    ax.fill(px, py, color="white")
    ax.fill(px, py, color=BLUE, alpha=0.25)
    ax.plot(px, py, color=BLUE, lw=1.4)
    S = n / 2 * np.sin(2 * np.pi / n)
    ax.set_title(T(f"正 {n} 边形：面积 {S:.4f}", f"{n}-gon: area {S:.4f}"), fontsize=10)
    ax.set_aspect("equal")
    ax.axis("off")
fig.tight_layout()
figure(fig, "fig3_1_2")
