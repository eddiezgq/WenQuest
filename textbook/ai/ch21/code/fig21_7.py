"""21.8 节的图：减速器车间的维护账。

图 21.8.1：（a）一队设备的退化曲线与三条报警线——**寿命差一倍多，所以定期更换一定吃亏**；
（b）阈值扫一遍：总代价、失效台数与"最短提前期"三条线放在一起，
验收条款就是在这张图上画出来的。
"""
import numpy as np

from _ch21 import degradation, first_cross, maintenance_cost
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N_UNITS, N_STEPS = 60, 160
COST_PLAN, COST_FAIL, COST_EARLY = 1.0, 12.0, 0.02
LEAD_NEED = 10

g = np.random.default_rng(0)
fleet = [degradation(N_STEPS, rate=float(g.uniform(0.004, 0.012)),
                     noise=float(g.uniform(0.01, 0.05)), seed=int(g.integers(1 << 30)))
         for _ in range(N_UNITS)]

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 退化曲线族
for x in fleet[:28]:
    a.plot(x, color=C["z"], lw=0.8, alpha=0.45)
a.axhline(1.0, color=C["x"], lw=2.0)
a.annotate(T("失效线", "failure level"), xy=(2, 1.0), xytext=(0, 5),
           textcoords="offset points", fontsize=9, color=C["x"])
for thr, col in ((0.5, C["muted"]), (0.7, C["accent"]), (0.9, C["y"])):
    a.axhline(thr, color=col, ls="--", lw=1.4)
    r = maintenance_cost(fleet, thr=thr, cost_plan=COST_PLAN, cost_fail=COST_FAIL,
                         cost_early=COST_EARLY)
    a.annotate(T(f"阈值 {thr:.1f}：平均提前 {r['lead_mean']:.0f}、最短 {r['lead_min']} 个周期",
                 f"threshold {thr:.1f}: mean lead {r['lead_mean']:.0f}, min {r['lead_min']}"),
               xy=(N_STEPS - 2, thr), xytext=(-4, 4), textcoords="offset points",
               ha="right", fontsize=8, color=col)
lives = [t for t in (first_cross(x, 1.0) for x in fleet) if t is not None]
a.annotate(T(f"寿命中位 {np.median(lives):.0f} 个周期，最短 {min(lives)}、最长 {max(lives)}"
             f"（差 {max(lives) / min(lives):.1f} 倍）",
             f"life: median {np.median(lives):.0f}, {min(lives)}–{max(lives)}"),
           xy=(0.03, 0.93), xycoords="axes fraction", ha="left",
           fontsize=8.5, color=C["ink"])
a.set_xlabel(T("运行周期", "operating cycles"))
a.set_ylabel(T("退化指标（1.0 为失效）", "degradation index (1.0 = failure)"))
a.set_ylim(0, 1.25)
a.set_title(T("(a) 同型号设备的寿命差一倍多", "(a) identical units, lives differing by 2×"),
            fontsize=10)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 阈值扫一遍
thrs = np.arange(0.30, 0.96, 0.02)
total, failed, lead_min = [], [], []
for thr in thrs:
    r = maintenance_cost(fleet, thr=float(thr), cost_plan=COST_PLAN,
                         cost_fail=COST_FAIL, cost_early=COST_EARLY)
    total.append(r["total"])
    failed.append(r["failed"])
    lead_min.append(r["lead_min"])
total, failed, lead_min = np.array(total), np.array(failed), np.array(lead_min)

b.plot(thrs, total, color=C["x"], lw=2.4, label=T("总代价", "total cost"))
b.set_xlabel(T("报警阈值", "alarm threshold"))
b.set_ylabel(T("总代价", "total cost"), color=C["x"])
b2 = b.twinx()
b2.plot(thrs, lead_min, color=C["z"], lw=2.0, ls="--",
        label=T("最短提前期（周期）", "minimum lead time (cycles)"))
b2.plot(thrs, failed, color=C["y"], lw=1.8, ls=":",
        label=T("失效台数", "units that failed"))
b2.axhline(LEAD_NEED, color=C["muted"], lw=1.2)
b2.annotate(T(f"条款要求：最短提前 {LEAD_NEED} 个周期",
              f"clause: at least {LEAD_NEED} cycles of lead"),
            xy=(thrs[0], LEAD_NEED), xytext=(4, 4), textcoords="offset points",
            fontsize=8, color=C["muted"])
b2.set_ylabel(T("周期 / 台数", "cycles / units"), color=C["z"])

i_best = int(np.argmin(total))
b.plot([thrs[i_best]], [total[i_best]], "o", color=C["x"], ms=9, zorder=4)
b.annotate(T(f"代价最低 {thrs[i_best]:.2f}\n但最短提前只有 {lead_min[i_best]} 个周期",
             f"cheapest at {thrs[i_best]:.2f}, min lead {lead_min[i_best]}"),
           xy=(thrs[i_best], total[i_best]), xytext=(-8, 26),
           textcoords="offset points", ha="right", fontsize=8.5, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.0))

ok = [i for i in range(len(thrs)) if lead_min[i] >= LEAD_NEED and failed[i] == 0]
if ok:
    i_ok = max(ok, key=lambda i: thrs[i])
    b.plot([thrs[i_ok]], [total[i_ok]], "P", color=C["accent"], ms=12, zorder=5)
    b.annotate(T(f"满足条款里最省的 {thrs[i_ok]:.2f}：代价 {total[i_ok]:.0f}"
                 f"（贵 {(total[i_ok] / total[i_best] - 1) * 100:.0f}%）",
                 f"cheapest compliant {thrs[i_ok]:.2f}"),
               xy=(thrs[i_ok], total[i_ok]), xytext=(8, 18),
               textcoords="offset points", fontsize=8.5, color=C["accent"],
               arrowprops=dict(arrowstyle="->", color=C["accent"], lw=1.0))
b.set_title(T("(b) 验收条款就画在这张图上", "(b) the acceptance clause is drawn on this chart"),
            fontsize=10)
h1, l1 = b.get_legend_handles_labels()
h2, l2 = b2.get_legend_handles_labels()
b.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper center", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig21_8_1")
