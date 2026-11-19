"""算例 25.2.1—25.2.3：贪心离最优有多远，以及**“对最优的比值”与“对下界的比值”
是两件完全不同的事**（25.2、25.3 节）。

同一批车辆路径实例，三个数一起算：

* **贪心解**（最近邻 + 装不下就回仓库，调度室手上那一版）；
* **已证明最优解**：枚举全部客户次序 × 按容量的最优切分——规模小到能穷举时才有；
* **可证明下界**：每个客户两条最便宜邻边之半求和——任何规模都有，但**它很松**。

于是报表必须分成两列：“贪心 / 最优”与“贪心 / 下界”。穷举不了的规模上只有第二列，
而第二列**会随规模越来越难看**——其中有一部分并不是贪心变差了，是下界变松了。
这正是 CVRPLIB 把“上界 UB”与“是否已证明最优 Opt”分成两列的理由：
X 集一百个实例，2017 年那篇论文当年只证了 40 个的最优，今天是 61 个，
剩下 39 个手上只有会被下一篇论文改掉的“最好已知解”。
"""
import numpy as np

from _ch25 import (vrp_cost, vrp_greedy, vrp_instance, vrp_lower_bound, vrp_min_vehicles,
                   vrp_optimal)
from bookout import out

CAP = 60.0
M = 24                       # 每种规模算这么多个实例，取平均
EXACT = list(range(3, 9))    # 能穷举的规模：9 个点开始 n! 就吃不住了
BIG = [9, 12, 16, 22, 30]    # 只有下界的规模
v = {"cap": CAP, "n_instances_per_size": M,
     "exact_sizes": str(EXACT), "big_sizes": str(BIG)}
print(f"玩具车辆路径实例：一个仓库 + n 个取送点，载重 {CAP:.0f}，每种规模 {M} 个实例")
print("（坐标、需求、载重都是**显式假设**，不取自任何企业数据）")

# ---------- 一、能穷举的规模：三个数都有
rows = []
for n in EXACT:
    r_opt, r_lb, tight = [], [], []
    for s in range(M):
        inst = vrp_instance(n, seed=s * 13 + n, cap=CAP)
        greedy = vrp_cost(inst, vrp_greedy(inst))
        opt, _ = vrp_optimal(inst)
        lb = vrp_lower_bound(inst)
        assert lb <= opt + 1e-9, "下界不可能超过最优值，超了说明下界写错了"
        assert greedy >= opt - 1e-9, "贪心不可能比穷举出来的最优解更好"
        r_opt.append(greedy / opt)
        r_lb.append(greedy / lb)
        tight.append(opt / lb)
    rows.append((n, float(np.mean(r_opt)), float(np.mean(r_lb)), float(np.mean(tight)),
                 float(np.max(r_opt))))
    v[f"ratio_opt_n{n}"] = rows[-1][1]
    v[f"ratio_lb_n{n}"] = rows[-1][2]
    v[f"tight_n{n}"] = rows[-1][3]

print("\n点数   贪心/最优（已证明）   贪心/下界   最优/下界（下界有多松）   最差的那个实例")
for n, a, b, t, w in rows:
    print(f"{n:>3}        {a:6.3f}          {b:6.3f}         {t:6.3f}"
          f"              {w:6.3f}")

v["ratio_opt_small"], v["ratio_opt_large"] = rows[0][1], rows[-1][1]
v["ratio_lb_small"], v["ratio_lb_large"] = rows[0][2], rows[-1][2]
v["slope_ratio_opt"] = float(np.polyfit([r[0] for r in rows], [r[1] for r in rows], 1)[0])
v["gap_small_pct"] = (v["ratio_opt_small"] - 1) * 100
v["gap_large_pct"] = (v["ratio_opt_large"] - 1) * 100
print(f"\n贪心对**已证明最优**的差距：{v['n_instances_per_size']} 个实例平均，"
      f"{EXACT[0]} 个点时 +{v['gap_small_pct']:.1f}%，{EXACT[-1]} 个点时 "
      f"+{v['gap_large_pct']:.1f}%，拟合斜率 {v['slope_ratio_opt']:+.4f}/点")
assert all(r[1] >= 1.0 for r in rows), "贪心/最优必须不小于 1"
assert v["slope_ratio_opt"] > 0, "本算例要讲的就是“差距随规模变大”，斜率必须为正"
assert v["ratio_opt_large"] > v["ratio_opt_small"], "两头比一下也要是变大的"
print("**规模越大，贪心丢的越多**——而且这是跟穷举证明的最优解比出来的，不是跟别的启发式比")

# ---------- 二、同一批实例，换成跟下界比
assert all(r[2] >= r[1] for r in rows), \
    "下界比最优小，所以“对下界的比值”必然不小于“对最优的比值”"
v["lb_overstates_small"] = (v["ratio_lb_small"] - v["ratio_opt_small"]) * 100
v["lb_overstates_large"] = (v["ratio_lb_large"] - v["ratio_opt_large"]) * 100
print(f"\n同一批实例换成跟下界比：{EXACT[0]} 个点时 {v['ratio_lb_small']:.3f}、"
      f"{EXACT[-1]} 个点时 {v['ratio_lb_large']:.3f}——"
      f"比真实差距分别**夸大了 {v['lb_overstates_small']:.0f} 个与 "
      f"{v['lb_overstates_large']:.0f} 个百分点**")
print(f"原因在最后一列：这个下界本身就松，最优值是下界的 {rows[0][3]:.2f}—{rows[-1][3]:.2f} 倍。"
      f"**下界松，不等于解差**")

# ---------- 三、穷举不了的规模：只剩下界这一列
big_rows = []
for n in BIG:
    r_lb, veh = [], []
    for s in range(M):
        inst = vrp_instance(n, seed=s * 13 + n, cap=CAP)
        greedy_routes = vrp_greedy(inst)
        r_lb.append(vrp_cost(inst, greedy_routes) / vrp_lower_bound(inst))
        veh.append(len(greedy_routes) - vrp_min_vehicles(inst))
    big_rows.append((n, float(np.mean(r_lb)), float(np.mean(veh))))
    v[f"ratio_lb_n{n}"] = big_rows[-1][1]
    v[f"extra_vehicles_n{n}"] = big_rows[-1][2]
print("\n穷举不了的规模（**这一列没有最优解，只有下界**）：")
print("点数   贪心/下界   比装箱下界多用的车数")
for n, b, e in big_rows:
    print(f"{n:>3}      {b:6.3f}            {e:+.2f}")
v["ratio_lb_biggest"] = big_rows[-1][1]
v["slope_ratio_lb_big"] = float(np.polyfit([r[0] for r in big_rows],
                                           [r[1] for r in big_rows], 1)[0])
print(f"到 {BIG[-1]} 个点时“贪心/下界”已经 {v['ratio_lb_biggest']:.2f}，"
      f"斜率 {v['slope_ratio_lb_big']:+.4f}/点。")
print("**但不能由此说“贪心在大规模上差了两倍多”**：这里面有多少是贪心变差、"
      "有多少是下界变松，手上没有最优解就分不开。能说的只有一句："
      "“在这个下界的意义下，差距不超过这么多”")

# ---------- 四、本章的报法
print("\n所以本章的报法钉死成三条：")
print("  1. 小规模：报**已证明最优**，并说明最优是穷举出来的；")
print("  2. 大规模：报**对下界的差距**，并同时报这个下界有多松（小规模上量得出来）；")
print("  3. 任何“改进了百分之多少”，必须写明是跟最优解、跟下界，还是只跟另一个启发式比的——"
      "只跟另一个启发式比出来的百分比，本章一个不收。")

out(**v)
