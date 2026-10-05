"""4.2 节的计算：

算例 4.2.2（生活中的例子）  博尔特 2009 年柏林世锦赛 100 m 决赛（9.58 s，世界纪录）的 10 m 分段时间（从发令枪响起算，
            含起跑反应时间 0.146 s，数据见国际田联生物力学报告）。求每 10 m 的平均速度、全程平均速度，以及速度最快的一段
            （图 4.2.2）。
"""
import numpy as np

from bookout import T, figure, out, style
import _draw as d

x = np.arange(0, 101, 10.0)
t = np.array([0, 1.89, 2.88, 3.78, 4.64, 5.47, 6.29, 7.10, 7.92, 8.75, 9.58])
vseg = np.diff(x) / np.diff(t)
k = int(np.argmax(vseg))
out(T100=t[-1], vavg=100 / t[-1], vmax=vseg[k], seg_from=x[k], seg_to=x[k + 1], v1=vseg[0], v2=vseg[1], vlast=vseg[-1],
    react=0.146, kmh=vseg[k] * 3.6, t1=t[1], t5=t[5], v_second_half=50 / (t[-1] - t[5]), v_first_half=50 / t[5])

plt = style()
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.0))
ax = axs[0]
ax.plot(t, x, "o-", color=d.INK, ms=4, lw=1.4)
ax.plot([0, t[-1]], [0, 100], color=d.VR, lw=1, ls="--")
ax.text(5.6, 40, T(f"全程平均 {100 / t[-1]:.2f} m/s", f"mean {100 / t[-1]:.2f} m/s"), color=d.VR, fontsize=8.5)
ax.set_xlabel("t / s"); ax.set_ylabel("x / m"); d.spines(ax)
ax = axs[1]
ax.stairs(vseg, x, color=d.VA, lw=2, baseline=None)
ax.axhline(100 / t[-1], color=d.VR, lw=1, ls="--")
ax.set_xlabel("x / m"); ax.set_ylabel(T("10 m 段的平均速度 / (m/s)", "mean speed per 10 m / (m/s)")); ax.set_ylim(0, 13.5); d.spines(ax)
ax.text(x[k] + 5, vseg[k] + 0.3, f"{vseg[k]:.2f}", ha="center", color=d.VA, fontsize=8.5)
fig.tight_layout()
figure(fig, "fig4_2_2")
