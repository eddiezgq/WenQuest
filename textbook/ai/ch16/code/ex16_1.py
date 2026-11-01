"""算例 16.1.1—16.1.3：五类生成模型在同一个分布上各走一遍（16.1 节）。

（1）把"生成得像不像"变成一个能算的数：真分布已知，于是柯尔莫哥洛夫—斯米尔诺夫距离说了算。
（2）五类模型各自的成绩：显式似然的三类（自回归、流、隐变量）又快又准，隐式的生成对抗网络
     慢得多也糙得多，扩散在两者之间——但这个结论只对这个一维玩具成立，正文说清楚为什么。
（3）三件事互相拉扯：采样要几次前向、能不能算似然、能不能精确算。
"""
import time

import numpy as np

from _ch16 import (autoregressive, coverage, flow, gan_1d, diffusion_fit, diffusion_sample,
                   ks, mix_pdf, mix_sample, vae_em, MIX_MU, MIX_SD, MIX_W)
from bookout import out

v = {}
N_TRAIN, N_GEN = 8000, 4000
train = mix_sample(N_TRAIN, 0)
v["n_train"], v["n_gen"] = N_TRAIN, N_GEN
v["n_modes"] = len(MIX_W)
v["w_min_pct"] = MIX_W.min() * 100
v["mu_small"], v["sd_small"] = float(MIX_MU[np.argmin(MIX_W)]), float(MIX_SD[np.argmin(MIX_W)])

# ---------- （1）先把尺子校准：同样本量的真样本，KS 距离也不是 0
floors = [ks(mix_sample(N_GEN, 900 + s)) for s in range(8)]
v["ks_floor"] = float(np.mean(floors))
v["ks_floor_max"] = float(np.max(floors))
# 真分布的平均对数密度：似然这一列的上限（谁也不可能超过它，除非过拟合训练集）
v["ll_true"] = float(np.mean(np.log(mix_pdf(mix_sample(N_GEN, 7)))))

# ---------- （2）五类模型
rows = []


def run(name, fn, exact_ll, passes):
    t0 = time.perf_counter()
    x, ll = fn()
    sec = time.perf_counter() - t0
    rows.append((name, ks(x), ll, coverage(x), passes, sec))
    return x


run("自回归（切格子数频率）", lambda: autoregressive(train, n=N_GEN), True, 1)
run("流（单调映射）", lambda: flow(train, n=N_GEN), True, 1)
run("隐变量（混合高斯）", lambda: vae_em(train, n=N_GEN)[:2], True, 1)
x_gan = run("生成对抗网络", lambda: (gan_1d(train, n=N_GEN)[0], float("nan")), False, 1)

t0 = time.perf_counter()
model = diffusion_fit(train)
v["fit_sec_diff"] = time.perf_counter() - t0
T_FULL = model["T"]
x_diff = diffusion_sample(model, N_GEN, steps=200, seed=0)
rows.append(("扩散（200 步采样）", ks(x_diff), float("nan"), coverage(x_diff), 200, 0.0))

v["rows"] = [(n, round(k, 4), ("—" if np.isnan(l) else round(l, 3)), c, p)
             for n, k, l, c, p, _ in rows]
for name, k, ll, cov, p, _ in rows:
    key = {"自回归（切格子数频率）": "ar", "流（单调映射）": "flow", "隐变量（混合高斯）": "mix",
           "生成对抗网络": "gan", "扩散（200 步采样）": "diff"}[name]
    v[f"ks_{key}"] = k
    v[f"cov_{key}"] = cov
    if not np.isnan(ll):
        v[f"ll_{key}"] = ll

# 显式似然的三类都贴着下限，隐式的那一类差一个数量级
v["ks_explicit_max"] = max(v["ks_ar"], v["ks_flow"], v["ks_mix"])
v["gan_over_floor"] = v["ks_gan"] / v["ks_floor"]
v["explicit_over_floor"] = v["ks_explicit_max"] / v["ks_floor"]
assert v["ks_explicit_max"] < 3 * v["ks_floor"], "显式似然的三类应当贴着有限样本的下限"
assert v["ks_gan"] > 4 * v["ks_explicit_max"], "一维上生成对抗网络明显更糙，这是本节要讲的对照"
assert all(c == v["n_modes"] for c in (v["cov_ar"], v["cov_flow"], v["cov_mix"], v["cov_diff"])), \
    "三个峰都该被覆盖到"
# 似然这一列：混合高斯几乎追上真分布，流略高是因为它在训练集上贴得太紧
v["ll_gap_mix"] = v["ll_true"] - v["ll_mix"]
assert abs(v["ll_gap_mix"]) < 0.02, "真分布本来就是混合高斯，所以这一类能几乎学到顶"

# ---------- （3）三件事的账
v["t_full"] = T_FULL
v["diff_passes_200"] = 200
v["speed_gap"] = 200                                  # 折算：扩散一次采样要 200 次前向，流只要 1 次
v["gan_no_likelihood"] = True

out(**v)
