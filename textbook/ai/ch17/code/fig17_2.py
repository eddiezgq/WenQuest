"""17.2 节的示意图。

图 17.2.1：（a）三种选法在同一个任务上的命中率随上下文预算怎么走；
（b）任务要改的三个文件是被符号串起来的——词面检索只够到第二个，两跳才够到第三个。
"""
import numpy as np

from _ch17 import make_repo, make_task, recall, select_lexical, select_recent, select_symbol_graph
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

BUDGETS = [5_000, 10_000, 20_000, 30_000, 60_000, 100_000]
SEEDS = 10
methods = [(T("按最近编辑", "most recently edited"), select_recent, {}, C["muted"], "o-"),
           (T("按词面检索", "lexical retrieval"), select_lexical, {}, C["x"], "s-"),
           (T("符号图（一跳）", "symbol graph, 1 hop"), select_symbol_graph, {"hops": 1}, C["accent"], "^-"),
           (T("符号图（两跳）", "symbol graph, 2 hops"), select_symbol_graph, {"hops": 2}, C["z"], "d-")]

fig, (a, b) = plt.subplots(1, 2, figsize=(11.6, 4.3))

repos = [make_repo(seed=s) for s in range(SEEDS)]
tasks = [make_task(repos[s], seed=s) for s in range(SEEDS)]
for name, fn, kw, col, mk in methods:
    ys = []
    for budget in BUDGETS:
        rc = [recall(fn(repos[s], tasks[s], budget, **kw)[0], tasks[s]) for s in range(SEEDS)]
        ys.append(float(np.mean(rc)))
    a.plot([x / 1000 for x in BUDGETS], ys, mk, color=col, lw=1.9, ms=5, label=name)
a.set_xlabel(T("上下文预算（千词元）", "context budget (thousand tokens)"))
a.set_ylabel(T("要改的文件找回了几成", "share of the files to edit that were found"))
a.set_ylim(-0.03, 1.05)
a.set_title(T("(a) 选法不对，预算加十倍也没用",
              "(a) With the wrong selector, ten times the budget buys nothing"), fontsize=10)
a.legend(fontsize=8, loc="center right")
a.grid(alpha=0.25, lw=0.5)

# （b）示意：一条 issue 提到符号 s，改动顺着符号链走
FOUND, DEEP = C["x"], C["z"]
nodes = [(0.14, 0.70, T("issue 提到\n符号 s", "issue mentions\nsymbol s"), C["muted"]),
         (0.46, 0.70, T("文件 A\n定义 s", "file A\ndefines s"), FOUND),
         (0.78, 0.70, T("文件 B\n用 s，定义 t", "file B\nuses s, defines t"), FOUND),
         (0.78, 0.30, T("文件 C\n用 t", "file C\nuses t"), DEEP)]
for x, y, label, col in nodes:
    b.add_patch(plt.Rectangle((x - 0.13, y - 0.10), 0.26, 0.20, facecolor="white",
                              edgecolor=col, lw=2.0, zorder=3))
    b.text(x, y, label, ha="center", va="center", fontsize=9, zorder=4)
for (x1, y1), (x2, y2) in (((0.14, 0.70), (0.46, 0.70)), ((0.46, 0.70), (0.78, 0.70)),
                           ((0.78, 0.60), (0.78, 0.40))):
    b.annotate("", xy=(x2, y2), xytext=(x1, y1), zorder=2,
               arrowprops=dict(arrowstyle="-|>", color=C["muted"], lw=1.8,
                               shrinkA=14, shrinkB=14))
b.add_patch(plt.Rectangle((0.03, 0.10), 0.03, 0.045, facecolor="white", edgecolor=FOUND, lw=2.0))
b.text(0.08, 0.1225, T("词面检索就能找到（三个里的两个）",
                       "found by lexical retrieval (two of the three)"),
       va="center", fontsize=8.5)
b.add_patch(plt.Rectangle((0.03, 0.02), 0.03, 0.045, facecolor="white", edgecolor=DEEP, lw=2.0))
b.text(0.08, 0.0425, T("要顺着符号再走一跳才找得到", "needs one more hop along the symbols"),
       va="center", fontsize=8.5)
b.set_xlim(-0.01, 0.95)
b.set_ylim(0.0, 0.92)
b.axis("off")
b.set_title(T("(b) 要改的文件是被符号串起来的",
              "(b) The files to edit are chained by symbols"), fontsize=10)

fig.tight_layout()
figure(fig, "fig17_2_1")
