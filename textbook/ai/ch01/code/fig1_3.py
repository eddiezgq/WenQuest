"""1.3 节的示意图。

图 1.3.1：人工智能年表（1943—2024），按线索着色，灰色带为两次低谷。
图 1.3.2：ImageNet 竞赛分类任务各年冠军的前五错误率，以及人类标注者的水平。
"""
import numpy as np

from _ch1 import HUMAN_TOP5, ILSVRC, ILSVRC_2012_SECOND, TIMELINE, WINTERS
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
THREAD = {"sym": ("#8c6d1f", T("符号主义", "symbolism")), "con": ("#1f77b4", T("连接主义", "connectionism")),
          "beh": ("#2ca02c", T("行为主义与控制", "behaviourism and control")), "gen": ("#555555", T("综合与里程碑", "milestones")),
          "win": ("#9a9a9a", T("低谷", "winters"))}

# ---------------------------------------------------------------- 图 1.3.1（两栏年表）
early = [e for e in TIMELINE if e[0] < 1995]
late = [e for e in TIMELINE if e[0] >= 1995]
rows = max(len(early), len(late))
fig, ax = plt.subplots(figsize=(10.6, 5.6))
ax.set_xlim(0, 10.6)
ax.set_ylim(-1.3, rows + 0.7)
ax.axis("off")
for items, x0, head in ((early, 0.1, T("1943—1994", "1943–1994")), (late, 5.45, T("1995 年以后", "From 1995"))):
    top = rows - 0.3
    ax.text(x0, top + 0.6, head, fontsize=12, weight="bold", color=C["ink"])
    ys = [top - i * (rows - 0.6) / max(len(items) - 1, 1) for i in range(len(items))] if len(items) > 1 else [top]
    ax.plot([x0 + 0.62, x0 + 0.62], [ys[-1], ys[0]], color=C["muted"], lw=1.0, zorder=1)
    for (yr, zh_t, en_t, th), yy in zip(items, ys):
        colr = THREAD[th][0]
        if th == "win":
            ax.add_patch(plt.Rectangle((x0 + 0.72, yy - 0.3), 4.4, 0.6, color="#ececec", lw=0, zorder=0))
        ax.plot([x0 + 0.62], [yy], "o", color=colr, ms=6.5, zorder=3)
        ax.text(x0 + 0.5, yy, str(yr), ha="right", va="center", fontsize=9.2, color=C["ink"])
        ax.text(x0 + 0.8, yy, T(zh_t, en_t), ha="left", va="center", fontsize=9.2, color=C["ink"])
for k, key in enumerate(["sym", "con", "beh", "gen", "win"]):
    colr, name = THREAD[key]
    xx = 0.3 + 2.1 * k
    ax.plot([xx], [-0.9], "o", color=colr, ms=7)
    ax.text(xx + 0.15, -0.9, name, va="center", fontsize=9.5, color=C["ink"])
figure(fig, "fig1_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 1.3.2
fig, ax = plt.subplots(figsize=(7.4, 4.0))
yrs = [y for y, _, _ in ILSVRC]
err = [v for _, v, _ in ILSVRC]
cols = [C["muted"] if y < 2012 else C["z"] for y in yrs]
bars = ax.bar(yrs, err, color=cols, width=0.62)
for b, (y, v, who) in zip(bars, ILSVRC):
    ax.text(b.get_x() + b.get_width() / 2, v + 0.7, f"{v:g}%", ha="center", fontsize=9, color=C["ink"])
ax.plot([2012.31, 2012.31], [ILSVRC[2][1], ILSVRC_2012_SECOND], color=C["x"], lw=1.2)
ax.plot(2012.31, ILSVRC_2012_SECOND, "_", color=C["x"], ms=10, mew=2)
ax.text(2012.4, ILSVRC_2012_SECOND - 0.3, T(f"第二名 {ILSVRC_2012_SECOND:g}%", f"runner-up {ILSVRC_2012_SECOND:g}%"), fontsize=8.6,
        color=C["x"], va="center")
ax.axhline(HUMAN_TOP5, color=C["accent"], lw=1.4, ls="--")
ax.text(2009.5, HUMAN_TOP5 + 0.6, T(f"人类约 {HUMAN_TOP5:g}%", f"human ≈ {HUMAN_TOP5:g}%"), ha="left", fontsize=9,
        color=C["accent"])
ax.set_ylabel(T("前五错误率（%）", "top-5 error (%)"))
ax.set_ylim(0, 33)
ax.set_xlim(2009.4, 2015.6)
ax.set_xticks(yrs)
ax.set_xticklabels([f"{y}\n{who}" for y, _, who in ILSVRC], fontsize=8.6)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.text(2015.55, 31.5, T("灰色：传统特征 + 浅层分类器；蓝色：深度卷积网络", "grey: hand-crafted features; blue: deep CNNs"),
        fontsize=8.6, color=C["muted"], ha="right")
figure(fig, "fig1_3_2")
plt.close(fig)
