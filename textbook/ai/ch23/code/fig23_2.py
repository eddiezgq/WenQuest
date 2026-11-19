"""23.3 节的图之一：融合、单传感器，以及一个偶尔骗人的传感器。

图 23.2.2：（a）卡死那一段的放大图——真值、只用好传感器、朴素融合、加门限的融合四条线；
（b）门限松紧扫一遍：朴素融合与只用单传感器是两条横线，门限曲线穿过它们，
**而且两头都更差**。
"""
import numpy as np

from _ch23 import DT, camera_range, kalman_fuse, lead_track, radar_range
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
N = 1200
SIG_A, REL_B = 0.45, 0.022
OUT_P, OUT_M, STUCK = 0.03, 14.0, (520, 580)

s_l, v_l = lead_track(N, DT, seed=4)
x_true = s_l - np.cumsum(np.full(N, 21.0)) * DT
SIG_B = REL_B * float(x_true.mean())

g = np.random.default_rng(11)
z_a = radar_range(x_true, g, SIG_A)
z_b = camera_range(x_true, g, REL_B, outlier_p=OUT_P, outlier_m=OUT_M, stuck=STUCK)

est_a, _ = kalman_fuse([(z_a, SIG_A)])
est_naive, _ = kalman_fuse([(z_a, SIG_A), (z_b, SIG_B)])
est_gate, _ = kalman_fuse([(z_a, SIG_A), (z_b, SIG_B)], gate=5.0)


def rmse(a, b):
    return float(np.sqrt(np.mean((a - b) ** 2)))


fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 卡死那一段
lo, hi = 440, 700
t = np.arange(lo, hi) * DT
bad = np.abs(z_b[lo:hi] - x_true[lo:hi]) > 5.0
a.plot(t[bad], z_b[lo:hi][bad], "x", color=C["muted"], ms=5, mew=1.2,
       label=T("传感器 B 骗人的那些帧", "frames where sensor B lies"))
a.plot(t, x_true[lo:hi], color=C["ink"], lw=2.4, label=T("真实距离", "true range"))
a.plot(t, est_a[lo:hi], color=C["y"], lw=1.7, ls="--",
       label=T("只用传感器 A", "sensor A alone"))
a.plot(t, est_naive[lo:hi], color=C["x"], lw=1.9,
       label=T("朴素融合（来什么都吃）", "naive fusion (accepts everything)"))
a.plot(t, est_gate[lo:hi], color=C["z"], lw=1.9, ls="-.",
       label=T("融合 + 5σ 新息门限", "fusion + 5$\\sigma$ innovation gate"))
a.axvspan(STUCK[0] * DT, STUCK[1] * DT, color=C["accent"], alpha=0.12)
a.annotate(T(f"B 卡死 {(STUCK[1] - STUCK[0]) * DT:.0f} s",
             f"B frozen for {(STUCK[1] - STUCK[0]) * DT:.0f} s"),
           xy=((STUCK[0] + STUCK[1]) / 2 * DT, x_true[lo:hi].max()),
           xytext=(0, 6), textcoords="offset points", ha="center",
           fontsize=8.5, color=C["accent"])
a.set_xlabel(T("时间（s）", "time (s)"))
a.set_ylabel(T("到前车的距离（m）", "range to the lead vehicle (m)"))
a.set_title(T("(a) 多一路传感器，估计被拖着走", "(a) one extra sensor drags the estimate away"),
            fontsize=10)
a.legend(fontsize=7.6, loc="lower left", framealpha=0.92, ncol=2)
a.set_ylim(x_true[lo:hi].min() - 4.5, x_true[lo:hi].max() + 3.0)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 门限松紧扫一遍
gates = np.array([12.0, 10.0, 8.0, 6.0, 5.0, 4.0, 3.5, 3.0, 2.5, 2.0])
rm = np.array([rmse(kalman_fuse([(z_a, SIG_A), (z_b, SIG_B)], gate=float(q))[0], x_true)
               for q in gates])
rm_naive = rmse(est_naive, x_true)
rm_a = rmse(est_a, x_true)
b.plot(gates, rm, "o-", color=C["z"], lw=2.2, ms=6,
       label=T("融合 + 门限", "fusion + gate"))
b.axhline(rm_naive, color=C["x"], lw=1.8, ls="--",
          label=T(f"朴素融合 {rm_naive:.3f} m", f"naive fusion {rm_naive:.3f} m"))
b.axhline(rm_a, color=C["y"], lw=1.8, ls=":",
          label=T(f"只用传感器 A {rm_a:.3f} m", f"sensor A alone {rm_a:.3f} m"))
i_best = int(np.argmin(rm))
b.plot(gates[i_best], rm[i_best], "*", color=C["z"], ms=16)
b.annotate(T(f"最好 {rm[i_best]:.3f} m", f"best {rm[i_best]:.3f} m"),
           xy=(gates[i_best], rm[i_best]), xytext=(0, -20), textcoords="offset points",
           ha="center", fontsize=8.5, color=C["z"])
worse = gates[rm > rm_naive]
if len(worse):
    b.axvspan(gates.min() - 0.2, float(worse.max()) + 0.25, color=C["x"], alpha=0.08)
    b.annotate(T("门限收到这一带，\n比不设门限还差",
                 "tighten into this band\nand it is worse than no gate"),
               xy=(float(worse.max()) + 0.35, rm.max() * 0.92), ha="left", va="top",
               fontsize=8.5, color=C["x"])
b.set_ylim(0.24, rm.max() * 1.10)
b.set_xlabel(T("新息门限（倍标准差，向右越松）", "innovation gate (×$\\sigma$, looser to the right)"))
b.set_ylabel(T("距离估计的均方根误差（m）", "RMSE of the range estimate (m)"))
b.set_title(T("(b) 门限不是越紧越好", "(b) a tighter gate is not a better gate"), fontsize=10)
b.legend(fontsize=8, loc="upper right", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig23_2_2")
