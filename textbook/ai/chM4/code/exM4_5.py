"""算例 M4.5.1—M4.5.3：数值稳定的写法（M4.5 节）。

三个在训练里天天遇到的问题，各有一个标准解法：
（1）softmax 与交叉熵直接算会上溢或下溢 → 先减最大值（logsumexp）；
（2）概率连乘会下溢到 0 → 在对数域里相加；
（3）梯度偶尔很大把参数带飞 → 梯度裁剪。
每一条都给出"错写法"与"对写法"的数值对照。
"""
import numpy as np

from _chM4 import logsumexp, softmax
from bookout import out

v = {}
# ---------- （1）softmax 的上溢与下溢
z = np.array([1000.0, 1001.0, 1002.0])
with np.errstate(over="ignore", invalid="ignore"):
    naive = np.exp(z) / np.exp(z).sum()
v["naive_nan"] = bool(np.isnan(naive).any())
good = softmax(z)
v["good"] = [round(float(a), 4) for a in good]
assert v["naive_nan"] and abs(good.sum() - 1) < 1e-12, "直接算会溢出，减最大值就不会"
z2 = np.array([-1000.0, -1001.0, -1002.0])                  # 另一头：全都下溢成 0，分母为 0
with np.errstate(invalid="ignore"):
    naive2 = np.exp(z2) / np.exp(z2).sum()
v["naive2_nan"] = bool(np.isnan(naive2).any())
v["good2"] = [round(float(a), 4) for a in softmax(z2)]
assert v["naive2_nan"]

# ---------- （2）交叉熵：先 softmax 再取对数，还是直接用 logits
rng = np.random.default_rng(45)
K = 1000
logits = rng.normal(0, 40, K).astype(np.float32)             # 单精度、尺度大一点就会出问题（训练里就是这样）
t = 7                                                       # 真实类别
p_naive = np.exp(logits - logits.max(), dtype=np.float32)
p_naive = p_naive / p_naive.sum()
with np.errstate(divide="ignore"):
    ce_naive = float(-np.log(p_naive[t]))                   # 先算概率再取对数：概率下溢成 0 就是 inf
ce_good = float(logsumexp(logits.astype(np.float64)) - float(logits[t]))   # 直接用 logits：永远有限
v["ce_naive"] = ce_naive
v["ce_good"] = ce_good
v["ce_naive_inf"] = bool(np.isinf(ce_naive))
v["p_true"] = float(p_naive[t])
assert v["ce_naive_inf"] and np.isfinite(ce_good), "带 logits 的交叉熵不会变成无穷"

# ---------- （3）概率连乘：对数域
probs = rng.uniform(0.01, 0.2, 400)                         # 四百个词元的概率连乘（一句话的似然）
v["n_prob"] = len(probs)
prod = float(np.prod(probs))
log_sum = float(np.sum(np.log(probs)))
v["prod"] = prod
v["prod_zero"] = prod == 0.0
v["log_sum"] = log_sum
v["log_sum_e"] = log_sum / np.log(10)                       # 相当于 10 的多少次方
assert v["prod_zero"], "四百个小于 1 的数连乘，双精度下已经下溢成 0"

# ---------- （4）梯度裁剪
g = rng.normal(0, 1, 1000)
g[17] = 500.0                                               # 偶尔来一个很大的梯度（坏样本、学习率没热身）
norm = float(np.linalg.norm(g))
CLIP = 5.0
scale = min(1.0, CLIP / norm)
gc = g * scale
v["gnorm"], v["clip"] = norm, CLIP
v["gnorm_after"] = float(np.linalg.norm(gc))
v["shrink"] = scale
v["step_before"] = norm * 0.1                               # 学习率 0.1 时这一步走多远
v["step_after"] = v["gnorm_after"] * 0.1
v["dir_cos"] = float(g @ gc / (np.linalg.norm(g) * np.linalg.norm(gc)))
assert abs(v["dir_cos"] - 1) < 1e-12, "裁剪只改长度、不改方向"
out(**v)
