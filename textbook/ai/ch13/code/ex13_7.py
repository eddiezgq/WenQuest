"""算例 13.7.1—13.7.3：思维链、采样投票与它们的代价（13.7 节）。

（1）投票为什么有用、能有多用：把“每条推理路径各自独立地以概率 p 答对”这个最简单的模型算一遍，
    多数投票的正确率就是二项分布的尾概率。用它去对照论文公布的提升（56.5% → 74.4%，40 条路径），
    反推出隐含的单路正确率——再看这个数说明了什么：**实测的提升远小于独立假设的预测，说明路径之间高度相关**。
（2）代价：思维链把输出词元数放大若干倍，投票再乘上路径数。按 9.7 节的结论，解码受带宽限制，
    所以“词元数 × 单价”与“词元数 × 每词元时间”就是账的全部。
（3）长思维链（强化学习训出来的推理模型）公布的分数与它的代价口径：一次作答、64 条共识、1000 条重排序
    不是同一类指标，正文必须写清。
"""
import math

import numpy as np

from bookout import out
from llm_facts import COT_GSM8K, COT_PRIOR_SOTA, O1, R1, R1_ZERO, SELF_CONSISTENCY

v = {}
# ---------- （1）投票的数学
def vote_acc(p, k):
    """k 条独立路径取多数（k 为奇数）时答对的概率。"""
    return sum(math.comb(k, m) * p ** m * (1 - p) ** (k - m) for m in range(k // 2 + 1, k + 1))


P0 = 0.565                                           # 论文给的单次思维链准确率（PaLM-540B，GSM8K）
v["p_single"] = P0 * 100
for k in (1, 5, 11, 41):
    v[f"vote_{k}"] = vote_acc(P0, k) * 100
v["vote_gain_indep"] = v["vote_41"] - v["vote_1"]    # 独立假设预测的提升
v["sc_before"], v["sc_after"] = SELF_CONSISTENCY["gsm8k"]
v["sc_paths"] = SELF_CONSISTENCY["paths"]
v["sc_gain_real"] = v["sc_after"] - v["sc_before"]   # 论文实测的提升
v["gap_indep_real"] = v["vote_gain_indep"] - v["sc_gain_real"]
# 反推：要让 41 条路径的投票只到 74.4%，单路的"等效独立正确率"得是多少
lo, hi = 0.3, 0.9
for _ in range(60):
    mid = (lo + hi) / 2
    if vote_acc(mid, 41) < v["sc_after"] / 100:
        lo = mid
    else:
        hi = mid
v["p_equiv"] = (lo + hi) / 2 * 100
v["p_equiv_drop"] = v["p_single"] - v["p_equiv"]
assert v["gap_indep_real"] > 3, "独立假设会高估投票的好处，这个结论不能靠手写"
# 思维链本身的提升（论文正文图 4 的三个模型）
for name, (std, cot) in COT_GSM8K.items():
    key = name.split()[0].lower()
    v[f"cot_{key}_std"], v[f"cot_{key}_cot"] = std, cot
    v[f"cot_{key}_gain"] = cot - std
v["cot_best_gain"] = max(cot - std for std, cot in COT_GSM8K.values())
v["cot_prior_sota"] = COT_PRIOR_SOTA

# ---------- （2）代价
IN_TOK, ANS_TOK, COT_TOK = 60, 12, 220               # 问题、直接作答、带推理过程的作答各多少词元
PRICE_IN, PRICE_OUT = 2.0, 8.0                       # 美元/百万词元（教材假设的单价）
MS_PER_TOK = 0.6                                     # 解码一个词元的时间（量级取自 12.4 节的办法）
v["in_tok"], v["ans_tok"], v["cot_tok"] = IN_TOK, ANS_TOK, COT_TOK
v["price_in"], v["price_out"], v["ms_per_tok"] = PRICE_IN, PRICE_OUT, MS_PER_TOK
v["cot_tok_ratio"] = COT_TOK / ANS_TOK


def cost_1k(out_tok, k=1):
    """一千个问题的费用（美元）：输入按一次计（投票时提示相同，可缓存），输出按 k 次计。"""
    return (IN_TOK * PRICE_IN + out_tok * k * PRICE_OUT) * 1000 / 1e6


v["cost_direct"] = cost_1k(ANS_TOK)
v["cost_cot"] = cost_1k(COT_TOK)
v["cost_vote40"] = cost_1k(COT_TOK, 40)
v["cot_vs_direct"] = v["cost_cot"] / v["cost_direct"]
v["vote_vs_cot"] = v["cost_vote40"] / v["cost_cot"]
v["lat_direct_ms"] = ANS_TOK * MS_PER_TOK
v["lat_cot_ms"] = COT_TOK * MS_PER_TOK
v["lat_vote_ms"] = COT_TOK * MS_PER_TOK              # 40 条路径可以并行，延迟不变，花的是钱与显存
v["acc_per_dollar_cot"] = (v["cot_palm_cot"] - v["cot_palm_std"]) / (v["cost_cot"] - v["cost_direct"])
v["acc_per_dollar_vote"] = v["sc_gain_real"] / (v["cost_vote40"] - v["cost_cot"])
v["dollar_ratio"] = v["acc_per_dollar_cot"] / v["acc_per_dollar_vote"]

# ---------- （3）长思维链公布的数字
v["o1_single"], v["o1_cons64"], v["o1_rerank"] = O1["aime_single"], O1["aime_cons64"], O1["aime_rerank1000"]
v["o1_base"] = O1["gpt4o_aime"]
v["o1_span"] = O1["aime_rerank1000"] - O1["aime_single"]     # 同一个模型，三种口径差这么多
v["o1_params_known"] = O1["params"] is not None              # 未公布
v["r1_aime"], v["r1_math"], v["r1_gpqa"], v["r1_mmlu"] = R1["aime"], R1["math500"], R1["gpqa"], R1["mmlu"]
v["r1_elo"] = R1["codeforces_elo"]
v["r0_aime"], v["r0_cons"] = R1_ZERO["aime_pass1"], R1_ZERO["aime_cons64"]
v["r0_gain"] = R1_ZERO["aime_cons64"] - R1_ZERO["aime_pass1"]
v["r1_vs_r0"] = R1["aime"] - R1_ZERO["aime_pass1"]
out(**v)
