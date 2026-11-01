"""17.4 节的示意图。

图 17.4.1：（a）同等预算下，自洽多采样与提议—复核谁更划算；
（b）但它有一个前提：错法要够分散。错法一少，投票塌下去，而复核不受影响。
"""
import numpy as np

from _ch17 import propose_review, self_consistency
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.2))

calls = [2, 4, 6, 8, 12, 16]
for p, col, mk in ((0.40, C["x"], "o-"), (0.55, C["accent"], "s-"), (0.70, C["z"], "^-")):
    sc = [self_consistency(p, n, n_wrong=4, trials=8000) for n in calls]
    pr = [propose_review(p, n, tpr=0.8, fpr=0.1) for n in calls]
    a.plot(calls, sc, mk, color=col, lw=2.0, ms=5,
           label=T(f"自洽投票（单次 {p:.2f}）", f"voting (single {p:.2f})"))
    a.plot(calls, pr, mk.replace("-", "--"), color=col, lw=1.5, ms=4, alpha=0.75,
           label=T(f"提议—复核（单次 {p:.2f}）", f"propose–review (single {p:.2f})"))
a.set_xlabel(T("一共调几次模型（同等预算）", "model calls (equal budget)"))
a.set_ylabel(T("最后答对的概率", "probability the final answer is right"))
a.set_ylim(0.3, 1.02)
a.set_title(T("(a) 实线是投票，虚线是复核", "(a) Solid: voting. Dashed: propose–review"),
            fontsize=10)
a.legend(fontsize=7, ncol=2)
a.grid(alpha=0.25, lw=0.5)

P = 0.35
nws = [1, 2, 3, 4, 6, 8]
sc = [self_consistency(P, 8, n_wrong=w, trials=12000) for w in nws]
pr = propose_review(P, 8, tpr=0.8, fpr=0.1)
b.plot(nws, sc, "o-", color=C["z"], lw=2.2, ms=6, label=T("自洽投票（调 8 次）", "voting (8 calls)"))
b.axhline(pr, color=C["y"], ls="-", lw=2.0,
          label=T("提议—复核（调 8 次）", "propose–review (8 calls)"))
b.axhline(P, color=C["x"], ls="--", lw=1.6, label=T("只调一次", "a single call"))
b.fill_between([nws[0], 2.0], P, 0.2, color=C["x"], alpha=0.10)
b.annotate(T("错法一少，投票选出来的\n就是那个错答案——比只调一次还差",
             "with few ways to be wrong,\nvoting picks the wrong answer"),
           xy=(1.05, sc[0] + 0.01), xytext=(1.6, 0.80), fontsize=8.5, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.0))
b.set_xlabel(T("模型一共有几种错法", "how many different ways the model can be wrong"))
b.set_ylabel(T("最后答对的概率", "probability the final answer is right"))
b.set_ylim(0.2, 0.9)
b.set_title(T("(b) 投票靠的是错得各不相同", "(b) Voting relies on errors being diverse"),
            fontsize=10)
b.legend(fontsize=8, loc="center right")
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig17_4_1")
