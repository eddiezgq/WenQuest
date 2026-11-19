"""23.4 节的图：规划权重的取舍曲线，以及“调快一点就不安全了”那一片。

图 23.3.2：（a）跟车距离权重一扫到底，通行效率与平均车距此消彼长，
**流量最高的那一档落在不安全区里**；（b）同一条横轴上的急刹次数与侵犯次数——
两头都坏，中间那一小段才是可用的。
"""
import numpy as np

from _ch23 import SCENE, cost_planner, follow_sim
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N, SEED, DELAY = 2400, 5, 2

WS = np.array([0.02, 0.035, 0.05, 0.07, 0.10, 0.14, 0.20, 0.28, 0.40,
               0.57, 0.80, 1.13, 1.60, 2.26, 3.20])
gap, flow, hard, viol = [], [], [], []
for w in WS:
    r = follow_sim(cost_planner(float(w)), n=N, seed=SEED, delay_steps=DELAY)
    gap.append(r["gap_mean"])
    flow.append(3600.0 * r["v_mean"] / (r["gap_mean"] + SCENE["veh_len"]))
    hard.append(r["hard"])
    viol.append(r["viol"])
gap, flow = np.array(gap), np.array(flow)
hard, viol = np.array(hard), np.array(viol)

unsafe = WS[viol > 0]
clean = WS[(viol == 0) & (hard == 0)]
w_bad_hi = float(unsafe.max()) if len(unsafe) else None

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

for ax in (a, b):
    ax.set_xscale("log")
    if w_bad_hi is not None:
        ax.axvspan(WS.min() * 0.85, w_bad_hi * 1.19, color=C["x"], alpha=0.09)
    if len(clean):
        ax.axvspan(clean.min() * 0.84, clean.max() * 1.19, color=C["y"], alpha=0.13)

# ---------------- (a) 效率与车距
a.plot(WS, flow, "o-", color=C["x"], lw=2.2, ms=6)
a.set_xlabel(T("跟车距离的权重 $w_{\\mathrm{gap}}$（对数）",
               "car-following distance weight $w_{\\mathrm{gap}}$ (log)"))
a.set_ylabel(T("通行流量（辆/小时）", "traffic flow (veh/h)"), color=C["x"])
a.tick_params(axis="y", labelcolor=C["x"])
a2 = a.twinx()
a2.plot(WS, gap, "s--", color=C["z"], lw=2.0, ms=5.5)
a2.set_ylabel(T("平均车距（m）", "mean gap (m)"), color=C["z"])
a2.tick_params(axis="y", labelcolor=C["z"])
i_best = int(np.argmax(flow))
a.plot(WS[i_best], flow[i_best], "*", color=C["x"], ms=17)
a.annotate(T(f"流量最高 {flow[i_best]:.0f} 辆/h，\n但它在不安全区里",
             f"highest flow {flow[i_best]:.0f} veh/h,\nbut it sits in the unsafe band"),
           xy=(WS[i_best], flow[i_best]), xytext=(16, -30), textcoords="offset points",
           fontsize=8.5, color=C["x"],
           arrowprops=dict(arrowstyle="->", color=C["x"], lw=1.1))
safe_mask = viol == 0
i_safe = int(np.argmax(np.where(safe_mask, flow, -1)))
a.annotate(T(f"安全区内最高 {flow[i_safe]:.0f} 辆/h\n（差 "
             f"{(flow[i_best] / flow[i_safe] - 1) * 100:.0f}%）",
             f"best safe flow {flow[i_safe]:.0f} veh/h\n"
             f"({(flow[i_best] / flow[i_safe] - 1) * 100:.0f}% lower)"),
           xy=(WS[i_safe], flow[i_safe]), xytext=(14, 24), textcoords="offset points",
           fontsize=8.5, color=C["ink"],
           arrowprops=dict(arrowstyle="->", color=C["ink"], lw=1.1))
a.set_ylim(flow.min() * 0.985, flow.max() * 1.035)
a.set_title(T("(a) 跟得越紧，通行越多——代价在另一张图上",
              "(a) the tighter you follow, the more cars pass; the price is on the right"),
            fontsize=10)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 两头都坏
b.plot(WS, viol, "o-", color=C["x"], lw=2.2, ms=6,
       label=T("侵犯最小安全间距（次）", "min-gap violations"))
b.plot(WS, hard, "s-", color=C["z"], lw=2.2, ms=6,
       label=T("急刹（次）", "hard brakes"))
b.set_xlabel(T("跟车距离的权重 $w_{\\mathrm{gap}}$（对数）",
               "car-following distance weight $w_{\\mathrm{gap}}$ (log)"))
b.set_ylabel(T("次数（120 s 内）", "count (over 120 s)"))
b.set_title(T("(b) 往小调就侵犯间距，往大调急刹回升",
              "(b) too small violates the gap, too large brings hard braking back"),
            fontsize=10)
b.legend(fontsize=8.5, loc="upper center", framealpha=0.92)
if len(clean):
    b.annotate(T(f"可用区间 {clean.min():.2f}—{clean.max():.2f}\n"
                 f"（只有 {clean.max() / clean.min():.1f} 倍宽）",
                 f"usable band {clean.min():.2f}–{clean.max():.2f}\n"
                 f"(only {clean.max() / clean.min():.1f}$\\times$ wide)"),
               xy=(float(np.sqrt(clean.min() * clean.max())), max(viol.max(), hard.max()) * 0.52),
               ha="center", va="center", fontsize=8.5, color=C["y"])
b.annotate(T("两头都坏，中间那一小段才是可用的",
             "both ends are bad; only the middle is usable"),
           xy=(0.02, 0.62), xycoords="axes fraction", ha="left", va="center",
           fontsize=8.5, color=C["accent"])
b.set_ylim(-4, max(viol.max(), hard.max()) * 1.22)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig23_3_2")
