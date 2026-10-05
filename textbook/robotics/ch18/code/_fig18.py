"""第 18 章示意图共用：平面作图、三维作图的小工具，五杆与 2R 臂、Delta、Stewart 平台的画法。
以下划线开头，构建时不单独运行。"""
import math

import numpy as np

from _ch18 import (DELTA, ST_A, FIVE, ARM2, e2, ek, elbow, five_elbows, five_motors, st_points)
from bookout import COLORS

C = COLORS
BLUE2 = "#6baed6"
PALE = "#dbe9f6"
GOLD = "#e8a33d"
PALEGOLD = "#f6e2bd"
GREY = "#c9ced3"


# ---------------------------------------------------------------- 平面
def plane(ax, xlim, ylim):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)


def arrow2(ax, p, q, color, lw=1.3, ms=10, z=5):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=ms, shrinkA=0, shrinkB=0), zorder=z)


def base_mark(ax, p=(0, 0), s=0.025, z=2):
    import matplotlib.patches as mp
    ax.add_patch(mp.Polygon([[p[0] - s, p[1] - s * 1.2], [p[0] + s, p[1] - s * 1.2], [p[0] + s * 0.5, p[1]], [p[0] - s * 0.5, p[1]]],
                            closed=True, facecolor=C["muted"], edgecolor="none", zorder=z))


def joint(ax, p, color, r=0.012, z=6):
    import matplotlib.patches as mp
    ax.add_patch(mp.Circle(p, r, facecolor="white", edgecolor=color, lw=1.3, zorder=z))


def draw_arm2(ax, th, color, lw=6, z=3, L1=ARM2["L1"], L2=ARM2["L2"]):
    e = L1 * e2(th[0])
    w = e + L2 * e2(th[0] + th[1])
    ax.plot([0, e[0], w[0]], [0, e[1], w[1]], color=color, lw=lw, solid_capstyle="round", zorder=z)
    base_mark(ax)
    joint(ax, (0, 0), color, z=z + 1)
    joint(ax, e, color, z=z + 1)
    ax.plot(*w, "o", color=color, ms=4, zorder=z + 1)
    return e, w


def draw_five(ax, th, P, color, lw=5, z=3, alpha=1.0, motors=True):
    A1, A2 = five_motors()
    B1, B2 = five_elbows(th)
    for A, B in ((A1, B1), (A2, B2)):
        ax.plot([A[0], B[0]], [A[1], B[1]], color=color, lw=lw, solid_capstyle="round", zorder=z, alpha=alpha)
        ax.plot([B[0], P[0]], [B[1], P[1]], color=color, lw=lw * 0.6, solid_capstyle="round", zorder=z, alpha=alpha)
        if motors:
            base_mark(ax, A)
        joint(ax, A, color, z=z + 1)
        joint(ax, B, color, z=z + 1)
    ax.plot(*P, "o", color=color, ms=4, zorder=z + 1, alpha=alpha)


def ellipse_pts(J, scale=1.0, n=120):
    t = np.linspace(0, 2 * math.pi, n)
    return (J @ np.vstack([np.cos(t), np.sin(t)])).T * scale


# ---------------------------------------------------------------- 三维
def axes3d(plt, fig=None, pos=111, elev=20, azim=-60, size=(5.6, 4.6)):
    if fig is None:
        fig = plt.figure(figsize=size)
    ax = fig.add_subplot(pos, projection="3d")
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    return fig, ax


def equal3d(ax, pts, pad=0.03, zoom=1.0):
    pts = np.asarray(pts)
    lo, hi = pts.min(0) - pad, pts.max(0) + pad
    c, r = (lo + hi) / 2, (hi - lo).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1), zoom=zoom)


def label3d(ax, p, text, color=None, fs=9, **kw):
    ax.text(*p, text, fontsize=fs, color=color or C["ink"], **kw)


def arrow3d(ax, p, d, color, lw=1.6, ratio=0.2):
    ax.quiver(*p, *d, color=color, lw=lw, arrow_length_ratio=ratio)


def polygon3d(ax, P, color, alpha=0.25, edge=None, lw=1.0):
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    pc = Poly3DCollection([P], facecolor=color, edgecolor=edge or color, alpha=alpha, lw=lw)
    ax.add_collection3d(pc)


def hexagon_order(P):
    """把平面上的六个点按方位角排好，画成六边形。"""
    c = P.mean(0)
    a = np.arctan2(P[:, 1] - c[1], P[:, 0] - c[0])
    return P[np.argsort(a)]


def draw_stewart(ax, T, leg_color=None, plat_color=BLUE2, base_color=GREY, lw=2.2, legs_cmap=None, alpha=0.35):
    """Stewart 平台：机架六边形、动平台六边形、六条腿。"""
    q = st_points(T)
    polygon3d(ax, hexagon_order(ST_A), base_color, alpha=0.45, edge=C["muted"])
    polygon3d(ax, hexagon_order(q), plat_color, alpha=alpha, edge=C["z"])
    for i in range(6):
        col = leg_color if leg_color else (legs_cmap[i] if legs_cmap else C["ink"])
        ax.plot(*np.vstack([ST_A[i], q[i]]).T, color=col, lw=lw, solid_capstyle="round")
    ax.scatter(*ST_A.T, s=10, color=C["muted"], depthshade=False)
    ax.scatter(*q.T, s=10, color=C["z"], depthshade=False)
    return q


def draw_delta(ax, th, p, color=C["z"], lw=2.4, rods=C["ink"], D=DELTA, w=0.06):
    """Delta：静平台三角、主动臂、平行四边形（两根杆）、动平台。"""
    H = np.array([D["Rb"] * ek(k) for k in range(3)])
    polygon3d(ax, np.array([D["Rb"] * 2.0 * np.array([math.cos(a), math.sin(a), 0]) for a in np.radians([60, 180, 300])]), GREY, alpha=0.4,
              edge=C["muted"])
    for k in range(3):
        E = elbow(k, th[k], D)
        ax.plot(*np.vstack([H[k], E]).T, color=color, lw=lw, solid_capstyle="round")
        t = np.cross([0, 0, 1.0], ek(k))
        Pk = np.asarray(p) + D["Rp"] * ek(k)
        for s in (1, -1):
            ax.plot(*np.vstack([E + s * w / 2 * t, Pk + s * w / 2 * t]).T, color=rods, lw=1.0)
        ax.plot(*np.vstack([E - w / 2 * t, E + w / 2 * t]).T, color=color, lw=1.6)
    plat = np.array([np.asarray(p) + D["Rp"] * 1.9 * np.array([math.cos(a), math.sin(a), 0]) for a in np.radians([60, 180, 300])])
    polygon3d(ax, plat, BLUE2, alpha=0.6, edge=C["z"])
    ax.scatter(*H.T, s=12, color=C["muted"], depthshade=False)
