"""22.1 节的示意图。

图 22.1.1：归一化的时间标度：直线 s = τ、三次、五次多项式的位置、速度、加速度、加加速度（对 τ 的导数）。
          直线插值在两端速度跳变、加速度为冲激；三次在两端加速度跳变、加加速度为冲激；五次的各阶导数都有界。
图 22.1.2：算例 22.1.1：UR5e 从 A 到 B 的同步点到点运动。(a) 五次多项式下六个关节角随时间的变化；
          (b)(c) 关节 1 的速度与加速度：三次、五次（各取最短时间）与直线插值，虚线为限值。
图 22.1.3：算例 22.1.2：关节空间的直线在笛卡尔空间是一条曲线：UR5e 在 A（浅）与 B 的形态、TCP 走过的路径（实线）
          与 A、B 的连线（虚线），旁边是料架与车床卡盘（示意）。
"""
import math

import numpy as np

from _fig22 import C, COL3, COL5, COLL, LIM, axes3d, base_frame, curves, draw_chain, draw_tool, equal3d, floor3d, ur_chain, workcell
from _traj import AMAX, VMAX, cell_joints, s_cubic, s_quintic, tcp_fk
from bookout import T, figure, style
import ex22_1 as E

plt = style()
deg = np.degrees

# ---------------------------------------------------------------- 图 22.1.1
tau = np.linspace(0, 1, 801)
fig, axs = plt.subplots(1, 4, figsize=(13.0, 3.3))
names = [T("位置 $s$", "position $s$"), T("速度 $\\mathrm{d}s/\\mathrm{d}\\tau$", "velocity $\\mathrm{d}s/\\mathrm{d}\\tau$"),
         T("加速度 $\\mathrm{d}^2s/\\mathrm{d}\\tau^2$", "acceleration $\\mathrm{d}^2s/\\mathrm{d}\\tau^2$"),
         T("加加速度 $\\mathrm{d}^3s/\\mathrm{d}\\tau^3$", "jerk $\\mathrm{d}^3s/\\mathrm{d}\\tau^3$")]
for r, ax in enumerate(axs):
    curves(ax, r"$\tau = t/T$")
    ax.set_title(names[r], fontsize=11)
    lin = [tau, np.ones_like(tau), np.zeros_like(tau), np.zeros_like(tau)][r]
    if r <= 1:
        ax.plot(tau, lin, color=COLL, lw=1.4, ls="--", label=T("直线 $s=\\tau$", "linear $s=\\tau$"))
    ax.plot(tau, s_cubic(tau, r), color=COL3, lw=1.8, label=T("三次", "cubic"))
    ax.plot(tau, s_quintic(tau, r), color=COL5, lw=1.8, label=T("五次", "quintic"))
    ax.set_xlim(-0.05, 1.05)
# 速度：直线插值在两端从 0 跳到 1
axs[1].plot([0, 0], [0, 1], color=COLL, lw=1.4, ls="--")
axs[1].plot([1, 1], [0, 1], color=COLL, lw=1.4, ls="--")
axs[1].set_ylim(-0.1, 2.15)
axs[1].text(0.5, 1.6, "1.5", color=COL3, ha="center", fontsize=9)
axs[1].text(0.5, 1.95, "1.875", color=COL5, ha="center", fontsize=9)
axs[0].legend(loc="upper left", fontsize=9, frameon=False)
# 加速度：三次两端跳变（竖线），直线两端为冲激（箭头，标 ∞）
for x0 in (0, 1):
    axs[2].plot([x0, x0], [0, s_cubic(x0, 2)], color=COL3, lw=1.2, ls=":")
axs[2].annotate("", xy=(0.0, 9.2), xytext=(0.0, 0), arrowprops=dict(arrowstyle="-|>", color=COLL, lw=1.4, ls="--"))
axs[2].annotate("", xy=(1.0, -9.2), xytext=(1.0, 0), arrowprops=dict(arrowstyle="-|>", color=COLL, lw=1.4, ls="--"))
axs[2].text(0.05, 8.4, r"$+\infty$" + T("（直线）", " (linear)"), color=COLL, fontsize=9)
axs[2].text(0.5, -9.4, r"$-\infty$" + T("（直线）", " (linear)"), color=COLL, fontsize=9, ha="center")
axs[2].set_ylim(-10.5, 10.5)
# 加加速度：三次两端为冲激
axs[3].annotate("", xy=(0.0, 75), xytext=(0.0, 0), arrowprops=dict(arrowstyle="-|>", color=COL3, lw=1.4))
axs[3].annotate("", xy=(1.0, 75), xytext=(1.0, 0), arrowprops=dict(arrowstyle="-|>", color=COL3, lw=1.4))
axs[3].text(0.06, 68, r"$\infty$" + T("（三次）", " (cubic)"), color=COL3, fontsize=9)
axs[3].set_ylim(-45, 82)
fig.tight_layout()
figure(fig, "fig22_1_1")

