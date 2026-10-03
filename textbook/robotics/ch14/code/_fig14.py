"""第 14 章示意图共用：平面臂、三维示意（轴线、圆弧、箭头）、UR5e 与球形手腕六轴臂的连杆折线。以下划线开头，构建时不单独运行。"""
import math

import numpy as np

from _ik import SW, SW_Q, SW_S, act, exp6, ur_points
from bookout import COLORS

C = COLORS
BLUE2 = "#6baed6"
PALE = "#dbe9f6"


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


def draw_arm(ax, pts, color, lw=6, alpha=1.0, z=3, ls="-", jr=0.018):
    import matplotlib.patches as mp
    ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, alpha=alpha, solid_capstyle="round", zorder=z, ls=ls)
    for p in pts[:-1]:
        ax.add_patch(mp.Circle(p, jr, facecolor="white", edgecolor=color, lw=1.4, zorder=z + 1, alpha=alpha))
    ax.plot(*pts[-1], "o", color=color, ms=4, alpha=alpha, zorder=z + 1)


def base_mark(ax, p=(0, 0), s=0.03):
    import matplotlib.patches as mp
    ax.add_patch(mp.Polygon([[p[0] - s, p[1] - s * 1.2], [p[0] + s, p[1] - s * 1.2], [p[0] + s * 0.5, p[1]], [p[0] - s * 0.5, p[1]]],
                            closed=True, facecolor=C["muted"], edgecolor="none", zorder=2))


def arc(ax, c, r, a0, a1, color, lw=1.2, ls="-", arrow=False, z=4):
    t = np.linspace(a0, a1, 50)
    ax.plot(c[0] + r * np.cos(t), c[1] + r * np.sin(t), color=color, lw=lw, ls=ls, zorder=z)
    if arrow:
        end = np.array([c[0] + r * math.cos(a1), c[1] + r * math.sin(a1)])
        d = np.sign(a1 - a0) * np.array([-math.sin(a1), math.cos(a1)])
        ax.annotate("", xy=end + 0.003 * d, xytext=end - 0.025 * d,
                    arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=9), zorder=z)


def arrow2(ax, p, q, color, lw=1.3, ms=10, z=5):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, mutation_scale=ms, shrinkA=0, shrinkB=0), zorder=z)


# ---------------------------------------------------------------- 三维
def axes3d(plt, size=(5.6, 4.4), elev=22, azim=-120, fig=None, pos=111):
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


def line3d(ax, p, u, t0, t1, color, lw=1.2, ls="-", alpha=1.0):
    p, u = np.asarray(p, float), np.asarray(u, float)
    P = np.array([p + t0 * u, p + t1 * u])
    ax.plot(*P.T, color=color, lw=lw, ls=ls, alpha=alpha)


def circle3d(ax, c, w, r, color, lw=1.0, ls="-", a0=0.0, a1=2 * math.pi, e1=None, alpha=1.0):
    """以 c 为圆心、法向 w、半径 r 的圆（或圆弧，从 e1 方向量起）。"""
    w = np.asarray(w, float) / np.linalg.norm(w)
    if e1 is None:
        h = np.array([1.0, 0, 0]) if abs(w[0]) < 0.9 else np.array([0, 1.0, 0])
        e1 = np.cross(w, h)
    e1 = np.asarray(e1, float)
    e1 = e1 - w * (w @ e1)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(w, e1)
    t = np.linspace(a0, a1, 120)
    P = np.array([c + r * (math.cos(s) * e1 + math.sin(s) * e2) for s in t])
    ax.plot(*P.T, color=color, lw=lw, ls=ls, alpha=alpha)
    return P


def arrow3d(ax, p, d, color, lw=1.6, ratio=0.2):
    ax.quiver(*p, *d, color=color, lw=lw, arrow_length_ratio=ratio)


def label3d(ax, p, text, color=None, fs=10, **kw):
    ax.text(*p, text, fontsize=fs, color=color or C["ink"], **kw)


# ---------------------------------------------------------------- 连杆折线
def ur_chain(theta):
    """UR5e 的连杆折线（与 _ik.ur_points 相同）。"""
    return ur_points(theta)


def sw_chain(theta):
    """球形手腕六轴臂的连杆折线：基座、肩、肘、腕心、法兰中心。"""
    Es = [np.eye(4)]
    for S, t in zip(SW_S, theta):
        Es.append(Es[-1] @ exp6(S, t))
    pts = [(0, np.zeros(3)), (1, SW_Q[1]), (2, SW_Q[2]), (3, SW_Q[3]), (6, SW_Q[3] + np.array([SW["D6"], 0, 0]))]
    return np.array([act(Es[k], p) for k, p in pts])


def draw_chain(ax, P, color, lw=5, alpha=1.0, joints=True, js=18):
    ax.plot(*P.T, color=color, lw=lw, alpha=alpha, solid_capstyle="round")
    if joints:
        ax.scatter(*P[1:-1].T, s=js, color="white", edgecolor=color, linewidths=1.0, alpha=alpha, depthshade=False, zorder=5)
    ax.scatter(*P[-1], s=js, color=color, alpha=alpha, depthshade=False)


def floor3d(ax, half=0.5, z=0.0, color="#e9ecef"):
    xs = np.array([-half, half])
    X, Y = np.meshgrid(xs, xs)
    ax.plot_surface(X, Y, np.full_like(X, z), color=color, alpha=0.35, linewidth=0, shade=False)
