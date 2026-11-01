"""图 17.5.1：左：AGV 停靠位置误差的正态分布（σ = 3 mm），公差 ±5 mm 内的面积约 90%；
右：零件到达间隔的指数分布（平均 20 s）与减速器寿命的韦布尔分布（η = 20000 h，β = 2），竖线是期望。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
s = 3.0
x = np.linspace(-12, 12, 400)
pdf = np.exp(-x * x / (2 * s * s)) / (s * math.sqrt(2 * math.pi))
a1.plot(x, pdf, color=BLUE, lw=2)
m = np.abs(x) <= 5
a1.fill_between(x[m], 0, pdf[m], color=BLUE, alpha=0.25, label=T("|误差| ≤ 5 mm：约 90.4%", "|error| ≤ 5 mm: about 90.4%"))
a1.set_xlabel(T("停靠位置误差 / mm", "docking error / mm"))
a1.set_ylabel(T("概率密度 / (1/mm)", "density / (1/mm)"))
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("P(a ≤ X ≤ b) = ∫ f(x) dx", "P(a ≤ X ≤ b) = ∫ f(x) dx"), fontsize=10)
clean(a1)
t = np.linspace(0, 100, 300)
a2.plot(t, np.exp(-t / 20) / 20, color=RED, lw=2, label=T("指数分布（零件间隔 / s），期望 20 s", "exponential (gap / s), mean 20 s"))
a2.axvline(20, color=RED, ls="--", lw=1)
u = np.linspace(0, 2.5, 300)
ax2 = a2.twiny()
eta = 20000
f = 2 / eta * u * np.exp(-u ** 2) * 1
ax2.plot(u * eta / 1000, 2 * u * np.exp(-u ** 2) / eta * 1000, color=GREEN, lw=2)
ax2.axvline(eta * math.gamma(1.5) / 1000, color=GREEN, ls="--", lw=1)
ax2.set_xlabel(T("寿命 / (1000 h)（绿：韦布尔，β = 2，期望 17.7×10³ h）", "life / (1000 h) (green: Weibull β = 2, mean 17.7×10³ h)"), color=GREEN, fontsize=9)
a2.set_xlabel(T("到达间隔 / s（红）", "gap / s (red)"), color=RED)
a2.set_ylabel(T("概率密度（相对）", "density (relative)"))
a2.legend(fontsize=9, frameon=False, loc="upper right")
a2.set_yticks([])
clean(a2)
fig.tight_layout()
figure(fig, "fig17_5_1")
