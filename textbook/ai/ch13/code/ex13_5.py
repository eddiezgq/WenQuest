"""算例 13.5.1—13.5.3：对齐（13.5 节）。

（1）奖励模型就是 Bradley–Terry：由“两两比较”求每个回答的分数。本算例造一批有已知真分数的回答，
    按人类标注的真实一致率加噪声（DPO 论文报告：人与 GPT-4 的一致率约 67%，人与人约 65%），
    看要多少条比较才能把排序排对——这决定了标注要花多少钱。
（2）直接偏好优化为什么能省掉强化学习：在一个三选项的小问题上，把“先学奖励再最大化”的最优策略
    与直接偏好优化的目标函数的最优解算出来，核对两者给出同一个策略
    （$\\pi^*(y) \\propto \\pi_{\\rm ref}(y)\\,e^{r(y)/\\beta}$）。
（3）标注要花多少：按 InstructGPT 公布的数据规模折算每条数据的单价与总价（单价是教材假设，公布的只有条数）。
"""
import numpy as np

from _ch13 import bradley_terry
from bookout import out
from llm_facts import DPO, INSTRUCTGPT, STIENNON_COMPARISONS

v = {}
rng = np.random.default_rng(135)
# ---------- （1）要多少条比较
N_ITEM = 12
true_s = np.sort(rng.normal(0, 1, N_ITEM))[::-1]               # 真分数（从高到低）
v["n_item"] = N_ITEM
v["agree_human"] = DPO["human_vs_human_agree"]
v["agree_gpt4"] = DPO["human_vs_gpt4_agree"]
# 标注噪声：按 Bradley–Terry 的概率翻硬币，再按一致率随机翻转一部分标签
FLIP = 1 - DPO["human_vs_human_agree"] / 100
v["flip_pct"] = FLIP * 100


def sample_pairs(n_pair, seed):
    r = np.random.default_rng(seed)
    out_ = []
    for _ in range(n_pair):
        i, j = r.choice(N_ITEM, 2, replace=False)
        p = 1 / (1 + np.exp(-(true_s[i] - true_s[j])))
        win = i if r.random() < p else j
        lose = j if win == i else i
        if r.random() < FLIP:                                  # 标注者看错了
            win, lose = lose, win
        out_.append((win, lose))
    return out_


def spearman(a, b):
    ra, rb = np.argsort(np.argsort(-a)), np.argsort(np.argsort(-b))
    return float(np.corrcoef(ra, rb)[0, 1])


for n_pair in (50, 200, 1000, 5000):
    rhos = [spearman(true_s, bradley_terry(sample_pairs(n_pair, s), N_ITEM)) for s in range(5)]
    v[f"rho_{n_pair}"] = float(np.mean(rhos))
    v[f"rho_{n_pair}_sd"] = float(np.std(rhos))
v["pairs_for_09"] = min(n for n in (50, 200, 1000, 5000) if v[f"rho_{n}"] >= 0.9)
v["rho_gain"] = v["rho_5000"] - v["rho_50"]
# 噪声的代价：同样 1000 条比较，没有标注噪声时能排到多准
FLIP0 = FLIP
FLIP = 0.0
v["rho_1000_clean"] = float(np.mean([spearman(true_s, bradley_terry(sample_pairs(1000, s), N_ITEM))
                                     for s in range(5)]))
FLIP = FLIP0
v["noise_cost"] = v["rho_1000_clean"] - v["rho_1000"]

