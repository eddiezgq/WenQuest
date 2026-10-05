"""图 11.5.1：左：经济批量——换型成本 DS/Q、库存成本 QH/2 与总成本，最优批量处两者相等，底部很平；
右：价格 p 与收入 R = pq(p)，弹性 |E| = 1 处收入最大。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
D, S, H = 12000, 800.0, 4.0
Q = np.linspace(400, 6000, 400)
a1.plot(Q, D * S / Q, color=BLUE, lw=1.5, label=T("换型成本 DS/Q", "setup DS/Q"))
a1.plot(Q, Q * H / 2, color=GREEN, lw=1.5, label=T("库存成本 QH/2", "holding QH/2"))
a1.plot(Q, D * S / Q + Q * H / 2, color=INK, lw=2.2, label=T("总成本", "total"))
Qs = math.sqrt(2 * D * S / H)
a1.plot([Qs], [D * S / Qs + Qs * H / 2], "o", color=ACC, ms=7)
a1.set_ylim(0, 25000)
a1.set_xlabel(T("每批数量 Q / 件", "batch size Q"))
a1.set_ylabel(T("每年成本 / 元", "cost per year"))
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("最优批量处两项成本相等，曲线底部很平", "At the optimum the two costs are equal; flat bottom"), fontsize=10)
clean(a1, zero=False)
p = np.linspace(1, 99, 300)
q = (100 - p) / 0.02
a2.plot(p, p * q / 1000, color=INK, lw=2, label=T("收入 R / 千元", "revenue R / thousand"))
a2b = a2.twinx()
a2b.plot(p, p / (100 - p), color=RED, lw=1.4, ls="--", label=T("弹性 |E|", "elasticity |E|"))
a2b.set_ylim(0, 4)
a2b.axhline(1, color=MUTED, lw=0.8)
a2.axvline(50, color=MUTED, lw=0.8, ls=":")
a2.set_xlabel(T("价格 p / 元", "price p"))
a2.set_title(T("|E| < 1 时提价增收，|E| > 1 时提价减收", "|E| < 1: raise price; |E| > 1: lower it"), fontsize=10)
h1, l1 = a2.get_legend_handles_labels()
h2, l2 = a2b.get_legend_handles_labels()
a2.legend(h1 + h2, l1 + l2, fontsize=9, frameon=False, loc="upper left")
clean(a2, zero=False)
a2b.spines["top"].set_visible(False)
fig.tight_layout()
figure(fig, "fig11_5_1")
