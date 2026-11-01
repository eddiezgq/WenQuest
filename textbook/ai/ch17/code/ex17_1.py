"""算例 17.1.1—17.1.4：代码模型怎么评，以及这把尺子的几处坑（17.1 节）。

（1）pass@k 的无偏估计量：用蒙特卡洛验证它确实无偏，再看两种常见的错写法各错多少。
（2）温度与 k：同一个模型，k 越大最优温度越高——这不是玄学，是采样分布的性质，算得出来。
（3）数据污染：背下答案的和真会解题的，在原题上分不开，在改写过的题上立刻分开。
（4）公开发表的数字与它们的口径：为什么 SWE-bench 的分数必须"三件事一起写"。
"""
import numpy as np

from _ch17 import (best_temperature, contamination, pass_at_k, pass_at_k_naive, pass_curve,
                   problem_logits, sample_pass_at_k, N_PROBLEMS, N_WAYS)
from agent_facts import (CODEX_TABLE1, CODEX_TEMP, CONTAM, EVALPLUS, HUMANEVAL, MBPP,
                         SWEBENCH, SWEBENCH_VERIFIED)
from bookout import out

v = {}

# ---------- （1）pass@k 的估计量
v["he_problems"] = HUMANEVAL["problems"]
v["he_n"], v["he_kmax"] = HUMANEVAL["n_samples"], HUMANEVAL["k_max"]
v["he_formula"] = HUMANEVAL["formula"]
v["he_tests_codex"], v["he_tests_evalplus"] = (HUMANEVAL["tests_per_problem_codex"],
                                               HUMANEVAL["tests_per_problem_evalplus"])
g = np.random.default_rng(0)
v["unbiased_rows"] = []
worst = 0.0
for p in (0.1, 0.3, 0.6):
    for k in (1, 10, 100):
        est, true = sample_pass_at_k(p, HUMANEVAL["n_samples"], k, 4000, g)
        v["unbiased_rows"].append((p, k, round(est, 4), round(true, 4)))
        worst = max(worst, abs(est - true))
v["unbiased_max_err"] = worst
assert worst < 0.01, "估计量是无偏的：蒙特卡洛均值应当贴着真值"

# 错写法甲：逐题用 1 − (1 − c/n)^k。n 小的时候偏得厉害
N_SMALL, K_SMALL, P_SMALL = 10, 5, 0.25
cs = g.binomial(N_SMALL, P_SMALL, 40000)
v["n_small"], v["k_small"], v["p_small"] = N_SMALL, K_SMALL, P_SMALL
v["naive_small"] = float(np.mean([pass_at_k_naive(c / N_SMALL, K_SMALL) for c in cs]))
v["unbiased_small"] = float(np.mean([pass_at_k(N_SMALL, int(c), K_SMALL) for c in cs]))
v["true_small"] = 1 - (1 - P_SMALL) ** K_SMALL
v["naive_small_err"] = (v["true_small"] - v["naive_small"]) * 100
assert v["naive_small"] < v["true_small"] - 0.05, "这种写法会低估"

# 错写法乙：拿"平均 pass@1"往上外推。难度不均时错得离谱
ps = np.concatenate([np.full(200, 0.02), np.full(200, 0.60)])   # 一半很难、一半很容易
cs2 = np.array([g.binomial(HUMANEVAL["n_samples"], p) for p in ps])
v["mixed_hard"], v["mixed_easy"] = 0.02, 0.60
v["mixed_true"] = float(np.mean([1 - (1 - p) ** 10 for p in ps]))
v["mixed_unbiased"] = float(np.mean([pass_at_k(HUMANEVAL["n_samples"], int(c), 10) for c in cs2]))
v["mixed_mean_p1"] = float(np.mean(cs2 / HUMANEVAL["n_samples"]))
v["mixed_extrap"] = 1 - (1 - v["mixed_mean_p1"]) ** 10
v["mixed_over_pts"] = (v["mixed_extrap"] - v["mixed_true"]) * 100
assert v["mixed_over_pts"] > 30, "难度一不均，外推就高估几十个百分点——这是这一节最该记住的一条"
assert abs(v["mixed_unbiased"] - v["mixed_true"]) < 0.02, "无偏估计量不受难度不均的影响"

# ---------- （2）温度与 k
logits, right = problem_logits()
v["n_toy_problems"], v["n_ways"] = N_PROBLEMS, N_WAYS
v["temp_rows"] = []
for T in (0.0, 0.2, 0.4, 0.6, 0.8, 1.2, 2.0):
    c = pass_curve(logits, right, T)
    v["temp_rows"].append((T, round(c[1], 3), round(c[10], 3), round(c[100], 3)))
    v[f"p1_T{str(T).replace('.', 'p')}"] = round(c[1], 3)
    v[f"p10_T{str(T).replace('.', 'p')}"] = round(c[10], 3)
    v[f"p100_T{str(T).replace('.', 'p')}"] = round(c[100], 3)
v["best_rows"] = []
last_t = -1.0
for k in (1, 5, 10, 50, 100):
    t, val = best_temperature(logits, right, k)
    v["best_rows"].append((k, t, round(val, 3)))
    v[f"bestT_k{k}"], v[f"bestV_k{k}"] = t, round(val, 3)
    assert t >= last_t, "k 越大，最优温度越高——与 Codex 论文的观察同一个方向"
    last_t = t
assert v["bestT_k100"] > v["bestT_k1"], "pass@1 与 pass@100 的最优温度不是同一个"
# Codex 论文自己给的那一组（679M 模型）
v["codex_t_p1"] = CODEX_TEMP["model_679m"]["pass1"]
v["codex_t_p100"] = CODEX_TEMP["model_679m"]["pass100"]
v["codex12b_p1"], v["codex12b_p10"], v["codex12b_p100"] = CODEX_TABLE1["Codex-12B"]
v["codex_ratio"] = v["codex12b_p100"] / v["codex12b_p1"]    # 折算：但两个数的温度不同