# ---------- （2）两条路给出同一个策略
BETA = 0.5
v["beta"] = BETA
r = np.array([0.0, 1.0, 2.0])                                  # 三个回答的奖励
pi_ref = np.array([0.5, 0.3, 0.2])                             # 参考策略（监督微调之后的模型）
v["r"], v["pi_ref"] = list(r), list(pi_ref)
# 路线一：有了奖励之后，带 KL 约束的最优策略有闭式解
w = pi_ref * np.exp(r / BETA)
pi_star = w / w.sum()
v["pi_star"] = [float(x) for x in pi_star]
# 路线二：直接偏好优化。它的隐含奖励是 β·log(π/π_ref)，在同样的偏好数据上最大化对数似然；
# 这里直接对 π 做带约束的梯度上升，看是否收敛到同一个分布
pairs = [(i, j) for i in range(3) for j in range(3) if r[i] > r[j]]
logit = np.zeros(3)
for _ in range(20000):
    pi = np.exp(logit) / np.exp(logit).sum()
    g = np.zeros(3)
    for i, j in pairs:
        # 偏好概率 σ(β log(π_i/π_ref_i) − β log(π_j/π_ref_j))
        z = BETA * (np.log(pi[i] / pi_ref[i]) - np.log(pi[j] / pi_ref[j]))
        p = 1 / (1 + np.exp(-z))
        true_p = 1 / (1 + np.exp(-(r[i] - r[j])))              # 数据里这一对的真实偏好概率
        g[i] += (true_p - p) * BETA
        g[j] -= (true_p - p) * BETA
    logit += 0.5 * (g - g.mean())
pi_dpo = np.exp(logit) / np.exp(logit).sum()
v["pi_dpo"] = [float(x) for x in pi_dpo]
v["dpo_max_diff"] = float(np.abs(pi_dpo - pi_star).max())
assert v["dpo_max_diff"] < 2e-3, "两条路线应当给出同一个策略；差这么多说明推导或实现有错"
v["kl_star"] = float(np.sum(pi_star * np.log(pi_star / pi_ref)))
v["gain_star"] = float(pi_star @ r - pi_ref @ r)               # 奖励涨了多少，代价是上面那个 KL

# ---------- （3）标注的账
PRICE_PER_COMPARISON, PRICE_PER_DEMO = 1.0, 3.0                # 教材假设的单价（美元），公布的只有条数
v["sft_prompts"], v["rm_prompts"], v["ppo_prompts"] = (INSTRUCTGPT["sft_prompts"],
                                                       INSTRUCTGPT["rm_prompts"],
                                                       INSTRUCTGPT["ppo_prompts"])
v["labelers"] = INSTRUCTGPT["labelers"]
v["price_cmp"], v["price_demo"] = PRICE_PER_COMPARISON, PRICE_PER_DEMO
K = 4                                                          # 每个提示采 K 个回答，两两比较 C(K,2) 次
v["k_resp"] = K
v["cmp_total"] = INSTRUCTGPT["rm_prompts"] * K * (K - 1) // 2
v["cost_demo_k"] = INSTRUCTGPT["sft_prompts"] * PRICE_PER_DEMO / 1e3
v["cost_cmp_k"] = v["cmp_total"] * PRICE_PER_COMPARISON / 1e3
v["cost_total_k"] = v["cost_demo_k"] + v["cost_cmp_k"]
v["stiennon_cmp"] = STIENNON_COMPARISONS
v["win_vs_gpt3"], v["win_err"] = INSTRUCTGPT["win_vs_gpt3"]
v["win_vs_fewshot"], v["win_fs_err"] = INSTRUCTGPT["win_vs_fewshot"]
v["small"], v["big"] = INSTRUCTGPT["params"][0] / 1e9, INSTRUCTGPT["params"][2] / 1e9
v["param_ratio"] = INSTRUCTGPT["params"][2] / INSTRUCTGPT["params"][0]
# 对齐阶段的算力有多少：按每条约 500 个词元、强化学习阶段每个提示采 4 个回答粗估，与预训练的 6ND 比
TOK_PER_ITEM, N_PARAM, PRETRAIN_FLOPS = 500, 175e9, 3.15e23
align_tokens = (INSTRUCTGPT["sft_prompts"] + v["cmp_total"] + INSTRUCTGPT["ppo_prompts"] * K) * TOK_PER_ITEM
v["align_tokens_M"] = align_tokens / 1e6
v["align_flops"] = 6 * N_PARAM * align_tokens
v["align_share_pct"] = v["align_flops"] / PRETRAIN_FLOPS * 100   # 占预训练算力的百分之几
v["dpo_win"] = DPO["tldr_win"]
out(**v)
