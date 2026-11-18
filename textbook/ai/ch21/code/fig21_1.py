"""21.1 节的图：数据在哪一层丢掉。

图 21.1.1：（a）扫码取整把工时记长了多少——**工序越短，被放大得越厉害**；
（b）两台服务器的时钟差多大，按工序时刻去截传感器信号就会截错多少零件。
"""
import numpy as np

from _ch21 import STATIONS, cycle_time, make_batch
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N_PARTS = 40

b = make_batch(N_PARTS, seed=0, drift_s=0.0, mes_round_s=60.0)

fig, (a, c) = plt.subplots(1, 2, figsize=(11.4, 4.4))

# ---------------- (a) 取整把短工序放大
rows = []
for st in STATIONS:
    cs, cm = cycle_time(b["sensor"], st), cycle_time(b["mes"], st)
    rows.append((st, cs, cm / cs))
rows.sort(key=lambda r: r[1])
names = [r[0] for r in rows]
secs = np.array([r[1] for r in rows])
ratio = np.array([r[2] for r in rows])
ys = np.arange(len(rows))
cols = [C["x"] if r > 1.5 else (C["accent"] if r > 1.15 else C["z"]) for r in ratio]
a.barh(ys, ratio, 0.6, color=cols)
a.axvline(1.0, color=C["ink"], ls=":", lw=1.2)
for y, (r, s) in enumerate(zip(ratio, secs)):
    a.annotate(T(f"×{r:.2f}（真实 {s:.0f} 秒）", f"×{r:.2f} (true {s:.0f} s)"),
               xy=(r, y), xytext=(5, 0), textcoords="offset points",
               va="center", fontsize=7.5, color=C["ink"])
a.set_yticks(ys)
a.set_yticklabels(names, fontsize=8.5)
a.set_xlim(0.9, max(ratio) * 1.45)
a.set_xlabel(T("制造执行系统记的工时 ÷ 真实工时", "logged cycle time ÷ true cycle time"))
a.set_title(T("(a) 扫码取整到 60 秒：工序越短，记得越长",
              "(a) 60-second rounding: short operations inflate most"), fontsize=10)
a.grid(alpha=0.25, lw=0.5, axis="x")

# ---------------- (b) 时钟差与错配
drifts = np.arange(0, 301, 15)
wrong = []
for d in drifts:
    bb = make_batch(N_PARTS, seed=0, drift_s=float(d), mes_round_s=60.0)
    bad = 0
    for s_row, m_row in zip(b["sensor"], bb["mes"]):
        mid = (m_row["start"] + m_row["end"]) / 2.0
        if not (s_row["start"] <= mid <= s_row["end"]):
            bad += 1
    wrong.append(bad / len(b["sensor"]) * 100)
wrong = np.array(wrong)
c.plot(drifts, wrong, "o-", color=C["x"], lw=2.2, ms=4)
for d in (30, 90, 300):
    i = int(np.argmin(np.abs(drifts - d)))
    c.plot([drifts[i]], [wrong[i]], "o", color=C["accent"], ms=9, zorder=3)
    c.annotate(T(f"差 {d} 秒 → {wrong[i]:.0f}%", f"{d} s → {wrong[i]:.0f}%"),
               xy=(drifts[i], wrong[i]), xytext=(8, -12), textcoords="offset points",
               fontsize=8.5, color=C["accent"])
c.set_xlabel(T("两台服务器的时钟差（秒）", "clock offset between servers (s)"))
c.set_ylabel(T("截到别的时间段的零件占比（%）",
               "share of parts whose signal window is wrong (%)"))
c.set_title(T("(b) 时间戳对不齐，后面所有分析都是空的",
              "(b) misaligned timestamps void everything downstream"), fontsize=10)
c.annotate(T("注意：整体平移不改变“工时”，所以看报表发现不了；\n"
             "一旦要把信号与零件对起来，错配立刻冒出来",
             "a pure offset leaves durations intact, so reports look fine"),
           xy=(0.03, 0.72), xycoords="axes fraction", ha="left",
           fontsize=8.5, color=C["muted"])
c.grid(alpha=0.25, lw=0.5)
c.set_ylim(-4, 104)

fig.tight_layout()
figure(fig, "fig21_1_1")
