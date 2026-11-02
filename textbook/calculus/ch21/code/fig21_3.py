"""图 21.3.1：四种平衡点的相图（流线）：稳定结点、鞍点、稳定焦点、中心，系数矩阵同表 21.3.1。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

mats = [(np.array([[-2.0, 0], [0, -0.5]]), T("稳定结点", "stable node")), (np.array([[1.0, 0], [0, -1]]), T("鞍点", "saddle")),
        (np.array([[-0.5, 2], [-2, -0.5]]), T("稳定焦点", "stable focus")), (np.array([[0.0, 1], [-4, 0]]), T("中心", "centre"))]
fig, axs = plt.subplots(1, 4, figsize=(12, 3.3))
x = np.linspace(-2, 2, 40)
X, Y = np.meshgrid(x, x)
for ax, (A, name) in zip(axs, mats):
    U = A[0, 0] * X + A[0, 1] * Y
    V = A[1, 0] * X + A[1, 1] * Y
    ax.streamplot(X, Y, U, V, color=BLUE, density=0.9, linewidth=0.9, arrowsize=0.9)
    ev, vec = np.linalg.eig(A)
    if np.all(np.abs(ev.imag) < 1e-12):
        for k in range(2):
            v = vec[:, k].real
            ax.plot([-2.5 * v[0], 2.5 * v[0]], [-2.5 * v[1], 2.5 * v[1]], color=RED, lw=1.5, ls="--")
    ax.plot(0, 0, "o", color=INK)
    ax.set_xlim(-2, 2)
    ax.set_ylim(-2, 2)
    ax.set_aspect("equal")
    ax.set_title(name, fontsize=10)
    ax.set_xticks([])
    ax.set_yticks([])
fig.tight_layout()
figure(fig, "fig21_3_1")
