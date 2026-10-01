"""第 4 章共用：基本转动、三维示意图的画法（坐标系、书本、圆弧）。以下划线开头，构建时不单独运行。"""
import math

import numpy as np

from bookout import COLORS

C = COLORS
AXIS = (C["x"], C["y"], C["z"])


def rot_x(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def skew(w):
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


def rot_axis(w, t):
    """罗德里格斯公式 (4.4 节)。"""
    w = np.asarray(w, float) / np.linalg.norm(w)
    K = skew(w)
    return np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K


def is_rotation(R, tol=1e-9):
    return np.allclose(R.T @ R, np.eye(3), atol=tol) and abs(np.linalg.det(R) - 1) < tol


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


def frame(ax, R=np.eye(3), o=(0, 0, 0), length=1.0, names=("x", "y", "z"), sub="", lw=2.0, alpha=1.0, ls="-", fs=12):
    o = np.asarray(o, float)
    for i in range(3):
        d = R[:, i] * length
        ax.quiver(*o, *d, color=AXIS[i], lw=lw, arrow_length_ratio=0.12, alpha=alpha, linestyle=ls)
        p = o + d * 1.12
        label = rf"$\hat {names[i]}_{{{sub}}}$" if sub else rf"$\hat {names[i]}$"
        ax.text(*p, label, color=AXIS[i], fontsize=fs, ha="center", va="center", alpha=alpha)


def box(ax, R=np.eye(3), o=(0, 0, 0), dims=(0.7, 1.0, 0.18), face="#e9dfc8", edge="#8a6d2b", spine=C["accent"], alpha=0.85):
    """一本书：长方体，书脊（沿自身 y 轴的一条棱）加粗着色。"""
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    a, b, c = (d / 2 for d in dims)
    V = np.array([[x, y, z] for x in (-a, a) for y in (-b, b) for z in (-c, c)])
    W = (R @ V.T).T + np.asarray(o)
    faces = [[0, 1, 3, 2], [4, 5, 7, 6], [0, 1, 5, 4], [2, 3, 7, 6], [0, 2, 6, 4], [1, 3, 7, 5]]
    ax.add_collection3d(Poly3DCollection([W[f] for f in faces], facecolor=face, edgecolor=edge, lw=0.6, alpha=alpha))
    s = W[[0, 2]]           # x=-a, z=-c 那条沿 y 的棱，与 x=-a,z=+c 一起构成书脊面
    s2 = W[[1, 3]]
    for e in (s, s2):
        ax.plot(*e.T, color=spine, lw=3.2)


def circle_arc(ax, center, u, v, r, a0, a1, color, lw=1.2, ls="-"):
    t = np.linspace(a0, a1, 60)
    P = np.asarray(center)[:, None] + r * (np.outer(u, np.cos(t)) + np.outer(v, np.sin(t)))
    ax.plot(*P, color=color, lw=lw, ls=ls)
    return P
