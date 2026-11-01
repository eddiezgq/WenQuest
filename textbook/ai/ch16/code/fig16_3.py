"""16.3 节的示意图。

图 16.3.1（动画 16.3.1 的静态版）：上一行是正向——原始分布一步步被噪声抹平成标准正态；
下一行是反向——从纯噪声出发，一步步把三个峰还原回来。

图 16.3.2：（a）采样步数与质量：步数砍到十分之一就明显偏了，五十步往上已经够用；
（b）各个时刻的训练损失量级差几千倍，所以"损失小"不等于"生成得好"。
"""
import numpy as np

from _ch16 import (diffusion_fit, diffusion_sample, eps_hat, forward, ks, mix_pdf, mix_sample,
                   _M, _S)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

train = mix_sample(8000, 0)
model = diffusion_fit(train)
abar, T_FULL = model["abar"], model["T"]
z0 = (mix_sample(20000, 1) - _M) / _S
g = np.random.default_rng(0)
grid = np.linspace(-4, 4, 400)
normal = np.exp(-0.5 * grid ** 2) / np.sqrt(2 * np.pi)

# ---------------------------------------------------------------- 图 16.3.1
# 把每个时刻的分布画成一列，左右两幅分别是正向与反向的整条轨迹。
EDGES = np.linspace(-4, 4, 121)
CENTERS = (EDGES[:-1] + EDGES[1:]) / 2
TS_GRID = np.linspace(0, T_FULL - 1, 80).astype(int)

fwd = np.zeros((len(CENTERS), len(TS_GRID)))
for j, t in enumerate(TS_GRID):
    zt, _ = forward(z0, int(t), abar, g)
    fwd[:, j], _ = np.histogram(zt, EDGES, density=True)

gg = np.random.default_rng(5)
z = gg.normal(size=20000)
rev = np.zeros((len(CENTERS), T_FULL))
for t in range(T_FULL - 1, -1, -1):
    rev[:, t], _ = np.histogram(z, EDGES, density=True)
    e = eps_hat(model, z, t)
    zh = np.clip((z - np.sqrt(1 - abar[t]) * e) / np.sqrt(abar[t]), -6, 6)
    ab_prev = abar[t - 1] if t > 0 else 1.0
    sig = np.sqrt(max((1 - ab_prev) / (1 - abar[t]) * (1 - abar[t] / ab_prev), 0.0)) if t > 0 else 0.0
    z = np.sqrt(ab_prev) * zh + np.sqrt(max(1 - ab_prev - sig ** 2, 0.0)) * e
    if sig > 0:
        z = z + sig * gg.normal(size=20000)
z_final = z

fig, (p, q) = plt.subplots(1, 2, figsize=(11.8, 4.4), sharey=True)
vmax = float(max(fwd.max(), rev.max()))
p.imshow(fwd, aspect="auto", origin="lower", cmap="Blues", vmin=0, vmax=vmax,
         extent=[0, T_FULL, EDGES[0], EDGES[-1]])
p.set_xlabel(T("正向：加噪的时刻 t", "forward: timestep t"))
p.set_ylabel(T("标准化之后的取值", "standardized value"))
p.set_title(T("(a) 三个峰一步步被噪声抹平", "(a) Noise flattens the three modes"), fontsize=10)

q.imshow(rev[:, ::-1], aspect="auto", origin="lower", cmap="Greens", vmin=0, vmax=vmax,
         extent=[0, T_FULL, EDGES[0], EDGES[-1]])
q.set_xlabel(T("反向：已经去掉的步数", "reverse: steps already taken"))
q.set_title(T("(b) 从纯噪声出发，峰一个个长回来", "(b) From pure noise, the modes come back"),
            fontsize=10)
for ax in (p, q):
    ax.grid(alpha=0.15, lw=0.4, color="white")

fig.tight_layout()
figure(fig, "fig16_3_1")

# ---------------------------------------------------------------- 图 16.3.2
fig2, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.2))

steps_list = [10, 20, 50, 100, 200, 500, 1000]
k1 = [float(np.mean([ks(diffusion_sample(model, 4000, steps=s, eta=1.0, seed=i))
                     for i in range(3)])) for s in steps_list]
k0 = [float(np.mean([ks(diffusion_sample(model, 4000, steps=s, eta=0.0, seed=i))
                     for i in range(3)])) for s in steps_list]
floor = float(np.mean([ks(mix_sample(4000, 900 + s)) for s in range(8)]))
a.semilogx(steps_list, k1, "o-", color=C["z"], lw=1.8, ms=5, label=T("随机采样（η = 1）", "stochastic (η = 1)"))
a.semilogx(steps_list, k0, "s--", color=C["y"], lw=1.6, ms=5, label=T("确定采样（η = 0）", "deterministic (η = 0)"))
a.axhline(floor, color=C["muted"], ls=":", lw=1.2,
          label=T(f"有限样本的下限 {floor:.3f}", f"finite-sample floor {floor:.3f}"))
a.set_xlabel(T("采样步数", "sampling steps"))
a.set_ylabel(T("柯尔莫哥洛夫—斯米尔诺夫距离", "KS distance"))
a.set_title(T("(a) 步数砍到十分之一就明显偏了", "(a) Ten steps is visibly off"), fontsize=10)
a.legend(fontsize=8)
a.grid(alpha=0.25, lw=0.5, which="both")

ts = np.arange(0, T_FULL, 20)
loss = []
for t in ts:
    zt, eps = forward(z0[:4000], int(t), abar, g)
    loss.append(float(np.mean((eps - eps_hat(model, zt, int(t))) ** 2)))
b.semilogy(ts, loss, color=C["x"], lw=1.8)
b.set_xlabel(T("时刻 t（噪声从小到大）", "timestep t (noise increasing)"))
b.set_ylabel(T("这一时刻的训练损失", "training loss at this t"))
b.set_title(T("(b) 不同时刻的损失差几千倍", "(b) Loss spans three orders of magnitude"), fontsize=10)
b.grid(alpha=0.25, lw=0.5, which="both")

fig2.tight_layout()
figure(fig2, "fig16_3_2")
