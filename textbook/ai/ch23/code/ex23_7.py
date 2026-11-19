"""算例 23.6.2：时延预算——感知、预测、规划分完一个控制周期之后（23.6 节）。

两件事：
（1）**时延不是延迟一点点，它是把控制效果按量削掉。** 同一个规划器、同一条路，
    只把“看到的是多久以前的世界”从 0 加到几百毫秒，急刹次数、车距波动、冲击度全部恶化，
    而且系统为了活下去会自己把车距拉宽——**通行效率是悄悄被时延吃掉的**；
（2）**“把感知做准但变慢”与“稍差但快”，哪个整体更好，是可以算出来的，而且答案是中间。**
    两头都更差：太快则观测噪声大、方向盘一直在修；太慢则反应跟不上、刹车来不及。

**本算例的时延数字全部是显式假设。** 本章资料卡里查不到任何官方的“感知到执行端到端
时延预算”原始出处（能核到的那组公开测量明确排除了采集与执行两端，不是端到端），
所以这里不引用任何外部数值——下面每个毫秒数都是我们自己设的，换成你们自己量的数再算一遍。
"""
import math

import numpy as np

from _ch23 import DT, SCENE, cost_planner, follow_sim, latency_to_steps
from bookout import out

N = 4800                   # 240 s
SEED = 5
SC = dict(SCENE)
SC["t_headway"] = 1.1      # 跟得比算例 23.4 紧一点，时延才咬得到
PLAN = lambda: cost_planner(2.0, scene=SC, horizon_s=1.0)
v = {"n_steps": N, "seed": SEED, "dt_ms": DT * 1000, "t_headway": SC["t_headway"]}
print(f"控制周期 {DT * 1000:.0f} ms（{1 / DT:.0f} Hz），跟车 {N * DT:.0f} s，"
      f"期望车头时距 {SC['t_headway']:.1f} s")


def flow_vph(r: dict) -> float:
    return 3600.0 * r["v_mean"] / (r["gap_mean"] + SC["veh_len"])


# ================================================ 一、时延预算怎么分
BUDGET = {"感知": 60.0, "预测": 25.0, "规划": 20.0, "通信与执行": 15.0}   # ms，显式假设
v["budget_items"] = list(BUDGET)
v["budget_ms"] = list(BUDGET.values())
v["budget_total_ms"] = float(sum(BUDGET.values()))
v["budget_steps"] = latency_to_steps(v["budget_total_ms"])
print("\n一份时延预算（**全部是显式假设**）：")
for k, x in BUDGET.items():
    print(f"  {k:<10}{x:6.0f} ms  （占 {x / v['budget_total_ms']:.0%}）")
print(f"  合计      {v['budget_total_ms']:6.0f} ms = {v['budget_total_ms'] / (DT * 1000):.1f} "
      f"个控制周期 → 折成 {v['budget_steps']} 拍")
assert v["budget_total_ms"] > DT * 1000, "这份预算已经超出一个控制周期——本算例要算的就是这个"
print(f"**它已经超出一个控制周期**（{DT * 1000:.0f} ms）：不足一拍也要占一拍，"
      f"所以 {v['budget_total_ms']:.0f} ms 折成 {v['budget_steps']} 拍，不是 "
      f"{v['budget_total_ms'] / (DT * 1000):.1f} 拍")

# ================================================ 二、时延加上去，控制怎么退化
print("\n时延(ms)  拍  平均车距(m)  车距波动(m)  最小车距(m)  急刹  侵犯  冲击度  流量(辆/h)")
LAT_MS = [0.0, 50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 600.0, 800.0]
deg = []
for ms in LAT_MS:
    d = latency_to_steps(ms) if ms > 0 else 0
    r = follow_sim(PLAN(), n=N, seed=SEED, delay_steps=d, scene=SC)
    deg.append({"ms": ms, "d": d, "gap": r["gap_mean"], "std": r["gap_std"],
                "min": r["gap_min"], "hard": r["hard"], "viol": r["viol"],
                "jerk": r["jerk_rms"], "flow": flow_vph(r), "crash": r["crash"]})
    print(f"{ms:8.0f}{d:4d}{r['gap_mean']:13.2f}{r['gap_std']:13.2f}{r['gap_min']:13.2f}"
          f"{r['hard']:6d}{r['viol']:6d}{r['jerk_rms']:8.2f}{flow_vph(r):12.0f}")
