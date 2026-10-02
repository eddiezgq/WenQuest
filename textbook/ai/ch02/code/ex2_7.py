"""算例 2.7.1～2.7.3：多项式拟合的过拟合；权重衰减（岭回归）；丢弃法的期望；层归一化。

式 (2.7.2)：岭回归 (XᵀX + nλI) w = Xᵀy；式 (2.7.4)：反向丢弃 h̃ = m ⊙ h / (1 − p)；
式 (2.7.5)：层归一化 LN(h) = γ ⊙ (h − μ)/√(σ² + ε) + β。
"""
import numpy as np
from numpy.polynomial import chebyshev as Ch

from _ch2 import poly_data
from bookout import out

xt, yt, xs, ys = poly_data()
n = len(xt)


def design(x, deg):
    return Ch.chebvander(2 * x - 1, deg)          # 切比雪夫多项式基，[0, 1] 映到 [−1, 1]，数值上稳定


def fit(deg, lam=0.0):
    X = design(xt, deg)
    w = np.linalg.solve(X.T @ X + n * lam * np.eye(deg + 1), X.T @ yt)
    tr = float(np.mean((X @ w - yt) ** 2))
    te = float(np.mean((design(xs, deg) @ w - ys) ** 2))
    return w, tr, te


res = {deg: fit(deg) for deg in (1, 3, 9, 14)}
noise_var = 0.15 ** 2
# 岭回归：14 次多项式，不同 λ
lams = [1e-6, 1e-4, 1e-3, 3e-3, 1e-2, 1]
ridge = {lam: fit(14, lam) for lam in lams}
best_lam = min(lams, key=lambda l: ridge[l][2])

# 丢弃法：反向丢弃的期望等于原值
rng = np.random.default_rng(0)
h = np.array([1.0, 2.0, 3.0, 4.0])
p = 0.5
trials = 100000
masks = rng.random((trials, 4)) > p
avg = (masks * h / (1 - p)).mean(axis=0)              # 多次随机丢弃后的平均
max_dev = float(np.max(np.abs(avg - h)))
assert max_dev < 0.05

# 层归一化
v = np.array([2.0, 4.0, 6.0, 8.0])
mu, var = v.mean(), v.var()
ln = (v - mu) / np.sqrt(var + 1e-5)
assert np.allclose(((10 * v) - 10 * mu) / np.sqrt(100 * var + 1e-5), ln, atol=1e-6)   # 对输入整体缩放不敏感

out(n=n, tr1=res[1][1], te1=res[1][2], tr3=res[3][1], te3=res[3][2], tr9=res[9][1], te9=res[9][2],
    tr14=res[14][1], te14=res[14][2], noise_var=noise_var, wmax14=float(np.max(np.abs(res[14][0]))),
    te_r6=ridge[1e-6][2], te_r4=ridge[1e-4][2], te_r3=ridge[1e-3][2], te_r3b=ridge[3e-3][2], te_r2=ridge[1e-2][2], te_r0=ridge[1][2],
    tr_r4=ridge[1e-4][1], best_lam=best_lam, wmax_best=float(np.max(np.abs(ridge[best_lam][0]))),
    avg0=avg[0], avg3=avg[3], max_dev=max_dev, trials=trials, mu=mu, var=var, ln0=ln[0], ln1=ln[1], ln2=ln[2], ln3=ln[3])
