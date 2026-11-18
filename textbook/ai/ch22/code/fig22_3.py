"""22.2 节的图之一：同样的误差，成本差几倍。

图 22.2.1：（a）申报偏置扫描——成本曲线与均方根误差曲线的最低点**不在同一处**；
（b）罚金比例一变，最优申报偏置就跟着移——**“该报多少”的答案在电价规则里，不在模型里**。
"""
import numpy as np

from _ch22 import (cloud_factor, design_matrix, fit_ls, imbalance_cost, pv_series, tou_price)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N_DAYS, UP, DOWN = 60, 1.6, 0.5

pv = pv_series(N_DAYS, seed=0)
cl = cloud_factor(N_DAYS, seed=0)
g = np.random.default_rng(5)
X = design_matrix(N_DAYS, np.clip(cl + 0.12 * g.normal(0, 1, len(cl)), 0, 1))
cut = int(len(pv) * 0.7)
w = fit_ls(X[:cut], pv[:cut])
pred = np.maximum(X[cut:] @ w, 0.0)
truth, price = pv[cut:], tou_price(N_DAYS)[cut:]

biases = np.arange(-60, 21, 2.0)
costs = np.array([imbalance_cost(truth, np.maximum(pred + b, 0.0), price, UP, DOWN)
                  for b in biases])
rmses = np.array([float(np.sqrt(np.mean((np.maximum(pred + b, 0.0) - truth) ** 2)))
                  for b in biases])
i_c, i_r = int(np.argmin(costs)), int(np.argmin(rmses))

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 两条曲线的最低点不在同一处
a.plot(biases, costs, color=C["x"], lw=2.2, label=T("偏差成本（元）", "imbalance cost (CNY)"))
a.plot(biases[i_c], costs[i_c], "o", color=C["x"], ms=9)
a.annotate(T(f"成本最低：{biases[i_c]:+.0f} kW", f"cheapest: {biases[i_c]:+.0f} kW"),
           xy=(biases[i_c], costs[i_c]), xytext=(26, 34), textcoords="offset points",
           fontsize=9, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.2))
a.set_xlabel(T("申报偏置（kW，负号 = 往低报）", "declaration bias (kW, negative = under-declare)"))
a.set_ylabel(T("偏差成本（元）", "imbalance cost (CNY)"), color=C["x"])
a.tick_params(axis="y", labelcolor=C["x"])
a2 = a.twinx()
a2.plot(biases, rmses, color=C["z"], lw=2.0, ls="--",
        label=T("均方根误差（kW）", "RMSE (kW)"))
a2.plot(biases[i_r], rmses[i_r], "s", color=C["z"], ms=8)
a2.annotate(T(f"误差最低：{biases[i_r]:+.0f} kW", f"lowest RMSE: {biases[i_r]:+.0f} kW"),
            xy=(biases[i_r], rmses[i_r]), xytext=(14, 54), textcoords="offset points",
            fontsize=9, color=C["z"],
            arrowprops=dict(arrowstyle="->", color=C["z"], lw=1.2))
a2.set_ylabel(T("均方根误差（kW）", "RMSE (kW)"), color=C["z"])
a2.tick_params(axis="y", labelcolor=C["z"])
a.axvspan(min(biases[i_c], biases[i_r]), max(biases[i_c], biases[i_r]),
          color=C["accent"], alpha=0.10)
a.set_title(T("(a) 两条曲线的最低点不在同一处", "(a) the two curves bottom out in different places"),
            fontsize=10)
a.annotate(T(f"差 {abs(biases[i_r] - biases[i_c]):.0f} kW：\n照成本调，省 "
             f"{(1 - costs[i_c] / costs[i_r]) * 100:.1f}%，\n代价是均方根误差差了 "
             f"{(rmses[i_c] / rmses[i_r] - 1) * 100:.1f}%",
             f"{abs(biases[i_r] - biases[i_c]):.0f} kW apart: tuning on cost saves "
             f"{(1 - costs[i_c] / costs[i_r]) * 100:.1f}%\nat {(rmses[i_c] / rmses[i_r] - 1) * 100:.1f}% worse RMSE"),
           xy=(0.97, 0.96), xycoords="axes fraction", ha="right", va="top",
           fontsize=8.5, color=C["accent"])
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 罚金比例一变，最优偏置就移
ups = np.array([1.2, 1.6, 2.0, 2.5, 3.0, 4.0])
best = []
for up in ups:
    cs = [imbalance_cost(truth, np.maximum(pred + bb, 0.0), price, up, DOWN) for bb in biases]
    best.append(biases[int(np.argmin(cs))])
best = np.array(best)
b.plot(ups, best, "o-", color=C["x"], lw=2.2, ms=7)
for u, bv in zip(ups, best):
    b.annotate(f"{bv:+.0f}", xy=(u, bv), xytext=(0, 9), textcoords="offset points",
               ha="center", fontsize=8.5, color=C["x"])
b.axhline(0, color=C["muted"], lw=1.2, ls=":")
b.annotate(T("0 = 照模型原样申报", "0 = declare the raw forecast"),
           xy=(ups[-1], 0), xytext=(-6, 7), textcoords="offset points",
           ha="right", fontsize=8.5, color=C["ink"])
b.set_xlabel(T("少发的罚金（倍电价；多发按 0.5 倍贱卖）",
                "shortfall penalty (× price; surplus sold at 0.5×)"))
b.set_ylabel(T("成本最低的申报偏置（kW）", "cost-optimal declaration bias (kW)"))
b.set_ylim(min(best) - 16, 12)
b.set_title(T("(b) 罚金越重，申报越要保守", "(b) the heavier the penalty, the more conservative"),
            fontsize=10)
b.annotate(T(f"罚金从 {ups[0]:.1f} 倍到 {ups[-1]:.1f} 倍，最优偏置移了 "
             f"{best[0] - best[-1]:.0f} kW——\n模型一个字没改，该报多少却变了",
             f"from {ups[0]:.1f}× to {ups[-1]:.1f}× the optimum moves {best[0] - best[-1]:.0f} kW;\n"
             f"the model never changed"),
           xy=(0.5, 0.12), xycoords="axes fraction", ha="center", va="bottom",
           fontsize=8.5, color=C["accent"])
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig22_2_1")
