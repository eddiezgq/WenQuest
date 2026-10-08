"""算例 M3.7.1—M3.7.3：估计的不确定性——为什么评测要报区间（M3.7 节）。

在 200 道题上测出 76% 与 79%，能说后者更好吗？本程序回答这个问题：
（1）比例的置信区间（威尔逊区间）有多宽，与题数的关系；
（2）两个模型的差有没有意义：配对比较比各算各的区间更灵敏；
（3）"在同一批数据上挑最好的那个"会高估多少——这是 13.8 节评测那一节的核心警告。
"""
import numpy as np

from _chM3 import rng, wilson
from bookout import out

v = {}
g = rng(7)
# ---------- （1）区间有多宽
for n in (50, 200, 1000, 10000):
    lo, hi = wilson(int(round(0.76 * n)), n)
    v[f"ci_{n}"] = [round(lo * 100, 1), round(hi * 100, 1)]
    v[f"w_{n}"] = (hi - lo) * 100
v["w_ratio"] = v["w_200"] / v["w_1000"]                        # 题数 ×5，区间宽约 1/√5
v["sqrt5"] = float(np.sqrt(5))
# 要把区间压到 ±1 个百分点，要多少题
z, p = 1.96, 0.76
v["n_for_1pt"] = int(np.ceil(z ** 2 * p * (1 - p) / 0.01 ** 2))

# ---------- （2）76% 对 79%：差得过区间吗
N = 200
a_acc, b_acc = 0.76, 0.79
v["N"], v["a_pct"], v["b_pct"] = N, a_acc * 100, b_acc * 100
la, ha = wilson(int(a_acc * N), N)
lb, hb = wilson(int(b_acc * N), N)
v["ci_a"] = [round(la * 100, 1), round(ha * 100, 1)]
v["ci_b"] = [round(lb * 100, 1), round(hb * 100, 1)]
v["overlap"] = bool(lb < ha)                                   # 两个区间重叠：单看区间说不出谁好
assert v["overlap"]

# 配对比较：同样的题，看两个模型在各题上的对错
RHO = 0.8                                                      # 两个模型的表现高度相关（错的往往是同几道难题）
def paired(n, pa, pb, rho, trials=20000):
    """相关的对错：共同的难度分量 + 各自的随机分量。返回 B 显著好于 A 的比例（符号检验）。"""
    sig = 0
    for _ in range(trials):
        common = g.random(n)
        ea = (rho * common + (1 - rho) * g.random(n)) < pa
        eb = (rho * common + (1 - rho) * g.random(n)) < pb
        d = int((eb & ~ea).sum()), int((ea & ~eb).sum())        # 只看结论不同的那些题
        m = d[0] + d[1]
        if m == 0:
            continue
        # 正态近似的符号检验：差 ≥ 1.96 个标准差才算显著
        if abs(d[0] - d[1]) / np.sqrt(m) > 1.96 and d[0] > d[1]:
            sig += 1
    return sig / trials * 100


v["paired_sig_pct"] = paired(N, a_acc, b_acc, RHO, trials=3000)
# 要多少题才能稳定地分出 3 个百分点的差（配对，粗估）
v["n_for_3pt"] = int(np.ceil((1.96 / 0.03) ** 2 * 0.2))         # 分歧率约 20% 时的量级

# ---------- （3）在同一批数据上挑最好的：高估多少
K, TRUE = 20, 0.75                                              # 20 个配置，真实水平都是 75%
best, best_true = [], []
for _ in range(2000):
    obs = g.binomial(N, TRUE, K) / N
    i = int(obs.argmax())
    best.append(obs[i])
    best_true.append(TRUE)
v["K"] = K
v["true_acc"] = TRUE * 100
v["best_mean"] = float(np.mean(best) * 100)
v["optimism"] = v["best_mean"] - v["true_acc"]
assert v["optimism"] > 1.0, "在同一批数据上挑最好的，必然高估"
v["best_max"] = float(np.max(best) * 100)
out(**v)
