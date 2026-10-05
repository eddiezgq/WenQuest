"""图 9.7.1：雅可比矩阵的对偶。两连杆臂（l1 = 0.4 m，l2 = 0.3 m，θ = (30°, 45°)）末端托住 2 kg 的工件，受力 f = (0, −19.62) N；
关节力矩 τ = Jᵀf。每个关节的力矩等于力乘以该关节到力作用线的水平距离（虚线）。"""
import numpy as np
from matplotlib.patches import FancyArrowPatch

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt

l1, l2 = 0.4, 0.3
t1, t2 = np.radians(30), np.radians(45)
p0 = np.zeros(2)
p1 = l1 * np.array([np.cos(t1), np.sin(t1)])
p2 = p1 + l2 * np.array([np.cos(t1 + t2), np.sin(t1 + t2)])
J = np.array([[-p2[1], -(p2 - p1)[1]], [p2[0], (p2 - p1)[0]]])
F = np.array([0.0, -19.62])
tau = J.T @ F
fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.plot(*np.c_[p0, p1, p2], color=INK, lw=6, solid_capstyle="round")
for p in (p0, p1):
    ax.add_patch(plt.Circle(p, 0.018, fc="white", ec=INK, lw=2, zorder=5))
ax.add_patch(plt.Rectangle(p2 + np.array([-0.04, -0.005]), 0.08, 0.05, fc=BLUE, alpha=0.5, ec=BLUE, zorder=4))
ax.annotate("", xy=p2 + np.array([0, -0.2]), xytext=p2, arrowprops=dict(arrowstyle="-|>", color=RED, lw=2.4, mutation_scale=18))
ax.text(p2[0] + 0.02, p2[1] - 0.16, "f = (0, −19.62) N", color=RED, fontsize=11)
for p, x, lab, val, dy in ((p0, p2[0], "τ₁", tau[0], -0.09), (p1, p2[0], "τ₂", tau[1], -0.05)):
    ax.plot([p[0], x], [p[1] + dy, p[1] + dy], color=MUTED, lw=1, ls="--")
    ax.plot([x, x], [p[1] + dy, p2[1] - 0.25], color=MUTED, lw=0.6, ls=":")
    arc = FancyArrowPatch(p + np.array([0.06, 0.05]), p + np.array([0.06, -0.05]), connectionstyle="arc3,rad=-0.8",
                          arrowstyle="-|>", mutation_scale=14, color=GREEN, lw=2)
    ax.add_patch(arc)
    ax.text(p[0] - 0.02, p[1] + 0.07, f"{lab} = {val:.2f} N·m".replace("-", "−"), color=GREEN, fontsize=11, ha="right")
ax.plot([-0.1, 0.1], [-0.02, -0.02], color=INK, lw=2)
ax.set_aspect("equal")
ax.set_xlim(-0.35, 0.75)
ax.set_ylim(-0.25, 0.6)
ax.axis("off")
ax.set_title(T("末端的力 f 经 Jᵀ 变成等效关节力矩 τ", "Jᵀ turns the tool force f into equivalent joint torques τ"), fontsize=12, color=INK)
figure(fig, "fig9_7_1")
