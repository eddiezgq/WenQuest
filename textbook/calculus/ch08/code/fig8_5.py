"""图 8.5.1：数值微分的误差随步长的变化——前向差商、中心差商、复步长法，以及误差模型。
图 8.5.2：由 17 位编码器读数估计角速度：步长 1 ms、5 ms、50 ms 的估计值，以及均方根误差随步长的变化。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _traj import quintic

TT, D, t0 = 2.0, math.radians(90), 0.5
th = lambda t: D * (10 * (t / TT) ** 3 - 15 * (t / TT) ** 4 + 6 * (t / TT) ** 5)
_, w, a, j = quintic(np.array([t0]), TT, D)
w, a, j = float(w[0]), float(a[0]), float(j[0])
eps = np.finfo(float).eps
f0 = th(t0)
hs = 10.0 ** np.linspace(-13, -1, 300)
ef = np.array([abs((th(t0 + h) - th(t0)) / h - w) for h in hs])
ec = np.array([abs((th(t0 + h) - th(t0 - h)) / (2 * h) - w) for h in hs])
es = np.array([abs(th(complex(t0, h)).imag / h - w) for h in hs])
fig, ax = plt.subplots(figsize=(11, 4.2))
ax.loglog(hs, np.maximum(ef, 1e-17), color=BLUE, lw=1, label=T("前向差商", "forward"))
ax.loglog(hs, np.maximum(ec, 1e-17), color=RED, lw=1, label=T("中心差商", "central"))
ax.loglog(hs, np.maximum(es, 1e-17), color=GREEN, lw=1, label=T("复步长法", "complex step"))
ax.loglog(hs, abs(a) * hs / 2 + 2 * eps * f0 / hs, color=BLUE, lw=2, ls="--", alpha=0.6, label=T("模型 |θ″|h/2 + 2ε|θ|/h", "model |θ″|h/2 + 2ε|θ|/h"))
ax.loglog(hs, abs(j) * hs ** 2 / 6 + eps * f0 / hs, color=RED, lw=2, ls="--", alpha=0.6, label=T("模型 |θ‴|h²/6 + ε|θ|/h", "model |θ‴|h²/6 + ε|θ|/h"))
ax.set_ylim(1e-17, 1)
ax.invert_xaxis()
ax.set_xlabel(T("步长 h / s（向右变小）", "step h / s (decreasing to the right)"))
ax.set_ylabel(T("角速度的误差 / (rad/s)", "error of angular velocity / (rad/s)"))
ax.legend(fontsize=8.5, frameon=False, ncol=2, loc="lower left")
clean(ax, zero=False)
fig.tight_layout()
figure(fig, "fig8_5_1")

q = 2 * math.pi / 2 ** 17
Ts = 1e-3
t = np.arange(0, TT + Ts / 2, Ts)
meas = np.round(th(t) / q) * q
wt = quintic(t, TT, D)[1]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4), gridspec_kw={"width_ratios": [1.5, 1]})
a1.plot(t, wt, color=INK, lw=2, label=T("真实角速度", "true velocity"))
for m, c in ((1, MUTED), (5, BLUE), (50, RED)):
    est = (meas[m:] - meas[:-m]) / (m * Ts)
    a1.plot(t[m:], est, color=c, lw=0.8 if m == 1 else 1.4, label=T(f"步长 {m} ms", f"step {m} ms"))
a1.set_xlim(0.3, 0.7)
a1.set_ylim(0.4, 1.3)
a1.set_xlabel(T("时间 t / s", "time t / s"))
a1.set_ylabel("rad/s")
a1.legend(fontsize=8.5, frameon=False, loc="upper left")
a1.set_title(T("步长太小：量化噪声被放大；太大：估计滞后", "Too small: quantization noise; too large: lag"), fontsize=10)
clean(a1, zero=False)
ms = np.array([1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 100])
rms = []
for m in ms:
    e = (meas[m:] - meas[:-m]) / (m * Ts) - wt[m:]
    rms.append(np.sqrt(np.mean(e[(t[m:] > 0.2) & (t[m:] < 1.8)] ** 2)))
a2.loglog(ms, rms, "o-", color=INK)
a2.set_xlabel(T("步长 / ms", "step / ms"))
a2.set_ylabel(T("均方根误差 / (rad/s)", "RMS error / (rad/s)"))
a2.set_title(T("存在最佳步长", "There is a best step"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig8_5_2")
