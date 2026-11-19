"""23.6 节的图之二：时延预算与控制退化。

图 23.6.1：（a）时延一加上去，急刹次数与冲击度怎么长，通行流量怎么被悄悄吃掉；
（b）“感知做准但变慢”与“稍差但更快”的取舍曲线——**最优点在中间，两头都更差**。

图里的毫秒数**全部是显式假设**，本章资料卡里查不到任何官方的端到端时延预算。
"""
import math

import numpy as np

from _ch23 import DT, SCENE, cost_planner, follow_sim, latency_to_steps
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N, SEED = 4800, 5
SC = dict(SCENE)
SC["t_headway"] = 1.1


def plan():
    return cost_planner(2.0, scene=SC, horizon_s=1.0)


def flow(r):
    return 3600.0 * r["v_mean"] / (r["gap_mean"] + SC["veh_len"])


# ---------------- (a) 时延 → 退化
LAT = np.array([0.0, 50.0, 100.0, 150.0, 200.0, 300.0, 400.0, 600.0, 800.0])
hard, jerk, fl = [], [], []
for ms in LAT:
    r = follow_sim(plan(), n=N, seed=SEED, scene=SC,
                   delay_steps=latency_to_steps(ms) if ms > 0 else 0)
    hard.append(r["hard"])
    jerk.append(r["jerk_rms"])
    fl.append(flow(r))
hard, jerk, fl = np.array(hard), np.array(jerk), np.array(fl)

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

a.plot(LAT, hard, "o-", color=C["x"], lw=2.2, ms=6, label=T("急刹次数", "hard brakes"))
a.set_xlabel(T("感知到执行的总时延（ms，显式假设）",
               "sensor-to-actuation latency (ms, an explicit assumption)"))
a.set_ylabel(T("急刹次数（240 s 内）", "hard brakes (over 240 s)"), color=C["x"])
a.tick_params(axis="y", labelcolor=C["x"])
a2 = a.twinx()
a2.plot(LAT, jerk, "s--", color=C["z"], lw=2.0, ms=5.5, label=T("冲击度", "jerk"))
a2.plot(LAT, (fl - fl.min()) / (fl.max() - fl.min()) * (jerk.max() - jerk.min()) + jerk.min(),
        "^:", color=C["y"], lw=1.8, ms=5.5,
        label=T(f"通行流量（{fl.max():.0f} → {fl.min():.0f} 辆/h）",
                f"traffic flow ({fl.max():.0f} → {fl.min():.0f} veh/h)"))
a2.set_ylabel(T("冲击度（m/s³）／流量（缩放后）", "jerk (m/s³) / flow (rescaled)"), color=C["z"])
a2.tick_params(axis="y", labelcolor=C["z"])
one = DT * 1000
a.axvline(one, color=C["muted"], lw=1.2, ls=":")
a.annotate(T(f"一个控制周期 {one:.0f} ms", f"one control period, {one:.0f} ms"),
           xy=(one, hard.max() * 0.42), xytext=(7, 0), textcoords="offset points",
           fontsize=8.5, color=C["muted"], va="center")
a.annotate(T(f"急刹 {hard[0]} → {hard[-1]} 次（{hard[-1] / hard[0]:.0f} 倍）",
             f"hard brakes {hard[0]} → {hard[-1]} ({hard[-1] / hard[0]:.0f}$\\times$)"),
           xy=(LAT[-1], hard[-1]), xytext=(-8, -26), textcoords="offset points",
           ha="right", fontsize=8.5, color=C["x"])
a.set_title(T("(a) 时延的账：先付在急刹与舒适上，再付在通行效率上",
              "(a) latency is paid in braking and comfort first, throughput second"),
            fontsize=10)
