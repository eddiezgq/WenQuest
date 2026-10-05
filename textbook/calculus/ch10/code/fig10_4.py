"""图 10.4.1：左：y = x³/(x − 1)² 的图像，铅直渐近线 x = 1、斜渐近线 y = x + 2、极小值点 (3, 27/4)、拐点 (0, 0)；
右：作图程序的陷阱——sin(2π·99x) 只在 101 个等距点上取值时，连起来像 −sin(2πx)。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.4))
for lo, hi in ((-4, 0.93), (1.07, 8)):
    x = np.linspace(lo, hi, 500)
    a1.plot(x, x ** 3 / (x - 1) ** 2, color=INK, lw=2)
xx = np.linspace(-4, 8, 10)
a1.plot(xx, xx + 2, color=RED, lw=1, ls="--", label=T("斜渐近线 y = x + 2", "oblique asymptote y = x + 2"))
a1.axvline(1, color=BLUE, lw=1, ls="--", label=T("铅直渐近线 x = 1", "vertical asymptote x = 1"))
a1.plot([3], [27 / 4], "o", color=ACC, ms=7)
a1.plot([0], [0], "s", color=GREEN, ms=6)
a1.annotate(T("极小值", "local min"), (3, 6.75), xytext=(3.6, 3.5), fontsize=9, arrowprops=dict(arrowstyle="->", color=MUTED))
a1.annotate(T("拐点", "inflection"), (0, 0), xytext=(-1.8, 2.5), fontsize=9, arrowprops=dict(arrowstyle="->", color=MUTED))
a1.set_ylim(-8, 16)
a1.set_title("y = x³/(x − 1)²", fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="upper left")
clean(a1)
x = np.linspace(0, 1, 4000)
a2.plot(x, np.sin(2 * np.pi * 99 * x), color=MUTED, lw=0.4, label=T("真实曲线", "true curve"))
xs = np.arange(101) / 100
a2.plot(xs, np.sin(2 * np.pi * 99 * xs), "o-", color=RED, ms=3, lw=1.2, label=T("101 个采样点连线", "101 samples joined"))
a2.set_title(T("采样太稀：程序画出的是另一条曲线", "Too few samples: the plot shows another curve"), fontsize=10)
a2.legend(fontsize=9, frameon=True, framealpha=1, loc="lower left")
clean(a2)
fig.tight_layout()
figure(fig, "fig10_4_1")