assert all(x["crash"] == 0 for x in deg), "这组时延都不该真撞上，否则量不出退化"
for k in ("ms", "d", "gap", "std", "min", "hard", "jerk", "flow"):
    v[f"lat_{k}"] = [x[k] for x in deg]

a, b = deg[0], deg[-1]
v["hard_0ms"], v["hard_800ms"] = a["hard"], b["hard"]
v["hard_growth_x"] = b["hard"] / max(a["hard"], 1)
v["gapmin_0ms"], v["gapmin_800ms"] = a["min"], b["min"]
v["jerk_0ms"], v["jerk_800ms"] = a["jerk"], b["jerk"]
v["flow_0ms"], v["flow_800ms"] = a["flow"], b["flow"]
v["flow_loss_pct"] = (1 - b["flow"] / a["flow"]) * 100
v["gapmin_worst"] = min(x["min"] for x in deg)
v["gapmin_worst_ms"] = min(deg, key=lambda x: x["min"])["ms"]
v["gap_widen_m"] = b["gap"] - a["gap"]
print(f"\n从 0 到 {b['ms']:.0f} ms：急刹 {v['hard_0ms']} → {v['hard_800ms']} 次"
      f"（{v['hard_growth_x']:.0f} 倍），冲击度 {v['jerk_0ms']:.2f} → "
      f"{v['jerk_800ms']:.2f} m/s³")
print(f"最小车距要照实读：它不是一路下滑，而是在 {v['gapmin_worst_ms']:.0f} ms 处触底"
      f"（{v['gapmin_worst']:.2f} m），到 {b['ms']:.0f} ms 又回到 {b['min']:.2f} m——"
      f"因为规划器把平均车距拉宽了 {v['gap_widen_m']:.2f} m 来自保。"
      f"**这正是时延最难验收的地方：它可以把自己藏进“更保守”里**")
assert b["hard"] > a["hard"], "时延越大，急刹必然越多"
assert b["jerk"] > a["jerk"], "时延越大，冲击度必然越大"
print(f"流量 {v['flow_0ms']:.0f} → {v['flow_800ms']:.0f} 辆/h（降 {v['flow_loss_pct']:.1f}%）")
assert b["flow"] < a["flow"], "时延大了，系统靠拉宽车距活下来，通行效率就掉了"
print("**时延的账是这么付的**：先付在舒适与急刹上，再付在通行效率上。"
      "它不会让报表上的“成功率”变低，所以只看成功率的验收，看不见它。")

# 哪一档开始明显退化
base = a["hard"]
first_bad = next((x for x in deg if x["hard"] > 2 * max(base, 1)), None)
v["lat_knee_ms"] = first_bad["ms"] if first_bad else None
if first_bad:
    print(f"急刹次数翻倍出现在 {v['lat_knee_ms']:.0f} ms"
          f"（= {latency_to_steps(v['lat_knee_ms'])} 个控制周期）")

# ================================================ 三、更准但更慢，与稍差但更快
# 感知给的时间越长，车距观测越准：σ(t) = σ_ref·√(t_ref / t)。**这条换算是显式假设。**
SIG_REF, T_REF = 3.40, 20.0
OTHER_MS = BUDGET["预测"] + BUDGET["规划"] + BUDGET["通信与执行"]
v["sigma_ref_m"], v["t_ref_ms"], v["other_ms"] = SIG_REF, T_REF, OTHER_MS
print(f"\n感知的时间—精度换算（显式假设）：σ(t) = {SIG_REF:.2f} m × √({T_REF:.0f} ms / t)；"
      f"其余环节固定占 {OTHER_MS:.0f} ms")
