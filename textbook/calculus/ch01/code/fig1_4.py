"""图 1.4.1：刘徽割圆——圆内接正 6、12、24 边形；图 1.4.2：祖暅原理——牟合方盖与球在同一高度的截面。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, axs = plt.subplots(1, 3, figsize=(10, 3.6))
for ax, n in zip(axs, (6, 12, 24)):
    t = np.linspace(0, 2 * math.pi, 300)
    ax.plot(np.cos(t), np.sin(t), color=INK, lw=1.2)
    a = np.linspace(0, 2 * math.pi, n + 1)
    ax.fill(np.cos(a), np.sin(a), color=BLUE, alpha=0.15)
    ax.plot(np.cos(a), np.sin(a), color=BLUE, lw=1.4)
    area = n / 2 * math.sin(2 * math.pi / n)
    ax.set_title(T(f"正 {n} 边形：面积 {area:.4f}", f"{n}-gon: area {area:.4f}"), fontsize=11)
    ax.set_aspect("equal")
    ax.axis("off")
fig.tight_layout()
figure(fig, "fig1_4_1")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 4.0))
r, z = 1.0, 0.6
w = math.sqrt(r * r - z * z)
for ax in (a1, a2):
    ax.set_aspect("equal")
    ax.set_xlim(-1.25, 1.25)
    ax.set_ylim(-1.25, 1.25)
    ax.axis("off")
a1.add_patch(plt.Rectangle((-w, -w), 2 * w, 2 * w, fc="#f6d6b8", ec=RED, lw=1.5))
a1.add_patch(plt.Circle((0, 0), w, fc="#d9e6f2", ec=BLUE, lw=1.5))
a1.add_patch(plt.Rectangle((-r, -r), 2 * r, 2 * r, fill=False, ec=MUTED, ls="--"))
a1.text(0, -1.18, T("高 z 处：牟合方盖截面为正方形，球截面为其内切圆", "At height z: square section and its inscribed circle"), ha="center", fontsize=10)
tt = np.linspace(0, 2 * math.pi, 300)
a2.plot(np.cos(tt), np.sin(tt), color=INK)
a2.plot([-w, w], [z, z], color=BLUE, lw=3)
a2.plot([-r, r], [0, 0], color=MUTED, lw=0.6)
a2.text(w + 0.05, z, "$z$", va="center")
a2.text(0, -1.18, T("侧视：两立体的截面积之比处处为 4 : π", "Side view: section areas in ratio 4 : π at every height"), ha="center", fontsize=10)
fig.tight_layout()
figure(fig, "fig1_4_2")
