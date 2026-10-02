"""第 5 章示意图共用：平面坐标系、三维坐标系、UR5e 骨架、工作台、相机、齿轮坯的画法。以下划线开头，构建时不单独运行。"""
import math

import numpy as np

from _frames import T, T_bt, T_wc, T_ws, inv, ur_edges_from_table
from bookout import COLORS

C = COLORS
AX = (C["x"], C["y"], C["z"])


# ---------------------------------------------------------------- 平面

def arrow(ax, p, q, color, lw=1.5, z=4, ms=11, ls="-"):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0,
                                                    mutation_scale=ms, linestyle=ls), zorder=z)


def frame2(ax, o, ang, size, name="", names=("x", "y"), sub="", fs=11, lw=1.5, name_off=(-0.12, -0.14), alpha=1.0):
    """平面坐标系：x 红、y 绿，原点一个小圆点，旁边写名字。"""
    o = np.asarray(o, float)
    for k in range(2):
        a = ang + k * math.pi / 2
        q = o + size * np.array([math.cos(a), math.sin(a)])
        arrow(ax, o, q, AX[k], lw)
        lab = f"${names[k]}_{{{sub}}}$" if sub else f"${names[k]}$"
        ax.text(*(o + 1.13 * size * np.array([math.cos(a), math.sin(a)]) + np.array([-0.03, -0.03]) * size),
                lab, color=AX[k], fontsize=fs, alpha=alpha)
    ax.plot(*o, "o", color=C["ink"], ms=3.5, zorder=6)
    if name:
        ax.text(o[0] + name_off[0] * size, o[1] + name_off[1] * size, name, fontsize=fs, color=C["ink"], ha="center")


def plane(ax, xlim, ylim):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)


# ---------------------------------------------------------------- 三维

def axes3d(plt, size=(6.4, 4.6), elev=24, azim=-60):
    fig = plt.figure(figsize=size)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_proj_type("ortho")
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


def frame3(ax, Tm, size, label="", fs=10, off=(0, 0, -0.05), lw=1.6, color=None):
    o = Tm[:3, 3]
    for k in range(3):
        ax.quiver(*o, *(Tm[:3, k] * size), color=AX[k], lw=lw, arrow_length_ratio=0.22)
    if label:
        ax.text(*(o + np.asarray(off)), label, fontsize=fs, color=color or C["ink"], ha="center", va="center")


def table3(ax, Tw=np.eye(4), w=1.2, d=0.8, color="#d9dee2"):
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    P = np.array([[0, 0, 0], [w, 0, 0], [w, d, 0], [0, d, 0]], float)
    P = (Tw[:3, :3] @ P.T).T + Tw[:3, 3]
    ax.add_collection3d(Poly3DCollection([P], facecolor=color, edgecolor="#9aa6ad", lw=0.8, alpha=0.45))


def cylinder3(ax, Tm, r, h, color="#b8860b", n=40, alpha=0.75):
    """圆柱（齿轮坯）：底面中心在 Tm 的原点，轴沿 Tm 的 z 轴。"""
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    t = np.linspace(0, 2 * math.pi, n, endpoint=False)
    bot = np.c_[r * np.cos(t), r * np.sin(t), np.zeros(n)]
    top = bot + [0, 0, h]
    tf = lambda P: (Tm[:3, :3] @ P.T).T + Tm[:3, 3]
    B, U = tf(bot), tf(top)
    sides = [[B[i], B[(i + 1) % n], U[(i + 1) % n], U[i]] for i in range(n)]
    ax.add_collection3d(Poly3DCollection(sides + [U], facecolor=color, edgecolor="none", alpha=alpha))


def camera3(ax, Tm, size=0.08, color="#444c52"):
    """相机：一个小四棱锥，锥顶在光心，沿 z_c 张开。"""
    o = Tm[:3, 3]
    R = Tm[:3, :3]
    cs = [R @ np.array([sx * size * 0.7, sy * size * 0.5, size]) + o for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1))]
    for c in cs:
        ax.plot(*np.c_[o, c], color=color, lw=1.0)
    P = np.array(cs + [cs[0]])
    ax.plot(*P.T, color=color, lw=1.0)


def ur_points(Tws, theta):
    """UR5e 骨架：各连杆坐标系的原点（{w} 中），从基座到法兰，再到夹爪指尖。"""
    M = Tws.copy()
    pts = [M[:3, 3].copy()]
    frames = []
    for child, parent, Tm in ur_edges_from_table(theta):
        M = M @ Tm
        pts.append(M[:3, 3].copy())
        frames.append((child, M.copy()))
    tip = M @ T_bt()
    return np.array(pts), frames, tip


def draw_ur(ax, Tws, theta, color="#9aa6ad", lw=6, tool=True):
    pts, frames, tip = ur_points(Tws, theta)
    ax.plot(*pts.T, color=color, lw=lw, solid_capstyle="round", alpha=0.9)
    if tool:
        fl = frames[-1][1]
        ax.plot(*np.c_[fl[:3, 3], tip[:3, 3]], color="#5b6b75", lw=3.5, solid_capstyle="round")
    # 底座
    t = np.linspace(0, 2 * math.pi, 40)
    o = Tws[:3, 3]
    ax.plot(o[0] + 0.075 * np.cos(t), o[1] + 0.075 * np.sin(t), o[2] + 0 * t, color="#5b6b75", lw=1.2)
    return pts, frames, tip


def workcell():
    """工作站中各坐标系相对 {w} 的位姿（不含工件）。"""
    return {"w": np.eye(4), "s": T_ws(), "c": T_wc()}


__all__ = ["C", "AX", "arrow", "frame2", "plane", "axes3d", "equal3d", "frame3", "table3", "cylinder3", "camera3",
           "ur_points", "draw_ur", "workcell", "inv", "T", "box3d"]


def box3d(ax, lo, hi, zoom=1.0):
    """按实际比例显示一个长方体范围（三个方向的单位长度相同），不浪费空白。"""
    lo, hi = np.asarray(lo, float), np.asarray(hi, float)
    ax.set_xlim(lo[0], hi[0])
    ax.set_ylim(lo[1], hi[1])
    ax.set_zlim(lo[2], hi[2])
    ax.set_box_aspect(tuple(hi - lo), zoom=zoom)

