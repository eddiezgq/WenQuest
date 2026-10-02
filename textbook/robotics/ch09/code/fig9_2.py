"""9.2 节的示意图。

图 9.2.1：相关系数不同的三组散点：独立、共用电源的两个传感器（ρ = 0.36）、2R 臂末端的 x 与 y。
图 9.2.2：不确定性椭圆：协方差矩阵的特征向量给出主轴方向，特征值的平方根给出半轴长；c = 1、2 与 95% 椭圆。
图 9.2.3：2R 臂两个形态下末端的不确定性椭圆（放大 100 倍）与蒙特卡洛点。
图 9.2.4：关节角标准差 8° 时，线性化失效：蒙特卡洛点弯成香蕉形，均值偏离 f(μ)。
"""
import math

import numpy as np

from _prob import ellipse_pts, fk2, jac2, L2R
from bookout import COLORS as C, T, figure, style

plt = style()
d = math.radians
rng = np.random.default_rng(9021)
c95 = math.sqrt(-2 * math.log(0.05))


def clean(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)


# ---------------------------------------------------------------- 图 9.2.1
n = 800
fig, axs = plt.subplots(1, 3, figsize=(9.6, 3.3))
a = rng.standard_normal(n) * 0.1
b = rng.standard_normal(n) * 0.1
S = 0.06 * rng.standard_normal(n)
X = S + 0.08 * rng.standard_normal(n)
Y = S + 0.08 * rng.standard_normal(n)
sth = d(0.1)
th = np.array([d(30), d(60)])
P = (fk2(th[:, None] + sth * rng.standard_normal((2, n))) - fk2(th)[:, None]) * 1000
sets = [(a, b, T("两个独立的传感器", "two independent sensors"), "N", 0.4),
        (X, Y, T("共用电源的两个传感器", "two sensors on one supply"), "N", 0.4),
        (P[0], P[1], T("2R 臂末端的 x、y 偏差", "2R arm tip: x and y errors"), "mm", 4.5)]
for ax, (u, v, title, unit, lim) in zip(axs, sets):
    ax.scatter(u, v, s=4, color=C["z"], alpha=0.45, lw=0)
    r = np.corrcoef(u, v)[0, 1]
    ax.set_title(title, fontsize=10)
    ax.text(0.04, 0.93, rf"$\rho \approx {r:.2f}$", transform=ax.transAxes, fontsize=11)
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_aspect("equal")
    ax.set_xlabel(T(f"偏差 1 / {unit}", f"error 1 / {unit}") if unit == "N" else f"$\\delta x$ / mm", fontsize=9)
    ax.set_ylabel(T(f"偏差 2 / {unit}", f"error 2 / {unit}") if unit == "N" else f"$\\delta y$ / mm", fontsize=9)
    ax.tick_params(labelsize=8)
    clean(ax)
fig.tight_layout()
figure(fig, "fig9_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 9.2.2 不确定性椭圆（算例 9.2.3 形态 A，单位 mm）
J = jac2(th)
Sp = J @ np.diag([sth ** 2] * 2) @ J.T * 1e6
lam, V = np.linalg.eigh(Sp)
pts = (fk2(th[:, None] + sth * rng.standard_normal((2, 1500))) - fk2(th)[:, None]) * 1000
fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.scatter(pts[0], pts[1], s=3, color=C["muted"], alpha=0.5, lw=0)
handles = []
for c, ls, lab in ((1, "-", "$c = 1$"), (2, "--", "$c = 2$"), (c95, ":", T("95% 椭圆（c = 2.45）", "95% ellipse (c = 2.45)"))):
    E = ellipse_pts(Sp, c=c)
    h, = ax.plot(E[0], E[1], color=C["z"], lw=1.5, ls=ls, label=lab)
    handles.append(h)
ax.legend(handles=handles, loc="lower left", fontsize=9, frameon=False)
for i, col, name, pos in ((1, C["x"], r"$\sqrt{\lambda_1}\,v_1$", (1.55, -0.95)), (0, C["accent"], r"$\sqrt{\lambda_2}\,v_2$", (0.55, 0.95))):
    v = V[:, i] * math.sqrt(lam[i])
    if v[0] < 0:
        v = -v
    ax.annotate("", xy=v, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.8, shrinkA=0, shrinkB=0))
    ax.annotate(name, xy=v, xytext=pos, color=col, fontsize=12, arrowprops=dict(arrowstyle="-", color=col, lw=0.7),
                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.9))
