"""本章第四幅图（`fig25_4_1`）：排队论估算什么时候开始不准。

图 `fig25_4_1`：（a）平均停留时间：Erlang C 的估算，与两种服务时间方差下的仿真；
（b）估算的相对误差随负载——**假设成立时一直准，假设不成立时被负载放大**；
到达不平稳（按班次忙闲）的那一点单独标出来。
"""
import numpy as np

from _ch25 import erlang_c_wait, simulate_queue, simulate_queue_shift
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
K, MU, N_JOBS, SEEDS = 3, 2.0, 120000, (0, 1, 2)
LOADS = np.array([0.4, 0.55, 0.7, 0.8, 0.875, 0.925, 0.95])

est, sim1, sim3 = [], [], []
for rho in LOADS:
    lam = rho * K * MU
    est.append(erlang_c_wait(lam, MU, K) + 1.0 / MU)
    sim1.append(np.mean([simulate_queue(lam, MU, K, n_jobs=N_JOBS, cv2=1.0, seed=s)["w"]
                         for s in SEEDS]))
    sim3.append(np.mean([simulate_queue(lam, MU, K, n_jobs=N_JOBS, cv2=3.0, seed=s)["w"]
                         for s in SEEDS]))
est, sim1, sim3 = np.array(est), np.array(sim1), np.array(sim3)
err1 = (est / sim1 - 1) * 100
err3 = (est / sim3 - 1) * 100

RHO_SHIFT = 0.8
shift = simulate_queue_shift(1.2 * K * MU, 0.4 * K * MU, 40.0, MU, K,
                             n_jobs=N_JOBS, cv2=1.0, seed=0)
w_shift_est = erlang_c_wait(RHO_SHIFT * K * MU, MU, K) + 1.0 / MU
err_shift = (w_shift_est / shift["w"] - 1) * 100

fig, (a, b) = plt.subplots(1, 2, figsize=(11.4, 4.3))

# ---------------- (a) 停留时间
a.plot(LOADS, est, "--", color=C["ink"], lw=2.2,
       label=T("Erlang C 估算 + 利特尔法则", "Erlang C estimate + Little's law"))
a.plot(LOADS, sim1, "o-", color=C["z"], lw=2.0, ms=5,
       label=T("仿真：服务时间符合假设", "simulation: service time as assumed"))
a.plot(LOADS, sim3, "s-", color=C["x"], lw=2.0, ms=5,
       label=T("仿真：方差是假设的 3 倍", "simulation: variance 3× the assumption"))
a.plot(RHO_SHIFT, shift["w"], "*", color=C["accent"], ms=16, zorder=5)
a.annotate(T("到达不平稳（忙闲两班）", "non-stationary arrivals (two shifts)"),
           xy=(RHO_SHIFT, shift["w"]), xytext=(-12, 16), textcoords="offset points",
           ha="right", fontsize=8.5, color=C["accent"],
           arrowprops=dict(arrowstyle="->", color=C["accent"], lw=1.1))
a.set_xlabel(T("利用率 ρ", "utilisation ρ"))
a.set_ylabel(T("平均停留时间 W（小时）", "mean time in system W (hours)"))
a.set_title(T("(a) 同一个公式，离真相有多远要看假设",
              "(a) one formula, accuracy depends on the assumptions"), fontsize=10)
a.legend(fontsize=8, loc="upper left", framealpha=0.92)
a.grid(alpha=0.25, lw=0.5)

# ---------------- (b) 相对误差
b.axhline(0, color=C["muted"], lw=1.0, ls=":")
b.axhspan(-15, 15, color=C["y"], alpha=0.10)
b.annotate(T("±15%：估个数量级还能用", "±15%: good enough for an order of magnitude"),
           xy=(LOADS[0], 13), fontsize=8, color=C["y"], va="top")
b.plot(LOADS, err1, "o-", color=C["z"], lw=2.0, ms=5,
       label=T("服务时间符合假设", "service time as assumed"))
b.plot(LOADS, err3, "s-", color=C["x"], lw=2.0, ms=5,
       label=T("方差是假设的 3 倍", "variance 3× the assumption"))
b.plot(RHO_SHIFT, err_shift, "*", color=C["accent"], ms=16, zorder=5)
b.annotate(T(f"不平稳：{err_shift:+.0f}%", f"non-stationary: {err_shift:+.0f}%"),
           xy=(RHO_SHIFT, err_shift), xytext=(-10, -16), textcoords="offset points",
           ha="right", fontsize=8.5, color=C["accent"],
           arrowprops=dict(arrowstyle="->", color=C["accent"], lw=1.1))
i_bad = int(np.argmax(np.abs(err3) > 15))
b.axvline(LOADS[i_bad], color=C["x"], lw=1.0, ls="--", alpha=0.6)
b.annotate(T(f"方差不对时，ρ≈{LOADS[i_bad]:.2f} 起就出界",
             f"with wrong variance the estimate leaves the band at ρ≈{LOADS[i_bad]:.2f}"),
           xy=(LOADS[i_bad], -52), xytext=(6, 0), textcoords="offset points",
           fontsize=8.5, color=C["x"])
b.set_xlabel(T("利用率 ρ", "utilisation ρ"))
b.set_ylabel(T("估算相对仿真的误差（%）", "estimate error vs simulation (%)"))
b.set_ylim(-72, 26)
b.set_title(T("(b) 不准的根子是假设，负载只是放大器",
              "(b) the assumptions are the cause; load is the amplifier"), fontsize=10)
b.legend(fontsize=8, loc="lower left", framealpha=0.92)
b.grid(alpha=0.25, lw=0.5)

fig.tight_layout()
figure(fig, "fig25_4_1")
