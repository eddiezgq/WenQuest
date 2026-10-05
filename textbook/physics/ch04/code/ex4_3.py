"""4.3 节的计算：

算例 4.3.1  4.1 节 AGV 往返一趟的 a–t 图：起步、刹车、倒车起步、倒车刹车时加速度的正负；“减速”不等于“加速度为负”（图 4.3.1）。
表 4.3.1    几种运动的加速度（数量级），用 g 的倍数表示：AGV 起步、电梯起动、轿车 8 s 内从静止加速到 100 km/h、
            博尔特起跑后的头 10 m（按匀加速估算）、自由落体。
"""
import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d
from _kin import trapezoid

P1, P2 = trapezoid(12.0, 1.0, 0.5), trapezoid(6.0, 1.0, 0.5)
t2 = P1["T"] + 4.0                                  # 倒车开始的时刻
Ttot = t2 + P2["T"]
tt = np.linspace(0, Ttot, 5201)
V = np.where(tt < P1["T"], P1["v"](tt), np.where(tt < t2, 0.0, -P2["v"](tt - t2)))
A = np.where(tt < P1["T"], P1["a"](tt), np.where(tt < t2, 0.0, -P2["a"](tt - t2)))

# 表 4.3.1
car = (100 / 3.6) / 8.0
bolt = 2 * 10 / (1.89 - 0.146) ** 2                  # 头 10 m 按从静止匀加速估算（扣除反应时间）
rows = dict(agv=0.5, lift=1.0, car=car, bolt=bolt, fall=g)
out(**{f"a_{k}": v for k, v in rows.items()}, **{f"n_{k}": v / g for k, v in rows.items()}, am=0.5, t2=t2, Ttot=Ttot)

plt = style()
fig, axs = plt.subplots(2, 1, figsize=(6.0, 4.4), sharex=True)
ax = axs[0]
ax.plot(tt, V, color=d.VA, lw=2); ax.axhline(0, color=d.MUTED, lw=0.8)
ax.set_ylabel("v / (m/s)"); ax.set_ylim(-1.3, 1.3); d.spines(ax)
ax = axs[1]
ax.plot(tt, A, color=d.VR, lw=2); ax.axhline(0, color=d.MUTED, lw=0.8)
lab = [(2.4, 0.8, T("起步：v > 0，a > 0\n越来越快", "start: v > 0, a > 0\nspeeding up")),
       (6.4, -0.85, T("刹车：v > 0，a < 0\n越来越慢", "brake: v > 0, a < 0\nslowing")),
       (t2 + 2.3, -0.85, T("倒车起步：v < 0，a < 0\n越来越快", "reverse: v < 0, a < 0\nspeeding up")),
       (Ttot - 7.6, 0.95, T("倒车刹车：v < 0，a > 0\n越来越慢", "reverse brake: v < 0, a > 0\nslowing"))]
pts = [(1.0, 0.5), (13.0, -0.5), (19.0, -0.5), (25.0, 0.5)]          # 各段加速度的位置
for (x0, y0, s), xy in zip(lab, pts):
    ax.annotate(s, xy=xy, xytext=(x0, y0), fontsize=8, color=d.INK, va="center", arrowprops=dict(arrowstyle="->", color=d.MUTED, lw=0.7))
ax.set_xlabel("t / s"); ax.set_ylabel(r"a / (m/s$^2$)"); ax.set_ylim(-1.3, 1.3); d.spines(ax)
fig.tight_layout()
figure(fig, "fig4_3_1")
