"""图 2.2.1：两连杆臂末端 = 两个连杆向量之和（三角形法则与平行四边形法则）；数乘。
图 2.2.2：u、w 的整数系数组合铺成一张斜网格，b = 2u + 3w；平行的两个向量只组合出一条直线。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow, figure, plt

l1, l2 = 0.425, 0.392
t1, t2 = math.radians(30), math.radians(45)
r1 = l1 * np.array([math.cos(t1), math.sin(t1)])
r2 = l2 * np.array([math.cos(t1 + t2), math.sin(t1 + t2)])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 4.4))
a1.plot([0, r1[0], r1[0] + r2[0]], [0, r1[1], r1[1] + r2[1]], color="#9db4c8", lw=9, solid_capstyle="round", zorder=1)
for P in (np.zeros(2), r1):
    a1.plot(*P, "o", ms=9, mfc="white", mec=INK, zorder=3)
arrow(a1, r1, BLUE, None)
arrow(a1, r2, GREEN, None, start=r1)
arrow(a1, r2, GREEN, None)
arrow(a1, r1, BLUE, None, start=r2)
for P, Q in ((r2, r1 + r2), (r1, r1 + r2)):
    a1.plot([P[0], Q[0]], [P[1], Q[1]], color=MUTED, ls=":", lw=0.8)
arrow(a1, r1 + r2, RED, None, lw=2.6)
a1.text(r1[0] / 2 + 0.01, r1[1] / 2 - 0.06, r"$\boldsymbol{r}_1$", color=BLUE, fontsize=13)
a1.text(r1[0] + r2[0] / 2 + 0.02, r1[1] + r2[1] / 2 - 0.02, r"$\boldsymbol{r}_2$", color=GREEN, fontsize=13)
a1.text(r2[0] / 2 - 0.08, r2[1] / 2, r"$\boldsymbol{r}_2$", color=GREEN, fontsize=13)
a1.text((r1 + r2)[0] + 0.02, (r1 + r2)[1], r"$\boldsymbol{p}=\boldsymbol{r}_1+\boldsymbol{r}_2$", color=RED, fontsize=13)
a1.text(0.03, -0.07, T("肩关节", "shoulder"), fontsize=9, color=MUTED)
a1.text(r1[0] + 0.02, r1[1] - 0.06, T("肘关节", "elbow"), fontsize=9, color=MUTED)
a1.set_xlim(-0.1, 0.75)
a1.set_ylim(-0.12, 0.72)
a1.set_aspect("equal")
a1.set_xlabel("x / m")
a1.set_ylabel("y / m")
a1.set_title(T("末端位置 = 上臂向量 + 前臂向量", "Tool position = upper-arm vector + forearm vector"), fontsize=11)
v = np.array([1.0, 0.5])
for c, col, off in ((2.0, RED, (0.08, 0.05)), (1.0, BLUE, (-0.15, 0.2)), (0.5, GREEN, (0.0, -0.35)), (-1.0, ACC, (-0.55, -0.25))):
    arrow(a2, c * v, col, None, lw=2.0 if c != 1 else 2.6)
    a2.text(c * v[0] + off[0], c * v[1] + off[1], {2.0: r"$2\boldsymbol{v}$", 1.0: r"$\boldsymbol{v}$", 0.5: r"$0.5\boldsymbol{v}$", -1.0: r"$-\boldsymbol{v}$"}[c], color=col, fontsize=13)
a2.plot([-2.4, 2.6], [-1.2, 1.3], color=MUTED, ls="--", lw=0.8)
a2.set_xlim(-2.0, 2.6)
a2.set_ylim(-1.4, 1.6)
a2.set_aspect("equal")
a2.axhline(0, color=MUTED, lw=0.5)
a2.axvline(0, color=MUTED, lw=0.5)
a2.set_title(T("数乘：沿同一条直线伸缩、反向", "Scalar multiples: stretch or reverse along one line"), fontsize=11)
for ax in (a1, a2):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig2_2_1")

u, w, b = np.array([2.0, 1.0]), np.array([1.0, 3.0]), np.array([7.0, 11.0])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 4.6))
for i in range(-8, 10):
    P, Q = i * u - 8 * w, i * u + 10 * w
    a1.plot([P[0], Q[0]], [P[1], Q[1]], color=BLUE, lw=0.6, alpha=0.4)
    P, Q = -8 * u + i * w, 10 * u + i * w
    a1.plot([P[0], Q[0]], [P[1], Q[1]], color=GREEN, lw=0.6, alpha=0.4)
arrow(a1, 2 * u, BLUE, None, lw=2.2)
arrow(a1, 3 * w, GREEN, None, start=2 * u, lw=2.2)
arrow(a1, b, RED, None, lw=1.6)
arrow(a1, u, BLUE, None, lw=3)
arrow(a1, w, GREEN, None, lw=3)
a1.text(u[0] + 0.1, u[1] - 0.6, r"$\boldsymbol{u}$", color=BLUE, fontsize=13)
a1.text(w[0] - 0.9, w[1], r"$\boldsymbol{w}$", color=GREEN, fontsize=13)
a1.text(b[0] + 0.2, b[1], r"$\boldsymbol{b}=2\boldsymbol{u}+3\boldsymbol{w}$", color=RED, fontsize=12)
a1.set_xlim(-4, 13)
a1.set_ylim(-4, 14)
a1.set_aspect("equal")
a1.axhline(0, color=MUTED, lw=0.5)
a1.axvline(0, color=MUTED, lw=0.5)
a1.set_title(T("不平行的 u、w：组合铺满平面（图中只画整数系数）", "u, w not parallel: combinations fill the plane (integer ones drawn)"), fontsize=10.5)
p, q = np.array([1.0, 2.0]), np.array([-2.0, -4.0])
a2.plot([-4, 4], [-8, 8], color=ACC, lw=2.0, alpha=0.6)
arrow(a2, p, BLUE, None, lw=2.6)
arrow(a2, q, GREEN, None, lw=2.6)
a2.plot(1, 0, "x", color=RED, ms=10, mew=2)
a2.text(1.2, -0.6, T("(1, 0) 凑不出来", "(1, 0) unreachable"), color=RED, fontsize=10)
a2.text(p[0] + 0.2, p[1], r"$(1,2)^{\mathrm{T}}$", color=BLUE, fontsize=12)
a2.text(q[0] + 0.3, q[1] - 0.3, r"$(-2,-4)^{\mathrm{T}}$", color=GREEN, fontsize=12)
a2.set_xlim(-5, 5)
a2.set_ylim(-8, 8)
a2.set_aspect("equal")
a2.axhline(0, color=MUTED, lw=0.5)
a2.axvline(0, color=MUTED, lw=0.5)
a2.set_title(T("平行的两个向量：组合只在一条直线上", "Parallel vectors: combinations stay on a line"), fontsize=10.5)
for ax in (a1, a2):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig2_2_2")
