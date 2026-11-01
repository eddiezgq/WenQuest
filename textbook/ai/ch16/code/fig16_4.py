"""16.4 节的示意图。

图 16.4.1：无分类器引导拿多样性换"像"。（a）引导强度一调大，采出来的分布就从真条件分布
（黑线）往一个峰上挤；（b）两条曲线反着走：单张更"像这一类"，分布却越来越偏，
两类共用的那个峰被挤没了。右边同时列出引导论文自己的 FID / IS 表，方向完全一致。
"""
import numpy as np

from _ch16 import (cond_cdf, cond_pdf, diffusion_fit, diffusion_sample, guided, ks, mix_sample,
                   mode_share, sharpness, COND_MU)
from bookout import COLORS, T, figure, style
from gen_facts import CFG

plt = style()
C = COLORS

train = mix_sample(8000, 0)
model = diffusion_fit(train)
abar = model["abar"]
CLS = 0
grid = np.linspace(-4.5, 5.0, 500)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.6, 4.3))

a.plot(grid, cond_pdf(CLS, grid), color=C["ink"], lw=2.2,
       label=T("真条件分布", "true conditional"), zorder=5)
for wg, col in ((0.0, C["z"]), (1.0, C["accent"]), (4.0, C["x"])):
    x = diffusion_sample(model, 6000, steps=200, guide=guided(CLS, wg, abar), seed=0)
    a.hist(x, bins=80, density=True, histtype="step", lw=1.5, color=col,
           label=T(f"引导强度 w = {wg:g}", f"guidance w = {wg:g}"))
a.axvline(COND_MU[CLS][1], color=C["muted"], ls=":", lw=1.2)
a.text(COND_MU[CLS][1] + 0.12, a.get_ylim()[1] * 0.92,
       T("两类共用的峰", "mode shared\nwith the other class"), fontsize=8, color=C["muted"])
a.set_xlabel(T("样本的取值", "value"))
a.set_ylabel(T("密度", "density"))
a.set_title(T("(a) 引导越强，越往一个峰上挤", "(a) Stronger guidance, narrower support"), fontsize=10)
a.legend(fontsize=8)
a.grid(alpha=0.25, lw=0.5)

ws = [0.0, 0.3, 0.6, 1.0, 2.0, 4.0, 8.0]
sharp, kss, share2 = [], [], []
for wg in ws:
    x = diffusion_sample(model, 6000, steps=200, guide=guided(CLS, wg, abar), seed=0)
    sharp.append(sharpness(x, CLS))
    kss.append(ks(x, lambda t: cond_cdf(CLS, t)))
    share2.append(float(mode_share(x, CLS)[1]))

b.plot(ws, sharp, "o-", color=C["y"], lw=1.8, ms=5,
       label=T("单张有多像这一类（平均对数密度）", "how typical each sample is (mean log-density)"))
b.set_xlabel(T("引导强度 w", "guidance strength w"))
b.set_ylabel(T("平均对数密度（越大越像）", "mean log-density (higher = more typical)"), color=C["y"])
b.tick_params(axis="y", labelcolor=C["y"])
b.grid(alpha=0.25, lw=0.5)

c2 = b.twinx()
c2.plot(ws, kss, "s--", color=C["x"], lw=1.6, ms=5,
        label=T("与真条件分布的 KS 距离", "KS distance to the true conditional"))
c2.plot(ws, share2, "^:", color=C["z"], lw=1.6, ms=5,
        label=T("共用那个峰的占比", "share of the shared mode"))
c2.set_ylabel(T("偏离程度 / 占比", "deviation / share"))
lines = b.get_lines() + c2.get_lines()
b.legend(lines, [l.get_label() for l in lines], fontsize=7.5, loc="center right")
b.set_title(T("(b) 两件事反着走", "(b) The two move in opposite directions"), fontsize=10)

# 引导论文自己的表，摆在图注里对照
pairs = [(w, CFG["in64"][w][0], CFG["in64"][w][1]) for w in (0.0, 0.1, 0.3, 1.0, 4.0)]
txt = T("引导论文（ImageNet 64×64）：w = " + "，".join(f"{w:g} → FID {f}/IS {i:.0f}" for w, f, i in pairs),
        "Guidance paper (ImageNet 64×64): " + ", ".join(f"w={w:g} → FID {f}/IS {i:.0f}" for w, f, i in pairs))
fig.text(0.5, 0.005, txt, ha="center", fontsize=7.5, color=C["muted"])

fig.tight_layout(rect=(0, 0.035, 1, 1))
figure(fig, "fig16_4_1")
