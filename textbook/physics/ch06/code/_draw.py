"""第 6 章示意图共用的画法：AGV、料车、箱子、力的箭头。所有长度以米为单位画在 matplotlib 的数据坐标里。"""
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

from bookout import COLORS

FORCE = "#c0392b"      # 力：红
VEL = "#e67e22"        # 速度：橙
ACC = "#8e44ad"        # 加速度：紫
BODY = "#5b8bd0"       # 机器人车体：蓝
CART = "#9aa7b2"       # 料车：灰
CRATE = "#d4a24c"      # 货箱：土黄
INK = COLORS["ink"]
MUTED = COLORS["muted"]


def arrow(ax, x0, y0, dx, dy, color=FORCE, text="", where="end", off=(0.0, 0.0), lw=2.2, size=11, ha="center"):
    """A force (or velocity) arrow from (x0, y0) by (dx, dy), labelled at its end or middle."""
    ax.add_patch(FancyArrowPatch((x0, y0), (x0 + dx, y0 + dy), arrowstyle="-|>", mutation_scale=14, lw=lw,
                                 color=color, shrinkA=0, shrinkB=0, zorder=5))
    if text:
        tx, ty = (x0 + dx, y0 + dy) if where == "end" else (x0 + dx / 2, y0 + dy / 2)
        ax.text(tx + off[0], ty + off[1], text, color=color, fontsize=size, ha=ha, va="center", zorder=6)


def agv(ax, x, y=0.0, w=1.0, h=0.32, color=BODY, label=""):
    """An AGV seen from the side: bottom-left corner of the body at (x, y + wheel radius)."""
    r = h * 0.28
    ax.add_patch(FancyBboxPatch((x, y + r), w, h, boxstyle="round,pad=0,rounding_size=0.04", fc=color, ec=INK, lw=1.2, zorder=3))
    for cx in (x + 0.2 * w, x + 0.8 * w):
        ax.add_patch(Circle((cx, y + r), r, fc=INK, ec=INK, zorder=4))
    ax.add_patch(Rectangle((x + w - 0.08, y + r + h * 0.45), 0.08, h * 0.25, fc="#f1c40f", ec=INK, lw=0.8, zorder=4))
    if label:
        ax.text(x + w / 2, y + r + h / 2, label, ha="center", va="center", fontsize=10, color="white", zorder=5)
    return y + r + h          # deck height


def cart(ax, x, y=0.0, w=0.8, h=0.22, label=""):
    """A material cart (no drive): a flat deck on four small casters."""
    r = 0.06
    ax.add_patch(Rectangle((x, y + 2 * r), w, h, fc=CART, ec=INK, lw=1.2, zorder=3))
    for cx in (x + 0.15 * w, x + 0.85 * w):
        ax.add_patch(Circle((cx, y + r), r, fc="white", ec=INK, lw=1.2, zorder=4))
    if label:
        ax.text(x + w / 2, y + 2 * r + h / 2, label, ha="center", va="center", fontsize=10, color=INK, zorder=5)
    return y + 2 * r + h


def crate(ax, x, y, s=0.3, label=""):
    ax.add_patch(Rectangle((x, y), s, s, fc=CRATE, ec=INK, lw=1.2, zorder=3))
    ax.plot([x, x + s], [y, y + s], color=INK, lw=0.6, zorder=4)
    ax.plot([x, x + s], [y + s, y], color=INK, lw=0.6, zorder=4)
    if label:
        ax.text(x + s / 2, y + s + 0.05, label, ha="center", va="bottom", fontsize=10, color=INK)


def floor(ax, x0, x1, y=0.0):
    ax.plot([x0, x1], [y, y], color=INK, lw=1.5, zorder=2)
    import numpy as np
    for x in np.arange(x0 + 0.05, x1, 0.12):
        ax.plot([x, x - 0.06], [y, y - 0.06], color=MUTED, lw=0.8, zorder=1)


def clean(ax):
    ax.set_aspect("equal")
    ax.axis("off")
