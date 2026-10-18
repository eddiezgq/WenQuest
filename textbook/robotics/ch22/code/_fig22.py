"""第 22 章示意图共用：平面臂、三维示意（坐标系、箭头）、UR5e 的连杆折线、上下料工位（料架、卡盘、夹爪与轴）。以下划线开头，构建时不单独运行。"""
import math

import numpy as np

from _traj import GRIP_L, P_CHUCK, P_PICK, TBT, act, exp6, tcp_fk, ur_fk, ur_points
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


def draw_chain(ax, P, color, lw=5, alpha=1.0, joints=True, js=18):
    ax.plot(*P.T, color=color, lw=lw, alpha=alpha, solid_capstyle="round")
    if joints:
        ax.scatter(*P[1:-1].T, s=js, color="white", edgecolor=color, linewidths=1.0, alpha=alpha, depthshade=False, zorder=5)
    ax.scatter(*P[-1], s=js, color=color, alpha=alpha, depthshade=False)


def floor3d(ax, half=0.5, z=0.0, color="#e9ecef"):
    xs = np.array([-half, half])
    X, Y = np.meshgrid(xs, xs)
    ax.plot_surface(X, Y, np.full_like(X, z), color=color, alpha=0.35, linewidth=0, shade=False)


def frame2d(ax, T, length, color=None, lw=1.5, label=None, fs=10, z=6, off=(0.012, -0.03)):
    """平面坐标系：x 轴红、y 轴绿（全书约定）。T 为 3×3 的 SE(2) 矩阵。"""
    o, R = T[:2, 2], T[:2, :2]
    for k, c in ((0, C["x"]), (1, C["y"])):
        e = o + length * R[:, k]
        ax.annotate("", xy=e, xytext=o, arrowprops=dict(arrowstyle="-|>", color=c, lw=lw, mutation_scale=9, shrinkA=0, shrinkB=0), zorder=z)
    if label:
        ax.text(o[0] + off[0], o[1] + off[1], label, fontsize=fs, color=color or C["ink"], zorder=z + 1)


def logaxis(ax):
    ax.set_yscale("log")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, which="major", color="#e6e6e6", lw=0.6)


# ---------------------------------------------------------------- 本章：曲线图的样式、上下料工位
LIM = "#9aa4ab"            # 限值（虚线）
COL3 = "#1f77b4"           # 三次
COL5 = "#d9730d"           # 五次
COLL = "#7a868d"           # 直线插值
SHAFT_L, SHAFT_TOP = 0.182, 0.04     # SH-301 坯料长 182 mm（数字工厂工艺规程 factory/digital/std/SH-301_process.yaml）、夹持点到轴端的距离（示意值）


def curves(ax, xlabel=None, ylabel=None):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, color="#ececec", lw=0.6)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)


def shaft_pts(Tst):
    """夹在 TCP 处的轴：轴线沿 z_t，从 TCP 往回 SHAFT_TOP，往前 SHAFT_L − SHAFT_TOP。"""
    z, p = Tst[:3, 2], Tst[:3, 3]
    return np.array([p - SHAFT_TOP * z, p + (SHAFT_L - SHAFT_TOP) * z])


def draw_tool(ax, theta, color, lw=3, alpha=1.0, shaft=True):
    """法兰盘到 TCP 的夹爪（线段）和夹着的轴（粗线）。"""
    Tb = ur_fk(theta)
    Tt = Tb @ TBT
    ax.plot(*np.array([Tb[:3, 3], Tt[:3, 3]]).T, color=color, lw=lw, alpha=alpha, solid_capstyle="round")
    if shaft:
        S = shaft_pts(Tt)
        ax.plot(*S.T, color="#8c6d1f", lw=lw + 2, alpha=alpha, solid_capstyle="butt")


def box3d(ax, lo, hi, color, alpha=0.18, edge=None, lw=0.6):
    """轴对齐的长方体（料架、车床床头箱等的示意）。"""
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    V = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]])
    F = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [2, 3, 7, 6], [1, 2, 6, 5], [0, 3, 7, 4]]
    pc = Poly3DCollection([V[f] for f in F], facecolor=color, edgecolor=edge or color, linewidths=lw, alpha=alpha)
    ax.add_collection3d(pc)


def workcell(ax, alpha=0.16):
    """上下料工位（示意值）：料架（抓取点下方）与车床的床头箱和卡盘（主轴沿 x_s，卡盘端面朝 +x_s）。"""
    px, py, pz = P_PICK
    box3d(ax, (px - 0.10, py - 0.08, pz - SHAFT_L + SHAFT_TOP - 0.06), (px + 0.10, py + 0.08, pz - SHAFT_L + SHAFT_TOP + 0.05),
          "#8c6d1f", alpha)
    cx, cy, cz = P_CHUCK
    box3d(ax, (cx - 0.36, cy - 0.10, cz - 0.16), (cx - 0.12, cy + 0.10, cz + 0.14), "#5d6b73", alpha)
    circle3d(ax, P_CHUCK + np.array([-0.02, 0, 0]), (1, 0, 0), 0.07, "#5d6b73", lw=1.2)
    circle3d(ax, P_CHUCK + np.array([-0.12, 0, 0]), (1, 0, 0), 0.07, "#5d6b73", lw=0.8)
    for a in np.linspace(0, 2 * math.pi, 7)[:-1]:
        e = np.array([0, math.cos(a), math.sin(a)]) * 0.07
        ax.plot(*np.array([P_CHUCK + e + (-0.02, 0, 0), P_CHUCK + e + (-0.12, 0, 0)]).T, color="#5d6b73", lw=0.6)


def base_frame(ax, L=0.15):
    """基座坐标系 {s}：x 红、y 绿、z 蓝。"""
    for k, c, n in ((0, C["x"], "$x_s$"), (1, C["y"], "$y_s$"), (2, C["z"], "$z_s$")):
        d = np.zeros(3)
        d[k] = L
        ax.quiver(0, 0, 0, *d, color=c, lw=1.4, arrow_length_ratio=0.2)
        ax.text(*(d * 1.25 + (np.array([-0.06, -0.04, 0.0]) if k == 2 else 0)), n, color=c, fontsize=10)
