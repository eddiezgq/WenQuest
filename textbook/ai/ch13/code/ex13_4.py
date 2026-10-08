"""算例 13.4.1—13.4.3：规模定律（13.4 节）。

（1）幂律能不能拟出来：按 Kaplan 给出的形式造一批“实验数据”（加上噪声），用最小二乘在对数坐标上拟合，
    看能不能把指数找回来——这就是读规模定律论文时该有的动作：先问“这条直线是怎么拟的”。
（2）外推有多准：只用小模型的点拟合，再外推到大 10 倍、100 倍的规模，看误差有多大。
    规模定律的用处就在外推，而外推的误差正是它最容易被过度相信的地方。
（3）给定算力怎样分配：在 $C = 6ND$ 的约束下最小化损失，得到参数与数据的分配比例；
    与 Chinchilla 的配置（按它自己的数折算约 1∶20）和 GPT-3 的实际配置对照。
"""
import numpy as np

from bookout import out
from llm_facts import CHINCHILLA, CHINCHILLA_OPT, GOPHER, GPT3_PARAMS, GPT3_TOKENS, KAPLAN, MMLU_EXPERT

v = {}
rng = np.random.default_rng(134)
A_N, N_C = KAPLAN["alpha_N"], KAPLAN["N_c"]
v["alpha_N"], v["N_c"] = A_N, N_C
v["alpha_D"], v["D_c"] = KAPLAN["alpha_D"], KAPLAN["D_c"]


def loss_of(n):
    return (N_C / n) ** A_N


# ---------- （1）把指数拟回来
NS = np.array([1e6, 3e6, 1e7, 3e7, 1e8, 3e8, 1e9])            # 七个“训练过的模型”
noise = rng.normal(0, 0.01, len(NS))                           # 每个点 1% 的测量噪声
LS = loss_of(NS) * (1 + noise)
a, b = np.polyfit(np.log(NS), np.log(LS), 1)                   # 对数坐标上的直线
v["n_points"] = len(NS)
v["noise_pct"] = 1.0
v["fit_alpha"] = -a                                            # 斜率的相反数就是指数
v["fit_alpha_err"] = abs(-a - A_N) / A_N * 100
v["fit_Nc"] = float(np.exp(b / A_N)) if A_N else 0.0
resid = np.log(LS) - (a * np.log(NS) + b)
v["fit_rms_pct"] = float(np.sqrt((resid ** 2).mean())) * 100
# 幂律的含义：规模每翻一倍，损失乘上 2^(−α)
v["per_double"] = (1 - 2 ** (-A_N)) * 100
v["per_10x"] = (1 - 10 ** (-A_N)) * 100
v["need_for_half"] = 2 ** (1 / A_N)                            # 损失减半要把模型放大多少倍

# ---------- （2）外推有多准
SMALL = NS <= 1e7                                              # 只用前三个点（≤ 1000 万参数）拟合
a2, b2 = np.polyfit(np.log(NS[SMALL]), np.log(LS[SMALL]), 1)
v["n_small"] = int(SMALL.sum())
v["small_alpha"] = -a2
for mult, key in ((100, "x100"), (10_000, "x10k")):
    n_big = 1e7 * mult
    pred = np.exp(a2 * np.log(n_big) + b2)
    true = loss_of(n_big)
    v[f"extra_{key}_pred"] = float(pred)
    v[f"extra_{key}_true"] = float(true)
    v[f"extra_{key}_err"] = abs(pred - true) / true * 100
v["extra_warn"] = v["extra_x10k_err"] > v["extra_x100_err"]
assert v["extra_warn"], "外推越远误差越大，这个结论不能靠手写"

# ---------- （3）算力怎样分配
# 在 C = 6ND 下最小化 L(N, D) = [(N_c/N)^(α_N/α_D) + D_c/D]^α_D（Kaplan 的联合式）
def joint_loss(n, d):
    return ((N_C / n) ** (A_N / KAPLAN["alpha_D"]) + KAPLAN["D_c"] / d) ** KAPLAN["alpha_D"]


def best_split(C):
    """给定总算力 C（FLOP），扫一遍参数量，取联合损失最小的那个分配。"""
    ns = np.logspace(7, 13, 400)
    ds = C / (6 * ns)
    ls = joint_loss(ns, ds)
    i = int(np.argmin(ls))
    return ns[i], ds[i], ls[i]


for C, key in ((1e21, "c21"), (1e23, "c23"), (1e25, "c25")):
    n_, d_, l_ = best_split(C)
    v[f"{key}_N_B"] = n_ / 1e9
    v[f"{key}_D_B"] = d_ / 1e9
    v[f"{key}_ratio"] = d_ / n_                                # 每个参数配几个词元
    v[f"{key}_loss"] = float(l_)
v["kaplan_N_exp"], v["kaplan_D_exp"] = KAPLAN["N_exp"], KAPLAN["D_exp"]

# 与两篇论文的实际配置对照
v["chin_params_B"], v["chin_tokens_T"] = CHINCHILLA["params"] / 1e9, CHINCHILLA["tokens"] / 1e12
v["chin_ratio"] = CHINCHILLA["tokens"] / CHINCHILLA["params"]  # 1.4T / 70B = 20
v["gopher_params_B"], v["gopher_tokens_B"] = GOPHER["params"] / 1e9, GOPHER["tokens"] / 1e9
v["gopher_ratio"] = GOPHER["tokens"] / GOPHER["params"]
v["chin_mmlu"], v["gopher_mmlu"] = CHINCHILLA["mmlu"], GOPHER["mmlu"]
v["mmlu_gain"] = CHINCHILLA["mmlu"] - GOPHER["mmlu"]
v["mmlu_expert"] = MMLU_EXPERT
v["chin_flops"] = 6 * CHINCHILLA["params"] * CHINCHILLA["tokens"]
v["gopher_flops"] = 6 * GOPHER["params"] * GOPHER["tokens"]
v["flops_ratio"] = v["chin_flops"] / v["gopher_flops"]         # 算力相近，分配不同
v["gpt3_ratio"] = GPT3_TOKENS / GPT3_PARAMS[-1]
v["gpt3_opt_T"] = CHINCHILLA_OPT[175e9] / 1e12
v["gpt3_params_B"] = GPT3_PARAMS[-1] / 1e9
# 同样的算力，按 1∶20 配置应该训多大的模型
v["gpt3_flops"] = 6 * GPT3_PARAMS[-1] * GPT3_TOKENS
n_eq = (v["gpt3_flops"] / (6 * 20)) ** 0.5                     # 6 N (20N) = C → N = sqrt(C/120)
v["gpt3_equal_N_B"] = n_eq / 1e9
v["gpt3_equal_D_T"] = 20 * n_eq / 1e12
out(**v)
