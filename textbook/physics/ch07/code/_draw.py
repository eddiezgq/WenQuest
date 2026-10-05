"""第 7 章示意图共用的配色与画法（与第 6、34、44 章一致）。"""
from bookout import COLORS

PSI = "#1d6fb8"        # 波函数：蓝
PROB = "#8e44ad"       # 概率密度：紫
POT = "#5d6d7e"        # 势能：灰
LEVEL = "#e67e22"      # 能级：橙
CLASS = "#c0392b"      # 经典结果：红
INK = COLORS["ink"]
MUTED = COLORS["muted"]


def spines(ax):
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)


def clean(ax):
    ax.axis("off")
DATA = "#1d6fb8"       # 测量数据：蓝
FIT = "#c0392b"        # 拟合与模型：红
VA = "#1d6fb8"         # 第一个矢量：蓝
VB = "#2e8b57"         # 第二个矢量：绿
VR = "#c0392b"         # 合矢量、结果：红
X_, Y_, Z_ = COLORS["x"], COLORS["y"], COLORS["z"]


def arrow(ax, p, q, color, lw=2.0, label=None, off=(0.0, 0.0), fs=11, ms=14, zorder=3):
    """A 2D arrow from p to q with an optional label near its middle."""
    from matplotlib.patches import FancyArrowPatch
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=ms, color=color, lw=lw, zorder=zorder,
                                 shrinkA=0, shrinkB=0))
    if label:
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], label, color=color, fontsize=fs,
                ha="center", va="center")
