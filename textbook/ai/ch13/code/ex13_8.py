"""算例 13.8.1—13.8.3：评测（13.8 节）。

（1）一个分数能信到几位：1000 道题上测出 70%，置信区间有多宽（威尔逊区间）；
    要把两个模型 1 个百分点的差别测出来，需要多少题。排行榜上相邻两名的差别，常常小于这个区间。
（2）排名会不会翻：两个真实水平相差 1 个百分点的模型，在 1000 道题上谁赢的概率是多少（模拟）。
（3）数据污染：按 GSM1k 论文的做法，在同难度的新题上重测，掉分多少才算异常；
    以及为自己的场景做一套评测要多少题（用第 13.9 节的手册问答集算）。
"""
import math

import numpy as np

from bookout import out
from llm_facts import GSM1K, GSM8K, HUMANEVAL, MMLU

v = {}
Z = 1.959963984540054                                # 95% 的正态分位数


def wilson(p, n, z=Z):
    """威尔逊区间：比正态近似稳，尤其在 p 接近 0 或 1 时。"""
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


# ---------- （1）一个分数能信到几位
v["gsm_test"] = GSM8K["test"]
v["mmlu_test"] = MMLU["test"]
v["humaneval_n"] = HUMANEVAL["problems"]
for n, key in ((164, "n164"), (1000, "n1k"), (14_079, "n14k")):
    lo, hi = wilson(0.70, n)
    v[f"{key}_lo"], v[f"{key}_hi"] = lo * 100, hi * 100
    v[f"{key}_halfwidth"] = (hi - lo) / 2 * 100
v["he_halfwidth"] = v["n164_halfwidth"]              # HumanEval 只有 164 题，这就是它的区间半宽
# 要把 1 个百分点的差别测出来需要多少题（两比例之差的检验，近似式 n ≈ 2·z²·p(1−p)/δ²）
for delta, key in ((0.01, "d1"), (0.02, "d2"), (0.05, "d5")):
    v[f"need_{key}"] = 2 * Z ** 2 * 0.7 * 0.3 / delta ** 2
v["mmlu_enough_1pt"] = v["mmlu_test"] >= v["need_d1"]
v["he_enough_5pt"] = v["humaneval_n"] >= v["need_d5"]

# ---------- （2）排名会不会翻
rng = np.random.default_rng(138)
P_A, P_B, N, TRIALS = 0.70, 0.71, 1000, 20_000
v["p_a"], v["p_b"], v["n_item"], v["trials"] = P_A * 100, P_B * 100, N, TRIALS
a = rng.binomial(N, P_A, TRIALS)
b = rng.binomial(N, P_B, TRIALS)
v["flip_pct"] = float((a > b).mean()) * 100          # 本该第二的模型赢了的比例
v["tie_pct"] = float((a == b).mean()) * 100
# 换成相差 5 个百分点
b5 = rng.binomial(N, 0.75, TRIALS)
v["flip5_pct"] = float((a > b5).mean()) * 100
v["flip_ratio"] = v["flip_pct"] / max(v["flip5_pct"], 1e-9)

# ---------- （3）污染与自建评测
v["gsm1k_n"], v["gsm1k_drop"], v["gsm1k_r2"] = GSM1K["problems"], GSM1K["max_drop"], GSM1K["spearman_r2"]
lo, hi = wilson(0.70, GSM1K["problems"])
v["gsm1k_halfwidth"] = (hi - lo) / 2 * 100
# 掉 8 个百分点在 1205 题上算不算显著：两组比例之差的 95% 区间
se = math.sqrt(0.70 * 0.30 / 1000 + 0.62 * 0.38 / GSM1K["problems"])
v["drop_se"] = se * 100
v["drop_signif"] = GSM1K["drop" if "drop" in GSM1K else "max_drop"] > Z * se * 100
v["drop_z"] = GSM1K["max_drop"] / (Z * se * 100)
# 自建评测：手册问答集只有几十题，区间有多宽
for n, key in ((29, "own29"), (100, "own100"), (500, "own500")):
    lo, hi = wilson(0.90, n)
    v[f"{key}_lo"], v[f"{key}_hi"] = lo * 100, hi * 100
    v[f"{key}_halfwidth"] = (hi - lo) / 2 * 100
v["own_need"] = 2 * Z ** 2 * 0.9 * 0.1 / 0.05 ** 2   # 要分辨 5 个百分点需要多少题
v["mmlu_expert"], v["mmlu_crowd"], v["mmlu_random"] = MMLU["expert_95pct"], MMLU["crowdworker"], MMLU["random"]
v["mmlu_subjects"] = MMLU["subjects"]
v["mmlu_per_subject"] = MMLU["test"] / MMLU["subjects"]
lo, hi = wilson(0.70, v["mmlu_per_subject"])
v["mmlu_subject_halfwidth"] = (hi - lo) / 2 * 100    # 单科的区间：按科目比较排名几乎没有意义
out(**v)
