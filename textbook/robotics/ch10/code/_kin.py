"""第 10 章共用：叉积矩阵、基本转动、数值求导、柱面与球面基矢量、示意图的画法。以下划线开头，构建时不单独运行。"""
import math

import numpy as np

from bookout import COLORS

C = COLORS
AXIS = (C["x"], C["y"], C["z"])
V_COL = "#e07b00"      # 速度：橙
A_COL = "#c0392b"      # 加速度：红
G_COL = "#7a868d"      # 辅助线：灰


def skew(a):
    """叉积矩阵 [a]，式 (3.2.10)：[a] b = a × b。"""
    a = np.asarray(a, float)
    return np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])


def rotz(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1.0]])


def roty(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[c, 0, s], [0, 1.0, 0], [-s, 0, c]])


def rotx(t):
    c, s = math.cos(t), math.sin(t)
    return np.array([[1.0, 0, 0], [0, c, -s], [0, s, c]])


def d1(f, t, h=1e-4):
    """中心差商 (7.4.3)：f′(t) ≈ [f(t+h) − f(t−h)] / (2h)；f 可返回数组。"""
    return (np.asarray(f(t + h)) - np.asarray(f(t - h))) / (2 * h)


def d2(f, t, h=1e-3):
    """二阶中心差商：f″(t) ≈ [f(t+h) − 2f(t) + f(t−h)] / h²。"""
    return (np.asarray(f(t + h)) - 2 * np.asarray(f(t)) + np.asarray(f(t - h))) / (h * h)


def cyl_basis(phi):
    """柱面坐标的局部基 e_ρ、e_φ、e_z 在直角坐标系中的分量（式 (10.3.3)）。"""
    c, s = math.cos(phi), math.sin(phi)
    return np.array([c, s, 0.0]), np.array([-s, c, 0.0]), np.array([0, 0, 1.0])


def sph_basis(theta, phi):
    """球面坐标 (r, θ, φ)（ISO 80000-2：θ 为极角，φ 为方位角）的局部基 e_r、e_θ、e_φ（式 (10.4.3)）。"""
    st, ct, sp, cp = math.sin(theta), math.cos(theta), math.sin(phi), math.cos(phi)
    return (np.array([st * cp, st * sp, ct]), np.array([ct * cp, ct * sp, -st]), np.array([-sp, cp, 0.0]))


def to_sph(r):
    """直角坐标 → 球面坐标 (r, θ, φ)。"""
    x, y, z = r
    rr = math.sqrt(x * x + y * y + z * z)
    return rr, math.atan2(math.hypot(x, y), z), math.atan2(y, x)


# ---------------------------------------------------------------- 示意图

def arrow(ax, p, q, color, lw=1.6, z=3, ms=12, ls="-"):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="-|>", color=color, lw=lw, shrinkA=0, shrinkB=0,
                                                    mutation_scale=ms, linestyle=ls), zorder=z)


def oblique(p, s=1.0):
    """三维点的斜投影（x 指向左下，y 向右，z 向上），与动画 wq_anim.proj3 相同。"""
    x, y, z = (float(v) for v in p)
    return np.array([y - 0.55 * x, z - 0.35 * x]) * s


def arc(ax, c, r, a0, a1, color, lw=1.0, ls="-", n=60):
    t = np.linspace(a0, a1, n)
    ax.plot(c[0] + r * np.cos(t), c[1] + r * np.sin(t), color=color, lw=lw, ls=ls)
