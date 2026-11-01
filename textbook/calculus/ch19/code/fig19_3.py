"""图 19.3.1：左：清洁机器人水箱的剩余水量——重力排水（h′ = −c√h）与保持初始流量的比较；
右：逻辑斯谛曲线 P(t) = K/(1 + ((K − P0)/P0)e^(−rt)) 与它的增长率，拐点在 P = K/2。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
g, A, d, Cd, h0 = 9.81, 0.03, 4e-3, 0.6, 0.2
c = Cd * np.pi * d * d / 4 * np.sqrt(2 * g) / A
Tm = 2 * np.sqrt(h0) / c
t = np.linspace(0, 900, 500)
h = np.where(t < Tm, (np.sqrt(h0) - c * t / 2) ** 2, 0.0)
a1.plot(t / 60, A * h * 1000, color=BLUE, lw=2, label=T("重力排水：h′ = −c√h", "gravity drain: h′ = −c√h"))
a1.plot(t / 60, np.maximum(6 - 6 * t / (Tm / 2), 0), color=ACC, lw=2, ls="--", label=T("保持初始流量", "constant initial flow"))
th = Tm * (1 - 1 / np.sqrt(2))
a1.plot([th / 60], [3], "o", color=RED)
a1.annotate(T("流出一半：约 3.9 min", "half gone: about 3.9 min"), (th / 60, 3), xytext=(5.5, 4.2), fontsize=9, color=RED,
            arrowprops=dict(arrowstyle="->", color=RED, lw=0.8))
a1.set_xlabel(T("时间 t / min", "time t / min"))
a1.set_ylabel(T("剩余水量 / L", "water left / L"))
a1.set_title(T("清洁机器人水箱：前一半水流得快，后一半很慢", "Cleaning-robot tank: the first half drains fast, the rest slowly"), fontsize=10)
a1.legend(fontsize=9, frameon=False)
clean(a1)
K, r, P0 = 1000.0, 0.5, 10.0
t = np.linspace(0, 20, 400)
P = K / (1 + (K - P0) / P0 * np.exp(-r * t))
a2.plot(t, P, color=BLUE, lw=2, label=T("P(t)", "P(t)"))
a2.axhline(K, color=MUTED, ls=":", lw=1)
ts = np.log((K - P0) / P0) / r
a2.plot([ts], [K / 2], "o", color=RED)
a2.text(ts + 0.4, K / 2 - 60, T("拐点 P = K/2", "inflection P = K/2"), color=RED, fontsize=9)
b = a2.twinx()
b.plot(t, r * P * (1 - P / K), color=GREEN, lw=1.5, ls="--")
b.set_ylabel(T("增长率 P′（虚线）", "growth rate P′ (dashed)"), color=GREEN, fontsize=9)
b.spines["top"].set_visible(False)
a2.set_xlabel(T("时间 t / h", "time t / h"))
a2.set_ylabel(T("数量 P / 百万个", "population P / million"))
a2.set_title(T("逻辑斯谛曲线：K = 1000，r = 0.5 /h，P₀ = 10", "Logistic curve: K = 1000, r = 0.5 /h, P₀ = 10"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig19_3_1")
