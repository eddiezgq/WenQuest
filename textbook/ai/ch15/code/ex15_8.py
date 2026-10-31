"""算例 15.8.1—15.8.4：用强化学习调度车间 AGV（15.8 节的案例）。

（1）把调度写成马尔可夫决策过程：状态、动作、奖励各是什么，一天有多少次决策。
（2）两条规则基线：最近任务优先、最久等待优先。
（3）学出来的策略：在"空驶距离"与"已等时间"之间找权重，比两条规则都好在哪、差在哪。
（4）奖励写歪了会怎样：只奖励"少空驶"，学出来的调度会把远处的单一直晾着。
"""
import numpy as np

from _ch15 import AGVShop, N_STATIONS, SPEED, dist, nearest_policy, oldest_policy, weighted_policy
from bookout import out

v = {}
N_AGV, RATE, HOURS = 3, 1 / 24, 3.0
shop = AGVShop(n_agv=N_AGV, rate=RATE, horizon=HOURS * 3600, seed=1)
v["n_agv"], v["n_stations"] = N_AGV, N_STATIONS
v["orders_per_h"] = RATE * 3600
v["hours"] = HOURS
v["speed"] = SPEED
v["max_dist"] = max(dist(a, b) for a in range(N_STATIONS) for b in range(N_STATIONS))
v["max_travel_s"] = v["max_dist"] / SPEED

base = shop.run(nearest_policy)
v["n_orders"] = base["done"]
v["n_decisions"] = base["done"]                 # 每送一单就是一次"派哪台车去接哪一单"的决策

# ---------- （2）两条规则
rows = []
for name, pol in (("最近任务优先", nearest_policy), ("最久等待优先", oldest_policy)):
    r = shop.run(pol)
    rows.append((name, round(r["wait_mean"], 1), round(r["wait_p95"], 1), round(r["wait_max"], 1),
                 round(r["empty_per_job"], 1), round(r["overtime_min"], 1)))
v["rule_rows"] = rows
v["near_mean"], v["near_p95"], v["near_max"] = rows[0][1], rows[0][2], rows[0][3]
v["old_mean"], v["old_p95"] = rows[1][1], rows[1][2]
v["near_empty"], v["old_empty"] = rows[0][4], rows[1][4]
v["old_max"] = rows[1][3]
assert v["old_mean"] > 3 * v["near_mean"], "'谁等得久接谁'听着公平，实际差得远——车一直在空跑"
v["old_vs_near"] = v["old_mean"] / v["near_mean"]

# ---------- （3）学权重
# 学出来的策略就是两项打分的权重：−w_dist·空驶距离 + w_wait·已等时间。
# 用一段历史数据（这里是另外三个随机种子的订单）去选权重，再在没用过的那一天上评估——
# 这与 13.8、14.6 节"阈值要在另一批数据上选"是同一条规矩。
TRAIN_SEEDS, TEST_SEED = (11, 12, 13), 1
grid = []
for w_wait in (0.0, 0.02, 0.05, 0.1, 0.2, 0.4, 0.8):
    costs = []
    for sd in TRAIN_SEEDS:
        r = AGVShop(n_agv=N_AGV, rate=RATE, horizon=HOURS * 3600, seed=sd).run(weighted_policy(1.0, w_wait))
        costs.append(r["wait_mean"] + 0.5 * r["wait_p95"])          # 奖励：平均等待 + 一半的尾部等待
    grid.append((w_wait, round(float(np.mean(costs)), 1)))
v["grid"] = grid
v["w_best"] = float(min(grid, key=lambda x: x[1])[0])
v["cost_best"] = float(min(grid, key=lambda x: x[1])[1])
v["cost_w0"] = float([c for w, c in grid if w == 0.0][0])
assert v["w_best"] > 0, "学出来的权重不是零——纯按距离派车不是最优的"
learned = shop.run(weighted_policy(1.0, v["w_best"]), seed=TEST_SEED)
v["learn_mean"] = round(learned["wait_mean"], 1)
v["learn_p95"] = round(learned["wait_p95"], 1)
v["learn_max"] = round(learned["wait_max"], 1)
v["learn_empty"] = round(learned["empty_per_job"], 1)
v["p95_gain"] = v["near_p95"] - v["learn_p95"]
v["max_gain"] = v["near_max"] - v["learn_max"]
v["mean_cost"] = v["learn_mean"] - v["near_mean"]
assert v["learn_p95"] < v["near_p95"] and v["learn_max"] < v["near_max"], "尾部等待明显降下来"
assert v["learn_mean"] > v["near_mean"], "代价是平均等待略有上升——这就是那笔交换"
v["mean_cost_pct"] = v["mean_cost"] / v["near_mean"] * 100
v["p95_gain_pct"] = v["p95_gain"] / v["near_p95"] * 100

# ---------- （4）奖励写歪了
# 只奖励"少空驶"：等价于 w_wait = 0，也就是最近任务优先。省下的那点空驶，要用尾部等待去换。
hack = shop.run(weighted_policy(1.0, 0.0), seed=TEST_SEED)
v["hack_empty"] = round(hack["empty_per_job"], 1)
v["hack_max"] = round(hack["wait_max"], 1)
v["hack_empty_gain"] = v["learn_empty"] - v["hack_empty"]
v["hack_max_loss"] = v["hack_max"] - v["learn_max"]
assert v["hack_empty"] <= v["learn_empty"] and v["hack_max"] > v["learn_max"], \
    "只按空驶给奖励，空驶确实更省，但有单会被一直晾着"
# 一个更糟的写法：按"每小时送完多少单"给奖励，而这个量在三台车都忙得过来时根本不变
v["throughput_near"] = round(base["throughput"], 1)
v["throughput_learn"] = round(learned["throughput"], 1)
v["throughput_same"] = abs(v["throughput_near"] - v["throughput_learn"]) < 2
out(**v)
