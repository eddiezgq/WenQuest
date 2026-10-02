"""第 11 章示意图共用：三维的圆柱、方块、球、弧形箭头，平面连杆的画法。以下划线开头，构建时不单独运行。"""
import math

import numpy as np

from bookout import COLORS

C = dict(COLORS)
C.update(steel="#9aa6ad", dark="#5d6b73", light="#d5dbde", orange="#e8913a", purple="#8e6bbf", fill="#eef2f4")


def _basis(axis):
    a = np.asarray(axis, float)
    a = a / np.linalg.norm(a)
    h = np.array([1.0, 0, 0]) if abs(a[0]) < 0.9 else np.array([0, 1.0, 0])
    u = np.cross(a, h)
    u /= np.linalg.norm(u)
    return a, u, np.cross(a, u)


def cylinder(ax, p0, p1, r, color, alpha=1.0, n=28, z=1):
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    a, u, w = _basis(p1 - p0)
    t = np.linspace(0, 2 * math.pi, n)
    s = np.linspace(0, 1, 2)
    T, S = np.meshgrid(t, s)
    P = p0[:, None, None] + (p1 - p0)[:, None, None] * S + r * (u[:, None, None] * np.cos(T) + w[:, None, None] * np.sin(T))
    ax.plot_surface(P[0], P[1], P[2], color=color, alpha=alpha, linewidth=0, shade=True, zorder=z)
    for p in (p0, p1):          # 端面
        c = p[:, None] + r * (u[:, None] * np.cos(t) + w[:, None] * np.sin(t))
        ax.plot(*c, color=C["dark"], lw=0.6, alpha=alpha)


def box(ax, center, size, color, alpha=1.0):
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    c, s = np.asarray(center, float), np.asarray(size, float) / 2
    v = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]) * s + c
    faces = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
    ax.add_collection3d(Poly3DCollection([v[f] for f in faces], facecolor=color, edgecolor=C["dark"], linewidths=0.5, alpha=alpha))


def sphere(ax, c, r, color, alpha=1.0):
    u, v = np.meshgrid(np.linspace(0, 2 * math.pi, 30), np.linspace(0, math.pi, 16))
    ax.plot_surface(c[0] + r * np.cos(u) * np.sin(v), c[1] + r * np.sin(u) * np.sin(v), c[2] + r * np.cos(v),
                    color=color, alpha=alpha, linewidth=0, shade=True)


def arrow3(ax, p, d, color, lw=1.8):
    ax.quiver(*p, *d, color=color, lw=lw, arrow_length_ratio=0.3)


def arc3(ax, center, axis, r, a0, a1, color, lw=1.6, head=True):
    """绕 axis 的弧形箭头（右手定则方向为正）。"""
    a, u, w = _basis(axis)
    t = np.linspace(a0, a1, 40)
    P = np.asarray(center, float)[:, None] + r * (u[:, None] * np.cos(t) + w[:, None] * np.sin(t))
    ax.plot(*P, color=color, lw=lw)
    if head:
        d = -u * math.sin(a1) + w * math.cos(a1)
        ax.quiver(*P[:, -1], *(0.35 * r * d * np.sign(a1 - a0)), color=color, lw=lw, arrow_length_ratio=0.9)


def axline(ax, p, d, L, color=None, lw=0.9):
    p, d = np.asarray(p, float), np.asarray(d, float)
    q = np.array([p - L * d, p + L * d])
    ax.plot(*q.T, color=color or C["muted"], lw=lw, ls=(0, (6, 3)))


def clean3d(ax, lim=1.0, elev=20, azim=-60, zoom=1.0):
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    ax.set_zlim(-lim, lim)
    ax.set_box_aspect((1, 1, 1), zoom=zoom)
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()


def plane(ax, xlim, ylim):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)


def pin(ax, p, r=0.022, color=None, z=6):
    """平面机构中的转动关节：白心圆。"""
    import matplotlib.patches as mp
    ax.add_patch(mp.Circle(p, r, facecolor="white", edgecolor=color or C["ink"], lw=1.4, zorder=z))


def ground(ax, p, w=0.12, color=None):
    """平面机构中的机架铰支座：三角形加剖面线。"""
    import matplotlib.patches as mp
    x, y = p
    col = color or C["dark"]
    ax.add_patch(mp.Polygon([[x, y], [x - w / 2, y - w * 0.6], [x + w / 2, y - w * 0.6]], closed=True, facecolor=C["fill"], edgecolor=col, lw=1.0, zorder=4))
    ax.plot([x - w * 0.7, x + w * 0.7], [y - w * 0.6] * 2, color=col, lw=1.2, zorder=4)
    for k in range(6):
        xx = x - w * 0.6 + k * w * 0.24
        ax.plot([xx, xx - w * 0.15], [y - w * 0.6, y - w * 0.8], color=col, lw=0.8, zorder=4)


def bar(ax, p, q, color, lw=5, z=3, alpha=1.0, ls="-"):
    ax.plot([p[0], q[0]], [p[1], q[1]], color=color, lw=lw, solid_capstyle="round", zorder=z, alpha=alpha, ls=ls)


def circ_int(c0, r0, c1, r1, sign=1):
    """两圆交点（平面）；sign 选两个交点中的哪一个。无交点时返回 None。"""
    c0, c1 = np.asarray(c0, float), np.asarray(c1, float)
    d = np.linalg.norm(c1 - c0)
    if d > r0 + r1 or d < abs(r0 - r1) or d == 0:
        return None
    a = (r0 * r0 - r1 * r1 + d * d) / (2 * d)
    h = math.sqrt(max(r0 * r0 - a * a, 0))
    e = (c1 - c0) / d
    m = c0 + a * e
    return m + sign * h * np.array([-e[1], e[0]])
