"""第 2 章共用：平面 2R、3R 臂（连杆长度取 UR5e 的大臂与小臂，与第 12 章相同）、示意图的画法。
以下划线开头，构建时不单独运行。"""
import math

import numpy as np

from bookout import COLORS

C = COLORS
L2R = (0.425, 0.392)          # 平面 2R 臂：L1、L2，m
L3R = (0.425, 0.392, 0.1)     # 平面 3R 臂：L1、L2、L3，m（与 12.1 节相同）


def d(deg):
    return math.radians(deg)


def rot2(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s], [s, c]])


def arm_points(th, lengths):
    """平面串联臂：各关节中心与末端的位置（每个关节角相对前一连杆，rad）。"""
    pts, a = [np.zeros(2)], 0.0
    for t, l in zip(th, lengths):
        a += t
        pts.append(pts[-1] + l * np.array([math.cos(a), math.sin(a)]))
    return np.array(pts)


def jac(th, lengths):
    """平面串联臂末端位置的雅可比矩阵（2×n）：第 i 列 = 关节 i 单独以 1 rad/s 转动时末端的速度，
    即把“关节 i 指向末端”的矢量逆时针转 90°。"""
    pts = arm_points(th, lengths)
    tip = pts[-1]
    cols = []
    for i in range(len(th)):
        r = tip - pts[i]
        cols.append([-r[1], r[0]])
    return np.array(cols).T


def jac_formula_2r(th, lengths=L2R):
    """2R 臂雅可比矩阵的显式公式（式 (2.1.9)），用来与 jac() 互相核对。"""
    l1, l2 = lengths
    t1, t12 = th[0], th[0] + th[1]
    return np.array([[-l1 * math.sin(t1) - l2 * math.sin(t12), -l2 * math.sin(t12)],
                     [l1 * math.cos(t1) + l2 * math.cos(t12), l2 * math.cos(t12)]])


# ---------------------------------------------------------------- 画图

def arrow(ax, p, q, color, lw=1.6, z=3, ms=12):
    ax.annotate("", xy=tuple(q), xytext=tuple(p),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0, mutation_scale=ms), zorder=z)


def draw_arm(ax, pts, color, lw=6, alpha=1.0, z=3, ls="-"):
    import matplotlib.patches as mp
    ax.plot(pts[:, 0], pts[:, 1], color=color, lw=lw, alpha=alpha, solid_capstyle="round", zorder=z, ls=ls)
    for p in pts[:-1]:
        ax.add_patch(mp.Circle(p, 0.018, facecolor="white", edgecolor=color, lw=1.4, zorder=z + 1, alpha=alpha))
    ax.plot(*pts[-1], "o", color=color, ms=4, alpha=alpha, zorder=z + 1)


def base(ax, p=(0, 0), w=0.06):
    import matplotlib.patches as mp
    ax.add_patch(mp.Polygon([[p[0] - w, p[1] - 0.6 * w], [p[0] + w, p[1] - 0.6 * w], [p[0] + 0.45 * w, p[1]], [p[0] - 0.45 * w, p[1]]],
                            closed=True, facecolor="#c9d0d5", edgecolor=C["muted"], lw=0.8, zorder=2))


def ellipse_pts(A, n=200):
    """单位圆在 A 作用下的像。"""
    t = np.linspace(0, 2 * math.pi, n)
    return A @ np.vstack([np.cos(t), np.sin(t)])
