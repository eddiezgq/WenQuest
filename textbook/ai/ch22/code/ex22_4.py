"""算例 22.4.1—22.4.3：储能调度，以及预测误差怎样变成电费（22.2、22.6 节）。

三件事：
（1）**先把真最优解算出来**（动态规划，知道未来的全部真值）——有了它，
    其他办法好不好才有尺子；
（2）**按预测调度要亏多少**：同一套策略，喂真值与喂预测，电费差多少；
（3）**用哪个分位数去调度**：喂中位数、喂 10% 分位、喂 90% 分位，哪个最省。

这一节的结论会很具体：预测准不准，最后是用**电费**来衡量的。
"""
import numpy as np

from _ch22 import (BATTERY, DT_H, STEPS_PER_DAY, cloud_factor, design_matrix,
                   dispatch_cost, fit_ls, fit_quantile, load_series, optimal_dispatch,
                   pv_series, rule_dispatch, safe_layer, tou_price)
from bookout import out

N_DAYS, TEST_DAYS = 40, 6
v = {"n_days": N_DAYS, "test_days": TEST_DAYS,
     "cap_kwh": BATTERY["cap_kwh"], "p_max_kw": BATTERY["p_max_kw"],
     "eta": BATTERY["eta"]}

pv = pv_series(N_DAYS, seed=0)
cl = cloud_factor(N_DAYS, seed=0)
load = load_series(N_DAYS, seed=0)
price = tou_price(N_DAYS)
g = np.random.default_rng(5)
X = design_matrix(N_DAYS, np.clip(cl + 0.12 * g.normal(0, 1, len(cl)), 0, 1))

cut = (N_DAYS - TEST_DAYS) * STEPS_PER_DAY
w_mid = fit_ls(X[:cut], pv[:cut])
w_lo = fit_quantile(X[:cut], pv[:cut], 0.1)
w_hi = fit_quantile(X[:cut], pv[:cut], 0.9)
fc = {"mid": np.maximum(X[cut:] @ w_mid, 0.0),
      "lo": np.maximum(X[cut:] @ w_lo, 0.0),
      "hi": np.maximum(X[cut:] @ w_hi, 0.0)}
truth, L, P = pv[cut:], load[cut:], price[cut:]
v["n_test_steps"] = len(truth)
v["rmse_mid"] = float(np.sqrt(np.mean((fc["mid"] - truth) ** 2)))
print(f"测试段 {TEST_DAYS} 天（{len(truth)} 个点），点预测的均方根误差 {v['rmse_mid']:.2f} kW")


def run(plan):
    """把计划交给真实的光伏与负荷，算电费与越界次数。"""
    c, _, viol = dispatch_cost(truth, L, P, safe_layer(plan, truth, L))
    return c, viol


# ---------- 一、三条基线
cost_nobat, _, _ = dispatch_cost(truth, L, P, np.zeros(len(truth)))
v["cost_nobattery"] = cost_nobat
cost_opt_total = 0.0
plan_opt = np.empty(len(truth))
for d in range(TEST_DAYS):
    sl = slice(d * STEPS_PER_DAY, (d + 1) * STEPS_PER_DAY)
    _, p = optimal_dispatch(truth[sl], L[sl], P[sl])
    plan_opt[sl] = p
v["cost_oracle"], v["viol_oracle"] = run(plan_opt)
v["cost_rule"], v["viol_rule"] = run(rule_dispatch(truth, L, P))
print(f"不装储能：          电费 {v['cost_nobattery']:,.0f} 元")
print(f"规则策略（谷充峰放）：电费 {v['cost_rule']:,.0f} 元，越界 {v['viol_rule']} 次")
print(f"真最优（知道未来）： 电费 {v['cost_oracle']:,.0f} 元，越界 {v['viol_oracle']} 次")
v["save_rule_pct"] = (1 - v["cost_rule"] / v["cost_nobattery"]) * 100
v["save_opt_pct"] = (1 - v["cost_oracle"] / v["cost_nobattery"]) * 100
assert v["cost_oracle"] < v["cost_rule"] < v["cost_nobattery"], \
    "最优要胜过规则，规则要胜过不装储能"
