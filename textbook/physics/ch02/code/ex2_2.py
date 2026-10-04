"""2.2 节的计算：

算例 2.2.1  水平关节（SCARA）机器人的两个连杆在水平面内：大臂长 l₁ = 0.30 m，小臂长 l₂ = 0.25 m；大臂与 x 轴成 30°，
            小臂相对大臂再转 45°。末端的位置矢量 r = a + b：用三角形法则作图，再用余弦定理求大小、正弦定理求方向
            （图 2.2.1）。程序还用分量相加核对（2.3 节）。
算例 2.2.2  零件在 Q 点，r_Q = (0.45, 0.30) m。夹爪要走的位移是 r_Q − r（矢量减法，图 2.2.2）。
算例 2.2.3  减速器壳体 35 kg，用两根吊索吊起静止，吊索与竖直方向分别成 30° 和 45°。把重力的反向矢量沿两根吊索的方向
            分解，求两根吊索的拉力（正弦定理，图 2.2.3）；并用分量核对（第 14 章把它作为静力平衡的例子）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

rad = math.radians
# ---- 算例 2.2.1
l1, l2, t1, t2 = 0.30, 0.25, 30.0, 45.0
a = l1 * np.array([math.cos(rad(t1)), math.sin(rad(t1))])
b = l2 * np.array([math.cos(rad(t1 + t2)), math.sin(rad(t1 + t2))])
r = a + b
# 三角形 OAB 中，a 与 b 首尾相接，两边夹角为 180° − θ₂
rmag = math.sqrt(l1 ** 2 + l2 ** 2 + 2 * l1 * l2 * math.cos(rad(t2)))
beta = math.degrees(math.asin(l2 * math.sin(rad(180 - t2)) / rmag))     # r 与 a 的夹角（正弦定理）
rang = t1 + beta
assert abs(rmag - np.linalg.norm(r)) < 1e-12 and abs(rang - math.degrees(math.atan2(r[1], r[0]))) < 1e-9
rmax, rmin = l1 + l2, l1 - l2
out(l1=l1, l2=l2, t1=t1, t2=t2, rmag=rmag, beta=beta, rang=rang, rx=r[0], ry=r[1], rmax=rmax, rmin=rmin)

# ---- 算例 2.2.2
rQ = np.array([0.45, 0.30])
dvec = rQ - r
dmag = float(np.linalg.norm(dvec))
out(rQ=f"(0.45, 0.30)", dx=dvec[0], dy=dvec[1], dmag=dmag, dang=math.degrees(math.atan2(dvec[1], dvec[0])))

# ---- 算例 2.2.3：吊索拉力
m, al, be = 35.0, 30.0, 45.0
W = m * g
# T1 + T2 = −W（竖直向上、大小 W）；三角形中 T1、T2、W 的对角分别为 β、α、180° − α − β
T1 = W * math.sin(rad(be)) / math.sin(rad(al + be))
T2 = W * math.sin(rad(al)) / math.sin(rad(al + be))
# 分量核对：T1 指向左上（与竖直成 α），T2 指向右上（与竖直成 β）
Fx = -T1 * math.sin(rad(al)) + T2 * math.sin(rad(be))
Fy = T1 * math.cos(rad(al)) + T2 * math.cos(rad(be)) - W
assert abs(Fx) < 1e-9 and abs(Fy) < 1e-9
out(m=m, W=W, al=al, be=be, T1=T1, T2=T2, Tsum=T1 + T2)

plt = style()
# ---- 图 2.2.1：三角形法则与平行四边形法则
fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.3))
O = np.zeros(2)
for ax, mode in zip(axs, ("tri", "para")):
    if mode == "tri":
        ax.plot([0, a[0]], [0, a[1]], color="#bfc7cc", lw=9, solid_capstyle="round", zorder=1)
        ax.plot([a[0], r[0]], [a[1], r[1]], color="#bfc7cc", lw=7, solid_capstyle="round", zorder=1)
        ax.plot(0, 0, "s", color=d.MUTED, ms=12, zorder=2)
        d.arrow(ax, O, a, d.VA, label=r"$\boldsymbol{a}$", off=(-0.02, 0.035))
        d.arrow(ax, a, r, d.VB, label=r"$\boldsymbol{b}$", off=(0.035, 0.0))
        d.arrow(ax, O, r, d.VR, label=r"$\boldsymbol{r}=\boldsymbol{a}+\boldsymbol{b}$", off=(-0.08, 0.04), fs=10)
        ax.set_title(T("三角形法则：首尾相接（SCARA 的两个连杆）", "triangle rule: head to tail (SCARA links)"), fontsize=9)
    else:
        d.arrow(ax, O, a, d.VA, label=r"$\boldsymbol{a}$", off=(0.01, -0.03))
        d.arrow(ax, O, b, d.VB, label=r"$\boldsymbol{b}$", off=(-0.03, 0.0))
        ax.plot([a[0], r[0]], [a[1], r[1]], color=d.VB, lw=1, ls="--")
        ax.plot([b[0], r[0]], [b[1], r[1]], color=d.VA, lw=1, ls="--")
        d.arrow(ax, O, r, d.VR, label=r"$\boldsymbol{a}+\boldsymbol{b}=\boldsymbol{b}+\boldsymbol{a}$", off=(0.09, -0.01), fs=10)
        ax.set_title(T("平行四边形法则：从同一点出发", "parallelogram rule: from one point"), fontsize=9)
    ax.set_xlim(-0.12, 0.55); ax.set_ylim(-0.05, 0.48); ax.set_aspect("equal")
    ax.set_xlabel("x / m"); d.spines(ax)
axs[0].set_ylabel("y / m")
figure(fig, "fig2_2_1")

# ---- 图 2.2.2：减法——从夹爪指向零件
fig, ax = plt.subplots(figsize=(4.4, 3.2))
d.arrow(ax, O, r, d.VA, label=r"$\boldsymbol{r}$", off=(0.03, -0.03))
d.arrow(ax, O, rQ, d.VB, label=r"$\boldsymbol{r}_Q$", off=(0.04, -0.035))
d.arrow(ax, r, rQ, d.VR, label=r"$\boldsymbol{r}_Q-\boldsymbol{r}$", off=(0.02, 0.04))
ax.plot(*r, "o", color=d.INK, ms=4); ax.text(r[0] - 0.06, r[1] + 0.015, T("夹爪", "gripper"), fontsize=9)
ax.plot(*rQ, "o", color=d.INK, ms=4); ax.text(rQ[0] + 0.01, rQ[1] + 0.015, T("零件 Q", "part Q"), fontsize=9)
ax.plot(0, 0, "s", color=d.MUTED, ms=10)
ax.set_xlim(-0.05, 0.55); ax.set_ylim(-0.05, 0.48); ax.set_aspect("equal"); ax.set_xlabel("x / m"); ax.set_ylabel("y / m"); d.spines(ax)
figure(fig, "fig2_2_2")

# ---- 图 2.2.3：沿两根吊索的方向分解
fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.5), gridspec_kw={"width_ratios": [1, 1.05]})
ax = axs[0]
H = 1.0
P = np.array([0.0, 0.0])
A1 = P + np.array([-math.tan(rad(al)), 1.0]) * H
A2 = P + np.array([math.tan(rad(be)), 1.0]) * H
ax.plot([A1[0] - 0.2, A2[0] + 0.2], [H, H], color=d.INK, lw=3)
ax.plot([P[0], A1[0]], [P[1], A1[1]], color=d.INK, lw=1.4)
ax.plot([P[0], A2[0]], [P[1], A2[1]], color=d.INK, lw=1.4)
ax.add_patch(plt.Rectangle((-0.28, -0.42), 0.56, 0.38, fc="#c8d0d4", ec=d.INK))
ax.text(0, -0.24, T("壳体", "housing"), ha="center", fontsize=9)
ax.plot([0, 0], [0, 0.55], color=d.MUTED, lw=0.8, ls=":")
ax.text(-0.17, 0.42, f"{al:.0f}°", fontsize=9); ax.text(0.05, 0.42, f"{be:.0f}°", fontsize=9)
ax.set_xlim(-1.0, 1.25); ax.set_ylim(-0.5, 1.12); ax.set_aspect("equal"); d.clean(ax)
ax.set_title(T("两根吊索吊起壳体", "two slings hold the housing"), fontsize=9)
ax = axs[1]
s = 1 / W * 1.0
u1 = np.array([-math.sin(rad(al)), math.cos(rad(al))])
u2 = np.array([math.sin(rad(be)), math.cos(rad(be))])
F1, F2 = T1 * s * u1, T2 * s * u2
d.arrow(ax, O, np.array([0, 1.0]), d.VR, label=r"$-\boldsymbol{W}$", off=(0.09, 0.15))
d.arrow(ax, O, F1, d.VA, label=r"$\boldsymbol{T}_1$", off=(-0.07, 0.0))
d.arrow(ax, O, F2, d.VB, label=r"$\boldsymbol{T}_2$", off=(0.08, -0.02))
ax.plot([F1[0], 0], [F1[1], 1.0], color=d.VB, lw=1, ls="--")
ax.plot([F2[0], 0], [F2[1], 1.0], color=d.VA, lw=1, ls="--")
ax.set_xlim(-0.6, 0.6); ax.set_ylim(-0.05, 1.1); ax.set_aspect("equal"); d.clean(ax)
ax.set_title(T(r"$-\boldsymbol{W}$ 沿两根吊索的方向分解", r"$-\boldsymbol{W}$ resolved along the slings"), fontsize=9)
figure(fig, "fig2_2_3")
