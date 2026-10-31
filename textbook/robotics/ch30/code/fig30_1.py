"""30.1 节的示意图。

图 30.1.1：减速器厂部件装配工位（示例布置）。(a) 俯视：机器人装在工作台上，六个取放点、WQ-CR5 的臂展 0.86 m、工位需要的最小臂展；
          (b) 手臂平面（r–z）：工具竖直朝下时 WQ-CR5 能到达的区域（式 (30.3.3)，两种手腕取并集），各点和上方 0.1 m 的接近点。
"""
import math

import numpy as np

from _ch30 import STATION, APPROACH, cr_dh, reach_margin, wqcr5
from bookout import COLORS as C, T, figure, style

plt = style()
W = wqcr5()
dh = cr_dh()
R = W.summary()["reach_mm"] / 1000
R_need = 0.759                                                 # 算例 30.1.2

fig, axs = plt.subplots(1, 2, figsize=(11.8, 4.6), gridspec_kw={"width_ratios": [1, 1.25]})
ax = axs[0]
th = np.linspace(0, 2 * math.pi, 361)
ax.fill(R * np.cos(th), R * np.sin(th), color=C["z"], alpha=0.07)
ax.plot(R * np.cos(th), R * np.sin(th), color=C["z"], lw=1.2, label=T("WQ-CR5 臂展 0.86 m", "WQ-CR5 reach 0.86 m"))
ax.plot(R_need * np.cos(th), R_need * np.sin(th), color=C["muted"], lw=1, ls="--", label=T("工位需要的最小臂展", "least reach the station needs"))
ax.add_patch(plt.Rectangle((-0.9, -0.45), 1.8, 0.9, fill=False, ec=C["ink"], lw=0.8))
ax.text(-0.88, 0.38, T("工作台", "bench"), fontsize=8, color=C["muted"])
ax.add_patch(plt.Circle((0, 0), 0.075, color=C["ink"]))
for zh, en, phi, r, z in STATION:
    x, y = r * math.cos(math.radians(phi)), r * math.sin(math.radians(phi))
    ax.plot(x, y, "o", color=C["x"] if z < 0 else C["y"], ms=7)
    ax.annotate(T(zh, en), (x, y), xytext=(6, 4), textcoords="offset points", fontsize=8)
ax.set_aspect("equal")
ax.set_xlim(-1.0, 1.0)
ax.set_ylim(-1.0, 1.0)
ax.set_xlabel("x / m")
ax.set_ylabel("y / m")
ax.legend(fontsize=8, frameon=False, loc="lower left")
ax.set_title(T("(a) 俯视：六个取放点", "(a) top view: six pick and place points"), fontsize=11)

ax = axs[1]
rs = np.linspace(0.0, 1.0, 251)
zs = np.linspace(-0.7, 0.9, 321)
Z = np.array([[reach_margin(r, z, dh) > 0 for r in rs] for z in zs], float)
ax.contourf(rs, zs, Z, levels=[0.5, 1.5], colors=[C["z"]], alpha=0.18)
ax.contour(rs, zs, Z, levels=[0.5], colors=[C["z"]], linewidths=1)
ax.axhline(0, color=C["ink"], lw=0.8)
ax.axvline(dh[3]["d"], color=C["accent"], lw=1, ls=":")
ax.text(dh[3]["d"] + 0.01, 0.8, T("r = d4：工具朝下时\n离 J1 轴更近就够不着", "r = d4: closer to J1's axis\nis out of reach with the tool down"),
        fontsize=8, color=C["accent"], va="top")
for zh, en, phi, r, z in STATION:
    ax.plot([r, r], [z, z + APPROACH], color=C["muted"], lw=0.8)
    ax.plot(r, z, "o", color=C["x"] if z < 0 else C["y"], ms=6)
    ax.plot(r, z + APPROACH, "^", color=C["muted"], ms=4)
ax.text(0.6, -0.55, T("台面以下", "below the bench"), fontsize=8, color=C["muted"])
ax.set_xlabel(T("离 J1 轴的距离 r / m", "distance from J1's axis r / m"))
ax.set_ylabel(T("TCP 高度 z / m（台面 = 0）", "TCP height z / m (bench = 0)"))
ax.set_xlim(0, 1.0)
ax.set_ylim(-0.7, 0.9)
ax.set_aspect("equal")
ax.set_title(T("(b) 工具朝下时能到达的区域", "(b) region reachable with the tool pointing down"), fontsize=11)
fig.tight_layout()
figure(fig, "fig30_1_1")
