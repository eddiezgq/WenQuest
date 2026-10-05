"""15.1 节的示意图。

图 15.1.1：平面 3R 臂（尺寸同 14.2.5 节）在 SE(2) 上的牛顿-拉夫森迭代（算例 15.1.1）。
           左：当前末端坐标系 {b}、目标 {d}，位姿误差 V_b 是“绕极点 c 转过 φ”的位移，e^{t[V_b]} 把 {b} 沿圆弧带到 {d}；
           右：各次迭代的手臂形态，第 5 次后与目标重合。
图 15.1.2：UR5e（算例 15.1.2、15.1.3）。左：从“当前关节角”出发的各次迭代；右：‖V_b‖ 随迭代次数的变化（对数坐标）。
"""
import math

import numpy as np

from _fig15 import BLUE2, C, axes3d, base_mark, draw_chain, equal3d, floor3d, frame2d, logaxis, plane, ur_chain
from _nik import (PL, TH_CUR, TH_HOME, err_twist, exp_se2, fk_space, joints_planar, jacobian_body, body_screws, log_se2, nr,
                  planar_nr, planar_pose, pole_se2, se2, ur_fk, ur_jb, ur_screws_perturbed, ur_table, ur_target)
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 15.1.1
Tp = se2(0.6, 0.05, -math.pi / 2)
p0 = np.radians([30, -40, -20])
_, _, hist = planar_nr(Tp, p0)
Tb = planar_pose(p0)
V = hist[0][1]
cs = Tb[:2, :2] @ pole_se2(V) + Tb[:2, 2]

fig, axs = plt.subplots(1, 2, figsize=(10.4, 3.9))
ax = axs[0]
plane(ax, (-0.08, 0.98), (-0.12, 0.6))
base_mark(ax)
P = joints_planar(p0)
ax.plot(P[:, 0], P[:, 1], color=C["muted"], lw=5, solid_capstyle="round", alpha=0.55, zorder=2)
for q in P[:-1]:
    ax.plot(*q, "o", ms=6, mfc="white", mec=C["muted"], zorder=3)
# e^{t[V]}：{b} 绕极点 c 转过 tφ
for t in np.linspace(0, 1, 6)[1:-1]:
    frame2d(ax, Tb @ exp_se2(V * t), 0.05, lw=0.9)
r = np.linalg.norm(Tb[:2, 2] - cs)
a0 = math.atan2(*(Tb[:2, 2] - cs)[::-1])
a1 = a0 + V[0]
tt = np.linspace(a0, a1, 80)
ax.plot(cs[0] + r * np.cos(tt), cs[1] + r * np.sin(tt), color=C["accent"], lw=1.4, ls="--", zorder=1)
ax.plot(*cs, "+", color=C["accent"], ms=11, mew=2, zorder=5)
ax.text(cs[0] + 0.02, cs[1] + 0.02, T("极点 c", "pole c"), fontsize=10, color=C["accent"])
ax.plot([cs[0], Tb[0, 2]], [cs[1], Tb[1, 2]], color=C["accent"], lw=0.7, ls=":")
ax.plot([cs[0], Tp[0, 2]], [cs[1], Tp[1, 2]], color=C["accent"], lw=0.7, ls=":")
ax.text(cs[0] + 0.07, cs[1] - 0.04, T("转过 φ = −60°", "turn φ = −60°"), fontsize=10, color=C["accent"])
frame2d(ax, Tb, 0.09, lw=1.8, label="{b}", off=(-0.075, 0.02))
frame2d(ax, Tp, 0.09, lw=1.8, label="{d}", off=(0.015, -0.06))
ax.text(-0.05, 0.57, T("(a) 位姿误差：绕极点的转动", "(a) Pose error: a turn about the pole"), fontsize=11, color=C["ink"])

ax = axs[1]
plane(ax, (-0.08, 0.98), (-0.12, 0.6))
base_mark(ax)
cols = ["#b0b7bc", "#8fb3d6", "#5b8fc4", "#2f6aa8", C["z"]]
for k, (th, _) in enumerate(hist[:5]):
    P = joints_planar(th)
    ax.plot(P[:, 0], P[:, 1], color=cols[k], lw=4 if k < 4 else 5, solid_capstyle="round", alpha=0.95, zorder=2 + k)
    for q in P[1:-1]:
        ax.plot(*q, "o", ms=4.5, mfc="white", mec=cols[k], zorder=3 + k)
    if k in (0, 1):
        dx, dy = {0: (0.02, 0.0), 1: (-0.075, -0.03)}[k]
        ax.text(P[3, 0] + dx, P[3, 1] + dy, f"θ$^{{({k})}}$", fontsize=10, color=cols[k], zorder=10)
