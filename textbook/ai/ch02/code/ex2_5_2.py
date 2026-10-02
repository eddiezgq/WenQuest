"""算例 2.5.2、程序 2.5.2：两层网络在“月牙”数据上的训练，反向传播按矩阵形式手写（式 (2.5.3)～(2.5.6)），
用有限差分核对梯度；并统计前向与反向的乘加次数。

网络：输入 2 维 → 隐藏层 16 个 ReLU → 输出 1 个 logit；损失为带 logit 的交叉熵。全批梯度下降。
"""
import numpy as np

from _ch2 import moons
from bookout import out

X, y = moons(200, seed=7)
Xt, yt = moons(200, seed=8)                       # 另取一组作为测试集
n, d = X.shape
m = 16
rng = np.random.default_rng(3)
params = {
    "W1": rng.normal(0, np.sqrt(2 / d), (d, m)),  # He 初始化（2.6 节）
    "b1": np.zeros(m),
    "W2": rng.normal(0, np.sqrt(2 / m), (m, 1)),
    "b2": np.zeros(1),
}


def forward(P, X):
    Z1 = X @ P["W1"] + P["b1"]                    # (n, m)
    H = np.maximum(Z1, 0)
    z = (H @ P["W2"] + P["b2"]).ravel()           # (n,)
    return Z1, H, z


def loss(P, X, y):
    z = forward(P, X)[2]
    return float(np.mean(np.logaddexp(0, z) - y * z))   # −[y ln σ(z) + (1−y) ln(1−σ(z))]，数值稳定的写法


def grads(P, X, y):
    Z1, H, z = forward(P, X)
    nn = len(y)
    dz = (1 / (1 + np.exp(-z)) - y)[:, None] / nn  # ∂L/∂z = (p − y)/n，形状 (n, 1)
    g = {"W2": H.T @ dz, "b2": dz.sum(0)}
    dH = dz @ P["W2"].T                           # (n, m)
    dZ1 = dH * (Z1 > 0)                           # ReLU 的导数
    g["W1"] = X.T @ dZ1
    g["b1"] = dZ1.sum(0)
    return g


# 梯度检查：随机方向上的有限差分
g = grads(params, X, y)
rel = []
for k in params:
    v = rng.normal(size=params[k].shape)
    Pp = {**params, k: params[k] + 1e-6 * v}
    Pm = {**params, k: params[k] - 1e-6 * v}
    fd = (loss(Pp, X, y) - loss(Pm, X, y)) / 2e-6
    an = float((g[k] * v).sum())
    rel.append(abs(fd - an) / max(abs(fd), abs(an), 1e-12))
max_rel = max(rel)
assert max_rel < 1e-6

loss0 = loss(params, X, y)
eta = 0.5
hist = []
for step in range(1, 5001):
    g = grads(params, X, y)
    for k in params:
        params[k] -= eta * g[k]
    if step % 500 == 0:
        hist.append(loss(params, X, y))
acc = lambda P, A, b: float(np.mean((forward(P, A)[2] > 0) == (b > 0.5)))
train_acc, test_acc = acc(params, X, y), acc(params, Xt, yt)

# 逻辑回归（没有隐藏层）作为对照
Z = np.c_[X, np.ones(n)]
w = np.zeros(3)
for _ in range(5000):
    w -= 0.5 * Z.T @ (1 / (1 + np.exp(-Z @ w)) - y) / n
lr_acc = float(np.mean((Z @ w > 0) == (y > 0.5)))

# 乘加次数（只计矩阵乘法）
B = n
fwd = B * d * m + B * m * 1
bwd = (m * B * 1) + (B * 1 * m) + (d * B * m)   # dW2 = Hᵀdz，dH = dz W2ᵀ，dW1 = Xᵀ dZ1（不需要 dX）
bwd_full = bwd + B * m * d                      # 若还要对输入求梯度（中间层都需要）
n_params = sum(v.size for v in params.values())

out(n=n, m=m, n_params=n_params, max_rel=max_rel, loss0=loss0, loss_end=hist[-1], train_acc=train_acc * 100,
    test_acc=test_acc * 100, lr_acc=lr_acc * 100, fwd=fwd, bwd=bwd, bwd_full=bwd_full, ratio=bwd_full / fwd, eta=eta)
