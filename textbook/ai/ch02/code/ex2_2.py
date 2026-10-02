"""算例 2.2.1～2.2.3：跑合试验台数据的线性回归（正规方程与梯度下降，标准化前后的收敛速度）；
零件检验数据的逻辑回归。

式 (2.2.3)：正规方程 XᵀX w = Xᵀy；式 (2.2.2)：均方误差的梯度 (2/n) Xᵀ(Xw − y)；
式 (2.2.4)、(2.2.6)、(2.2.7)：σ(z)、交叉熵与它的梯度 (1/n) Xᵀ(p − y)。
"""
import numpy as np

from _ch2 import PARTS, RIG_TRUE, rig_data
from bookout import out

# ---------------------------------------------------------------- 算例 2.2.1：正规方程
x, y = rig_data()
n = len(x)
X = np.c_[x, np.ones(n)]                          # 增广：每行 (x_i, 1)
w = np.linalg.solve(X.T @ X, X.T @ y)             # 正规方程
w_ls = np.linalg.lstsq(X, y, rcond=None)[0]
assert np.allclose(w, w_ls)
res = y - X @ w
mse = float(res @ res / n)
r2 = 1 - float(res @ res) / float(((y - y.mean()) ** 2).sum())
sigma_hat = float(np.sqrt(res @ res / (n - 2)))
pred50 = float(w @ [50.0, 1.0])
assert abs(res.sum()) < 1e-9 and abs(res @ x) < 1e-6      # 残差与每一列正交

# ---------------------------------------------------------------- 算例 2.2.2：梯度下降，原始特征与标准化特征


def gd_steps(A, t, eta, tol=1e-6, max_steps=2_000_000):
    """均方误差上的梯度下降，直到与最小二乘解的距离小于 tol（相对）。"""
    v_star = np.linalg.lstsq(A, t, rcond=None)[0]
    v = np.zeros(A.shape[1])
    for k in range(1, max_steps + 1):
        v = v - eta * (2 / len(t)) * A.T @ (A @ v - t)
        if np.linalg.norm(v - v_star) <= tol * np.linalg.norm(v_star):
            return k, v
    return None, v


H_raw = 2 / n * X.T @ X
lam_raw = np.linalg.eigvalsh(H_raw)
eta_raw = 1.0 / lam_raw.max()
k_raw, _ = gd_steps(X, y, eta_raw)
mu, sd = x.mean(), x.std()
Xs = np.c_[(x - mu) / sd, np.ones(n)]
H_s = 2 / n * Xs.T @ Xs
lam_s = np.linalg.eigvalsh(H_s)
eta_s = 1.0 / lam_s.max()
k_s, v_s = gd_steps(Xs, y, eta_s)
w_back = np.array([v_s[0] / sd, v_s[1] - v_s[0] * mu / sd])   # 换回原始单位
assert np.allclose(w_back, w, rtol=1e-5)

# ---------------------------------------------------------------- 算例 2.2.3：逻辑回归
P = np.array(PARTS, dtype=float)
Z = np.c_[P[:, :2], np.ones(len(P))]
t = (P[:, 2] > 0).astype(float)                  # 合格为 1，不合格为 0


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


def ce(v, lam=0.0):
    p = sigmoid(Z @ v)
    return float(-np.mean(t * np.log(p) + (1 - t) * np.log(1 - p)) + lam / 2 * v[:2] @ v[:2])


lam = 0.01                                        # 很小的权重衰减（2.7 节），使线性可分时解仍然有限
v = np.zeros(3)
eta_lr = 0.5
losses = []
for k in range(20000):
    p = sigmoid(Z @ v)
    g = Z.T @ (p - t) / len(t) + lam * np.r_[v[:2], 0.0]
    v = v - eta_lr * g
    if k in (0, 99, 999, 19999):
        losses.append(ce(v, lam))
# 梯度用有限差分核对
eps = 1e-6
num = np.array([(ce(v + eps * e, lam) - ce(v - eps * e, lam)) / (2 * eps) for e in np.eye(3)])
ana = Z.T @ (sigmoid(Z @ v) - t) / len(t) + lam * np.r_[v[:2], 0.0]
assert np.allclose(num, ana, atol=1e-8)
acc = float(np.mean((sigmoid(Z @ v) > 0.5) == (t > 0.5)))
p_new = float(sigmoid(np.array([1.5, 1.5, 1.0]) @ v))
p_far = float(sigmoid(np.array([0.3, 0.3, 1.0]) @ v))
p0 = ce(np.zeros(3))
ce_pure = ce(v, 0.0)

out(n=n, w1=w[0], b=w[1], w1_true=RIG_TRUE[0], b_true=RIG_TRUE[1], mse=mse, r2=r2, sigma_hat=sigma_hat, pred50=pred50,
    lam_raw_max=lam_raw.max(), lam_raw_min=lam_raw.min(), cond_raw=lam_raw.max() / lam_raw.min(), k_raw=k_raw,
    cond_s=lam_s.max() / lam_s.min(), k_s=k_s, x_mean=mu, x_sd=sd,
    v1=v[0], v2=v[1], v0=v[2], ce0=p0, ce_end=losses[-1], ce_pure=ce_pure, acc_pct=acc * 100, p_new=p_new, p_far=p_far, lam=lam,
    grad_err=float(np.max(np.abs(num - ana))))
