"""图 15.7.1：左：Γ 函数（x > 0），在正整数处等于阶乘；右：减速器寿命的韦布尔可靠度曲线 R(t) = exp(−(t/η)^β)，
η = 20000 h，β = 1、2、3；曲线下的面积是平均寿命（竖线）。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
x = np.linspace(0.08, 5.2, 400)
a1.plot(x, [math.gamma(v) for v in x], color=BLUE, lw=2)
for n in range(1, 6):
    a1.plot([n], [math.factorial(n - 1)], "o", color=RED, ms=5)
a1.plot([0.5], [math.sqrt(math.pi)], "s", color=GREEN, ms=6)
a1.text(0.6, math.sqrt(math.pi) + 0.6, "Γ(1/2) = √π", color=GREEN, fontsize=10)
a1.set_ylim(0, 26)
a1.set_xlabel("x")
a1.set_ylabel("Γ(x)")
a1.set_title(T("Γ(n) = (n − 1)!：阶乘的连续推广", "Γ(n) = (n − 1)!: factorial made continuous"), fontsize=10)
clean(a1, zero=False)
eta = 20000.0
t = np.linspace(0, 60000, 600)
for beta, c in ((1.0, RED), (2.0, BLUE), (3.0, GREEN)):
    a2.plot(t / 1000, np.exp(-(t / eta) ** beta), color=c, lw=2, label=f"β = {beta:g}")
    m = eta * math.gamma(1 + 1 / beta)
    a2.axvline(m / 1000, color=c, lw=0.8, ls="--")
a2.set_xlabel(T("运行时间 t / 千小时", "running time t / 1000 h"))
a2.set_ylabel(T("可靠度 R(t)", "reliability R(t)"))
a2.legend(fontsize=9, frameon=False)
a2.set_title(T(r"平均寿命 = $\int_0^\infty R(t)\,dt = \eta\,\Gamma(1 + 1/\beta)$（竖线）", r"Mean life = $\int_0^\infty R(t)\,dt = \eta\,\Gamma(1 + 1/\beta)$ (dashed)"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig15_7_1")
