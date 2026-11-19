"""算例 25.6.1—25.6.3：无人机厂区巡检与盘库的航迹——**启发式、最优解、下界三个数一起报**（25.1、25.6 节）。

题目：厂区里若干个巡检点（库位、料场、屋面、围墙），无人机从起降点出发，
每点悬停一会儿拍照盘库，电量不够就回去换电再飞下一趟。要排的是航线。

三个数：

* **启发式**：最近邻 + 电量不够就回去换电（现场最常见的排法）；
* **已证明最优**：巡检点少到能穷举时，枚举全部次序 × 按电量的最优切分；
* **可证明下界**：每个点两条最便宜邻边之半求和——它与电量无关，所以**对加了电量约束的
  问题同样是下界**（约束只会把解推坏）。

另外一条本章口径（c）：**续航与载重只引官方规格书的标称值，并且写明标称条件**。
这里的计算**一个厂家标称值都没用**，用的是本书自己设的工况参数（见 `_ch25.DRONE_ASSUMED`）。
为什么不能直接拿标称值来算，程序开头把标称条件打出来就明白了。
"""
import numpy as np
from logi_facts import DRONE_M4, DRONE_M350

from _ch25 import (DRONE_ASSUMED, inspect_greedy, inspect_instance, inspect_length,
                   inspect_lower_bound, inspect_mission_time, inspect_optimal)
from bookout import T, out

cfg = DRONE_ASSUMED
SEEDS = range(8)
N_SMALL = 8                 # 能穷举的规模（8! 个次序）
N_BIG = 14                  # 只有下界的规模
v = {"n_small": N_SMALL, "n_big": N_BIG, "n_seeds": len(list(SEEDS)),
     "cruise_ms": cfg["cruise_ms"], "endurance_s": cfg["endurance_s"],
     "hover_s": cfg["hover_s"], "swap_s": cfg["swap_s"]}

print("本算例用的工况参数全部是**本书的显式假设**：")
print(f"  巡航 {cfg['cruise_ms']:.0f} m/s，一块电池可用 {cfg['endurance_s'] / 60:.0f} 分钟"
      f"（已扣掉返航与安全余量），每点悬停 {cfg['hover_s']:.0f} s，换电 "
      f"{cfg['swap_s'] / 60:.0f} 分钟")
print("厂家标称值只在正文作对照，**不进任何计算**，因为标称条件根本不是巡检工况：")
print(f"  {DRONE_M350['model']}：最长飞行时间 {DRONE_M350['max_flight_time_min']} 分钟，"
      f"标称条件是“{DRONE_M350['flight_time_conditions']}”")
print(f"  {DRONE_M4['model']}：最长飞行时间 "
      f"{DRONE_M4['max_flight_time_min']['standard']} 分钟（标准桨），标称条件是"
      f"“{DRONE_M4['flight_time_conditions']}”；整机载重 {DRONE_M4['max_payload_g']} g")
print(f"  而 {DRONE_M350['model']} 的**整机最大载重官方没给**，"
      f"资料卡里就记成空值——不许用最大起飞重量减空重自己算")
v["m350_flight_min"] = DRONE_M350["max_flight_time_min"]
v["m350_flight_cond"] = T(DRONE_M350["flight_time_conditions"],
                          "about 8 m/s level flight, no payload, no wind, discharged to 0%")
v["m4_flight_min"] = DRONE_M4["max_flight_time_min"]["standard"]
v["m4_flight_cond"] = T(DRONE_M4["flight_time_conditions"],
                        "about 9 m/s level flight, no payload, no wind, discharged to 0%")
v["m4_payload_g"] = DRONE_M4["max_payload_g"]
assert DRONE_M350["max_payload_g"] is None, "口径（c）：官方没给的，程序里也不能有"
assert DRONE_M350["flight_time_conditions"] and DRONE_M4["flight_time_conditions"], \
    "续航印出来就必须带标称条件"

