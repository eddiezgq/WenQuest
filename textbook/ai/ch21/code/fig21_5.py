"""21.4 节的图：在产线上调参数，好点总在废品区边上。

图 21.4.1：（a）参数平面——质量等高线、废品区、产出等值线，以及三种办法试过的点；
（b）合格线一提，最优点就往回缩，产出要让出多少。
"""
import numpy as np

from _ch21 import best_feasible, cut_quality, search_parameters
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
BUDGET = 40

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.4))

# ---------------- (a) 参数平面
ax = np.linspace(0.05, 0.95, 181)
S, F = np.meshgrid(ax, ax)
Q = np.vectorize(cut_quality)(S, F)
a.contourf(S, F, (Q < 0.72).astype(float), levels=[0.5, 1.5],
           colors=[C["x"]], alpha=0.12)
cs = a.contour(S, F, Q, levels=[0.72, 0.80, 0.86, 0.92], colors=C["muted"],
               linewidths=1.0)
a.clabel(cs, fmt=lambda q: T(f"质量 {q:.2f}", f"quality {q:.2f}"), fontsize=7)
rate = a.contour(S, F, S * F, levels=[0.15, 0.25, 0.35], colors=C["z"],
                 linewidths=1.0, linestyles="--")
a.clabel(rate, fmt=lambda q: T(f"产出 {q:.2f}", f"rate {q:.2f}"), fontsize=7)

for method, col, name in (("free", C["muted"], T("随机搜索", "random search")),
                          ("ofat", C["y"], T("单因素轮换", "one factor at a time")),
                          ("trust", C["x"], T("代理模型 + 信赖域", "surrogate + trust region"))):
    r = search_parameters(method, BUDGET, seed=3)
    pts = r["tried"]
    a.plot(pts[:, 0], pts[:, 1], "o", color=col, ms=3.6, alpha=0.75, label=name)
    a.plot([r["best"][0]], [r["best"][1]], "*", color=col, ms=15, zorder=4)

bs, bf, best_val = best_feasible()
a.plot([bs], [bf], "P", color=C["accent"], ms=12, zorder=5)
a.annotate(T(f"真正的最优：({bs:.2f}, {bf:.2f})，就贴着合格线",
             f"true optimum ({bs:.2f}, {bf:.2f}), right on the limit"),
           xy=(bs, bf), xytext=(-12, 14), textcoords="offset points",
           ha="right", fontsize=8.5, color=C["accent"],
           arrowprops=dict(arrowstyle="->", color=C["accent"], lw=1.0))
a.annotate(T("淡红区域 = 做出来就是废品", "shaded: parts come out scrap"),
           xy=(0.04, 0.93), xycoords="axes fraction", ha="left",
           fontsize=8.5, color=C["x"])
a.set_xlabel(T("切削速度（归一化）", "cutting speed (normalised)"))
a.set_ylabel(T("进给（归一化）", "feed (normalised)"))
a.set_title(T("(a) 好参数总在废品区的边上", "(a) good settings sit against the scrap region"),
            fontsize=10)
a.legend(fontsize=8, loc="lower right", framealpha=0.92)

# ---------------- (b) 合格线与产出的取舍
lines = np.linspace(0.70, 0.90, 21)
vals, speeds = [], []
for line in lines:
    best, bsx, bfx = -1.0, 0.0, 0.0
    for s in ax:
        for f in ax:
            q = cut_quality(float(s), float(f))
            val = 0.0 if q < line else float(s) * float(f)
            if val > best:
                best, bsx, bfx = val, float(s), float(f)
    vals.append(best)
    speeds.append(bsx)
vals = np.array(vals)
b.plot(lines, vals / vals[0] * 100, "o-", color=C["x"], lw=2.2, ms=4)
for line in (0.72, 0.80, 0.86):
    i = int(np.argmin(np.abs(lines - line)))
    b.plot([lines[i]], [vals[i] / vals[0] * 100], "o", color=C["accent"], ms=9, zorder=3)
    b.annotate(T(f"合格线 {line:.2f} → 产出 {vals[i] / vals[0] * 100:.0f}%",
                 f"limit {line:.2f} → {vals[i] / vals[0] * 100:.0f}% of the rate"),
               xy=(lines[i], vals[i] / vals[0] * 100), xytext=(6, 8),
               textcoords="offset points", fontsize=8.5, color=C["accent"])
b.set_xlabel(T("质量合格线", "quality acceptance limit"))
b.set_ylabel(T("能拿到的产出（以合格线 0.70 为 100%）",
               "attainable rate (limit 0.70 = 100%)"))
b.set_title(T("(b) 质量与产出的取舍是一条算得出来的曲线",
              "(b) the quality-throughput trade-off is a computable curve"), fontsize=10)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig21_4_1")
