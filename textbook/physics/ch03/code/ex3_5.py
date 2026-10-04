"""3.5 节的计算：

算例 3.5.1  dv/dt = a（常数）：AGV 以 1.5 m/s 行驶时急停，制动减速度 2.0 m/s²。由 v = v₀ + at、x = v₀t + at²/2 求停车时间和距离。
算例 3.5.2  dω/dt = −ω/τ：断电后的关节靠粘性摩擦慢慢停下，τ = J/b = 0.80 s，ω₀ = 3.0 rad/s。求 ω(t)、降到 1% 所需时间、
            半衰时间 τ ln 2，以及停下前一共转过的角度 ω₀τ（图 3.5.1）。
算例 3.5.3  欧拉法：不解方程，用 ω_{n+1} = ω_n + h·(−ω_n/τ) 一步步推进，比较 t = 2 s 时不同步长 h 的误差（图 3.5.1 右）；
            误差 ∝ h（第 8 章还要用更好的方法）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

# ---- 算例 3.5.1
v0, a = 1.5, -2.0
t_stop = -v0 / a
x_stop = v0 * t_stop + 0.5 * a * t_stop ** 2
assert abs(x_stop - v0 ** 2 / (2 * -a)) < 1e-12
out(v0=v0, adec=-a, t_stop=t_stop, x_stop=x_stop)

# ---- 算例 3.5.2
tau, w0 = 0.80, 3.0
w = lambda t: w0 * np.exp(-np.asarray(t, float) / tau)
t1 = tau * math.log(100)
th_half = tau * math.log(2)
angle = w0 * tau
out(tau=tau, w0=w0, t1=t1, th_half=th_half, angle=angle, angle_deg=math.degrees(angle),
    w_at1=float(w(1.0)), w_at_tau=float(w(tau)), frac_tau=math.exp(-1))

# ---- 算例 3.5.3：欧拉法
T2 = 2.0


def euler(h, Tend=T2):
    n = int(round(Tend / h))
    ws = [w0]
    for _ in range(n):
        ws.append(ws[-1] + h * (-ws[-1] / tau))
    return np.linspace(0, Tend, n + 1), np.array(ws)


hs = [0.4, 0.2, 0.1, 0.05, 0.01]
errs = [abs(euler(h)[1][-1] - float(w(T2))) for h in hs]
rel = [100 * e / float(w(T2)) for e in errs]
slope = np.polyfit(np.log(hs), np.log(errs), 1)[0]
out(wT=float(w(T2)), e04=errs[0], e02=errs[1], e01=errs[2], e005=errs[3], e001=errs[4],
    r04=rel[0], r01=rel[2], r001=rel[4], slope=slope)

plt = style()
# ---- 图 3.5.1：指数衰减与欧拉法
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw={"width_ratios": [1.25, 1]})
ax = axs[0]
tt = np.linspace(0, 4, 300)
ax.plot(tt, w(tt), color=d.INK, lw=2, label=T("精确解", "exact"))
for h, c in ((0.4, "#f0a35e"), (0.1, d.VA)):
    te, we = euler(h, 4.0)
    ax.plot(te, we, "o-", ms=3, lw=1, color=c, label=T(f"欧拉法 h = {h:g} s", f"Euler, h = {h:g} s"))
ax.axvline(tau, color=d.MUTED, lw=0.8, ls=":"); ax.text(tau + 0.05, 2.6, r"$t=\tau$", color=d.MUTED, fontsize=9)
ax.axhline(w0 / math.e, color=d.MUTED, lw=0.8, ls=":"); ax.text(2.6, w0 / math.e + 0.08, r"$\omega_0/\mathrm{e}$", color=d.MUTED, fontsize=9)
ax.set_xlabel("t / s"); ax.set_ylabel(r"$\omega$ / (rad/s)"); ax.legend(frameon=False, fontsize=8.5); d.spines(ax)
ax = axs[1]
ax.loglog(hs, errs, "o-", color=d.VR)
ax.set_xlabel(T("步长 h / s", "step h / s")); ax.set_ylabel(T("t = 2 s 时的误差 / (rad/s)", "error at t = 2 s / (rad/s)")); d.spines(ax)
ax.text(0.012, errs[0] * 0.5, T(f"斜率 ≈ {slope:.2f}：误差 ∝ h", f"slope ≈ {slope:.2f}: error ∝ h"), fontsize=9, color=d.VR)
fig.tight_layout()
figure(fig, "fig3_5_1")