# ================================================================ 一、能穷举的规模
rows = []
for s in SEEDS:
    inst = inspect_instance(N_SMALL, seed=s)
    lb = inspect_lower_bound(inst)
    free_greedy = inspect_length(inst, inspect_greedy(inst, cfg, battery=False))
    free_opt, _ = inspect_optimal(inst, cfg, battery=False)
    batt_trips_g = inspect_greedy(inst, cfg, battery=True)
    batt_greedy = inspect_length(inst, batt_trips_g)
    batt_opt, batt_trips = inspect_optimal(inst, cfg, battery=True)
    assert lb <= free_opt + 1e-6, "下界不可能超过不带电量约束的最优值"
    assert lb <= batt_opt + 1e-6, "同一个下界对带电量约束的问题也成立"
    assert free_opt <= batt_opt + 1e-6, "加约束只会让最优值变大，不会变小"
    assert free_greedy >= free_opt - 1e-6 and batt_greedy >= batt_opt - 1e-6, \
        "启发式不可能比穷举出来的最优解更好"
    rows.append({"seed": s, "lb": lb, "free_greedy": free_greedy, "free_opt": free_opt,
                 "batt_greedy": batt_greedy, "batt_opt": batt_opt,
                 "trips_greedy": len(batt_trips_g), "trips_opt": len(batt_trips),
                 "mission_min": inspect_mission_time(inst, batt_trips, cfg) / 60})

print(f"\n① {N_SMALL} 个巡检点（{v['n_seeds']} 个实例，航程单位米）：")
print("实例   下界    不带电量约束：启发式/最优    带电量约束：启发式/最优   趟数 启发/最优  任务总时长")
for r in rows:
    print(f" {r['seed']}   {r['lb']:6.0f}      {r['free_greedy']:6.0f} / {r['free_opt']:6.0f}"
          f"            {r['batt_greedy']:6.0f} / {r['batt_opt']:6.0f}"
          f"          {r['trips_greedy']} / {r['trips_opt']}      "
          f"{r['mission_min']:5.1f} 分钟")


def mean(key):
    return float(np.mean([r[key] for r in rows]))


v["lb_mean"] = mean("lb")
v["free_opt_mean"], v["free_greedy_mean"] = mean("free_opt"), mean("free_greedy")
v["batt_opt_mean"], v["batt_greedy_mean"] = mean("batt_opt"), mean("batt_greedy")
v["trips_opt_mean"], v["trips_greedy_mean"] = mean("trips_opt"), mean("trips_greedy")
v["mission_min_mean"] = mean("mission_min")
v["greedy_gap_free_pct"] = (v["free_greedy_mean"] / v["free_opt_mean"] - 1) * 100
v["greedy_gap_batt_pct"] = (v["batt_greedy_mean"] / v["batt_opt_mean"] - 1) * 100
v["lb_slack_pct"] = (v["free_opt_mean"] / v["lb_mean"] - 1) * 100
v["batt_price_pct"] = (v["batt_opt_mean"] / v["free_opt_mean"] - 1) * 100
v["greedy_vs_lb_batt_pct"] = (v["batt_greedy_mean"] / v["lb_mean"] - 1) * 100

print(f"\n   启发式离**已证明最优**：不带电量约束 +{v['greedy_gap_free_pct']:.1f}%，"
      f"带电量约束 +{v['greedy_gap_batt_pct']:.1f}%")
print(f"   同一个启发式离**下界**：+{v['greedy_vs_lb_batt_pct']:.1f}%"
      f"——差了 {v['greedy_vs_lb_batt_pct'] - v['greedy_gap_batt_pct']:.0f} 个百分点，"
      f"因为这个下界本身就松（最优值是下界的 "
      f"{v['free_opt_mean'] / v['lb_mean']:.2f} 倍）")
assert v["greedy_gap_batt_pct"] >= 0 and v["greedy_vs_lb_batt_pct"] >= v["greedy_gap_batt_pct"], \
    "对下界的差距必然不小于对最优的差距"
print(f"   **电量约束把最优解推坏了 {v['batt_price_pct']:.1f}%**："
      f"同样的点，一趟飞不完就要多回来一次，多出来的全是往返腿"
      f"（平均 {v['trips_opt_mean']:.2f} 趟）")
