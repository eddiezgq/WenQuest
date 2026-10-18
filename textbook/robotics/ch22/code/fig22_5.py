"""22.5 节的示意图。

图 22.5.1：位姿插值的三种做法。(a)(b)(c) 平面上的刚体（示意）从位姿 A 移到位姿 B（转 120°）：
          以 P 为参考点的解耦插值（P 走直线）、以 Q 为参考点的解耦插值（Q 走直线）、旋量插值（整个物体绕极点 c 转动，
          平面上的旋量轴就是 6.1 节的极点）；(d) 算例 22.5.1：TCP 在三种插值下的路径（俯视），旋量插值的螺旋轴。
图 22.5.2：算例 22.5.2：经过三个姿态的物体角速度的大小：分段测地线在路径点和两端跳变；C¹ 姿态样条连续，两端为零。
"""
import math

import numpy as np

from _fig22 import C, COL3, COL5, LIM, curves
from _traj import expso3, logR, screw_interp, decoupled
from bookout import T, figure, style
import ex22_5 as E

plt = style()
deg = np.degrees


def se2(x, y, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, x], [s, c, y], [0, 0, 1.0]])


def to3(T2):
    T = np.eye(4)
    T[:2, :2] = T2[:2, :2]
    T[:2, 3] = T2[:2, 2]
    return T


SHAPE = np.array([[0, -0.25], [2.0, -0.25], [2.0, 0.25], [0.5, 0.25], [0.5, 0.9], [0, 0.9]])     # 物体坐标系中的轮廓
P_b, Q_b = np.array([0.0, 0.0]), np.array([1.9, 0.0])
TA2, TB2 = to3(se2(0.0, 0.0, 0.0)), to3(se2(3.2, 1.0, math.radians(120)))

fig = plt.figure(figsize=(13.2, 7.4))
gs = fig.add_gridspec(2, 3, height_ratios=[1, 1.1])
titles = [T("(a) 解耦插值，参考点 P：P 走直线", "(a) decoupled, reference P: P goes straight"),
          T("(b) 解耦插值，参考点 Q：Q 走直线", "(b) decoupled, reference Q: Q goes straight"),
          T("(c) 旋量插值：绕极点 c 转动", "(c) screw interpolation: rotation about the pole c")]
funcs = [lambda s: decoupled(TA2, TB2, s, np.r_[P_b, 0]), lambda s: decoupled(TA2, TB2, s, np.r_[Q_b, 0]), lambda s: screw_interp(TA2, TB2, s)]
for k in range(3):
    ax = fig.add_subplot(gs[0, k])
    ax.set_aspect("equal")
    ax.axis("off")
    for s in np.linspace(0, 1, 6):
        Tm = funcs[k](s)
        pts = (Tm[:2, :2] @ SHAPE.T).T + Tm[:2, 3]
        col = C["muted"] if 0 < s < 1 else (C["ink"] if s == 0 else C["z"])
        ax.fill(*pts.T, fc=col, alpha=0.08 if 0 < s < 1 else 0.25, ec=col, lw=0.8)
    ss = np.linspace(0, 1, 100)
    for pb, col, nm in ((P_b, C["x"], "P"), (Q_b, C["y"], "Q")):
        tr = np.array([(funcs[k](s)[:2, :2] @ pb) + funcs[k](s)[:2, 3] for s in ss])
        ax.plot(*tr.T, color=col, lw=1.8)
        ax.plot(*tr[0], "o", color=col, ms=4)
        ax.annotate(nm, tr[0], textcoords="offset points", xytext=(-12, -12), fontsize=11, color=col)
    if k == 2:
        V = E.log_twist(np.linalg.inv(TA2) @ TB2)
        th = V[2]
        vx, vy = V[3] / th, V[4] / th
        c = np.array([-vy, vx])                    # 平面：极点 c = (−v_y/ω, v_x/ω)
        ax.plot(*c, "o", color=C["accent"], ms=6)
        ax.annotate("c", c, textcoords="offset points", xytext=(6, -10), fontsize=12, color=C["accent"])
    ax.text(-0.45, -0.75, "A", fontsize=12)
    ax.text(2.6, 2.6, "B", fontsize=12, color=C["z"])
    ax.set_xlim(-1.4, 4.2)
    ax.set_ylim(-1.4, 3.4)
    ax.set_title(titles[k], fontsize=10.5)
