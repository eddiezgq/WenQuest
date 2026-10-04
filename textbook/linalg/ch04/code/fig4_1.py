"""图 4.1.1：Ax 是 A 的各列以 x 的分量为系数的线性组合（A 为 2×3，x = (2, 1, −1)ᵀ）。
图 4.1.2：线性映射由基向量的像确定——转 30°、关于 y = x 反射、向 x 轴投影，红、绿箭头是 e₁、e₂ 的像（矩阵的两列）。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow, figure, plt

A = np.array([[1.0, 2.0, 0.0], [3.0, -1.0, 4.0]])
x = np.array([2.0, 1.0, -1.0])
fig, ax = plt.subplots(figsize=(5.6, 4.6))
p = np.zeros(2)
for j, col, name in ((0, BLUE, r"$2\boldsymbol{a}_1$"), (1, GREEN, r"$1\boldsymbol{a}_2$"), (2, ACC, r"$-1\boldsymbol{a}_3$")):
    v = x[j] * A[:, j]
    arrow(ax, v, col, None, start=p, lw=2.4)
    m = p + v / 2
    ax.text(m[0] + 0.15, m[1], name, color=col, fontsize=13)
    p = p + v
arrow(ax, A @ x, RED, None, lw=2.0)
ax.text(4.15, 0.6, r"$A\boldsymbol{x}=(4,1)^{\mathrm{T}}$", color=RED, fontsize=13)
for j, col in ((0, BLUE), (1, GREEN), (2, ACC)):
    arrow(ax, A[:, j], col, None, lw=1.0)
ax.text(0.6, 3.2, r"$\boldsymbol{a}_1$", color=BLUE, fontsize=11)
ax.text(2.1, -1.1, r"$\boldsymbol{a}_2$", color=GREEN, fontsize=11)
ax.text(-0.5, 3.6, r"$\boldsymbol{a}_3$", color=ACC, fontsize=11)
ax.set_xlim(-1, 6)
ax.set_ylim(-1.6, 8)
ax.set_aspect("equal")
ax.axhline(0, color=MUTED, lw=0.6)
ax.axvline(0, color=MUTED, lw=0.6)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig4_1_1")

t = math.radians(30)
mats = [(np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]]), T("转 30°", "rotate 30°")),
        (np.array([[0.0, 1.0], [1.0, 0.0]]), T("关于 y = x 反射", "reflect in y = x")),
        (np.array([[1.0, 0.0], [0.0, 0.0]]), T("向 x 轴投影", "project onto the x axis"))]
fig, axs = plt.subplots(1, 3, figsize=(10.6, 3.8))
flag = np.array([[0.2, 0.2], [0.9, 0.2], [0.9, 0.45], [0.55, 0.45], [0.55, 0.7], [0.2, 0.7], [0.2, 0.2]]).T
for ax, (M, name) in zip(axs, mats):
    ax.fill(flag[0], flag[1], color=MUTED, alpha=0.25)
    F = M @ flag
    ax.fill(F[0], F[1], color=ACC, alpha=0.55)
    arrow(ax, M[:, 0], RED, None, lw=2.4)
    arrow(ax, M[:, 1], GREEN, None, lw=2.4)
    ax.set_xlim(-1.2, 1.4)
    ax.set_ylim(-1.0, 1.4)
    ax.set_aspect("equal")
    ax.axhline(0, color=MUTED, lw=0.6)
    ax.axvline(0, color=MUTED, lw=0.6)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(name, fontsize=11)
fig.tight_layout()
figure(fig, "fig4_1_2")
