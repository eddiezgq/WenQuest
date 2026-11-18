"""算例 22.5.1—22.5.3：学出来的策略、规则策略，以及安全层（22.3、22.5 节）。

本算例把强化学习那一套在工业控制里最要紧的三件事算出来：

（1）**只报收益不报越界次数的结果不能信**：在仿真里调出来的策略，收益更高，
    但它是靠蹭着约束边界拿到的；
（2）**仿真到现实有差距**：仿真里电池效率与容量都是标称值，真设备不是。
    在仿真里调到最好的参数，拿到真设备上会掉多少？
（3）**安全层值多少钱**：外面套一层"把动作投影到可行范围"的逻辑，
    损失多少收益、避免多少次越界。

策略本身故意取得极简（四个参数的阈值策略），因为本节要讲的是**验收方式**，不是算法。
"""
import numpy as np

from _ch22 import (BATTERY, STEPS_PER_DAY, dispatch_cost, load_series, pv_series,
                   safe_layer, tou_price)
from bookout import out

N_DAYS = 12
v = {"n_days": N_DAYS}

pv = pv_series(N_DAYS, seed=3)
load = load_series(N_DAYS, seed=3)
price = tou_price(N_DAYS)

# 真设备与标称值的差别：效率低一点、可用容量小一点（**这就是仿真到现实的差距**）
REAL = dict(BATTERY)
REAL["eta"] = BATTERY["eta"] - 0.06
REAL["cap_kwh"] = BATTERY["cap_kwh"] * 0.92
v["eta_nominal"], v["eta_real"] = BATTERY["eta"], REAL["eta"]
v["cap_nominal"], v["cap_real"] = BATTERY["cap_kwh"], REAL["cap_kwh"]


def policy(params, bat):
    """四个参数的阈值策略：低价充、高价放、余电存、留多少余量。"""
    p_lo, p_hi, charge_frac, keep = params
    out_c = np.zeros(len(pv))
    for i in range(len(pv)):
        surplus = pv[i] - load[i]
        if surplus > 0:
            out_c[i] = min(surplus, bat["p_max_kw"]) * charge_frac
        elif price[i] <= p_lo:
            out_c[i] = bat["p_max_kw"] * charge_frac
        elif price[i] >= p_hi:
            out_c[i] = -bat["p_max_kw"] * (1.0 - keep)
    return out_c


MARGIN = 0.05                      # 安全层额外留的余量（占总容量），显式假设
v["margin"] = MARGIN


def evaluate(params, bat, use_safe):
    plan = policy(params, bat)
    if use_safe:
        plan = safe_layer(plan, pv, load, bat, margin=MARGIN)
    cost, _, viol = dispatch_cost(pv, load, price, plan, bat)
    return cost, viol


BASE = (0.35, 0.95, 0.8, 0.2)
v["cost_rule"], v["viol_rule"] = evaluate(BASE, REAL, False)
print(f"手写规则（没调过）：电费 {v['cost_rule']:,.0f} 元，越界 {v['viol_rule']} 次")

# ---------- 一、在仿真里调参数（标称电池），只盯收益
g = np.random.default_rng(0)
best, best_cost = BASE, 1e18
for _ in range(1500):
    cand = (float(g.uniform(0.25, 0.7)), float(g.uniform(0.7, 1.1)),
            float(g.uniform(0.2, 1.0)), float(g.uniform(0.0, 0.8)))
    c, _ = evaluate(cand, BATTERY, False)        # **只看电费，不看越界**
    if c < best_cost:
        best, best_cost = cand, c
v["cost_sim_tuned_sim"] = best_cost
_, v["viol_sim_tuned_sim"] = evaluate(best, BATTERY, False)
print(f"在仿真里调到最好：仿真电费 {best_cost:,.0f} 元，"
      f"仿真里越界 {v['viol_sim_tuned_sim']} 次")

# ---------- 二、拿到真设备上
v["cost_sim_tuned_real"], v["viol_sim_tuned_real"] = evaluate(best, REAL, False)
v["sim2real_gap_pct"] = (v["cost_sim_tuned_real"] / v["cost_sim_tuned_sim"] - 1) * 100
print(f"同一组参数、真设备：电费 {v['cost_sim_tuned_real']:,.0f} 元"
      f"（比仿真里贵 {v['sim2real_gap_pct']:.1f}%），越界 {v['viol_sim_tuned_real']} 次")
assert v["cost_sim_tuned_real"] > v["cost_sim_tuned_sim"], \
    "真设备效率低、容量小，成本必然比仿真里高"
print("**这就是仿真到现实的差距**：仿真里调出来的参数，真设备上既没那么省，"
      "还可能更频繁地蹭到约束边界")

# ---------- 三、加安全层
v["cost_safe"], v["viol_safe"] = evaluate(best, REAL, True)
v["safe_cost_pct"] = (v["cost_safe"] / v["cost_sim_tuned_real"] - 1) * 100
v["viol_avoided"] = v["viol_sim_tuned_real"] - v["viol_safe"]
print(f"\n外面套一层安全层（额外留 {MARGIN:.0%} 余量）：电费 {v['cost_safe']:,.0f} 元"
      f"（{v['safe_cost_pct']:+.2f}%），越界 {v['viol_safe']} 次"
      f"（少了 {v['viol_avoided']} 次）")
