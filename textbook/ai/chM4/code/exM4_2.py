"""算例 M4.2.1—M4.2.3：交叉熵、困惑度与语言模型的指标（M4.2 节）。

困惑度就是交叉熵的指数，直观上是"模型平均在多少个词之间犹豫"。本程序算三件事：
（1）在一个小词表上，真实分布的熵、模型的交叉熵与困惑度；
（2）困惑度随训练数据增多怎样降，以及它的下界（数据本身的熵）；
（3）两个常见的坑：换了词表或分词方式，困惑度不可比；给某个词 0 概率，困惑度是无穷。
"""
import numpy as np

from _chM4 import toy_lm
from bookout import out

v = {}
p, q, tokens = toy_lm()
v["vocab"] = len(p)
v["n_tokens"] = len(tokens)
H = float(-(p * np.log(p)).sum())
CE = float(-(p * np.log(q)).sum())
v["H_nat"], v["CE_nat"] = H, CE
v["H_bits"], v["CE_bits"] = H / np.log(2), CE / np.log(2)
v["KL"] = CE - H
v["ppl_true"] = float(np.exp(H))                            # 真实分布的困惑度：下界
v["ppl_model"] = float(np.exp(CE))
v["ppl_uniform"] = float(len(p))                            # 完全不会时：在整个词表之间犹豫
v["ppl_gap"] = v["ppl_model"] - v["ppl_true"]

# ---------- （2）数据越多，模型越准，困惑度越接近下界
for n in (200, 1000, 5000, 50000):
    _, q_n, _ = toy_lm(n=n)
    ce = float(-(p * np.log(q_n)).sum())
    v[f"ppl_{n}"] = float(np.exp(ce))
    v[f"ce_{n}"] = ce
assert v["ppl_200"] > v["ppl_50000"] > v["ppl_true"], "数据越多越接近下界，但永远到不了"
v["ppl_floor_pct"] = (v["ppl_50000"] - v["ppl_true"]) / v["ppl_true"] * 100

# ---------- （3）两个坑
# 坑一：词表变了，困惑度不可比。把词表对半合并（相当于更粗的分词），困惑度立刻变小
half = p.reshape(-1, 2).sum(axis=1)
v["vocab_half"] = len(half)
v["ppl_half"] = float(np.exp(-(half * np.log(half)).sum()))
v["ppl_half_ratio"] = v["ppl_true"] / v["ppl_half"]
# 坑二：零概率
q_bad = q.copy()
q_bad[-1] = 0.0
with np.errstate(divide="ignore", invalid="ignore"):
    ce_bad = float(-(p * np.log(q_bad)).sum())
v["ce_bad_inf"] = bool(np.isinf(ce_bad))
assert v["ce_bad_inf"]
# 平滑之后
eps = 1e-6
q_s = (q_bad + eps) / (q_bad + eps).sum()
v["eps"] = eps
v["ppl_smooth"] = float(np.exp(-(p * np.log(q_s)).sum()))
v["ppl_smooth_up"] = v["ppl_smooth"] - v["ppl_model"]

# ---------- （4）每个词元多少比特：与存储的账对上
v["bits_per_token"] = v["CE_bits"]
v["bytes_1M"] = v["CE_bits"] * 1e6 / 8 / 1024 ** 2          # 一百万个词元按这个交叉熵能压到多少 MB
v["bytes_1M_fixed"] = int(np.ceil(np.log2(len(p)))) * 1e6 / 8 / 1024 ** 2
out(**v)
