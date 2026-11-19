"""算例 25.3.1—25.3.3：窄道相遇，**等一等还是绕一绕**——两种代价给出不同的答案（25.4 节）。

资料卡里 MAPF 基准论文把两种代价分开定义：makespan 是“所有车都到位所需的时间步数”，
sum-of-costs 是“逐车到位所需时间步数之和”（也叫 flowtime）。两个定义不一样，
**最优解一般就不是同一个解**——这件事在这里算出来，不是说出来。

办法：把时间展开的联合图逐层做动态规划，把“makespan 不超过 t 时 sum-of-costs 最少是多少”
整条曲线**穷举**出来（不是采样）。曲线的两头就是两个最优解：

* sum-of-costs 最优的那头：**让一台车原地等一等**（等待只花它自己一步）；
* makespan 最优的那头：**让闲着的那台车绕一绕**（绕路对它是白送的，因为它反正早到）。

第二个实例作对照：窄道上对向相遇时，两种代价给的是**同一个答案**。
所以“该等还是该绕”这个问题，答案不在算法里，在**你报的是哪个代价**里。
"""
from _ch25 import (GRID_CORRIDOR, GRID_WORKSHOP, Grid, block_cells, find_conflicts, makespan,
                   optimal_joint, path_profile, plan_independent, sum_of_costs,
                   tradeoff_joint)
from bookout import out

v = {}

# ================================================================ 一、会分叉的实例
grid = Grid(GRID_WORKSHOP)
STARTS = [(4, 6), (3, 5)]
GOALS = [(5, 3), (9, 11)]
v["a_start"], v["a_goal"] = str(STARTS), str(GOALS)
d0, d1 = int(grid.dist(STARTS[0], GOALS[0])), int(grid.dist(STARTS[1], GOALS[1]))
v["a_dist_short"], v["a_dist_long"] = d0, d1
ind = plan_independent(grid, STARTS, GOALS)
v["a_conflicts"] = len(find_conflicts(ind))
print(f"实例甲：两台搬运车，一台只要走 {d0} 步（近），一台要走 {d1} 步（远），"
      f"在窄道口相遇——各走各的有 {v['a_conflicts']} 处冲突")
assert v["a_conflicts"] > 0

T_MAX = 20
front = tradeoff_joint(grid, STARTS, GOALS, t_max=T_MAX)
v["a_mk_opt"] = front["mk_min"]
v["a_soc_opt"] = front["soc_min"]
# 两头各取一个解，并用另一套独立实现（联合空间 A\*）交叉验一遍
p_mk = front["paths_at"](front["mk_min"])
p_soc = front["paths_at"](max(front["curve"]))
_, cost_soc, _ = optimal_joint(grid, STARTS, GOALS, metric="soc")
_, cost_mk, _ = optimal_joint(grid, STARTS, GOALS, metric="makespan")
assert cost_soc == v["a_soc_opt"] and cost_mk == v["a_mk_opt"], \
    "逐层动态规划与联合空间 A\\* 两套实现必须给出同一个最优值"
print(f"   两套独立实现交叉验过：sum-of-costs 最优 {v['a_soc_opt']} 步、"
      f"makespan 最优 {v['a_mk_opt']} 步，**都是穷举证明的**")

v["a_soc_of_mk_opt"] = sum_of_costs(p_mk)
v["a_mk_of_soc_opt"] = makespan(p_soc)
v["a_front"] = str({t: c for t, c in sorted(front["curve"].items()) if t <= v["a_mk_of_soc_opt"]})
v["a_profile_wait"] = str(path_profile(grid, p_soc, STARTS, GOALS))
v["a_profile_detour"] = str(path_profile(grid, p_mk, STARTS, GOALS))
for p in (p_mk, p_soc):
    assert not find_conflicts(p), "两头的解都必须是无冲突的"

wait_steps = sum(x[2] for x in path_profile(grid, p_soc, STARTS, GOALS))
detour_steps = sum(x[1] for x in path_profile(grid, p_mk, STARTS, GOALS))
v["a_wait_steps"] = wait_steps
v["a_detour_steps"] = detour_steps
print(f"\n   ① “等一等”（sum-of-costs 最优）：sum-of-costs {v['a_soc_opt']}、"
      f"makespan {v['a_mk_of_soc_opt']}；全程只有 {wait_steps} 步原地等待、"
      f"没有一步绕路　{v['a_profile_wait']}")
print(f"   ② “绕一绕”（makespan 最优）：sum-of-costs {v['a_soc_of_mk_opt']}、"
      f"makespan {v['a_mk_opt']}；没有一步等待，但多绕了 {detour_steps} 步"
      f"　{v['a_profile_detour']}")
print(f"   每台车的三列是 (代价, 比最短路多绕的步数, 原地等待的步数)")

