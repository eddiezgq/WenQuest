"""第 4 章示意图共用的配色与画法。"""
from bookout import COLORS

NMOS = "#1d6fb8"       # NMOS、下拉、tPHL：蓝
PMOS = "#c0392b"       # PMOS、上拉、tPLH：红
MEAN = "#2e8b57"       # 平均值、合成结果：绿
LOAD = "#e67e22"       # 负载线、要求、限值：橙
INK = COLORS["ink"]
MUTED = COLORS["muted"]


def spines(ax):
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)
