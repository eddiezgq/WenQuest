"""18.4 节的示意图。

图 18.4.1：（a）绝大多数序列没有唯一的基态，有唯一基态的那些还全挤在少数几个结构上；
（b）给一个目标结构，随手挑序列与按结构挑序列，成功率差两个量级——但都远不是百发百中。
"""
import collections

import numpy as np

from _ch18 import (all_sequences, contacts, design_sequence, designability,
                   enumerate_folds, unique_structures)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

N = 12
folds_all = enumerate_folds(N)
reps, fc = unique_structures(folds_all, [contacts(f) for f in folds_all])
lo, deg, arg = designability(N, fc)
uniq = deg == 1
cnt = collections.Counter(arg[uniq].tolist())
counts = np.array(sorted(cnt.values(), reverse=True))

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 可设计性
a.bar(np.arange(len(counts)), counts, color=C["z"], width=0.85)
a.set_xlabel(T(f"被唯一折成的 {len(counts)} 个结构（按序列数排序）",
               f"the {len(counts)} structures that are uniquely folded to (sorted)"))
a.set_ylabel(T("有多少条序列折成它", "how many sequences fold to it"))
a.set_title(T("(a) 少数结构被很多条序列折成", "(a) A few structures are highly designable"),
            fontsize=10)
a.grid(alpha=0.25, lw=0.5, axis="y")
a.annotate(T(f"{2 ** N} 条序列里只有 {int(uniq.sum())} 条有唯一基态\n"
             f"它们只落在 {len(counts)} 个结构上（全部 {len(fc)} 个）",
             f"only {int(uniq.sum())} of {2 ** N} sequences have a unique ground state;\n"
             f"they land on just {len(counts)} of the {len(fc)} structures"),
           xy=(0.42, 0.72), xycoords="axes fraction", fontsize=8.5, color=C["ink"])

# ---------------- (b) 随手挑 vs 按结构挑
seqs = all_sequences(N)
ok = 0
for st in cnt:
    s = design_sequence(fc[st], N)
    bits = np.array([1 if ch == "H" else 0 for ch in s], dtype=np.int8)
    r = int(np.where((seqs == bits).all(1))[0][0])
    if deg[r] == 1 and arg[r] == st:
        ok += 1
rand_pct = cnt.most_common(1)[0][1] / 2 ** N * 100
design_pct = ok / len(cnt) * 100

bars = b.bar([0, 1], [rand_pct, design_pct], color=[C["muted"], C["y"]], width=0.5)
b.set_yscale("log")
b.set_xticks([0, 1])
b.set_xticklabels([T("随手挑一条序列", "pick a sequence at random"),
                   T("按目标结构挑", "pick it from the target structure")])
b.set_ylabel(T("折成目标结构的比例（%，对数）", "share that folds to the target (%, log)"))
b.set_title(T("(b) 按结构挑，好两个量级——但也不是百发百中",
              "(b) Designing helps by two orders of magnitude — but is not a sure thing"),
            fontsize=10)
for rect, val in zip(bars, (rand_pct, design_pct)):
    b.annotate(f"{val:.2f}%", xy=(rect.get_x() + rect.get_width() / 2, val),
               xytext=(0, 4), textcoords="offset points", ha="center", fontsize=9)
b.axhline(100, color=C["x"], ls=":", lw=1.2)
b.annotate(T("百发百中", "100%"), xy=(0.01, 0.80), xycoords="axes fraction",
           fontsize=8, color=C["x"], va="bottom")
b.set_ylim(0.1, 300)
b.grid(alpha=0.25, lw=0.5, axis="y", which="both")

fig.tight_layout()
figure(fig, "fig18_4_1")
