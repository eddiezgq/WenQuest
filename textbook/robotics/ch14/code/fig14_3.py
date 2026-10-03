"""14.3 节的示意图。

图 14.3.1：(a) 子问题 1：p 绕轴转到 q。p、q 在垂直于轴的同一平面内、到轴的距离相等；u′、v′ 是它们在该平面内
           相对轴心 c 的矢量，转角是 u′ 到 v′ 的角。(b) 子问题 3：p 绕轴转动时走一个圆；以 q 为球心、半径 δ 的球面
           与这个圆一般交于两点，对应两个解。
图 14.3.2：子问题 2：两根轴交于 r。p 绕 ω2 转动走一个圆，q 绕 ω1 反向转动走另一个圆，两圆都在以 r 为球心的球面上；
           它们的交点 c₁、c₂ 就是中间点，对应两组解。
"""
import math

import numpy as np

from _fig14 import C, arrow3d, axes3d, circle3d, equal3d, label3d, line3d
from _ik import rot, sp2, sp3
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 14.3.1
fig = plt.figure(figsize=(9.6, 4.6))
# (a) 子问题 1
_, ax = axes3d(plt, fig=fig, pos=121, elev=20, azim=-60)
w = np.array([0, 0, 1.0])
r = np.zeros(3)
line3d(ax, r, w, -0.2, 1.25, C["ink"], lw=1.6)
arrow3d(ax, r + 1.05 * w, 0.2 * w, C["ink"], lw=1.6)
label3d(ax, r + 1.3 * w, r"$\omega$", fs=12)
label3d(ax, r - 0.05 * w + np.array([0.06, 0, 0]), "r", fs=11)
h, R0 = 0.6, 0.8
cpt = r + h * w
a_p, a_q = math.radians(-20), math.radians(85)
p = cpt + R0 * np.array([math.cos(a_p), math.sin(a_p), 0])
q = cpt + R0 * np.array([math.cos(a_q), math.sin(a_q), 0])
circle3d(ax, cpt, w, R0, C["muted"], lw=0.9, ls=":")
ax.plot(*np.array([cpt, p]).T, color=C["accent"], lw=1.6)
ax.plot(*np.array([cpt, q]).T, color=C["accent"], lw=1.6)
circle3d(ax, cpt, w, 0.35, C["x"], lw=1.4, a0=a_p, a1=a_q, e1=np.array([1.0, 0, 0]))
label3d(ax, cpt + 0.42 * np.array([math.cos(0.55), math.sin(0.55), 0]) + np.array([0, 0, 0.04]), r"$\theta$", C["x"], fs=12)
ax.scatter(*p, color=C["z"], s=26, depthshade=False)
ax.scatter(*q, color=C["x"], s=26, depthshade=False)
ax.scatter(*cpt, color=C["ink"], s=12, depthshade=False)
label3d(ax, p + np.array([0.05, -0.05, 0.03]), "p", C["z"], fs=12)
label3d(ax, q + np.array([0.02, 0.05, 0.04]), "q", C["x"], fs=12)
label3d(ax, cpt + np.array([-0.15, 0.0, 0.05]), "c", fs=11)
label3d(ax, cpt + 0.72 * (p - cpt) + np.array([0.0, -0.1, -0.09]), r"$u'$", C["accent"], fs=11)
label3d(ax, (cpt + q) / 2 + np.array([-0.12, 0.0, 0.02]), r"$v'$", C["accent"], fs=11)
ax.plot(*np.array([r, p]).T, color=C["z"], lw=0.8, ls="--")
ax.plot(*np.array([r, q]).T, color=C["x"], lw=0.8, ls="--")
label3d(ax, r + np.array([-0.8, -0.9, 1.45]), T("(a) 子问题 1", "(a) Subproblem 1"), fs=11)
equal3d(ax, [r - 0.2 * w, r + 1.3 * w, p, q, cpt + np.array([-0.8, -0.8, 0]), cpt + np.array([0.8, 0.8, 0])], pad=0.02, zoom=1.15)
# (b) 子问题 3
_, ax = axes3d(plt, fig=fig, pos=122, elev=20, azim=-60)
line3d(ax, r, w, -0.2, 1.25, C["ink"], lw=1.6)
arrow3d(ax, r + 1.05 * w, 0.2 * w, C["ink"], lw=1.6)
label3d(ax, r + 1.3 * w, r"$\omega$", fs=12)
p0 = cpt + R0 * np.array([math.cos(math.radians(215)), math.sin(math.radians(215)), 0])
qb = np.array([1.25, 0.9, 0.1])
delta = 1.35
circle3d(ax, cpt, w, R0, C["z"], lw=1.4)
sols = sp3(w, r, p0, qb, delta)
pts = [cpt + rot(w, t) @ (p0 - cpt) for t in sols]
ax.scatter(*p0, color=C["z"], s=26, depthshade=False)
label3d(ax, p0 + np.array([0.04, -0.04, 0.04]), "p", C["z"], fs=12)
ax.scatter(*qb, color=C["x"], s=26, depthshade=False)
label3d(ax, qb + np.array([0.04, 0.04, 0.04]), "q", C["x"], fs=12)
for k, pp in enumerate(pts, 1):
    ax.plot(*np.array([qb, pp]).T, color=C["x"], lw=1.2)
    ax.scatter(*pp, color=C["accent"], s=30, depthshade=False)
    label3d(ax, pp + np.array([0.05, 0.02, 0.05]), f"$p_{k}$", C["accent"], fs=12)
