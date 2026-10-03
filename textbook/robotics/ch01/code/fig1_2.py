"""1.2 节的示意图。

图 1.2.1：机器人发展年表（四条线索：自动机与程序、反馈与控制、工业机器人、智能与移动）。
图 1.2.2：2024、2025 年工业机器人安装量最多的五个国家（IFR《World Robotics》2025、2026）。
"""
import numpy as np

from _ch1 import IFR, TIMELINE
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
THREAD = {"auto": ("#8c6d1f", T("自动机与程序", "automata and programs")),
          "ctrl": ("#2ca02c", T("反馈与控制", "feedback and control")),
          "ind": ("#1f77b4", T("工业机器人", "industrial robots")),
          "ai": ("#d62728", T("智能、移动与学习", "intelligence, mobility and learning"))}


def year_text(y):
    if y < 0:
        return T(f"约公元前 {-y} 年", f"c. {-y} BC")
    if y < 1000:
        return T(f"约公元 {y} 年", f"c. AD {y}")
    return str(y)


# ---------------------------------------------------------------- 图 1.2.1
early = [e for e in TIMELINE if e[0] < 1950]
late = [e for e in TIMELINE if e[0] >= 1950]
rows = max(len(early), len(late))
fig, ax = plt.subplots(figsize=(10.4, 7.6))
ax.set_xlim(0, 10.4)
ax.set_ylim(-1.6, rows + 0.6)
ax.axis("off")
for col, items, x0, head in ((0, early, 0.2, T("1950 年以前", "Before 1950")), (1, late, 5.3, T("1950 年以后", "From 1950"))):
    top = rows - 0.2
    ax.text(x0, top + 0.55, head, fontsize=12, weight="bold", color=C["ink"])
    step = (rows - 0.4) / max(len(items) - 1, 1) if col == 0 else 1.0
    ys = [top - i * step for i in range(len(items))]
    ax.plot([x0 + 1.05, x0 + 1.05], [ys[-1], ys[0]], color=C["muted"], lw=1.0, zorder=1)
    for (y, zh_en, _en, th), yy in zip(items, ys):
        col_th = THREAD[th][0]
        ax.plot([x0 + 1.05], [yy], "o", color=col_th, ms=6, zorder=3)
        ax.text(x0 + 0.95, yy, year_text(y), ha="right", va="center", fontsize=8.6, color=C["ink"])
        ax.text(x0 + 1.2, yy, T(zh_en, _en), ha="left", va="center", fontsize=8.6, color=C["ink"])
LEG_X = (0.3, 2.85, 5.4, 7.95) if T("zh", "en") == "zh" else (0.2, 2.45, 4.45, 6.1)
for k, (key, (colr, name)) in enumerate(THREAD.items()):
    xx = LEG_X[k]
    ax.plot([xx], [-1.1], "o", color=colr, ms=7)
    ax.text(xx + 0.15, -1.1, name, va="center", fontsize=9.5, color=C["ink"])
figure(fig, "fig1_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 1.2.2
fig, ax = plt.subplots(figsize=(6.4, 3.6))
names = [T(c[0], c[1]) for c in IFR["country"]]
a24 = np.array([c[2] for c in IFR["country"]]) / 1000
a25 = np.array([c[3] for c in IFR["country"]]) / 1000
x = np.arange(len(names))
w = 0.38
b1 = ax.bar(x - w / 2, a24, w, color="#9fb4c8", label="2024")
b2 = ax.bar(x + w / 2, a25, w, color=C["z"], label="2025")
for bars, year in ((b1, 2024), (b2, 2025)):
    for b, c in zip(bars, IFR["country"]):
        lab = f"<{b.get_height():.0f}" if year == 2025 and c[0] in IFR.get("upper_2025", []) else f"{b.get_height():.1f}"
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 4, lab, ha="center", fontsize=7.8,
                color=C["ink"])
ax.set_xticks(x)
ax.set_xticklabels(names)
ax.set_ylabel(T("年安装量（千台）", "installations (thousand units)"))
ax.set_ylim(0, 400)
ax.legend(frameon=False, fontsize=9)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.text(1.0, -0.2, T("数据：IFR《World Robotics》2025、2026", "Data: IFR World Robotics 2025, 2026"), transform=ax.transAxes,
        ha="right", fontsize=8, color=C["muted"])
figure(fig, "fig1_2_2")
plt.close(fig)
