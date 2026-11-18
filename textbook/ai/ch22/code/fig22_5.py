"""22.3 节的图：贴着上限走，与外面那层兜底。

图 22.3.1：（a）两天的冷通道温度——在仿真里不越界的那套参数，到了真设备上天天骑在
上限上；（b）电耗与越界放在同一张图上——**只看横轴，排名是反的**。
"""
import numpy as np

from _ch22 import DT_H, HALL, STEPS_PER_DAY, learned_policy, run_hall
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N_DAYS, GAIN = 10, 0.90

rule = run_hall(learned_policy(23.0, 240.0, 0.0), N_DAYS, seed=0, gain=GAIN)
best = None
for sp in np.arange(23.0, 26.96, 0.05):
    for lead in (0.0, -30.0, -60.0, -90.0):
        r = run_hall(learned_policy(float(sp), 240.0, float(lead)), N_DAYS, seed=0)
        if r["viol"] == 0 and (best is None or r["kwh"] < best[0]["kwh"]):
            best = (r, float(sp), float(lead))
sim, SP, LEAD = best
real = run_hall(learned_policy(SP, 240.0, LEAD), N_DAYS, seed=0, gain=GAIN)
safed = run_hall(learned_policy(SP, 240.0, LEAD), N_DAYS, seed=0, gain=GAIN, safety=True)
t_max = HALL["t_max"]

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 两天的温度
D0, D1 = 4, 6
sl = slice(D0 * STEPS_PER_DAY, D1 * STEPS_PER_DAY)
t = np.arange(sl.stop - sl.start) * DT_H
a.axhline(t_max, color=C["x"], lw=1.6, ls="--")
a.annotate(T(f"温度上限 {t_max:.0f} ℃（绝对不许越过）",
             f"hard limit {t_max:.0f} ℃ (never cross)"),
           xy=(0.5, t_max), xytext=(0, 4), textcoords="offset points",
           fontsize=8.5, color=C["x"])
a.plot(t, rule["temps"][sl], color=C["muted"], lw=1.8,
       label=T("保守规则（盯住 23 ℃）", "conservative rule (hold 23 ℃)"))
a.plot(t, real["temps"][sl], color=C["x"], lw=2.0,
       label=T("仿真里搜出来的参数，放到真设备上", "sim-tuned policy on the real plant"))
a.plot(t, safed["temps"][sl], color=C["z"], lw=1.8, ls="--",
       label=T("同一套参数 + 安全层", "same policy + safety layer"))
over = real["temps"][sl] > t_max
a.fill_between(t, t_max, real["temps"][sl], where=over, color=C["x"], alpha=0.35)
a.set_xlabel(T("时间（小时，连续两天）", "time (hours, two consecutive days)"))
a.set_ylabel(T("冷通道温度（℃）", "cold-aisle temperature (℃)"))
a.set_ylim(21.5, t_max + 1.2)
a3 = a.twinx()
a3.plot(t, real["amb"][sl], color=C["y"], lw=1.4, alpha=0.75)
a3.set_ylabel(T("室外温度（℃，细线）", "ambient temperature (℃, thin line)"), color=C["y"])
a3.tick_params(axis="y", labelcolor=C["y"])
a3.set_ylim(real["amb"][sl].min() - 1.0, real["amb"][sl].max() + 7.0)
a.set_title(T("(a) 在仿真里不越界，到真设备上天天骑在上限上",
              "(a) safe in simulation, riding the limit in reality"), fontsize=10)
a.legend(fontsize=8, loc="lower left", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 电耗对越界
pts = [(T("保守规则", "conservative rule"), rule["kwh"], rule["viol"], C["muted"], "o"),
       (T("仿真里的成绩（骗人的）", "score in simulation (misleading)"),
        sim["kwh"], sim["viol"], C["y"], "^"),
       (T("真设备上，无安全层", "real plant, no safety layer"),
        real["kwh"], real["viol"], C["x"], "s"),
       (T("真设备上，加安全层", "real plant, with safety layer"),
        safed["kwh"], safed["viol"], C["z"], "D")]
for name, kwh, viol, col, mk in pts:
    b.scatter([kwh / 1000.0], [viol], s=130, color=col, marker=mk, zorder=3, label=name)
b.annotate(T(f"安全层：多花 {(safed['kwh'] / real['kwh'] - 1) * 100:.2f}% 的电，"
             f"\n把 {real['viol']} 次越界变成 0 次",
             f"safety layer: +{(safed['kwh'] / real['kwh'] - 1) * 100:.2f}% energy, "
             f"{real['viol']} violations → 0"),
           xy=(safed["kwh"] / 1000.0, 0), xytext=(-20, 120), textcoords="offset points",
           ha="center", fontsize=8.5, color=C["accent"],
           arrowprops=dict(arrowstyle="->", color=C["accent"], lw=1.2))
b.set_xlabel(T("10 天的冷却电耗（兆瓦时，越左越省）",
                "cooling energy over 10 days (MWh, left is cheaper)"))
b.set_ylabel(T("越界次数（15 分钟一个点）", "limit violations (15-min steps)"))
b.set_ylim(-60, max(p[2] for p in pts) * 1.35)
b.set_title(T("(b) 只看横轴，排名是反的", "(b) rank them by the x-axis alone and you get it backwards"),
            fontsize=10)
b.legend(fontsize=8, loc="upper right", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig22_3_1")
