"""16.2 节的示意图。

图 16.2.1：（a）狄拉克生成对抗网络的轨迹——同时走梯度时绕着最优点往外转，加了正则才收进去；
（b）一维真例子上，KS 距离先降后升，而训练过程本身看不出该在哪里停。

图 16.2.2：环上八个峰的模式坍塌——左边是真样本，右边三张分别是惯例目标、原始的饱和目标、
生成器太窄时生成器采出来的点。
"""
import numpy as np

from _ch16 import (dirac_gan, gan_1d, gan_2d, mix_sample, ring_centers, ring_coverage,
                   ring_sample, RING_K)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

# ---------------------------------------------------------------- 图 16.2.1
fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

p_sim = dirac_gan(lr=0.1, steps=300)
p_reg = dirac_gan(lr=0.1, steps=300, reg=0.3)
a.plot(p_sim[:, 0], p_sim[:, 1], color=C["x"], lw=1.3,
       label=T("同时走梯度：往外转", "simultaneous: spirals out"))
a.plot(p_reg[:, 0], p_reg[:, 1], color=C["z"], lw=1.3,
       label=T("判别器加正则：收进去", "with regularization: converges"))
a.plot([p_sim[0, 0]], [p_sim[0, 1]], "o", color=C["ink"], ms=5)
a.plot([0], [0], "*", color=C["y"], ms=14, label=T("最优点 (0, 0)", "optimum (0, 0)"))
a.set_xlabel(T("生成器参数 θ", "generator parameter θ"))
a.set_ylabel(T("判别器参数 ψ", "discriminator parameter ψ"))
a.set_title(T("(a) 唯一能手算的对抗例子：它不收敛", "(a) The one solvable example: it does not converge"),
            fontsize=10)
a.set_aspect("equal")
a.legend(fontsize=8, loc="upper left")
a.grid(alpha=0.25, lw=0.5)

train = mix_sample(8000, 0)
_, _, hist = gan_1d(train, steps=40_000, decay=None, seed=0, track=2000)
steps_h = np.array([h[0] for h in hist])
ks_h = np.array([h[1] for h in hist])
best = int(np.argmin(ks_h))
b.plot(steps_h / 1000, ks_h, "o-", color=C["x"], lw=1.6, ms=4)
b.plot([steps_h[best] / 1000], [ks_h[best]], "o", color=C["y"], ms=9,
       label=T(f"最好的时候：{ks_h[best]:.3f}", f"best: {ks_h[best]:.3f}"))
b.annotate(T("再往下训就变坏了", "it gets worse from here"),
           xy=(steps_h[best] / 1000, ks_h[best]), xytext=(12, 0.26), fontsize=9,
           arrowprops=dict(arrowstyle="->", color=C["muted"], lw=1.0))
b.set_xlabel(T("训练步数（千步）", "training steps (thousands)"))
b.set_ylabel(T("柯尔莫哥洛夫—斯米尔诺夫距离", "KS distance"))
b.set_title(T("(b) 没有可靠的停的判据", "(b) No reliable stopping signal"), fontsize=10)
b.legend(fontsize=8)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig16_2_1")

# ---------------------------------------------------------------- 图 16.2.2
ring = ring_sample(6000)
panels = [(ring, T("真样本", "real samples"), None),
          (gan_2d(ring, steps=8000, batch=128, hid=24, seed=0), T("非饱和目标（惯例）", "non-saturating loss"), None),
          (gan_2d(ring, steps=8000, batch=128, hid=24, seed=0, saturating=True),
           T("原始的饱和目标", "original saturating loss"), None),
          (gan_2d(ring, steps=8000, batch=128, hid=4, seed=0), T("生成器太窄", "generator too narrow"), None)]

fig2, axes = plt.subplots(1, 4, figsize=(13.2, 3.5))
fig2.set_dpi(200)
cen = ring_centers()
for ax, (pts, title, _) in zip(axes, panels):
    cov, _ = ring_coverage(pts)
    ax.scatter(pts[:, 0], pts[:, 1], s=2, alpha=0.25, color=C["z"], linewidths=0, rasterized=True)
    ax.scatter(cen[:, 0], cen[:, 1], s=40, facecolors="none", edgecolors=C["x"], lw=1.2)
    ax.set_xlim(-3.2, 3.2)
    ax.set_ylim(-3.2, 3.2)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(T(f"{title}\n覆盖 {cov}/{RING_K} 个峰", f"{title}\ncovers {cov}/{RING_K} modes"),
                 fontsize=9)

fig2.tight_layout()
figure(fig2, "fig16_2_2")
