"""13.2 节的示意图。

图 13.2.1：建系的三种特殊情形。(a) 相邻两轴相交；(b) 相邻两轴平行；(c) 移动关节。
图 13.2.2：SCARA 的连杆坐标系（表 13.2.1 中的表 B），零位。
图 13.2.3：UR5e 的连杆坐标系 {0}…{6}，零位（由表 12.1.1 的轴按 13.2.2 节的步骤生成，数据与程序 13.2.1 相同）。
"""
import math

import numpy as np

from _dh import Model, fk_sdh, lines_to_sdh, ur_poe
from _fig13 import C, arc3d, equal3d, frame3d, line3d
from bookout import T, figure, style

plt = style()
GREY, NORM = "#5b6670", C["accent"]

# ---------------------------------------------------------------- 图 13.2.1 三种特殊情形
fig = plt.figure(figsize=(11.0, 4.0))
# (a) 相交：轴 i 竖直，轴 i+1 水平，交于 P
ax = fig.add_subplot(131, projection="3d")
ax.view_init(elev=20, azim=-60)
ax.set_axis_off()
P = np.array([0, 0, 0.5])
line3d(ax, (0, 0, 0), (0, 0, 1), -0.1, 1.0, GREY, lw=2.2)
u2 = np.array([0, 1.0, 0])
line3d(ax, P, u2, -0.55, 0.55, GREY, lw=2.2)
F = np.eye(4)
F[:3, 0], F[:3, 1], F[:3, 2], F[:3, 3] = [1, 0, 0], [0, 0, 1], [0, -1, 0], P
F[:3, 2] = u2
F[:3, 1] = np.cross(u2, [1, 0, 0])
frame3d(ax, F, 0.3, "", names=("x_i", None, "z_i"))
frame3d(ax, np.eye(4), 0.25, "", names=(None, None, "z_{i-1}"))
ax.text(0.04, 0.0, 1.02, T("轴 $i$", "axis $i$"), fontsize=10, color=GREY)
ax.text(0.0, 0.6, 0.5, T("轴 $i+1$", "axis $i+1$"), fontsize=10, color=GREY)
ax.text2D(0.5, 0.02, T("原点在交点，$a_i = 0$；$x_i$ 沿 $\\pm z_{i-1}\\times z_i$", "origin at the intersection, $a_i = 0$; $x_i$ along $\\pm z_{i-1}\\times z_i$"),
          transform=ax.transAxes, fontsize=9.5, ha="center")
equal3d(ax, [[0, 0, -0.1], [0, 0, 1.0], P - 0.55 * u2, P + 0.55 * u2, [0.4, 0, 0.5]], pad=0.02, zoom=1.2)
ax.set_title(T("(a) 相邻两轴相交", "(a) Adjacent axes intersect"), fontsize=10)

# (b) 平行：两条竖直轴，几条公垂线，选过 o_{i-1} 的那一条
ax = fig.add_subplot(132, projection="3d")
ax.view_init(elev=20, azim=-60)
ax.set_axis_off()
line3d(ax, (0, 0, 0), (0, 0, 1), -0.1, 1.0, GREY, lw=2.2)
line3d(ax, (0.7, 0, 0), (0, 0, 1), -0.1, 1.0, GREY, lw=2.2)
for h in (0.3, 0.55, 0.8):
    ax.plot([0, 0.7], [0, 0], [h, h], color=C["muted"], lw=1.0, ls=":")
ax.plot([0, 0.7], [0, 0], [0, 0], color=NORM, lw=1.8, ls="--")
frame3d(ax, np.eye(4), 0.22, "", names=("x_{i-1}", None, "z_{i-1}"))
F = np.eye(4)
F[:3, 3] = [0.7, 0, 0]
frame3d(ax, F, 0.22, "", names=("x_i", None, "z_i"))
ax.text(0.12, 0.0, 0.9, T("公垂线有无穷多条", "infinitely many normals"), fontsize=9.5, color=C["muted"])
ax.text2D(0.5, 0.02, T("取过 $o_{i-1}$ 的一条（虚线）：$d_i = 0$", "take the one through $o_{i-1}$ (dashed): $d_i = 0$"),
          transform=ax.transAxes, fontsize=9.5, ha="center", color=NORM)
equal3d(ax, [[0, 0, -0.1], [0, 0, 1.0], [0.7, 0, 1.0], [0.7, 0, -0.1]], pad=0.02, zoom=1.2)
ax.set_title(T("(b) 相邻两轴平行", "(b) Adjacent axes parallel"), fontsize=10)

# (c) 移动关节：只有方向有意义，可以平移到任何位置
ax = fig.add_subplot(133, projection="3d")
ax.view_init(elev=20, azim=-60)
ax.set_axis_off()
for x0, al in ((0.0, 1.0), (0.35, 0.35), (0.7, 0.35)):
    line3d(ax, (x0, 0, 0), (0, 0, -1), -1.0, 0.0, GREY if al == 1.0 else C["muted"], lw=2.2 if al == 1.0 else 1.2,
           ls="-" if al == 1.0 else "--", alpha=al)
ax.quiver(0, 0, 0.75, 0, 0, -0.35, color=C["z"], lw=2.2, arrow_length_ratio=0.25)
ax.text(0.05, 0.0, 0.62, "$d_i$", fontsize=12, color=C["z"])
ax.text(0.05, 0.0, 1.02, T("移动方向", "sliding direction"), fontsize=9.5, color=GREY)
ax.text2D(0.5, 0.02, T("只有方向确定，轴线可以平移", "only the direction counts; the line may be shifted"),
          transform=ax.transAxes, fontsize=9.5, ha="center", color=C["ink"])
