"""17.3 节的计算：

算例 17.3.1  转动圆环上的珠子：半径 0.15 m 的光滑圆环绕竖直直径以角速度 ω 匀速转动，珠子可沿环无摩擦滑动。
            由拉格朗日方程求珠子的平衡位置；ω 超过多大时最低点不再稳定？ω = 12 rad/s 时珠子停在哪里（图 17.3.1）？
算例 17.3.2  行车吊运：小车由电机按给定的速度曲线带动，吊绳长 4.0 m。小车用 2.0 s 和用一个摆动周期的时间
            匀加速到 1.0 m/s，然后匀速。由拉格朗日方程得到摆角的运动方程，数值求解，比较两种加速方式留下的摆动（图 17.3.2）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d


def rk4(f, y, t, dt):
    k1 = f(t, y); k2 = f(t + dt / 2, y + dt / 2 * k1); k3 = f(t + dt / 2, y + dt / 2 * k2); k4 = f(t + dt, y + dt * k3)
    return y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def lagrange_check(Lfun, q, qd, qdd, e=1e-5):
    """数值核对：d/dt(∂L/∂q̇) − ∂L/∂q，用于检验手推的运动方程。t 固定时只对 q、q̇ 求导。"""
    dLdqd = lambda q_, qd_: (Lfun(q_, qd_ + e) - Lfun(q_, qd_ - e)) / (2 * e)
    ddt = (dLdqd(q + qd * e, qd + qdd * e) - dLdqd(q - qd * e, qd - qdd * e)) / (2 * e)
    return ddt - (Lfun(q + e, qd) - Lfun(q - e, qd)) / (2 * e)


# ---- 算例 17.3.1：转动圆环上的珠子。θ 从最低点量起；L = ½mR²(θ̇² + ω² sin²θ) + mgR cosθ（取 m = 1）
R, w12 = 0.15, 12.0
wc = math.sqrt(g / R)


def bead_acc(th, w):
    return math.sin(th) * (w * w * math.cos(th) - g / R)


for th, thd, w in [(0.7, 1.3, 12.0), (2.0, -0.4, 5.0)]:
    Lb = lambda q, qd: 0.5 * R * R * (qd * qd + w * w * math.sin(q) ** 2) + g * R * math.cos(q)
    a = bead_acc(th, w)
    assert abs(lagrange_check(Lb, th, thd, a)) < 1e-6
th_eq = math.acos(g / (R * w12 * w12))
out(R=R, wc=wc, w12=w12, th12=math.degrees(th_eq), Om12=w12 * math.sin(th_eq))

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
ws = np.linspace(0, 20, 400)
ax.plot(ws[ws <= wc], 0 * ws[ws <= wc], color=d.VA, lw=2, label=T("稳定平衡", "stable"))
ax.plot(ws[ws >= wc], 0 * ws[ws >= wc], color=d.VA, lw=1.5, ls="--", label=T("不稳定平衡", "unstable"))
wb = ws[ws >= wc]
ax.plot(wb, np.degrees(np.arccos(g / (R * wb ** 2))), color=d.VA, lw=2)
ax.axhline(90, color=d.MUTED, lw=0.7, ls=":")
ax.axvline(wc, color=d.MUTED, lw=0.7, ls=":")
ax.text(wc + 0.3, 8, r"$\omega_\mathrm{c} = \sqrt{g/R}$", fontsize=9)
ax.plot([w12], [math.degrees(th_eq)], "o", color=d.VR, ms=6)
ax.annotate(T("ω = 12 rad/s", "ω = 12 rad/s"), (w12, math.degrees(th_eq)), xytext=(12, -16), textcoords="offset points", fontsize=8.5, color=d.VR)
ax.set_xlabel(T("圆环的角速度 ω / (rad/s)", "hoop angular velocity ω / (rad/s)"))
ax.set_ylabel(T("平衡位置 θ / (°)", "equilibrium θ / (°)"))
ax.set_ylim(-5, 100); ax.legend(frameon=False, fontsize=8.5, loc="center right")
d.spines(ax)
figure(fig, "fig17_3_1")

# ---- 算例 17.3.2：行车。小车位置 X(t) 给定；L = ½m[(Ẋ + lθ̇ cosθ)² + (lθ̇ sinθ)²] + mgl cosθ
# 拉格朗日方程：l θ̈ + Ẍ cosθ + g sinθ = 0
l, vmax = 4.0, 1.0
Tp = 2 * math.pi * math.sqrt(l / g)


def crane_run(ta, tend=20.0, dt=1e-3):
    a = vmax / ta
    acc = lambda t: a if t < ta else 0.0
    f = lambda t, y: np.array([y[1], -(acc(t) * math.cos(y[0]) + g * math.sin(y[0])) / l])
    ts, ys, y, t = [0.0], [0.0], np.array([0.0, 0.0]), 0.0
    while t < tend - 1e-12:
        y = rk4(f, y, t, dt); t += dt; ts.append(t); ys.append(y[0])
    ts, ys = np.array(ts), np.array(ys)
    return ts, ys, np.max(np.abs(ys[ts > ta]))


# 核对运动方程：X 取任意给定的加速度，比较数值的 d/dt ∂L/∂θ̇ − ∂L/∂θ 与手推的结果（t 显含于 Ẋ，用一个瞬时值检验）
Xd, Xdd = 0.6, 0.25
Lc = lambda q, qd: 0.5 * ((Xd + l * qd * math.cos(q)) ** 2 + (l * qd * math.sin(q)) ** 2) + g * l * math.cos(q)
th, thd = 0.2, -0.3
thdd = -(Xdd * math.cos(th) + g * math.sin(th)) / l
e = 1e-5
dLdqd = lambda q, qd, X_d: l * math.cos(q) * (X_d + l * qd * math.cos(q)) + l * l * qd * math.sin(q) ** 2
ddt = (dLdqd(th + thd * e, thd + thdd * e, Xd + Xdd * e) - dLdqd(th - thd * e, thd - thdd * e, Xd - Xdd * e)) / (2 * e)
assert abs(ddt - (Lc(th + e, thd) - Lc(th - e, thd)) / (2 * e)) < 1e-6

t2, y2, r2 = crane_run(2.0)
tT, yT, rT = crane_run(Tp)
small = 2 * (vmax / 2.0) / g * abs(math.sin(math.pi * 2.0 / Tp))         # 小角度近似下加速 2.0 s 留下的振幅
assert abs(math.degrees(small) - math.degrees(r2)) < 0.1
out(l=l, Tp=Tp, res2=math.degrees(r2), resT=math.degrees(rT), max2=math.degrees(np.max(np.abs(y2))), maxT=math.degrees(np.max(np.abs(yT))))

fig, ax = plt.subplots(figsize=(4.8, 2.9))
ax.plot(t2, np.degrees(y2), color=d.VR, lw=1.8, label=T("用 2.0 s 加速", "accelerate in 2.0 s"))
ax.plot(tT, np.degrees(yT), color=d.VA, lw=1.8, label=T("用一个摆动周期加速", "accelerate in one swing period"))
ax.axvspan(0, 2.0, color=d.VR, alpha=0.08); ax.axvspan(0, Tp, color=d.VA, alpha=0.06)
ax.axhline(0, color=d.MUTED, lw=0.6)
ax.set_xlabel(T("时间 t / s", "time t / s")); ax.set_ylabel(T("摆角 θ / (°)", "swing angle θ / (°)"))
ax.legend(frameon=False, fontsize=8.5, loc="lower center", ncol=2, bbox_to_anchor=(0.5, 1.0)); ax.set_xlim(0, 20)
d.spines(ax)
figure(fig, "fig17_3_2")
