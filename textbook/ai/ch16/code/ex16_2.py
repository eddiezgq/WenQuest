"""算例 16.2.1—16.2.4：对抗训练为什么难（16.2 节）。

（1）狄拉克生成对抗网络：唯一能手算的对抗例子，结论是同时走梯度**不收敛**，
     而且离最优点的距离每步恰好乘 sqrt(1+h²)——这不是调参没调好，是动力学本身如此。
（2）一维真例子：不衰减学习率时，KS 距离先降后升，而损失曲线看不出来——没有停的判据。
（3）模式坍塌：判别器走得比生成器多，矮峰就先被放掉。
（4）FID 这类"拟合两个高斯再比"的指标是有偏的：两组都来自真分布，算出来也不是 0。
"""
import numpy as np

from _ch16 import (dirac_gan, frechet, gan_1d, gan_2d, ks, mix_sample, ring_coverage,
                   ring_sample, MIX_MU, MIX_W, RING_K)
from bookout import out
from gen_facts import DCGAN, FID, FID_BIAS_SOURCE, GAN, STYLEGAN2

v = {}

# ---------- （1）狄拉克生成对抗网络
LR = 0.1
path = dirac_gan(lr=LR, steps=400)
r = np.hypot(path[:, 0], path[:, 1])
v["dirac_lr"] = LR
v["dirac_r0"], v["dirac_r400"] = float(r[0]), float(r[-1])
v["dirac_growth"] = float(np.sqrt(1 + LR ** 2))
ratio = r[1:] / r[:-1]
assert np.allclose(ratio, v["dirac_growth"], atol=1e-9), \
    "每一步的距离恰好乘 sqrt(1+h²)：这是上面那两行更新式解出来的，不是实验凑的"
v["dirac_ratio_max_err"] = float(np.max(np.abs(ratio - v["dirac_growth"])))
# 交替更新也不收敛，只是绕圈
r_alt = np.hypot(*dirac_gan(lr=LR, steps=400, alt=True).T)
v["dirac_alt_r400"] = float(r_alt[-1])
assert r_alt[-1] > 0.9 * r_alt[0], "交替更新同样收不进去"
# 给判别器加一点正则才会往里收
r_reg = np.hypot(*dirac_gan(lr=LR, steps=400, reg=0.3).T)
v["dirac_reg"] = 0.3
v["dirac_reg_r400"] = float(r_reg[-1])
assert r_reg[-1] < 0.05, "加了正则就收到最优点附近"

