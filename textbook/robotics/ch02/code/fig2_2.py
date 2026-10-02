"""2.2 节的示意图。

图 2.2.1：四种线性变换（转动、剪切、伸缩、反射）作用在方格和单位正方形上；基向量的像就是矩阵的两列，
         单位正方形变成以两列为边的平行四边形，有向面积等于行列式。
图 2.2.2：柔顺手腕：{b} 的两根轴是刚度的两个主方向；沿 x_s 推 1 mm，回复力偏向刚度大的方向；
         同一个变换在 {s} 和 {b} 中的矩阵不同，迹和行列式相同。
"""
import math

import numpy as np

from _la import C, arrow, d, ellipse_pts, rot2
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 2.2.1
cases = [(rot2(d(30)), T("转动 R(30°)", "rotation R(30°)")),
         (np.array([[1.0, 0.5], [0.0, 1.0]]), T("剪切", "shear")),
         (np.array([[1.5, 0.0], [0.0, 0.5]]), T("伸缩", "scaling")),
         (np.array([[1.0, 0.0], [0.0, -1.0]]), T("反射", "reflection"))]
fig, axs = plt.subplots(1, 4, figsize=(9.6, 3.2))
for ax, (A, name) in zip(axs, cases):
    ax.set_aspect("equal")
    ax.axis("off")
    for k in np.arange(-1, 2.01, 0.5):
        for a0, a1 in (((k, -1), (k, 2)), ((-1, k), (2, k))):
            p = A @ np.array([[a0[0], a1[0]], [a0[1], a1[1]]], float)
            ax.plot(p[0], p[1], color="#c7ced3", lw=0.6, zorder=1)
    sq = A @ np.array([[0, 1, 1, 0, 0], [0, 0, 1, 1, 0]], float)
    ax.fill(sq[0], sq[1], color="#f3e2b3", alpha=0.8, zorder=2)
    ax.plot([0, 1, 1, 0, 0], [0, 0, 1, 1, 0], color=C["muted"], lw=0.8, ls="--", zorder=3)
    arrow(ax, (0, 0), A[:, 0], C["x"], 2.0, z=4)
    arrow(ax, (0, 0), A[:, 1], C["y"], 2.0, z=4)
    det = np.linalg.det(A)
    ax.set_xlim(-1.0, 2.0)
    ax.set_ylim(-1.35, 1.9)
    ax.text(-0.95, 1.7, name, fontsize=10.5, color=C["ink"])
    ax.text(-0.95, -1.3, r"$\det = %s$" % (f"{det:.2f}".rstrip("0").rstrip(".")), fontsize=10.5, color=C["ink"])
fig.text(0.02, 0.06, T("虚线：单位正方形；红、绿箭头：基向量的像，即矩阵的第 1、2 列；黄色：单位正方形的像，面积等于 |det|",
                        "dashed: unit square; red and green arrows: images of the basis vectors, i.e. columns 1 and 2; "
                        "yellow: image of the unit square, area |det|"), fontsize=9, color=C["ink"])
figure(fig, "fig2_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 2.2.2
Kb = np.diag([2000.0, 500.0])
R = rot2(d(30))
Ks = R @ Kb @ R.T
fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.set_aspect("equal")
ax.axis("off")
# 手腕（圆盘）与两个主方向
t = np.linspace(0, 2 * math.pi, 100)
ax.fill(0.55 * np.cos(t), 0.55 * np.sin(t), color="#e8ecef", zorder=0)
for k, (col, lab) in enumerate(((C["x"], r"$x_b$:  $k_1$ = 2000 N/m"), (C["y"], r"$y_b$:  $k_2$ = 500 N/m"))):
    u = R[:, k]
    ax.plot([-1.25 * u[0], 1.25 * u[0]], [-1.25 * u[1], 1.25 * u[1]], color=col, lw=0.9, ls="-.", zorder=1)
    ax.text(1.3 * u[0] - (0.15 if k == 0 else 0.55), 1.3 * u[1] + 0.05, lab, color=col, fontsize=11)
arrow(ax, (0, 0), (1.25, 0), C["x"], 1.1)
arrow(ax, (0, 0), (0, 1.25), C["y"], 1.1)
ax.text(1.27, -0.08, r"$x_s$", color=C["x"], fontsize=12)
ax.text(0.04, 1.24, r"$y_s$", color=C["y"], fontsize=12)
# 位移 1 mm 的单位圆 → 力的椭圆（力按 1 N 画成 0.5 单位）
E = ellipse_pts(Ks * 0.001 * 0.5)
ax.plot(E[0], E[1], color=C["accent"], lw=1.1, ls="--")
delta = np.array([1.0, 0.0])
f = Ks @ (delta * 0.001) * 0.5
arrow(ax, (0, 0), delta * 0.5, C["ink"], 2.0)
arrow(ax, (0, 0), f, C["accent"], 2.2)
ax.text(0.24, -0.19, r"$\delta$ = 1 mm", fontsize=10.5, color=C["ink"])
ax.text(f[0] + 0.03, f[1] + 0.03, r"$f = K_s\,\delta$", fontsize=11, color=C["accent"])
ax.text(0.62, 0.05, f"{math.degrees(math.atan2(f[1], f[0])):.1f}°", fontsize=9, color=C["accent"])
ax.text(-1.45, -1.05, T("虚线椭圆：沿各个方向推 1 mm 时回复力的端点", "dashed ellipse: tips of the force for a 1 mm push in every direction"),
        fontsize=9, color=C["accent"])
ax.text(-1.45, -1.23, T("同一刚度：在 {b} 中 diag(2000, 500)，在 {s} 中不是对角阵；迹与行列式相同",
                        "same stiffness: diag(2000, 500) in {b}, not diagonal in {s}; same trace and determinant"),
        fontsize=9, color=C["ink"])
ax.set_xlim(-1.5, 1.6)
ax.set_ylim(-1.3, 1.4)
figure(fig, "fig2_2_2")
plt.close(fig)