# ---------------------------------------------------------------- 图 22.1.2
thR, thA, thB, thC = cell_joints()
dq = thB - thA
T3, T5 = E.T3, E.T5
fig, axs = plt.subplots(1, 3, figsize=(13.0, 3.6))
t5 = np.linspace(0, T5, 400)
cols = [C["x"], C["y"], C["z"], "#8e6bbf", "#e8913a", "#5d6b73"]
ax = axs[0]
curves(ax, T("时间 $t$ / s", "time $t$ / s"), T("关节角 / (°)", "joint angle / (°)"))
for i in range(6):
    q = deg(thA[i] + dq[i] * s_quintic(t5 / T5))
    ax.plot(t5, q, color=cols[i], lw=1.6)
    ax.text(T5 + 0.03, q[-1], rf"$\theta_{i + 1}$", color=cols[i], fontsize=10, va="center")
ax.set_xlim(0, T5 + 0.22)
ax.set_title(T("(a) 五次多项式：六个关节同时起止", "(a) quintic: all six joints start and stop together"), fontsize=10.5)
for k, (ax, r, lim, unit) in enumerate(((axs[1], 1, VMAX[0], T("关节 1 的速度 / (rad/s)", "joint 1 velocity / (rad/s)")),
                                        (axs[2], 2, AMAX[0], T("关节 1 的加速度 / (rad/s²)", "joint 1 acceleration / (rad/s²)")))):
    curves(ax, T("时间 $t$ / s", "time $t$ / s"), unit)
    t3 = np.linspace(0, T3, 400)
    ax.plot(t3, dq[0] * s_cubic(t3 / T3, r) / T3 ** r, color=COL3, lw=1.8, label=T("三次", "cubic") + f"  T = {T3:.3f} s")
    ax.plot(t5, dq[0] * s_quintic(t5 / T5, r) / T5 ** r, color=COL5, lw=1.8, label=T("五次", "quintic") + f"  T = {T5:.3f} s")
    for sgn in ((1,) if r == 1 else (1, -1)):
        ax.axhline(sgn * lim, color=LIM, lw=1.0, ls="--")
    if r == 1:
        vl = dq[0] / T3
        ax.plot([0, 0, T3, T3], [0, vl, vl, 0], color=COLL, lw=1.3, ls="--", label=T("直线插值", "linear"))
        ax.text(0.02, lim + 0.08, T("限值 180°/s", "limit 180°/s"), color=LIM, fontsize=9)
        ax.set_ylim(-0.1, 4.6)
        ax.legend(loc="upper right", fontsize=8.5, frameon=False, ncol=1)
        ax.set_title(T("(b) 关节 1 的速度", "(b) joint 1 velocity"), fontsize=10.5)
    else:
        ax.text(0.02, lim + 0.4, T("限值 ±6 rad/s²", "limit ±6 rad/s²"), color=LIM, fontsize=9)
        ax.set_ylim(-8, 8.2)
        ax.set_title(T("(c) 关节 1 的加速度", "(c) joint 1 acceleration"), fontsize=10.5)
fig.tight_layout()
figure(fig, "fig22_1_2")

# ---------------------------------------------------------------- 图 22.1.3
fig, ax = axes3d(plt, size=(7.2, 5.6), elev=24, azim=-38)
floor3d(ax, 0.75, z=-0.25)
workcell(ax)
base_frame(ax)
PA, PB = ur_chain(thA), ur_chain(thB)
draw_chain(ax, PA, C["muted"], lw=4, alpha=0.45)
draw_tool(ax, thA, C["muted"], alpha=0.45)
draw_chain(ax, PB, C["z"], lw=4)
draw_tool(ax, thB, C["z"])
ss = np.linspace(0, 1, 200)
P = np.array([tcp_fk(thA + s * dq)[:3, 3] for s in ss])
ax.plot(*P.T, color=C["x"], lw=2.2)
ax.plot(*np.array([P[0], P[-1]]).T, color=C["ink"], lw=1.2, ls="--")
k = int(np.argmax(E.dev[::10][:200])) if False else 92
for X, s, off in ((P[0], "A", (0.03, -0.05, 0.03)), (P[-1], "B", (0.03, 0.03, 0.04))):
    ax.scatter(*X, color=C["ink"], s=14, depthshade=False)
    ax.text(*(X + np.array(off)), s, fontsize=12, color=C["ink"])
ax.text(*(P[k] + np.array([0.10, 0.02, -0.12])), T("TCP 的路径", "TCP path"), color=C["x"], fontsize=10)
ax.text2D(0.03, 0.93, T(f"弦长 {E.chord:.3f} m，路径长 {E.L_tcp:.3f} m，最大偏离 {E.dev.max() * 1000:.0f} mm",
                        f"chord {E.chord:.3f} m, path length {E.L_tcp:.3f} m, max. deviation {E.dev.max() * 1000:.0f} mm"),
          transform=ax.transAxes, fontsize=10, color=C["ink"])
from _traj import P_CHUCK, P_PICK
ax.text(*(P_CHUCK + np.array([-0.25, 0.12, 0.18])), T("车床卡盘", "lathe chuck"), fontsize=10, color="#5d6b73")
ax.text(*(P_PICK + np.array([-0.05, -0.22, -0.20])), T("料架", "rack"), fontsize=10, color="#8c6d1f")
pts = np.vstack([PA, PB, P, [[0.6, 0.5, -0.25], [-0.45, -0.6, -0.25]]])
equal3d(ax, pts, pad=0.02, zoom=1.25)
figure(fig, "fig22_1_3")
