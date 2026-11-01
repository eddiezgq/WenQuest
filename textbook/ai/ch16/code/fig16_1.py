"""16.1 节的示意图。

图 16.1.1：（a）本章那个一维真分布，与五类模型各自采出来的直方图叠在一起；
（b）同一张图上把三件事摆清楚：采样质量（KS 距离）、能不能算似然、采一次要几次前向。
"""
import numpy as np

from _ch16 import (autoregressive, diffusion_fit, diffusion_sample, flow, gan_1d, ks, mix_pdf,
                   mix_sample, vae_em, MIX_MU)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

train = mix_sample(8000, 0)
grid = np.linspace(MIX_MU.min() - 2.5, MIX_MU.max() + 2.5, 600)

x_ar, _ = autoregressive(train, n=6000)
x_fl, _ = flow(train, n=6000)
x_mx, _, _ = vae_em(train, n=6000)
x_gn, _ = gan_1d(train, n=6000)
model = diffusion_fit(train)
x_df = diffusion_sample(model, 6000, steps=200)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.2))

a.plot(grid, mix_pdf(grid), color=C["ink"], lw=2.2, label=T("真分布", "true density"), zorder=5)
sets = [(x_fl, T("流", "flow"), C["z"]),
        (x_df, T("扩散（200 步）", "diffusion (200 steps)"), C["y"]),
        (x_gn, T("生成对抗网络", "GAN"), C["x"])]
for xs, lab, col in sets:
    a.hist(xs, bins=90, density=True, histtype="step", lw=1.4, color=col, label=lab)
a.set_xlabel(T("样本的取值", "value"))
a.set_ylabel(T("密度", "density"))
a.set_title(T("(a) 同一个分布，三类模型采出来的样子", "(a) One target, three model families"),
            fontsize=10)
a.legend(fontsize=8)
a.grid(alpha=0.25, lw=0.5)

floor = float(np.mean([ks(mix_sample(6000, 900 + s)) for s in range(8)]))
rows = [(T("自回归", "autoregressive"), ks(x_ar), 1, True),
        (T("流", "flow"), ks(x_fl), 1, True),
        (T("隐变量", "latent variable"), ks(x_mx), 1, True),
        (T("扩散", "diffusion"), ks(x_df), 200, False),
        (T("生成对抗网络", "GAN"), ks(x_gn), 1, False)]
names = [r[0] for r in rows]
vals = [r[1] for r in rows]
cols = [C["z"] if r[3] else C["x"] for r in rows]
bars = b.barh(names, vals, color=cols)
b.axvline(floor, color=C["muted"], ls="--", lw=1.0,
          label=T(f"同样本量真样本的下限 {floor:.3f}", f"finite-sample floor {floor:.3f}"))
for bar, r in zip(bars, rows):
    b.text(bar.get_width() + 0.004, bar.get_y() + bar.get_height() / 2,
           T(f"采样 {r[2]} 次前向", f"{r[2]} pass(es)"), va="center", fontsize=8)
b.set_xlim(0, max(vals) * 1.45)
b.set_xlabel(T("柯尔莫哥洛夫—斯米尔诺夫距离（越小越好）", "KS distance (lower is better)"))
b.set_title(T("(b) 蓝色能算似然，红色不能", "(b) Blue: likelihood available; red: not"), fontsize=10)
b.legend(fontsize=8, loc="upper right")
b.grid(alpha=0.25, lw=0.5, axis="x")
b.invert_yaxis()

fig.tight_layout()
figure(fig, "fig16_1_1")