frame2d(ax, Tp, 0.09, lw=1.8, label="{d}", off=(0.015, -0.06))
ax.text(-0.05, 0.57, T("(b) 迭代：θ⁽⁰⁾ → θ⁽¹⁾ → …", "(b) Iterates: θ⁽⁰⁾ → θ⁽¹⁾ → …"), fontsize=11, color=C["ink"])
norms = [float(np.linalg.norm(Vk)) for _, Vk in hist]
txt = "\n".join(f"k = {k}:  ‖V$_b$‖ = {x:.1e}" for k, x in enumerate(norms))
ax.text(0.56, 0.58, txt, fontsize=8.6, color=C["ink"], va="top", family="DejaVu Sans")
fig.tight_layout()
figure(fig, "fig15_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 15.1.2
Td = ur_target()
_, _, hc = nr(ur_fk, ur_jb, Td, TH_CUR)
_, _, hh = nr(ur_fk, ur_jb, Td, TH_HOME)
_, _, hb = nr(ur_fk, ur_jb, Td, np.radians([-120, -100, -80, -60, 90, 60]))
Sc, Mc = ur_screws_perturbed(dL1=0.4e-3, dL2=-0.3e-3, tilt3=math.radians(0.05))
offs = np.radians([0.03, -0.05, 0.04, 0.06, -0.02, 0.05])
Bc = body_screws(Sc, Mc)
_, _, hcal = nr(lambda t: fk_space(Sc, Mc, np.asarray(t) + offs), lambda t: jacobian_body(Bc, np.asarray(t) + offs), Td, ur_table()[2])

fig = plt.figure(figsize=(10.6, 4.6))
_, ax = axes3d(plt, fig=fig, pos=121, elev=20, azim=-60)
pts = []
cols = ["#b0b7bc", "#9db8d6", "#5b8fc4", C["z"]]
for k, (th, _) in enumerate(hh[:7]):
    Pk = ur_chain(th)
    pts.append(Pk)
    if k in (0, 1, 2, 6):
        c = {0: cols[0], 1: cols[1], 2: cols[2], 6: cols[3]}[k]
        draw_chain(ax, Pk, c, lw=4 if k < 6 else 5, alpha=0.9 if k < 6 else 1.0, js=12)
pts = np.vstack(pts)
p = Td[:3, 3]
ax.scatter(*p, s=40, color=C["x"], depthshade=False, zorder=10)
n = Td[:3, 1] * 0.12
ax.quiver(*p, *n, color=C["x"], lw=1.6, arrow_length_ratio=0.25)
floor3d(ax, half=0.55)
equal3d(ax, np.vstack([pts, [[0.4, 0.4, 0], [-0.6, -0.6, 0]]]), pad=0.02, zoom=1.25)
ax.text2D(0.02, 0.95, T("(a) 从起始姿态出发的迭代", "(a) Iterates from the start posture"), transform=ax.transAxes, fontsize=10.5)
ax.text2D(0.02, 0.88, T("灰：θ⁽⁰⁾；浅蓝：θ⁽¹⁾、θ⁽²⁾；深蓝：收敛", "grey: θ⁽⁰⁾; light blue: θ⁽¹⁾, θ⁽²⁾; dark: converged"),
          transform=ax.transAxes, fontsize=8.5, color=C["muted"])

ax = fig.add_subplot(122)
for h, c, m, lab in ((hc, C["z"], "o", T("起点：当前关节角", "start: current angles")),
                     (hh, C["accent"], "s", T("起点：大臂竖直的姿态", "start: upper arm upright")),
                     (hb, C["y"], "^", T("起点：习题 14.5.5 的关节角", "start: Exercise 14.5.5")),
                     (hcal, C["x"], "D", T("标定后的手臂（算例 15.1.3）", "calibrated arm (Example 15.1.3)"))):
    y = [max(float(np.linalg.norm(V)), 1e-17) for _, V in h]
    ax.plot(range(len(y)), y, color=c, marker=m, ms=5, lw=1.4, label=lab)
logaxis(ax)
ax.set_ylim(1e-17, 3)
ax.axhspan(1e-17, 2e-16, color="#f0f0f0", zorder=0)
ax.text(0.2, 3e-17, T("双精度舍入误差", "double-precision round-off"), fontsize=8.5, color=C["muted"])
ax.set_xlabel(T("迭代次数 k", "iteration k"))
ax.set_ylabel(T("‖V$_b$‖（弧度与米合在一起）", "‖V$_b$‖ (radians and metres together)"))
ax.legend(fontsize=8.5, frameon=False, loc="upper right")
ax.set_title(T("(b) 误差旋量的大小", "(b) Size of the error twist"), fontsize=10.5, loc="left")
fig.tight_layout()
figure(fig, "fig15_1_2")
plt.close(fig)
