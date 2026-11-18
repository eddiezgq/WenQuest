"""20.1 节的图：候选空间有多大，以及真实的筛选漏斗长什么样。

图 20.1.1：（a）元数每加一，候选数两个因子同时变大——挑哪几种元素 × 每种组合的成分点数；
（b）一次公开发表的大规模筛选，四层漏斗各剩多少（数来自 `conventions/mat_facts.py`）。
"""
import numpy as np

from _ch20 import n_candidates, n_compositions
from mat_facts import M3GNET_SCREEN
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
POOL, GRID = 40, 20

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 两个因子相乘
ks = [2, 3, 4, 5]
choose = [n_candidates(POOL, k, GRID) // n_compositions(k, GRID) for k in ks]
comps = [n_compositions(k, GRID) for k in ks]
total = [n_candidates(POOL, k, GRID) for k in ks]
w = 0.26
xs = np.arange(len(ks))
a.bar(xs - w, choose, w, color=C["z"], label=T("挑哪几种元素（组合数）", "which elements"))
a.bar(xs, comps, w, color=C["y"], label=T("每种组合的成分点数", "compositions per set"))
a.bar(xs + w, total, w, color=C["x"], label=T("候选数 = 两者相乘", "candidates = product"))
for i, t in enumerate(total):
    a.annotate(f"{t:,}", xy=(i + w, t), xytext=(0, 4), textcoords="offset points",
               ha="center", fontsize=7.5, color=C["x"])
a.set_yscale("log")
a.set_xticks(xs)
a.set_xticklabels([T(f"{k} 元", f"{k}-ary") for k in ks])
a.set_ylabel(T("个数（对数轴）", "count (log scale)"))
a.set_title(T(f"(a) 元素池 {POOL} 种、成分按 {100 // GRID}% 一档",
              f"(a) pool of {POOL} elements, {100 // GRID}% composition grid"), fontsize=10)
a.legend(fontsize=8, loc="upper left", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5, axis="y")

# ---------------- (b) 一次公开筛选的四层漏斗
M = M3GNET_SCREEN
stage = [T("生成的结构", "generated"), T("预测能量够低", "predicted low-energy"),
         T("真去算了第一性原理", "actually computed"), T("算完仍然过关", "confirmed")]
left = [M["n_generated"], M["n_below_1mev"], M["n_dft_checked"], M["n_dft_confirmed"]]
cols = [C["muted"], C["z"], C["y"], C["x"]]
ys = np.arange(len(stage))[::-1]
b.barh(ys, left, 0.55, color=cols)
for y, n in zip(ys, left):
    b.annotate(f"{n:,}", xy=(n, y), xytext=(6, 0), textcoords="offset points",
               va="center", fontsize=8.5, color=C["ink"])
b.set_xscale("log")
b.set_yticks(ys)
b.set_yticklabels(stage, fontsize=9)
b.set_xlabel(T("个数（对数轴）", "count (log scale)"))
b.set_xlim(left[-1] * 0.4, left[0] * 12)
b.set_title(T("(b) 漏斗每一层掉几个数量级", "(b) each stage drops orders of magnitude"),
            fontsize=10)
b.annotate(T(f"预筛剩下的里只有 {M['n_dft_checked'] / M['n_below_1mev'] * 100:.2f}%\n"
             f"真的拿去算了，"
             f"筛选漏斗的瓶颈从来是最后一层",
             f"only {M['n_dft_checked'] / M['n_below_1mev'] * 100:.2f}% of the shortlist\n"
             f"was actually computed"),
           xy=(M["n_dft_checked"], ys[2]), xytext=(M["n_dft_checked"] * 0.012, ys[2] - 0.75),
           fontsize=8.5, color=C["accent"],
           arrowprops=dict(arrowstyle="->", color=C["accent"], lw=1.0))
b.grid(alpha=0.25, lw=0.5, axis="x")

fig.tight_layout()
figure(fig, "fig20_1_1")
