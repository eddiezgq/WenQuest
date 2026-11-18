"""算例 22.2.1—22.2.3：同样的均方根误差，成本可以差几倍（22.2 节）。

发电计划要提前申报，实际与计划不符就要结算，而**两个方向的价钱不一样**：
少发了要按高价买电补上，多发了只能贱卖。于是：

（1）**同样大小的误差，偏一边与偏另一边，成本差几倍**；
（2）**把点预测往下压一点（故意保守），总成本反而更低**——最优的"申报偏置"能算出来；
（3）**均方根误差最小的预测，不是成本最低的预测**。本算例把这两条曲线画在一起。

这是全书那条线在本章的样子：**拿一个指标做决定，必然被另一个指标反咬**。
"""
import numpy as np

from _ch22 import (DT_H, cloud_factor, design_matrix, fit_ls, imbalance_cost,
                   pv_series, tou_price)
from bookout import out

N_DAYS = 60
UP, DOWN = 1.6, 0.5          # 少发按 1.6 倍电价买、多发按 0.5 倍贱卖（显式假设）
v = {"n_days": N_DAYS, "up": UP, "down": DOWN}

pv = pv_series(N_DAYS, seed=0)
cl = cloud_factor(N_DAYS, seed=0)
g = np.random.default_rng(5)
X = design_matrix(N_DAYS, np.clip(cl + 0.12 * g.normal(0, 1, len(cl)), 0, 1))
cut = int(len(pv) * 0.7)
w = fit_ls(X[:cut], pv[:cut])
pred = np.maximum(X[cut:] @ w, 0.0)
truth = pv[cut:]
price = tou_price(N_DAYS)[cut:]
v["n_test"] = len(truth)

base_rmse = float(np.sqrt(np.mean((pred - truth) ** 2)))
v["rmse_base"] = base_rmse
v["cost_base"] = imbalance_cost(truth, pred, price, UP, DOWN)
print(f"原始预测：均方根误差 {base_rmse:.2f} kW，偏差成本 {v['cost_base']:,.0f} 元")

# ---------- 一、同样大小的误差，方向不同
for sign, tag in ((+1, "over"), (-1, "under")):
    shifted = np.maximum(pred + sign * 20.0, 0.0)
    v[f"rmse_{tag}"] = float(np.sqrt(np.mean((shifted - truth) ** 2)))
    v[f"cost_{tag}"] = imbalance_cost(truth, shifted, price, UP, DOWN)
    name = "往高报 20 kW" if sign > 0 else "往低报 20 kW"
    print(f"{name}：均方根误差 {v[f'rmse_{tag}']:.2f} kW，"
          f"偏差成本 {v[f'cost_{tag}']:,.0f} 元")
v["cost_dir_ratio"] = v["cost_over"] / v["cost_under"]
print(f"**两边的均方根误差几乎一样（{v['rmse_over']:.2f} 对 {v['rmse_under']:.2f}），"
      f"成本却差 {v['cost_dir_ratio']:.2f} 倍**")
assert v["cost_over"] > v["cost_under"], "少发要按高价补，所以往高报更贵"

# ---------- 二、最优的申报偏置
biases = np.arange(-60, 21, 2.0)
costs, rmses = [], []
for b in biases:
    p = np.maximum(pred + b, 0.0)
    costs.append(imbalance_cost(truth, p, price, UP, DOWN))
    rmses.append(float(np.sqrt(np.mean((p - truth) ** 2))))
costs, rmses = np.array(costs), np.array(rmses)
i_cost, i_rmse = int(np.argmin(costs)), int(np.argmin(rmses))
v["best_bias_cost"] = float(biases[i_cost])
v["best_bias_rmse"] = float(biases[i_rmse])
v["cost_at_best"] = float(costs[i_cost])
v["cost_at_rmse_best"] = float(costs[i_rmse])
v["rmse_at_best_cost"] = float(rmses[i_cost])
v["rmse_at_rmse_best"] = float(rmses[i_rmse])
v["cost_saving_pct"] = (1 - v["cost_at_best"] / v["cost_at_rmse_best"]) * 100
v["rmse_penalty_pct"] = (v["rmse_at_best_cost"] / v["rmse_at_rmse_best"] - 1) * 100
print(f"\n成本最低的申报偏置是 {v['best_bias_cost']:+.0f} kW（成本 {v['cost_at_best']:,.0f} 元，"
      f"均方根误差 {v['rmse_at_best_cost']:.2f} kW）")
print(f"均方根误差最低的偏置是 {v['best_bias_rmse']:+.0f} kW（成本 {v['cost_at_rmse_best']:,.0f} 元，"
      f"均方根误差 {v['rmse_at_rmse_best']:.2f} kW）")
assert v["best_bias_cost"] < v["best_bias_rmse"], "罚金不对称时，最优申报要保守一点"
print(f"**照成本调，省 {v['cost_saving_pct']:.1f}%，代价是均方根误差差了 "
      f"{v['rmse_penalty_pct']:.1f}%**——这两条曲线的最低点不在同一处")

# ---------- 三、罚金比例一变，最优偏置就变
for up, tag in ((1.2, "12"), (1.6, "16"), (2.5, "25"), (4.0, "40")):
    cs = [imbalance_cost(truth, np.maximum(pred + b, 0.0), price, up, DOWN) for b in biases]
    bb = float(biases[int(np.argmin(cs))])
    v[f"bias_up{tag}"] = bb
    print(f"少发的罚金 {up:.1f} 倍电价：最优申报偏置 {bb:+.0f} kW")
assert v["bias_up40"] <= v["bias_up12"], "罚金越重，申报越要保守"
v["bias_span"] = v["bias_up12"] - v["bias_up40"]
print(f"罚金从 1.2 倍到 4.0 倍，最优偏置移了 {v['bias_span']:.0f} kW")
print("**所以“该报多少”这个问题，答案在电价规则里，不在模型里**")

# ---------- 四、把它折成一句能写进合同的话
v["cost_per_rmse"] = (v["cost_at_rmse_best"] - v["cost_at_best"]) / max(
    v["rmse_at_best_cost"] - v["rmse_at_rmse_best"], 1e-9)
print(f"\n在这段数据上，每让出 1 kW 的均方根误差，换回约 {v['cost_per_rmse']:,.0f} 元偏差成本")
print("这句话才是调度部门要的：**预测精度的价值，要能换算成钱**")

out(**v)
