"""算例 17.6.1—17.6.3：怎么评一个会动手的东西，以及防护侧的账（17.6 节）。

（1）评一个智能体，光看"做对了没有"不够：还要看它做了什么、代价多大、错的时候错成什么样。
（2）pass@k 与 pass^k 是方向相反的两个量；把它们并排算一遍，就不会再混。
（3）防护侧的账：把高风险动作交给人确认，拦住了多少、又拦掉了多少本来没问题的。
     本节只讲防护，不给任何可用于构造攻击的内容。
"""
import numpy as np

from _ch17 import pass_at_k
from agent_facts import OWASP_LLM, PROMPT_INJECTION, TAU_BENCH
from bookout import out

v = {}

# ---------- （1）（2）pass@k 与 pass^k：方向相反
# 同一组题、同一个模型：每题采 n 次，c 次成功。
N, TRIALS = 20, 4000
g = np.random.default_rng(0)
v["n_samples"] = N
v["cmp_rows"] = []
for p in (0.3, 0.5, 0.8):
    cs = g.binomial(N, p, TRIALS)
    for k in (1, 2, 4, 8):
        at_k = float(np.mean([pass_at_k(N, int(c), k) for c in cs]))
        # pass^k：k 次独立重跑全部成功
        hat_k = float(np.mean([0.0 if c < k else np.prod([(c - i) / (N - i) for i in range(k)])
                               for c in cs]))
        v["cmp_rows"].append((p, k, round(at_k, 3), round(hat_k, 3)))
        v[f"at_p{int(p * 100)}_k{k}"] = round(at_k, 3)
        v[f"hat_p{int(p * 100)}_k{k}"] = round(hat_k, 3)
assert v["at_p50_k8"] > v["at_p50_k1"], "pass@k 随 k 单调上升（k 次里有一次成功）"
assert v["hat_p50_k8"] < v["hat_p50_k1"], "pass^k 随 k 单调下降（k 次全要成功）"
v["spread_k8"] = v["at_p50_k8"] - v["hat_p50_k8"]
assert v["spread_k8"] > 0.9, "同一个模型、同一组题，两个指标能差到天上地下"
v["tau_at_formula"], v["tau_hat_formula"] = (TAU_BENCH["pass_at_k_formula"],
                                             TAU_BENCH["pass_k_formula"])
v["tau_pass8"] = TAU_BENCH["pass8_gpt4o_retail_below"]
v["tau_retail_tasks"], v["tau_tools"] = TAU_BENCH["retail_tasks"], TAU_BENCH["retail_tools"]
v["tau_gpt4o_retail"] = TAU_BENCH["pass1"]["gpt-4o"][0]
v["tau_agent_temp"], v["tau_user_temp"] = TAU_BENCH["agent_temp"], TAU_BENCH["user_temp"]

# ---------- （3）人工确认这道闸的账
# 一批动作里有 base 的比例是高风险的；闸门按"看起来危险"拦下来，它也会误拦。
def gate(n_actions: int, risky_frac: float, tpr: float, fpr: float, seed: int = 0):
    """返回 (拦住的高风险动作占高风险总数的比例, 被误拦的正常动作占正常总数的比例,
    要人看的动作占全部的比例)。"""
    g2 = np.random.default_rng(3000 + seed)
    risky = g2.random(n_actions) < risky_frac
    stopped = np.where(risky, g2.random(n_actions) < tpr, g2.random(n_actions) < fpr)
    return (float(stopped[risky].mean()), float(stopped[~risky].mean()), float(stopped.mean()))


N_ACT, RISKY = 20000, 0.03
v["n_actions"], v["risky_frac_pct"] = N_ACT, RISKY * 100
v["gate_rows"] = []
for tpr, fpr in ((0.99, 0.30), (0.99, 0.05), (0.90, 0.01), (0.60, 0.00)):
    caught, mis, load = gate(N_ACT, RISKY, tpr, fpr)
    v["gate_rows"].append((tpr, fpr, round(caught * 100, 1), round(mis * 100, 1),
                           round(load * 100, 1)))
    tag = f"{int(tpr * 100)}_{int(fpr * 100)}"
    v[f"caught_{tag}"], v[f"mis_{tag}"], v[f"load_{tag}"] = (round(caught * 100, 1),
                                                             round(mis * 100, 1),
                                                             round(load * 100, 1))
assert v["load_99_30"] > 3.5 * v["load_99_5"], \
    "误拦率从 30% 降到 5%，要人看的量就降了好几倍——而拦住的高风险动作一个没少"
v["load_drop"] = v["load_99_30"] / v["load_99_5"]
assert v["caught_60_0"] < v["caught_99_5"], "闸门太松就拦不住"
# 一天跑多少次动作，人要看多少次
PER_DAY = 2000
v["per_day"] = PER_DAY
v["human_per_day_loose"] = round(PER_DAY * v["load_99_30"] / 100)
v["human_per_day_tight"] = round(PER_DAY * v["load_99_5"] / 100)
v["missed_per_day"] = round(PER_DAY * RISKY * (1 - 0.99), 1)
assert v["human_per_day_tight"] < 200, "这才是一个人盯得过来的量"
v["human_per_day_tighter"] = round(PER_DAY * v["load_90_1"] / 100)

# ---------- 防护侧的公开事实（只列条目，不展开）
v["owasp_version"] = OWASP_LLM["version"]
v["owasp_items"] = OWASP_LLM["items"]
v["owasp_agent_items"] = OWASP_LLM["closest_to_agents"]
v["pi_def"] = PROMPT_INJECTION["owasp_def"]
v["pi_direct"], v["pi_indirect"] = PROMPT_INJECTION["direct"], PROMPT_INJECTION["indirect"]
v["pi_defenses"] = PROMPT_INJECTION["defenses"]
v["pi_n_defenses"] = len(PROMPT_INJECTION["defenses"])
v["pi_no_silver"] = PROMPT_INJECTION["no_silver_bullet"]
v["pi_source"] = PROMPT_INJECTION["ipi_source"]
assert v["pi_n_defenses"] == 7, "照原文列七条"

out(**v)
