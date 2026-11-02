"""23.3 节：正则化。由关节编码器的位置读数求关节速度：位置是速度的积分，p = p₀ + A v，A 为累加（积分）矩阵（h 乘下三角全 1）。
求 v 是一个病态的最小二乘问题：A 的条件数随点数增长，位置读数中 0.1 mrad 的噪声在速度中被放大成很大的抖动（直接差分也一样）。
采样周期 4 ms，共 500 个点。
(1) A 的奇异值与条件数；直接求解（相当于逐点差分）的速度误差；
(2) 吉洪诺夫正则化 min ‖Av − b‖² + λ²‖Lv‖²：L = I（岭回归）与 L = 一阶差分（惩罚加速度）；扫描 λ，
误差最小的 λ（事先不知道，只作对照）、L 曲线拐角处的 λ、偏差原理（残差 ≈ 噪声水平）给出的 λ；
(3) 滤波因子 σᵢ²/(σᵢ² + λ²)：正则化 = 平滑地截断 SVD。"""
import numpy as np

from _num import sci
from bookout import out

rng = np.random.default_rng(23031)
n = 500
h = 0.004                                         # 采样周期 4 ms，共 2 s
t = h * np.arange(1, n + 1)
# 真实速度：平滑的“加速—匀速—减速”（rad/s）
v_true = 1.2 * (np.tanh((t - 0.4) / 0.12) - np.tanh((t - 1.5) / 0.15)) / 2
A = h * np.tril(np.ones((n, n)))
p = A @ v_true
sigma = 1e-4
b = p + rng.normal(0, sigma, n)
s = np.linalg.svd(A, compute_uv=False)
out(n=n, s1=float(s[0]), sn=sci(float(s[-1]), 1), kA=float(s[0] / s[-1]))
v_naive = np.linalg.solve(A, b)
err = lambda v: float(np.sqrt(np.mean((v - v_true) ** 2)))
out(e_naive=err(v_naive), vmax=float(v_true.max()), noise_amp=float(sigma / h * np.sqrt(2)))

D = (np.eye(n) - np.eye(n, k=-1))[1:] / h          # 一阶差分（加速度）
AtA, Atb = A.T @ A, A.T @ b
lams = np.logspace(-6, 0, 121)
res = {}
for name, L in (("I", np.eye(n)), ("D", D)):
    rn, sn, es = [], [], []
    for lam in lams:
        v = np.linalg.solve(AtA + lam ** 2 * (L.T @ L), Atb)          # 正规方程（这里 A 的条件数不大，可以这样算）
        rn.append(np.linalg.norm(A @ v - b)); sn.append(np.linalg.norm(L @ v)); es.append(err(v))
    rn, sn, es = np.array(rn), np.array(sn), np.array(es)
    # L 曲线拐角：(log‖r‖, log‖Lv‖) 曲线曲率最大处
    x, y = np.log(rn), np.log(sn)
    dx, dy = np.gradient(x), np.gradient(y)
    ddx, ddy = np.gradient(dx), np.gradient(dy)
    kappa = (dx * ddy - dy * ddx) / (dx ** 2 + dy ** 2) ** 1.5
    i_l = int(np.argmax(kappa[5:-5])) + 5
    i_best = int(np.argmin(es))
    i_dp = int(np.argmin(np.abs(rn - sigma * np.sqrt(n))))          # 偏差原理
    res[name] = dict(rn=rn, sn=sn, es=es, i_l=i_l, i_best=i_best, i_dp=i_dp)
    out(**{f"{name}_best_lam": sci(float(lams[i_best]), 1), f"{name}_best_e": float(es[i_best]),
           f"{name}_l_lam": sci(float(lams[i_l]), 1), f"{name}_l_e": float(es[i_l]),
           f"{name}_dp_lam": sci(float(lams[i_dp]), 1), f"{name}_dp_e": float(es[i_dp])})
out(dp_target=sci(sigma * np.sqrt(n), 1))
# 滤波因子
lam = lams[res["D"]["i_l"]]
lamI = lams[res["I"]["i_l"]]
f = s ** 2 / (s ** 2 + lamI ** 2)
out(f_first=float(f[0]), f_half=int(np.sum(f > 0.5)), f_last=sci(float(f[-1]), 1))
