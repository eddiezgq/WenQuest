"""22.6 节的示意图。

图 22.6.1：相平面（算例 22.6.2）。横轴为路径参数 σ（关节空间中的弧长），纵轴为 σ̇。灰色：关节速度限值给出的上限；
          橙色虚线：加速度限值给出的上限（两者合起来是速度上限曲线）；红色：可控集的上界（从终点往回算，刹得住的最大速度）；
          蓝色：时间最优的 σ̇(σ)。竖线为路径点 A、M。
图 22.6.2：(a) 时间最优轨迹上，各关节速度、加速度占限值的比例（各取最大的关节）：几乎每一时刻都有一个约束达到限值；
          (b) 关节 1 的加速度：样条整体缩放、时间最优（bang-bang）、时间最优加盒形窗滤波（t_j = 1/f_n）。
图 22.6.3：经过手腕奇异附近的直线（算例 22.6.4）：时间最优的直线速度 ℓ̇(ℓ)，与 TCP 速度上限、只考虑关节速度的上限比较。
"""
import math

import numpy as np

from _fig22 import C, COL3, COL5, LIM, curves
from _traj import AMAX, VMAX, segs_eval
from bookout import T, figure, style
import ex22_6 as E

plt = style()
deg = np.degrees

# ---------------------------------------------------------------- 图 22.6.1
fig, ax = plt.subplots(figsize=(10.4, 4.6))
curves(ax, T("路径参数 $\\sigma$（关节空间中的弧长）/ rad", "path parameter $\\sigma$ (arc length in joint space) / rad"),
       T("$\\dot\\sigma$ / (rad/s)", "$\\dot\\sigma$ / (rad/s)"))
sv = np.min(VMAX[None, :] / np.maximum(np.abs(E.D2), 1e-12), axis=1)
ax.plot(E.s2, sv, color=LIM, lw=1.4, label=T("关节速度限值：$\\min_i v_i/|\\theta_i'(\\sigma)|$", "joint speed limits: $\\min_i v_i/|\\theta_i'(\\sigma)|$"))
ax.plot(E.s2, np.sqrt(np.minimum(E.MVC2, 1e6)), color=COL5, lw=1.2, ls="--", label=T("速度上限曲线（速度、加速度限值都可满足）", "maximum velocity curve (speed and acceleration feasible)"))
ax.plot(E.s2, np.sqrt(np.maximum(E.K2, 0)), color=C["x"], lw=1.4, label=T("可控集的上界（刹得住）", "upper bound of the controllable set (can still stop)"))
ax.plot(E.s2, np.sqrt(np.maximum(E.x2, 0)), color=COL3, lw=2.4, label=T("时间最优", "time-optimal"))
for k, nm in ((1, "A"), (2, "M")):
    sk = float(np.interp(E.E3.ts[k], E.ug2, E.s2))
    ax.axvline(sk, color=LIM, lw=0.8, ls=":")
    ax.text(sk + 0.02, 0.93 * 1.25 * float(np.sqrt(E.x2.max())), nm, fontsize=11)
ytop = 1.25 * float(np.sqrt(E.x2.max()))
ax.set_ylim(0, ytop)
ax.set_xlim(0, E.L_sig)
ax.legend(loc="lower center", fontsize=8.8, frameon=False)
fig.tight_layout()
figure(fig, "fig22_6_1")

# ---------------------------------------------------------------- 图 22.6.2
fig, axs = plt.subplots(1, 2, figsize=(13.0, 4.0))
ax = axs[0]
curves(ax, T("时间 $t$ / s", "time $t$ / s"), T("占限值的比例", "fraction of the limit"))
tm = 0.5 * (E.t2[:-1] + E.t2[1:])
ax.plot(tm, E.act_a, color=C["x"], lw=2.0, label=T("加速度（最大的关节）", "acceleration (largest joint)"))
ax.plot(E.t2, E.act_v, color=COL3, lw=1.4, label=T("速度（最大的关节）", "velocity (largest joint)"))
ax.axhline(1.0, color=LIM, lw=0.9, ls="--")
ax.set_ylim(0, 1.12)
ax.legend(loc="lower center", fontsize=9, frameon=False)
ax.set_title(T("(a) 时间最优：每一时刻都有一个约束达到限值", "(a) time-optimal: some constraint is at its limit at every instant"), fontsize=10.5)
ax = axs[1]
curves(ax, T("时间 $t$ / s", "time $t$ / s"), T("关节 1 的加速度 / (rad/s²)", "joint 1 acceleration / (rad/s²)"))
ts = np.arange(0, E.U, 1e-3)
ax.plot(ts, segs_eval(E.S, ts, 2)[:, 0], color=C["muted"], lw=1.4, label=T("样条整体缩放", "scaled spline") + f"  {E.U:.3f} s")
ax.step(E.t2[:-1], E.acc2[:, 0], where="post", color=COL3, lw=1.6, label=T("时间最优", "time-optimal") + f"  {E.T_opt:.3f} s")
ax.plot(E.tfE, E.aE[:, 0], color=COL5, lw=1.6, label=T("时间最优 + 滤波", "time-optimal + filter") + f"  {E.T_fir:.3f} s")
for v in (AMAX[0], -AMAX[0]):
    ax.axhline(v, color=LIM, lw=0.9, ls="--")
ax.set_ylim(-7.5, 8.5)
ax.legend(loc="upper right", fontsize=8.5, frameon=False, ncol=1)
ax.set_title(T("(b) 关节 1 的加速度：bang-bang 与滤波后", "(b) joint 1 acceleration: bang-bang and filtered"), fontsize=10.5)
fig.tight_layout()
figure(fig, "fig22_6_2")

# ---------------------------------------------------------------- 图 22.6.3
fig, ax = plt.subplots(figsize=(9.6, 4.0))
curves(ax, T("沿直线的距离 $\\ell$ / m", "distance along the line $\\ell$ / m"), T("直线速度 $\\dot\\ell$ / (m/s)", "line speed $\\dot\\ell$ / (m/s)"))
vj = np.min(VMAX[None, :] / np.maximum(np.abs(E.DL), 1e-12), axis=1)
ax.plot(E.ells, np.minimum(vj, 0.3), color=LIM, lw=1.3, label=T("关节速度限值换算的上限（式 (22.4.9)）", "limit from joint speeds (Eq. (22.4.9))"))
ax.axhline(0.25, color=COL5, lw=1.2, ls="--", label=T("TCP 速度上限 0.25 m/s", "TCP speed limit 0.25 m/s"))
ax.plot(E.ells, np.sqrt(E.x4), color=COL3, lw=2.2, label=T("时间最优", "time-optimal") + f"  {E.T_sing:.3f} s")
ax.set_ylim(0, 0.3)
ax.legend(loc="lower left", fontsize=9, frameon=False, ncol=1, bbox_to_anchor=(0.11, 0.03))
fig.tight_layout()
figure(fig, "fig22_6_3")
