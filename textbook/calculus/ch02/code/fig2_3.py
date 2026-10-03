"""图 2.3.1：函数的四种性质——奇偶、周期、有界、单调。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, axs = plt.subplots(2, 2, figsize=(10, 7))
a = axs[0, 0]
x = np.linspace(-2, 2, 400)
a.plot(x, x**2 - 1, color=BLUE, lw=2, label=T("偶函数 x² − 1", "even: x² − 1"))
a.plot(x, x**3 - x, color=RED, lw=2, label=T("奇函数 x³ − x", "odd: x³ − x"))
a.axvline(0, color=MUTED, lw=0.6)
a.set_ylim(-3, 3)
a.legend(fontsize=9, frameon=False, loc="upper center")
a.set_title(T("奇偶：关于 y 轴、原点对称", "Even and odd: symmetric about the y-axis / origin"), fontsize=10)
clean(a)
a = axs[0, 1]
Tg = 0.5
t = np.linspace(0, 1.5, 1000)
k = -90 + 20 * np.sin(2 * np.pi * t / Tg) + 6 * np.sin(4 * np.pi * t / Tg + 0.6)
a.plot(t, k, color=GREEN, lw=2)
for j in range(4):
    a.axvline(j * Tg, color=MUTED, lw=0.6, ls=":")
a.annotate("", xy=(Tg, -62), xytext=(0, -62), arrowprops=dict(arrowstyle="<->", color=INK))
a.text(Tg / 2, -60, T("周期 Tg", "period Tg"), ha="center")
a.set_ylim(-120, -55)
a.set_xlabel("t / s")
a.set_title(T("周期：四足机器人膝关节角 / (°)", "Periodic: quadruped knee angle / (°)"), fontsize=10)
clean(a, zero=False)
a = axs[1, 0]
x = np.linspace(-6, 6, 600)
a.plot(x, x / (1 + x**2), color=ACC, lw=2)
a.axhline(0.5, color=RED, lw=1, ls="--")
a.axhline(-0.5, color=RED, lw=1, ls="--")
a.text(3, 0.53, T("上界 1/2", "upper bound 1/2"), color=RED)
a.text(-6, -0.62, T("下界 −1/2", "lower bound −1/2"), color=RED)
a.set_ylim(-0.75, 0.75)
a.set_title(T("有界：x/(1+x²)", "Bounded: x/(1+x²)"), fontsize=10)
clean(a)
a = axs[1, 1]
x = np.linspace(-2, 2, 400)
a.plot(x, x**3, color=BLUE, lw=2, label="$x^3$")
for xs in (np.linspace(-2, -0.25, 200), np.linspace(0.25, 2, 200)):
    a.plot(xs, 1 / xs, color=RED, lw=2, label="$1/x$" if xs[0] > 0 else None)
a.set_ylim(-5, 5)
a.legend(fontsize=9, frameon=False)
a.set_title(T("单调：x³ 递增；1/x 在两个区间上各自递减", "Monotonic: x³ increases; 1/x decreases on each interval"), fontsize=10)
clean(a)
fig.tight_layout()
figure(fig, "fig2_3_1")
