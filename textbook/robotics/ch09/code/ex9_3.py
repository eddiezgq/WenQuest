"""算例 9.3.1～9.3.3：贝叶斯公式。

9.3.1 减速器车间的视觉检测：缺陷率 1%，有缺陷时报警的概率 95%，无缺陷时误报的概率 5%。
      求报警的零件真有缺陷的概率；两台独立的检测站都报警时又是多少。用 100 万个零件的模拟核对。
9.3.2 AGV 在 20 格的走廊里定位：第 2、6、7、15 格有反光标志，检测器在标志格上报“有”的概率 0.9，在其他格上 0.1。
      先验均匀；测量“有” → 前进一格（以 0.8 的概率走一格，各以 0.1 的概率原地不动或走两格）→ 测量“有” → 前进 → 测量“无”。
      逐步的贝叶斯计算与“穷举全部起点和走法”的直接计算必须一致。
9.3.3 AGV 沿通道的位置：里程计给出先验 𝒩(5.20, 0.10²) m；激光雷达测得到 6.00 m 处标志的距离 0.75 m（标准差 0.03 m）。
      按定理 9.3.3 求后验，再用网格上的数值贝叶斯计算核对；第二次测量 0.77 m，逐次更新与一次合并的结果一致。
"""
import itertools
import math

import numpy as np

from _prob import gauss_pdf
from bookout import out, T

rng = np.random.default_rng(903)

# ---------------------------------------------------------------- 算例 9.3.1 视觉检测
pD, sens, fa = 0.01, 0.95, 0.05
p_alarm = sens * pD + fa * (1 - pD)                        # 全概率公式 (9.3.3)
post1 = sens * pD / p_alarm                                 # 贝叶斯公式 (9.3.5)
p_alarm2 = sens ** 2 * pD + fa ** 2 * (1 - pD)
post2 = sens ** 2 * pD / p_alarm2
post2_seq = sens * post1 / (sens * post1 + fa * (1 - post1))   # 以第一次的后验为先验
assert abs(post2 - post2_seq) < 1e-12
N = 1_000_000
defect = rng.random(N) < pD
alarm1 = np.where(defect, rng.random(N) < sens, rng.random(N) < fa)
alarm2 = np.where(defect, rng.random(N) < sens, rng.random(N) < fa)
mc1 = defect[alarm1].mean()
mc2 = defect[alarm1 & alarm2].mean()
assert abs(mc1 - post1) < 0.01 and abs(mc2 - post2) < 0.03
# 1000 个零件的自然频数
n_def = 1000 * pD
n_hit = n_def * sens
n_fa = 1000 * (1 - pD) * fa

# ---------------------------------------------------------------- 算例 9.3.2 走廊里的 AGV
ncell = 20
tags = {2, 6, 7, 15}
hit, false = 0.9, 0.1
move = {0: 0.1, 1: 0.8, 2: 0.1}                             # 前进 0、1、2 格的概率（到头则停在最后一格）
zs = [1, 1, 0]                                              # 三次测量：有、有、无


def like(z, cell):
    p = hit if cell in tags else false
    return p if z == 1 else 1 - p


def predict(b):
    nb = np.zeros(ncell)
    for i in range(ncell):
        for k, pk in move.items():
            nb[min(i + k, ncell - 1)] += pk * b[i]            # 全概率公式 (9.3.6)
    return nb


bel = np.full(ncell, 1 / ncell)
steps = [bel.copy()]
for j, z in enumerate(zs):
    bel = np.array([like(z, i) for i in range(ncell)]) * bel
    bel /= bel.sum()                                        # 贝叶斯公式 (9.3.5)
    steps.append(bel.copy())
    if j < len(zs) - 1:
        bel = predict(bel)
        steps.append(bel.copy())
# 直接计算：穷举起点和两次走法，按乘法公式算出每条“路径”的联合概率，再按末位置汇总
direct = np.zeros(ncell)
for x0 in range(ncell):
    for k1, k2 in itertools.product(move, move):
        x1 = min(x0 + k1, ncell - 1)
        x2 = min(x1 + k2, ncell - 1)
        pr = (1 / ncell) * like(zs[0], x0) * move[k1] * like(zs[1], x1) * move[k2] * like(zs[2], x2)
        direct[x2] += pr
direct /= direct.sum()
assert np.allclose(direct, bel, atol=1e-14)
after1 = steps[1]
p_tags1 = sum(after1[i] for i in tags)
best = int(np.argmax(bel))
assert best == 8

# ---------------------------------------------------------------- 算例 9.3.3 高斯先验与高斯测量
mu0, s0 = 5.20, 0.10
lm, dz, sz = 6.00, 0.75, 0.03
z1 = lm - dz
K = s0 ** 2 / (s0 ** 2 + sz ** 2)
mu1 = mu0 + K * (z1 - mu0)
var1 = 1 / (1 / s0 ** 2 + 1 / sz ** 2)
s1 = math.sqrt(var1)
assert abs(mu1 - (sz ** 2 * mu0 + s0 ** 2 * z1) / (s0 ** 2 + sz ** 2)) < 1e-12
assert abs(var1 - (1 - K) * s0 ** 2) < 1e-15
# 网格上的数值贝叶斯：后验 ∝ 似然 × 先验
x = np.linspace(4.5, 6.0, 300001)
post = gauss_pdf(x, mu0, s0) * gauss_pdf(z1, x, sz)
post /= np.trapezoid(post, x)
mu_g = np.trapezoid(x * post, x)
s_g = math.sqrt(np.trapezoid((x - mu_g) ** 2 * post, x))
assert abs(mu_g - mu1) < 1e-8 and abs(s_g - s1) < 1e-8
# 第二次测量：逐次更新 = 一次合并
dz2 = 0.77
z2 = lm - dz2
K2 = var1 / (var1 + sz ** 2)
mu2 = mu1 + K2 * (z2 - mu1)
var2 = (1 - K2) * var1
var_b = 1 / (1 / s0 ** 2 + 2 / sz ** 2)
mu_b = var_b * (mu0 / s0 ** 2 + (z1 + z2) / sz ** 2)
assert abs(mu2 - mu_b) < 1e-12 and abs(var2 - var_b) < 1e-15

out(
    pD=100 * pD, sens=100 * sens, fa=100 * fa, p_alarm=100 * p_alarm, post1=100 * post1, post2=100 * post2,
    mc1=100 * mc1, mc2=100 * mc2, n_def=n_def, n_hit=n_hit, n_fa=n_fa, N=N,
    ncell=ncell, tags=T("第 2、6、7、15 格", "cells 2, 6, 7 and 15"), p_tag1=after1[2], p_other1=after1[0], p_tags1=100 * p_tags1,
    best=best, p_best=bel[best], p_second=float(np.sort(bel)[-2]),
    bel_final=", ".join(f"{v:.3f}" for v in bel[5:12]),
    mu0=mu0, s0=s0, z1=z1, K=K, mu1=mu1, s1=s1, s1_mm=1000 * s1, mu_g=mu_g, s_g=s_g,
    z2=z2, K2=K2, mu2=mu2, s2=math.sqrt(var2), s2_mm=1000 * math.sqrt(var2),
    w_prior=100 * (1 - K), w_meas=100 * K,
)
