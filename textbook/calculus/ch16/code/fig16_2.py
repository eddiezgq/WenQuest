"""图 16.2.1：左：牟合方盖（两个互相垂直的圆柱的公共部分）与内切球；右：同一高度 z 处的截面，球是圆，牟合方盖是外切的正方形，
面积之比为 π : 4；立方体减去牟合方盖剩下的截面面积 4z²，与倒置方锥的截面相同（祖暅的做法）。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig = plt.figure(figsize=(11, 4.6))
ax = fig.add_subplot(1, 2, 1, projection="3d")
# 牟合方盖：高度 z 处的截面是边长 2√(1 − z²) 的正方形；画出若干层正方形与四条棱线（x = ±y = ±√(1 − z²)）
for zz in np.linspace(-0.95, 0.95, 13):
    ww = np.sqrt(1 - zz ** 2)
    sq0 = np.array([[-ww, -ww], [ww, -ww], [ww, ww], [-ww, ww], [-ww, -ww]])
    ax.plot(sq0[:, 0], sq0[:, 1], zz, color=ACC, lw=0.9, alpha=0.8)
    tt0 = np.linspace(0, 2 * np.pi, 80)
    ax.plot(ww * np.cos(tt0), ww * np.sin(tt0), zz, color=BLUE, lw=0.8, alpha=0.7)
zs = np.linspace(-1, 1, 101)
ws = np.sqrt(1 - zs ** 2)
for sx in (-1, 1):
    for sy in (-1, 1):
        ax.plot(sx * ws, sy * ws, zs, color=ACC, lw=1.6)
for ang in np.linspace(0, np.pi, 7)[:-1]:
    ax.plot(np.cos(ang) * ws, np.sin(ang) * ws, zs, color=BLUE, lw=0.6, alpha=0.5)
    ax.plot(-np.cos(ang) * ws, -np.sin(ang) * ws, zs, color=BLUE, lw=0.6, alpha=0.5)
z0 = 0.45
w0 = np.sqrt(1 - z0 ** 2)
sq = np.array([[-w0, -w0], [w0, -w0], [w0, w0], [-w0, w0], [-w0, -w0]])
ax.plot(sq[:, 0], sq[:, 1], z0, color=RED, lw=2)
tt = np.linspace(0, 2 * np.pi, 100)
ax.plot(w0 * np.cos(tt), w0 * np.sin(tt), z0, color=RED, lw=2)
ax.set_box_aspect((1, 1, 1))
ax.set_axis_off()
ax.view_init(elev=18, azim=30)
ax.set_title(T("牟合方盖（黄）与内切球（蓝），红线是 z = 0.45 处的截面", "Mouhe fanggai (yellow), inscribed sphere (blue); red: section at z = 0.45"), fontsize=10)
a2 = fig.add_subplot(1, 2, 2)
s = w0
a2.add_patch(plt.Rectangle((-1, -1), 2, 2, fill=False, ec=MUTED, lw=1, ls="--"))
a2.add_patch(plt.Rectangle((-s, -s), 2 * s, 2 * s, color=ACC, alpha=0.35))
a2.add_patch(plt.Circle((0, 0), s, color=BLUE, alpha=0.55))
a2.text(0, 0, T("圆：π(r² − z²)", "circle: π(r² − z²)"), ha="center", va="center", fontsize=10, color="white")
a2.text(0, -s - 0.12, T("正方形：4(r² − z²)", "square: 4(r² − z²)"), ha="center", va="top", fontsize=10, color=INK)
a2.text(-1.0, 1.13, T("立方体截面 4r²；去掉正方形，剩下 4z²", "cube section 4r²; minus the square leaves 4z²"), fontsize=9, color=MUTED)
a2.set_xlim(-1.1, 1.1)
a2.set_ylim(-1.15, 1.25)
a2.set_aspect("equal")
a2.axis("off")
a2.set_title(T("同一高度的截面：面积之比 π : 4", "Sections at the same height: area ratio π : 4"), fontsize=10)
fig.tight_layout()
figure(fig, "fig16_2_1")
