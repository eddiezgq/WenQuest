"""图 10.1.1：正交补。左：ℝ³ 中的平面 V: x + y + z = 0 与它的正交补——过原点、方向 (1, 1, 1) 的直线；b = (1, 2, 6) 唯一地分解为
v ∈ V 与 w ∈ V⊥ 之和。右：末端在斜面上滑动（侧视）：允许的速度沿斜面（切平面），接触力沿法线，两者正交。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow3, figure, plt, view3

fig = plt.figure(figsize=(11.0, 4.8))
ax = fig.add_subplot(1, 2, 1)
P, _ = view3(-80, 28)
u1 = np.array([1.0, -1, 0]) / np.sqrt(2)
u2 = np.array([1.0, 1, -2]) / np.sqrt(6)
corners = [P(a * u1 + c * u2) for a, c in ((-4, -4), (4, -4), (4, 4), (-4, 4))]
ax.add_patch(plt.Polygon(corners, closed=True, fc=ACC, alpha=0.25, ec=ACC))
n = np.array([1.0, 1, 1]) / np.sqrt(3)
ax.plot(*np.c_[P(-4 * n), P(8.5 * n)], color=GREEN, lw=2, zorder=3)
b, w = np.array([1.0, 2, 6]), np.array([3.0, 3, 3])
v = b - w
ax.plot(*np.c_[P(v), P(b)], color=MUTED, lw=1, ls="--")
ax.plot(*np.c_[P(w), P(b)], color=MUTED, lw=1, ls="--")
arrow3(ax, P, (0, 0, 0), b, BLUE, "b = (1, 2, 6)")
arrow3(ax, P, (0, 0, 0), w, GREEN, "w ∈ V⊥", off=(0.25, -0.35))
arrow3(ax, P, (0, 0, 0), v, RED, "v ∈ V", off=(-0.9, 0.1))
ax.plot(*P(np.zeros(3)), "o", color=INK, ms=4, zorder=8)
lo = min(corners, key=lambda q: q[1])
ax.text(*lo + np.array([0.3, 0.2]), "V", color=INK, fontsize=14)
ax.text(*P(8.6 * n) + np.array([0.1, 0.0]), "V⊥", color=GREEN, fontsize=14)
ax.set_aspect("equal"); ax.axis("off")
ax.set_title(T("平面 V 与它的正交补 V⊥（b = v + w）", "the plane V and its orthogonal complement V⊥ (b = v + w)"), fontsize=11)
ax2 = fig.add_subplot(1, 2, 2)
t = np.radians(20)
tan, nrm = np.array([np.cos(t), np.sin(t)]), np.array([-np.sin(t), np.cos(t)])
ax2.fill([-0.2, 2.4, 2.4], [-0.2 * np.tan(t), 2.4 * np.tan(t), -0.2 * np.tan(t)], color=MUTED, alpha=0.35)
ax2.plot([-0.2, 2.4], [-0.2 * np.tan(t), 2.4 * np.tan(t)], color=INK, lw=1.5)
c = 1.1 * tan
ax2.add_patch(plt.Rectangle(c + 0.02 * nrm - 0.09 * tan, 0.18, 0.5, angle=np.degrees(t), fc=BLUE, alpha=0.35, ec=BLUE))
ax2.annotate("", xy=c + 0.75 * tan + 0.04 * nrm, xytext=c + 0.04 * nrm, arrowprops=dict(arrowstyle="-|>", color=RED, lw=2.2, mutation_scale=16))
ax2.text(*(c + 0.78 * tan + 0.12 * nrm), T("速度 v（切平面内）", "velocity v (tangent)"), color=RED, fontsize=11)
ax2.annotate("", xy=c + 0.02 * nrm, xytext=c + 0.8 * nrm, arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=2.2, mutation_scale=16))
ax2.text(*(c + 0.85 * nrm + np.array([-0.35, 0.02])), T("接触力 f（沿法线）", "contact force f (normal)"), color=GREEN, fontsize=11)
m = 0.1
ax2.plot(*np.c_[c + 0.04 * nrm + m * tan, c + 0.04 * nrm + m * tan + m * nrm, c + 0.04 * nrm + m * nrm], color=INK, lw=1)
ax2.set_aspect("equal"); ax2.set_xlim(-0.3, 2.5); ax2.set_ylim(-0.3, 1.6); ax2.axis("off")
ax2.set_title(T("接触：速度 ⊥ 力，功率 f·v = 0", "contact: velocity ⊥ force, power f·v = 0"), fontsize=11)
figure(fig, "fig10_1_1")
