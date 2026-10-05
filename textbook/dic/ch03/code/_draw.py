"""第 3 章示意图共用的配色与门级电路画法（matplotlib 直接画：反相器、传输门、与门、触发器方框、导线）。"""
import matplotlib.patches as mp

from bookout import COLORS

NMOS = "#1d6fb8"       # 蓝：数据、主锁存器
PMOS = "#c0392b"       # 红：时钟、违例
MEAN = "#2e8b57"       # 绿：余量、合格
LOAD = "#e67e22"       # 橙：要求、限值
INK = COLORS["ink"]
MUTED = COLORS["muted"]


def spines(ax):
    for k in ("top", "right"):
        ax.spines[k].set_visible(False)


def wire(ax, pts, color=INK, lw=1.3):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round")


def dot(ax, p, color=INK):
    ax.add_patch(mp.Circle(p, 0.06, color=color, zorder=5))


def text(ax, p, s, color=INK, size=10, ha="center", va="center"):
    ax.text(p[0], p[1], s, color=color, fontsize=size, ha=ha, va=va)


def inv(ax, x, y, right=True, size=0.5, color=INK):
    """反相器：三角形加小圆圈。right=True 时朝右（输入在 x，输出在 x + 1.2·size）。返回 (输入点, 输出点)。"""
    s = size
    if right:
        tri = [(x, y + s * 0.6), (x, y - s * 0.6), (x + s, y)]
        ax.add_patch(mp.Polygon(tri, closed=True, fill=False, ec=color, lw=1.3))
        ax.add_patch(mp.Circle((x + s + 0.08, y), 0.08, fill=False, ec=color, lw=1.3))
        return (x, y), (x + s + 0.16, y)
    tri = [(x, y + s * 0.6), (x, y - s * 0.6), (x - s, y)]
    ax.add_patch(mp.Polygon(tri, closed=True, fill=False, ec=color, lw=1.3))
    ax.add_patch(mp.Circle((x - s - 0.08, y), 0.08, fill=False, ec=color, lw=1.3))
    return (x, y), (x - s - 0.16, y)


def tg(ax, x, y, top, bot, color=INK, w=0.6):
    """传输门：两个相对的三角形（领结形），上方标 NMOS 栅极的时钟、下方标 PMOS 栅极的时钟。返回 (左端, 右端)。"""
    h = 0.32
    ax.add_patch(mp.Polygon([(x, y + h), (x, y - h), (x + w, y)], closed=True, fill=False, ec=color, lw=1.2))
    ax.add_patch(mp.Polygon([(x + w, y + h), (x + w, y - h), (x, y)], closed=True, fill=False, ec=color, lw=1.2))
    ax.add_patch(mp.Circle((x + w / 2, y - h - 0.07), 0.07, fill=False, ec=color, lw=1.1))
    wire(ax, [(x + w / 2, y + h * 0.5), (x + w / 2, y + h + 0.12)], color)
    text(ax, (x + w / 2, y + h + 0.3), top, PMOS, 9)
    text(ax, (x + w / 2, y - h - 0.38), bot, PMOS, 9)
    return (x, y), (x + w, y)


def and_gate(ax, x, y, size=0.6, color=INK):
    """与门：左边平、右边半圆。返回 (上输入, 下输入, 输出)。"""
    s = size
    wire(ax, [(x + s / 2, y + s / 2), (x, y + s / 2), (x, y - s / 2), (x + s / 2, y - s / 2)], color)
    ax.add_patch(mp.Arc((x + s / 2, y), s, s, theta1=-90, theta2=90, ec=color, lw=1.3))
    return (x, y + s / 4), (x, y - s / 4), (x + s, y)


def box(ax, x, y, w, h, label, color=INK, size=10):
    ax.add_patch(mp.Rectangle((x, y - h / 2), w, h, fill=False, ec=color, lw=1.3))
    text(ax, (x + w / 2, y), label, color, size)


def blank(ax, x0, x1, y0, y1):
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ax.set_aspect("equal")
    ax.axis("off")
