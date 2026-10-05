"""20.4 节的示意图。

图 20.4.1：(a) Go2 抬起右前腿：三脚支撑三角形，质心投影几乎落在对角线上；把机身移到使质心投影位于内心处（算例 20.4.2）。
          (b) G1 的两只脚：双脚支撑多边形、左脚的支撑多边形，骨盆侧移前后质心的投影（算例 20.4.4）。
图 20.4.2：爬行步态（算例 20.4.3）：(a) 一个周期中几个瞬间的支撑多边形与质心投影的轨迹（俯视，β = 0.85、A = 0.02 m）；
          (b) 稳定裕度随时间的变化：β = 0.75、β = 0.85 不侧摆、β = 0.85 侧摆 2 cm。
"""
import math

import numpy as np

from _fig20 import C, arrow, plane
from _leg import (G1, G1_INERTIAL, G1_REST, GO2, GO2_FOOT_R, GO2_INERTIAL, LEGS, TH_REST, Tm, com, crawl_min_margin, fk_links,
                  g1_leg_ik, g1_sole_world, g1_stand_height, go2_q, hull, leg_fk, margin, stance_ik)
from bookout import T, figure, style

plt = style()
h0 = -leg_fk("FL", TH_REST)[2] + GO2_FOOT_R
feet0 = {leg: leg_fk(leg, TH_REST) + np.array([0, 0, h0]) for leg in LEGS}


def go2_com(T_sb):
    th = stance_ik(T_sb, feet0)
    return com(GO2, GO2_INERTIAL, go2_q(th), T_sb)[0]


fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.6, 5.0), gridspec_kw={"width_ratios": [1.15, 1.0]})
c0 = go2_com(Tm(np.eye(3), (0, 0, h0)))
P = {l: feet0[l][:2] for l in LEGS}
quad = np.array([P["FL"], P["FR"], P["RR"], P["RL"], P["FL"]])
a1.plot(quad[:, 0], quad[:, 1], color=C["light"], lw=1.0, ls="--", zorder=1)
tri = np.array([P["FL"], P["RL"], P["RR"], P["FL"]])
a1.fill(tri[:, 0], tri[:, 1], color=C["blue"], alpha=0.12, zorder=1)
a1.plot(tri[:, 0], tri[:, 1], color=C["blue"], lw=1.4, zorder=2)
for l in LEGS:
    lifted = l == "FR"
    a1.plot(*P[l], "o", ms=10, color="white" if lifted else "#3a3a3a", mec="#3a3a3a", zorder=4)
    a1.text(P[l][0] + (0.02 if P[l][0] > 0 else -0.075), P[l][1] + (0.02 if P[l][1] > 0 else -0.04),
            l + (T("（抬起）", " (lifted)") if lifted else ""), fontsize=10)
# 内心与内切圆
A, B, Cc = P["FL"], P["RL"], P["RR"]
a_, b_, c_ = np.linalg.norm(B - Cc), np.linalg.norm(A - Cc), np.linalg.norm(A - B)
I = (a_ * A + b_ * B + c_ * Cc) / (a_ + b_ + c_)
s = (a_ + b_ + c_) / 2
u, w = B - A, Cc - A
r_in = abs(u[0] * w[1] - u[1] * w[0]) / 2 / s
t = np.linspace(0, 2 * math.pi, 100)
a1.plot(I[0] + r_in * np.cos(t), I[1] + r_in * np.sin(t), color=C["green"], lw=0.9, ls=":", zorder=2)
a1.plot(*c0[:2], "x", ms=10, mew=2.2, color=C["red"], zorder=5)
a1.text(c0[0] + 0.015, c0[1] + 0.012, T("质心投影（站立）", "CoM (standing)"), color=C["red"], fontsize=9.5)
a1.plot(*I, "+", ms=12, mew=2.2, color=C["green"], zorder=5)
a1.text(I[0] - 0.02, I[1] - 0.04, T("内心：裕度最大", "incentre: largest margin"), color=C["green"], fontsize=9.5, ha="center")
arrow(a1, c0[:2], I, C["green"], 1.4, 10, z=6)
a1.add_patch(plt.Rectangle((-0.24, -0.10), 0.48, 0.20, facecolor="none", edgecolor=C["steel"], lw=0.9, ls="-", zorder=0))
arrow(a1, (-0.33, -0.22), (-0.25, -0.22), C["x"], 1.2, 9)
arrow(a1, (-0.33, -0.22), (-0.33, -0.14), C["y"], 1.2, 9)
a1.text(-0.245, -0.235, "$x$", color=C["x"], fontsize=10)
a1.text(-0.35, -0.125, "$y$", color=C["y"], fontsize=10)
a1.set_title(T("(a) Go2 抬起右前腿：先把质心移进三角形", "(a) Go2 lifts its front-right leg: move the CoM into the triangle first"), fontsize=11)
plane(a1, (-0.36, 0.33), (-0.25, 0.22))

# (b) G1
z = g1_stand_height()
Tp = Tm(np.eye(3), (0, 0, z))
L = g1_sole_world(G1_REST, Tp, "left")[:, :2]
R = g1_sole_world(G1_REST, Tp, "right")[:, :2]
hull2 = hull(np.vstack([L, R]))
H = np.vstack([hull2, hull2[:1]])
a2.fill(H[:, 0], H[:, 1], color=C["blue"], alpha=0.08)
a2.plot(H[:, 0], H[:, 1], color=C["blue"], lw=1.0, ls="--")
for S, col in ((L, C["green"]), (R, C["dark"])):
    hh = hull(S)
    hh = np.vstack([hh, hh[:1]])
    a2.fill(hh[:, 0], hh[:, 1], color=col, alpha=0.25)
    a2.plot(hh[:, 0], hh[:, 1], color=col, lw=1.4)
