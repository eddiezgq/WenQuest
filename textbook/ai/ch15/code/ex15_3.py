"""算例 15.3.1—15.3.3：搜索到底值多少（15.3 节）。

（1）取木棍游戏有必胜策略（剩下的根数是 4 的倍数时轮到谁谁输），所以可以拿它核对搜索对不对。
（2）蒙特卡洛树搜索：模拟次数从十几次加到几千次，选对率怎样上去。
（3）AlphaGo 那条线的公开数字：策略网络、价值网络、走子网络各管什么，搜索值多少 Elo。
"""
import numpy as np

from _ch15 import sticks_best, uct
from bookout import out
from rl_facts import ALPHAGO, ALPHAGO_ZERO

v = {}
# ---------- （1）这个游戏的解析解
v["take_max"] = 3
v["losing_mod"] = 4                       # 剩 4 的倍数根时，轮到走的人必输
v["n_test"] = len([n for n in range(5, 26) if n % 4])
v["example_n"] = 13
v["example_best"] = sticks_best(13)       # 13 % 4 = 1，取 1 根留下 12

# ---------- （2）模拟次数与选对率
rows = []
for sims in (10, 30, 100, 300, 1000):
    ok = 0
    for n in range(5, 26):
        if n % 4 == 0:
            continue
        a, acts, visits, wins = uct(n, sims, g=np.random.default_rng(100 + n))
        ok += int(a == sticks_best(n))
    rows.append((sims, round(ok / v["n_test"] * 100, 1)))
v["uct_rows"] = rows
v["acc_10"], v["acc_100"], v["acc_1000"] = rows[0][1], rows[2][1], rows[-1][1]
assert v["acc_1000"] >= v["acc_100"] >= 99 > v["acc_10"], "模拟次数一多就选得对了"
# 搜索的"分配"：它把绝大多数模拟花在看着最好的那一支上
a, acts, visits, wins = uct(13, 1000, g=np.random.default_rng(7))
v["visits"] = [int(x) for x in visits]
v["acts"] = list(acts)
v["best_share"] = float(visits.max() / visits.sum() * 100)
v["winrate_best"] = float(wins[int(visits.argmax())] / visits.max() * 100)
v["uniform_share"] = 100 / len(acts)
assert v["best_share"] > 1.5 * v["uniform_share"], "搜索不平均用力，它把模拟集中在最有希望的那一支上"

# ---------- （3）AlphaGo 那条线的公开数字
v["ag_acc_policy"] = ALPHAGO["acc_policy"]
v["ag_acc_prior"] = ALPHAGO["acc_prior_best"]
v["ag_acc_rollout"] = ALPHAGO["acc_rollout"]
v["ag_us_rollout"], v["ag_ms_policy"] = ALPHAGO["us_rollout"], ALPHAGO["ms_policy"]
v["ag_speed_ratio"] = ALPHAGO["ms_policy"] * 1000 / ALPHAGO["us_rollout"]     # 折算：快多少倍
v["ag_kgs_games_w"] = ALPHAGO["kgs_games"] / 1e4
v["ag_kgs_pos_M"] = ALPHAGO["kgs_positions"] / 1e6
v["ag_value_pos_M"] = ALPHAGO["value_positions"] / 1e6
v["ag_dist_cpu"], v["ag_dist_gpu"] = ALPHAGO["dist_cpu"], ALPHAGO["dist_gpu"]
v["ag_elo_dist"], v["ag_elo_pachi"] = ALPHAGO["elo_dist"], ALPHAGO["elo_pachi"]
v["ag_wins"], v["ag_games"] = ALPHAGO["wins"], ALPHAGO["games_vs_programs"]
v["ag_winrate"] = ALPHAGO["wins"] / ALPHAGO["games_vs_programs"] * 100
v["ag_sims_known"] = ALPHAGO["sims_per_move"] is not None     # 论文没给每步模拟次数
assert not v["ag_sims_known"]
# 搜索值多少：同一个网络，带搜索与不带搜索的 Elo 差（AlphaGo Zero 论文给的数）
v["az_elo_search"] = ALPHAGO_ZERO["elo_zero40"]
v["az_elo_raw"] = ALPHAGO_ZERO["elo_raw_net"]
v["az_elo_gain"] = v["az_elo_search"] - v["az_elo_raw"]
v["az_sims"] = ALPHAGO_ZERO["sims_per_move"]
v["az_sec"] = ALPHAGO_ZERO["sec_per_move"]
# Elo 差换成胜率（逻辑斯谛公式，这是 Elo 的定义，不是论文数字）
v["az_winrate"] = 1 / (1 + 10 ** (-v["az_elo_gain"] / 400)) * 100
assert v["az_winrate"] > 99, "带搜索对不带搜索，几乎不输"
out(**v)
