"""22.2 节的图之二：储能调度，以及“预测值多少钱”。

图 22.2.2：（a）一天里光伏、负荷、电价与储能的荷电状态——真最优是在**便宜的时候存，
贵的时候放**；（b）同一个模型，换一套结算规则，预测精度的价值差几十倍。
"""
import numpy as np

from _ch22 import (BATTERY, DT_H, STEPS_PER_DAY, cloud_factor, design_matrix,
                   dispatch_cost, fit_ls, load_series, optimal_dispatch, pv_series,
                   rule_dispatch, safe_layer, tou_price)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N_DAYS, TEST_DAYS, UP, DOWN = 40, 6, 1.6, 0.5

pv = pv_series(N_DAYS, seed=0)
cl = cloud_factor(N_DAYS, seed=0)
load = load_series(N_DAYS, seed=0)
price = tou_price(N_DAYS)
g = np.random.default_rng(5)
X = design_matrix(N_DAYS, np.clip(cl + 0.12 * g.normal(0, 1, len(cl)), 0, 1))
cut = (N_DAYS - TEST_DAYS) * STEPS_PER_DAY
w_mid = fit_ls(X[:cut], pv[:cut])
fc_mid = np.maximum(X[cut:] @ w_mid, 0.0)
truth, L, P = pv[cut:], load[cut:], price[cut:]

plan_opt = np.empty(len(truth))
for d in range(TEST_DAYS):
    sl = slice(d * STEPS_PER_DAY, (d + 1) * STEPS_PER_DAY)
    plan_opt[sl] = optimal_dispatch(truth[sl], L[sl], P[sl])[1]
_, soc_opt, _ = dispatch_cost(truth, L, P, safe_layer(plan_opt, truth, L))
_, soc_rule, _ = dispatch_cost(truth, L, P, safe_layer(rule_dispatch(truth, L, P), truth, L))

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 一天的样子
D = 1
sl = slice(D * STEPS_PER_DAY, (D + 1) * STEPS_PER_DAY)
t = np.arange(STEPS_PER_DAY) * DT_H
a.plot(t, truth[sl], color=C["y"], lw=2.0, label=T("光伏出力", "PV output"))
a.plot(t, L[sl], color=C["ink"], lw=2.0, label=T("车间负荷", "workshop load"))
a.fill_between(t, 0, np.where(P[sl] > P[sl].mean(), a.get_ylim()[1], 0),
               color=C["accent"], alpha=0.10, step="mid",
               label=T("电价高于平均的时段", "above-average price hours"))
a.set_xlabel(T("时间（小时）", "time of day (h)"))
a.set_ylabel(T("功率（kW）", "power (kW)"))
a.set_xlim(0, 24)
a.set_ylim(0, 600)
a2 = a.twinx()
a2.plot(t, soc_opt[sl] / BATTERY["cap_kwh"] * 100, color=C["x"], lw=2.2,
        label=T("荷电状态：真最优", "state of charge: optimum"))
a2.plot(t, soc_rule[sl] / BATTERY["cap_kwh"] * 100, color=C["z"], lw=1.8, ls="--",
        label=T("荷电状态：规则策略", "state of charge: rule"))
a2.axhline(BATTERY["soc_min"] * 100, color=C["muted"], lw=1.0, ls=":")
a2.axhline(BATTERY["soc_max"] * 100, color=C["muted"], lw=1.0, ls=":")
a2.set_ylabel(T("荷电状态（%）", "state of charge (%)"))
a2.set_ylim(0, 108)
a2.annotate(T("上下限（不许越过）", "limits (never cross)"),
            xy=(23.6, BATTERY["soc_max"] * 100), xytext=(0, 3), textcoords="offset points",
            ha="right", fontsize=8, color=C["muted"])
h1, l1 = a.get_legend_handles_labels()
h2, l2 = a2.get_legend_handles_labels()
a.legend(h1 + h2, l1 + l2, fontsize=7.6, loc="upper left", framealpha=0.92, ncol=2)
a.set_title(T("(a) 便宜的时候存，贵的时候放", "(a) store when power is cheap, release when dear"),
            fontsize=10)
a.grid(alpha=0.25, lw=0.5)


# ---------------- (b) 预测精度值多少钱
def plan_from(fc_pv):
    plan = np.empty(len(truth))
    declared = np.empty(len(truth))
    for d in range(TEST_DAYS):
        s = slice(d * STEPS_PER_DAY, (d + 1) * STEPS_PER_DAY)
        p = optimal_dispatch(np.maximum(fc_pv[s], 0.0), L[s], P[s])[1]
        plan[s] = p
        declared[s] = L[s] - np.maximum(fc_pv[s], 0.0) + p
    return safe_layer(plan, truth, L), declared


def settle(fc_pv):
    plan, declared = plan_from(fc_pv)
    actual = L - truth + plan
    base = float(np.sum(np.maximum(declared, 0.0) * P) * DT_H)
    dd = actual - declared
    extra = float(np.sum(np.maximum(dd, 0.0) * P * UP
                         - np.maximum(-dd, 0.0) * P * DOWN) * DT_H)
    return base + extra


shrinks = np.array([1.0, 0.75, 0.5, 0.25, 0.0])
rm, c_plain, c_settle = [], [], []
for s in shrinks:
    better = truth + (fc_mid - truth) * s
    rm.append(float(np.sqrt(np.mean((better - truth) ** 2))))
    plan, _ = plan_from(better)
    c_plain.append(dispatch_cost(truth, L, P, plan)[0])
    c_settle.append(settle(better))
rm = np.array(rm)
rel_plain = (np.array(c_plain) / c_plain[-1] - 1) * 100
rel_settle = (np.array(c_settle) / c_settle[-1] - 1) * 100
b.plot(rm, rel_plain, "o-", color=C["z"], lw=2.0, ms=6,
       label=T("只有分时电价", "time-of-use price only"))
b.plot(rm, rel_settle, "s-", color=C["x"], lw=2.2, ms=6,
       label=T("加上日前申报 + 偏差考核", "plus day-ahead declaration & imbalance penalty"))
for xx, yy in ((rm[0], rel_plain[0]), (rm[0], rel_settle[0])):
    b.annotate(f"+{yy:.2f}%", xy=(xx, yy), xytext=(-6, 0), textcoords="offset points",
               ha="right", va="center", fontsize=9,
               color=C["x"] if yy > 1 else C["z"])
b.set_xlabel(T("预测的均方根误差（kW，0 = 完美预测）",
                "forecast RMSE (kW, 0 = perfect foresight)"))
b.set_ylabel(T("比完美预测贵多少（%）", "cost premium over perfect foresight (%)"))
b.set_title(T("(b) 同一个模型，换一套结算规则就值钱了",
              "(b) same model, different settlement rules, different value"), fontsize=10)
b.annotate(T(f"差 {rel_settle[0] / max(rel_plain[0], 1e-9):.0f} 倍——\n"
             f"“预测值多少钱”的答案在结算规则里，不在模型里",
             f"{rel_settle[0] / max(rel_plain[0], 1e-9):.0f}× apart — what a forecast is worth "
             f"is set by the rules, not the model"),
           xy=(0.97, 0.30), xycoords="axes fraction", ha="right", va="center",
           fontsize=8.5, color=C["accent"])
b.legend(fontsize=8, loc="upper left", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig22_2_2")
