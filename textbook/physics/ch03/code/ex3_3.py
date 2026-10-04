"""3.3 节的计算：

算例 3.3.1  AGV 起步：速度控制器让速度按 v(t) = 1.0 × (1 − e^(−t/τ)) m/s 趋近 1.0 m/s，τ = 1.2 s。控制器每 Δt 记录一次
            速度。用左矩形和、右矩形和、中点和估计前 5 s 走过的路程，与精确值（速度–时间图下的面积）比较，看误差怎样随
            Δt 减小（图 3.3.1、表 3.3.1）。
算例 3.3.2  电池管理系统用“安时积分”估计电量：放电电流 I(t) = 20 + 15 sin(0.5 t)（A，t 的单位为 s），每 1 s 采样一次，
            求 60 s 内放出的电荷量。精确值由原函数求出（微积分基本定理），与梯形法比较。
            再核对基本定理：累积函数 Q(t) = ∫₀ᵗ I dt 的数值导数等于 I(t)（图 3.3.2）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d


TAU, TEND = 1.2, 5.0


def vprof(t):
    return 1.0 * (1 - np.exp(-np.asarray(t, float) / TAU))


s_exact = TEND - TAU * (1 - math.exp(-TEND / TAU))          # 原函数 t + τ e^(−t/τ)
from scipy.integrate import quad
assert abs(quad(lambda t: float(vprof(t)), 0, TEND)[0] - s_exact) < 1e-10


def sums(dt):
    tl = np.arange(0, TEND - 1e-12, dt)
    return (float(np.sum(vprof(tl)) * dt), float(np.sum(vprof(tl + dt)) * dt), float(np.sum(vprof(tl + dt / 2)) * dt))


rows = {dt: sums(dt) for dt in (1.0, 0.5, 0.25, 0.1)}
out(s_exact=s_exact,
    **{f"L{k}": rows[dt][0] for k, dt in zip("abcd", rows)}, **{f"R{k}": rows[dt][1] for k, dt in zip("abcd", rows)},
    **{f"M{k}": rows[dt][2] for k, dt in zip("abcd", rows)})

# ---- 算例 3.3.2：安时积分
I = lambda t: 20 + 15 * np.sin(0.5 * t)
Iprim = lambda t: 20 * t - 30 * np.cos(0.5 * t)                 # 原函数
Tend = 60.0
Q_exact = float(Iprim(Tend) - Iprim(0.0))
ts = np.arange(0, Tend + 1e-9, 1.0)
Q_trap = float(np.trapezoid(I(ts), ts))
Q_left = float(np.sum(I(ts[:-1])) * 1.0)
ts10 = np.arange(0, Tend + 1e-9, 10.0)
Q_trap10 = float(np.trapezoid(I(ts10), ts10))
# 基本定理的核对：累积函数的数值导数
tt = np.linspace(0, Tend, 6001)
Qc = np.concatenate([[0], np.cumsum((I(tt[1:]) + I(tt[:-1])) / 2 * np.diff(tt))])
dQ = np.gradient(Qc, tt)
assert np.max(np.abs(dQ[5:-5] - I(tt[5:-5]))) < 1e-3
out(Q_exact=Q_exact, Q_Ah=Q_exact / 3600, Q_trap=Q_trap, Q_left=Q_left, Q_trap10=Q_trap10,
    e_trap=100 * abs(Q_trap - Q_exact) / Q_exact, e_left=100 * abs(Q_left - Q_exact) / Q_exact,
    e_trap10=100 * abs(Q_trap10 - Q_exact) / Q_exact)

plt = style()
# ---- 图 3.3.1：矩形和逼近速度曲线下的面积
fig, axs = plt.subplots(1, 3, figsize=(7.6, 2.6), sharey=True)
tt2 = np.linspace(0, TEND, 400)
for ax, dt in zip(axs, (1.0, 0.5, 0.1)):
    tl = np.arange(0, TEND - 1e-12, dt)
    for t0 in tl:
        ax.add_patch(plt.Rectangle((t0, 0), dt, float(vprof(t0)), fc="#cfe0f2", ec=d.VA, lw=0.6))
    ax.plot(tt2, vprof(tt2), color=d.VR, lw=1.8)
    ax.set_title(T(f"左矩形和，Δt = {dt:g} s：{sums(dt)[0]:.3f} m", f"left sum, Δt = {dt:g} s: {sums(dt)[0]:.3f} m"), fontsize=8.5)
    ax.set_xlim(0, TEND + 0.2); ax.set_ylim(0, 1.25); ax.set_xlabel("t / s"); d.spines(ax)
axs[0].set_ylabel("v / (m/s)")
fig.tight_layout()
figure(fig, "fig3_3_1")

# ---- 图 3.3.2：累积函数与它的导数
fig, axs = plt.subplots(2, 1, figsize=(5.4, 3.8), sharex=True)
axs[0].plot(tt, I(tt), color=d.VA, lw=1.6)
axs[0].fill_between(tt[tt <= 25], I(tt[tt <= 25]), color="#cfe0f2")
axs[0].text(12, 8, T("面积 = Q(25 s)", "area = Q(25 s)"), ha="center", fontsize=9, color=d.VA)
axs[0].set_ylabel("I / A"); axs[0].set_ylim(0, 40); d.spines(axs[0])
axs[1].plot(tt, Qc, color=d.VR, lw=1.6)
k = np.searchsorted(tt, 25.0)
axs[1].plot([25], [Qc[k]], "o", color=d.VR)
slope = I(25.0)
axs[1].plot([18, 32], [Qc[k] + slope * (18 - 25), Qc[k] + slope * (32 - 25)], color=d.INK, lw=1, ls="--")
axs[1].text(33, Qc[k] + slope * 8 - 60, T("切线斜率 = I(25 s)", "tangent slope = I(25 s)"), fontsize=9)
axs[1].set_ylabel(T("Q / C", "Q / C")); axs[1].set_xlabel("t / s"); d.spines(axs[1])
fig.tight_layout()
figure(fig, "fig3_3_2")
