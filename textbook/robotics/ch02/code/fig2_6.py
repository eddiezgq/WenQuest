"""2.6 节的示意图。

图 2.6.1：平面 3R 臂的自运动：末端固定在 θ = (30°, 60°, −60°) 时的位置，θ1 取 27°、30°、40°、55°，
         另两个关节随之调整（算例 2.6.1）。零空间方向就是这条“形态曲线”的切向。
图 2.6.2：四个基本子空间：A（m×n，秩 r）把行空间一一对应地映到值域，把零空间映到 0；
         行空间 ⟂ 零空间（在 ℝⁿ 中），值域 ⟂ 左零空间（在 ℝᵐ 中）。
"""
import math

import numpy as np

from _la import C, L3R, arm_points, arrow, base, d, draw_arm
from bookout import T, figure, style

plt = style()
L1, L2, L3 = L3R


def ik_rest(t1, p):
    e = np.array([L1 * math.cos(t1), L1 * math.sin(t1)])
    q = p - e
    c3 = (q @ q - L2 ** 2 - L3 ** 2) / (2 * L2 * L3)
    t3 = -math.acos(max(-1.0, min(1.0, c3)))
    a = math.atan2(q[1], q[0]) - math.atan2(L3 * math.sin(t3), L2 + L3 * math.cos(t3))
    return np.array([t1, a - t1, t3])


# ---------------------------------------------------------------- 图 2.6.1
th = np.array([d(30), d(60), d(-60)])
tip = arm_points(th, L3R)[-1]
fig, ax = plt.subplots(figsize=(5.8, 4.8))
ax.set_aspect("equal")
ax.axis("off")
base(ax, w=0.05)
cols = {27: C["z"], 30: C["ink"], 40: C["accent"], 55: C["x"]}
for deg, col in cols.items():
    q = ik_rest(d(deg), tip)
    pts = arm_points(q, L3R)
    draw_arm(ax, pts, col, lw=4 if deg != 30 else 5, alpha=0.9)
    ax.text(0.5, 0.4 - 0.05 * list(cols).index(deg), f"θ₁ = {deg}°", fontsize=10, color=col)
# 肘部（关节 2）随 θ1 走过的圆弧、关节 3 的轨迹
tt = np.radians(np.linspace(27, 55, 60))
ax.plot(L1 * np.cos(tt), L1 * np.sin(tt), color=C["muted"], lw=0.8, ls=":")
j3 = np.array([arm_points(ik_rest(t, tip), L3R)[2] for t in tt])
ax.plot(j3[:, 0], j3[:, 1], color=C["muted"], lw=0.8, ls=":")
ax.plot(*tip, "*", color=C["accent"], ms=12, zorder=8)
ax.text(tip[0] + 0.02, tip[1] + 0.02, T("末端不动", "end-effector fixed"), fontsize=10)
ax.text(-0.1, -0.08, T("虚线：关节 2、关节 3 的轨迹；黑色是算例 2.6.1 的形态",
                       "dotted: paths of joints 2 and 3; black: the configuration of Example 2.6.1"), fontsize=9, color=C["ink"])
ax.set_xlim(-0.12, 0.7)
ax.set_ylim(-0.1, 0.75)
figure(fig, "fig2_6_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 2.6.2
fig, ax = plt.subplots(figsize=(8.6, 4.0))
ax.axis("off")
ax.set_xlim(0, 10)
ax.set_ylim(0, 5)


def space(cx, cy, top, bot, name, ctop, cbot):
    ax.add_patch(plt.Rectangle((cx - 1.6, cy - 1.8), 3.2, 3.6, fill=False, ec=C["muted"], lw=0.8))
    ax.add_patch(plt.Polygon([[cx - 1.4, cy + 0.1], [cx + 0.6, cy + 0.1], [cx + 1.4, cy + 1.6], [cx - 0.6, cy + 1.6]], closed=True,
                             fc=ctop, ec="none", alpha=0.35))
    ax.add_patch(plt.Polygon([[cx - 0.9, cy - 0.1], [cx + 0.9, cy - 0.1], [cx + 0.5, cy - 1.6], [cx - 1.3, cy - 1.6]], closed=True,
                             fc=cbot, ec="none", alpha=0.35))
    ax.text(cx - 1.25, cy + 1.0, top, fontsize=10)
    ax.text(cx - 1.2, cy - 1.0, bot, fontsize=10)
    ax.text(cx - 1.6, cy + 1.95, name, fontsize=11)
    ax.text(cx + 0.95, cy - 0.15, r"$\perp$", fontsize=16)


space(2.0, 2.5, T("行空间\n维数 r", "row space R(Aᵀ)\ndim r"), T("零空间 N(A)\n维数 n − r", "null space N(A)\ndim n − r"), r"$\mathbb{R}^n$", C["z"], C["x"])
space(8.0, 2.5, T("值域 R(A)\n维数 r", "range R(A)\ndim r"), T("左零空间 N(Aᵀ)\n维数 m − r", "left null space N(Aᵀ)\ndim m − r"), r"$\mathbb{R}^m$", C["z"], C["y"])
ax.annotate("", xy=(6.6, 3.5), xytext=(3.4, 3.5), arrowprops=dict(arrowstyle="-|>", color=C["z"], lw=1.6))
ax.text(4.3, 3.65, T("A：一一对应", "A: one-to-one"), fontsize=10, color=C["z"])
ax.annotate("", xy=(6.75, 2.5), xytext=(3.4, 1.5), arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=1.4, ls="--"))
ax.text(3.9, 1.95, T("A x = 0", "A x = 0"), fontsize=10, color=C["x"])
ax.plot([6.8], [2.5], "o", color=C["ink"], ms=4)
ax.text(6.55, 2.2, "0", fontsize=11)
figure(fig, "fig2_6_2")
plt.close(fig)
