"""图 3.2.1：二元方程组 2x − y = 1、x + y = 5 的消元。每一步把一个方程换成它与另一个方程的组合，
直线绕交点 (2, 3) 转动：原方程组（左）、消去 x 后第二条直线变为水平线 y = 3（中）、再消去 y 后第一条直线变为竖直线 x = 2（右）。"""
import numpy as np

from _fig import BLUE, GREEN, MUTED, RED, T, figure, plt

steps = [((2, -1, 1), (1, 1, 5), T("原方程组", "original system")),
         ((2, -1, 1), (0, 1.5, 4.5), T("R₂ ← R₂ − ½R₁", "R₂ ← R₂ − ½R₁")),
         ((2, 0, 4), (0, 1.5, 4.5), T("R₁ ← R₁ + ⅔R₂", "R₁ ← R₁ + ⅔R₂"))]


def draw(ax, e, col):
    a, b, c = e
    if abs(b) > 1e-9:
        x = np.array([-0.5, 6])
        ax.plot(x, (c - a * x) / b, color=col, lw=2.2)
    else:
        ax.axvline(c / a, color=col, lw=2.2)


def lab(e):
    a, b, c = e
    f = lambda v: "" if abs(abs(v) - 1) < 1e-9 else f"{abs(v):g}"
    s = ""
    if abs(a) > 1e-9:
        s += ("−" if a < 0 else "") + f(a) + "x"
    if abs(b) > 1e-9:
        s += (" − " if b < 0 else (" + " if s else "")) + f(b) + "y"
    return s + f" = {c:g}"


fig, axs = plt.subplots(1, 3, figsize=(11.0, 3.8))
for ax, (e1, e2, name) in zip(axs, steps):
    draw(ax, e1, BLUE)
    draw(ax, e2, GREEN)
    ax.plot(2, 3, "o", color=RED, ms=7, zorder=5)
    ax.text(0.0, 5.5, lab(e1), color=BLUE, fontsize=10)
    ax.text(0.0, 5.0, lab(e2), color=GREEN, fontsize=10)
    ax.set_xlim(-0.5, 6)
    ax.set_ylim(-0.5, 6)
    ax.set_aspect("equal")
    ax.axhline(0, color=MUTED, lw=0.5)
    ax.axvline(0, color=MUTED, lw=0.5)
    ax.set_title(name, fontsize=11)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig3_2_1")
