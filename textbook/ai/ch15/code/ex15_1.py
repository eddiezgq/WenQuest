"""算例 15.1.1—15.1.4：把一件事写成马尔可夫决策过程，再把价值算出来（15.1 节）。

（1）小车间的网格：状态、动作、转移、奖励各是什么，一共多少个状态。
（2）价值迭代：贝尔曼最优方程反复迭代，收敛要几轮，误差怎样按折扣因子的幂往下掉。
（3）策略迭代：另一条路——评估、改进、再评估，与价值迭代给出同一个答案。
（4）折扣因子管什么：γ 小只顾眼前，γ 大愿意绕远路去拿大奖励。
"""
import numpy as np

from _ch15 import ACTION_NAMES, policy_iteration, shop_mdp, value_iteration
from bookout import out

v = {}
P, R, idx, g, start, goal = shop_mdp()
H, W = g.shape
v["rows"], v["cols"] = int(H), int(W)
v["n_states"] = len(idx)
v["n_walls"] = int((g == "#").sum())
v["n_actions"] = len(ACTION_NAMES)
v["n_transitions"] = int((P > 0).sum())
v["slip"] = 0.1
v["start"], v["goal"] = f"第{int(start[0])+1}行第{int(start[1])+1}列", f"第{int(goal[0])+1}行第{int(goal[1])+1}列"

# ---------- （2）价值迭代
GAMMA = 0.95
V, pi, iters, deltas = value_iteration(P, R, GAMMA)
v["gamma"] = GAMMA
v["vi_iters"] = iters
v["v_start"] = float(V[idx[start]])
v["v_goal"] = float(V[idx[goal]])
v["v_max"], v["v_min"] = float(V.max()), float(V.min())
# 每一轮的误差按 γ 的比例往下掉：这是压缩映射的保证，不是经验
ratio = deltas[5:12] / deltas[4:11]
v["contract_ratio"] = float(np.mean(ratio))
assert abs(v["contract_ratio"] - GAMMA) < 0.02, "每轮的误差大约乘以 γ——贝尔曼算子是压缩映射"
v["delta_first"], v["delta_last"] = float(deltas[0]), float(deltas[-1])
# 从起点照最优策略走，平均要走多少步
s, steps, seen = idx[start], 0, set()
while s != idx[goal] and steps < 100:
    s = int(np.argmax(P[s, pi[s]]))
    steps += 1
v["steps_greedy"] = steps

# ---------- （3）策略迭代
V2, pi2, pi_iters = policy_iteration(P, R, GAMMA)
v["pi_iters"] = pi_iters
v["same_policy"] = bool((pi == pi2).all())
v["v_diff"] = float(np.abs(V - V2).max())
assert v["same_policy"] and v["v_diff"] < 1e-9, "两条路给出同一个答案"
v["speedup_iters"] = v["vi_iters"] / v["pi_iters"]

# ---------- （4）折扣因子
rows = []
for gm in (0.5, 0.8, 0.95, 0.99):
    Vg, pig, it, _ = value_iteration(P, R, gm)
    s, steps = idx[start], 0
    while s != idx[goal] and steps < 200:
        s = int(np.argmax(P[s, pig[s]]))
        steps += 1
    rows.append((gm, round(float(Vg[idx[start]]), 2), it, steps if steps < 200 else -1,
                 round(1 / (1 - gm), 1)))
v["gamma_rows"] = rows                     # （γ, 起点价值, 迭代轮数, 走到出口的步数, 有效视野 1/(1−γ)）
v["horizon_50"], v["horizon_99"] = 1 / (1 - 0.5), 1 / (1 - 0.99)
v["v_start_50"], v["v_start_99"] = rows[0][1], rows[-1][1]
assert rows[0][3] > 0 and rows[-1][3] > 0, "各档折扣因子下都走得到出口"
v["iters_50"], v["iters_99"] = rows[0][2], rows[-1][2]
# 这个车间里迭代轮数与 γ 无关（14 轮），因为出口是吸收态、绝大多数格子的转移是确定的：
# 价值在"最长的一条路"走完之后就不再变了。一般的 MDP 不是这样，轮数随 γ 接近 1 而变多。
v["same_iters"] = v["iters_50"] == v["iters_99"]
v["longest_path"] = v["vi_iters"]
assert v["v_start_50"] < 0 < v["v_start_99"], "折扣太小的时候，连走过去都不值得"
out(**v)
