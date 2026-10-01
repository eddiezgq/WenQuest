"""4.1 节的示意图。

图 4.1.1：零件绕 O 转过 θ，角点 P 沿圆弧到 P′；标出 r、φ、θ。
图 4.1.2：坐标轴的单位矢量转过 θ 后，在原坐标系中的分量正是旋转矩阵的两列。
"""
import math

import numpy as np

from bookout import COLORS, figure, style

plt = style()
C = COLORS


def arrow(ax, p, q, color, lw=1.6, z=3):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0,
                                                    mutation_scale=12), zorder=z)


def arc(ax, r, a0, a1, color, lw=1.0, ls="-", n=60):
    t = np.linspace(a0, a1, n)
    ax.plot(r * np.cos(t), r * np.sin(t), color=color, lw=lw, ls=ls)


# ---------------------------------------------------------------- 图 4.1.1
x, y = 0.2, 0.1
th = math.radians(30)
r, phi = math.hypot(x, y), math.atan2(y, x)
xp, yp = r * math.cos(phi + th), r * math.sin(phi + th)
part = np.array([[-0.2, -0.1], [0.2, -0.1], [0.2, 0.1], [-0.2, 0.1], [-0.2, -0.1]])   # 0.4 m × 0.2 m，中心在 O
R = np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])

fig, ax = plt.subplots(figsize=(5.2, 4.0))
ax.set_aspect("equal")
ax.axis("off")
arrow(ax, (-0.32, 0), (0.33, 0), C["x"], 1.2)
arrow(ax, (0, -0.2), (0, 0.3), C["y"], 1.2)
ax.text(0.335, -0.018, "$x$", color=C["x"], fontsize=13)
ax.text(0.012, 0.3, "$y$", color=C["y"], fontsize=13)
ax.fill(part[:, 0], part[:, 1], color="#d9dee2", alpha=0.55, lw=0)
ax.plot(part[:, 0], part[:, 1], color=C["muted"], lw=0.8, ls="--")
rp = (R @ part.T).T
ax.fill(rp[:, 0], rp[:, 1], color="#f3e2b3", alpha=0.6, lw=0)
ax.plot(rp[:, 0], rp[:, 1], color=C["accent"], lw=1.0)
ax.plot([0, x], [0, y], color=C["ink"], lw=1.1)
ax.plot([0, xp], [0, yp], color=C["ink"], lw=1.1)
arc(ax, r, phi, phi + th, C["accent"], 1.4, "-")
arc(ax, 0.07, 0, phi, C["ink"], 0.9)
arc(ax, 0.11, phi, phi + th, C["accent"], 0.9)
ax.plot([x, xp], [y, yp], "o", color=C["ink"], ms=4, zorder=5)
ax.plot([0], [0], "o", color=C["ink"], ms=3)
ax.text(-0.03, -0.035, "O", fontsize=12)
ax.text(x + 0.008, y - 0.03, "P", fontsize=12)
ax.text(xp - 0.005, yp + 0.012, "P′", fontsize=12)
ax.text(0.08, 0.016, r"$\varphi$", fontsize=12)
mid = phi + th / 2
ax.text(0.125 * math.cos(mid), 0.125 * math.sin(mid), r"$\theta$", fontsize=12, color=C["accent"])
ax.text(0.5 * xp - 0.035, 0.5 * yp + 0.01, "$r$", fontsize=12)
ax.text(-0.33, -0.165, "转动前的零件（虚线）", fontsize=9, color=C["muted"])
ax.text(-0.24, 0.24, "转动后的零件", fontsize=9, color=C["accent"])
ax.set_xlim(-0.33, 0.37)
ax.set_ylim(-0.26, 0.32)
figure(fig, "fig4_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 4.1.2
fig, ax = plt.subplots(figsize=(5.0, 4.2))
ax.set_aspect("equal")
ax.axis("off")
c, s = math.cos(th), math.sin(th)
arrow(ax, (0, 0), (1, 0), C["x"], 1.0)
arrow(ax, (0, 0), (0, 1), C["y"], 1.0)
ax.text(1.03, -0.05, r"$\hat x$", color=C["x"], fontsize=13)
ax.text(-0.09, 1.0, r"$\hat y$", color=C["y"], fontsize=13)
arrow(ax, (0, 0), (c, s), C["x"], 2.0)
arrow(ax, (0, 0), (-s, c), C["y"], 2.0)
ax.text(c + 0.03, s + 0.02, r"$R\hat x=(\cos\theta,\ \sin\theta)^{\mathsf{T}}$", color=C["x"], fontsize=11)
ax.text(-s - 0.62, c + 0.06, r"$R\hat y=(-\sin\theta,\ \cos\theta)^{\mathsf{T}}$", color=C["y"], fontsize=11)
for (px, py), col in (((c, s), C["x"]), ((-s, c), C["y"])):
    ax.plot([px, px], [0, py], color=col, lw=0.8, ls=":")
    ax.plot([0, px], [py, py], color=col, lw=0.8, ls=":")
arc(ax, 0.32, 0, th, C["ink"], 0.9)
arc(ax, 0.32, math.pi / 2, math.pi / 2 + th, C["ink"], 0.9)
ax.text(0.34, 0.07, r"$\theta$", fontsize=12)
ax.text(-0.17, 0.33, r"$\theta$", fontsize=12)
ax.text(c / 2 - 0.08, -0.09, r"$\cos\theta$", fontsize=10, color=C["muted"])
ax.text(c + 0.02, s / 2 - 0.03, r"$\sin\theta$", fontsize=10, color=C["muted"])
ax.text(-0.15, -0.12, "O", fontsize=12)
ax.text(-0.15, -0.32, "旋转矩阵的第 1 列 = 转动后的 x 轴，第 2 列 = 转动后的 y 轴", fontsize=9.5, color=C["ink"])
ax.set_xlim(-0.75, 1.35)
ax.set_ylim(-0.38, 1.15)
figure(fig, "fig4_1_2")
plt.close(fig)
