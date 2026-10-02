"""5.3 节的示意图。

图 5.3.1：同样的平移和转动，右乘（相对物体自身坐标系）与左乘（相对固定坐标系）的结果不同。
图 5.3.2：求逆的几何意义：{b} 的原点在 {a} 中为 p_ab；{a} 的原点在 {b} 中为 p_ba = −R_abᵀ p_ab。
"""
import math

import numpy as np

from _fig5 import C, arrow, frame2, plane
from _frames import DEG
from bookout import T as TT, figure, style

plt = style()


def se2(x, y, a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, x], [s, c, y], [0, 0, 1.0]])


def draw(ax, M, size, color, alpha=1.0):
    """位姿：原点一个圆点，x 轴（夹爪接近方向）一支同色箭头，y 轴一支细箭头。"""
    o = M[:2, 2]
    arrow(ax, o, o + size * M[:2, 0], color, 1.6)
    arrow(ax, o, o + 0.6 * size * M[:2, 1], color, 0.9)
    ax.plot(*o, "o", color=color, ms=4, alpha=alpha, zorder=6)


def gripper(ax, M, color, alpha=1.0):
    pts = np.array([[0.0, -0.18], [0.0, 0.18], [0.0, 0.18], [0.25, 0.18], [0.0, -0.18], [0.25, -0.18]])
    P = (M[:2, :2] @ pts.T).T + M[:2, 2]
    ax.plot(*P[[0, 1]].T, color=color, lw=3, alpha=alpha)
    ax.plot(*P[[2, 3]].T, color=color, lw=3, alpha=alpha)
    ax.plot(*P[[4, 5]].T, color=color, lw=3, alpha=alpha)


# ---------------------------------------------------------------- 图 5.3.1
T0 = se2(1.5, 0.9, 30 * DEG)
Rz = se2(0, 0, 90 * DEG)
Tx = se2(1.0, 0, 0)
fig, axs = plt.subplots(1, 2, figsize=(9.0, 4.2))
for k, ax in enumerate(axs):
    frame2(ax, (0, 0), 0, 0.7, "{s}", sub="s", fs=10, name_off=(-0.2, -0.3))
    gripper(ax, T0, C["ink"])
    draw(ax, T0, 0.5, C["ink"])
    ax.text(T0[0, 2] + 0.1, T0[1, 2] - 0.4, TT("起点 $T$", "start $T$"), fontsize=9.5, color=C["ink"])
    if k == 0:
        A, B = T0 @ Tx, T0 @ Rz
        ax.set_title(TT("(a) 右乘：相对工具自身的坐标系", "(a) Right-multiply: relative to the tool's own frame"), fontsize=10.5)
        t1, t2 = r"$T\,\mathrm{Trans}(x, 1)$", r"$T\,\mathrm{Rot}(z, 90^\circ)$"
    else:
        A, B = Tx @ T0, Rz @ T0
        ax.set_title(TT("(b) 左乘：相对基座坐标系 {s}", "(b) Left-multiply: relative to the base frame {s}"), fontsize=10.5)
        t1, t2 = r"$\mathrm{Trans}(x, 1)\,T$", r"$\mathrm{Rot}(z, 90^\circ)\,T$"
        a0 = math.atan2(T0[1, 2], T0[0, 2])
        r = math.hypot(T0[0, 2], T0[1, 2])
        tt = np.linspace(a0, a0 + math.pi / 2, 50)
        ax.plot(r * np.cos(tt), r * np.sin(tt), color="#1f77b4", lw=1.0, ls=":")
    gripper(ax, A, C["accent"], 0.9)
    draw(ax, A, 0.5, C["accent"])
    arrow(ax, T0[:2, 2], A[:2, 2], C["accent"], 1.0, ls=":")
    gripper(ax, B, "#1f77b4", 0.9)
    draw(ax, B, 0.5, "#1f77b4")
    ax.text(A[0, 2] + 0.05, A[1, 2] - 0.42, t1, fontsize=10, color=C["accent"])
    ax.text(B[0, 2] - 0.1, B[1, 2] + 0.6, t2, fontsize=10, color="#1f77b4", ha="center")
    plane(ax, (-1.4, 3.3), (-0.5, 2.8))
figure(fig, "fig5_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 5.3.2
fig, ax = plt.subplots(figsize=(6.0, 3.9))
Ob, ang = np.array([2.4, 1.1]), -60 * DEG
frame2(ax, (0, 0), 0, 0.9, "{a}", sub="a", name_off=(-0.15, -0.25))
frame2(ax, Ob, ang, 0.8, "{b}", sub="b", name_off=(-0.25, 0.25))
arrow(ax, (0.03, 0.02), Ob - np.array([0.03, 0.0]), C["accent"], 1.8)
arrow(ax, Ob + np.array([-0.06, 0.16]), (-0.06, 0.16), "#1f77b4", 1.8, ls="--")
ax.text(1.25, 0.25, r"$p_{ab}$" + TT("（在 {a} 中读）", " (read in {a})"), fontsize=10.5, color=C["accent"])
ax.text(0.55, 0.95, r"$p_{ba}=-R_{ab}^{\mathrm{T}}p_{ab}$" + TT("（在 {b} 中读）", " (read in {b})"), fontsize=10.5,
        color="#1f77b4", rotation=math.degrees(math.atan2(Ob[1], Ob[0])))
ax.text(-0.3, -0.7, TT("同一段距离，方向相反，并换到 {b} 的三根轴上读数", "Same distance, opposite direction, read along the axes of {b}"),
        fontsize=10, color=C["ink"])
plane(ax, (-0.5, 3.6), (-0.95, 2.1))
figure(fig, "fig5_3_2")
plt.close(fig)