# ---------- （2）KS 距离先降后升
train = mix_sample(8000, 0)
_, _, hist = gan_1d(train, steps=40_000, decay=None, seed=0, track=2000)
steps_h = np.array([h[0] for h in hist])
ks_h = np.array([h[1] for h in hist])
best = int(np.argmin(ks_h))
v["nodecay_steps"] = 40_000
v["ks_start"] = float(ks_h[0])
v["ks_best"] = float(ks_h[best])
v["ks_best_step"] = int(steps_h[best])
v["ks_end"] = float(ks_h[-1])
v["ks_rise"] = v["ks_end"] / v["ks_best"]
assert v["ks_end"] > 2.5 * v["ks_best"], "后来又变坏了——这是本节的要点：没有可靠的停的判据"
v["curve"] = [(int(s), round(float(k), 3)) for s, k in zip(steps_h, ks_h)][::3]
v["ks_mid"] = float(ks_h[len(ks_h) // 2])
v["ks_mid_step"] = int(steps_h[len(steps_h) // 2])
# 衰减学习率只是把它按住，不是解决
x_decay, _ = gan_1d(train, seed=0)
v["ks_decay"] = ks(x_decay)

# ---------- （3）模式坍塌：环上八个峰，三种常见的坏法
# 一维的单调映射丢不掉中间的峰（最多把它饿瘦），所以这一段换到二维。
RING_STEPS, RING_SEEDS = 8000, 2
ring = ring_sample(8000)
v["ring_k"] = RING_K
v["ring_steps"] = RING_STEPS
cov_true, share_true = ring_coverage(ring)
v["ring_cov_true"] = cov_true
v["ring_share_true"] = round(float(share_true.sum()), 3)
assert cov_true == RING_K, "真样本当然覆盖全部八个峰"

v["ring_rows"] = []
settings = [("非饱和目标（惯例）", {}),
            ("原始的饱和目标", {"saturating": True}),
            ("生成器太窄（4 个隐单元）", {"hid": 4}),
            ("判别器每轮走 6 步", {"k_disc": 6, "steps": RING_STEPS // 2})]
ring_cov = {}
for name, kw in settings:
    cs, ms = [], []
    for s in range(RING_SEEDS):
        kw2 = {"steps": RING_STEPS, "batch": 128, "hid": 24, **kw}
        c, sh = ring_coverage(gan_2d(ring, seed=s, **kw2))
        cs.append(c)
        ms.append(float(sh.sum()))
    ring_cov[name] = float(np.mean(cs))
    v["ring_rows"].append((name, round(float(np.mean(cs)), 1), round(float(np.mean(ms)), 2)))
for tag, key in (("非饱和目标（惯例）", "ok"), ("原始的饱和目标", "sat"),
                 ("生成器太窄（4 个隐单元）", "narrow"), ("判别器每轮走 6 步", "kdisc")):
    row = next(r for r in v["ring_rows"] if r[0] == tag)
    v[f"ring_cov_{key}"], v[f"ring_mass_{key}"] = row[1], row[2]
v["ring_mass_true"] = v["ring_share_true"]
v["ring_cov_sat"] = ring_cov["原始的饱和目标"]
v["ring_cov_narrow"] = ring_cov["生成器太窄（4 个隐单元）"]
assert v["ring_cov_sat"] < 1, "原始的饱和目标根本训不动：判别器一强，生成器的梯度就没了"
assert v["ring_cov_narrow"] < 0.6 * v["ring_cov_ok"], "生成器太窄 → 只守住几个峰，这就是模式坍塌"
v["mode_small_pct"] = MIX_W.min() * 100
v["mu_small"] = float(MIX_MU[np.argmin(MIX_W)])
v["n_modes"] = len(MIX_W)

# ---------- （4）"拟合两个高斯再比"的指标有偏
v["fid_rows"] = []
for n in (50, 100, 200, 500, 1000, 2000, 5000):
    d = float(np.mean([frechet(mix_sample(n, 10 + s), mix_sample(n, 500 + s)) for s in range(12)]))
    v["fid_rows"].append((n, round(d, 4)))
for n, d in v["fid_rows"]:
    v[f"fid_n{n}"] = d
v["fid_n_lo"], v["fid_n_hi"] = v["fid_rows"][0][0], v["fid_rows"][-1][0]
v["fid_bias_ratio"] = v["fid_n50"] / v["fid_n5000"]
assert v["fid_n50"] > 10 * v["fid_n5000"], "样本少的时候偏差大得多——真值是 0"
v["fid_samples"] = FID["samples"]
v["fid_layer"] = FID["layer"]
v["fid_bias_src"] = FID_BIAS_SOURCE
v["fid_bias_in_paper"] = FID["small_sample_bias"] is not None
assert not v["fid_bias_in_paper"], "小样本偏差不是原始 FID 论文讨论的，出处要写清楚"

# ---------- 公开发表的数字
v["gan_parzen_mnist"], v["gan_parzen_mnist_se"] = GAN["parzen_mnist"]
v["gan_k"] = GAN["k"]
v["gan_hours_known"] = GAN["hours"] is not None
assert not v["gan_hours_known"], "最早那篇生成对抗网络论文没给训练硬件与时长"
v["dcgan_batch"], v["dcgan_lr"], v["dcgan_beta1"] = DCGAN["batch"], DCGAN["lr"], DCGAN["beta1"]
v["dcgan_leaky"] = DCGAN["leaky"]
v["sg2_fid"], v["sg2_days"], v["sg2_gpus"] = STYLEGAN2["ffhq_fid"], STYLEGAN2["ffhq_days"], STYLEGAN2["gpus"]
v["sg2_gpu_days"] = STYLEGAN2["ffhq_days"] * STYLEGAN2["gpus"]      # 折算：8 块 × 9 天
v["sg2_fid_n_known"] = STYLEGAN2["fid_images"] is not None
assert not v["sg2_fid_n_known"], "StyleGAN2 论文没写 FID 用了多少张图——所以它的 FID 不能与别家直接比"

out(**v)
