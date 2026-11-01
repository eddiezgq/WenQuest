"""算例 16.3.1—16.3.4：扩散模型的原理，逐条核对（16.3 节）。

（1）前向过程的闭式解：x_t = sqrt(ᾱ_t)·x_0 + sqrt(1−ᾱ_t)·ε。用程序验证它与"一步一步加噪"
     得到的是同一个分布，所以训练时可以直接跳到任意时刻。
（2）最优的噪声预测器写得出来（本章的真分布是混合高斯，分数函数有解析式）。学出来的那个
     离它有多远，正好量出"模型不够好"这部分误差。
（3）采样步数与质量：步数砍到十分之一，分布就明显偏了；五十到一百步够用。
     真模型上的同一条曲线见 DDIM 论文表 1，本节两边都列。
（4）为什么不能用"训练损失"判断好坏：不同时刻的损失量级差几十倍，加权一变，数就变。
"""
import numpy as np

from _ch16 import (diffusion_fit, diffusion_sample, eps_exact, eps_hat, forward, ks, mix_sample,
                   schedule, _M, _S)
from bookout import out
from gen_facts import DDIM, DDPM

v = {}
train = mix_sample(8000, 0)
z_train = (train - _M) / _S

# ---------- （1）前向的闭式解
T = DDPM["T"]
beta, alpha, abar = schedule(T, DDPM["beta_start"], DDPM["beta_end"])
v["t_total"] = T
v["beta_start"], v["beta_end"] = DDPM["beta_start"], DDPM["beta_end"]
v["abar_1"], v["abar_half"], v["abar_T"] = float(abar[0]), float(abar[T // 2]), float(abar[-1])
v["snr_T"] = float(abar[-1] / (1 - abar[-1]))
assert abar[-1] < 1e-4, "走到最后一步，原始信号基本没了——所以反向可以从纯噪声起步"
# 一步跳 vs 一步一步走：比前四阶矩
g = np.random.default_rng(0)
T_CHECK = 300
z_big = (mix_sample(20000, 3) - _M) / _S
x = z_big.copy()
for t in range(T_CHECK + 1):                                  # 一步一步加
    x = np.sqrt(alpha[t]) * x + np.sqrt(beta[t]) * g.normal(size=len(x))
x_jump, _ = forward(z_big, T_CHECK, abar, g)
v["t_check"] = T_CHECK
v["step_mean"], v["jump_mean"] = float(x.mean()), float(x_jump.mean())
v["step_std"], v["jump_std"] = float(x.std()), float(x_jump.std())
v["mean_err"] = abs(v["step_mean"] - v["jump_mean"])
v["std_err"] = abs(v["step_std"] - v["jump_std"])
assert v["mean_err"] < 0.02 and v["std_err"] < 0.02, "闭式解与逐步加噪给出同一个分布"
# 理论标准差：sqrt(ᾱ·Var(z) + 1−ᾱ) = 1（因为 z 已标准化）
v["std_theory"] = float(np.sqrt(abar[T_CHECK] * z_big.var() + (1 - abar[T_CHECK])))

# ---------- （2）学出来的预测器 vs 解析最优
model = diffusion_fit(train, T=T)
v["n_params"] = int(model["W"].size)
v["rmse_rows"] = []
for t in (10, 100, 300, 600, 900):
    zt, _ = forward(z_train, t, abar, g)
    a, b = eps_hat(model, zt, t), eps_exact(zt, t, abar)
    v["rmse_rows"].append((t, round(float(np.sqrt(np.mean((a - b) ** 2))), 4),
                           round(float(b.std()), 3)))
for t, rm, sd in v["rmse_rows"]:
    v[f"rmse_t{t}"], v[f"std_t{t}"] = rm, sd
assert v["rmse_t600"] < 0.05, "噪声大的时候，学出来的预测器几乎就是最优的那个"
assert v["rmse_t10"] > v["rmse_t600"], "噪声小的时候反而更难学——那时候 ε 几乎决定不了 x_t 往哪偏"

# 用解析最优采样 vs 用学出来的采样：差的那一点就是"模型不够好"
ks_exact = float(np.mean([ks(diffusion_sample(model, 4000, steps=200, exact=True, seed=s))
                          for s in range(3)]))
ks_learn = float(np.mean([ks(diffusion_sample(model, 4000, steps=200, seed=s)) for s in range(3)]))
floor = float(np.mean([ks(mix_sample(4000, 900 + s)) for s in range(8)]))
v["ks_exact"], v["ks_learn"], v["ks_floor"] = ks_exact, ks_learn, floor
v["model_gap"] = ks_learn - ks_exact
assert ks_exact < 1.6 * floor, "换成解析最优的预测器，采样结果就贴着有限样本的下限"

# ---------- （3）步数与质量
v["step_rows"] = []
for steps in (10, 20, 50, 100, 200, 1000):
    k1 = float(np.mean([ks(diffusion_sample(model, 4000, steps=steps, eta=1.0, seed=s))
                        for s in range(3)]))
    k0 = float(np.mean([ks(diffusion_sample(model, 4000, steps=steps, eta=0.0, seed=s))
                        for s in range(3)]))
    v["step_rows"].append((steps, round(k1, 4), round(k0, 4)))
for st, k1, k0 in v["step_rows"]:
    v[f"ks_{st}"], v[f"ks0_{st}"] = k1, k0
v["ks_10_over_1000"] = v["ks_10"] / v["ks_1000"]
assert v["ks_10"] > 3 * v["ks_1000"], "十步采样明显偏，这与 DDIM 论文的表 1 一个方向"
assert v["ks_50"] < 2.5 * v["ks_1000"], "五十步已经接近走满"
# 真模型上的数字（DDIM 论文表 1，CIFAR-10 的 FID）
v["ddim_fid"] = [(k, DDIM["cifar_fid"][k], DDIM["cifar_fid_ddpm"][k]) for k in (10, 20, 50, 100, 1000)]
for k in (10, 20, 50, 100, 1000):
    v[f"ddim_fid_{k}"], v[f"ddim_fid_ddpm_{k}"] = DDIM["cifar_fid"][k], DDIM["cifar_fid_ddpm"][k]
v["ddim_usable_lo"], v["ddim_usable_hi"] = DDIM["usable_steps"]
v["ddim_speed_lo"], v["ddim_speed_hi"] = DDIM["speedup"]
v["ddim_10_ratio"] = DDIM["cifar_fid_ddpm"][10] / DDIM["cifar_fid"][10]
v["ddim_usable"] = DDIM["usable_steps"]
v["ddim_speedup"] = DDIM["speedup"]
v["ddpm_fid_train"], v["ddpm_fid_test"] = DDPM["cifar_fid_train"], DDPM["cifar_fid_test"]
v["ddpm_fid_L"] = DDPM["cifar_fid_L"]
v["ddpm_fid_ratio"] = DDPM["cifar_fid_L"] / DDPM["cifar_fid_train"]   # 折算：换成变分下界当损失，FID 差多少
v["ddpm_steps_w"] = DDPM["steps"] / 1e4
v["ddpm_batch"], v["ddpm_hours"] = DDPM["batch"], DDPM["hours"]
v["ddpm_hardware"] = DDPM["hardware"]
v["ddpm_params_m"] = DDPM["params_cifar"] / 1e6

# ---------- （4）训练损失的量级随时刻差几十倍
losses = []
for t in range(0, T, 25):
    zt, eps = forward(z_train[:4000], t, abar, g)
    losses.append((t, float(np.mean((eps - eps_hat(model, zt, t)) ** 2))))
lo = min(l for _, l in losses)
hi = max(l for _, l in losses)
v["loss_min"], v["loss_max"] = lo, hi
v["loss_spread"] = hi / max(lo, 1e-12)
assert v["loss_spread"] > 20, "不同时刻的损失量级差很大，所以'损失小'不等于'生成得好'"
v["loss_rows"] = [(t, round(l, 4)) for t, l in losses][::8]

out(**v)
