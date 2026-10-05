"""第 7 章插图共用的画法。以下划线开头，构建时不单独运行。"""
from bookout import COLORS, T, figure, style  # noqa: F401

plt = style()
RED, GREEN, BLUE, INK, MUTED, ACC = COLORS["x"], COLORS["y"], COLORS["z"], COLORS["ink"], COLORS["muted"], COLORS["accent"]


def clean(ax, zero=True):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if zero:
        ax.axhline(0, color=MUTED, lw=0.6, zorder=0)
