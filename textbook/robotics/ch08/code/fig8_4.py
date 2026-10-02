"""8.4 节的示意图。

图 8.4.1：(a) 凸集：任意两点的连线都在集合内；(b) 非凸集：车间里绕过货架的可通行区域，连线穿过货架；
         (c) 凸函数：弦在图像上方；(d) 非凸函数：2R 臂逆运动学目标函数沿两组解 A、B 连线的取值，弦（f = 0）在图像下方。
图 8.4.2：夹爪（矩形）与障碍物（三角形）的最短距离与分离直线（算例 8.4.2）。
图 8.4.3：AGV 在两段凸走廊中的路径（算例 8.4.3）与障碍函数法的中心路径（t = 1、10、100、1000）。
"""
import math

import numpy as np

from _fig8 import BLUE, C, GREY, ORANGE, PURPLE, arrow, clean
from _opt import L2R, barrier_qp, ik_closed_2r, tip
from bookout import T, figure, style

plt = style()


def halfplanes(P):
    A, b = [], []
    for i in range(len(P)):
        p, q = np.array(P[i], float), np.array(P[(i + 1) % len(P)], float)
        t = q - p
        n = np.array([t[1], -t[0]]) / np.linalg.norm(t)
        A.append(n)
        b.append(n @ p)
    return np.array(A), np.array(b)


# ---------------------------------------------------------------- 图 8.4.1
fig, axs = plt.subplots(1, 4, figsize=(12.0, 3.3))
a1, a2, a3, a4 = axs
for a in (a1, a2):
    clean(a)
