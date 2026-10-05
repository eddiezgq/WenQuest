"""图 14.1.1：对称与不对称。(a) 对称矩阵 [[2, 1], [1, 2]] 把单位圆变成椭圆，两条特征直线（虚线）互相垂直，恰是椭圆的主轴；
(b) 不对称矩阵 [[1, 2], [0, 3]] 的两条特征直线夹角 45°，与椭圆的主轴不重合。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, axes_box, figure, plt

t = np.linspace(0, 2 * np.pi, 400)
C = np.vstack([np.cos(t), np.sin(t)])
fig, axs = plt.subplots(1, 2, figsize=(10.0, 4.6))
for ax, A, title in ((axs[0], np.array([[2.0, 1], [1, 2]]), T("(a) 对称：特征方向互相垂直", "(a) Symmetric: perpendicular eigen-directions")),
                     (axs[1], np.array([[1.0, 2], [0, 3]]), T("(b) 不对称：特征方向夹角 45°", "(b) Not symmetric: eigen-directions 45° apart"))):
    axes_box(ax, 3.6)
    ax.plot(C[0], C[1], color=MUTED, lw=0.8, ls=":")
    E = A @ C
    ax.plot(E[0], E[1], color=ACC, lw=2)
    w, V = np.linalg.eig(A)
    for j, c in zip(range(2), (GREEN, RED)):
        v = V[:, j] / np.linalg.norm(V[:, j])
        ax.plot([-3.5 * v[0], 3.5 * v[0]], [-3.5 * v[1], 3.5 * v[1]], ls="--", color=c, lw=1.2)
        ax.annotate("", xy=w[j] * v, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=c, lw=2.2, mutation_scale=13))
        ax.text(*(w[j] * v + np.array([0.15, -0.35 if j == 0 else 0.1])), f"λ = {w[j].real:.0f}", color=c, fontsize=11)
    ax.set_title(title, fontsize=11)
figure(fig, "fig14_1_1")
