"""7.4 节的示意图。

图 7.4.1：用差商求 sin t 在 t = 1 处的导数：误差与步长（双对数坐标），截断误差与舍入误差此消彼长。
图 7.4.2：编码器测速：(a) 量化后的角度读数；(b) 均方根误差与差商跨度 h；(c) 三种估计与真实角速度。
图 7.4.3：带电流环的电机（刚性方程）：(a) 电流和转速的精确解；(b) 显式欧拉法 50 µs 与 60 µs；(c) 隐式欧拉法 1 ms。
图 7.4.4：三种方法的稳定区域（复平面上的 hλ），以及电机快、慢两个特征值与单摆特征值的位置。
"""
import math

import numpy as np
from scipy.linalg import expm

from _ode import MOTOR, link_params
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
box = dict(fc="white", ec="none", pad=1.0, alpha=0.9)
PURPLE = "#8e44ad"


def clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# ---------------------------------------------------------------- 图 7.4.1
t0 = 1.0
hs = 10.0 ** -np.arange(1, 16.01, 0.25)
fw = np.abs((np.sin(t0 + hs) - np.sin(t0)) / hs - np.cos(t0))
ce = np.abs((np.sin(t0 + hs) - np.sin(t0 - hs)) / (2 * hs) - np.cos(t0))
eps = np.finfo(float).eps
fig, ax = plt.subplots(figsize=(5.8, 4.0))
ax.loglog(hs, np.maximum(fw, 1e-17), "o-", color=C["x"], ms=3, lw=1.1, label=T("前向差商", "forward difference"))
ax.loglog(hs, np.maximum(ce, 1e-17), "s-", color=C["z"], ms=3, lw=1.1, label=T("中心差商", "central difference"))
hh = np.logspace(-16, -1, 50)
ax.loglog(hh, hh * math.sin(t0) / 2, color=C["x"], lw=0.7, ls=":")
ax.loglog(hh, hh ** 2 * math.cos(t0) / 6, color=C["z"], lw=0.7, ls=":")
ax.loglog(hh, 2 * eps * math.sin(t0) / hh, color=C["muted"], lw=0.7, ls="--")
ax.text(3e-16, 2.0, T("舍入误差 ∝ ε/h", "round-off ∝ ε/h"), color=C["muted"], fontsize=9)
ax.text(1.5e-3, 1.5e-6, T("截断误差 ∝ h", "truncation ∝ h"), color=C["x"], fontsize=9, bbox=box)
ax.text(1.5e-3, 1.5e-9, T("截断误差 ∝ h²", "truncation ∝ h²"), color=C["z"], fontsize=9, bbox=box)
ax.set_xlim(1e-16, 0.2)
ax.set_ylim(1e-12, 10)
ax.set_xlabel(T("步长 h", "step size h"))
ax.set_ylabel(T("误差", "error"))
ax.grid(True, which="major", lw=0.3, alpha=0.5)
ax.legend(loc="lower left", frameon=False, fontsize=9.5)
clean(ax)
figure(fig, "fig7_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 7.4.2
A, Om = 2.0, 2 * math.pi
q = 2 * math.pi / 16384
Ts = 1e-3
t = np.arange(0, 2.2, Ts)
theta = A * np.sin(Om * t)
theta_q = np.floor(theta / q) * q
w_true = A * Om * np.cos(Om * t)
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(12.0, 3.8), gridspec_kw=dict(wspace=0.33, width_ratios=[1, 1.1, 1.3]))
sel = (t >= 0.2495) & (t <= 0.2505 + 0.012)
tz = np.linspace(0.2495, 0.2625, 400)
a1.plot((tz - 0.25) * 1e3, (A * np.sin(Om * tz) - A) / q, color=C["ink"], lw=1.0, label=T("真实角度", "true angle"))
a1.step((t[sel] - 0.25) * 1e3, (theta_q[sel] - A) / q, where="post", color=C["x"], lw=1.2, label=T("编码器读数", "encoder reading"))
a1.plot((t[sel] - 0.25) * 1e3, (theta_q[sel] - A) / q, "o", color=C["x"], ms=3)
a1.set_xlabel(T("t − 0.25 s / ms", "t − 0.25 s / ms"))
a1.set_ylabel(T("(θ − A) / 计数", "(θ − A) / counts"))
a1.set_title(T("(a) 速度过零附近的读数", "(a) readings near zero speed"), fontsize=10.5)
a1.legend(loc="lower left", frameon=False, fontsize=8.5)
clean(a1)
ns = np.arange(1, 61)
start = 100
rb, rc = [], []
for n in ns:
    est = (theta_q[start:] - theta_q[start - n:-n]) / (n * Ts)
    rb.append(np.sqrt(np.mean((est - w_true[start:]) ** 2)))
    est = (theta_q[start + n:len(t) - n] - theta_q[start - n:len(t) - 3 * n]) / (2 * n * Ts)
    rc.append(np.sqrt(np.mean((est - w_true[start:len(t) - 2 * n]) ** 2)))
