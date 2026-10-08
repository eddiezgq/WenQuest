"""13.6 节的示意图（数值同程序 13.6.1）。

图 13.6.1：（a）召回率与代价此消彼长：切片越长、取回越多，召回越高，送进模型的词元也越多；
（b）同一套检索，问法一换就掉：手册原词问 vs 工人口语问，三种检索加上同义词表与零件号加权的对照。
"""
import numpy as np

from _ch13 import chunks, manual, questions, recall, retrieve
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
MAN, QS = manual(), questions()
ANS = [q for q in QS if q["answerable"]]
K = 5

fig, (a, b) = plt.subplots(1, 2, figsize=(12.0, 4.2))
sizes = (150, 300, 600, 1200)
rc, tok = [], []
for size in sizes:
    ch = chunks(MAN, size, size // 5)
    rc.append(100 * float(np.mean([recall(retrieve(q["q"], ch, K, "bm25"), ch, q["gold"]) for q in ANS])))
    tok.append(size * K / 1.5)
a.plot(tok, rc, "o-", color=C["z"], lw=1.8, ms=7)
for t, r, s in zip(tok, rc, sizes):
    a.annotate(T(f"{s} 字一片", f"{s} chars"), (t, r), textcoords="offset points", xytext=(6, -12), fontsize=9)
a.set_xlabel(T("每个问题送进模型的词元数", "tokens sent per question"))
a.set_ylabel(T("召回率（%）", "recall (%)"))
a.set_title(T("(a) 召回率与代价", "(a) Recall against cost"), fontsize=10)
a.grid(alpha=0.25, lw=0.5)

CH = chunks(MAN, 300, 60)
methods = [("bm25", T("词频", "BM25")), ("vector", T("哈希向量", "hashed vectors")),
           ("hybrid", T("混合", "hybrid")), ("hybrid+syn+part", T("混合+同义词+零件号", "hybrid+syn+part"))]
book, shop = [], []
for how, _ in methods:
    book.append(100 * float(np.mean([recall(retrieve(q["q"], CH, K, how), CH, q["gold"]) for q in ANS])))
    shop.append(100 * float(np.mean([recall(retrieve(q["q2"], CH, K, how), CH, q["gold"]) for q in ANS])))
x = np.arange(len(methods))
b.bar(x - 0.19, book, 0.36, color=C["z"], label=T("按手册原词问", "worded like the manual"))
b.bar(x + 0.19, shop, 0.36, color=C["x"], label=T("工人口语问", "worded like the shop floor"))
for i, (bb, ss) in enumerate(zip(book, shop)):
    b.text(i - 0.19, bb + 1.5, f"{bb:.0f}", ha="center", fontsize=8)
    b.text(i + 0.19, ss + 1.5, f"{ss:.0f}", ha="center", fontsize=8)
b.set_xticks(x)
b.set_xticklabels([n for _, n in methods], fontsize=8)
b.set_ylabel(T("召回率（%）", "recall (%)"))
b.set_ylim(0, 112)
b.set_title(T("(b) 问法一换就掉", "(b) Rewording breaks retrieval"), fontsize=10)
b.legend(fontsize=8, loc="lower right")
b.grid(alpha=0.25, lw=0.5, axis="y")
fig.tight_layout()
figure(fig, "fig13_6_1")
