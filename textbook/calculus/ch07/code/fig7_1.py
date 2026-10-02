"""图 7.1.1：AGV 位置曲线上的割线逐渐变成切线；图 7.1.2：前向差商与中心差商的误差随步长 h 的变化。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt
from _traj import quintic

x = lambda t: 0.25 * t**2
fig, ax = plt.subplots(figsize=(6.4, 4.4))
tt = np.linspace(0, 4.4, 300)
ax.plot(tt, x(tt), color=INK, lw=2)
for h, c in ((2.0, MUTED), (1.0, BLUE), (0.5, GREEN)):
    m = (x(2 + h) - x(2)) / h
    ax.plot(tt, x(2) + m * (tt - 2), color=c, lw=1.2, ls="--")
    ax.plot([2 + h], [x(2 + h)], "o", color=c, ms=5)
    ax.text(2 + h + 0.06, x(2 + h) - 0.18, f"$h={h:g}$", color=c, fontsize=10)
ax.plot(tt, 1 + 1.0 * (tt - 2), color=RED, lw=2)
ax.plot([2], [1], "o", color=RED, ms=7, mec=INK)
ax.text(2.05, 0.62, "$P(2,\\,1)$", fontsize=11)
ax.text(3.1, 1.7, T("切线：斜率 1 m/s", "tangent: slope 1 m/s"), color=RED, fontsize=11)
ax.set_xlim(0, 4.4)
ax.set_ylim(-0.3, 4.6)
ax.set_xlabel(T("时间 t / s", "time t / s"))
ax.set_ylabel(T("位置 x / m", "position x / m"))
clean(ax, zero=False)
ax.set_title(T("割线 PQ 绕 P 转动，趋向切线", "The secant PQ turns about P towards the tangent"), fontsize=12)
fig.tight_layout()
figure(fig, "fig7_1_1")

T2, D = 2.0, math.pi / 2
th = lambda t: float(quintic(t, T2, D)[0])
w = float(quintic(0.5, T2, D)[1])
hs = 10.0 ** -np.arange(1, 14.01, 0.25)
ef = [abs((th(0.5 + h) - th(0.5)) / h - w) for h in hs]
ec = [abs((th(0.5 + h) - th(0.5 - h)) / (2 * h) - w) for h in hs]
fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.loglog(hs, ef, "o-", color=BLUE, ms=3, lw=1.2, label=T("前向差商", "forward quotient"))
ax.loglog(hs, ec, "s-", color=RED, ms=3, lw=1.2, label=T("中心差商", "central quotient"))
ax.loglog(hs, 1.1 * hs, color=MUTED, ls=":", lw=1)
ax.loglog(hs, 0.25 * hs**2, color=MUTED, ls=":", lw=1)
ax.loglog(hs, 1e-16 / hs, color=MUTED, ls=":", lw=1)
ax.text(2e-3, 6e-3, "$\\propto h$", color=MUTED)
ax.text(3e-3, 4e-8, "$\\propto h^2$", color=MUTED)
ax.text(1e-12, 3e-3, "$\\propto 1/h$", color=MUTED)
ax.set_ylim(1e-13, 1)
ax.set_xlabel(T("步长 h / s", "step h / s"))
ax.set_ylabel(T("误差 / (rad/s)", "error / (rad/s)"))
ax.invert_xaxis()
ax.legend(frameon=False)
clean(ax, zero=False)
ax.set_title(T("步长变小，误差先减小后增大", "As h shrinks the error first falls, then rises"), fontsize=12)
fig.tight_layout()
figure(fig, "fig7_1_2")
