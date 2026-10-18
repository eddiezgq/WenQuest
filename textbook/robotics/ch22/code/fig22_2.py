"""22.2 节的示意图。

图 22.2.1：梯形速度曲线（算例 22.2.1）。(a) 关节 1 的角度、速度、加速度：加速 t_a、匀速 t_c、减速 t_a；
          (b) 六个关节同步：同一加速时间与总时间，各自的速度；(c) 转角小时速度达不到上限，梯形变成三角形。
图 22.2.2：七段 S 形曲线（算例 22.2.2）：关节 1 的角度、速度、加速度、加加速度，灰色竖条为加加速度不为零的段；
          虚线为同一 v′、a 的梯形曲线：S 形曲线是它用宽 t_j 的盒形窗滑动平均的结果（定理 22.2.2）。
图 22.2.3：残余振动（算例 22.2.3）。(a) TCP 沿圆周方向的振动位移：梯形、三次、五次、S 形（t_j = 0.1 s 与 1/f_n）；
          (b) 运动结束时的振幅随 t_j 的变化（对数坐标）：实线为计入阻尼的精确响应，虚线为无阻尼时的
          “梯形振幅 × |sin(π f_n t_j)/(π f_n t_j)|”；t_j = 1/f_n、2/f_n 处振幅几乎为零。
"""
import math

import numpy as np

from _fig22 import C, COL3, COL5, LIM, curves
from _traj import (AMAX, FN_TOOL, VMAX, accel_breaks, cell_joints, fourier_pw, response_pw, scurve_eval, scurve_plan, sinc_factor,
                   trap_eval, trap_plan, trap_sync)
from bookout import T, figure, style
import ex22_2 as E

plt = style()
deg = np.degrees
thR, thA, thB, thC = cell_joints()
dq = thB - thA
COLT = "#2ca02c"     # 梯形
COLS = "#8e6bbf"     # S 形

# ---------------------------------------------------------------- 图 22.2.1
P1 = trap_plan(E.L1, VMAX[0], AMAX[0])
fig, axs = plt.subplots(1, 3, figsize=(13.0, 3.7))
t = np.linspace(0, P1["T"], 600)
q, v, a = trap_eval(P1, t)
ax = axs[0]
curves(ax, T("时间 $t$ / s", "time $t$ / s"))
ax.plot(t, v, color=COLT, lw=2.0, label=T("速度 / (rad/s)", "velocity / (rad/s)"))
ax.plot(t, a / 2, color=C["x"], lw=1.4, label=T("加速度 / 2 / (rad/s²)", "acceleration / 2 / (rad/s²)"))
ax.plot(t, q, color=C["ink"], lw=1.4, ls="--", label=T("角度 / rad", "angle / rad"))
ax.axhline(VMAX[0], color=LIM, lw=1.0, ls="--")
for x in (P1["ta"], P1["ta"] + P1["tc"]):
    ax.axvline(x, color=LIM, lw=0.8, ls=":")
ax.annotate("", xy=(P1["ta"], -3.6), xytext=(0, -3.6), arrowprops=dict(arrowstyle="<->", color=C["muted"], lw=1))
ax.text(P1["ta"] / 2, -3.45, "$t_a$", ha="center", fontsize=10)
ax.annotate("", xy=(P1["T"], -3.6), xytext=(P1["ta"] + P1["tc"], -3.6), arrowprops=dict(arrowstyle="<->", color=C["muted"], lw=1))
ax.text(P1["T"] - P1["ta"] / 2, -3.45, "$t_a$", ha="center", fontsize=10)
ax.text(P1["ta"] + P1["tc"] / 2, VMAX[0] + 0.22, "$t_c$", ha="center", fontsize=10)
ax.set_ylim(-4.0, 4.6)
ax.legend(loc="lower left", fontsize=8.5, frameon=False, ncol=1, bbox_to_anchor=(0.0, 0.12))
ax.set_title(T("(a) 关节 1：加速、匀速、减速", "(a) joint 1: accelerate, cruise, decelerate"), fontsize=10.5)
ax = axs[1]
curves(ax, T("时间 $t$ / s", "time $t$ / s"), T("关节速度 / (°/s)", "joint velocity / (°/s)"))
cols = [C["x"], C["y"], C["z"], "#8e6bbf", "#e8913a", "#5d6b73"]
for i in range(6):
    Pi = trap_sync(P1["T"], P1["ta"], abs(dq[i]))
    vi = trap_eval(Pi, t)[1] * np.sign(dq[i])
    ax.plot(t, deg(vi), color=cols[i], lw=1.6)
    ax.text(P1["T"] / 2, deg(vi[300]) + (6 if i != 2 else -14), rf"$\theta_{i + 1}$", color=cols[i], fontsize=10, ha="center")
