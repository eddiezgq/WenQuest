"""图 13.6.2：陀螺仪积分的漂移。左：航向角误差随时间的变化——未标定（零偏 0.05°/s 线性漂移）、
静止 5 s 标定后（只剩噪声的随机游走与标定残差）；右：AGV 以 1 m/s 行驶 60 s 的真实轨迹与航位推算轨迹。"""
import math
import random

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

Ts, Tend, sig, bias = 0.01, 65.0, 0.1, 0.05
rnd = random.Random(13)


def yaw_rate(tt):
    if tt < 5:
        return 0.0
    u = (tt - 5) % 20
    return 45 * (1 - math.cos(math.pi * u)) if u < 2 else 0.0


n = int(round(Tend / Ts))
ts = np.arange(n + 1) * Ts
w = np.array([yaw_rate(t) for t in ts])
m = w + bias + np.array([rnd.gauss(0, sig) for _ in ts])
th = np.concatenate([[0], np.cumsum((w[1:] + w[:-1]) / 2 * Ts)])
raw = np.concatenate([[0], np.cumsum((m[1:] + m[:-1]) / 2 * Ts)])
k5 = int(round(5 / Ts))
cal = raw - m[:k5].mean() * ts
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
a1.plot(ts, raw - th, color=RED, lw=1.5, label=T("未标定", "uncalibrated"))
a1.plot(ts, cal - th, color=BLUE, lw=1.5, label=T("静止 5 s 标定零偏后", "after 5 s bias calibration"))
a1.plot(ts, bias * ts, color=MUTED, lw=0.8, ls="--", label=T("零偏 × t", "bias × t"))
a1.set_xlabel("t / s")
a1.set_ylabel(T("航向角误差 / (°)", "heading error / (°)"))
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("零偏的积分随时间线性增长", "The integral of a bias grows linearly"), fontsize=10)
clean(a1)
v = np.where(ts >= 5, 1.0, 0.0)


def path(h):
    hr = np.radians(h)
    x = np.concatenate([[0], np.cumsum(v[1:] * np.cos(hr[1:]) * Ts)])
    y = np.concatenate([[0], np.cumsum(v[1:] * np.sin(hr[1:]) * Ts)])
    return x, y


for h, c, lab in ((th, INK, T("真实轨迹", "true path")), (raw, RED, T("未标定", "uncalibrated")), (cal, BLUE, T("标定后", "calibrated"))):
    x, y = path(h)
    a2.plot(x, y, color=c, lw=1.6 if c != INK else 2.4, label=lab, ls="-" if c != BLUE else "--")
a2.set_aspect("equal")
a2.set_xlabel("x / m")
a2.set_ylabel("y / m")
a2.legend(fontsize=9, frameon=False, loc="lower right")
a2.set_title(T("航位推算：航向误差再积分成位置误差", "Dead reckoning: heading error integrates into position error"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig13_6_2")