hgrid = ns * Ts
th_rms = np.sqrt((hgrid * A * Om ** 2 / (2 * math.sqrt(2))) ** 2 + (q / (math.sqrt(6) * hgrid)) ** 2)
a2.loglog(hgrid * 1e3, rb, "o", color=C["x"], ms=3.5, label=T("后向差商（仿真）", "backward difference (simulated)"))
a2.loglog(hgrid * 1e3, th_rms, color=C["x"], lw=1.0, label=T("后向差商（式 (7.4.7)）", "backward difference (Eq. (7.4.7))"))
a2.loglog(hgrid * 1e3, rc, "s", color=C["z"], ms=3.5, label=T("中心差商（仿真）", "central difference (simulated)"))
a2.set_xlabel(T("差商跨度 h / ms", "difference span h / ms"))
a2.set_ylabel(T("均方根误差 / (rad/s)", "RMS error / (rad/s)"))
a2.set_title(T("(b) 误差与跨度", "(b) error versus span"), fontsize=10.5)
a2.legend(loc="upper center", frameon=False, fontsize=8.3)
a2.set_ylim(3e-3, 3)
a2.grid(True, which="major", lw=0.3, alpha=0.5)
clean(a2)
w0, w1 = 0.62, 0.66
m = (t >= w0) & (t <= w1)
idx = np.where(m)[0]
a3.plot(t[m], w_true[m], color=C["ink"], lw=1.8, label=T("真实角速度", "true speed"))
for n, col, lab, kind in ((1, C["muted"], T("后向差商 h = 1 ms", "backward, h = 1 ms"), "b"),
                          (2, C["x"], T("后向差商 h = 2 ms", "backward, h = 2 ms"), "b"),
                          (10, C["z"], T("中心差商 h = 10 ms（晚 10 ms 得到）", "central, h = 10 ms (10 ms late)"), "c")):
    if kind == "b":
        est = (theta_q[idx] - theta_q[idx - n]) / (n * Ts)
    else:
        est = (theta_q[idx + n] - theta_q[idx - n]) / (2 * n * Ts)
    a3.plot(t[idx], est, color=col, lw=0.9 if n == 1 else 1.2, label=lab)
a3.set_xlabel(T("时间 t / s", "time t / s"))
a3.set_ylabel(T("角速度 / (rad/s)", "speed / (rad/s)"))
a3.set_title(T("(c) 估计出的角速度", "(c) estimated speed"), fontsize=10.5)
a3.legend(loc="upper right", frameon=False, fontsize=8.3)
clean(a3)
figure(fig, "fig7_4_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 7.4.3
mo = MOTOR
Kp, Kv, w_ref = 20.0, 0.04, 100.0
L, R, Kt, Ke, Jm, b = mo["L"], mo["R"], mo["Kt"], mo["Ke"], mo["Jm"], mo["b"]
Am = np.array([[-(R + Kp) / L, -(Ke + Kp * Kv) / L], [Kt / Jm, -b / Jm]])
Bm = np.array([Kp * Kv * w_ref / L, 0.0])
x_eq = -np.linalg.solve(Am, Bm)
ex = lambda s: x_eq + expm(Am * s) @ (-x_eq)
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(12.6, 3.7), gridspec_kw=dict(wspace=0.55))
tt = np.concatenate([np.linspace(0, 0.002, 200), np.linspace(0.002, 0.1, 300)])
X = np.array([ex(s) for s in tt])
a1.plot(tt * 1e3, X[:, 1], color=C["z"], lw=1.6, label=T("转速 ω / (rad/s)", "speed ω / (rad/s)"))
a1b = a1.twinx()
a1b.plot(tt * 1e3, X[:, 0], color=C["accent"], lw=1.4)
a1b.set_ylabel(T("电流 i / A", "current i / A"), color=C["accent"])
a1.set_xlabel(T("时间 t / ms", "time t / ms"))
a1.set_ylabel(T("转速 ω / (rad/s)", "speed ω / (rad/s)"), color=C["z"])
a1.set_title(T("(a) 精确解：电流约 0.2 ms 时达到峰值", "(a) exact: the current peaks at about 0.2 ms"), fontsize=10)
a1.text(28, 60, T("转速：时间常数约 20 ms，\n约 60 ms 达到 95%", "speed: time constant ~20 ms,\n95% at ~60 ms"), color=C["z"], fontsize=9, bbox=box)
a1.text(12, 20, T("电流", "current"), color=C["accent"], fontsize=9, bbox=box)
for h, col, lab in ((60e-6, C["x"], "h = 60 µs"), (50e-6, C["y"], "h = 50 µs")):
    x = np.zeros(2)
    ts_, ws_ = [0.0], [0.0]
    for k in range(int(round(0.012 / h))):
        x = x + h * (Am @ x + Bm)
        ts_.append((k + 1) * h)
        ws_.append(x[1])
    a2.plot(np.array(ts_) * 1e3, ws_, color=col, lw=0.7, label=T("显式欧拉法 ", "explicit Euler, ") + lab)