equal3d(ax, [[0, 0, -0.1], [0, 0, 1.0], [0.7, 0, 1.0], [0.7, 0, -0.1]], pad=0.02, zoom=1.2)
ax.set_title(T("(c) 移动关节", "(c) Prismatic joint"), fontsize=10)
figure(fig, "fig13_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 13.2.2 SCARA
pi = math.pi
tabB = [(0.35, 0.0, 0.4, 0.0), (0.25, pi, 0.0, 0.0), (0.0, pi, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)]
offB = [0.0, 0.0, 0.158, 0.0]
kinds = ["R", "R", "P", "R"]
Fs = fk_sdh(tabB, np.zeros(4), kinds, offB, frames=True)
fig = plt.figure(figsize=(7.2, 4.4))
ax = fig.add_subplot(111, projection="3d")
ax.view_init(elev=18, azim=-70)
ax.set_axis_off()
body = np.array([[0, 0, 0], [0, 0, 0.4], [0.35, 0, 0.4], [0.35, 0, 0.448], [0.6, 0, 0.448], [0.6, 0, 0.242]])
ax.plot(*body.T, color="#9aa6ad", lw=7, solid_capstyle="round", alpha=0.8)
for x0, z0, z1 in ((0.0, -0.02, 0.62), (0.35, 0.3, 0.62), (0.6, 0.15, 0.62)):
    ax.plot([x0, x0], [0, 0], [z0, z1], color=GREY, lw=1.0, ls="-.")
offs = {0: (-0.1, 0.0, -0.06), 1: (-0.07, 0.0, 0.06), 2: (0.04, 0.0, 0.05), 3: (0.05, 0.0, -0.05), 4: (0.05, 0.0, -0.05)}
for i, F in enumerate(Fs):
    if i == 4:
        continue
    frame3d(ax, F, 0.1, "{%d}" % i, fs=10, off=offs[i])
ax.text2D(0.5, 0.06, T("零位时 {4} 与 {3} 重合（$d_4 = 0$），随 $\\theta_4$ 转动；{3} 在工具安装面中心，随丝杠升降",
                       "At home {4} coincides with {3} ($d_4 = 0$) and turns with $\\theta_4$; {3} is at the tool mount and moves with the screw"),
          transform=ax.transAxes, fontsize=9, color=C["ink"], ha="center")
ax.text(-0.05, 0.0, 0.66, T("轴 1", "axis 1"), fontsize=9.5, color=GREY)
ax.text(0.3, 0.0, 0.66, T("轴 2", "axis 2"), fontsize=9.5, color=GREY)
ax.text(0.52, 0.0, 0.66, T("轴 3、4", "axes 3, 4"), fontsize=9.5, color=GREY)
equal3d(ax, np.r_[body, [[0.7, 0.1, 0.65], [0, -0.1, 0.1]]], pad=0.0, zoom=1.5)
figure(fig, "fig13_2_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 13.2.3 UR5e 的 {0}…{6}
tab, S, M = ur_poe()
axes = [("R", np.asarray(w, float), np.asarray(q, float)) for w, q in tab]
rows, F = lines_to_sdh(axes, M[:3, 3])
ur = Model("B-ARM-UR5E", "base", "wrist_3_link", (0, 0.1, 0))
qs = [a[2] for a in ur.axes()]
path = [np.zeros(3), qs[0], qs[1], qs[1] + np.array([-0.425, 0, 0]), qs[2], qs[2] + np.array([-0.392, 0, 0]),
        qs[3], qs[4], qs[5], M[:3, 3]]
P = np.array(path)
fig = plt.figure(figsize=(8.4, 5.0))
ax = fig.add_subplot(111, projection="3d")
ax.view_init(elev=24, azim=-35)
ax.set_axis_off()
ax.plot(*P.T, color="#c3cbd0", lw=8, solid_capstyle="round", alpha=0.7)
for i, (k, w, q) in enumerate(axes):
    line3d(ax, q, w, -0.12, 0.12, GREY, lw=1.0, ls="-.")
offs = {0: (0.03, 0.03, -0.07), 1: (0.03, 0.04, 0.03), 2: (0.03, 0.04, 0.03), 3: (0.05, 0.05, 0.03),
        4: (0.02, -0.02, 0.06), 5: (0.04, 0.03, -0.06), 6: (0.0, -0.07, -0.05)}
for i, Fi in enumerate(F):
    frame3d(ax, Fi, 0.09, "{%d}" % i, fs=10, off=offs[i], lw=1.4)
ax.text2D(0.0, 0.1, T("{1}、{2}、{3} 的原点都在 y = 0 的平面内，并不在关节实物的中心；{6} 在法兰盘中心，$z_6$ 沿法兰法线向外",
                       "Origins of {1}, {2}, {3} lie in the plane y = 0, not at the joint centres; {6} is at the flange centre, $z_6$ along the flange normal"),
          transform=ax.transAxes, fontsize=8.8)
equal3d(ax, np.r_[P, [[0.05, 0.05, 0.25]]], pad=0.0, zoom=1.75)
figure(fig, "fig13_2_3")
plt.close(fig)
