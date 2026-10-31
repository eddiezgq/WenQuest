"""图 15.6.1：直立双连杆的稳定性（程序 15.6.1）。总势能 V(θ₁, θ₂)（弹簧 + 重力）在 θ = 0 附近的等值线。
(a) k₁ = 20、k₂ = 5 N·m/rad：H 正定，θ = 0 是极小点（碗底），稳定；
(b) k₁ = 9.5、k₂ = 5：H 的两个对角元都正，但 det H < 0，θ = 0 是鞍点，沿红色箭头（H 的负特征值的特征向量）方向势能下降，臂会倒下。
(c) 示意：直立的两连杆臂与关节扭簧。"""
import numpy as np

import _arm2m as A2
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig = plt.figure(figsize=(12.0, 4.2))
gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 0.55])
u = np.radians(np.linspace(-30, 30, 241))
X, Y = np.meshgrid(u, u)
G = A2.gravity_hessian()
for i, (k1, title) in enumerate(((20.0, T("(a) k₁ = 20：极小点，稳定", "(a) k₁ = 20: minimum, stable")),
                                 (9.5, T("(b) k₁ = 9.5：鞍点，不稳定", "(b) k₁ = 9.5: saddle, unstable")))):
    ax = fig.add_subplot(gs[0, i])
    Z = A2.potential(X, Y, k1, 5.0)
    lv = np.linspace(-0.6, 1.2, 19) if i == 0 else np.linspace(-0.25, 0.4, 14)
    cs = ax.contour(np.degrees(X), np.degrees(Y), Z, levels=lv, cmap="coolwarm", linewidths=1.1)
    ax.contour(np.degrees(X), np.degrees(Y), Z, levels=[0], colors=[INK], linewidths=1.6)
    w, V = np.linalg.eigh(np.diag([k1, 5.0]) - G)
    for j in range(2):
        v = V[:, j] * np.sign(V[0, j] if abs(V[0, j]) > 1e-9 else 1)
        col = RED if w[j] < 0 else GREEN
        ax.annotate("", xy=22 * v, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=col, lw=2))
        ax.text(*(24 * v + [0.5, 1.0]), f"λ = {w[j]:.2f}", color=col, fontsize=9)
    ax.plot(0, 0, "o", color=INK, ms=5)
    ax.set_aspect("equal")
    ax.set_xlabel(T("θ₁ / °", "θ₁ / °")); ax.set_ylabel(T("θ₂ / °", "θ₂ / °"))
    ax.set_title(title, fontsize=11)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
ax = fig.add_subplot(gs[0, 2])
th = np.radians([12, 15])
p0 = np.zeros(2)
p1 = A2.L1 * np.array([np.sin(th[0]), np.cos(th[0])])
p2 = p1 + A2.L2 * np.array([np.sin(th.sum()), np.cos(th.sum())])
ax.plot([0, 0], [0, 0.75], color=MUTED, lw=0.8, ls=":")
ax.plot([p1[0], p1[0] + 0.3 * np.sin(th[0])], [p1[1], p1[1] + 0.3 * np.cos(th[0])], color=MUTED, lw=0.8, ls=":")
ax.plot(*np.array([p0, p1]).T, color=BLUE, lw=7, solid_capstyle="round")
ax.plot(*np.array([p1, p2]).T, color=GREEN, lw=5, solid_capstyle="round")
for p, r in ((p0, 0.035), (p1, 0.028)):
    t = np.linspace(0.3, 2 * np.pi * 1.6, 120)
    rr = r * (1 + 0.12 * t)
    ax.plot(p[0] + rr * np.cos(t), p[1] + rr * np.sin(t), color=ACC, lw=1.2)
ax.plot([-0.12, 0.12], [-0.02, -0.02], color=INK, lw=2)
ax.text(0.04, 0.20, "θ₁", fontsize=10, color=INK)
ax.text(p1[0] + 0.06, p1[1] + 0.12, "θ₂", fontsize=10, color=INK)
ax.text(-0.17, -0.1, T("扭簧 k₁、k₂", "springs k₁, k₂"), fontsize=9, color=ACC)
ax.annotate("", xy=(p2[0], p2[1] - 0.12), xytext=p2, arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.2))
ax.text(p2[0] + 0.02, p2[1] - 0.12, "g", color=RED, fontsize=10)
ax.set_aspect("equal"); ax.set_xlim(-0.2, 0.35); ax.set_ylim(-0.15, 0.8); ax.axis("off")
ax.set_title(T("(c) 直立的两连杆", "(c) Upright two-link arm"), fontsize=11)
fig.tight_layout()
figure(fig, "fig15_6_1")
