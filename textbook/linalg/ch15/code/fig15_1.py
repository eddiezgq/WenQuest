"""图 15.1.1：二维二次型 z = xᵀAx 的四种形状。A = diag(1, 1)（碗，正定）、diag(1, −1)（马鞍，不定）、
diag(1, 0)（槽，半正定）、diag(−1, −1)（倒扣的碗，负定）。曲面下方画出等值线。"""
import numpy as np

from _fig import BLUE, INK, MUTED, RED, T, figure, plt

cases = [((1, 1), T("(a) 正定：碗", "(a) Positive definite: bowl"), "x² + y²"),
         ((1, -1), T("(b) 不定：马鞍", "(b) Indefinite: saddle"), "x² − y²"),
         ((1, 0), T("(c) 半正定：槽", "(c) Semidefinite: trough"), "x²"),
         ((-1, -1), T("(d) 负定：倒扣的碗", "(d) Negative definite: dome"), "−x² − y²")]
fig = plt.figure(figsize=(12.0, 3.4))
u = np.linspace(-1, 1, 41)
X, Y = np.meshgrid(u, u)
for i, ((a, b), title, formula) in enumerate(cases):
    ax = fig.add_subplot(1, 4, i + 1, projection="3d")
    Z = a * X ** 2 + b * Y ** 2
    ax.plot_surface(X, Y, Z, cmap="coolwarm", vmin=-1.5, vmax=1.5, linewidth=0, antialiased=True, alpha=0.9, rasterized=True)
    ax.contour(X, Y, Z, levels=7, zdir="z", offset=-2.2, colors=MUTED, linewidths=0.7)
    ax.plot([0], [0], [0], "o", color=INK, ms=4)
    ax.set_zlim(-2.2, 2.0)
    ax.set_xticks([-1, 0, 1]); ax.set_yticks([-1, 0, 1]); ax.set_zticks([-2, 0, 2])
    ax.tick_params(labelsize=7, pad=0)
    ax.set_xlabel("x", fontsize=9, labelpad=-6); ax.set_ylabel("y", fontsize=9, labelpad=-6)
    ax.view_init(elev=24, azim=-58)
    ax.set_title(title + "\n" + "z = " + formula, fontsize=10, color=RED if a * b < 0 else (BLUE if a > 0 else INK))
fig.subplots_adjust(left=0.0, right=1.0, wspace=0.02)
fig.set_dpi(200)
figure(fig, "fig15_1_1")
