"""17.4 节的示意图。

图 17.4.1：协作工位（算例 17.4.1）。Panda 的手从 A 沿直线搬到 B，工人的手（球）从左后方伸进来。
           (a) 做法 S1（离 ready 最近的起始形态、最小范数解）：起点与终点的形态、肘点的路径；(b) 做法 S3（沿自运动闭曲线挑选起始形态，
           再加局部的优先级控制）。
图 17.4.2：(a) 全局挑选：A 的自运动闭曲线上限位以内的各起始形态（横轴为其 θ3），用最小范数解走完全程时离工人的手的最小距离、
           最小可操作度，满足全部要求的用阴影标出；(b) 四种做法离工人的手的距离随时间的变化。
数据与 ex17_4.py 相同（重算一遍）。
"""
import math

import numpy as np

from _fig17 import C, GOLD2, axes3d, draw_chain, equal3d, floor3d, rerun, sphere3d, spines
from _red import pa_fk, pa_points
from bookout import T, figure, style

plt = style()
E = rerun("ex17_4.py")
R0, R1, R2, R3 = E["R0"], E["R1"], E["R2"], E["R3"]
A_, B_, C0, C1, RAD = E["A_"], E["B_"], E["C0"], E["C1"], E["RAD"]

# ---------------------------------------------------------------- 图 17.4.1
fig = plt.figure(figsize=(12.4, 5.2))
for pos, R, col, title in ((121, R1, C["x"], T("(a) S1：离 ready 最近的起始形态，最小范数解", "(a) S1: start nearest to ready, minimum-norm solution")),
                           (122, R3, C["z"], T("(b) S3：沿自运动闭曲线挑选起始形态，再加优先级控制", "(b) S3: start chosen on the self-motion curve, plus priority control"))):
    ax = axes3d(plt, fig, pos=pos, elev=22, azim=-145)
    floor3d(ax, (-0.55, 0.55), (-0.55, 0.55))
    ax.plot([0, 0], [0, 0], [0, 0.333], color="#9aa6ad", lw=7, solid_capstyle="butt")
    q_start, q_end = R[0, 6:13], R[-1, 6:13]
    draw_chain(ax, pa_points(q_end)[1:], "#9aa6ad", lw=3.5, alpha=0.8, js=8)
    draw_chain(ax, pa_points(q_start)[1:], col, lw=4.5, js=10)
    EL = np.array([pa_points(r[6:13])[3] for r in R[::10]])
    ax.plot(*EL.T, color=C["accent"], lw=2.0)
    ax.plot(*np.array([A_, B_]).T, color=C["ink"], lw=1.5, ls="--")
    ax.text(*(A_ + np.array([0.0, 0.05, -0.08])), "A", fontsize=11, weight="bold")
    ax.text(*(B_ + np.array([0.0, -0.05, -0.08])), "B", fontsize=11, weight="bold")
    hp = np.array([C0 + s * (C1 - C0) for s in np.linspace(0, 1, 20)])
    ax.plot(*hp.T, color=C["x"], lw=1.0, ls=":")
    sphere3d(ax, C1, RAD, C["x"], alpha=0.35)
    ax.text(*(C0 + np.array([0.0, 0.05, 0.05])), T("工人的手", "worker's hand"), fontsize=9, color=C["x"])
    k = int(np.argmin(R[:, 1]))
    ax.text2D(0.02, 0.04, T(f"最小距离 {R[:, 1].min() * 100:.1f} cm", f"min. distance {R[:, 1].min() * 100:.1f} cm"),
              transform=ax.transAxes, fontsize=9.5, color=col)
    equal3d(ax, np.vstack([np.array([[-0.5, -0.45, 0], [0.5, 0.45, 0.75]]), EL]), pad=0.0, zoom=1.2)
    ax.set_title(title, fontsize=10, loc="left")
