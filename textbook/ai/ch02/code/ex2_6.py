"""程序 2.6.1：病态二次函数上的梯度下降、动量法与 Adam；算例 2.6.1 小批量随机梯度的噪声；算例 2.6.2 初始化对深层网络各层输出方差的影响。

损失 L(w) = ½ (λ₁ w₁² + λ₂ w₂²)，λ₁ = 1，λ₂ = 100（条件数 κ = 100）。
梯度下降最优学习率 2/(λ₁ + λ₂)，收敛因子 (κ − 1)/(κ + 1)（式 (2.6.2)）；
动量法（重球法）最优参数下收敛因子 (√κ − 1)/(√κ + 1)（式 (2.6.4)）。
"""
import math

import numpy as np

from _ch2 import TINY, rig_data, tiny_params
from bookout import out

lam = np.array([1.0, 100.0])
kappa = lam[1] / lam[0]
w0 = np.array([-5.0, 1.0])
tol = 1e-6


def grad(w):
    return lam * w


def run_gd(eta, steps=20000):
    w = w0.copy()
    for k in range(1, steps + 1):
        w = w - eta * grad(w)
        if np.linalg.norm(w) < tol:
            return k
    return None


def run_mom(eta, beta, steps=20000):
    w, v = w0.copy(), np.zeros(2)
    for k in range(1, steps + 1):
        v = beta * v - eta * grad(w)
        w = w + v
        if np.linalg.norm(w) < tol:
            return k
    return None


def run_adam(eta, b1=0.9, b2=0.999, eps=1e-8, steps=20000, tol_=tol):
    w, m, v = w0.copy(), np.zeros(2), np.zeros(2)
    for k in range(1, steps + 1):
        g = grad(w)
        m = b1 * m + (1 - b1) * g
        v = b2 * v + (1 - b2) * g * g
        mh, vh = m / (1 - b1 ** k), v / (1 - b2 ** k)
        w = w - eta * mh / (np.sqrt(vh) + eps)
        if np.linalg.norm(w) < tol_:
            return k
    return None


eta_gd = 2 / (lam[0] + lam[1])
rate_gd = (kappa - 1) / (kappa + 1)
k_gd = run_gd(eta_gd)
k_gd_pred = math.log(tol / np.linalg.norm(w0)) / math.log(rate_gd)
sq = math.sqrt(kappa)
beta_opt = ((sq - 1) / (sq + 1)) ** 2
eta_mom = (2 / (math.sqrt(lam[0]) + math.sqrt(lam[1]))) ** 2
rate_mom = (sq - 1) / (sq + 1)
k_mom = run_mom(eta_mom, beta_opt)
k_mom09 = run_mom(eta_gd, 0.9)
# Adam：固定学习率 0.05，看它在病态方向上的表现（以误差小于 1e-3 为准）
k_adam = run_adam(0.05, tol_=1e-3)
k_gd_1e3 = None
w = w0.copy()
for k in range(1, 20000):
    w = w - eta_gd * grad(w)
    if np.linalg.norm(w) < 1e-3:
        k_gd_1e3 = k
        break
k_mom_1e3 = None
w, v = w0.copy(), np.zeros(2)
for k in range(1, 20000):
    v = beta_opt * v - eta_mom * grad(w)
    w = w + v
    if np.linalg.norm(w) < 1e-3:
        k_mom_1e3 = k
        break

# 算例 2.6.1：小批量随机梯度（跑合试验台数据，标准化后的线性回归），不同批大小下最后 100 步损失的波动
x, y = rig_data()
xs = (x - x.mean()) / x.std()
A = np.c_[xs, np.ones(len(x))]
v_star = np.linalg.lstsq(A, y, rcond=None)[0]
L_star = float(np.mean((A @ v_star - y) ** 2))
rng = np.random.default_rng(5)
spread = {}
for Bsz in (1, 4, 40):
    v = np.zeros(2)
    ls = []
    for step in range(600):
        idx = rng.choice(len(y), Bsz, replace=False)
        g = 2 / Bsz * A[idx].T @ (A[idx] @ v - y[idx])
        v = v - 0.05 * g
        ls.append(float(np.mean((A @ v - y) ** 2)))
    tail = np.array(ls[-100:])
    spread[Bsz] = (float(tail.mean() - L_star), float(tail.std()))

# 算例 2.6.2：20 层、每层 256 个 ReLU 单元，输入方差 1，不同初始化下最后一层输出的标准差
width, depth = 256, 20
rng = np.random.default_rng(1)
X0 = rng.normal(size=(512, width))
stds = {}
for name, s in (("small", 0.01), ("xavier", math.sqrt(1 / width)), ("he", math.sqrt(2 / width))):
    h = X0
    for _ in range(depth):
        W = rng.normal(0, s, (width, width))
        h = np.maximum(h @ W, 0)
    stds[name] = float(h.std())

# Adam 的显存：每个参数 4 字节权重 + 4 字节梯度 + 8 字节两个动量 = 16 字节（全部单精度）
N_tiny = tiny_params(TINY)["total"]
adam_mb = N_tiny * 16 / 2 ** 20

out(kappa=kappa, eta_gd=eta_gd, rate_gd=rate_gd, k_gd=k_gd, k_gd_pred=k_gd_pred, beta_opt=beta_opt, eta_mom=eta_mom,
    rate_mom=rate_mom, k_mom=k_mom, k_mom09=k_mom09, k_adam=k_adam, k_gd_1e3=k_gd_1e3, k_mom_1e3=k_mom_1e3,
    gap1=spread[1][0], sd1=spread[1][1], gap4=spread[4][0], sd4=spread[4][1], gap40=spread[40][0], sd40=spread[40][1],
    std_small=stds["small"], std_xavier=stds["xavier"], std_he=stds["he"], depth=depth, width=width,
    N_tiny=N_tiny, adam_mb=adam_mb)
