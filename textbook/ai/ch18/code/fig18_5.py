"""18.5 节的示意图。

图 18.5.1：（a）同一个打分函数，阳性比例一变，命中率就天差地别，而富集因子基本不动；
（b）随机划分与骨架划分把两个模型的名次排**反**了。
"""
import numpy as np

from _ch18 import (auc_score, enrichment, fit_logistic, hit_rate, knn_score,
                   library, molecules, predict, split_random, split_scaffold)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 命中率 vs 富集因子
FRACS = (0.01, 0.03, 0.1, 0.3, 1.0)
hits, efs = [], []
for f in FRACS:
    s, act = library(200_000, f / 100, seed=1, auc=0.80)
    hits.append(hit_rate(s, act, 100))
    efs.append(enrichment(s, act, 0.01))
a.semilogx(FRACS, hits, "o-", color=C["x"], lw=2.0, ms=6,
           label=T("买 100 个来测的命中率（%）", "hit rate among the top 100 tested (%)"))
a.set_xlabel(T("库里本来有多少阳性（%）", "share of actives in the library (%)"))
a.set_ylabel(T("命中率（%）", "hit rate (%)"), color=C["x"])
a.tick_params(axis="y", colors=C["x"])
a.set_title(T("(a) 打分函数一点没变，命中率却差一个量级",
              "(a) Same scoring function, hit rate differs by an order of magnitude"),
            fontsize=10)
a.grid(alpha=0.25, lw=0.5, which="both")

a2 = a.twinx()
a2.semilogx(FRACS, efs, "s--", color=C["z"], lw=1.8, ms=5,
            label=T("富集因子 EF 1%", "enrichment factor EF 1%"))
a2.set_ylabel(T("富集因子 EF 1%", "enrichment factor EF 1%"), color=C["z"])
a2.tick_params(axis="y", colors=C["z"])
a2.set_ylim(0, max(efs) * 1.6)
a.annotate(T("变的只是库里本来有多少阳性\n——富集因子基本不动",
             "only the base rate changed;\nthe enrichment factor barely moves"),
           xy=(0.22, 0.60), xycoords="axes fraction", fontsize=8.5, color=C["ink"])

# ---------------- (b) 两种划分，两个模型
N_MOL, N_SCAF = 4000, 220
x, y, scaf = molecules(N_MOL, N_SCAF, seed=2)
res = {}
for name, sp in (("random", lambda sd: split_random(N_MOL, seed=sd)),
                 ("scaffold", lambda sd: split_scaffold(scaf, seed=sd))):
    knn, lin = [], []
    for sd in range(12):
        tr, te = sp(sd)
        knn.append(auc_score(y[te], knn_score(x[tr], y[tr], x[te])))
        w = fit_logistic(x[tr], y[tr])
        lin.append(auc_score(y[te], predict(w, x[te])))
    res[name] = (np.mean(knn), np.std(knn), np.mean(lin), np.std(lin))

pos = np.array([0, 1])
w_ = 0.34
b.bar(pos - w_ / 2, [res["random"][0], res["scaffold"][0]], w_,
      yerr=[res["random"][1], res["scaffold"][1]], capsize=4, color=C["x"],
      label=T("会记类似物的模型（最近邻）", "a model that memorizes analogues (kNN)"))
b.bar(pos + w_ / 2, [res["random"][2], res["scaffold"][2]], w_,
      yerr=[res["random"][3], res["scaffold"][3]], capsize=4, color=C["z"],
      label=T("只会用真信号的模型（线性）", "a model that can only use the real signal (linear)"))
b.axhline(0.5, color=C["muted"], ls=":", lw=1.2)
b.annotate(T("瞎猜", "chance"), xy=(0.01, 0.10), xycoords="axes fraction",
           fontsize=8, color=C["muted"])
b.set_xticks(pos)
b.set_xticklabels([T("随机划分", "random split"), T("骨架划分", "scaffold split")])
b.set_ylabel("ROC-AUC")
b.set_ylim(0.45, 1.0)
b.set_title(T("(b) 换个划分，两个模型的名次排反了",
              "(b) Change the split and the two models swap places"), fontsize=10)
b.legend(fontsize=8, loc="upper right")
b.grid(alpha=0.25, lw=0.5, axis="y")

fig.tight_layout()
figure(fig, "fig18_5_1")
