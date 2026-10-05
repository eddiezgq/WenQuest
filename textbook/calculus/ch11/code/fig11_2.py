"""图 11.2.1：左：x(t) = t³ − 6t² + 9t 的位置、速度、加速度，阴影为加速（v、a 同号）的时段；
右：AGV 的安全车速随探测距离的变化，反应时间 0.2 s 与 0.4 s。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
t = np.linspace(0, 4, 400)
x = t ** 3 - 6 * t ** 2 + 9 * t
v = 3 * t * t - 12 * t + 9
a = 6 * t - 12
speedup = v * a > 0
a1.fill_between(t, -12, 12, where=speedup, color=GREEN, alpha=0.1, lw=0)
a1.plot(t, x, color=INK, lw=2, label="x(t)")
a1.plot(t, v, color=BLUE, lw=1.6, label="v(t)")
a1.plot(t, a, color=RED, lw=1.6, label="a(t)")
a1.set_ylim(-12, 12)
a1.set_xlabel("t / s")
a1.set_title(T("绿色时段 v、a 同号：越走越快", "Green: v and a share a sign, speeding up"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="lower right")
clean(a1)
d = np.linspace(0.2, 8, 300)
ab = 1.5
for tr, c in ((0.2, BLUE), (0.4, RED)):
    a2.plot(d, ab * (-tr + np.sqrt(tr * tr + 2 * d / ab)), color=c, lw=2, label=T(f"反应时间 {tr} s", f"reaction time {tr} s"))
a2.set_xlabel(T("探测距离 d / m", "sensing distance d / m"))
a2.set_ylabel(T("安全车速 / (m/s)", "safe speed / (m/s)"))
a2.set_title(T("v t_r + v²/(2a_b) ≤ d：车速只随距离的平方根增长", "v t_r + v²/(2a_b) ≤ d: speed grows only like √d"), fontsize=10)
a2.legend(fontsize=9, frameon=False)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig11_2_1")
