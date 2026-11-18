"""20.2 节的图：图表示能分辨什么、不能分辨什么。

图 20.2.1：（a）两个不同的一维周期结构，所有原子对的距离完全相同——两体描述子看不见差别；
（b）截断半径一改，同一个晶体的图就变（边数与平均配位数）。
"""
import numpy as np

from _ch20 import (angle_feature, edge_histogram, homometric_pair, neighbor_graph,
                   pair_distances)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
L = 18
A, B = homometric_pair(L)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.4))

# ---------------- (a) 同距的两个结构
for row, (sites, col, name) in enumerate(((A, C["z"], T("结构甲", "structure A")),
                                          (B, C["x"], T("结构乙", "structure B")))):
    y = 1.0 - row * 0.45
    a.hlines(y, -0.6, L - 0.4, color=C["muted"], lw=0.8)
    a.plot(sites, [y] * len(sites), "o", color=col, ms=9, zorder=3)
    for s in sites:
        a.annotate(str(s), xy=(s, y), xytext=(0, 9), textcoords="offset points",
                   ha="center", fontsize=7.5, color=col)
    a.annotate(name, xy=(-0.6, y), xytext=(-6, 0), textcoords="offset points",
               ha="right", va="center", fontsize=9, color=col)

# 两套距离的直方图（叠在一起，正好完全重合）
da, db = pair_distances(A, L), pair_distances(B, L)
dd = np.arange(1, L // 2 + 2)
ca = np.array([(da == e).sum() for e in dd], dtype=float)
cb = np.array([(db == e).sum() for e in dd], dtype=float)
a.bar(dd, ca * 0.075, 0.6, bottom=0.02, color=C["z"], alpha=0.8,
      label=T("结构甲的距离分布", "pair distances of A"))
a.step(dd, cb * 0.075 + 0.02, where="mid", color=C["x"], lw=1.8,
       label=T("结构乙的（完全重合）", "and of B (identical)"))
a.annotate(T("每个原子对的距离，按长度数个数", "counts of pair distances"),
           xy=(L - 0.4, 0.06), ha="right", fontsize=8, color=C["muted"])
a.set_xlim(-2.6, L - 0.2)
a.set_ylim(-0.12, 1.42)
a.set_yticks([])
a.set_xlabel(T("位置 / 原子对距离（周期 18）", "site / pair distance (period 18)"))
a.set_title(T("(a) 两个不同的结构，距离分布一模一样",
              "(a) two different structures, identical pair distances"), fontsize=10)
a.legend(fontsize=8, loc="upper right", framealpha=0.92)

gap = float(np.abs(angle_feature(A, L) - angle_feature(B, L)).max())
a.annotate(T(f"补上三体信息（相邻两段的长短搭配）后两者分开：差 {gap:.2f}",
             f"three-body features separate them: gap {gap:.2f}"),
           xy=(0.03, 0.60), xycoords="axes fraction", ha="left",
           fontsize=8.5, color=C["accent"])

# ---------------- (b) 截断半径一改图就变
rcs = np.arange(1.5, 9.1, 0.25)
ea = [len(neighbor_graph(A, L, rc)) for rc in rcs]
eb = [len(neighbor_graph(B, L, rc)) for rc in rcs]
b.step(rcs, ea, where="post", color=C["z"], lw=2.4,
       label=T("结构甲的边数", "edges of structure A"))
b.step(rcs, eb, where="post", color=C["x"], lw=1.6, ls="--",
       label=T("结构乙的边数（还是一样）", "edges of B (identical again)"))
for rc, col in ((2.0, C["muted"]), (4.0, C["accent"]), (8.0, C["y"])):
    b.axvline(rc, color=col, ls=":", lw=1.2)
    n = len(neighbor_graph(A, L, rc))
    nb = len(edge_histogram(A, L, rc))
    b.annotate(T(f"截断 {rc:.0f}：{n} 条边、{nb} 种边长，平均配位数 {2 * n / len(A):.1f}",
                 f"cutoff {rc:.0f}: {n} edges, {nb} lengths, coordination {2 * n / len(A):.1f}"),
               xy=(rc, n), xytext=(5, -13), textcoords="offset points",
               fontsize=7.5, color=col)
b.set_xlabel(T("截断半径（人定的）", "cutoff radius (a human choice)"))
b.set_ylabel(T("图里的边数", "edges in the graph"))
b.set_title(T("(b) 同一个晶体，喂进模型的图完全不同",
              "(b) same crystal, very different graphs"), fontsize=10)
b.legend(fontsize=8, loc="upper left", framealpha=0.92)
b.margins(y=0.18)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig20_2_1")
