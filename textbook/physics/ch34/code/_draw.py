"""第 34 章示意图共用的画法与配色（与第 6 章一致）。"""
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle

from bookout import COLORS

FORCE = "#c0392b"      # 力
CURR = "#e67e22"       # 电流
FIELD = "#1d6fb8"      # 磁场
EFIELD = "#2ca02c"     # 电场
INK = COLORS["ink"]
MUTED = COLORS["muted"]
NORTH, SOUTH = "#c0392b", "#1d6fb8"


def arrow(ax, x0, y0, dx, dy, color=FORCE, text="", off=(0.0, 0.0), lw=2.0, size=11, ha="center", ms=14):
    ax.add_patch(FancyArrowPatch((x0, y0), (x0 + dx, y0 + dy), arrowstyle="-|>", mutation_scale=ms, lw=lw,
                                 color=color, shrinkA=0, shrinkB=0, zorder=5))
    if text:
        ax.text(x0 + dx + off[0], y0 + dy + off[1], text, color=color, fontsize=size, ha=ha, va="center", zorder=6)


def magnet(ax, x, y, w=0.6, h=0.25, north_right=True, labels=True):
    """A bar magnet centred at (x, y); N half red, S half blue."""
    left, right = (SOUTH, NORTH) if north_right else (NORTH, SOUTH)
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w / 2, h, fc=left, ec=INK, lw=1, zorder=3))
    ax.add_patch(Rectangle((x, y - h / 2), w / 2, h, fc=right, ec=INK, lw=1, zorder=3))
    if labels:
        ax.text(x - w / 4, y, "N" if not north_right else "S", color="white", ha="center", va="center", fontsize=11, zorder=4)
        ax.text(x + w / 4, y, "N" if north_right else "S", color="white", ha="center", va="center", fontsize=11, zorder=4)


def dot_or_cross(ax, x, y, out=True, r=0.05, color=FIELD):
    """B pointing out of the page (dot) or into it (cross)."""
    ax.add_patch(Circle((x, y), r, fc="none", ec=color, lw=1))
    if out:
        ax.add_patch(Circle((x, y), r * 0.25, fc=color, ec=color))
    else:
        ax.plot([x - r * 0.7, x + r * 0.7], [y - r * 0.7, y + r * 0.7], color=color, lw=1)
        ax.plot([x - r * 0.7, x + r * 0.7], [y + r * 0.7, y - r * 0.7], color=color, lw=1)


def clean(ax):
    ax.set_aspect("equal")
    ax.axis("off")


def spines(ax):
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
