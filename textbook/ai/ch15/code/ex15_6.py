"""算例 15.6.1—15.6.3：对手也在学的时候（15.6 节）。

（1）三条调度规则互相克制，构成一个循环：谁都不是最强的，"打赢上一个版本"会一直转圈。
（2）自我对弈只盯着上一版，策略就在圈里打转；留一个"过去各版本的池子"才停得下来。
（3）AlphaStar 的联盟训练与 OpenAI Five 的规模：公开发表的数字。
"""
import numpy as np

from _ch15 import CYCLE, RULES, self_play_cycle
from bookout import out
from rl_facts import ALPHASTAR, OPENAI_FIVE

v = {}
# ---------- （1）循环克制
v["rules"] = list(RULES)
v["payoff"] = [[int(x) for x in row] for row in CYCLE]
v["n_rules"] = len(RULES)
# 任何一个纯策略都能被另一个克制：每一列都有一个 +1
v["each_beaten"] = bool(all((CYCLE[:, j] > 0).any() for j in range(len(RULES))))
assert v["each_beaten"], "每条规则都有克星——没有哪条是最强的"
# 混合策略的均衡：三条规则各三分之一（这是这个循环博弈的唯一均衡）
v["mix"] = 1 / len(RULES)
v["mix_value"] = float(np.ones(3) @ CYCLE @ np.ones(3) / 9)
assert abs(v["mix_value"]) < 1e-12, "均匀混合时谁也占不到便宜"

# ---------- （2）自我对弈只盯着上一版
seq = self_play_cycle(rounds=60, seed=0)
v["seq_head"] = [int(x) for x in seq[:9]]
v["period"] = int(np.argmax([np.array_equal(seq[:5], seq[k:k + 5]) for k in range(1, 10)]) + 1)
assert v["period"] == len(RULES), "每隔三轮回到原地——这就是转圈"
v["rounds"] = len(seq)
# 转了这么多轮，针对"全部历史对手的平均"其实一点没变好：对历史平均的收益一直是 0
hist = np.bincount(seq, minlength=3) / len(seq)
v["share"] = [round(float(x) * 100, 1) for x in hist]
v["vs_history"] = float(max(CYCLE @ hist))
v["vs_last"] = 1.0                          # 对上一版永远赢 1 分
assert v["vs_history"] < 0.1, "打赢上一版很容易，打赢'过去全部版本的平均'就没那么容易了"
# 对付转圈的办法：每一轮针对"历史平均"而不是"上一版"训练
cur = np.ones(3) / 3
for _ in range(200):
    br = int(np.argmax(CYCLE @ cur))
    cur = cur * 0.98
    cur[br] += 0.02
v["fp_mix"] = [round(float(x) * 100, 1) for x in cur]
v["fp_gap"] = float(np.abs(cur - 1 / 3).max())
assert v["fp_gap"] < 0.1, "对历史平均做最优应对，策略收敛到均衡附近"

# ---------- （3）公开发表的数字
v["as_percentile"] = ALPHASTAR["percentile"]
v["as_mmr_p"], v["as_mmr_sup"] = ALPHASTAR["mmr_protoss"], ALPHASTAR["mmr_supervised"]
v["as_days"] = ALPHASTAR["league_days"]
v["as_agents"], v["as_players"] = ALPHASTAR["agents"], ALPHASTAR["players"]
v["as_tpu_each"] = ALPHASTAR["tpu_per_agent"]
v["as_tpu_total"] = ALPHASTAR["agents"] * ALPHASTAR["tpu_per_agent"]      # 折算：论文没给总数
v["as_league_games_yi"] = ALPHASTAR["league_games"] / 1e8
v["as_replays_w"] = ALPHASTAR["replays"] / 1e4
v["as_actions_5s"] = ALPHASTAR["actions_per_5s"]
v["as_apm"] = ALPHASTAR["actions_per_5s"] * 12                            # 折算：论文给的是每 5 秒
v["as_delay_ms"] = ALPHASTAR["delay_ms"]
v["as_pros_known"] = ALPHASTAR["vs_pros_final"] is not None
assert not v["as_pros_known"], "最终版对职业选手的战绩，论文没给"
v["of_days"] = OPENAI_FIVE["train_days"]
v["of_pflops_days"] = OPENAI_FIVE["pflops_days_og"]
v["of_gpu"], v["of_cpu_w"] = OPENAI_FIVE["gpu_peak"], OPENAI_FIVE["cpu_peak"] / 1e4
v["of_arena_games"], v["of_arena_win"] = OPENAI_FIVE["arena_games"], OPENAI_FIVE["arena_winrate"]
v["of_reaction"], v["of_blog_reaction"] = OPENAI_FIVE["reaction_ms"], OPENAI_FIVE["blog_reaction_ms"]
v["of_rerun_months"], v["of_rerun_pflops"] = OPENAI_FIVE["rerun_months"], OPENAI_FIVE["rerun_pflops_days"]
v["of_rerun_share"] = OPENAI_FIVE["rerun_pflops_days"] / OPENAI_FIVE["pflops_days_og"] * 100
v["of_surgeries"] = OPENAI_FIVE["surgeries"]
v["of_obs"] = OPENAI_FIVE["obs_values"]
v["of_actions_min"], v["of_actions_max"] = OPENAI_FIVE["actions_min"], OPENAI_FIVE["actions_max"]
out(**v)
