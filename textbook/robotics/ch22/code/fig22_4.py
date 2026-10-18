"""22.4 节的示意图。

图 22.4.1：送料的直线（算例 22.4.1）。(a) TCP 偏离直线的距离：关节空间五次多项式与笛卡尔直线；
          (b) 笛卡尔直线下六个关节的速度：TCP 的速度是梯形，关节速度却不是。
图 22.4.2：过三点的圆弧（算例 22.4.2）。(a) 由三点求圆心：两条弦的中垂线交于圆心；(b) 沿弧的速率与总加速度：
          梯形（加速度在加速结束时跳变）与 S 形时间标度。
图 22.4.3：经过手腕奇异附近的直线（算例 22.4.4）。(a) 关节 5 的转角；(b) 由关节速度上限得到的每一点允许的最大直线速度
          （对数坐标）与匀速 0.1 m/s：中间约一成的路段必须减速。
"""
import math

import numpy as np

from _fig22 import C, COL3, COL5, LIM, curves
from _traj import scurve_eval, trap_eval
from bookout import T, figure, style
import ex22_4 as E

plt = style()
deg = np.degrees

# ---------------------------------------------------------------- 图 22.4.1
fig, axs = plt.subplots(1, 2, figsize=(12.6, 3.9))
ax = axs[0]
curves(ax, T("时间 $t$ / s", "time $t$ / s"), T("TCP 偏离直线 / mm", "TCP off the line / mm"))
ax.plot(E.t, np.array(E.dev) * 1000, color=COL5, lw=1.8, label=T("关节空间五次多项式", "joint-space quintic"))
ax.plot(E.t, np.zeros_like(E.t), color=COL3, lw=2.0, label=T("笛卡尔直线（逐点求逆解）", "Cartesian line (IK at every point)"))
ax.legend(loc="upper right", fontsize=9, frameon=False)
ax.set_ylim(-0.3, 4.2)
ax.set_title(T("(a) 送入卡盘的 0.12 m：TCP 是否走直线", "(a) the 0.12 m into the chuck: does the TCP go straight"), fontsize=10.5)
ax = axs[1]
curves(ax, T("时间 $t$ / s", "time $t$ / s"), T("关节速度 / (°/s)", "joint velocity / (°/s)"))
cols = [C["x"], C["y"], C["z"], "#8e6bbf", "#e8913a", "#5d6b73"]
for i in range(6):
    ax.plot(E.t, deg(E.dth_J[:, i]), color=cols[i], lw=1.6, label=rf"$\dot\theta_{i + 1}$")
ax2 = ax.twinx()
ax2.plot(E.t, E.ld * 1000, color=C["ink"], lw=1.0, ls="--")
ax2.set_ylabel(T("TCP 速率 / (mm/s)（虚线）", "TCP speed / (mm/s) (dashed)"))
ax2.spines["top"].set_visible(False)
ax2.set_ylim(0, 160)
ax.legend(loc="upper left", fontsize=8.5, frameon=False, ncol=3)
ax.set_ylim(-25, 30)
ax.set_title(T("(b) 笛卡尔直线下各关节的速度", "(b) joint velocities on the Cartesian line"), fontsize=10.5)
fig.tight_layout()
figure(fig, "fig22_4_1")

# ---------------------------------------------------------------- 图 22.4.2
fig, axs = plt.subplots(1, 2, figsize=(12.6, 4.4), gridspec_kw=dict(width_ratios=[1, 1.35]))
ax = axs[0]
ax.set_aspect("equal")
ax.axis("off")
P2 = [(p - E.c)[:2] for p in E.pts]
th = np.linspace(0, 2 * math.pi, 300)
ax.plot(E.rho * np.cos(th), E.rho * np.sin(th), color=LIM, lw=0.8, ls=":")
tha = np.linspace(0, E.ph3, 200)                 # E.ph3 是弧度（ex22_4 只在输出时换成度）
ax.plot(E.rho * np.cos(tha), E.rho * np.sin(tha), color=COL3, lw=2.4)
for a_, b_ in ((P2[0], P2[1]), (P2[1], P2[2])):
    ax.plot([a_[0], b_[0]], [a_[1], b_[1]], color=C["muted"], lw=1.0)
    m = (a_ + b_) / 2
    n = m / np.linalg.norm(m)                    # 弦的中垂线经过弦的中点和圆心，方向就是中点相对圆心的方向
    ax.plot([m[0] + 0.04 * n[0], -0.03 * n[0]], [m[1] + 0.04 * n[1], -0.03 * n[1]], color=C["accent"], lw=1.0, ls="--")