ax.axhline(180, color=LIM, lw=1.0, ls="--")
ax.text(0.02, 184, T("限值 180°/s", "limit 180°/s"), color=LIM, fontsize=9)
ax.set_ylim(-80, 205)
ax.set_title(T("(b) 六个关节同步：同一 $t_a$、同一 $T$", "(b) six joints in step: same $t_a$, same $T$"), fontsize=10.5)
ax = axs[2]
curves(ax, T("时间 $t$ / s", "time $t$ / s"), T("关节 1 的速度 / (rad/s)", "joint 1 velocity / (rad/s)"))
for L, ls, name in ((E.L1, "-", T("转 {:.2f} rad：梯形", "turn {:.2f} rad: trapezoid")), (0.5, "--", T("转 {:.2f} rad：三角形", "turn {:.2f} rad: triangle"))):
    P = trap_plan(L, VMAX[0], AMAX[0])
    tt = np.linspace(0, P["T"], 300)
    ax.plot(tt, trap_eval(P, tt)[1], color=COLT, lw=1.8, ls=ls, label=name.format(L))
ax.axhline(VMAX[0], color=LIM, lw=1.0, ls="--")
ax.text(0.02, VMAX[0] + 0.08, "$v_{\\max}$", color=LIM, fontsize=10)
ax.set_ylim(0, 4.0)
ax.legend(loc="upper right", fontsize=8.5, frameon=False)
ax.set_title(T("(c) 达不到 $v_{\\max}$ 时是三角形", "(c) a triangle when $v_{\\max}$ is not reached"), fontsize=10.5)
fig.tight_layout()
figure(fig, "fig22_2_1")

# ---------------------------------------------------------------- 图 22.2.2
S1 = scurve_plan(E.L1, VMAX[0], AMAX[0], 60.0)
Pq = trap_plan(E.L1, S1["vp"], AMAX[0])
tt = np.linspace(0, S1["T"], 1201)
SX = scurve_eval(S1, tt)
TQ = trap_eval(Pq, tt)
fig, axs = plt.subplots(4, 1, figsize=(8.6, 8.0), sharex=True)
names = [T("角度 / rad", "angle / rad"), T("速度 / (rad/s)", "velocity / (rad/s)"), T("加速度 / (rad/s²)", "acceleration / (rad/s²)"),
         T("加加速度 / (rad/s³)", "jerk / (rad/s³)")]
bounds = np.cumsum([0, S1["tj"], S1["ta"], S1["tj"], S1["tv"], S1["tj"], S1["ta"], S1["tj"]])
for r, ax in enumerate(axs):
    curves(ax, None, names[r])
    for k in (0, 2, 4, 6):
        ax.axvspan(bounds[k], bounds[k + 1], color="#eceff1", lw=0)
    if r < 3:
        ax.plot(tt, TQ[r], color=COLT, lw=1.3, ls="--")
    ax.plot(tt, SX[r], color=COLS, lw=2.0)
axs[1].axhline(VMAX[0], color=LIM, lw=1.0, ls="--")
axs[1].text(0.01, VMAX[0] + 0.1, T("$v_{\\max}$ = π rad/s，未达到", "$v_{\\max}$ = π rad/s, not reached"), color=LIM, fontsize=9)
axs[1].set_ylim(0, 3.8)
axs[2].set_ylim(-7.5, 7.5)
axs[3].set_ylim(-75, 75)
for k, lab in enumerate(["1", "2", "3", "4", "5", "6", "7"]):
    axs[3].text((bounds[k] + bounds[k + 1]) / 2, 62, lab, ha="center", fontsize=10, color=C["muted"])
