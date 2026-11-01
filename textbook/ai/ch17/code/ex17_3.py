"""算例 17.3.1—17.3.4：智能体的循环，以及错误怎么累积（17.3 节）。

（1）指数衰减：每步出错率 p、走 n 步，成功率是 (1−p)^n。这是恒等式，不是经验规律，
     程序用蒙特卡洛核对一遍，再反过来解出"要保住某个成功率最多能走几步"。
（2）三种救法各买回多少：整件事重试、每步自检、末端校验。
（3）校验器会误判：把对的判成错，是要把好结果扔掉的——这一项常被忘掉。
（4）记忆与缓存的账：每一轮都要把前面所有东西重送一遍，代价怎么长。
"""
import numpy as np

from _ch17 import (memory_cost, plain, simulate_agent, steps_for, with_check, with_retry,
                   with_verifier)
from agent_facts import CACHE, METR, REACT, REFLEXION, STEP_DECAY_SOURCE, TAU_BENCH, TOOLS
from bookout import out

v = {}

# ---------- （1）指数衰减
v["decay_rows"] = []
worst = 0.0
for p in (0.02, 0.05, 0.10):
    for n in (5, 20, 50):
        a, m = plain(p, n), simulate_agent(p, n, 30000)
        v["decay_rows"].append((p, n, round(a, 4), round(m, 4)))
        v[f"ok_p{int(p * 100)}_n{n}"] = round(a, 4)
        worst = max(worst, abs(a - m))
v["decay_max_err"] = worst
assert worst < 0.01, "解析与模拟对得上——(1−p)^n 是恒等式"
v["source_known"] = STEP_DECAY_SOURCE is not None
assert not v["source_known"], \
    "没有任何论文给出'逐步成功率曲线'，所以本书只把它当数学恒等式用，不挂引文"
v["budget_rows"] = []
for p in (0.01, 0.02, 0.05, 0.10, 0.20):
    v["budget_rows"].append((p, round(steps_for(p, 0.8), 1), round(steps_for(p, 0.5), 1)))
    v[f"steps80_p{int(p * 100)}"] = round(steps_for(p, 0.8), 1)
v["steps80_p5"], v["steps80_p1"] = v["steps80_p5"], v["steps80_p1"]
assert v["steps80_p1"] > 4 * v["steps80_p5"], \
    "每步出错率降到五分之一，能走的步数就长五倍——这是本章最值钱的一条"
v["ratio_1_to_5"] = v["steps80_p1"] / v["steps80_p5"]

# ---------- （2）三种救法
P, N = 0.05, 20
v["p_base"], v["n_base"] = P, N
v["base"] = plain(P, N)
v["retry_rows"] = [(t, round(with_retry(P, N, t), 3)) for t in (1, 2, 3, 5)]
v["check_rows"] = [(d, round(with_check(P, N, d), 3)) for d in (0.5, 0.8, 0.95)]
v["verify_rows"] = [(tpr, fpr, round(with_verifier(P, N, tpr, fpr), 3))
                    for tpr, fpr in ((0.8, 0.05), (0.95, 0.05), (0.95, 0.20))]
v["retry3"] = with_retry(P, N, 3)
v["check80"] = with_check(P, N, 0.8)
v["verify_good"] = with_verifier(P, N, 0.95, 0.05)
assert v["check80"] > v["base"] + 0.4, "每步自检买回来的最多"
assert v["retry3"] > v["base"], "整件事重试也有用，但要求失败看得出来、而且能重来"
v["check_gain_pts"] = (v["check80"] - v["base"]) * 100
v["retry_gain_pts"] = (v["retry3"] - v["base"]) * 100
# 每步自检相当于把每步出错率降到多少
v["p_effective"] = 1 - v["check80"] ** (1 / N)
assert v["p_effective"] < P, "自检的作用就是把每一步的有效出错率压下去"

# ---------- （3）校验器误判的代价
v["fp_low"], v["fp_high"] = with_verifier(P, N, 0.95, 0.05), with_verifier(P, N, 0.95, 0.20)
v["fp_cost_pts"] = (v["fp_low"] - v["fp_high"]) * 100
assert v["fp_high"] < v["fp_low"], "把对的判成错，是要把好结果扔掉的"
# 一个极端：校验器很灵敏但误判率高，反而不如不校验
v["fp_worst"] = with_verifier(P, N, 1.0, 0.6)
assert v["fp_worst"] < v["base"] + 0.25, "误判率一高，校验器就开始帮倒忙"

