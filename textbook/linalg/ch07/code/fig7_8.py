"""图 7.8.1：ℝ³ 中两个平面 U（z = 0）与 W（x = 0）的和是整个 ℝ³，交是 y 轴：dim(U + W) = 2 + 2 − 1 = 3。"""
import numpy as np

from _fig import BLUE, GREEN, RED, T, figure, plt

fig = plt.figure(figsize=(5.6, 4.8))
ax = fig.add_subplot(projection="3d")
s = np.linspace(-1, 1, 2)
A, B = np.meshgrid(s, s)
ax.plot_surface(A, B, 0 * A, color=BLUE, alpha=0.3, edgecolor="none")
ax.plot_surface(0 * A, A, B, color=GREEN, alpha=0.3, edgecolor="none")
ax.plot([0, 0], [-1.3, 1.3], [0, 0], color=RED, lw=3)
ax.text(0, 1.4, 0, "U ∩ W", color=RED, fontsize=11)
ax.text(1, -1, 0, "U", color=BLUE, fontsize=12)
ax.text(0, -1, 1, "W", color=GREEN, fontsize=12)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_zlabel("z")
ax.view_init(elev=20, azim=-50)
ax.set_title(T("dim(U + W) = 2 + 2 − 1 = 3", "dim(U + W) = 2 + 2 − 1 = 3"), fontsize=11)
fig.tight_layout()
figure(fig, "fig7_8_1")
