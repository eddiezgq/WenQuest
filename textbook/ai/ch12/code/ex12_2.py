"""算例 12.2.1—12.2.2：隐马尔可夫模型与维特比解码（12.2 节）。

端到端方法出现之前，语音识别是一条流水线：特征 → 声学模型（每帧属于哪个音素状态的概率，用高斯混合模型算）
→ 隐马尔可夫模型把状态按时间串起来 → 配合发音词典与语言模型解码出词序列。
本程序用一个三音素（a、s、i）、每音素一个状态的玩具例子，把维特比解码算清楚：

（1）手算核对：给定 4 帧的观测似然与转移概率，枚举全部 3⁴ 条路径求最优，与维特比的结果比较；
（2）为什么要维特比：枚举的代价是 S^T，维特比是 T·S²——帧数一多，两者差出天文数字。
（3）自环的作用：同一个音素要占好几帧，所以每个状态都有一条指向自己的边；自环概率决定音素的典型时长。
"""
import itertools

import numpy as np

from _ch12 import viterbi
from bookout import out

rng = np.random.default_rng(12)
PHONES = ["a", "s", "i"]
S, T = len(PHONES), 4
obs = np.log(rng.dirichlet(np.ones(S), T))                   # 每帧在各状态上的似然（取对数）
trans = np.log(np.array([[0.6, 0.3, 0.1],                    # 自环 0.6：一个音素平均持续 1/(1−0.6) = 2.5 帧
                         [0.1, 0.6, 0.3],
                         [0.1, 0.2, 0.7]]))
init = np.log(np.array([0.6, 0.3, 0.1]))

path, lp = viterbi(obs, trans, init)
best, best_lp = None, -np.inf
for p in itertools.product(range(S), repeat=T):              # 枚举全部路径
    s = init[p[0]] + obs[0, p[0]]
    for t in range(1, T):
        s += trans[p[t - 1], p[t]] + obs[t, p[t]]
    if s > best_lp:
        best, best_lp = list(p), s
assert path == best and abs(lp - best_lp) < 1e-12, (path, best)

v = {"S": S, "T": T, "path": "".join(PHONES[i] for i in path), "logp": lp, "same": True}
v["enum_paths"] = S ** T
v["viterbi_ops"] = T * S * S
# 一秒的语音（100 帧）、一个中等词表的声学模型（约 3000 个状态）
FRAMES, STATES = 100, 3000
v["frames"], v["states"] = FRAMES, STATES
v["enum_exp"] = FRAMES * np.log10(STATES)                    # 枚举路径数的数量级（10 的几次方）
v["viterbi_ops_real"] = FRAMES * STATES * STATES
v["viterbi_Gops"] = FRAMES * STATES * STATES / 1e9
# 自环概率与时长
for p in (0.5, 0.6, 0.8, 0.9):
    v[f"dur_{int(p * 100)}"] = 1 / (1 - p)                   # 平均持续多少帧
    v[f"ms_{int(p * 100)}"] = 1 / (1 - p) * 10               # 每帧 10 ms
out(**v)
