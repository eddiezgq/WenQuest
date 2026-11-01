"""16.7 节的示意图。

图 16.7.1：（a）水印检得出来是因为两堆数分得开——带水印的接近 1，错密钥的挤在 0 附近；
（b）四种常见处理之后还剩多少：压缩与裁剪扛得住，噪声加到和内容一个量级就失效。
"""
import numpy as np

from _ch16 import attack, content, detect, watermark
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

KEY, STRENGTH, N = 7, 0.05, 4096
x = content(N, 0)
w = watermark(x, KEY, STRENGTH)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.2))

wrong = [detect(w, k) for k in range(2000, 2600)]
plain = [detect(content(N, s), KEY) for s in range(1, 200)]
a.hist(wrong, bins=40, color=C["muted"], alpha=0.75, linewidth=0,
       label=T("密钥不对（600 次）", "wrong key (600 trials)"))
a.hist(plain, bins=40, color=C["z"], alpha=0.6, linewidth=0,
       label=T("没嵌水印（199 段）", "unmarked content (199 clips)"))
a.axvline(detect(w, KEY), color=C["y"], lw=2.4,
          label=T(f"密钥对上：{detect(w, KEY):.3f}", f"correct key: {detect(w, KEY):.3f}"))
a.axvline(0.1, color=C["x"], ls="--", lw=1.4, label=T("门限 0.1", "threshold 0.1"))
a.set_xlabel(T("检测量（高通之后与密钥序列的相关系数）",
                "detection statistic (correlation after high-pass)"))
a.set_ylabel(T("次数", "count"))
a.set_xlim(-0.15, 1.05)
a.set_title(T("(a) 两堆数分得很开，门限好定", "(a) The two populations separate cleanly"), fontsize=10)
a.legend(fontsize=8, loc="upper center")
a.grid(alpha=0.25, lw=0.5)

levels = np.linspace(0.05, 1.0, 12)
styles = [("noise", T("加噪声", "additive noise"), C["x"], "o-"),
          ("quantize", T("量化（相当于压缩）", "quantization (≈ compression)"), C["z"], "s-"),
          ("crop", T("截掉一段", "cropping"), C["y"], "^-"),
          ("resample", T("下采样再插回来", "down- then up-sampling"), C["accent"], "d-")]
for kind, lab, col, mk in styles:
    vals = [detect(attack(w, kind, float(lv)), KEY) for lv in levels]
    b.plot(levels, vals, mk, color=col, lw=1.6, ms=4, label=lab)
b.axhline(0.1, color=C["muted"], ls="--", lw=1.2, label=T("门限 0.1", "threshold 0.1"))
b.set_xlabel(T("处理的强度", "strength of the processing"))
b.set_ylabel(T("检测量", "detection statistic"))
b.set_ylim(-0.05, 1.05)
b.set_title(T("(b) 扛得住压缩，扛不住大噪声", "(b) Survives compression, not heavy noise"), fontsize=10)
b.legend(fontsize=8)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig16_7_1")
