"""2.3 节的示意图。

图 2.3.1：单位圆上的一圈向量 x（灰）和它们的像 Ax（彩色，从 x 的端点画到 Ax 的端点）。
         左：实测刚度矩阵 K（对称），两个特征方向互相垂直；右：橡皮膜的拉伸 A（不对称），两个特征方向不垂直。
         沿特征方向的向量只伸缩、不转向。
"""
import math

import numpy as np

from _la import C, arrow
from bookout import T, figure, style

plt = style()

K = np.array([[1600.0, 650.0], [650.0, 900.0]]) / 1000.0          # 画图时以 1000 N/m 为单位
A = np.array([[1.5, 0.5], [0.0, 1.0]])
fig, axs = plt.subplots(1, 2, figsize=(9.0, 4.4))
for ax, M, title in ((axs[0], K, T("刚度矩阵 K（对称）：特征方向互相垂直", "stiffness K (symmetric): eigen-directions perpendicular")),
                     (axs[1], A, T("橡皮膜的拉伸 A（不对称）：特征方向不垂直", "stretching a rubber sheet, A (not symmetric): not perpendicular"))):
    ax.set_aspect("equal")
    ax.axis("off")
    t = np.linspace(0, 2 * math.pi, 200)
    ax.plot(np.cos(t), np.sin(t), color=C["muted"], lw=0.8, ls="--")
    w, V = np.linalg.eig(M)
    eig_dirs = [math.atan2(v[1], v[0]) for v in V.T]
    for a in np.linspace(0, 2 * math.pi, 24, endpoint=False):
        x = np.array([math.cos(a), math.sin(a)])
        y = M @ x
        ax.plot([0, x[0]], [0, x[1]], color="#c7ced3", lw=0.7)
        if np.linalg.norm(y - x) > 1e-6:
            arrow(ax, x, y, C["accent"], 1.0, ms=8)
    for e, lam in zip(eig_dirs, w.real):
        u = np.array([math.cos(e), math.sin(e)])
        ax.plot([-2.1 * u[0], 2.1 * u[0]], [-2.1 * u[1], 2.1 * u[1]], color=C["x"], lw=0.9, ls="-.")
        for sgn in (1, -1):
            arrow(ax, (0, 0), sgn * lam * u, C["x"], 2.4, z=5)
            ax.plot(*(sgn * u), "o", color=C["ink"], ms=3.5, zorder=6)
        lab = 2.15 * u if u[1] >= -1e-9 else -2.15 * u
        ax.text(lab[0] - 0.05, lab[1] + 0.05, r"$\lambda = %.2f$" % lam, fontsize=10, color=C["x"])
    E = M @ np.vstack([np.cos(t), np.sin(t)])
    ax.plot(E[0], E[1], color=C["accent"], lw=0.8)
    ax.set_xlim(-2.4, 2.6)
    ax.set_ylim(-2.2, 2.4)
    ax.text(-2.35, -2.2, title, fontsize=9.5, color=C["ink"])
fig.text(0.02, 0.05, T("灰：单位圆上的向量 x；金色箭头：从 x 的端点指到 Ax 的端点；红：特征方向，x（黑点）变成 λx，不转向、只伸缩（K 以 1000 N/m 为单位）",
                      "grey: unit vectors x; gold arrows: from the tip of x to the tip of Ax; red: eigen-directions, x (black dot) becomes λx, only stretched (K in units of 1000 N/m)"),
         fontsize=9, color=C["ink"])
figure(fig, "fig2_3_1")
plt.close(fig)
