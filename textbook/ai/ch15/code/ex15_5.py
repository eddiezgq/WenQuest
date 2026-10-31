"""算例 15.5.1—15.5.3：看不见对方的牌时，怎么才算下得好（15.5 节）。

（1）Kuhn 扑克有闭式的纳什均衡：先手拿最小牌虚张的概率 α ∈ [0, 1/3]，
    任何均衡下先手的期望收益都是 −1/18。拿它核对算出来的策略对不对。
（2）反事实遗憾最小化（CFR）自我对弈若干轮，可利用度怎样按 1/√T 往下掉。
（3）Pluribus 的算力：六人德扑打赢职业选手，蓝图策略在 64 核上训了 8 天，全程没用 GPU。
"""
import numpy as np

from _ch15 import CARDS, CFR, KUHN_VALUE
from bookout import out
from rl_facts import CFR as CFR_FACTS
from rl_facts import KUHN, LIBRATUS, PLURIBUS

v = {}
# ---------- （1）（2）CFR 跑到均衡
rows = []
for iters in (100, 1_000, 10_000, 50_000):
    cf = CFR()
    avg, val = cf.run(iters, seed=0)
    rows.append((iters, round(float(cf.exploitability(avg)), 5), round(float(val), 4)))
v["cfr_rows"] = rows                      # （轮数, 可利用度, 先手的平均收益）
v["expl_100"], v["expl_50k"] = rows[0][1], rows[-1][1]
v["drop"] = v["expl_100"] / v["expl_50k"]
assert v["expl_50k"] < v["expl_100"] / 10, "轮数多了，可利用度掉下去"
# 理论上界按 1/√T 掉：轮数乘 100，可利用度大约除以 10
v["sqrt_pred"] = np.sqrt(rows[-1][0] / rows[0][0])
v["drop_vs_pred"] = v["drop"] / v["sqrt_pred"]

cf = CFR()
avg, val = cf.run(50_000, seed=0)
v["iters"] = 50_000
v["value"] = float(val)
v["value_theory"] = KUHN_VALUE
v["value_err"] = abs(v["value"] - KUHN_VALUE)
assert v["value_err"] < 0.01, "算出来的博弈值与 −1/18 对得上"
v["alpha"] = float(avg["J"][1])           # 先手拿最小牌（J）时下注的概率，就是均衡族里的 α
v["alpha_hi"] = KUHN["alpha_hi"]
assert -1e-6 <= v["alpha"] <= KUHN["alpha_hi"] + 0.02, "α 落在 [0, 1/3] 里"
v["bet_K"] = float(avg["K"][1])           # 拿最大牌时下注的概率
v["call_Qb"] = float(avg["Qb"][1])        # 后手拿 Q 面对下注时跟注的概率
v["bluff_ratio"] = v["bet_K"] / max(v["alpha"], 1e-9)
# 均衡的一条漂亮性质：拿最大牌下注的概率正好是拿最小牌虚张的三倍
assert abs(v["bluff_ratio"] - 3) < 0.6, "拿 K 下注的概率约等于拿 J 虚张的三倍"
v["expl"] = float(cf.exploitability(avg))
v["n_infosets"] = len(avg)
# 均衡的一条性质：拿 Q（中间那张牌）先手时几乎从不下注
v["bet_Q"] = float(avg["Q"][1])
assert v["bet_Q"] < 0.1, "拿中间那张牌时先手几乎不下注——这也是均衡的一部分"

# ---------- （3）公开发表的数字
v["lib_pros"], v["lib_hands_w"] = LIBRATUS["pros"], LIBRATUS["hands"] / 1e4
v["lib_mbb"], v["lib_p"] = LIBRATUS["mbb_per_hand"], LIBRATUS["p_value"]
v["lib_points"] = LIBRATUS["decision_points"]
v["lib_compute_known"] = LIBRATUS["compute"] is not None
assert not v["lib_compute_known"], "Libratus 的算力论文没给"
v["plu_pros"], v["plu_hands_w"] = PLURIBUS["pros_pool"], PLURIBUS["hands_exp1"] / 1e4
v["plu_mbb"], v["plu_se"], v["plu_p"] = PLURIBUS["mbb_exp1"], PLURIBUS["se_exp1"], PLURIBUS["p_exp1"]
v["plu_cores"], v["plu_days"] = PLURIBUS["cores"], PLURIBUS["days_train"]
v["plu_core_hours"] = PLURIBUS["core_hours"]
v["plu_usd"] = PLURIBUS["usd"]
v["plu_gpu"] = PLURIBUS["gpu"]
v["ag_search_cpu"], v["ag_search_gpu"] = PLURIBUS["alphago_search_cpu"], PLURIBUS["alphago_search_gpu"]
v["plu_sec_per_hand"] = PLURIBUS["sec_per_hand"]
# CFR 的理论保证（Zinkevich 等 2007）
v["zink_iters_yi"] = CFR_FACTS["zinkevich_iters"] / 1e8
v["zink_hours"], v["zink_cpus"] = CFR_FACTS["zinkevich_hours"], CFR_FACTS["zinkevich_cpus"]
v["zink_exploit"] = CFR_FACTS["zinkevich_exploit_mbh"]
v["abs_infosets_M"] = CFR_FACTS["abstraction_infosets"] / 1e6
v["full_infosets_M"] = CFR_FACTS["full_infosets"] / 1e6
v["abs_ratio"] = CFR_FACTS["full_infosets"] / CFR_FACTS["abstraction_infosets"]
out(**v)