print(f"规则省 {v['save_rule_pct']:.1f}%，真最优省 {v['save_opt_pct']:.1f}%——"
      f"**中间这段差距，才是“更好的调度”能拿走的东西**")

# ---------- 二、按预测调度亏多少
for tag, name in (("mid", "点预测（中位数）"), ("lo", "10% 分位（保守）"),
                  ("hi", "90% 分位（乐观）")):
    plan = np.empty(len(truth))
    for d in range(TEST_DAYS):
        sl = slice(d * STEPS_PER_DAY, (d + 1) * STEPS_PER_DAY)
        _, p = optimal_dispatch(fc[tag][sl], L[sl], P[sl])    # 按预测排计划
        plan[sl] = p
    c, viol = run(plan)                                       # 真实世界结算
    v[f"cost_{tag}"] = c
    v[f"viol_{tag}"] = viol
    v[f"gap_{tag}_pct"] = (c / v["cost_oracle"] - 1) * 100
    print(f"{name:>16}：电费 {c:,.0f} 元，比真最优贵 {v[f'gap_{tag}_pct']:.2f}%，"
          f"越界 {viol} 次")
v["best_quantile"] = min(("mid", "lo", "hi"), key=lambda t: v[f"cost_{t}"])
print(f"**三者里最省的是：{ {'mid': '点预测', 'lo': '10% 分位', 'hi': '90% 分位'}[v['best_quantile']] }**")
print("注意这件事没有通用答案：哪个分位数最省，取决于电价结构与储能容量，要**按自己的参数算**")

# ---------- 三、预测准一点，值多少钱
# 把预测人为改好：误差按比例缩小
for shrink, tag in ((1.0, "100"), (0.5, "50"), (0.25, "25"), (0.0, "0")):
    better = truth + (fc["mid"] - truth) * shrink
    plan = np.empty(len(truth))
    for d in range(TEST_DAYS):
        sl = slice(d * STEPS_PER_DAY, (d + 1) * STEPS_PER_DAY)
        _, p = optimal_dispatch(np.maximum(better[sl], 0.0), L[sl], P[sl])
        plan[sl] = p
    c, _ = run(plan)
    v[f"cost_shrink{tag}"] = c
    v[f"rmse_shrink{tag}"] = float(np.sqrt(np.mean((better - truth) ** 2)))
    print(f"预测误差缩到 {shrink:.0%}（均方根 {v[f'rmse_shrink{tag}']:5.2f} kW）："
          f"电费 {c:,.0f} 元")
v["value_per_kw"] = ((v["cost_shrink100"] - v["cost_shrink0"])
                     / max(v["rmse_shrink100"], 1e-9))
v["value_pct"] = (v["cost_shrink100"] / v["cost_shrink0"] - 1) * 100
print(f"\n**在这套参数下，预测准到什么程度几乎不影响电费**："
      f"误差从 {v['rmse_shrink100']:.1f} kW 降到 0，{TEST_DAYS} 天只省 "
      f"{v['cost_shrink100'] - v['cost_shrink0']:,.0f} 元（{v['value_pct']:.2f}%）")
print("原因看得见：储能容量相对负荷不大，电费主要由分时电价的套利决定，"
      "**调度几乎不依赖对光伏的预测**")

# ---------- 四、换一套结算规则，预测立刻值钱
# 加上"日前申报 + 偏差考核"：要提前申报每个时段从电网买多少，实际与申报不符按
# 非对称价格结算（少买了按 1.6 倍补、多买了按 0.5 倍退）。
UP, DOWN = 1.6, 0.5
v["up"], v["down"] = UP, DOWN


