"""4.6 节的计算：

算例 4.6.1  加速度已知是时间的函数：AGV 上的加速度计每 10 ms 给一个读数，积分一次得速度、两次得位置。读数有 0.02 m/s²
            的零点偏差 β 和随机噪声（标准差 0.05 m/s²），看速度和位置的误差怎样随时间增长（图 4.6.1）：零点偏差造成的
            位置误差 ≈ ½βt²。
算例 4.6.2  加速度是速度的函数：驱动电机的转矩随转速增大而下降，AGV 的加速度近似为 a = a₀(1 − v/v_∞)。
            分离变量积分得 v = v_∞(1 − e^(−t/τ))，τ = v_∞/a₀；正是 3.3 节算例 3.3.1 的速度曲线。
算例 4.6.3  加速度是位置的函数：轨道尽头的缓冲器像一根弹簧，a = −(k/m)x。用 a = v dv/dx 积分得 v² = v₀² − (k/m)x²，
            求最大压缩量和最大减速度（图 4.6.2）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d
from _kin import trapezoid

# ---- 算例 4.6.1
P = trapezoid(6.0, 1.0, 0.5)
dt = 0.01
t = np.arange(0, 30 + 1e-9, dt)
a_true = P["a"](t)
rng = np.random.default_rng(46)
beta, sig = 0.02, 0.05                       # 零点偏差 β 与随机噪声的标准差
a_meas = a_true + beta + rng.normal(0, sig, t.size)
cum = lambda y: np.concatenate([[0], np.cumsum((y[1:] + y[:-1]) / 2) * dt])
v_est, v_true = cum(a_meas), cum(a_true)
x_est, x_true = cum(v_est), cum(v_true)
i10, i30 = int(round(10 / dt)), int(round(30 / dt))
out(beta=beta, sig=sig, ex10=x_est[i10] - x_true[i10], ex30=x_est[i30] - x_true[i30], ev30=v_est[i30] - v_true[i30],
    eb10=0.5 * beta * 10 ** 2, eb30=0.5 * beta * 30 ** 2, T_move=P["T"])

# ---- 算例 4.6.2
vinf, a0 = 1.0, 1.0 / 1.2
tau = vinf / a0
vt = lambda tt: vinf * (1 - np.exp(-tt / tau))
tt = np.linspace(0, 6, 6001)
v_num = np.zeros_like(tt)
for i in range(1, tt.size):                          # 小步长欧拉法核对
    v_num[i] = v_num[i - 1] + (tt[1] - tt[0]) * a0 * (1 - v_num[i - 1] / vinf)
assert np.max(np.abs(v_num - vt(tt))) < 1e-3
out(vinf=vinf, a0=a0, tau=tau, x5=5 - tau * (1 - math.exp(-5 / tau)), v_at_3tau=vt(3 * tau))

# ---- 算例 4.6.3
m, k, v0 = 500.0, 20e3, 0.50
xmax = v0 * math.sqrt(m / k)
amax = k * xmax / m
tstop = math.pi / 2 * math.sqrt(m / k)
out(m=m, k_kN=k / 1000, v0=v0, xmax_mm=1000 * xmax, amax=amax, tstop=tstop)

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.0))
ax = axs[0]
ax.plot(t, v_true, color=d.INK, lw=2, label=T("真实", "true"))
ax.plot(t, v_est, color=d.VR, lw=1.2, label=T("积分加速度计", "integrated"))
ax.set_xlabel("t / s"); ax.set_ylabel("v / (m/s)"); ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
ax = axs[1]
ax.plot(t, x_est - x_true, color=d.VR, lw=1.5, label=T("位置误差", "position error"))
ax.plot(t, 0.5 * beta * t ** 2, color=d.MUTED, lw=1, ls="--", label=r"$\frac{1}{2}\beta t^2$")
ax.set_xlabel("t / s"); ax.set_ylabel(T("位置误差 / m", "position error / m")); ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
fig.tight_layout()
figure(fig, "fig4_6_1")

fig, ax = plt.subplots(figsize=(4.6, 3.0))
xs = np.linspace(0, xmax, 300)
ax.plot(xs * 1000, np.sqrt(np.maximum(0, v0 ** 2 - k / m * xs ** 2)), color=d.VA, lw=2)
ax.set_xlabel(T("缓冲器压缩量 x / mm", "buffer compression x / mm")); ax.set_ylabel("v / (m/s)"); d.spines(ax)
ax2 = ax.twinx()
ax2.plot(xs * 1000, k / m * xs, color=d.VR, lw=1.5, ls="--")
ax2.set_ylabel(T("减速度 / (m/s²)", "deceleration / (m/s²)"), color=d.VR); ax2.tick_params(axis="y", colors=d.VR)
for sp in ("top",):
    ax2.spines[sp].set_visible(False)
ax.text(30, 0.04, T("实线：速度；虚线：减速度", "solid: speed; dashed: deceleration"), fontsize=8, color=d.MUTED)
figure(fig, "fig4_6_2")
