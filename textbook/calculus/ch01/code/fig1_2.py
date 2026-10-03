"""图 1.2.1：上：里程（函数 1）；下：速度（函数 2）。左：每小时一记的数据，相减与相加；右：连续变化的情形。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, axs = plt.subplots(2, 2, figsize=(10, 6), sharex="col")
h = np.arange(5)
d = h**2
axs[0, 0].plot(h, d, "o-", color=INK, lw=1.5)
for k in range(4):
    axs[0, 0].annotate("", xy=(k + 1, d[k + 1]), xytext=(k + 1, d[k]), arrowprops=dict(arrowstyle="-", color=RED, lw=2))
    axs[0, 0].text(k + 1.08, (d[k] + d[k + 1]) / 2, f"+{d[k+1]-d[k]}", color=RED)
axs[0, 0].set_ylabel(T("里程（单位里程）", "distance (units)"))
axs[0, 0].set_title(T("每小时一记：相减得速度，相加回里程", "Hourly records: subtract for speed, add back for distance"), fontsize=11)
axs[1, 0].bar(h[1:] - 0.5, np.diff(d), width=1, color="#f6d6b8", ec=RED)
for k in range(4):
    axs[1, 0].text(k + 0.5, np.diff(d)[k] + 0.2, str(np.diff(d)[k]), ha="center", color=RED)
axs[1, 0].set_ylabel(T("每小时走的里程", "distance per hour"))
axs[1, 0].set_xlabel(T("时间 / h", "time / h"))
t = np.linspace(0, 4, 400)
axs[0, 1].plot(t, 0.25 * t**2, color=INK, lw=2)
t0 = 2.5
axs[0, 1].plot(t, 0.25 * t0**2 + 0.5 * t0 * (t - t0), color=RED, lw=1.4, ls="--")
axs[0, 1].plot([t0], [0.25 * t0**2], "o", color=RED)
axs[0, 1].set_ylim(-0.2, 4.4)
axs[0, 1].set_ylabel(T("位置 x / m", "position x / m"))
axs[0, 1].set_title(T("连续变化：速度是切线斜率，位置是速度曲线下的面积", "Continuous: speed is a slope, position an area"), fontsize=11)
axs[1, 1].plot(t, 0.5 * t, color=BLUE, lw=2)
axs[1, 1].fill_between(t[t <= t0], 0.5 * t[t <= t0], color=ACC, alpha=0.3)
axs[1, 1].plot([t0], [0.5 * t0], "o", color=RED)
axs[1, 1].text(1.2, 0.15, T("面积 = 位置", "area = position"), color=INK)
axs[1, 1].set_ylabel(T("速度 v / (m/s)", "speed v / (m/s)"))
axs[1, 1].set_xlabel(T("时间 t / s", "time t / s"))
for a in axs.flat:
    clean(a)
fig.tight_layout()
figure(fig, "fig1_2_1")