ax = fig.add_subplot(gs[1, :2])
ax.set_aspect("equal")
curves(ax, "$x_s$ / m", "$y_s$ / m")
for key, col, lw, ls, nm in (("tcp", COL3, 2.0, "-", T("解耦，参考点 TCP", "decoupled, reference TCP")),
                             ("fl", COL5, 1.8, "--", T("解耦，参考点法兰盘中心", "decoupled, reference flange centre")),
                             ("screw", C["y"], 1.8, "-.", T("旋量插值", "screw interpolation"))):
    P = E.paths[key][:, :3, 3]
    ax.plot(P[:, 0], P[:, 1], color=col, lw=lw, ls=ls, label=nm)
    ax.plot(*P[1000, :2], "o", color=col, ms=5)
pa, pb = E.paths["tcp"][0][:3, 3], E.paths["tcp"][-1][:3, 3]
ax.annotate("A", pa[:2], textcoords="offset points", xytext=(6, -4), fontsize=11)
ax.annotate("B", pb[:2], textcoords="offset points", xytext=(6, -4), fontsize=11)
ax.plot(0, 0, "s", color=C["ink"], ms=6)
ax.text(0.02, -0.05, T("基座", "base"), fontsize=9)
ax.legend(loc="upper left", fontsize=9, frameon=False)
ax.set_title(T("(d) 算例 22.5.1：TCP 的路径（俯视），圆点为 s = 0.5", "(d) Example 22.5.1: TCP paths (top view), dots at s = 0.5"), fontsize=10.5)
ax.set_xlim(-0.35, 0.85)
ax = fig.add_subplot(gs[1, 2])
ax.axis("off")
txt = [T("旋量插值的螺旋轴（{s} 中）：", "screw axis of the screw interpolation (in {s}):"),
       T("方向", "direction") + " (1, 1, 1)/√3",
       T("转角", "rotation") + f" {math.degrees(E.th_sc):.0f}°",
       T("沿轴移动", "advance along the axis") + f" {E.d_ax:.3f} m",
       T("TCP 到轴的距离", "distance of TCP from the axis") + f" {E.r_tcp:.3f} m",
       "",
       T("TCP 走过的路程：", "distance travelled by the TCP:"),
       T("解耦（TCP）", "decoupled (TCP)") + f" {E.L_tcp['tcp']:.3f} m",
       T("解耦（法兰盘）", "decoupled (flange)") + f" {E.L_tcp['fl']:.3f} m",
       T("旋量", "screw") + f" {E.L_tcp['screw']:.3f} m"]
for i, s in enumerate(txt):
    ax.text(0.02, 0.95 - i * 0.085, s, fontsize=10.5, transform=ax.transAxes, color=C["ink"] if i not in (0, 6) else C["muted"])
fig.tight_layout()
figure(fig, "fig22_5_1")

# ---------------------------------------------------------------- 图 22.5.2
fig, ax = plt.subplots(figsize=(8.6, 3.8))
curves(ax, T("时间 $t$ / s", "time $t$ / s"), T("物体角速度的大小 / (rad/s)", "body angular speed / (rad/s)"))
t1, t2 = E.h[0], E.h.sum()
n01, n12 = np.linalg.norm(E.w01), np.linalg.norm(E.w12)
ax.plot([0, 0, t1, t1, t2, t2], [0, n01, n01, n12, n12, 0], color=COL5, lw=1.8, label=T("分段测地线（每段匀角速度）", "piecewise geodesics (constant rate per segment)"))
ax.plot(E.tt, np.linalg.norm(E.wb, axis=1), color=COL3, lw=2.0, label=T("C¹ 姿态样条", "C¹ orientation spline"))
ax.axvline(t1, color=LIM, lw=0.8, ls=":")
ax.text(t1 + 0.02, 0.15, "$R_1$", fontsize=11)
ax.legend(loc="upper left", fontsize=9, frameon=False)
ax.set_ylim(0, 3.4)
fig.tight_layout()
figure(fig, "fig22_5_2")
