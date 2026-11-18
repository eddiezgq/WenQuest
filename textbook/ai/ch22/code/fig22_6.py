"""22.5 节的图：收益与越界要并排看。

图 22.5.1：（a）四百套随机策略在真设备上的电费与越界次数——**最省的那几套，
全都压在越界最多的地方**；（b）三行报表并排：仿真里的成绩、真设备上的成绩、
以及加了安全层之后的成绩。
"""
import numpy as np

from _ch22 import (BATTERY, dispatch_cost, load_series, pv_series, safe_layer, tou_price)
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N_DAYS, MARGIN, PENALTY = 12, 0.05, 20.0

pv = pv_series(N_DAYS, seed=3)
load = load_series(N_DAYS, seed=3)
price = tou_price(N_DAYS)
REAL = dict(BATTERY)
REAL["eta"] = BATTERY["eta"] - 0.06
REAL["cap_kwh"] = BATTERY["cap_kwh"] * 0.92


def policy(params, bat):
    p_lo, p_hi, charge_frac, keep = params
    o = np.zeros(len(pv))
    for i in range(len(pv)):
        s = pv[i] - load[i]
        if s > 0:
            o[i] = min(s, bat["p_max_kw"]) * charge_frac
        elif price[i] <= p_lo:
            o[i] = bat["p_max_kw"] * charge_frac
        elif price[i] >= p_hi:
            o[i] = -bat["p_max_kw"] * (1.0 - keep)
    return o


def evaluate(params, bat, use_safe):
    plan = policy(params, bat)
    if use_safe:
        plan = safe_layer(plan, pv, load, bat, margin=MARGIN)
    cost, _, viol = dispatch_cost(pv, load, price, plan, bat)
    return cost, viol


BASE = (0.35, 0.95, 0.8, 0.2)
g = np.random.default_rng(0)
cands = [(float(g.uniform(0.25, 0.7)), float(g.uniform(0.7, 1.1)),
          float(g.uniform(0.2, 1.0)), float(g.uniform(0.0, 0.8))) for _ in range(400)]
sim = np.array([evaluate(c, BATTERY, False) for c in cands])
real = np.array([evaluate(c, REAL, False) for c in cands])
i_cheap = int(np.argmin(sim[:, 0]))                       # 只盯电费挑出来的那一套
i_pen = int(np.argmin(sim[:, 0] + PENALTY * sim[:, 1]))   # 把越界计入目标挑出来的那一套

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 电费对越界
a.scatter(real[:, 0] / 1000.0, real[:, 1], s=16, color=C["muted"], alpha=0.55,
          label=T("四百套随机策略（真设备）", "400 random policies (real plant)"))
a.scatter([real[i_cheap, 0] / 1000.0], [real[i_cheap, 1]], s=150, marker="s",
          color=C["x"], zorder=3,
          label=T("只盯电费挑出来的那一套", "picked by cost alone"))
a.scatter([real[i_pen, 0] / 1000.0], [real[i_pen, 1]], s=150, marker="D",
          color=C["z"], zorder=3,
          label=T(f"把越界按每次 {PENALTY:.0f} 元计入目标", f"cost + {PENALTY:.0f} CNY per violation"))
c_safe, v_safe = evaluate(cands[i_pen], REAL, True)
a.scatter([c_safe / 1000.0], [v_safe], s=170, marker="*", color=C["y"], zorder=4,
          label=T("再加安全层", "plus the safety layer"))
a.annotate("", xy=(c_safe / 1000.0, v_safe),
           xytext=(real[i_pen, 0] / 1000.0, real[i_pen, 1]),
           arrowprops=dict(arrowstyle="->", color=C["y"], lw=1.4))
a.set_xlabel(T("12 天电费（千元，越左越省）", "12-day bill (thousand CNY, left is cheaper)"))
a.set_ylabel(T("越界次数", "limit violations"))
a.set_title(T("(a) 省下的那一点点，是拿越界换来的",
              "(a) the last sliver of savings is bought with violations"), fontsize=10)
a.annotate(T(f"只盯电费那一套，比计入越界的那一套只省 "
             f"{(real[i_pen, 0] - real[i_cheap, 0]):,.0f} 元，\n"
             f"却多越界 {real[i_cheap, 1] - real[i_pen, 1]:.0f} 次",
             f"picking by cost alone saves {(real[i_pen, 0] - real[i_cheap, 0]):,.0f} CNY "
             f"and adds {real[i_cheap, 1] - real[i_pen, 1]:.0f} violations"),
           xy=(0.03, 0.62), xycoords="axes fraction", ha="left", va="top",
           fontsize=8.5, color=C["accent"])
a.legend(fontsize=7.8, loc="upper right", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 三行报表
rows = [
    (T("手写规则\n（没调过）", "hand rule\n(untuned)"), *evaluate(BASE, REAL, False)),
    (T("仿真里的成绩\n（骗人的）", "score in simulation\n(misleading)"),
     sim[i_cheap, 0], sim[i_cheap, 1]),
    (T("同一套参数\n在真设备上", "same policy\non the real plant"),
     real[i_cheap, 0], real[i_cheap, 1]),
    (T("计入越界代价\n+ 安全层", "violation cost\n+ safety layer"), c_safe, v_safe),
]
xs = np.arange(len(rows))
costs = np.array([r[1] for r in rows]) / 1000.0
viols = np.array([r[2] for r in rows])
b.bar(xs - 0.2, costs, 0.38, color=C["muted"], label=T("电费（千元）", "bill (thousand CNY)"))
b.set_ylabel(T("12 天电费（千元）", "12-day bill (thousand CNY)"))
b.set_ylim(0, costs.max() * 1.5)
for i, cc in enumerate(costs):
    b.annotate(f"{cc:.1f}", xy=(i - 0.2, cc), xytext=(0, 3), textcoords="offset points",
               ha="center", fontsize=8.5, color=C["ink"])
b2 = b.twinx()
b2.bar(xs + 0.2, viols, 0.38, color=C["x"], label=T("越界次数", "violations"))
b2.set_ylabel(T("越界次数", "violations"), color=C["x"])
b2.tick_params(axis="y", labelcolor=C["x"])
b2.set_ylim(0, max(viols.max(), 1) * 1.5)
for i, vv in enumerate(viols):
    b2.annotate(f"{vv:.0f}", xy=(i + 0.2, vv), xytext=(0, 3), textcoords="offset points",
                ha="center", fontsize=8.5, color=C["x"])
b.set_xticks(xs)
b.set_xticklabels([r[0] for r in rows], fontsize=8.2)
b.set_title(T("(b) 两列并排，这件事才看得清",
              "(b) only both columns together tell the story"), fontsize=10)
h1, l1 = b.get_legend_handles_labels()
h2, l2 = b2.get_legend_handles_labels()
b.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper left", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5, axis="y")

fig.tight_layout()
figure(fig, "fig22_5_1")
