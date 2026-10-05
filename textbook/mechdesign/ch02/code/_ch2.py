"""第 2 章共用：数字工厂的数据（WQR-105 的物料、参数配置器）、零件库（Go2 的厂商参数）和示意图的画法。

数据只从数字工厂与零件库取：factory/factory/data.py、factory/digital/hub/configurator.py、library/catalog。
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
for p in (ROOT / "factory", ROOT / "factory" / "digital", Path(__file__).resolve().parents[2] / "conventions"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from factory import data as F          # noqa: E402
from hub import configurator as C      # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

from bookout import COLORS, T          # noqa: E402

INK, MUTED = COLORS["ink"], COLORS["muted"]
PALE = {"blue": "#e8eef7", "green": "#eef6e8", "orange": "#fbefe0", "purple": "#f3e8f7", "teal": "#e8f4f4", "gray": "#eef0f2"}


def box(ax, x, y, w, h, text, fc="#ffffff", size=8.5, bold=False, ec=None, lw=0.8):
    """圆角方框，中心写字（x, y 为左下角）"""
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06", fc=fc, ec=ec or INK, lw=lw))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, weight="bold" if bold else "normal")


def arrow(ax, p, q, color=None, lw=0.9, style="-|>", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=10, lw=lw, color=color or INK,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2))


def bom_tree(item="WQR-105"):
    """BOM 展开：[(层级, 物料, 数量)]，深度优先"""
    out = []

    def walk(code, qty, lvl):
        out.append((lvl, code, qty))
        for c, q in F.BOMS.get(code, (None, []))[1]:
            walk(c, q, lvl + 1)
    walk(item, 1, 0)
    return out


def kind(code):
    return F.ITEMS[code][1]


def go2():
    """零件库 B-LEG-GO2 的厂商参数（重量、外形、负载……）"""
    import yaml
    v = yaml.safe_load((ROOT / "library" / "catalog" / "B" / "B-LEG-GO2" / "vendor.yaml").read_text(encoding="utf-8"))
    return v["datasheet"]["values"]
