"""图 11.1.1：标准正交基下的坐标就是点积。点 p = (0.2, 0.1) 不动，坐标系转 30°：新坐标系的基 q1、q2 是 R 的两列，
p 在新坐标系中的坐标是 (q1·p, q2·p) = Rᵀp，几何上就是 p 向两根新坐标轴的投影。"""
import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, arrow, figure, plt

t = np.radians(30)
q1, q2 = np.array([np.cos(t), np.sin(t)]), np.array([-np.sin(t), np.cos(t)])
p = np.array([0.2, 0.1])
c1, c2 = q1 @ p, q2 @ p
fig, ax = plt.subplots(figsize=(5.6, 4.6))
ax.set_aspect("equal"); ax.set_xlim(-0.14, 0.3); ax.set_ylim(-0.1, 0.29); ax.axis("off")
for e, nm in ((np.array([1.0, 0]), "x"), (np.array([0.0, 1]), "y")):
    ax.annotate("", xy=0.26 * e, xytext=-0.08 * e, arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1))
    ax.text(*(0.27 * e + np.array([0.0, -0.012 if nm == "x" else 0.0])), nm, color=MUTED, fontsize=11)
for q, col, nm in ((q1, RED, "q₁"), (q2, GREEN, "q₂")):
    ax.plot(*np.c_[-0.1 * q, 0.26 * q], color=col, lw=0.8, ls="--")
    arrow(ax, 0.1 * q, col, nm, offset=(0.004, 0.006), lw=2.4)
ax.plot(*p, "o", color=BLUE, ms=7)
ax.text(p[0] + 0.006, p[1] + 0.006, "p", color=BLUE, fontsize=13)
for c, q, col in ((c1, q1, RED), (c2, q2, GREEN)):
    f = c * q
    ax.plot(*np.c_[p, f], color=col, lw=1, ls=":")
    ax.plot(*f, "o", color=col, ms=4)
ax.text(*(c1 * q1 + np.array([0.01, -0.03])), f"q₁·p = {c1:.4f}", color=RED, fontsize=11)
ax.text(*(c2 * q2 + np.array([-0.13, -0.025])), f"q₂·p = {c2:.4f}".replace("-", "−"), color=GREEN, fontsize=11)
ax.set_title(T("坐标系转 30°，点不动：新坐标是 (q₁·p, q₂·p) = Rᵀp", "frame turned 30°, point fixed: new coordinates (q₁·p, q₂·p) = Rᵀp"), fontsize=11)
figure(fig, "fig11_1_1")
