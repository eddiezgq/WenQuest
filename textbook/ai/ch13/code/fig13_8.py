"""13.8 节的示意图（数值同程序 13.8.1）。

图 13.8.1：（a）一个分数能信到几位：95% 置信区间的半宽随题数缩小，几百题的榜单上相邻两名的差别常常落在区间里；
（b）两个真实水平相差 1 个与 5 个百分点的模型，在 1000 道题上谁赢——相差 1 个点时，排名有三成的机会是反的。
"""
import math

import numpy as np

from bookout import COLORS, T, figure, style
from llm_facts import GSM8K, HUMANEVAL, MMLU

plt = style()
C = COLORS
Z = 1.959963984540054


def halfwidth(p, n):
    d = 1 + Z * Z / n
    return Z * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n)) / d * 100


fig, (a, b) = plt.subplots(1, 2, figsize=(12.0, 4.2))
ns = np.logspace(1.5, 4.5, 80)
a.loglog(ns, [halfwidth(0.7, n) for n in ns], color=C["z"], lw=1.8)
for n, name in ((HUMANEVAL["problems"], T("HumanEval 164 题", "HumanEval, 164")),
                (GSM8K["test"], T("GSM8K 1000 题", "GSM8K, 1000")),
                (MMLU["test"], T("MMLU 14 079 题", "MMLU, 14 079"))):
    h = halfwidth(0.7, n)
    a.plot([n], [h], "o", ms=7, color=C["x"])
    a.annotate(f"{name}：±{h:.1f}", (n, h), textcoords="offset points", xytext=(8, 4), fontsize=9)
a.axhline(1.0, color=C["muted"], lw=1.0, ls="--")
a.annotate(T("±1 个百分点", "±1 point"), (2000, 1.05), fontsize=9, color=C["muted"])
a.set_xlabel(T("题数", "number of items"))
a.set_ylabel(T("95% 区间的半宽（百分点）", "95% CI half-width (points)"))
a.set_title(T("(a) 分数能信到几位", "(a) How precise a score is"), fontsize=10)
a.grid(alpha=0.25, lw=0.5, which="both")

rng = np.random.default_rng(138)
N, TR = 1000, 20000
x = rng.binomial(N, 0.70, TR) / N * 100
for p, col, lab in ((0.71, C["x"], T("真实 71%", "true 71%")), (0.75, C["y"], T("真实 75%", "true 75%"))):
    y = rng.binomial(N, p, TR) / N * 100
    flip = (x > y).mean() * 100
    b.hist(y - x, bins=60, color=col, alpha=0.5, density=True,
           label=f"{lab}：{T('排名翻转', 'rank flips')} {flip:.0f}%")
b.axvline(0, color=C["ink"], lw=1.2)
b.set_xlabel(T("两个模型在同一套题上的分差（百分点）", "score difference on the same items (points)"))
b.set_ylabel(T("密度", "density"))
b.set_title(T("(b) 排名会不会翻", "(b) Will the ranking flip"), fontsize=10)
b.legend(fontsize=8)
b.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
figure(fig, "fig13_8_1")