axs[3].set_xlabel(T("时间 $t$ / s", "time $t$ / s"))
axs[0].plot([], [], color=COLS, lw=2.0, label=T("S 形（$j_{\\max}$ = 60 rad/s³）", "S-curve ($j_{\\max}$ = 60 rad/s³)"))
axs[0].plot([], [], color=COLT, lw=1.3, ls="--", label=T("同一 $v'$、$a$ 的梯形", "trapezoid with the same $v'$, $a$"))
axs[0].legend(loc="lower right", fontsize=9, frameon=False)
axs[2].annotate("", xy=(bounds[1], 6.6), xytext=(bounds[0], 6.6), arrowprops=dict(arrowstyle="<->", color=C["muted"], lw=1))
axs[2].text((bounds[0] + bounds[1]) / 2, 5.6, "$t_j$", ha="center", fontsize=10)
fig.tight_layout()
figure(fig, "fig22_2_2")

# ---------------------------------------------------------------- 图 22.2.3
fig, axs = plt.subplots(1, 2, figsize=(13.0, 4.0))
ax = axs[0]
curves(ax, T("时间 $t$ / s", "time $t$ / s"), T("TCP 的振动位移 / mm", "TCP vibration / mm"))
for key, col, name, lw in (("trap", COLT, T("梯形", "trapezoid"), 1.4), ("cubic", COL3, T("三次", "cubic"), 1.2),
                           ("quintic", COL5, T("五次", "quintic"), 1.4), ("s10", COLS, T("S 形，$t_j$ = 0.1 s", "S-curve, $t_j$ = 0.1 s"), 1.6),
                           ("s125", C["ink"], T("S 形，$t_j$ = 1/$f_n$", "S-curve, $t_j$ = 1/$f_n$"), 1.8)):
    ts, xs = E.hist[key]
    ax.plot(ts, xs, color=col, lw=lw, label=name)
ax.set_xlim(0, 2.6)
ax.legend(loc="upper right", fontsize=8.5, frameon=False, ncol=2)
ax.set_ylim(-4.2, 5.5)
ax.set_title(T("(a) 运动中与运动结束后的振动（运动在 1.1～1.3 s 结束）", "(a) vibration during and after the move (it ends at 1.1–1.3 s)"), fontsize=10.5)
ax = axs[1]
curves(ax, T("$t_j$ / s", "$t_j$ / s"), T("振幅 / 梯形的振幅", "amplitude / trapezoid amplitude"))
ax.set_yscale("log")
ax.plot(E.tj_scan, E.amp_scan / E.amp_scan[0], color=COLS, lw=1.8, label=T("S 形的残余振幅（计入阻尼，精确计算）", "S-curve residual amplitude (damped, exact)"))
sc = np.array([max(sinc_factor(FN_TOOL, tj), 1e-5) for tj in E.tj_scan])
ax.plot(E.tj_scan, sc, color=C["ink"], lw=1.0, ls="--", label=T("盒形窗的增益 |sin(π$f_n t_j$)/(π$f_n t_j$)|", "box-filter gain |sin(π$f_n t_j$)/(π$f_n t_j$)|"))
for k in (1, 2):
    ax.axvline(k / FN_TOOL, color=LIM, lw=0.9, ls=":")
    ax.text(k / FN_TOOL, 1.6, f"{k}/$f_n$", color=C["muted"], fontsize=9, ha="center")
ax.set_ylim(1e-3, 3)
ax.legend(loc="upper right", bbox_to_anchor=(1.0, 0.86), fontsize=8.5, frameon=False)
ax.set_title(T("(b) 振幅随 $t_j$ 的变化：$t_j$ = $k/f_n$ 处出现深谷", "(b) amplitude against $t_j$: deep notches at $t_j$ = $k/f_n$"), fontsize=10.5)
fig.tight_layout()
figure(fig, "fig22_2_3")
