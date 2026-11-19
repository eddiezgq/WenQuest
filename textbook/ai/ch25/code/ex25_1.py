"""算例 25.1.1—25.1.4：A\\* 与冲突搜索，**对着穷举证明的最优解**量（25.4 节）。

四台搬运车在同一座车间里跑，三种做法摆在一起比：

（1）**各车各规划各的**（独立 A\\*）：代价最低，但它不是一个解——车会撞；
（2）**优先级法**：可行、快，但不最优，而且顺序一换结果就变；
（3）**冲突搜索**：论文定理 1 说它返回最优解，这里用穷举把这句话**验一遍**。

本章的硬规矩在这里第一次用上：**这里的"最优"不是"最好已知解"，是在联合状态空间里
穷举出来的已证明最优**（CVRPLIB 把"上界"与"是否已证明最优"分成两列，说的就是这个区别）。
另外还有一个免费的**下界**：各车单独的最短步数之和——任何可行解都不可能比它更省，
最优解超出它多少，就是"协调"这件事本身的代价。
"""
import itertools

from _ch25 import (GRID_WORKSHOP, Grid, cbs, find_conflicts, makespan, optimal_joint,
                   path_profile, plan_independent, plan_prioritized, sum_of_costs, trim)
from bookout import out

grid = Grid(GRID_WORKSHOP)
STARTS = [(7, 5), (3, 1), (4, 6), (2, 11)]
GOALS = [(4, 9), (8, 1), (6, 9), (6, 10)]
v = {"n_agv": len(STARTS), "grid_rows": grid.h, "grid_cols": grid.w,
     "grid_free": len(grid.free)}
print(f"车间网格 {grid.h}×{grid.w}，可走格子 {len(grid.free)} 个，"
      f"窄道只有两个口；{len(STARTS)} 台搬运车同时要过")

# ---------- 零、免费的下界：各车单独的最短步数之和
v["lb_sum_shortest"] = int(sum(grid.dist(s, g) for s, g in zip(STARTS, GOALS)))
print(f"\n下界（各车单独最短步数之和）：sum-of-costs ≥ {v['lb_sum_shortest']} 步"
      f"——这是**可证明的下界**，不是解")

# ---------- 一、各车各规划各的
ind = plan_independent(grid, STARTS, GOALS)
conf = find_conflicts(ind)
v["soc_independent"] = sum_of_costs(ind)
v["mk_independent"] = makespan(ind)
v["conflicts_independent"] = len(conf)
v["conflicts_vertex"] = sum(1 for c in conf if c[0] == "vertex")
v["conflicts_edge"] = sum(1 for c in conf if c[0] == "edge")
print(f"\n① 独立 A\\*：sum-of-costs {v['soc_independent']} 步、makespan "
      f"{v['mk_independent']} 步，**但有 {v['conflicts_independent']} 处冲突**"
      f"（点冲突 {v['conflicts_vertex']} 处、换位冲突 {v['conflicts_edge']} 处）")
assert v["conflicts_independent"] > 0, "这个实例要的就是“各走各的一定撞”"
assert v["soc_independent"] == v["lb_sum_shortest"], \
    "独立 A\\* 的代价正好等于那个下界——它便宜是因为它不可行"
print("   它的代价正好等于下界：**便宜是因为它不是解**。报“比独立规划多花了多少”，"
      "等于报“协调要花多少”")

# ---------- 二、穷举出真正的最优（本算例的真值）
opt_paths, opt_cost, expanded = optimal_joint(grid, STARTS, GOALS, metric="soc")
v["soc_optimal"] = opt_cost
v["mk_optimal_of_soc"] = makespan(opt_paths)
v["joint_states_expanded"] = expanded
assert sum_of_costs(opt_paths) == opt_cost
assert not find_conflicts(opt_paths), "最优解必须是无冲突的"
v["coord_price"] = v["soc_optimal"] - v["lb_sum_shortest"]
print(f"\n② 联合状态空间穷举（A\\*，启发函数可采纳）：sum-of-costs 最优 = "
      f"{v['soc_optimal']} 步，展开了 {expanded} 个联合状态")
print(f"   **这个数是穷举证明的最优**，不是“最好已知解”。协调的代价 = "
      f"{v['coord_price']} 步（比下界多 {v['coord_price'] / v['lb_sum_shortest'] * 100:.1f}%）")

# ---------- 三、优先级法：可行，但不最优，而且看顺序
pri = trim(plan_prioritized(grid, STARTS, GOALS))
v["soc_prioritized"] = sum_of_costs(pri)
v["mk_prioritized"] = makespan(pri)
v["conflicts_prioritized"] = len(find_conflicts(pri))
v["prio_gap_pct"] = (v["soc_prioritized"] / v["soc_optimal"] - 1) * 100
print(f"\n③ 优先级法（按车号 0,1,2,3）：sum-of-costs {v['soc_prioritized']} 步、"
      f"冲突 {v['conflicts_prioritized']} 处，**比最优贵 {v['prio_gap_pct']:.1f}%**")