v["a_soc_price_of_detour"] = v["a_soc_of_mk_opt"] - v["a_soc_opt"]
v["a_mk_price_of_wait"] = v["a_mk_of_soc_opt"] - v["a_mk_opt"]
v["a_soc_price_pct"] = (v["a_soc_of_mk_opt"] / v["a_soc_opt"] - 1) * 100
assert v["a_mk_of_soc_opt"] > v["a_mk_opt"], \
    "sum-of-costs 最优解的 makespan 必须严格更差，否则这个实例不分叉"
assert v["a_soc_of_mk_opt"] > v["a_soc_opt"], \
    "makespan 最优解的 sum-of-costs 必须严格更差，否则这个实例不分叉"
print(f"\n   **两种代价给出不同的选择**：按 sum-of-costs 该“等”，按 makespan 该“绕”。")
print(f"   买卖是：多走 {v['a_soc_price_of_detour']} 步总行程"
      f"（+{v['a_soc_price_pct']:.0f}%），换最后一台车早 {v['a_mk_price_of_wait']} 步到位")
print(f"   帕累托前沿（makespan ≤ t 时 sum-of-costs 的最小值）：{v['a_front']}"
      f"——只有两个点，中间没有别的折中")
print("   道理在定义里：sum-of-costs 是**加和**，等待只记在等的那台车头上；"
      "makespan 是**取最大**，所以让早到的那台车去绕路，对它是白送的")

# ================================================================ 二、不分叉的实例（对照）
grid2 = Grid(GRID_CORRIDOR)
S2 = [(1, 4), (7, 6)]
G2 = [(7, 4), (1, 6)]
v["b_start"], v["b_goal"] = str(S2), str(G2)
v["b_conflicts"] = len(find_conflicts(plan_independent(grid2, S2, G2)))
front2 = tradeoff_joint(grid2, S2, G2, t_max=22)
v["b_mk_opt"], v["b_soc_opt"] = front2["mk_min"], front2["soc_min"]
p2 = front2["paths_at"](front2["mk_min"])
v["b_soc_at_mk_opt"] = sum_of_costs(p2)
v["b_profile"] = str(path_profile(grid2, p2, S2, G2))
v["b_front_points"] = len(set(front2["curve"].values()))
print(f"\n实例乙（对照）：长窄道上对向相遇，各走各的有 {v['b_conflicts']} 处冲突。"
      f"穷举出来的前沿只有 {v['b_front_points']} 个值：makespan 最优 {v['b_mk_opt']}、"
      f"sum-of-costs 最优 {v['b_soc_opt']}，**同一个解同时最优**　{v['b_profile']}")
assert v["b_soc_at_mk_opt"] == v["b_soc_opt"], \
    "这个实例上两种代价不分叉——有分叉的实例要特意去找"

# 把“只许等、不许绕”的那个解也算出来（封掉旁边两条通道），好把两条路的价钱摆在一起
only_mid = Grid(block_cells(GRID_CORRIDOR, [(r, c) for r in range(2, 7) for c in (1, 9)]))
front_wait = tradeoff_joint(only_mid, S2, G2, t_max=30)
p_wait = front_wait["paths_at"](max(front_wait["curve"]))
prof_wait = path_profile(only_mid, p_wait, S2, G2)
v["b_soc_wait"], v["b_mk_wait"] = front_wait["soc_min"], makespan(p_wait)
v["b_wait_steps"] = sum(x[2] for x in prof_wait)
v["b_detour_steps"] = sum(x[1] for x in path_profile(grid2, p2, S2, G2))
print(f"   把旁路封掉、只许等：sum-of-costs {v['b_soc_wait']}、makespan "
      f"{v['b_mk_wait']}，要原地等 {v['b_wait_steps']} 步；"
      f"而绕一绕只多走 {v['b_detour_steps']} 步")
assert v["b_soc_wait"] > v["b_soc_opt"] and v["b_mk_wait"] > v["b_mk_opt"], \
    "这个实例上“等”在两种代价下都更贵，所以不分叉"
print("   **等得比绕得贵，两种代价当然就一致了**——窄道越长，等的那一方越吃亏")

# ================================================================ 三、本算例的结论
print(f"\n**所以“等还是绕”不是算法问题，是报表问题**：")
print(f"  在意“最后一车几点下线”（节拍、班次交接）就报 makespan，按它调度该绕；")
print(f"  在意“全天总行程、总电耗、总磨损”就报 sum-of-costs，按它调度该等；")
print(f"  两个数一起报，还要写明优化的是哪一个——同一套路径，"
      f"按一个口径是最优，按另一个口径就差 "
      f"{max(v['a_soc_price_pct'], v['a_mk_price_of_wait'] / v['a_mk_opt'] * 100):.0f}%。")
print("  跨论文、跨厂家的“谁家调度更好”，先看两边报的是不是同一个代价——"
      "资料卡里 SINTEF 官方自己写了一句：results are not directly comparable")

out(**v)
