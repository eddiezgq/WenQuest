"""第 8 章示意图共用的画法。以下划线开头，构建时不单独运行。"""
import numpy as np

from bookout import COLORS

C = COLORS
BLUE = "#1f77b4"
ORANGE = "#d9730d"
PURPLE = "#7b4fa0"
GREY = "#9aa4ab"


def arrow(ax, p, q, color, lw=1.4, z=4, ms=11, style="-|>"):
    ax.annotate("", xy=tuple(q), xytext=tuple(p),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=ms), zorder=z)


def draw_arm(ax, pts, color, lw=4.0, alpha=1.0, z=5, joint=True, base=True, ls="-"):
    """平面串联臂：pts 为关节中心与末端（arm_points 的结果）。"""
    ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, alpha=alpha, solid_capstyle="round", zorder=z, ls=ls)
    if joint:
        ax.plot(pts[:-1, 0], pts[:-1, 1], "o", ms=5.5, mfc="white", mec=color, mew=1.4, alpha=alpha, zorder=z + 1)
    if base:
        b = pts[0]
        ax.fill([b[0] - 0.05, b[0] + 0.05, b[0] + 0.025, b[0] - 0.025], [b[1] - 0.04, b[1] - 0.04, b[1], b[1]],
                color="#b9c1c7", zorder=z - 1)


def target(ax, p, label=None, dx=0.015, dy=0.015, fs=10):
    ax.plot(*p, marker="x", ms=8, mew=2, color=C["x"], zorder=8)
    if label:
        ax.text(p[0] + dx, p[1] + dy, label, color=C["x"], fontsize=fs, zorder=8)


def clean(ax):
    ax.set_aspect("equal")
    ax.axis("off")