assert v["conflicts_prioritized"] == 0, "优先级法应当给出可行解"
assert v["soc_prioritized"] >= v["soc_optimal"], "可行解不可能比最优解更省"

orders = []
for order in itertools.permutations(range(len(STARTS))):
    p = plan_prioritized(grid, STARTS, GOALS, order=list(order))
    if p:
        orders.append((sum_of_costs(trim(p)), order))
orders.sort()
v["prio_best"], v["prio_worst"] = orders[0][0], orders[-1][0]
v["prio_best_order"] = "".join(str(i) for i in orders[0][1])
v["prio_worst_order"] = "".join(str(i) for i in orders[-1][1])
v["prio_n_orders"] = len(orders)
v["prio_spread_pct"] = (v["prio_worst"] / v["prio_best"] - 1) * 100
v["prio_best_gap_pct"] = (v["prio_best"] / v["soc_optimal"] - 1) * 100
print(f"   把 {v['prio_n_orders']} 种优先级顺序全试一遍：最好 {v['prio_best']} 步"
      f"（顺序 {v['prio_best_order']}）、最差 {v['prio_worst']} 步"
      f"（顺序 {v['prio_worst_order']}），**同一个算法差 {v['prio_spread_pct']:.1f}%**")
print(f"   连最好的那个顺序都比最优贵 {v['prio_best_gap_pct']:.1f}%——"
      f"所以优先级法的毛病**不只是顺序没挑好**：顺序全试一遍也到不了最优，"
      f"因为它从不回头改已经规划好的那几台车")
assert v["prio_best"] >= v["soc_optimal"]

# ---------- 四、冲突搜索：把“定理 1”验一遍
cbs_paths, cbs_nodes = cbs(grid, STARTS, GOALS)
assert cbs_paths is not None, "这个实例有解，冲突搜索应当找到"
cbs_paths = trim(cbs_paths)
v["soc_cbs"] = sum_of_costs(cbs_paths)
v["mk_cbs"] = makespan(cbs_paths)
v["cbs_nodes"] = cbs_nodes
v["conflicts_cbs"] = len(find_conflicts(cbs_paths))
print(f"\n④ 冲突搜索：sum-of-costs {v['soc_cbs']} 步、冲突 {v['conflicts_cbs']} 处，"
      f"高层只展开了 {v['cbs_nodes']} 个冲突树节点")
assert v["conflicts_cbs"] == 0, "冲突搜索给出的解必须无冲突"
assert v["soc_cbs"] == v["soc_optimal"], \
    "冲突搜索论文定理 1：返回最优解。这里用穷举验到了同一个值"
print("   **与穷举的最优值一模一样**——论文 §5.1 定理 1 的原话是 “CBS returns an "
      "optimal solution.”，这一句在这个实例上验到了")
print("   要注意论文里**没有** “CBS is complete and optimal” 这句：定理 1 只管最优性，"
      "而“有解必能找到”与“无解能判出来”是两半，后一半在冲突搜索上不总成立"
      "（无解时冲突树可以无限增长），所以程序里要给冲突树加节点上限")

# ---------- 五、四种做法的报表（按本章口径，成绩必须连“失败的那一列”一起报）
v["profile_optimal"] = str(path_profile(grid, opt_paths, STARTS, GOALS))
v["profile_prioritized"] = str(path_profile(grid, pri, STARTS, GOALS))
print("\n五列并排才算报表（代价 / makespan / 冲突 / 是不是可行解 / 跟谁比的）：")
rows = [("独立 A\\*（各走各的）", v["soc_independent"], v["mk_independent"],
         v["conflicts_independent"], "不可行", "= 下界"),
        ("优先级法（按车号）", v["soc_prioritized"], v["mk_prioritized"],
         v["conflicts_prioritized"], "可行", f"+{v['prio_gap_pct']:.1f}% 对最优"),
        ("优先级法（最好的顺序）", v["prio_best"], "—", 0, "可行",
         f"+{v['prio_best_gap_pct']:.1f}% 对最优"),
        ("冲突搜索", v["soc_cbs"], v["mk_cbs"], v["conflicts_cbs"], "可行", "= 最优"),
        ("穷举（真值）", v["soc_optimal"], v["mk_optimal_of_soc"], 0, "可行",
         "**已证明最优**")]
for name, soc, mk, cf, ok, cmp_ in rows:
    print(f"  {name:<22}  sum-of-costs {soc:>3}  makespan {str(mk):>3}  "
          f"冲突 {cf:>2}  {ok}  {cmp_}")
print(f"每台车的 (代价, 多绕的步数, 原地等待的步数)：最优解 {v['profile_optimal']}，"
      f"优先级法 {v['profile_prioritized']}")
print("最后一行是本章的规矩：**这个实例的最优值是穷举证明的**。规模再大一点就穷举不了，"
      "那时只能拿下界说话，而“上界”与“已证明最优”必须分成两列报——"
      "CVRPLIB 的表头就是这么分的")

out(**v)