# ---------- （4）记忆与缓存的账
TURNS, PER_TURN = 20, 800
SYS, TOOLS_TOK = 500, 2686
total, rel = memory_cost(TURNS, PER_TURN, TOOLS_TOK, SYS)
v["turns"], v["per_turn"], v["sys_tokens"], v["tool_tokens"] = TURNS, PER_TURN, SYS, TOOLS_TOK
v["total_tokens_w"] = total / 1e4
v["naive_last_turn"] = SYS + TOOLS_TOK + PER_TURN * TURNS
v["cache_rel_price"] = rel
v["cache_write"], v["cache_read"] = CACHE["write_5min"], CACHE["read_default"]
v["cache_ttl_min"] = CACHE["ttl_default_min"]
v["cache_breakpoints"] = CACHE["breakpoints"]
v["cache_min"] = CACHE["min_cacheable"]
v["cache_savings_known"] = CACHE["savings_pct"] is not None
assert not v["cache_savings_known"], "官方只给价格倍数，不给任何'省多少'的百分比"
# 折算：前缀复用 N 次的相对价格 (1.25 + 0.1N)/(N+1)
v["reuse_rows"] = [(n, round((CACHE["write_5min"] + CACHE["read_default"] * n) / (n + 1), 3))
                   for n in (1, 3, 10, 50)]
v["reuse1"], v["reuse10"] = v["reuse_rows"][0][1], v["reuse_rows"][2][1]
assert v["reuse1"] > 0.6, "只复用一次，总价还是全价的六成以上——缓存不是立刻就省"

# ---------- 公开发表的数字（口径见资料卡）
v["react_hotpot_cot"], v["react_hotpot_react"] = REACT["hotpotqa"]["CoT"], REACT["hotpotqa"]["ReAct"]
v["react_hotpot_best"] = REACT["hotpotqa"]["ReAct→CoT-SC"]
assert v["react_hotpot_react"] < v["react_hotpot_cot"], \
    "在这个任务上加了工具反而更低——'加工具就一定涨'是不对的"
v["react_alfworld"], v["react_butler"] = REACT["alfworld_react"], REACT["alfworld_butler"]
v["react_fallback_steps"] = REACT["fallback_steps_hotpotqa"]
v["reflex_solved"], v["reflex_total"] = REFLEXION["alfworld_solved"], REFLEXION["alfworld_total"]
v["reflex_he_before"], v["reflex_he_after"] = REFLEXION["humaneval_py"]
v["reflex_mbpp_before"], v["reflex_mbpp_after"] = REFLEXION["mbpp_py"]
assert v["reflex_mbpp_after"] < v["reflex_mbpp_before"], \
    "同一篇论文里，反思在 MBPP 上反而更低——不能只引 HumanEval 那一行"
v["reflex_fp_he"], v["reflex_fp_mbpp"] = (REFLEXION["false_positive_humaneval"],
                                          REFLEXION["false_positive_mbpp"])
v["reflex_small"] = REFLEXION["small_model"][1] - REFLEXION["small_model"][0]
assert v["reflex_small"] == 0, "底座不够强时，反思一点用都没有"
v["tau_pass8"] = TAU_BENCH["pass8_gpt4o_retail_below"]
v["tau_formula"], v["tau_at_formula"] = TAU_BENCH["pass_k_formula"], TAU_BENCH["pass_at_k_formula"]
v["tau_values_known"] = TAU_BENCH["pass_k_values"] is not None
assert not v["tau_values_known"], "pass^2 到 pass^7 的具体值论文没给"
v["metr_model"] = METR["model"]
v["metr_h50"], v["metr_h80"] = METR["h50_claude37"], METR["h80_claude37"]
v["metr_ratio"] = METR["h80_over_h50"]
v["metr_doubling"] = METR["doubling_days"]
v["everything_counts"] = TOOLS["everything_counts"]

out(**v)