a2.plot(tt[tt < 0.012] * 1e3, X[tt < 0.012, 1], color=C["ink"], lw=1.0, ls="--", label=T("精确解", "exact"))
a2.set_ylim(-150, 250)
a2.set_xlabel(T("时间 t / ms", "time t / ms"))
a2.set_ylabel(T("转速 ω / (rad/s)", "speed ω / (rad/s)"))
a2.set_title(T("(b) 显式欧拉法：步长稍大即发散", "(b) explicit Euler: a little too large and it blows up"), fontsize=10)
a2.legend(loc="lower left", frameon=False, fontsize=8.5)
clean(a2)
h = 1e-3
Mi = np.linalg.inv(np.eye(2) - h * Am)
x = np.zeros(2)
xs = [x.copy()]
for k in range(100):
    x = Mi @ (x + h * Bm)
    xs.append(x.copy())
xs = np.array(xs)
tk = np.arange(len(xs)) * h
a3.plot(tt * 1e3, X[:, 1], color=C["ink"], lw=1.2, ls="--", label=T("精确解", "exact"))
a3.plot(tk * 1e3, xs[:, 1], "o", color=PURPLE, ms=3, label=T("隐式欧拉法 h = 1 ms", "implicit Euler, h = 1 ms"))
a3.set_xlabel(T("时间 t / ms", "time t / ms"))
a3.set_ylabel(T("转速 ω / (rad/s)", "speed ω / (rad/s)"))
a3.set_title(T("(c) 隐式欧拉法：步长为上限的 18 倍仍稳定", "(c) implicit Euler: stable at ~18× the explicit limit"), fontsize=10)
a3.legend(loc="lower right", frameon=False, fontsize=8.5)
clean(a3)
figure(fig, "fig7_4_3")
plt.close(fig)

# ---------------------------------------------------------------- 图 7.4.4
fig, ax = plt.subplots(figsize=(6.4, 4.6))
xr = np.linspace(-4.5, 2.5, 600)
yr = np.linspace(-3.5, 3.5, 600)
X_, Y_ = np.meshgrid(xr, yr)
Z = X_ + 1j * Y_
g_rk4 = np.abs(1 + Z + Z ** 2 / 2 + Z ** 3 / 6 + Z ** 4 / 24)
g_eu = np.abs(1 + Z)
g_im = np.abs(1 / (1 - Z))
ax.contourf(X_, Y_, (g_im <= 1).astype(float), levels=[0.5, 1.5], colors=[PURPLE], alpha=0.12)
ax.contourf(X_, Y_, (g_rk4 <= 1).astype(float), levels=[0.5, 1.5], colors=[C["z"]], alpha=0.25)
ax.contourf(X_, Y_, (g_eu <= 1).astype(float), levels=[0.5, 1.5], colors=[C["x"]], alpha=0.35)
ax.contour(X_, Y_, g_eu, levels=[1], colors=[C["x"]], linewidths=1.2)
ax.contour(X_, Y_, g_rk4, levels=[1], colors=[C["z"]], linewidths=1.2)
ax.contour(X_, Y_, g_im, levels=[1], colors=[PURPLE], linewidths=1.2, linestyles="--")
ax.axhline(0, color=C["ink"], lw=0.6)
ax.axvline(0, color=C["ink"], lw=0.6)
ax.text(-1.55, 0.2, T("欧拉法", "Euler"), color=C["x"], fontsize=10, bbox=box)
ax.text(-2.6, 2.35, T("RK4", "RK4"), color=C["z"], fontsize=10, bbox=box)
ax.text(1.0, 2.45, T("隐式欧拉法：\n圆外全部稳定", "implicit Euler:\nstable outside the circle"), color=PURPLE, fontsize=9.5, bbox=box)
Jo, lc, wn2 = link_params()
for z, lab, dy in ((0.02 * math.sqrt(wn2) * 1j, T("单摆 hλ = ±ihω_n（h = 0.02 s）", "pendulum hλ = ±ihω_n (h = 0.02 s)"), 0.35),):
    ax.plot([0, 0], [z.imag, -z.imag], "o", color=C["accent"], ms=5)
    ax.annotate(lab.replace("ω_n", "$\\omega_n$").replace("hλ", "$h\\lambda$").replace("±ih", "$\\pm ih$"),
                xy=(0, z.imag), xytext=(0.25, 1.2), fontsize=9, color=C["accent"],
                arrowprops=dict(arrowstyle="-", color=C["accent"], lw=0.7))
ax.annotate(T("电机快模态 hλ ≈ −35（h = 1 ms），在左边很远处", "fast motor mode hλ ≈ −35 (h = 1 ms), far to the left"),
            xy=(-4.4, 0), xytext=(-4.3, -2.6), fontsize=9, color=C["ink"],
            arrowprops=dict(arrowstyle="-|>", color=C["ink"], lw=0.8))
ax.text(-4.3, -3.2, T("显式方法：不稳定；隐式欧拉法：稳定", "explicit: unstable; implicit Euler: stable"), fontsize=9)
ax.set_xlabel(T("Re(hλ)", "Re(hλ)"))
ax.set_ylabel(T("Im(hλ)", "Im(hλ)"))
ax.set_xlim(-4.5, 2.5)
ax.set_ylim(-3.5, 3.5)
ax.set_aspect("equal")
figure(fig, "fig7_4_4")
plt.close(fig)
