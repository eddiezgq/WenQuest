"""算例 M3.6.1—M3.6.3：采样与蒙特卡洛（M3.6 节）。

"算不出来就抽样算"是人工智能里的常用手段：生成模型按概率抽词（第 13 章）、
投票法用多次采样提高正确率（13.7 节）、强化学习用轨迹的样本估期望（第 14 章）。
本程序讲三件事：怎样从一个分布里抽样、蒙特卡洛估计的误差怎样随样本数下降、
以及"多抽几次再投票"能把正确率提到多高（这就是 13.7 节那条曲线的来历）。
"""
import numpy as np

from _chM3 import rng
from bookout import out

v = {}
g = rng(6)
# ---------- （1）按给定的概率抽样：逆变换法
p = np.array([0.55, 0.30, 0.15])
cum = np.cumsum(p)
u = g.random(100000)
draw = np.searchsorted(cum, u)                                 # 逆变换：均匀随机数落在哪一段
hit = np.bincount(draw, minlength=3) / len(u)
v["p"] = [round(float(a), 2) for a in p]
v["hit"] = [round(float(a), 4) for a in hit]
v["hit_err"] = float(np.abs(hit - p).max())
assert v["hit_err"] < 0.005

# ---------- （2）蒙特卡洛：误差按 1/√n
TRUE = float((p * np.array([1.0, 2.5, 4.0])).sum())            # 三类缺陷的平均返工工时
cost = np.array([1.0, 2.5, 4.0])
v["true_mean"] = TRUE
for n in (100, 1000, 10000, 100000):
    est = np.array([cost[np.searchsorted(cum, g.random(n))].mean() for _ in range(200)])
    v[f"mc_sd_{n}"] = float(est.std(ddof=1))
    v[f"mc_err_{n}"] = float(np.abs(est - TRUE).mean())
v["mc_ratio"] = v["mc_sd_100"] / v["mc_sd_10000"]              # n 大 100 倍，波动小 10 倍
v["sqrt100"] = 10.0
assert 7 < v["mc_ratio"] < 14, "蒙特卡洛的误差按 1/√n 下降"
v["n_for_1pct"] = int(np.ceil((float(np.sqrt((p * (cost - TRUE) ** 2).sum())) / (0.01 * TRUE)) ** 2))

# ---------- （3）多数投票：抽 k 次取多数，正确率能提到多少
def vote_acc(acc1: float, k: int, trials: int = 20000) -> float:
    """每次独立正确的概率是 acc1，抽 k 次（k 为奇数）取多数，正确率是多少。"""
    wins = g.random((trials, k)) < acc1
    return float((wins.sum(axis=1) > k / 2).mean())


from math import comb                                            # noqa: E402（放在这里是为了与上面的采样对照）


def vote_exact(acc1: float, k: int) -> float:
    """同一件事的闭式解：二项分布尾和。采样是为了说明做法，闭式解用来核对。"""
    return sum(comb(k, i) * acc1 ** i * (1 - acc1) ** (k - i) for i in range(k // 2 + 1, k + 1))


for a in (0.45, 0.55, 0.70):
    for k in (1, 5, 21, 51):
        exact = vote_exact(a, k) * 100
        v[f"vote_{int(a * 100)}_{k}"] = exact
        if k <= 21:                                                # 采样与闭式解核对（k 大时采样太慢）
            assert abs(vote_acc(a, k) * 100 - exact) < 1.5, "采样估计应当接近闭式解"
v["vote_gain_55"] = v["vote_55_51"] - v["vote_55_1"]
assert v["vote_45_51"] < v["vote_45_1"], "单次低于一半时，投票只会更糟"
assert v["vote_70_51"] > 99, "单次 70% 时，投 51 次几乎必对"
# 投票的代价：k 倍的运算量换这些百分点
v["k"] = 51
v["cost_x"] = 51
out(**v)
