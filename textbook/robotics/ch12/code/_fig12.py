"""第 12 章示意图共用：平面 3R 臂和三维机械臂的画法。以下划线开头，构建时不单独运行。"""
import math

import numpy as np

from bookout import COLORS

C = COLORS
L = (0.425, 0.392, 0.1)


def arm_points(th, lengths=L, base=(0.0, 0.0)):
    """平面串联臂各关节中心与末端：[(x0,y0), (x1,y1), …, 末端]。"""
    pts, a = [np.array(base, float)], 0.0
    for t, l in zip(th, lengths):
        a += t
        pts.append(pts[-1] + l * np.array([math.cos(a), math.sin(a)]))
    return np.array(pts), a


def draw_arm(ax, pts, color, lw=6, alpha=1.0, joints=True, z=3, ls="-"):
    ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, alpha=alpha, solid_capstyle="round", zorder=z, ls=ls)
    if joints:
        for p in pts[:-1]:
            ax.add_patch(_circle(p, 0.022, "white", color, z + 1, alpha))
    ax.plot(*pts[-1], "o", color=color, ms=4, alpha=alpha, zorder=z + 1)


def _circle(c, r, face, edge, z, alpha=1.0):
    import matplotlib.patches as mp
    return mp.Circle(c, r, facecolor=face, edgecolor=edge, lw=1.6, zorder=z, alpha=alpha)


def frame2d(ax, p, ang, size, label, color=None, fs=10):
    """平面坐标系：x 红、y 绿。"""
    for k, col in ((0, C["x"]), (1, C["y"])):
        a = ang + k * math.pi / 2
        ax.annotate("", xy=(p[0] + size * math.cos(a), p[1] + size * math.sin(a)), xytext=p,
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.3, mutation_scale=10), zorder=6)
    ax.text(p[0] - 0.02, p[1] - 0.06, label, fontsize=fs, color=color or C["ink"])


def arc_arrow(ax, c, r, a0, a1, color, lw=1.4):
    t = np.linspace(a0, a1, 40)
    ax.plot(c[0] + r * np.cos(t), c[1] + r * np.sin(t), color=color, lw=lw, zorder=5)
    end = np.array([c[0] + r * math.cos(a1), c[1] + r * math.sin(a1)])
    d = np.sign(a1 - a0) * np.array([-math.sin(a1), math.cos(a1)])
    ax.annotate("", xy=end + 0.004 * d, xytext=end - 0.03 * d,
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=10), zorder=5)


def plane(ax, xlim, ylim):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)


def axes3d(plt, size=(5.6, 4.4), elev=22, azim=-120):
    fig = plt.figure(figsize=size)
    ax = fig.add_subplot(111, projection="3d")
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    return fig, ax


def equal3d(ax, pts, pad=0.05):
    pts = np.asarray(pts)
    lo, hi = pts.min(0) - pad, pts.max(0) + pad
    c, r = (lo + hi) / 2, (hi - lo).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1))


def frame3d(ax, T, size, label, fs=10):
    o = T[:3, 3]
    for k, col in enumerate((C["x"], C["y"], C["z"])):
        d = T[:3, k] * size
        ax.quiver(*o, *d, color=col, lw=1.6, arrow_length_ratio=0.25)
    ax.text(*(o + np.array([0.0, 0.0, -0.06])), label, fontsize=fs, color=C["ink"])
