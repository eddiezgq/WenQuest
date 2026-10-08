"""算例 M3.4.1—M3.4.3：最大似然——交叉熵损失是从哪来的（M3.4 节）。

第 2 章直接给出了交叉熵损失，说它"来自概率"。这里把那一步补上：
（1）伯努利的对数似然取负、除以 n，正好就是式 (2.2.6) 的交叉熵；它的最大值点是样本比例。
（2）高斯（方差固定）的负对数似然，正好就是平方误差——这解释了为什么回归默认用平方误差。
（3）用程序扫一遍参数，看似然的峰与解析解重合，并核对梯度（M2.7 节那条"预测减真值"）。
"""
import numpy as np

from _chM3 import P_BAD, rng
from bookout import out

v = {}
g = rng(4)
n = 400
x = (g.random(n) < P_BAD).astype(float)
k = int(x.sum())
v["n"], v["k"] = n, k
v["p_hat"] = k / n                                            # 解析解：样本比例

# ---------- （1）伯努利：扫一遍 p，看负对数似然的最低点
ps = np.linspace(1e-4, 0.3, 300000)
nll = -(k * np.log(ps) + (n - k) * np.log(1 - ps)) / n        # 每样本的负对数似然 = 交叉熵
i = int(np.argmin(nll))
v["p_grid"] = float(ps[i])
v["nll_min"] = float(nll[i])
assert abs(v["p_grid"] - v["p_hat"]) < 1e-3, "扫出来的最低点应当就是样本比例"
# 这个最小值正是数据的"熵"（M4.1 节会给它名字）
q = v["p_hat"]
v["entropy"] = float(-(q * np.log(q) + (1 - q) * np.log(1 - q)))
assert abs(v["entropy"] - v["nll_min"]) < 1e-6
# 用真实的 p 算一遍交叉熵：一定不比用 p̂ 小
v["nll_true"] = float(-(k * np.log(P_BAD) + (n - k) * np.log(1 - P_BAD)) / n)
v["gap"] = v["nll_true"] - v["nll_min"]
assert v["gap"] >= -1e-12

# ---------- （2）高斯：负对数似然就是平方误差
MU, SD = 35.0, 0.012
z = g.normal(MU, SD, n)
mus = np.linspace(MU - 0.01, MU + 0.01, 200001)
sse = ((z[None, :] - mus[:, None]) ** 2).sum(axis=1)
j = int(np.argmin(sse))
v["mu_grid"] = float(mus[j])
v["mu_hat"] = float(z.mean())
assert abs(v["mu_grid"] - v["mu_hat"]) < 1e-6, "平方误差最小的点就是样本均值"
# 负对数似然与平方误差只差一个与 μ 无关的常数
nll_g = 0.5 * sse / SD ** 2 + n * np.log(SD * np.sqrt(2 * np.pi))
v["nll_gauss_min"] = float(nll_g.min())
v["const_part"] = float(n * np.log(SD * np.sqrt(2 * np.pi)))
v["same_argmin"] = bool(int(np.argmin(nll_g)) == j)
assert v["same_argmin"]

# ---------- （3）梯度：预测减真值
def ce_grad(p, x):
    """二元交叉熵对 logit 的梯度：σ(z) − y 的平均（式 (2.2.7)、M2.7 节）。"""
    return float(np.mean(p - x))


z0 = 0.0
p0 = 1 / (1 + np.exp(-z0))
h = 1e-6
num = (( -np.mean(x * np.log(1 / (1 + np.exp(-(z0 + h)))) + (1 - x) * np.log(1 - 1 / (1 + np.exp(-(z0 + h))))))
       - (-np.mean(x * np.log(1 / (1 + np.exp(-(z0 - h)))) + (1 - x) * np.log(1 - 1 / (1 + np.exp(-(z0 - h))))))) / (2 * h)
v["grad_ana"] = ce_grad(p0, x)
v["grad_num"] = float(num)
v["grad_err"] = abs(v["grad_ana"] - v["grad_num"])
assert v["grad_err"] < 1e-7
out(**v)