# ---------- （3）数据污染
c = contamination()
v["seen_frac_pct"] = c["seen_frac"] * 100
v["memo_orig"], v["memo_para"] = c["memo_orig"] * 100, c["memo_para"] * 100
v["solver_orig"], v["solver_para"] = c["solver_orig"] * 100, c["solver_para"] * 100
v["memo_seen"], v["memo_unseen"] = c["memo_seen"] * 100, c["memo_unseen"] * 100
v["solver_seen"], v["solver_unseen"] = c["solver_seen"] * 100, c["solver_unseen"] * 100
v["memo_gap"] = v["memo_seen"] - v["memo_unseen"]
v["solver_gap"] = abs(v["solver_seen"] - v["solver_unseen"])
assert abs(v["memo_orig"] - v["solver_orig"]) < 15, "在原题上两者分不太开"
assert v["memo_para"] < v["solver_para"] - 20, "一改写就分开了"
assert v["memo_gap"] > 60 and v["solver_gap"] < 15, \
    "见过与没见过的落差，是查污染最直接的信号"
# 真实研究给的数字
v["contam_he_pile"], v["contam_he_star"] = CONTAM["humaneval_pile_pct"], CONTAM["humaneval_starcoder_pct"]
v["contam_mbpp_pile"], v["contam_mbpp_star"] = CONTAM["mbpp_pile_pct"], CONTAM["mbpp_starcoder_pct"]
v["contam_drop_before"], v["contam_drop_after"] = CONTAM["drop"]["HumanEval/Pythia-12B"]
v["contam_drop_rel"] = (1 - v["contam_drop_after"] / v["contam_drop_before"]) * 100
v["contam_top"], v["contam_bottom"] = CONTAM["top_vs_bottom"]["HumanEval/StarCoderBase-15.5B"]
v["contam_single"] = CONTAM["single_number"] is not None
v["contam_causal"] = CONTAM["causal"]
assert not v["contam_single"], "那篇论文不给一个总的'污染抬高多少'的数"
assert not v["contam_causal"], "论文明说只是相关性，不能确定因果——引用时必须带上这一句"
# EvalPlus：这是"测试不够"，不是"污染"，两件事不要混讲
v["ep_multiplier"] = EVALPLUS["test_multiplier"]
v["ep_before"], v["ep_after"] = EVALPLUS["gpt4_before"], EVALPLUS["gpt4_after"]
v["ep_drop_pts"] = v["ep_before"] - v["ep_after"]
v["ep_wrong"], v["ep_wrong_pct"] = EVALPLUS["wrong_reference_solutions"], EVALPLUS["wrong_pct"]
v["ep_rank_flip"] = EVALPLUS["rank_flip"]
v["ep_mbpp_plus"] = EVALPLUS["mbpp_plus"] is not None
assert not v["ep_mbpp_plus"], "常见的 MBPP+ 分数不出自这篇论文"

# ---------- （4）SWE-bench：为什么必须三件事一起写
v["swe_instances"], v["swe_repos"], v["swe_lite"] = (SWEBENCH["instances"], SWEBENCH["repos"],
                                                     SWEBENCH["lite"])
v["swe_files"], v["swe_lines_k"] = SWEBENCH["files_mean"], SWEBENCH["lines_mean_k"]
v["swe_patch_files"], v["swe_patch_lines"] = SWEBENCH["patch_files"], SWEBENCH["patch_lines"]
v["swe_locate_ratio"] = SWEBENCH["files_mean"] / SWEBENCH["patch_files"]   # 折算：要在多少个里挑出这几个
v["swe_is_agent"] = SWEBENCH["is_agent"]
assert not v["swe_is_agent"], "原论文是单轮'读提示→产出 diff'，那些分数不是 agent 成绩"
v["swe_tokens_known"] = SWEBENCH["repo_tokens"] is not None
assert not v["swe_tokens_known"], "没有任何论文给'典型仓库多少词元'"
v["ver_samples"], v["ver_filtered"] = SWEBENCH_VERIFIED["samples"], SWEBENCH_VERIFIED["filtered_pct"]
v["ver_under"], v["ver_unfair"] = (SWEBENCH_VERIFIED["underspecified_pct"],
                                   SWEBENCH_VERIFIED["unfair_tests_pct"])
v["ver_gpt4o_v"], v["ver_gpt4o_o"] = (SWEBENCH_VERIFIED["gpt4o_verified"],
                                      SWEBENCH_VERIFIED["gpt4o_original"])
v["ver_subset_ratio"] = v["ver_gpt4o_v"] / v["ver_gpt4o_o"]       # 同一个模型，换个子集
v["scaffold_low"], v["scaffold_high"] = (SWEBENCH_VERIFIED["scaffold_low"],
                                         SWEBENCH_VERIFIED["scaffold_high"])
v["scaffold_ratio"] = v["scaffold_high"] / v["scaffold_low"]      # 同一个模型，换个脚手架
assert v["ver_subset_ratio"] > 1.9 and v["scaffold_ratio"] > 9, \
    "子集换一个差一倍，脚手架换一个差十倍——所以不写清口径的分数没有意义"
v["mbpp_total"], v["mbpp_test"] = MBPP["total"], MBPP["test"]
v["mbpp_gives_tests"] = MBPP["gives_tests_in_prompt"]
assert v["mbpp_gives_tests"], "MBPP 默认把 3 个断言交给模型，HumanEval 不给——两者不可直接比"

out(**v)