t = np.linspace(0, 2 * math.pi, 200)
a1.fill(1.2 * np.cos(t), 0.8 * np.sin(t), color="#d7e7f5")
a1.plot(1.2 * np.cos(t), 0.8 * np.sin(t), color=BLUE, lw=1.2)
P = np.array([[-0.8, -0.3], [0.9, 0.45]])
a1.plot(P[:, 0], P[:, 1], "-o", color=C["ink"], ms=4, lw=1.2)
a1.text(-0.9, -0.5, "$x$", fontsize=11)
a1.text(0.85, 0.55, "$y$", fontsize=11)
a1.text(-1.25, -1.15, T("(a) 凸集：连线在集合内", "(a) convex set: the segment stays inside"), fontsize=9)
a1.set_xlim(-1.4, 1.4)
a1.set_ylim(-1.25, 1.0)
free = np.array([[0, 0], [3, 0], [3, 2], [2.2, 2], [2.2, 0.7], [0, 0.7]])
a2.fill(free[:, 0], free[:, 1], color="#d7e7f5")
a2.plot(np.r_[free[:, 0], 0], np.r_[free[:, 1], 0], color=BLUE, lw=1.2)
a2.fill([0, 2.2, 2.2, 0], [0.7, 0.7, 2.0, 2.0], color="#c9c2b6")
a2.text(0.7, 1.3, T("货架", "shelves"), fontsize=9)
P = np.array([[0.4, 0.35], [2.6, 1.7]])
a2.plot(P[:, 0], P[:, 1], "-o", color=C["x"], ms=4, lw=1.2)
a2.text(-0.05, -0.45, T("(b) 非凸集：连线穿过货架", "(b) non-convex: the segment crosses the shelves"), fontsize=9)
a2.set_xlim(-0.1, 3.1)
a2.set_ylim(-0.5, 2.1)
xx = np.linspace(-1.5, 2.0, 200)
fc = 0.5 * xx ** 2 + 0.2 * xx + 0.3
a3.plot(xx, fc, color=C["ink"], lw=1.6)
x1, x2 = -1.1, 1.6
f1, f2 = 0.5 * x1 ** 2 + 0.2 * x1 + 0.3, 0.5 * x2 ** 2 + 0.2 * x2 + 0.3
a3.plot([x1, x2], [f1, f2], "-o", color=C["x"], ms=4, lw=1.2)
s = 0.4
xm = (1 - s) * x1 + s * x2
a3.plot([xm, xm], [0.5 * xm ** 2 + 0.2 * xm + 0.3, (1 - s) * f1 + s * f2], color=C["accent"], lw=1.2, ls=":")
a3.text(xm - 0.95, 1.05, T("弦在上方", "chord above"), fontsize=8.5, color=C["accent"])
a3.set_title(T("(c) 凸函数", "(c) convex function"), fontsize=9.5)
a3.set_yticks([])
a3.set_xticks([])
pd = np.array([0.5, 0.4])
ta, tb = ik_closed_2r(pd, L2R, +1), ik_closed_2r(pd, L2R, -1)
ss = np.linspace(-0.15, 1.15, 300)
fv = [0.5 * float((tip((1 - u) * ta + u * tb, L2R) - pd) @ (tip((1 - u) * ta + u * tb, L2R) - pd)) for u in ss]
a4.plot(ss, fv, color=C["ink"], lw=1.6)
a4.plot([0, 1], [0, 0], "-o", color=C["x"], ms=4, lw=1.2)
a4.text(-0.05, 0.0015, "A", fontsize=10, color=BLUE)
a4.text(1.0, 0.0015, "B", fontsize=10, color=ORANGE)
a4.text(0.25, 0.004, T("弦（f = 0）在下方", "chord (f = 0) below"), fontsize=8.5, color=C["x"])
a4.set_title(T("(d) 非凸：IK 目标函数沿 A→B", "(d) non-convex: the IK objective along A→B"), fontsize=9.5)
a4.set_xlabel("$s$", fontsize=9)
a4.set_ylabel(r"$f((1-s)\theta_A + s\theta_B)$", fontsize=8.5)
a4.tick_params(labelsize=7.5)
for a in (a3, a4):
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
fig.tight_layout()
figure(fig, "fig8_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 8.4.2
ang = math.radians(25)
Rg = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
cg = np.array([0.30, 0.20])
G = np.array([cg + Rg @ np.array(v) for v in [(-0.06, -0.03), (0.06, -0.03), (0.06, 0.03), (-0.06, 0.03)]])
O = np.array([(0.42, 0.28), (0.55, 0.25), (0.50, 0.40)])
A1, b1 = halfplanes(G)
A2, b2 = halfplanes(O)
A = np.block([[A1, np.zeros((4, 2))], [np.zeros((3, 2)), A2]])
b = np.r_[b1, b2]
Q = np.block([[np.eye(2), -np.eye(2)], [-np.eye(2), np.eye(2)]])
x, cent, mu, _, _ = barrier_qp(Q, np.zeros(4), A, b, np.r_[G.mean(0), O.mean(0)], t0=1.0, eps=1e-10)
u, w = x[:2], x[2:]
n = (w - u) / np.linalg.norm(w - u)
fig, ax = plt.subplots(figsize=(6.4, 4.4))
clean(ax)
ax.fill(G[:, 0], G[:, 1], color="#d7e7f5")
ax.plot(np.r_[G[:, 0], G[0, 0]], np.r_[G[:, 1], G[0, 1]], color=BLUE, lw=1.4)
ax.text(cg[0] - 0.05, cg[1] - 0.008, T("夹爪", "gripper"), fontsize=9, color=BLUE)
ax.fill(O[:, 0], O[:, 1], color="#f3d9c6")
ax.plot(np.r_[O[:, 0], O[0, 0]], np.r_[O[:, 1], O[0, 1]], color=ORANGE, lw=1.4)
ax.text(O[:, 0].mean() - 0.02, O[:, 1].mean() - 0.01, T("障碍物", "obstacle"), fontsize=9, color=ORANGE)
ax.plot([u[0], w[0]], [u[1], w[1]], "-", color=C["x"], lw=1.4)
ax.plot(*u, "o", color=C["x"], ms=5)
ax.plot(*w, "o", color=C["x"], ms=5)
ax.text(u[0] - 0.035, u[1] + 0.012, "$u^*$", fontsize=11, color=C["x"])
ax.text(w[0] - 0.005, w[1] + 0.015, "$w^*$", fontsize=11, color=C["x"])
mid = (u + w) / 2
tdir = np.array([-n[1], n[0]])
ax.plot([mid[0] - 0.2 * tdir[0], mid[0] + 0.17 * tdir[0]], [mid[1] - 0.2 * tdir[1], mid[1] + 0.17 * tdir[1]], color=PURPLE, lw=1.1, ls="--")
ax.text(mid[0] + 0.17 * tdir[0] - 0.02, mid[1] + 0.17 * tdir[1] + 0.008, T("分离直线", "separating line"), fontsize=9, color=PURPLE)
nb = mid - 0.1 * tdir
arrow(ax, nb, nb + 0.05 * n, PURPLE, 1.3, ms=9)
ax.text(nb[0] + 0.05 * n[0] + 0.004, nb[1] + 0.05 * n[1] - 0.012, "$n$", fontsize=11, color=PURPLE)
ax.text(0.2, 0.06, T(f"最短距离 d = {np.linalg.norm(u - w) * 1000:.2f} mm", f"shortest distance d = {np.linalg.norm(u - w) * 1000:.2f} mm"), fontsize=9.5)
ax.set_xlim(0.19, 0.6)
ax.set_ylim(0.04, 0.43)
figure(fig, "fig8_4_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 8.4.3
R1 = [(0, 0), (6, 0), (6, 1.2), (0, 1.8)]
R2 = [(4.6, 0), (6, 0), (6, 4), (4.6, 4)]
Ar1, br1 = halfplanes(R1)
Ar2, br2 = halfplanes(R2)
start, goal = np.array([0.5, 0.9]), np.array([5.3, 3.5])
Nw, kx = 10, 5
nv = 2 * (Nw - 1)
rows, rhs = [], []
for i in range(1, Nw):
    regs = ([(Ar1, br1)] if i <= kx else []) + ([(Ar2, br2)] if i >= kx else [])
    for Aa, bb in regs:
        for a_, b_ in zip(Aa, bb):
            r = np.zeros(nv)
            r[2 * (i - 1):2 * i] = a_
            rows.append(r)
            rhs.append(b_)
Ac, bc = np.array(rows), np.array(rhs)
Dm, dv = np.zeros((2 * Nw, nv)), np.zeros(2 * Nw)
for i in range(Nw):
    for k in range(2):
        if i + 1 <= Nw - 1:
            Dm[2 * i + k, 2 * i + k] += 1
        else:
            dv[2 * i + k] += goal[k]
        if i >= 1:
            Dm[2 * i + k, 2 * (i - 1) + k] -= 1
        else:
            dv[2 * i + k] -= start[k]
Qc, cc = 2 * Dm.T @ Dm, 2 * Dm.T @ dv
x0c = np.array([start + (np.array([5.3, 0.9]) - start) * i / kx if i <= kx else
                np.array([5.3, 0.9 + (goal[1] - 0.9) * (i - kx) / (Nw - kx)]) for i in range(1, Nw)]).ravel()
xc, cent_c, _, _, _ = barrier_qp(Qc, cc, Ac, bc, x0c, t0=1.0, eps=1e-9)
fig, ax = plt.subplots(figsize=(8.6, 5.2))
clean(ax)
ax.fill([0, 6, 6, 0], [0, 0, 4, 4], color="#f4f1ea")
ax.fill([0, 4.6, 4.6, 0], [1.8 - 0.0, 1.8 - 0.6 * 4.6 / 6, 4, 4], color="#c9c2b6")
ax.text(1.6, 2.9, T("货架区（障碍，已按 AGV 半径膨胀）", "shelf area (obstacle, inflated by the AGV radius)"), fontsize=9.5)
ax.fill([0, 6, 6, 0], [0, 0, 1.2, 1.8], color="#d7e7f5", alpha=0.6)
ax.fill([4.6, 6, 6, 4.6], [0, 0, 4, 4], color="#e4d7f0", alpha=0.6)
ax.plot([0, 6, 6, 0, 0], [0, 0, 1.2, 1.8, 0], color=BLUE, lw=1.0)
ax.plot([4.6, 6, 6, 4.6, 4.6], [0, 0, 4, 4, 0], color=PURPLE, lw=1.0)
ax.text(0.15, 0.15, T("凸区域 R₁", "convex region R₁"), fontsize=9, color=BLUE)
ax.text(4.68, 3.75, T("凸区域 R₂", "convex region R₂"), fontsize=9, color=PURPLE)
cols = {1: GREY, 10: "#2ca02c", 100: ORANGE}
for tt, xx in cent_c:
    k = round(tt)
    if k in cols:
        Pk = np.vstack([start, xx.reshape(-1, 2), goal])
        ax.plot(Pk[:, 0], Pk[:, 1], "-o", color=cols[k], lw=0.9, ms=2.5, label=f"t = {k}")
P = np.vstack([start, xc.reshape(-1, 2), goal])
ax.plot(P[:, 0], P[:, 1], "-o", color=C["x"], lw=1.6, ms=4, label=T("最优路径", "optimal path"), zorder=6)
ax.plot(*start, "s", color=C["ink"], ms=7)
ax.plot(*goal, "*", color=C["ink"], ms=11)
ax.text(start[0] - 0.1, start[1] + 0.15, T("起点", "start"), fontsize=9)
ax.text(goal[0] + 0.12, goal[1] - 0.05, T("终点", "goal"), fontsize=9)
ax.text(P[kx][0] - 0.95, P[kx][1] + 0.12, T("x₅ 在 R₁ ∩ R₂", "x₅ in R₁ ∩ R₂"), fontsize=9, color=C["x"])
ax.legend(fontsize=8.5, loc="center right", bbox_to_anchor=(1.32, 0.55), frameon=False, title=T("中心路径", "central path"), title_fontsize=9)
ax.set_xlim(-0.1, 6.1)
ax.set_ylim(-0.1, 4.1)
ax.text(0, -0.45, T("单位：m", "units: m"), fontsize=8.5, color=C["muted"])
figure(fig, "fig8_4_3")
plt.close(fig)
