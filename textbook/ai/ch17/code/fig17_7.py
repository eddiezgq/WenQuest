"""17.7 节的示意图。

图 17.7.1：案例的产线数据——二号线从第 25 天起掉产能，而且只影响最近七天里的后四天。
图 17.7.2：三种工具毛病、五种检查配置的对照表：不查的时候三种全给出确信无疑的错结论。
"""
import numpy as np

from _ch17 import agent_report, factory_data, report_ok, truth, DAYS, LINES
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

data = factory_data()
tru = truth(data)

# ---------------------------------------------------------------- 图 17.7.1
fig, (a, b) = plt.subplots(1, 2, figsize=(11.6, 4.2))

days = np.arange(1, DAYS + 1)
for i, (name, col) in enumerate(zip(LINES, (C["z"], C["x"], C["y"]))):
    a.plot(days, data[name]["output"], "-o", color=col, lw=1.6, ms=3,
           label=T(name, ("line 1", "line 2", "line 3")[i]))
a.axvspan(DAYS - 7 + 0.5, DAYS + 0.5, color=C["accent"], alpha=0.10)
a.axvspan(DAYS - 14 + 0.5, DAYS - 7 + 0.5, color=C["muted"], alpha=0.08)
a.text(DAYS - 3.5, a.get_ylim()[1] * 0.99, T("最近 7 天", "last 7 days"), ha="center",
       fontsize=8.5, color=C["accent"], va="top")
a.text(DAYS - 10.5, a.get_ylim()[1] * 0.99, T("前 7 天", "previous 7 days"), ha="center",
       fontsize=8.5, color=C["muted"], va="top")
a.axvline(25, color=C["x"], ls="--", lw=1.2)
a.annotate(T("第 25 天起二号线掉产能", "line 2 degrades from day 25"), xy=(25, 330),
           xytext=(13, 300), fontsize=9, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.0))
a.set_xlabel(T("第几天", "day"))
a.set_ylabel(T("当日产量（件）", "daily output (pieces)"))
a.set_title(T("(a) 数据里确实有这件事", "(a) The degradation really is in the data"), fontsize=10)
a.legend(fontsize=8, loc="lower left")
a.grid(alpha=0.25, lw=0.5)

names = [T(n, s) for n, s in zip(LINES, ("line 1", "line 2", "line 3"))]
vals = [tru["drop"][k] for k in LINES]
cols = [C["x"] if k == tru["worst_line"] else C["muted"] for k in LINES]
bars = b.bar(names, vals, color=cols)
for bar, val in zip(bars, vals):
    b.text(bar.get_x() + bar.get_width() / 2, val + (0.4 if val > 0 else -1.0),
           f"{val:+.1f}%", ha="center", fontsize=10)
b.axhline(0, color=C["ink"], lw=1.0)
b.set_ylabel(T("最近 7 天比前 7 天（%）", "last 7 days vs the previous 7 (%)"))
b.set_ylim(min(vals) - 3, max(vals) + 3)
b.set_title(T("(b) 标准答案：掉得最狠的是二号线",
              "(b) Ground truth: line 2 dropped the most"), fontsize=10)
b.grid(alpha=0.25, lw=0.5, axis="y")

fig.tight_layout()
figure(fig, "fig17_7_1")

# ---------------------------------------------------------------- 图 17.7.2
FAULTS = [(T("一切正常", "no fault"), None),
          (T("取成了上一周", "wrong time window"), {"fetch": "stale"}),
          (T("只取回四天", "partial data"), {"fetch": "partial"}),
          (T("一条线单位是箱", "one line in boxes"), {"fetch": "mixed"})]
CHECKS = [(T("全不开", "no checks"), ()),
          (T("只查天数", "length only"), ("length",)),
          (T("只查量级", "magnitude only"), ("range",)),
          (T("只交叉核对", "cross-check only"), ("cross",)),
          (T("三道全开", "all three"), ("length", "range", "cross"))]

M = np.zeros((len(FAULTS), len(CHECKS)))
labels = []
for i, (_, faults) in enumerate(FAULTS):
    row = []
    for j, (_, checks) in enumerate(CHECKS):
        rep, warn = agent_report(data, faults, checks)
        ok = report_ok(rep, tru)
        M[i, j] = 1.0 if ok else 0.0
        row.append(T(f"{'对' if ok else '错'}\n{rep['worst_drop_pct']:+.1f}%",
                     f"{'ok' if ok else 'wrong'}\n{rep['worst_drop_pct']:+.1f}%"))
    labels.append(row)

fig2, ax = plt.subplots(figsize=(9.6, 4.4))
ax.imshow(M, cmap="RdYlGn", vmin=-0.4, vmax=1.3, aspect="auto")
for i in range(len(FAULTS)):
    for j in range(len(CHECKS)):
        ax.text(j, i, labels[i][j], ha="center", va="center", fontsize=9)
ax.set_xticks(range(len(CHECKS)))
ax.set_xticklabels([n for n, _ in CHECKS], fontsize=9)
ax.set_yticks(range(len(FAULTS)))
ax.set_yticklabels([n for n, _ in FAULTS], fontsize=9)
ax.set_title(T("工具出毛病时，哪一道检查挡得住（格子里是结论与它给出的变化幅度）",
               "Which check catches which fault (cell shows the verdict and the reported change)"),
             fontsize=10)
fig2.tight_layout()
figure(fig2, "fig17_7_2")
