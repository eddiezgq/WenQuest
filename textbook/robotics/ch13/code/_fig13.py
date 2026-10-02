"""第 13 章示意图共用：三维示意（坐标系、轴线、圆弧、尺寸）和平面臂。以下划线开头，构建时不单独运行。"""
import math

import numpy as np

from bookout import COLORS

C = COLORS
L3R = (0.425, 0.392, 0.1)


def axes3d(plt, size=(5.6, 4.4), elev=22, azim=-120, ax=None, fig=None, pos=111):
    if fig is None:
        fig = plt.figure(figsize=size)
    ax = fig.add_subplot(pos, projection="3d")
    ax.view_init(elev=elev, azim=azim)
    ax.set_axis_off()
    return fig, ax


def equal3d(ax, pts, pad=0.05, zoom=1.0):
    pts = np.asarray(pts)
    lo, hi = pts.min(0) - pad, pts.max(0) + pad
    c, r = (lo + hi) / 2, (hi - lo).max() / 2
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    ax.set_box_aspect((1, 1, 1), zoom=zoom)


def frame3d(ax, T, size, label="", fs=10, off=(0.0, 0.0, -0.06), names=None, lw=1.6, color=None):
    """三维坐标系：x 红、y 绿、z 蓝。names=("x_1", "y_1", "z_1") 时在箭头端写轴名（LaTeX）。"""
    o = T[:3, 3]
    cols = (C["x"], C["y"], C["z"])
    for k in range(3):
        if names is not None and names[k] is None:
            continue
        d = T[:3, k] * size
        ax.quiver(*o, *d, color=cols[k], lw=lw, arrow_length_ratio=0.22)
        if names:
            # z 轴常与画出的关节轴重合：把轴名稍向本坐标系的 x 方向错开，并衬白底，免得被轴线压住
            pos = o + d * 1.12 + (0.28 * size * T[:3, 0] if k == 2 else 0.0)
            ax.text(*pos, f"${names[k]}$", fontsize=fs - 1, color=cols[k], zorder=20,
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.6, alpha=0.85))
    if label:
        ax.text(*(o + np.asarray(off)), label, fontsize=fs, color=color or C["ink"])


def line3d(ax, p, u, t0, t1, color, lw=1.2, ls="-", alpha=1.0):
    p, u = np.asarray(p, float), np.asarray(u, float)
    P = np.array([p + t0 * u, p + t1 * u])
    ax.plot(*P.T, color=color, lw=lw, ls=ls, alpha=alpha)


def arc3d(ax, c, e1, e2, r, a0, a1, color, lw=1.3, arrow=True):
    """以 c 为圆心、在 e1、e2 张成的平面内从角 a0 画到 a1 的圆弧（e1、e2 为正交单位矢量），终点带箭头。"""
    c, e1, e2 = (np.asarray(x, float) for x in (c, e1, e2))
    t = np.linspace(a0, a1, 40)
    P = np.array([c + r * (math.cos(s) * e1 + math.sin(s) * e2) for s in t])
    ax.plot(*P.T, color=color, lw=lw)
    if arrow:
        d = P[-1] - P[-4]
        ax.quiver(*P[-4], *d, color=color, lw=lw, arrow_length_ratio=0.9)
    return P


def plane(ax, xlim, ylim):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)


def arm_points(th, lengths=L3R, base=(0.0, 0.0)):
    pts, a = [np.array(base, float)], 0.0
    for t, l in zip(th, lengths):
        a += t
        pts.append(pts[-1] + l * np.array([math.cos(a), math.sin(a)]))
    return np.array(pts), a


def draw_arm(ax, pts, color, lw=6, alpha=1.0, joints=True, z=3, ls="-"):
    import matplotlib.patches as mp
    ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, alpha=alpha, solid_capstyle="round", zorder=z, ls=ls)
    if joints:
        for p in pts[:-1]:
            ax.add_patch(mp.Circle(p, 0.022, facecolor="white", edgecolor=color, lw=1.6, zorder=z + 1, alpha=alpha))
    ax.plot(*pts[-1], "o", color=color, ms=4, alpha=alpha, zorder=z + 1)


def frame2d(ax, p, ang, size, label="", fs=10, dx=-0.02, dy=-0.06, names=None):
    """平面坐标系：x 红、y 绿。"""
    for k, col in ((0, C["x"]), (1, C["y"])):
        a = ang + k * math.pi / 2
        e = (p[0] + size * math.cos(a), p[1] + size * math.sin(a))
        ax.annotate("", xy=e, xytext=p, arrowprops=dict(arrowstyle="-|>", color=col, lw=1.3, mutation_scale=10), zorder=6)
        if names:
            ax.text(p[0] + 1.25 * size * math.cos(a) - 0.015, p[1] + 1.25 * size * math.sin(a) - 0.012, f"${names[k]}$",
                    fontsize=fs - 1, color=col)
    if label:
        ax.text(p[0] + dx, p[1] + dy, label, fontsize=fs, color=C["ink"])
