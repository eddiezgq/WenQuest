"""算例 M3.3.1—M3.3.2：常见分布与它们在模型里的位置（M3.3 节）。

机器学习里反复出现的就那么几个分布，而且每一个都对应一种输出层与一种损失：
伯努利 ↔ sigmoid ↔ 二元交叉熵；类别分布 ↔ softmax ↔ 交叉熵；高斯 ↔ 恒等输出 ↔ 平方误差。
本程序把这组对应关系算出来：同一批数据，用对应的损失拟合，参数的最大似然估计正是样本的统计量。
"""
import numpy as np

from _chM3 import P_BAD, rng
from bookout import out

v = {}
g = rng(3)
# ---------- 伯努利：均值就是 p
n = 5000
x = (g.random(n) < P_BAD).astype(float)
v["n"] = n
v["bern_mle"] = float(x.mean())
v["bern_true"] = P_BAD
v["bern_var"] = float(P_BAD * (1 - P_BAD))
v["bern_var_hat"] = float(x.var())

# ---------- 类别分布（三类缺陷的比例）
probs = np.array([0.55, 0.30, 0.15])                          # 划痕、压痕、锈斑（第 11 章的三类）
y = g.choice(3, size=n, p=probs)
counts = np.bincount(y, minlength=3)
v["cat_true"] = [round(float(a), 3) for a in probs]
v["cat_mle"] = [round(float(a), 4) for a in counts / n]
v["cat_err"] = float(np.abs(counts / n - probs).max())
assert v["cat_err"] < 0.02

# ---------- 高斯：均值与方差的最大似然就是样本均值与（有偏的）样本方差
MU, SD = 35.0, 0.012                                          # 外径（mm），与 M1 章同一批零件的量级
z = g.normal(MU, SD, n)
v["gauss_mu"], v["gauss_sd"] = MU, SD
v["gauss_mu_hat"] = float(z.mean())
v["gauss_sd_hat"] = float(z.std())                            # 最大似然估计用 1/n（有偏）
v["gauss_sd_unb"] = float(z.std(ddof=1))                      # 无偏估计用 1/(n−1)
v["bias_pct"] = (v["gauss_sd_unb"] - v["gauss_sd_hat"]) / v["gauss_sd_hat"] * 100
# 正态的"几个西格玛"：工程上用来定公差
for k in (1, 2, 3):
    v[f"within_{k}"] = float((np.abs(z - MU) < k * SD).mean() * 100)
v["out3_ppm"] = float((np.abs(z - MU) >= 3 * SD).mean() * 1e6)   # 超出 3σ 的件数（每百万）

# ---------- 泊松：稀有事件的计数（每班的停机次数）
LAM = 2.5
k = g.poisson(LAM, n)
v["pois_lam"] = LAM
v["pois_mean"], v["pois_var"] = float(k.mean()), float(k.var())
v["pois_p0"] = float(np.exp(-LAM))                            # 一班一次都不停机的概率
v["pois_p0_hat"] = float((k == 0).mean())
assert abs(v["pois_mean"] - v["pois_var"]) < 0.15, "泊松的期望与方差相等（这是它的标志）"

# ---------- 指数：两次停机之间的间隔（与泊松互为表里）
t = g.exponential(1 / LAM, n)
v["exp_mean"], v["exp_sd"] = float(t.mean()), float(t.std())
v["exp_theory"] = 1 / LAM
assert abs(v["exp_mean"] - v["exp_sd"]) < 0.05, "指数分布的均值与标准差相等"
out(**v)
