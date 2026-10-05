"""第 17 章示意图共用：平面臂、三维示意、Panda 与 UR5e 的连杆折线；以及“重算某个算例程序、但不把它的数交给正文”的办法。
以下划线开头，构建时不单独运行。"""
import contextlib
import io
import math
import os
import runpy

import numpy as np

import bookout
from bookout import COLORS

C = COLORS
BLUE2 = "#6baed6"
PALE = "#dbe9f6"
GOLD2 = "#e3b54a"


def rerun(script):
    """重算 exNN_M.py，取回它的全部变量；它交给正文的数不算在本程序名下。"""
    env = os.environ.pop("WQ_BOOK_OUT", None)
    with contextlib.redirect_stdout(io.StringIO()):
        E = runpy.run_path(script)
    bookout._values.clear()
    if env is not None:
        os.environ["WQ_BOOK_OUT"] = env
    return E


# ---------------------------------------------------------------- 平面
def plane(ax, xlim, ylim):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)


def arm_pts(th, lengths, base=(0.0, 0.0)):
    pts, a = [np.array(base, float)], 0.0
    for t, l in zip(th, lengths):
        a += t
        pts.append(pts[-1] + l * np.array([math.cos(a), math.sin(a)]))
    return np.array(pts)


def draw_arm(ax, pts, color, lw=6, alpha=1.0, z=3, ls="-", jr=0.016):
    import matplotlib.patches as mp
    ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, alpha=alpha, solid_capstyle="round", zorder=z, ls=ls)
    for p in pts[:-1]:
        ax.add_patch(mp.Circle(p, jr, facecolor="white", edgecolor=color, lw=1.2, zorder=z + 1, alpha=alpha))
    ax.plot(*pts[-1], "o", color=color, ms=3.5, alpha=alpha, zorder=z + 1)


def base_mark(ax, p=(0, 0), s=0.03):
    import matplotlib.patches as mp
    ax.add_patch(mp.Polygon([[p[0] - s, p[1] - s * 1.2], [p[0] + s, p[1] - s * 1.2], [p[0] + s * 0.5, p[1]], [p[0] - s * 0.5, p[1]]],
                            closed=True, facecolor=C["muted"], edgecolor="none", zorder=2))


def spines(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, color="#ececec", lw=0.6)


def broken(x, y, jump=math.pi):
    """画角度曲线时，在跨过 ±180° 的地方断开。"""
    x, y = np.asarray(x, float), np.asarray(y, float).copy()
    k = np.where(np.abs(np.diff(y)) > jump)[0]
    y = np.insert(y, k + 1, np.nan)
    x = np.insert(x, k + 1, np.nan)
    return x, y


# ---------------------------------------------------------------- 三维
def axes3d(plt, fig, pos=111, elev=22, azim=-120):
    ax = fig.add_subplot(pos, projection="3d")
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    return ax


def equal3d(ax, pts, pad=0.05, zoom=1.0):
    pts = np.asarray(pts)
    lo, hi = pts.min(0) - pad, pts.max(0) + pad
    c, r = (lo + hi) / 2, (hi - lo).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1), zoom=zoom)


def draw_chain(ax, P, color, lw=5, alpha=1.0, joints=True, js=14):
    ax.plot(*P.T, color=color, lw=lw, alpha=alpha, solid_capstyle="round")
    if joints:
        ax.scatter(*P[1:-1].T, s=js, color="white", edgecolor=color, linewidths=0.9, alpha=alpha, depthshade=False)
    ax.scatter(*P[-1], s=js, color=color, alpha=alpha, depthshade=False)


def floor3d(ax, x=(-0.5, 0.5), y=(-0.5, 0.5), z=0.0, color="#e9ecef"):
    X, Y = np.meshgrid(np.array(x), np.array(y))
    ax.plot_surface(X, Y, np.full_like(X, z), color=color, alpha=0.35, linewidth=0, shade=False)


def sphere3d(ax, c, r, color, alpha=0.25):
    u, v = np.meshgrid(np.linspace(0, 2 * math.pi, 24), np.linspace(0, math.pi, 12))
    ax.plot_surface(c[0] + r * np.cos(u) * np.sin(v), c[1] + r * np.sin(u) * np.sin(v), c[2] + r * np.cos(v),
                    color=color, alpha=alpha, linewidth=0, shade=False)