def settle(fc_pv):
    """按预测申报、按真实结算：返回总成本。"""
    plan = np.empty(len(truth))
    declared = np.empty(len(truth))
    for d in range(TEST_DAYS):
        sl = slice(d * STEPS_PER_DAY, (d + 1) * STEPS_PER_DAY)
        _, p = optimal_dispatch(np.maximum(fc_pv[sl], 0.0), L[sl], P[sl])
        plan[sl] = p
        declared[sl] = L[sl] - np.maximum(fc_pv[sl], 0.0) + p      # 申报的购电曲线
    plan = safe_layer(plan, truth, L)
    actual = L - truth + plan
    base = float(np.sum(np.maximum(declared, 0.0) * P) * DT_H)     # 按申报结算的电费
    d = actual - declared
    extra = float(np.sum(np.maximum(d, 0.0) * P * UP
                         + np.maximum(-d, 0.0) * P * DOWN * -1.0) * DT_H)
    return base + extra


for shrink, tag in ((1.0, "s100"), (0.5, "s50"), (0.25, "s25"), (0.0, "s0")):
    better = truth + (fc["mid"] - truth) * shrink
    v[f"settle_{tag}"] = settle(better)
    print(f"有申报考核时，预测误差缩到 {shrink:.0%}：总成本 {v[f'settle_{tag}']:,.0f} 元")
v["settle_value_per_kw"] = ((v["settle_s100"] - v["settle_s0"])
                            / max(v["rmse_shrink100"], 1e-9))
v["settle_value_pct"] = (v["settle_s100"] / v["settle_s0"] - 1) * 100
v["value_ratio"] = (v["settle_s100"] - v["settle_s0"]) / max(
    v["cost_shrink100"] - v["cost_shrink0"], 1e-9)
print(f"\n同样把误差降到 0，有申报考核时省 "
      f"{v['settle_s100'] - v['settle_s0']:,.0f} 元（{v['settle_value_pct']:.1f}%），"
      f"是没有考核时的 {v['value_ratio']:.0f} 倍")
print(f"折成单价：**预测均方根误差每降 1 kW，{TEST_DAYS} 天省约 "
      f"{v['settle_value_per_kw']:,.0f} 元**")
print("**所以“预测值多少钱”这个问题，答案在结算规则里，不在模型里**——"
      "换一套规则，同一个模型的价值能差几十倍")

# ---------- 五、案例要印的那一天（22.6 节）
# 取测试段里的第 3 天，分别算峰段与谷段从电网买了多少电
D = 2
sl = slice(D * STEPS_PER_DAY, (D + 1) * STEPS_PER_DAY)
peak_mask = P[sl] >= P.max() - 1e-9
valley_mask = P[sl] <= P.min() + 1e-9
plan_fc = np.empty(len(truth))
for d in range(TEST_DAYS):
    s2 = slice(d * STEPS_PER_DAY, (d + 1) * STEPS_PER_DAY)
    _, p = optimal_dispatch(np.maximum(fc["mid"][s2], 0.0), L[s2], P[s2])
    plan_fc[s2] = p
plan_fc = safe_layer(plan_fc, truth, L)
grid_none = (L - truth)[sl]
grid_fc = (L - truth + plan_fc)[sl]
for tag, mask in (("peak", peak_mask), ("valley", valley_mask)):
    v[f"{tag}_kwh_none"] = float(np.sum(np.maximum(grid_none, 0.0)[mask]) * DT_H)
    v[f"{tag}_kwh_fc"] = float(np.sum(np.maximum(grid_fc, 0.0)[mask]) * DT_H)
print(f"\n案例那一天：峰段购电 {v['peak_kwh_none']:.0f} → {v['peak_kwh_fc']:.0f} kWh，"
      f"谷段 {v['valley_kwh_none']:.0f} → {v['valley_kwh_fc']:.0f} kWh")

out(**v)
