"""20.5 节的示意图。

图 20.5.1：Go2 边走边转（俯视）：(a) v = 0.5 m/s、ω = 0.5 rad/s，瞬心在左侧 1 m 处，支撑脚在 {b} 中绕瞬心转过的弧，
          外侧两脚的支撑行程较长；(b) 原地转（v = 0、ω = 0.8 rad/s），瞬心在机身中心，四只脚的行程相同。
图 20.5.2：G1 的三个姿态（侧视，算例 20.5.2、20.5.3）：(a) 两脚不动、骨盆下降 0.10 m；(b) 弯腰取物，质心任务在内；
          (c) 去掉质心任务：手到了，质心却移到脚尖前方。
"""
import math

import numpy as np

from _fig20 import C, arrow, draw_g1_side, g1_points, plane
from _leg import (G1, G1_INERTIAL, G1_REST, LEGS, TH_REST, Tm, com, fk_links, g1_leg_ik, g1_sole_world, g1_stand_height,
                  g1_whole_body, hull, leg_fk, margin)
from bookout import T, figure, style

plt = style()
nominal = {l: leg_fk(l, TH_REST)[:2] for l in LEGS}

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.6, 5.2), gridspec_kw={"width_ratios": [1.15, 1.0]})
for ax, (v, om, Rlim, ttl) in zip((a1, a2), ((0.5, 0.5, None, T("(a) 小跑左转：v = 0.5 m/s，ω = 0.5 rad/s", "(a) trotting left turn: v = 0.5 m/s, ω = 0.5 rad/s")),
                                        (0.0, 0.8, None, T("(b) 原地转：v = 0，ω = 0.8 rad/s", "(b) turning on the spot: v = 0, ω = 0.8 rad/s")))):
    icr = np.array([0.0, v / om])
    ax.add_patch(plt.Rectangle((-0.24, -0.10), 0.48, 0.20, facecolor=C["body"], edgecolor=C["dark"], lw=1.0, zorder=1))
    ang = om * 0.25                                   # β t_c = 0.25 s 内转过的角度
    for l in LEGS:
        p = nominal[l]
        d = np.linalg.norm(p - icr)
        a0 = math.atan2(p[1] - icr[1], p[0] - icr[0])
        t = np.linspace(a0 + ang / 2, a0 - ang / 2, 30)
        arc = icr + d * np.c_[np.cos(t), np.sin(t)]
        col = C["orange"] if l[1] == "R" and v > 0 else C["thigh"]
        ax.plot(arc[:, 0], arc[:, 1], color=col, lw=3, zorder=3, solid_capstyle="round")
        arrow(ax, arc[-3], arc[-1], col, 1.4, 10, z=4)
        ax.plot([icr[0], p[0]], [icr[1], p[1]], color=C["muted"], lw=0.6, ls=":", zorder=2)
        ax.plot(*p, "o", ms=5, color="#3a3a3a", zorder=5)
        chord = 2 * d * math.sin(ang / 2)
        ax.text(p[0] + (0.03 if p[0] > 0 else -0.03), p[1] + (-0.06 if p[1] < 0 else 0.035),
                f"{l}  ℓ = {chord:.3f} m", fontsize=9.5, ha="left" if p[0] > 0 else "right", color=col)
    ax.plot(*icr, "o", ms=9, mfc="white", mec=C["accent"], mew=2, zorder=6)
    ax.text(icr[0] + 0.03, icr[1] + 0.02, T("瞬心", "ICR"), color=C["accent"], fontsize=10.5)
    arrow(ax, (0.0, 0.0), (0.16, 0.0), C["x"], 1.4, 9, z=6)
    ax.text(0.17, -0.02, "$x_b$", color=C["x"], fontsize=11)
    if v > 0:
        ax.text(-0.33, -0.32, T("支撑脚在 {b} 中绕瞬心转（箭头：β t_c = 0.25 s 内）", "stance feet circle the ICR in {b} (arrows: over β t_c = 0.25 s)"),
                fontsize=9.5, color=C["muted"])
        plane(ax, (-0.42, 0.45), (-0.36, 1.08))
    else:
        plane(ax, (-0.42, 0.45), (-0.30, 0.30))
    ax.set_title(ttl, fontsize=11)
fig.tight_layout()
figure(fig, "fig20_5_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 20.5.2（与程序 20.5.1 相同的计算）
z = g1_stand_height()
Tp = Tm(np.eye(3), (0, 0, z))
Tl0 = fk_links(G1, G1_REST, Tp)
T_fl, T_fr = Tl0["left_ankle_roll_link"].copy(), Tl0["right_ankle_roll_link"].copy()
soles = np.vstack([g1_sole_world(G1_REST, Tp, "left"), g1_sole_world(G1_REST, Tp, "right")])
poly = hull(soles[:, :2])
x_heel, x_toe = poly[:, 0].min(), poly[:, 0].max()
Tsq = Tm(np.eye(3), (0, 0, z - 0.10))
qsq, _, _ = g1_leg_ik("left", Tsq, T_fl)
qsq, _, _ = g1_leg_ik("right", Tsq, T_fr, qsq)
target = np.array([0.40, -0.20, 0.35])
Tw, qw, _ = g1_whole_body(target, Tp, G1_REST, T_fl, T_fr, poly.mean(0))
Tn, qn, _ = g1_whole_body(target, Tp, G1_REST, T_fl, T_fr, None)

fig, axs = plt.subplots(1, 3, figsize=(12.6, 5.4))
cases = [(axs[0], qsq, Tsq, T("(a) 下蹲：骨盆下降 0.10 m", "(a) squat: pelvis 0.10 m lower"), False),
         (axs[1], qw, Tw, T("(b) 弯腰取物：质心任务在内", "(b) reaching down, CoM task on"), True),
         (axs[2], qn, Tn, T("(c) 去掉质心任务", "(c) CoM task removed"), True)]
for ax, q, Tb, ttl, reach in cases:
    ax.plot([-0.35, 0.92], [0, 0], color=C["dark"], lw=1.2)
    ax.plot([x_heel, x_toe], [0, 0], color=C["green"], lw=6, solid_capstyle="butt", zorder=2)
    P = g1_points(q, Tb)
    draw_g1_side(ax, P)
    c, _ = com(G1, G1_INERTIAL, q, Tb)
    inside = margin(poly, c[:2]) > 0
    col = C["green"] if inside else C["red"]
    ax.plot(c[0], c[2], "o", ms=9, mfc="white", mec=col, mew=2.2, zorder=8)
    ax.plot([c[0], c[0]], [c[2], 0.0], color=col, lw=1.0, ls="--", zorder=7)
    ax.plot(c[0], 0, "v", ms=8, color=col, zorder=8)
    ax.text(c[0] + 0.02, c[2] + 0.03, T("质心", "CoM"), color=col, fontsize=10)
    if reach:
        ax.plot(*target[[0, 2]], "*", ms=14, color=C["accent"], zorder=9)
        ax.add_patch(plt.Rectangle((target[0] - 0.08, 0), 0.20, target[2] - 0.02, facecolor=C["fill"], edgecolor=C["steel"], lw=0.8, zorder=0))
    ax.text(-0.33, -0.06, T("绿：支撑区（脚底前后范围）", "green: support (heel to toe)"), fontsize=9, color=C["green"])
    ax.set_title(ttl, fontsize=11)
    plane(ax, (-0.35, 0.92), (-0.09, 1.40))
fig.tight_layout()
figure(fig, "fig20_5_2")
plt.close(fig)