assert v["batt_price_pct"] > 5.0, \
    "本算例要讲的就是电量约束的代价，这个工况下它必须明显"
n_worse = sum(1 for r in rows if r["batt_opt"] > r["free_opt"] + 1e-6)
v["n_instances_worse"] = n_worse
print(f"   {v['n_seeds']} 个实例里有 {n_worse} 个被电量约束推坏了"
      f"（这个工况下 {N_SMALL} 个点一趟飞不完，所以每个实例都得分两趟）")
print(f"   算上换电（每次 {cfg['swap_s'] / 60:.0f} 分钟），整轮巡检要 "
      f"{v['mission_min_mean']:.1f} 分钟——**排班要用的是这个数，不是航程**")

# ================================================================ 二、穷举不了的规模
big = []
for s in SEEDS:
    inst = inspect_instance(N_BIG, seed=100 + s)
    lb = inspect_lower_bound(inst)
    trips_free = inspect_greedy(inst, cfg, battery=False)
    trips_batt = inspect_greedy(inst, cfg, battery=True)
    big.append({"lb": lb, "free": inspect_length(inst, trips_free),
                "batt": inspect_length(inst, trips_batt),
                "trips": len(trips_batt),
                "mission_min": inspect_mission_time(inst, trips_batt, cfg) / 60})
v["big_lb_mean"] = float(np.mean([r["lb"] for r in big]))
v["big_free_mean"] = float(np.mean([r["free"] for r in big]))
v["big_batt_mean"] = float(np.mean([r["batt"] for r in big]))
v["big_trips_mean"] = float(np.mean([r["trips"] for r in big]))
v["big_mission_min_mean"] = float(np.mean([r["mission_min"] for r in big]))
v["big_greedy_vs_lb_pct"] = (v["big_batt_mean"] / v["big_lb_mean"] - 1) * 100
v["big_batt_price_pct"] = (v["big_batt_mean"] / v["big_free_mean"] - 1) * 100
print(f"\n② {N_BIG} 个巡检点（**穷举不了，手上只有下界**）：")
print(f"   下界 {v['big_lb_mean']:.0f} m；启发式不带电量约束 {v['big_free_mean']:.0f} m、"
      f"带电量约束 {v['big_batt_mean']:.0f} m（{v['big_trips_mean']:.2f} 趟，"
      f"{v['big_mission_min_mean']:.1f} 分钟）")
print(f"   能说的只有一句：**在这个下界的意义下，启发式最多差 "
      f"{v['big_greedy_vs_lb_pct']:.0f}%**。至于其中有多少是启发式的毛病、"
      f"多少是下界的松，这个规模上分不开——{N_SMALL} 个点时量到的松是 "
      f"{v['lb_slack_pct']:.0f}%")
print(f"   电量约束在这个规模上的代价是 +{v['big_batt_price_pct']:.1f}%"
      f"（跟同一个启发式不带约束的解比，**这是启发式对启发式，不是对最优**）")

# ================================================================ 三、结论
print("\n本算例的三条：")
print(f"  1. 报航线成绩要三个数：启发式、（能算就算的）已证明最优、下界。"
      f"少了最优那一列，“+{v['greedy_vs_lb_batt_pct']:.0f}%”这个数会被当成启发式的毛病，"
      f"其实大部分是下界松；")
print(f"  2. **电量是把解推坏的硬约束**，不是一句“续航 xx 分钟”就能带过去的："
      f"同样的巡检点，带约束的最优比不带约束的最优长 {v['batt_price_pct']:.1f}%，"
      f"而排班要看的是算上换电的 {v['mission_min_mean']:.1f} 分钟；")
print(f"  3. 厂家标称的续航（如 {v['m350_flight_min']} 分钟）**不能当工况用**："
      f"它的标称条件是“{v['m350_flight_cond']}”——无载重、无风、放到 0%，"
      f"而巡检要挂载、要悬停、要留返航余量。本算例用的 "
      f"{cfg['endurance_s'] / 60:.0f} 分钟是显式假设，照你们自己实测的来改。")

out(**v)
