"""12.3 节的示意图（规则与数值同程序 12.3.1）。

图 12.3.1：（a）CTC 的折叠规则：三条不同的帧级路径折叠后都得到"开停"；要得到"停停"这种叠字，
中间必须隔一个空白符。（b）前向算法在扩展后的目标序列（空白 开 空白 停 空白）上逐帧递推：
每个格子只能从正上方、左上方、以及跳过一个空白的左上方转移过来。
"""
import numpy as np

from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
fig, (a, b) = plt.subplots(1, 2, figsize=(12.4, 4.3), gridspec_kw={"width_ratios": [1, 1.25]})

# (a) 三条路径折叠成同一个结果
paths = [["开", "开", "_", "停", "停", "_"], ["_", "开", "_", "_", "停", "_"], ["开", "_", "停", "停", "停", "停"]]
for r, p in enumerate(paths):
    for c, sym in enumerate(p):
        col = C["muted"] if sym == "_" else (C["z"] if sym == "开" else C["x"])
        a.add_patch(plt.Rectangle((c, -r), 0.9, 0.8, fc=col, alpha=0.35 if sym == "_" else 0.6, ec="none"))
        a.text(c + 0.45, -r + 0.4, T(sym, {"开": "o", "停": "s", "_": "–"}[sym]), ha="center", va="center", fontsize=10)
    a.text(len(p) + 0.4, -r + 0.4, T("→ 开停", "→ os"), va="center", fontsize=10, color=C["ink"])
a.text(0, 1.1, T("空白符写作 _，折叠：先去重复，再去空白", "blank = –; collapse: drop repeats, then blanks"),
       fontsize=9, color=C["muted"])
a.set_xlim(-0.4, 9.2)
a.set_ylim(-2.6, 1.6)
a.axis("off")
a.set_title(T("(a) 三条路径，同一个结果", "(a) Three paths, one label"), fontsize=10)

# (b) 前向递推的格子
ext = ["_", "开", "_", "停", "_"]
T_ = 6
for s, sym in enumerate(ext):
    for t in range(T_):
        ok = (s <= 2 * t + 1) and (len(ext) - 1 - s <= 2 * (T_ - 1 - t) + 1)   # 能到达终点的格子
        b.add_patch(plt.Rectangle((t, -s), 0.86, 0.8, fc=C["z"] if ok else C["muted"],
                                  alpha=0.35 if ok else 0.12, ec="none"))
    b.text(-0.35, -s + 0.4, T(sym, {"开": "o", "停": "s", "_": "–"}[sym]), ha="right", va="center", fontsize=10)
for (t0, s0, t1, s1) in ((2, 2, 3, 2), (2, 2, 3, 1), (2, 3, 3, 1)):
    b.annotate("", (t1 + 0.1, -s1 + 0.4), (t0 + 0.8, -s0 + 0.4),
               arrowprops=dict(arrowstyle="-|>", lw=1.1, color=C["x"]))
b.text(3.1, -0.2, T("三种转移：停在原处、进一格、跳过一个空白", "three moves: stay, advance, skip a blank"),
       fontsize=9, color=C["x"])
b.set_xlabel(T("帧", "frame"))
b.set_xlim(-1.4, T_ + 0.4)
b.set_ylim(-len(ext) - 0.6, 1.2)
b.set_yticks([])
b.set_title(T("(b) 在扩展目标上的前向递推", "(b) Forward recursion over the extended target"), fontsize=10)
fig.tight_layout()
figure(fig, "fig12_3_1")
