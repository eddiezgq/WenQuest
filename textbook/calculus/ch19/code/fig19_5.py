"""图 19.5.1：左：水面机器人始终对准码头渡河的轨迹（k = w/s = 0.25、0.5、0.75、1）；
右：无人机减速滑行（伯努利方程）的速度与距离。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
a = 50.0
x = np.linspace(1e-4, a, 800)
for k, col in ((0.25, GREEN), (0.5, BLUE), (0.75, ACC), (1.0, RED)):
    y = a / 2 * ((x / a) ** (1 - k) - (x / a) ** (1 + k))
    a1.plot(x, y, color=col, lw=2, label=f"k = {k:g}")
a1.plot([0], [0], "s", color=INK)
a1.text(1, -2.5, T("码头", "dock"), fontsize=9)
a1.plot([a], [0], "o", color=INK)
a1.text(a - 6, -2.5, T("出发", "start"), fontsize=9)
a1.annotate("", xy=(5, 21), xytext=(5, 16), arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.5))
a1.text(6, 18, T("水流", "current"), color=MUTED, fontsize=9)
a1.set_xlim(-2, 52)
a1.set_ylim(-4, 28)
a1.set_xlabel(T("离码头的横向距离 x / m", "distance across x / m"))
a1.set_ylabel(T("下漂 y / m", "drift y / m"))
a1.set_title(T("船头始终对准码头：k = 水速/船速", "Always heading for the dock: k = current / boat speed"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="upper right")
clean(a1)
m, c1, c2, v0 = 1.5, 0.3, 0.05, 10.0
t = np.linspace(0, 25, 500)
e = np.exp(-c1 * t / m)
v = c1 * v0 * e / (c1 + c2 * v0 * (1 - e))
xd = m / c2 * np.log(1 + c2 * v0 / c1 * (1 - e))
a2.plot(t, v, color=BLUE, lw=2, label=T("速度 v(t)", "speed v(t)"))
a2.set_xlabel(T("时间 t / s", "time t / s"))
a2.set_ylabel(T("速度 / (m/s)", "speed / (m/s)"), color=BLUE)
b = a2.twinx()
b.plot(t, xd, color=ACC, lw=2)
b.axhline(m / c2 * np.log(1 + c2 * v0 / c1), color=ACC, ls=":", lw=1)
b.set_ylabel(T("滑行距离 x(t) / m（虚线为上限 29.4 m）", "glide distance x(t) / m (dotted: limit 29.4 m)"), color=ACC, fontsize=9)
b.spines["top"].set_visible(False)
a2.set_title(T("无人机减速滑行：速度永不为零，距离有上限", "Drone glide: speed never reaches zero, distance is bounded"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig19_5_1")