print("感知耗时(ms)  σ(m)  总时延(ms)  拍  急刹  侵犯  冲击度  最小车距(m)")
T_PERC = [20.0, 30.0, 45.0, 60.0, 90.0, 130.0, 180.0, 250.0, 350.0, 500.0]
tr = []
for t in T_PERC:
    sg = SIG_REF * math.sqrt(T_REF / t)
    tot = t + OTHER_MS
    d = latency_to_steps(tot)
    r = follow_sim(PLAN(), n=N, seed=SEED, delay_steps=d, meas_sigma=sg, scene=SC)
    tr.append({"t": t, "sig": sg, "tot": tot, "d": d, "hard": r["hard"],
               "viol": r["viol"], "jerk": r["jerk_rms"], "min": r["gap_min"],
               "flow": flow_vph(r)})
    print(f"{t:12.0f}{sg:7.2f}{tot:12.0f}{d:4d}{r['hard']:6d}{r['viol']:6d}"
          f"{r['jerk_rms']:8.2f}{r['gap_min']:13.2f}")
for k in ("t", "sig", "tot", "d", "hard", "jerk", "min", "flow"):
    v[f"tr_{k}"] = [x[k] for x in tr]

best = min(tr, key=lambda x: x["hard"])
fastest, slowest = tr[0], tr[-1]
v["t_best_ms"], v["sig_best"], v["hard_best"] = best["t"], best["sig"], best["hard"]
v["hard_fastest"], v["sig_fastest"] = fastest["hard"], fastest["sig"]
v["hard_slowest"], v["sig_slowest"] = slowest["hard"], slowest["sig"]
print(f"\n急刹次数最少的一档：感知给 {v['t_best_ms']:.0f} ms（σ = {v['sig_best']:.2f} m），"
      f"急刹 {v['hard_best']} 次")
print(f"最快那一档（{fastest['t']:.0f} ms，σ = {v['sig_fastest']:.2f} m）："
      f"急刹 {v['hard_fastest']} 次")
print(f"最慢也最准那一档（{slowest['t']:.0f} ms，σ = {v['sig_slowest']:.2f} m）："
      f"急刹 {v['hard_slowest']} 次")
assert v["t_best_ms"] != fastest["t"] and v["t_best_ms"] != slowest["t"], \
    "最优点必须在中间——两头都更差，这才叫取舍"

v["slower_more_accurate_worse_pct"] = (v["hard_slowest"] / v["hard_best"] - 1) * 100
v["sig_improve_x"] = v["sig_best"] / v["sig_slowest"]
assert v["hard_slowest"] > v["hard_best"], \
    "存在这样一个点：更准但更慢，整体反而更差——这是本算例要钉住的结论"
print(f"**存在这样一个点**：从 {v['t_best_ms']:.0f} ms 再加到 {slowest['t']:.0f} ms，"
      f"观测精度提高了 {v['sig_improve_x']:.1f} 倍（σ {v['sig_best']:.2f} → "
      f"{v['sig_slowest']:.2f} m），急刹次数反而多了 "
      f"{v['slower_more_accurate_worse_pct']:.0f}%")
print("所以“感知再做准一点”这件事，必须连它要花多少毫秒一起报。"
      "**只报精度的感知指标，不能作为上车的依据。**")

# 两头各自坏在哪儿：噪声坏在冲击度，时延坏在最小车距
v["jerk_fastest"], v["jerk_slowest"] = fastest["jerk"], slowest["jerk"]
v["min_fastest"], v["min_slowest"] = fastest["min"], slowest["min"]
print(f"\n两头坏的不是同一件事：最快那头冲击度 {v['jerk_fastest']:.1f} m/s³"
      f"（最慢那头只有 {v['jerk_slowest']:.1f}），"
      f"最慢那头最小车距 {v['min_slowest']:.2f} m（最快那头还有 {v['min_fastest']:.2f}）")
assert v["jerk_fastest"] > v["jerk_slowest"], "噪声大的那头，方向盘/油门一直在修"
assert v["min_slowest"] < v["min_fastest"], "时延大的那头，车距被压得更低"
print("**噪声的账记在舒适上，时延的账记在安全余量上**——两笔账不能合成一个分数去调参，"
      "要分开报，再由人决定哪一笔付得起")

print("\n这个算例回答不了什么：真系统的时延不是常数，它是一条有长尾的分布"
      "（99 分位比均值大得多），而退化多半由尾部造成，本算例用的是固定时延；"
      "感知的时间—精度换算也不是一条平方根曲线，真实的曲线要自己测；"
      "本算例只有纵向跟车，横向控制对时延更敏感。**这些毫秒数一个都不要照抄。**")

out(**v)
