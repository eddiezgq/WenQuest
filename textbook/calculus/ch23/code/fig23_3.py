"""图 23.3.1：左：积分判别法，Σ1/k² 的余项夹在两个积分之间；右：数字控制器的单位脉冲响应 hₙ = n·0.9ⁿ 与 Σ|hₙ| 的部分和。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
x = np.linspace(2.5, 12, 300)
n = 3
for k in range(n + 1, 12):
    a1.add_patch(plt.Rectangle((k - 1, 0), 1, 1 / k ** 2, facecolor=BLUE, alpha=0.25, edgecolor=BLUE, lw=0.8))
    a1.add_patch(plt.Rectangle((k, 0), 1, 1 / k ** 2, facecolor="none", edgecolor=GREEN, lw=1.0, ls="--"))
a1.plot(x, 1 / x ** 2, color=RED, lw=2, label="y = 1/x²")
a1.axvline(n, color=MUTED, ls=":", lw=1)
a1.text(5.6, 0.06, T(r"蓝色矩形：余项 $R_n\leq\int_n^{\infty}$" + "\n" + r"绿色虚线：$R_n\geq\int_{n+1}^{\infty}$（n = 3）", r"blue: $R_n\leq\int_n^{\infty}$" + "\n" + r"green dashed: $R_n\geq\int_{n+1}^{\infty}$ (n = 3)"), fontsize=9, linespacing=1.9)
a1.set_xlabel("x"); a1.set_ylabel("y"); a1.set_ylim(0, 0.115)
a1.set_title(T("积分判别法：用面积夹住余项", "Integral test: areas bracket the remainder"), fontsize=10)
a1.legend(fontsize=9, frameon=False); clean(a1)
k = np.arange(0, 80)
h = k * 0.9 ** k
a2.bar(k, h, color=BLUE, alpha=0.7, width=0.8, label=T("hₙ = n·0.9ⁿ", "hₙ = n·0.9ⁿ"))
b = a2.twinx()
b.plot(k, np.cumsum(h), color=RED, lw=2, label=T("部分和 Σ|hₙ|", "partial sum Σ|hₙ|"))
b.axhline(90, color=RED, ls=":", lw=1)
b.text(45, 82, T("和 = 0.9/(1 − 0.9)² = 90", "sum = 0.9/(1 − 0.9)² = 90"), color=RED, fontsize=9)
b.set_ylabel(T("部分和", "partial sum"), color=RED); b.set_ylim(0, 100); b.spines["top"].set_visible(False)
a2.set_xlabel(T("采样序号 n", "sample n")); a2.set_ylabel("hₙ", color=BLUE)
a2.set_title(T("脉冲响应绝对可和 ⇒ 有界输入有界输出", "Absolutely summable impulse response ⇒ BIBO stable"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig23_3_1")