ax.set_aspect("equal")
ax.set_xlim(-4.6, 4.6)
ax.set_ylim(-2.4, 2.4)
ax.axhline(0, color=C["muted"], lw=0.5)
ax.axvline(0, color=C["muted"], lw=0.5)
ax.set_xlabel(r"$\delta x$ / mm")
ax.set_ylabel(r"$\delta y$ / mm")
clean(ax)
figure(fig, "fig9_2_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 9.2.3 两个形态的不确定性椭圆（放大 100 倍）
mag = 100
fig, axs = plt.subplots(1, 2, figsize=(9.4, 4.4))
for ax, (t1, t2), title in zip(axs, ((30, 60), (30, 10)),
                               (T("θ = (30°, 60°)", "θ = (30°, 60°)"), T("θ = (30°, 10°)，接近伸直", "θ = (30°, 10°), nearly straight"))):
    t = np.array([d(t1), d(t2)])
    j = np.array([L2R[0] * math.cos(t[0]), L2R[0] * math.sin(t[0])])
    e = fk2(t)
    ax.plot([0, j[0], e[0]], [0, j[1], e[1]], color=C["accent"], lw=6, solid_capstyle="round")
    for q in ((0, 0), j):
        ax.plot(*q, "o", ms=9, mfc="white", mec=C["ink"], mew=1.5)
    ax.plot([-0.08, 0.08], [-0.03, -0.03], color=C["ink"], lw=3)
    Jt = jac2(t)
    Sp = Jt @ np.diag([sth ** 2] * 2) @ Jt.T
    cl = fk2(t[:, None] + sth * rng.standard_normal((2, 800)))
    cl = e[:, None] + mag * (cl - e[:, None])
    ax.scatter(cl[0], cl[1], s=2.5, color=C["z"], alpha=0.35, lw=0)
    E = ellipse_pts(Sp * mag ** 2, center=e, c=c95)
    ax.plot(E[0], E[1], color=C["z"], lw=1.6)
    ax.plot(*e, "o", ms=3, color=C["ink"])
    ax.text(0.02, 1.15, title, fontsize=10)
    ax.set_aspect("equal")
    ax.set_xlim(-0.15, 1.15)
    ax.set_ylim(-0.12, 1.2)
    ax.axis("off")
fig.text(0.5, 0.01, T("蓝点：关节角各加标准差 0.1° 的随机误差后的末端；蓝线：95% 不确定性椭圆。均放大 100 倍",
                            "blue dots: tip with 0.1° random errors on each joint; blue line: 95% uncertainty ellipse; both magnified ×100"),
            fontsize=8.5, color=C["muted"], ha="center")
fig.tight_layout(rect=(0, 0.04, 1, 1))
figure(fig, "fig9_2_3")
plt.close(fig)

# ---------------------------------------------------------------- 图 9.2.4 线性化失效（关节角标准差 8°）
sb = d(8)
cl = fk2(th[:, None] + sb * rng.standard_normal((2, 4000)))
e = fk2(th)
Jt = jac2(th)
Sp = Jt @ np.diag([sb ** 2] * 2) @ Jt.T
fig, ax = plt.subplots(figsize=(6.2, 4.6))
ax.scatter(cl[0], cl[1], s=2.5, color=C["muted"], alpha=0.45, lw=0)
E = ellipse_pts(Sp, center=e, c=c95)
ax.plot(E[0], E[1], color=C["z"], lw=1.6)
mc = cl.mean(axis=1)
ax.plot(*e, "o", ms=6, color=C["z"])
ax.plot(*mc, "s", ms=6, color=C["x"])
ax.annotate(T("f(μ)：关节角取均值时的末端", "f(μ): tip at the mean joint angles"), xy=e, xytext=(0.42, 0.72),
            fontsize=9, color=C["z"], arrowprops=dict(arrowstyle="-", color=C["z"], lw=0.8))
ax.annotate(T("末端位置的均值（蒙特卡洛）", "mean tip position (Monte Carlo)"), xy=mc, xytext=(0.06, 0.44),
            fontsize=9, color=C["x"], arrowprops=dict(arrowstyle="-", color=C["x"], lw=0.8))
ax.text(0.645, 0.50, T("线性化的\n95% 椭圆", "linearized\n95% ellipse"), fontsize=9, color=C["z"])
# 以基座为圆心的圆弧：末端与基座的距离只由 θ2 决定
r = np.linalg.norm(e)
ang = np.linspace(math.atan2(e[1], e[0]) - 0.6, math.atan2(e[1], e[0]) + 0.6, 100)
ax.plot(r * np.cos(ang), r * np.sin(ang), color=C["accent"], lw=0.9, ls="--")
ax.text(-0.02, 0.73, T("以基座为圆心的圆弧（虚线）", "arc about the base (dashed)"), fontsize=9, color=C["accent"])
ax.set_aspect("equal")
ax.set_xlim(-0.06, 0.78)
ax.set_ylim(0.28, 0.80)
ax.set_xlabel("$x$ / m")
ax.set_ylabel("$y$ / m")
clean(ax)
figure(fig, "fig9_2_4")
plt.close(fig)