mid = (qb + pts[0]) / 2
label3d(ax, mid + np.array([0.0, 0.0, 0.06]), r"$\delta$", C["x"], fs=12)
mid = (qb + pts[1]) / 2
label3d(ax, mid + np.array([0.0, 0.0, -0.12]), r"$\delta$", C["x"], fs=12)
qp = cpt + (qb - cpt) - w * ((qb - cpt) @ w)
ax.plot(*np.array([qb, qp]).T, color=C["muted"], lw=0.8, ls=":")
ax.scatter(*qp, color=C["muted"], s=10, depthshade=False)
label3d(ax, qp + np.array([0.04, 0.0, -0.08]), "q′", C["muted"], fs=11)
label3d(ax, r + np.array([-0.8, -0.9, 1.45]), T("(b) 子问题 3", "(b) Subproblem 3"), fs=11)
equal3d(ax, [r - 0.2 * w, r + 1.3 * w, qb, cpt + np.array([-0.8, -0.8, 0]), cpt + np.array([0.8, 0.8, 0])], pad=0.02, zoom=1.05)
figure(fig, "fig14_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 14.3.2
fig, ax = axes3d(plt, size=(6.2, 5.2), elev=18, azim=-55)
r = np.zeros(3)
w1, w2 = np.array([0, 0, 1.0]), np.array([1.0, 0, 0])
p = np.array([0.35, 0.55, 0.62])
p = p / np.linalg.norm(p)
q = rot(w1, math.radians(70)) @ rot(w2, math.radians(-60)) @ p
sol = sp2(w1, w2, r, p, q)
# 球面（淡色经纬线）
for lat in np.radians([-60, -30, 0, 30, 60]):
    circle3d(ax, np.array([0, 0, math.sin(lat)]), w1, math.cos(lat), "#d5dbe0", lw=0.5)
for lon in np.radians(range(0, 180, 30)):
    circle3d(ax, r, np.array([math.cos(lon), math.sin(lon), 0]), 1.0, "#d5dbe0", lw=0.5)
line3d(ax, r, w1, -1.25, 1.35, C["ink"], lw=1.4)
line3d(ax, r, w2, -1.25, 1.35, C["ink"], lw=1.4)
arrow3d(ax, 1.15 * w1, 0.2 * w1, C["ink"])
arrow3d(ax, 1.15 * w2, 0.2 * w2, C["ink"])
label3d(ax, 1.42 * w1, r"$\omega_1$", fs=12)
label3d(ax, 1.42 * w2 + np.array([0, 0, 0.05]), r"$\omega_2$", fs=12)
cp = w2 * (w2 @ p)
circle3d(ax, cp, w2, float(np.linalg.norm(p - cp)), C["z"], lw=1.6)
cq = w1 * (w1 @ q)
circle3d(ax, cq, w1, float(np.linalg.norm(q - cq)), C["x"], lw=1.6)
ax.scatter(*p, color=C["z"], s=30, depthshade=False)
ax.scatter(*q, color=C["x"], s=30, depthshade=False)
label3d(ax, p + np.array([0.04, 0.04, 0.06]), "p", C["z"], fs=12)
label3d(ax, q + np.array([0.04, 0.04, 0.06]), "q", C["x"], fs=12)
for k, (_, _, c) in enumerate(sol, 1):
    ax.scatter(*c, color=C["accent"], s=40, depthshade=False)
    label3d(ax, c + np.array([0.05, 0.03, 0.06]), f"$c_{k}$", C["accent"], fs=12)
ax.scatter(*r, color=C["ink"], s=14, depthshade=False)
label3d(ax, r + np.array([0.05, -0.12, -0.12]), "r", fs=11)
ax.text2D(0.02, 0.02, T("蓝圆：p 绕 ω₂ 转动的轨迹；红圆：q 绕 ω₁ 转动的轨迹；两圆的交点 c₁、c₂",
                         "blue: p turning about ω₂; red: q turning about ω₁; they meet at c₁ and c₂"), transform=ax.transAxes, fontsize=9, color=C["ink"])
equal3d(ax, [np.array([-1.1, -1.1, -1.1]), np.array([1.1, 1.1, 1.1])], pad=0.0, zoom=1.2)
figure(fig, "fig14_3_2")
plt.close(fig)