fig.text(0.5, 0.02, T("彩色：起点形态；灰色：终点形态；金线：肘点的路径；虚线：手的直线路径；红点线：工人的手伸进来的路线",
                      "colour: start; grey: end; gold: path of the elbow; dashed: straight path of the hand; red dotted: how the worker's hand comes in"),
         ha="center", fontsize=8.8, color=C["muted"])
figure(fig, "fig17_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 17.4.2
cand = E["cand"]
ok = E["ok"]
fig, axs = plt.subplots(1, 2, figsize=(11.8, 4.2))
ax = axs[0]
o = np.argsort(cand[:, 5])
x = cand[o, 5]
ax.plot(x, cand[o, 1] * 100, "o-", color=C["x"], ms=3.5, lw=1.4, label=T("最小距离 / cm", "min. distance / cm"))
ax.axhline(E["D_SAFE"] * 100, color=C["x"], lw=0.8, ls=":")
ax.text(-12, E["D_SAFE"] * 100 + 0.6, T("要求 ≥ 10 cm", "required ≥ 10 cm"), fontsize=8.5, color=C["x"])
for xi, good in zip(x, ok[o]):
    if good:
        ax.axvspan(xi - 1.5, xi + 1.5, color="#e3f1e3", zorder=0)
ax.set_xlabel(T("起始形态的 θ₃ / (°)", "θ₃ of the start configuration / (°)"))
ax.set_ylabel(T("最小距离 / cm", "min. distance / cm"), color=C["x"])
ax.set_ylim(-8, 30)
spines(ax)
ax2 = ax.twinx()
ax2.plot(x, cand[o, 3], "s-", color=C["z"], ms=3, lw=1.2)
ax2.set_ylabel(T("最小可操作度 w（方块）", "min. manipulability w (squares)"), color=C["z"])
ax2.set_ylim(0, 0.09)
ax.axvline(math.degrees(E["q3"][2]), color=C["ink"], lw=1.0, ls="--")
ax.text(math.degrees(E["q3"][2]) + 3, 27, T("S3 选用", "chosen for S3"), fontsize=8.5)
ax.axvline(math.degrees(E["qA"][2]), color=C["muted"], lw=1.0, ls="--")
ax.text(math.degrees(E["qA"][2]) - 3, 27, T("S1、S2 的起点", "start of S1, S2"), fontsize=8.5, ha="right", color=C["muted"])
ax.set_title(T("(a) 沿自运动闭曲线挑选起始形态（绿色：满足挑选门槛）", "(a) Choosing the start on the self-motion curve (green: passes the selection thresholds)"), fontsize=9.8, loc="left")
ax = axs[1]
for R, col, ls, lab in ((R0, "#7f7f7f", "-.", T("S0：锁住关节 3（六轴）", "S0: joint 3 locked (six axes)")),
                        (R1, C["x"], "-", T("S1：最小范数解", "S1: minimum norm")),
                        (R2, GOLD2, "-", T("S2：局部优先级控制", "S2: local priority control")),
                        (R3, C["z"], "-", T("S3：全局挑选 + 局部", "S3: global choice + local"))):
    ax.plot(R[:, 0], R[:, 1] * 100, color=col, lw=2, ls=ls, label=lab)
ax.axhline(E["D_SAFE"] * 100, color=C["muted"], lw=0.9, ls=":")
ax.text(0.03, E["D_SAFE"] * 100 + 0.5, T("要求 ≥ 10 cm", "required ≥ 10 cm"), fontsize=8.5, color=C["muted"])
ax.set_xlabel(T("时间 t / s", "time t / s"))
ax.set_ylabel(T("手臂到工人的手的距离 / cm", "distance from the arm to the worker's hand / cm"))
spines(ax)
ax.legend(fontsize=8.5, frameon=False, loc="upper right")
ax.set_title(T("(b) 四种做法", "(b) The four approaches"), fontsize=10, loc="left")
fig.tight_layout()
figure(fig, "fig17_4_2")
plt.close(fig)
