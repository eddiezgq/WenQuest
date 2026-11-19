"""22.6 节的图：问渠减速器厂的光伏 + 储能微网。

图 22.6.1：（a）一天里从电网买多少电——不装储能、规则策略、按预测调度三条线；
（b）六天电费的阶梯：每一级是谁省下来的，**最上面那一级（预测准不准）最小**。
"""
import numpy as np

from _ch22 import (DT_H, STEPS_PER_DAY, cloud_factor, design_matrix, dispatch_cost,
                   fit_ls, load_series, optimal_dispatch, pv_series, rule_dispatch,
                   safe_layer, tou_price)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N_DAYS, TEST_DAYS = 40, 6

pv = pv_series(N_DAYS, seed=0)
cl = cloud_factor(N_DAYS, seed=0)
load = load_series(N_DAYS, seed=0)
price = tou_price(N_DAYS)
g = np.random.default_rng(5)
X = design_matrix(N_DAYS, np.clip(cl + 0.12 * g.normal(0, 1, len(cl)), 0, 1))
cut = (N_DAYS - TEST_DAYS) * STEPS_PER_DAY
w = fit_ls(X[:cut], pv[:cut])
fc = np.maximum(X[cut:] @ w, 0.0)
truth, L, P = pv[cut:], load[cut:], price[cut:]


def by_day(fc_pv):
    plan = np.empty(len(truth))
    for d in range(TEST_DAYS):
        s = slice(d * STEPS_PER_DAY, (d + 1) * STEPS_PER_DAY)
        plan[s] = optimal_dispatch(np.maximum(fc_pv[s], 0.0), L[s], P[s])[1]
    return safe_layer(plan, truth, L)


plan_fc = by_day(fc)
plan_opt = by_day(truth)
plan_rule = safe_layer(rule_dispatch(truth, L, P), truth, L)
cost_none = dispatch_cost(truth, L, P, np.zeros(len(truth)))[0]
cost_rule = dispatch_cost(truth, L, P, plan_rule)[0]
cost_fc = dispatch_cost(truth, L, P, plan_fc)[0]
cost_opt = dispatch_cost(truth, L, P, plan_opt)[0]

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 一天从电网买多少
D = 2
sl = slice(D * STEPS_PER_DAY, (D + 1) * STEPS_PER_DAY)
t = np.arange(STEPS_PER_DAY) * DT_H
grid_none = (L - truth)[sl]
grid_rule = (L - truth + plan_rule)[sl]
grid_fc = (L - truth + plan_fc)[sl]
peak = P[sl] >= P.max() - 1e-9
valley = P[sl] <= P.min() + 1e-9
a.fill_between(t, -120, 560, where=peak, color=C["x"], alpha=0.10, step="mid",
               label=T("峰电价时段", "peak-price hours"))
a.fill_between(t, -120, 560, where=valley, color=C["z"], alpha=0.10, step="mid",
               label=T("谷电价时段", "valley-price hours"))
a.plot(t, grid_none, color=C["muted"], lw=1.8, label=T("不装储能", "no battery"))
a.plot(t, grid_rule, color=C["z"], lw=1.8, ls="--", label=T("规则策略（谷充峰放）", "rule policy"))
a.plot(t, grid_fc, color=C["x"], lw=2.0, label=T("按预测调度", "forecast-driven dispatch"))
a.axhline(0, color=C["ink"], lw=1.0, ls=":")
a.annotate(T("0 以下 = 余电上网", "below 0 = exporting"), xy=(0.4, 0), xytext=(0, -14),
           textcoords="offset points", fontsize=8, color=C["ink"])
a.set_xlim(0, 24)
a.set_ylim(-120, 560)
a.set_xlabel(T("时间（小时）", "time of day (h)"))
a.set_ylabel(T("从电网买的功率（kW）", "power drawn from the grid (kW)"))
pk_none = float(np.sum(np.maximum(grid_none, 0)[peak]) * DT_H)
pk_fc = float(np.sum(np.maximum(grid_fc, 0)[peak]) * DT_H)
vl_none = float(np.sum(np.maximum(grid_none, 0)[valley]) * DT_H)
vl_fc = float(np.sum(np.maximum(grid_fc, 0)[valley]) * DT_H)
a.set_title(T("(a) 谷时多买一点，峰时少买一截", "(a) buy more at valley price, less at peak"),
            fontsize=10)
a.annotate(T(f"这一天：峰段购电 {pk_none:.0f} → {pk_fc:.0f} kWh，"
             f"谷段 {vl_none:.0f} → {vl_fc:.0f} kWh",
             f"this day: peak-hour purchases {pk_none:.0f} → {pk_fc:.0f} kWh, "
             f"valley {vl_none:.0f} → {vl_fc:.0f} kWh"),
           xy=(0.98, 0.04), xycoords="axes fraction", ha="right", va="bottom",
           fontsize=8.5, color=C["accent"])
a.legend(fontsize=8, loc="upper left", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 电费阶梯
steps = [
    (T("不装储能", "no battery"), cost_none, C["muted"]),
    (T("装了储能\n谷充峰放", "battery with\na simple rule"), cost_rule, C["z"]),
    (T("按预测\n排计划", "dispatch on\nthe forecast"), cost_fc, C["x"]),
    (T("完美预知\n（上限）", "perfect foresight\n(the ceiling)"), cost_opt, C["y"]),
]
xs = np.arange(len(steps))
vals = np.array([s[1] for s in steps]) / 1000.0
b.bar(xs, vals, 0.52, color=[s[2] for s in steps])
for i, vv in enumerate(vals):
    b.annotate(f"{vv:.1f}", xy=(i, vv), xytext=(0, 4), textcoords="offset points",
               ha="center", fontsize=9, color=C["ink"])
for i in range(1, len(steps)):
    drop = (vals[i - 1] - vals[i]) / vals[0] * 100
    b.annotate(T(f"−{drop:.1f}%", f"−{drop:.1f}%"),
               xy=(i - 0.5, (vals[i - 1] + vals[i]) / 2), ha="center", va="bottom",
               fontsize=9, color=C["accent"])
    b.annotate("", xy=(i - 0.12, vals[i]), xytext=(i - 0.88, vals[i - 1]),
               arrowprops=dict(arrowstyle="->", color=C["accent"], lw=1.3))
b.set_xticks(xs)
b.set_xticklabels([s[0] for s in steps], fontsize=8.5)
b.set_ylabel(T(f"{TEST_DAYS} 天电费（千元）", f"{TEST_DAYS}-day bill (thousand CNY)"))
b.set_ylim(0, vals.max() * 1.35)
b.set_title(T("(b) 每一级是谁省下来的", "(b) who saves what, step by step"), fontsize=10)
b.annotate(T("装储能那一级最大，排计划那一级其次，预测准不准那一级最小——\n"
             "这还是在只有分时电价、没有申报考核的规则下。换一套有偏差考核的\n"
             "规则，最上面那一级立刻变大（见图 22.2.2）",
             "the battery step is the big one; the forecast step is the smallest — "
             "and that is\nwithout an imbalance penalty (see Figure 22.2.2)"),
           xy=(0.5, 0.97), xycoords="axes fraction", ha="center", va="top",
           fontsize=8.2, color=C["accent"])
b.grid(alpha=0.25, lw=0.5, axis="y")

fig.tight_layout()
figure(fig, "fig22_6_1")
