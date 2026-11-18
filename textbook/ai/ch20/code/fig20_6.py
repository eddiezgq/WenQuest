"""20.4 节的图：“稳定”是对参考集说的，而且是个阈值判断。

图 20.6.1：（a）一个伪二元体系的形成能下凸包；参考集里加入一个新相之后，原来落在包上的
点变成正距离——它们自己一个数都没变；（b）阈值从 0 放到 100 meV/atom，被称作“稳定”的
个数变几倍。
"""
import numpy as np

from _ch20 import convex_hull_lower, hull_distance, hull_energy_at
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

POINTS = [(0.00, 0.000), (0.10, -0.060), (0.20, -0.150), (0.25, -0.230),
          (0.30, -0.240), (0.33, -0.300), (0.40, -0.250), (0.45, -0.290),
          (0.50, -0.330), (0.55, -0.280), (0.60, -0.240), (0.67, -0.250),
          (0.75, -0.190), (0.80, -0.120), (0.90, -0.055), (1.00, 0.000)]
NEW = (0.42, -0.420)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 凸包，以及加一个相之后
d0 = hull_distance(POINTS)
d1 = hull_distance(POINTS, extra=[NEW])
hull0 = convex_hull_lower(POINTS)
hull1 = convex_hull_lower(POINTS + [NEW])

xs = np.linspace(0, 1, 400)
a.plot(xs, [hull_energy_at(hull0, x) for x in xs], color=C["z"], lw=2.0,
       label=T("原参考集的下凸包", "hull of the original reference set"))
a.plot(xs, [hull_energy_at(hull1, x) for x in xs], color=C["x"], lw=2.0, ls="--",
       label=T("加入新相之后的下凸包", "hull after adding one phase"))

flipped = [p for p in POINTS if d0[p] < 1e-12 and d1[p] > 1e-12]
for p in POINTS:
    if p in flipped:
        a.plot([p[0]], [p[1]], "s", color=C["accent"], ms=10, zorder=4)
    elif d0[p] < 1e-12:
        a.plot([p[0]], [p[1]], "o", color=C["z"], ms=8, zorder=3)
    else:
        a.plot([p[0]], [p[1]], "o", color=C["muted"], ms=6, zorder=3, alpha=0.8)
a.plot([NEW[0]], [NEW[1]], "*", color=C["x"], ms=17, zorder=5)
a.annotate(T("新算出来（或新合成出来）的一个相", "the newly added phase"),
           xy=NEW, xytext=(NEW[0] + 0.07, NEW[1] + 0.035), fontsize=8.5, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.0))
if flipped:
    p = flipped[0]
    a.annotate(T(f"原来落在包上（距离 0，“稳定”），\n现在是 {d1[p] * 1000:.0f} meV/atom——"
                 f"它自己一个数都没变",
                 f"was on the hull, now {d1[p] * 1000:.0f} meV/atom above it"),
               xy=p, xytext=(p[0] - 0.33, p[1] + 0.085), fontsize=8.5, color=C["accent"],
               arrowprops=dict(arrowstyle="->", color=C["accent"], lw=1.0))
a.set_xlabel(T("成分 x（B 的比例）", "composition x"))
a.set_ylabel(T("形成能（eV/atom，越负越稳）", "formation energy (eV/atom)"))
a.set_title(T("(a) “稳定”是相对一个参考集说的", "(a) stability is relative to a reference set"),
            fontsize=10)
a.legend(fontsize=8, loc="lower left", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 阈值一改，个数就变
thr = np.arange(0, 121, 1)
cnt = [sum(1 for d in d0.values() if d <= t / 1000 + 1e-12) for t in thr]
b.step(thr, cnt, where="post", color=C["z"], lw=2.2)
for t, col in ((0, C["muted"]), (10, C["y"]), (50, C["accent"]), (100, C["x"])):
    n = sum(1 for d in d0.values() if d <= t / 1000 + 1e-12)
    b.plot([t], [n], "o", color=col, ms=8, zorder=3)
    b.annotate(T(f"{t} meV/atom：{n} 个", f"{t} meV/atom: {n}"),
               xy=(t, n), xytext=(6, -4), textcoords="offset points",
               fontsize=8.5, color=col)
n0 = sum(1 for d in d0.values() if d < 1e-12)
n50 = sum(1 for d in d0.values() if d <= 0.05 + 1e-12)
b.set_xlabel(T("称作“稳定”所用的凸包距离阈值（meV/atom）",
               "hull-distance threshold used for 'stable' (meV/atom)"))
b.set_ylabel(T("被称作“稳定”的个数", "number called 'stable'"))
b.set_title(T("(b) 不说阈值，“发现了 N 个稳定材料”就没有意义",
              "(b) a count without its threshold means nothing"), fontsize=10)
b.annotate(T(f"阈值从 0 放到 50，个数变成 {n50 / n0:.1f} 倍（本例 {len(POINTS)} 个相）；"
             f"\n工程上用过的三个阈值分别是 10、50 与 0 meV/atom，口径互不相同",
             f"0 to 50 meV/atom: {n50 / n0:.1f}x more"),
           xy=(0.40, 0.42), xycoords="axes fraction", ha="left",
           fontsize=8.5, color=C["accent"])
b.margins(y=0.16)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig20_6_1")
