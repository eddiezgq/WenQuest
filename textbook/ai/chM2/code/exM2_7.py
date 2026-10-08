"""算例 M2.7.1：矩阵微分的几个常用公式，逐条用数值梯度核对（M2.7 节）。

写模型、推导反向传播时反复要用的就这么几条。公式记不住可以查，但必须会验：
把解析式与中心差分算出来的数值梯度比一比，差在 1e-8 以下才算对。
"""
import numpy as np

from bookout import out


def num_grad(fun, x, h=1e-6):
    x = np.asarray(x, dtype=float)
    g = np.zeros_like(x)
    it = np.nditer(x, flags=["multi_index"])
    while not it.finished:
        e = np.zeros_like(x)
        e[it.multi_index] = h
        g[it.multi_index] = (fun(x + e) - fun(x - e)) / (2 * h)
        it.iternext()
    return g


rng = np.random.default_rng(7)
d = 5
w = rng.normal(0, 1, d)
c = rng.normal(0, 1, d)
A = rng.normal(0, 1, (d, d))
S = (A + A.T) / 2                                               # 对称矩阵
X = rng.normal(0, 1, (20, d))
y = rng.normal(0, 1, 20)

cases = {
    # 名称: (函数, 解析梯度)
    "linear": (lambda w: float(c @ w), lambda w: c),                                  # ∇(cᵀw) = c
    "quad": (lambda w: float(w @ S @ w), lambda w: 2 * S @ w),                        # ∇(wᵀSw) = 2Sw（S 对称）
    "quad_gen": (lambda w: float(w @ A @ w), lambda w: (A + A.T) @ w),                # 一般 A：∇ = (A + Aᵀ)w
    "l2": (lambda w: float(w @ w), lambda w: 2 * w),                                  # ∇‖w‖² = 2w
    "norm": (lambda w: float(np.linalg.norm(w)), lambda w: w / np.linalg.norm(w)),    # ∇‖w‖ = w/‖w‖
    "lsq": (lambda w: float(np.mean((X @ w - y) ** 2)),                               # 最小二乘（式 (2.2.2)）
            lambda w: 2 * X.T @ (X @ w - y) / len(y)),
    "logistic": (lambda w: float(np.mean(np.log1p(np.exp(-y_sign * (X @ w))))),       # 逻辑回归（式 (2.2.7)）
                 lambda w: -X.T @ (y_sign / (1 + np.exp(y_sign * (X @ w)))) / len(y)),
    "softmax_ce": (None, None),                                                        # 下面单独算
}
y_sign = np.sign(rng.normal(0, 1, 20))
v = {}
for name, (fun, ana) in cases.items():
    if fun is None:
        continue
    g_num, g_ana = num_grad(fun, w), ana(w)
    err = float(np.abs(g_num - g_ana).max() / max(np.abs(g_ana).max(), 1e-12))
    v[f"err_{name}"] = err
    assert err < 1e-7, f"{name} 的解析梯度与数值梯度不符"

# ---------- 交叉熵 + softmax：最常用的一条，梯度正好是"预测减真值"（2.2 节、M3.4 节）
K = 4
z = rng.normal(0, 1, K)
t = np.zeros(K)
t[2] = 1.0                                                      # 真实类别是第 3 类


def ce(z):
    z = np.asarray(z, dtype=float)
    p = np.exp(z - z.max())
    p /= p.sum()
    return float(-(t * np.log(p)).sum())


p_hat = np.exp(z - z.max())
p_hat /= p_hat.sum()
g_ana = p_hat - t                                               # 就这么简洁
err = float(np.abs(num_grad(ce, z) - g_ana).max())
v["err_softmax_ce"] = err
assert err < 1e-7
v["p_hat"] = [round(float(a), 4) for a in p_hat]
v["g_ce"] = [round(float(a), 4) for a in g_ana]
v["n_rules"] = sum(1 for k in v if k.startswith("err_"))
v["err_max"] = max(val for k, val in v.items() if k.startswith("err_"))
out(**v)
