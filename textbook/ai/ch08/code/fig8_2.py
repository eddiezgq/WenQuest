"""8.2 节的示意图（分布与规则同程序 8.2.1）。

图 8.2.1：（a）示意的梯度绝对值分布 log₁₀|g| ~ N(−6, 1.5²)，与 FP16 的可表示范围：最小次正规数以左下溢为 0，
最小规格化数以左精度不足；乘以损失缩放因子 S = 2¹⁶ 后整个分布右移约 4.8 个数量级，几乎全部落进规格化区，最右端仍远小于最大值。
（b）动态损失缩放：S 从 2¹⁶ 开始，遇到溢出就减半并跳过这一步，连续 2000 步正常就加倍。
"""
import numpy as np

from _ch8 import FMTS
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
f = FMTS["FP16"]
fig, (a, b) = plt.subplots(1, 2, figsize=(12.5, 4.2))
lg = np.linspace(-14, 6, 600)
pdf = np.exp(-0.5 * ((lg + 6) / 1.5) ** 2)
a.fill_between(lg, pdf, color=C["z"], alpha=0.35, label=T("梯度（缩放前）", "gradients (unscaled)"))
sh = 16 * np.log10(2)
a.fill_between(lg, np.exp(-0.5 * ((lg + 6 - sh) / 1.5) ** 2), color=C["y"], alpha=0.35, label=T("乘以 S = 2¹⁶ 之后", "after × S = 2¹⁶"))
for v, lab, col in ((f.min_sub, T("最小次正规数", "min subnormal"), C["x"]), (f.min_normal, T("最小规格化数", "min normal"), C["accent"]),
                    (f.max, T("最大值 65504", "max 65504"), C["x"])):
    a.axvline(np.log10(v), color=col, lw=1, ls="--")
    a.text(np.log10(v) + 0.1, 1.02, lab, fontsize=8, color=col, rotation=90, va="bottom")
a.axvspan(-14, np.log10(f.min_sub / 2), color=C["x"], alpha=0.08)
a.set_xlim(-14, 6)
a.set_ylim(0, 1.6)
a.set_yticks([])
a.set_xlabel(T("log₁₀|梯度|", "log₁₀|gradient|"))
a.legend(frameon=False, fontsize=8, loc="upper left")
a.set_title(T("（a）FP16 的范围与梯度的分布（示意）", "(a) FP16 range and the gradient distribution (illustrative)"), fontsize=10)

rng = np.random.default_rng(82)
rng.normal(-6, 1.5, 1_000_000)                              # 与程序 8.2.1 的随机数序列保持一致
steps = 20000
gmax = 10.0 ** (-1.0 + 0.5 * np.sin(np.arange(steps) / 3000.0)) * np.where(rng.random(steps) < 0.002, 1e2, 1.0)
S, good, hist, skips = 2.0 ** 16, 0, [], []
for t in range(steps):
    if gmax[t] * S > f.max:
        skips.append(t)
        S /= 2
        good = 0
    else:
        good += 1
        if good == 2000:
            S *= 2
            good = 0
    hist.append(np.log2(S))
b.plot(hist, color=C["z"], lw=1.5)
b.plot(skips, [hist[t] for t in skips], "x", color=C["x"], ms=6, label=T("溢出，跳过这一步", "overflow, step skipped"))
b.set_xlabel(T("训练步", "step"))
b.set_ylabel(T("log₂ S", "log₂ S"))
b.legend(frameon=False, fontsize=8)
b.set_title(T("（b）动态损失缩放", "(b) Dynamic loss scaling"), fontsize=10)
fig.tight_layout()
figure(fig, "fig8_2_1")
plt.close(fig)