h1, l1 = a.get_legend_handles_labels()
h2, l2 = a2.get_legend_handles_labels()
a.legend(h1 + h2, l1 + l2, fontsize=8, loc="upper left", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 更准但更慢 vs 稍差但更快
SIG_REF, T_REF, OTHER = 3.40, 20.0, 60.0
T_PERC = np.array([20.0, 30.0, 45.0, 60.0, 90.0, 130.0, 180.0, 250.0, 350.0, 500.0])
h2_, j2_, sig = [], [], []
for t in T_PERC:
    s = SIG_REF * math.sqrt(T_REF / t)
    r = follow_sim(plan(), n=N, seed=SEED, scene=SC, meas_sigma=s,
                   delay_steps=latency_to_steps(t + OTHER))
    h2_.append(r["hard"])
    j2_.append(r["jerk_rms"])
    sig.append(s)
h2_, j2_, sig = np.array(h2_), np.array(j2_), np.array(sig)

b.plot(T_PERC, h2_, "o-", color=C["x"], lw=2.4, ms=7)
i_best = int(np.argmin(h2_))
b.plot(T_PERC[i_best], h2_[i_best], "*", color=C["ink"], ms=18)
b.set_xscale("log")
b.set_xlabel(T("分给感知的时间（ms，显式假设；其余环节固定占 60 ms）",
               "time given to perception (ms; the rest of the stack costs 60 ms)"))
b.set_ylabel(T("急刹次数（240 s 内）", "hard brakes (over 240 s)"))
b.set_title(T("(b) 最优点在中间：两头都更差",
              "(b) the optimum is in the middle; both ends are worse"), fontsize=10)
for i in (0, i_best, len(T_PERC) - 1):
    b.annotate(T(f"σ = {sig[i]:.2f} m\n{h2_[i]} 次", f"σ = {sig[i]:.2f} m\n{h2_[i]} brakes"),
               xy=(T_PERC[i], h2_[i]),
               xytext=(0, 20) if i == i_best else ((12, -6) if i == 0 else (-14, 16)),
               textcoords="offset points",
               ha="center" if i == i_best else ("left" if i == 0 else "right"),
               va="center" if i == i_best else ("top" if i == 0 else "bottom"),
               fontsize=8.5, color=C["ink"])
b.axvspan(T_PERC[0] * 0.88, T_PERC[i_best] * 0.78, color=C["z"], alpha=0.09)
b.axvspan(T_PERC[i_best] * 1.28, T_PERC[-1] * 1.14, color=C["accent"], alpha=0.10)
b.annotate(T("太快：观测噪声大，\n方向盘一直在修",
             "too fast: noisy observations,\nconstant corrections"),
           xy=(T_PERC[1], h2_.max() * 0.33), ha="center", va="top",
           fontsize=8.5, color=C["z"])
b.annotate(T("太慢：反应跟不上，\n虽然看得更准",
             "too slow: cannot react in time,\neven though it sees better"),
           xy=(T_PERC[-2], h2_.max() * 0.33), ha="center", va="top",
           fontsize=8.5, color=C["accent"])
b.annotate(T(f"从 {T_PERC[i_best]:.0f} ms 加到 {T_PERC[-1]:.0f} ms："
             f"精度提高 {sig[i_best] / sig[-1]:.1f} 倍，急刹反而多 "
             f"{(h2_[-1] / h2_[i_best] - 1) * 100:.0f}%",
             f"from {T_PERC[i_best]:.0f} ms to {T_PERC[-1]:.0f} ms: "
             f"{sig[i_best] / sig[-1]:.1f}$\\times$ more accurate, "
             f"{(h2_[-1] / h2_[i_best] - 1) * 100:.0f}% more hard brakes"),
           xy=(0.5, 0.025), xycoords="axes fraction", ha="center", va="bottom",
           fontsize=8.5, color=C["x"])
b.set_ylim(0, h2_.max() * 1.18)
b.grid(alpha=0.25, lw=0.5, which="both")

fig.tight_layout()
figure(fig, "fig23_6_1")
