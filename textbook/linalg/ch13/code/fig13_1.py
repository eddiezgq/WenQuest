"""图 13.1.1：不改变方向的向量。(a) A = [[3, 1], [0, 2]] 把单位圆上的向量 v（细线）变成 Av（箭头）：
一般 Av 与 v 不共线，只有沿 (1, 0) 与 (−1, 1) 的向量被拉长而方向不变；(b) 柔顺腕 K = [[4, 1], [1, 4]] kN/m：
沿 x 推 10 N，位移（蓝）偏向下方；沿两条主轴（虚线）推时位移与力同向。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, arrow, axes_box, figure, plt

A = np.array([[3.0, 1], [0, 2]])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.8))
axes_box(a1, 3.6)
for t in np.radians(np.arange(0, 180, 15)):
    v = np.array([np.cos(t), np.sin(t)]); w = A @ v
    eig = abs(v[0] * w[1] - v[1] * w[0]) < 1e-9
    a1.plot([0, v[0]], [0, v[1]], color=MUTED, lw=0.8)
    a1.annotate("", xy=w, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=(RED if eig else ACC), lw=(2.4 if eig else 1.0), mutation_scale=10))
for d, c, lab in (((1, 0), RED, "λ = 3"), ((-1, 1), GREEN, "λ = 2")):
    d = np.array(d) / np.linalg.norm(d)
    a1.plot([-3.5 * d[0], 3.5 * d[0]], [-3.5 * d[1], 3.5 * d[1]], ls="--", color=c, lw=1)
arrow(a1, A @ np.array([-1, 1]) / np.sqrt(2), GREEN, "λ = 2", offset=(-0.9, 0.1), lw=2.4)
a1.text(2.4, -0.45, "λ = 3", color=RED, fontsize=11)
t = np.linspace(0, 2 * np.pi, 361)
a1.plot(np.cos(t), np.sin(t), color=MUTED, lw=0.6, ls=":")
a1.set_title(T("(a) v（细线）与 Av（箭头）", "(a) v (thin) and Av (arrows)"), fontsize=11)
K = np.array([[4.0, 1], [1, 4]])
axes_box(a2, 3.2)
F = np.array([10.0, 0]); d = np.linalg.solve(K, F)
arrow(a2, F / 4, RED, T("力 F（10 N）", "force F (10 N)"), offset=(-0.6, 0.2))
arrow(a2, d, BLUE, T("位移 d / mm", "deflection d / mm"), offset=(-0.6, -0.45))
for u, c in (((1, 1), GREEN), ((1, -1), ACC)):
    u = np.array(u) / np.sqrt(2)
    a2.plot([-3 * u[0], 3 * u[0]], [-3 * u[1], 3 * u[1]], ls="--", color=c, lw=1)
a2.text(1.3, 1.9, T("主轴：5 kN/m", "axis: 5 kN/m"), color=GREEN, fontsize=10)
a2.text(1.3, -2.1, T("主轴：3 kN/m", "axis: 3 kN/m"), color=ACC, fontsize=10)
a2.set_title(T("(b) 柔顺腕：力与位移的方向", "(b) Compliant wrist: force and deflection"), fontsize=11)
figure(fig, "fig13_1_1")
