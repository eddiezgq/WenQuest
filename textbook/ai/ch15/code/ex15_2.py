"""算例 15.2.1—15.2.4：从表格到网络，中间会掉进什么坑（15.2 节）。

（1）表格 Q 学习：不知道转移与奖励，只靠试，能不能逼近价值迭代算出来的那个答案。
（2）三件事凑在一起会发散：Baird 1995 的七状态反例——奖励全是零、真实价值全是零，
    权重却能飞到十万。
（3）目标网络与同策略取样各能治住它——这正是深度 Q 网络那两条"工程技巧"的来历。
（4）DQN 公开发表的那几个数：评测规模、训练帧数、回放池、ε 怎样退火。
"""
import numpy as np

from _ch15 import baird, q_learning, shop_mdp, value_iteration
from bookout import out
from rl_facts import DQN, DQN2013

v = {}
P, R, idx, g, start, goal = shop_mdp()
GAMMA = 0.95
V, pi, _, _ = value_iteration(P, R, GAMMA)

# ---------- （1）表格 Q 学习
rows = []
for steps in (20_000, 100_000, 400_000):
    Q, _ = q_learning(P, R, GAMMA, steps=steps, goal=idx[goal], seed=0)
    err = float(np.abs(Q.max(1) - V).max())
    match = int((Q.argmax(1) == pi).sum())
    rows.append((steps, round(err, 3), match, len(pi)))
v["q_rows"] = rows
v["q_err_20k"], v["q_err_400k"] = rows[0][1], rows[-1][1]
v["q_match_400k"], v["n_states"] = rows[-1][2], len(pi)
assert v["q_err_400k"] < v["q_err_20k"], "试得越多，估得越准"
v["q_match_pct"] = v["q_match_400k"] / v["n_states"] * 100
# 它停在一个噪声底上，不会精确收敛——因为步长是常数（每一步都把新样本按固定比例掺进去）
v["alpha"] = 0.2
v["v_scale"] = float(V.max())
v["q_err_rel"] = v["q_err_400k"] / v["v_scale"] * 100

# ---------- （2）（3）三件事凑在一起
STEPS = 3000
curves = {}
for name, kw in (("deadly", {}), ("target", {"target_every": 200}), ("onpolicy", {"on_policy": True})):
    h, w = baird(steps=STEPS, **kw)
    curves[name] = h
    v[f"norm_{name}"] = float(h[-1])
v["norm_start"] = float(curves["deadly"][0])
v["baird_steps"] = STEPS
v["baird_states"] = 7
v["baird_weights"] = 8
v["blowup"] = v["norm_deadly"] / v["norm_start"]
assert v["norm_deadly"] > 1000 * v["norm_target"], "三件事齐了就发散，冻住自举的那一份就不发散"
assert v["norm_onpolicy"] < v["norm_start"] * 2, "改成同策略取样也不发散"
v["target_every"] = 200

# ---------- （4）公开发表的数字
v["dqn_games"] = DQN["games"]
v["dqn_beat_prior"] = DQN["beat_prior_rl"]
v["dqn_above75"] = DQN["above_75pct_human"]
v["dqn_frames_M"] = DQN["frames"] / 1e6
v["dqn_game_days"] = DQN["game_days"]
v["dqn_steps_M"] = DQN["frames"] / DQN["skip"] / 1e6          # 折算：跳帧 4
v["dqn_replay_M"] = DQN["replay"] / 1e6
v["dqn_eps_from"], v["dqn_eps_to"] = DQN["eps_from"], DQN["eps_to"]
v["dqn_eps_frames_M"] = DQN["eps_frames"] / 1e6
v["dqn_batch"], v["dqn_gamma"] = DQN["batch"], DQN["gamma"]
v["dqn_replay_ratio"] = DQN["replay"] / DQN["batch"]           # 回放池里一个样本平均被用多少次的量级
v["dqn2013_games"], v["dqn2013_frames_M"] = DQN2013["games"], DQN2013["frames"] / 1e6
v["dqn2013_target"] = DQN2013["target_net"]
v["dqn_hardware_known"] = DQN["hardware"] is not None          # 论文没写训练硬件
v["dqn_median_known"] = DQN["median_human_norm"] is not None   # 论文也没给中位数
assert not v["dqn_hardware_known"] and not v["dqn_median_known"]
out(**v)