cg, _ = com(G1, G1_INERTIAL, G1_REST, Tp)
a2.plot(cg[0], cg[1], "x", ms=10, mew=2.2, color=C["red"])
a2.text(cg[0] + 0.012, cg[1] - 0.03, T("站立时的质心投影", "CoM, standing"), color=C["red"], fontsize=9.5)
# 骨盆侧移后的质心（与程序 20.4.1 相同的计算）
Tl0 = fk_links(G1, G1_REST, Tp)
Tf = {s: Tl0[f"{s}_ankle_roll_link"].copy() for s in ("left", "right")}
ctrL = hull(L).mean(0)


def shifted(dy, dz=-0.03):
    Tq = Tm(np.eye(3), (0, dy, z + dz))
    q = None
    for s in ("left", "right"):
        q, _, _ = g1_leg_ik(s, Tq, Tf[s], q)
    return com(G1, G1_INERTIAL, q, Tq)[0]


dy = 0.0
for _ in range(30):
    c1 = shifted(dy)
    e = ctrL[1] - c1[1]
    if abs(e) < 1e-12:
        break
    dy += e / ((shifted(dy + 1e-5)[1] - c1[1]) / 1e-5)
c1 = shifted(dy)
a2.plot(c1[0], c1[1], "x", ms=10, mew=2.2, color=C["green"])
arrow(a2, cg[:2] + [0, 0.008], c1[:2] - [0, 0.008], C["green"], 1.3, 9)
a2.text(-0.215, c1[1] + 0.01, T("骨盆左移 %.3f m 后的\n质心投影" % dy, "CoM after the pelvis\nmoves %.3f m left" % dy), color=C["green"], fontsize=9.5)
a2.text(0.13, 0.105, T("左脚", "left foot"), fontsize=10, color=C["green"])
a2.text(0.13, -0.15, T("右脚", "right foot"), fontsize=10, color=C["dark"])
a2.text(-0.18, 0.02, T("双脚支撑\n多边形", "double-support\npolygon"), fontsize=9.5, color=C["blue"])
arrow(a2, (-0.20, -0.20), (-0.14, -0.20), C["x"], 1.2, 9)
arrow(a2, (-0.20, -0.20), (-0.20, -0.14), C["y"], 1.2, 9)
a2.text(-0.135, -0.21, "$x$", color=C["x"], fontsize=10)
a2.text(-0.22, -0.125, "$y$", color=C["y"], fontsize=10)
a2.set_title(T("(b) G1：从双脚到单脚（俯视）", "(b) G1: from two feet to one (top view)"), fontsize=11)
plane(a2, (-0.23, 0.30), (-0.22, 0.20))
fig.tight_layout()
figure(fig, "fig20_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 20.4.2
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.6, 4.8), gridspec_kw={"width_ratios": [1.2, 1.0]})
best, (ts, ms, cs, polys, feets) = crawl_min_margin(0.85, 0.02, n=400, ret=True)
cs = np.array(cs)
a1.plot(cs[:, 0], cs[:, 1], color=C["red"], lw=1.6, zorder=4, label=T("质心投影的轨迹", "CoM path"))
cols = [C["blue"], C["orange"], C["green"], C["purple"]]
for j, k in enumerate((70, 170, 270, 370)):
    pg = np.vstack([polys[k], polys[k][:1]])
    a1.fill(pg[:, 0], pg[:, 1], color=cols[j], alpha=0.10, zorder=1)
    a1.plot(pg[:, 0], pg[:, 1], color=cols[j], lw=1.2, zorder=2)
    a1.plot(*cs[k], "o", ms=5, color=cols[j], zorder=5)
    off = [(-0.075, 0.018), (-0.01, -0.04), (0.005, 0.022), (0.0, -0.04)][j]
    a1.text(cs[k][0] + off[0], cs[k][1] + off[1], f"t = {ts[k]:.2f} s", fontsize=9, color=cols[j], zorder=6)
a1.set_xlabel("x / m")
a1.set_ylabel("y / m")
a1.set_aspect("equal")
a1.grid(alpha=0.25)
a1.legend(loc="upper left", fontsize=9.5, frameon=False)
a1.set_title(T("(a) 四次单腿摆动中途的支撑三角形与质心投影", "(a) support triangles mid-swing of each leg, and the CoM"), fontsize=11)
for (beta, A, col, lab) in ((0.75, 0.0, C["dark"], "β = 0.75"), (0.85, 0.0, C["blue"], "β = 0.85"),
                            (0.85, 0.02, C["green"], T("β = 0.85，侧摆 2 cm", "β = 0.85, sway 2 cm"))):
    _, (tt, mm, _, _, _) = crawl_min_margin(beta, A, n=400, ret=True)
    a2.plot(tt, np.array(mm) * 1000, color=col, lw=1.6, label=lab)
a2.axhline(0, color=C["red"], lw=0.8)
a2.set_xlabel(T("t / s（周期 2 s）", "t / s (cycle 2 s)"))
a2.set_ylabel(T("稳定裕度 / mm", "stability margin / mm"))
a2.set_xlim(0, 2)
a2.grid(alpha=0.25)
a2.legend(loc="upper right", fontsize=9.5, frameon=False)
a2.set_title(T("(b) 稳定裕度随时间的变化", "(b) stability margin over the cycle"), fontsize=11)
fig.tight_layout()
figure(fig, "fig20_4_2")
plt.close(fig)
