"""本章插图共用的画法（与第 18 章相同）：坐标轴、箭头、单位圆与它的像。以下划线开头，构建时不单独运行。"""
import math

import numpy as np

from bookout import COLORS, T, figure, style  # noqa: F401

plt = style()
RED, GREEN, BLUE, INK, MUTED, ACC = COLORS["x"], COLORS["y"], COLORS["z"], COLORS["ink"], COLORS["muted"], COLORS["accent"]


def axes_box(ax, lim, ticks=True):
    ax.set_aspect("equal")
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.axhline(0, color=MUTED, lw=0.6, zorder=0)
    ax.axvline(0, color=MUTED, lw=0.6, zorder=0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if not ticks:
        ax.set_xticks([])
        ax.set_yticks([])


def arrow(ax, v, color, text=None, offset=(0.08, 0.08), lw=2.0, size=12, start=(0, 0)):
    ax.annotate("", xy=(start[0] + v[0], start[1] + v[1]), xytext=start,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=14), zorder=5)
    if text:
        ax.text(start[0] + v[0] + offset[0], start[1] + v[1] + offset[1], text, color=color, fontsize=size, zorder=6)


def circle_pts(M=None, r=1.0, n=361):
    t = np.linspace(0, 2 * math.pi, n)
    P = np.vstack([r * np.cos(t), r * np.sin(t)])
    return (np.asarray(M) @ P) if M is not None else P


def marker(M=None, scale=0.35):
    """一个不对称的小旗，用来看出变换是转动还是反射。"""
    P = np.array([[0.0, 0.0], [0.9, 0.0], [0.9, 0.35], [0.55, 0.35], [0.55, 0.6], [0.0, 0.6], [0.0, 0.0]]).T * scale + np.array([[0.25], [0.15]])
    return (np.asarray(M) @ P) if M is not None else P


def view3(az=35, el=22):
    """正交投影的三维示意：返回 P(p) → 平面坐标，以及视线方向（指向观察者），用于手工画三维示意图。"""
    a, e = math.radians(az), math.radians(el)
    right = np.array([-math.sin(a), math.cos(a), 0.0])
    up = np.array([-math.sin(e) * math.cos(a), -math.sin(e) * math.sin(a), math.cos(e)])
    fwd = np.array([math.cos(e) * math.cos(a), math.cos(e) * math.sin(a), math.sin(e)])
    return (lambda p: np.array([np.dot(p, right), np.dot(p, up)])), fwd


def arrow3(ax, P, a, b, color, text=None, lw=2.2, size=12, off=(0.08, 0.08)):
    pa, pb = P(np.asarray(a, float)), P(np.asarray(b, float))
    ax.annotate("", xy=pb, xytext=pa, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=14), zorder=6)
    if text:
        ax.text(pb[0] + off[0], pb[1] + off[1], text, color=color, fontsize=size, zorder=7)
