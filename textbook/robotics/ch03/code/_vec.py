"""第 3 章共用：反对称矩阵、基本转动、二维与三维示意图的画法。以下划线开头，构建时不单独运行。"""
import math

import numpy as np

from bookout import COLORS

C = COLORS
AXIS = (C["x"], C["y"], C["z"])


def d(deg):
    """度 → 弧度。"""
    return math.radians(deg)


def skew(a):
    """叉积矩阵 [a]，式 (3.2.10)：[a] b = a × b。"""
    a = np.asarray(a, float)
    return np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])


def unskew(A):
    """反对称矩阵 → 矢量（skew 的逆）。"""
    return np.array([A[2, 1], A[0, 2], A[1, 0]])


def cross(a, b):
    """叉积的分量公式 (3.2.9)，逐项写出，用来与 numpy.cross 核对。"""
    return np.array([a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]])


def rot_x(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def is_rotation(R, tol=1e-9):
    return np.allclose(R.T @ R, np.eye(3), atol=tol) and abs(np.linalg.det(R) - 1) < tol


# ---------------------------------------------------------------- 2D drawing

def arrow2(ax, p, q, color, lw=1.6, z=3, ms=12, alpha=1.0):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0,
                                                    mutation_scale=ms, alpha=alpha), zorder=z)


def arc2(ax, c, r, a0, a1, color, lw=1.0, ls="-", n=60):
    t = np.linspace(a0, a1, n)
    ax.plot(c[0] + r * np.cos(t), c[1] + r * np.sin(t), color=color, lw=lw, ls=ls)


# ---------------------------------------------------------------- 3D drawing

def axes3d(plt, size=(4.6, 4.2), elev=22, azim=-58, lim=1.1, zoom=1.0, center=(0, 0, 0)):
    fig = plt.figure(figsize=size)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_proj_type("ortho")
    ax.view_init(elev=elev, azim=azim)
    cx, cy, cz = center
    ax.set_xlim(cx - lim, cx + lim)
    ax.set_ylim(cy - lim, cy + lim)
    ax.set_zlim(cz - lim, cz + lim)
    ax.set_box_aspect((1, 1, 1), zoom=zoom)
    ax.set_axis_off()
    return fig, ax


def sub3d(fig, pos, elev=22, azim=-58, lim=1.1, zoom=1.0, center=(0, 0, 0)):
    ax = fig.add_subplot(pos, projection="3d")
    ax.set_proj_type("ortho")
    ax.view_init(elev=elev, azim=azim)
    cx, cy, cz = center
    ax.set_xlim(cx - lim, cx + lim)
    ax.set_ylim(cy - lim, cy + lim)
    ax.set_zlim(cz - lim, cz + lim)
    ax.set_box_aspect((1, 1, 1), zoom=zoom)
    ax.set_axis_off()
    return ax


def arrow3(ax, p, d, color, lw=2.0, ratio=0.12, alpha=1.0, ls="-"):
    ax.quiver(*p, *d, color=color, lw=lw, arrow_length_ratio=ratio, alpha=alpha, linestyle=ls)


def frame3(ax, R=np.eye(3), o=(0, 0, 0), length=1.0, sub="", lw=1.6, alpha=1.0, ls="-", fs=12, names=("x", "y", "z"), off=1.13):
    o = np.asarray(o, float)
    for i in range(3):
        dd = R[:, i] * length
        ax.quiver(*o, *dd, color=AXIS[i], lw=lw, arrow_length_ratio=0.1, alpha=alpha, linestyle=ls)
        p = o + dd * off
        label = rf"$\hat{{\boldsymbol{{{names[i]}}}}}_{{{sub}}}$" if sub else rf"$\hat{{\boldsymbol{{{names[i]}}}}}$"
        ax.text(*p, label, color=AXIS[i], fontsize=fs, ha="center", va="center", alpha=alpha)


def circle3(ax, center, u, v, r, a0, a1, color, lw=1.2, ls="-", n=80):
    t = np.linspace(a0, a1, n)
    P = np.asarray(center, float)[:, None] + r * (np.outer(u, np.cos(t)) + np.outer(v, np.sin(t)))
    ax.plot(*P, color=color, lw=lw, ls=ls)
    return P
