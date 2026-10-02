"""第 44 章示意图共用的配色与画法（与第 6、34 章一致）。"""
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