for k2, p in enumerate(P2):
    ax.plot(*p, "o", color=C["ink"], ms=6, zorder=5)
    ax.annotate(f"$p_{k2 + 1}$", p, textcoords="offset points", xytext=(8, 4) if k2 != 2 else (-22, 4), fontsize=12)
ax.plot(0, 0, "o", color=C["x"], ms=6)
ax.annotate(T("圆心 $c$", "centre $c$"), (0, 0), textcoords="offset points", xytext=(6, -14), fontsize=11, color=C["x"])
ax.annotate("", xy=(E.rho * math.cos(math.radians(250)), E.rho * math.sin(math.radians(250))), xytext=(0, 0),
            arrowprops=dict(arrowstyle="-|>", color=C["muted"], lw=1))
ax.text(-0.045, -0.055, r"$\rho$", fontsize=12, color=C["muted"])
ax.set_xlim(-0.13, 0.13)
ax.set_ylim(-0.12, 0.125)
ax.set_title(T("(a) 两条弦的中垂线交于圆心", "(a) perpendicular bisectors of two chords meet at the centre"), fontsize=10.5)
ax = axs[1]
curves(ax, T("时间 $t$ / s", "time $t$ / s"))
ax.plot(E.tt_t, E.v_t, color="#2ca02c", lw=1.2, ls="--", label=T("梯形：速率 / (m/s)", "trapezoid: speed / (m/s)"))
ax.plot(E.tt_t, E.A_t, color="#2ca02c", lw=1.8, label=T("梯形：总加速度 / (m/s²)", "trapezoid: total acceleration / (m/s²)"))
ax.plot(E.tt_s, E.v_s, color="#8e6bbf", lw=1.2, ls="--", label=T("S 形：速率 / (m/s)", "S-curve: speed / (m/s)"))
ax.plot(E.tt_s, E.A_s, color="#8e6bbf", lw=1.8, label=T("S 形：总加速度 / (m/s²)", "S-curve: total acceleration / (m/s²)"))
ax.legend(loc="upper right", fontsize=8.5, frameon=False)
ax.set_ylim(0, 1.15)
ax.set_title(T("(b) 沿圆弧的速率与总加速度", "(b) speed and total acceleration along the arc"), fontsize=10.5)
fig.tight_layout()
figure(fig, "fig22_4_2")

# ---------------------------------------------------------------- 图 22.4.3
fig, axs = plt.subplots(1, 2, figsize=(12.6, 3.9))
ax = axs[0]
curves(ax, T("沿直线的距离 $\\ell$ / m", "distance along the line $\\ell$ / m"), T("关节 5 的转角 / (°)", "joint 5 angle / (°)"))
ax.plot(E.ells, deg(E.THL[:, 4]), color=C["z"], lw=1.8)
ax.axhline(0, color=LIM, lw=0.8, ls=":")
ax.set_title(T("(a) 手腕在中点附近接近奇异（θ₅ 最小 1°）", "(a) the wrist nearly singular at the middle (θ₅ down to 1°)"), fontsize=10.5)
ax = axs[1]
curves(ax, T("沿直线的距离 $\\ell$ / m", "distance along the line $\\ell$ / m"), T("允许的直线速度 / (m/s)", "admissible line speed / (m/s)"))
ax.set_yscale("log")
ax.plot(E.ells, E.v_allow, color=COL3, lw=1.8, label=T("$\\min_i v_{i,\\max}/|\\theta_i'(\\ell)|$", "$\\min_i v_{i,\\max}/|\\theta_i'(\\ell)|$"))
ax.axhline(0.1, color=COL5, lw=1.4, ls="--", label=T("匀速 0.1 m/s", "constant 0.1 m/s"))
ax.fill_between(E.ells, 1e-3, 10, where=E.v_allow < 0.1, color=COL5, alpha=0.12, lw=0)
ax.set_ylim(0.01, 10)
ax.legend(loc="upper right", fontsize=9, frameon=False)
ax.set_title(T("(b) 关节限速换算到直线上的速度上限", "(b) joint speed limits mapped to a line-speed limit"), fontsize=10.5)
fig.tight_layout()
figure(fig, "fig22_4_3")
