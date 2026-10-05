"""第 19 章示意图共用：俯视的车轮、车体、箭头、轴线。以下划线开头，构建时不单独运行。"""
import math

import numpy as np

from bookout import COLORS

C = dict(COLORS)
C.update(steel="#9aa6ad", dark="#5d6b73", light="#d5dbde", orange="#e8913a", purple="#8e6bbf", fill="#eef2f4",
         body="#dfe6ea", blue="#1f77b4", red="#d62728", green="#2ca02c")


def rot(a):
    return np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])


def to_world(pose, pts):
    x, y, f = pose
    return (rot(f) @ np.asarray(pts, float).T).T + np.array([x, y])


def arrow(ax, p, q, color, lw=1.6, ms=11, z=4, ls="-"):
    ax.annotate("", xy=tuple(q), xytext=tuple(p),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=ms, linestyle=ls),
                zorder=z)


def rect(ax, pose, cx, cy, ang, L, W, fc, ec, lw=0.9, z=2, alpha=1.0):
    """车体坐标中心 (cx, cy)、方向 ang、长 L 宽 W 的矩形，画在位姿 pose 处。"""
    c = np.array([[-L / 2, -W / 2], [L / 2, -W / 2], [L / 2, W / 2], [-L / 2, W / 2], [-L / 2, -W / 2]])
    c = (rot(ang) @ c.T).T + np.array([cx, cy])
    w = to_world(pose, c)
    ax.fill(w[:, 0], w[:, 1], fc=fc, ec=ec, lw=lw, zorder=z, alpha=alpha)
    return w


def wheel(ax, pose, x, y, beta, r=0.05, width=0.025, fc="#4a555c", z=3, rollers=0, gamma=0.0):
    """俯视的车轮：长 2r、宽 width。rollers > 0 时画瑞典轮的辊子（与轮平面成 gamma 角的短线）。"""
    rect(ax, pose, x, y, beta, 2 * r, width, fc, C["ink"], 0.6, z)
    if rollers:
        for s in np.linspace(-0.75, 0.75, rollers):
            c = np.array([x, y]) + s * r * np.array([math.cos(beta), math.sin(beta)])
            k = 0.45 * width / max(0.35, abs(math.sin(gamma))) if abs(gamma) > 1e-6 else 0.12 * r
            d = k * np.array([math.cos(beta + gamma), math.sin(beta + gamma)])
            p = to_world(pose, [c - d, c + d])
            ax.plot(p[:, 0], p[:, 1], color="#f0f0f0", lw=1.2, zorder=z + 1, solid_capstyle="round")


def line_world(ax, pose, p, q, **kw):
    w = to_world(pose, [p, q])
    ax.plot(w[:, 0], w[:, 1], **kw)


def label(ax, p, text, **kw):
    kw.setdefault("fontsize", 10)
    ax.text(p[0], p[1], text, **kw)
