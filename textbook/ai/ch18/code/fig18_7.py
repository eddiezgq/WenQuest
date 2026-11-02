"""18.7 节的示意图。

图 18.7.1：（a）逐残基的自评分数与真实误差——分数高的那一段确实准，可**最高档里仍有一撮
误差大得不能用**；（b）四档各是什么样。
"""
import numpy as np

from _ch18 import band_stats, protein_regions
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

R_IN, BAD = 0.68, 2.0
N_CORE, N_LINK, N_TAIL = 150, 40, 30
score, err, region = protein_regions(N_CORE, N_LINK, N_TAIL, R_IN, seed=0)
idx = np.arange(len(score))

fig, (a, b) = plt.subplots(1, 2, figsize=(11.6, 4.3),
                           gridspec_kw={"width_ratios": [1.5, 1.0]})

# ---------------- (a) 沿着序列看
for k, (name, col) in enumerate(((T("核心域", "core domain"), C["y"]),
                                 (T("连接段", "linker"), C["accent"]),
                                 (T("末端尾巴", "tail"), C["muted"]))):
    sel = region == k
    a.axvspan(idx[sel][0] - 0.5, idx[sel][-1] + 0.5, color=col, alpha=0.12)
    a.annotate(name, xy=((idx[sel][0] + idx[sel][-1]) / 2, 103), ha="center",
               fontsize=8.5, color=C["ink"])
a.plot(idx, score, "-", color=C["z"], lw=1.2, label=T("自评分数（左轴）", "self-score (left)"))
a.axhline(90, color=C["ink"], ls=":", lw=1.0)
a.axhline(70, color=C["ink"], ls=":", lw=1.0)
a.axhline(50, color=C["ink"], ls=":", lw=1.0)
a.set_ylim(0, 110)
a.set_xlabel(T("第几个残基", "residue index"))
a.set_ylabel(T("自评分数（0—100）", "self-score (0–100)"), color=C["z"])
a.tick_params(axis="y", colors=C["z"])

a2 = a.twinx()
a2.plot(idx, err, ".", color=C["x"], ms=3.2, alpha=0.75)
hi = (score >= 90) & (err > BAD)
a2.plot(idx[hi], err[hi], "o", color=C["x"], ms=7, mfc="none", mew=1.5)
a2.set_ylabel(T("真实误差（Å）", "true error (Å)"), color=C["x"])
a2.tick_params(axis="y", colors=C["x"])
a2.set_yscale("log")
a2.axhline(BAD, color=C["x"], ls="--", lw=1.0)
a2.annotate(T(f"圈出来的是“分数 ≥ 90 却错超过 {BAD:.0f} Å”的残基",
              f"circled: self-score ≥ 90 yet off by more than {BAD:.0f} Å"),
            xy=(0.03, 0.04), xycoords="axes fraction", fontsize=8, color=C["x"])
a.set_title(T("(a) 分数高的那一段确实准——但不是每个残基都准",
              "(a) High-score stretches really are accurate — but not every residue"),
            fontsize=10)

# ---------------- (b) 四档
labels, meds, bads = [], [], []
for lo, hi_, name in ((90, 101, "≥ 90"), (70, 90, "70–90"), (50, 70, "50–70"), (0, 50, "< 50")):
    n, med, bad = band_stats(score, err, lo, hi_, BAD)
    labels.append(f"{name}\n(n={n})"); meds.append(med); bads.append(bad)

pos = np.arange(4)
b.bar(pos, meds, 0.55, color=C["z"])
b.set_xticks(pos); b.set_xticklabels(labels, fontsize=8.5)
b.set_ylabel(T("误差中位数（Å）", "median error (Å)"), color=C["z"])
b.tick_params(axis="y", colors=C["z"])
b.set_xlabel(T("自评分数的档位（官方分法）", "self-score band (official bands)"))
b.grid(alpha=0.25, lw=0.5, axis="y")

b2 = b.twinx()
b2.plot(pos, bads, "o--", color=C["x"], lw=1.8, ms=7)
b2.set_ylabel(T(f"误差大于 {BAD:.0f} Å 的占比（%）", f"share off by more than {BAD:.0f} Å (%)"),
              color=C["x"])
b2.tick_params(axis="y", colors=C["x"])
b2.set_ylim(0, 105)
b2.annotate(T(f"最高档里仍有 {bads[0]:.0f}% 错超过 {BAD:.0f} Å",
              f"{bads[0]:.0f}% of the top band is still off by > {BAD:.0f} Å"),
            xy=(0, bads[0]), xytext=(0.30, 46), fontsize=8.5, color=C["x"],
            arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.0))
b.set_title(T("(b) 最高档也不是“一定对”", "(b) Even the top band is not 'certainly right'"),
            fontsize=10)

fig.tight_layout()
figure(fig, "fig18_7_1")