assert v["viol_safe"] == 0, "安全层的职责就是把越界清零"
assert v["cost_safe"] > v["cost_sim_tuned_real"], "留余量要花钱，这笔钱就是安全层的价钱"
print(f"**安全层的价钱是 {v['safe_cost_pct']:.2f}% 的电费，买回来的是 "
      f"{v['viol_avoided']} 次越界变成 0 次**")
print("要留余量，是因为真设备的效率与可用容量都与标称值不一样：只按标称值投影，"
      "等于把余量全交给电池管理系统去兜——那每一次都是报警、是寿命损耗，不是免费的")

# ---------- 四、把越界计入目标，再调一次
best2, best2_cost = BASE, 1e18
PENALTY = 20.0                     # 每次越界罚 20 元（显式假设，照你们自己的损失填）
for _ in range(1500):
    cand = (float(g.uniform(0.25, 0.7)), float(g.uniform(0.7, 1.1)),
            float(g.uniform(0.2, 1.0)), float(g.uniform(0.0, 0.8)))
    c, viol = evaluate(cand, BATTERY, False)
    score = c + PENALTY * viol
    if score < best2_cost:
        best2, best2_cost = cand, score
v["penalty"] = PENALTY
v["cost_pen_tuned_real"], v["viol_pen_tuned_real"] = evaluate(best2, REAL, True)
v["pen_vs_plain_pct"] = (v["cost_pen_tuned_real"] / v["cost_safe"] - 1) * 100
print(f"\n把越界按每次 {PENALTY:.0f} 元计入目标再调，然后加安全层上真设备："
      f"电费 {v['cost_pen_tuned_real']:,.0f} 元（{v['pen_vs_plain_pct']:+.2f}%），"
      f"越界 {v['viol_pen_tuned_real']} 次")
print("两件事一起做才稳妥：**目标函数里写进约束的代价**（它改变策略的性格），"
      "**外面再套一层安全层**（它兜住剩下的）")

# ---------- 五、把仿真到现实那一段差距单独量出来
# 假装我们能直接在真设备参数上调（现实里做不到，这里只为给上面那几个数一把尺子）
best3, best3_cost = BASE, 1e18
for _ in range(1500):
    cand = (float(g.uniform(0.25, 0.7)), float(g.uniform(0.7, 1.1)),
            float(g.uniform(0.2, 1.0)), float(g.uniform(0.0, 0.8)))
    c, viol = evaluate(cand, REAL, True)
    score = c + PENALTY * viol
    if score < best3_cost:
        best3, best3_cost = cand, score
v["cost_real_tuned"], v["viol_real_tuned"] = evaluate(best3, REAL, True)
v["sim_tuning_waste_pct"] = (v["cost_pen_tuned_real"] / v["cost_real_tuned"] - 1) * 100
print(f"\n直接按真设备参数调（现实里做不到，只作尺子）：电费 "
      f"{v['cost_real_tuned']:,.0f} 元，越界 {v['viol_real_tuned']} 次")
print(f"**在仿真里调出来的那一版，比这把尺子贵 {v['sim_tuning_waste_pct']:.1f}%**——"
      f"这就是仿真到现实那一段差距吃掉的收益")

# ---------- 六、报表应该长什么样
v["cost_vs_rule_pct"] = (1 - v["cost_pen_tuned_real"] / v["cost_rule"]) * 100
v["real_vs_rule_pct"] = (1 - v["cost_real_tuned"] / v["cost_rule"]) * 100
print(f"\n三行并排才看得清：")
print(f"  手写规则（没调过）　　　　：电费 {v['cost_rule']:,.0f} 元，越界 {v['viol_rule']} 次")
print(f"  仿真里调好 + 安全层　　　：电费 {v['cost_pen_tuned_real']:,.0f} 元"
      f"（{v['cost_vs_rule_pct']:+.1f}%），越界 {v['viol_pen_tuned_real']} 次")
print(f"  按真设备调好 + 安全层　　：电费 {v['cost_real_tuned']:,.0f} 元"
      f"（{v['real_vs_rule_pct']:+.1f}%），越界 {v['viol_real_tuned']} 次")
print(f"**这一组数要照实读**：在这套参数下，仿真里调一千五百次、再拿到真设备上，"
      f"电费并没有比没调过的手写规则更省（{v['cost_vs_rule_pct']:+.1f}%）；"
      f"真正的收益是**越界从 {v['viol_rule']} 次变成 0 次**。"
      f"所以报表必须两列并排——只报电费，这件事看起来白做；只报越界，又看不出代价。"
      f"而那把尺子（按真设备调）告诉我们：这中间有 {v['sim_tuning_waste_pct']:.1f}% "
      f"是被仿真到现实的差距吃掉的，想拿回来，得先把仿真的参数标定准")

out(**v)
