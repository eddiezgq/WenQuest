"""3.3 节的示意图。

图 3.3.1：方向余弦：{b} 的 x 轴与 {a} 三根轴的夹角 α11、α21、α31，它们的余弦就是 R_ab 的第一列。
图 3.3.2：算例 3.3.2、3.3.3：俯视传送带的相机，机座坐标系 {a}、支架坐标系 {c}、相机坐标系 {b}，以及位移 d。
"""
import math

import numpy as np

from _vec import AXIS, C, arrow3, circle3, d, frame3, rot_x, rot_y, rot_z, sub3d, unit
from bookout import T, figure, style

plt = style()
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

# ---------------------------------------------------------------- 图 3.3.1
R = rot_z(d(25)) @ rot_y(d(-35)) @ rot_x(d(40))
fig = plt.figure(figsize=(9.6, 4.6))
ax = sub3d(fig, 121, elev=34, azim=-70, lim=0.85, zoom=1.35, center=(0.25, 0.25, 0.3))
frame3(ax, np.eye(3), length=1.0, sub="a", lw=1.4, alpha=0.9)
frame3(ax, R, length=0.85, sub="b", lw=2.4, fs=13, off=1.17)
xbv = R[:, 0]
labs = (r"$\alpha_{11}$", r"$\alpha_{21}$", r"$\alpha_{31}$")
for i in range(3):
    e = np.eye(3)[:, i]
    ang = math.acos(np.clip(e @ xbv, -1, 1))
    w = unit(xbv - (xbv @ e) * e)
    rr = 0.24 + 0.13 * i
    P = circle3(ax, np.zeros(3), e, w, rr, 0, ang, AXIS[i], 1.3)
    mid = P[:, len(P[0]) // (5 if i == 2 else 2)]
    ax.text(*(mid * (1.32 - 0.04 * i)), labs[i], color=AXIS[i], fontsize=12, ha="center")
ax.text2D(0.0, 0.97, T("(a) {b} 的 x 轴与 {a} 三根轴的夹角", "(a) Angles between x_b and the three axes of {a}"),
          transform=ax.transAxes, fontsize=10)
ax2 = fig.add_subplot(122)
ax2.axis("off")
ax2.text(0.0, 0.86, T("(b) 方向余弦矩阵：第 j 列是 {b} 的第 j 根轴", "(b) Direction cosine matrix: column j is axis j of {b}"), fontsize=10)
ax2.text(0.02, 0.535, r"$R_{ab}=$", fontsize=15)
# matplotlib 的 mathtext 不排矩阵，这里逐格写出
cells = [[r"$\cos\alpha_{%d%d}$" % (i + 1, j + 1) for j in range(3)] for i in range(3)]
for i in range(3):
    for j in range(3):
        ax2.text(0.25 + 0.22 * j, 0.68 - 0.13 * i, cells[i][j], fontsize=14, color=AXIS[i] if j == 0 else C["ink"])
ax2.plot([0.22, 0.21, 0.21, 0.22], [0.75, 0.75, 0.37, 0.37], color=C["ink"], lw=1.2)
ax2.plot([0.86, 0.87, 0.87, 0.86], [0.75, 0.75, 0.37, 0.37], color=C["ink"], lw=1.2)
ax2.add_patch(plt.Rectangle((0.235, 0.36), 0.2, 0.4, fc="none", ec=C["accent"], lw=1.2, ls="--"))
ax2.text(0.24, 0.27, T(r"第 1 列 = $\hat{\boldsymbol{x}}_b$ 在 {a} 中的分量", r"column 1 = $\hat{\boldsymbol{x}}_b$ written in {a}"), fontsize=10, color=C["accent"])
ax2.text(0.0, 0.14, T("第 i 行 = {a} 的第 i 根轴在 {b} 中的分量", "row i = axis i of {a} written in {b}"), fontsize=10, color=C["muted"])
ax2.text(0.0, 0.05, r"$\cos\alpha_{ij}$" + T(" = （{a} 的第 i 根轴）·（{b} 的第 j 根轴）", " = (axis i of {a}) · (axis j of {b})"), fontsize=11, color=C["muted"])
ax2.set_xlim(0, 1)
ax2.set_ylim(0, 1)
fig.subplots_adjust(wspace=0.0)
figure(fig, "fig3_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 3.3.2
c20, s20 = math.cos(d(20)), math.sin(d(20))
R_ab = np.column_stack([[0, -1.0, 0], [-c20, 0, s20], [-s20, 0, -c20]])
R_ac = rot_z(d(-90))
cam = np.array([0.55, 0.15, 0.75])                # 相机在 {a} 中的位置（示意，m）
d_b = np.array([0.12, -0.05, 0.60])
d_a = R_ab @ d_b
fig = plt.figure(figsize=(7.6, 5.6))
ax = sub3d(fig, 111, elev=8, azim=-62, lim=0.55, zoom=1.2, center=(0.45, 0.05, 0.42))
P = cam + d_a                                    # 零件在 {a} 中的位置
zt = P[2]                                        # 传送带面的高度
for yy in (-0.12, 0.18):                         # 传送带的两条边
    ax.plot([0.2, 0.95], [yy, yy], [zt, zt], color=C["muted"], lw=1.2)
ax.text(0.95, 0.2, zt + 0.02, T("传送带", "conveyor"), fontsize=9.5, color=C["muted"])
ax.add_collection3d(Poly3DCollection([[P + [-0.04, -0.04, 0], P + [0.04, -0.04, 0], P + [0.04, 0.04, 0], P + [-0.04, 0.04, 0]]],
                                     facecolor="#f3e2b3", edgecolor=C["accent"], alpha=0.9))
ax.text(*(P + [0.0, 0.06, -0.06]), T("零件", "part"), fontsize=10, color="#8a6d2b")
frame3(ax, np.eye(3), o=(0, 0, 0), length=0.25, sub="a", lw=1.6, fs=11)
ax.text(0.02, -0.12, -0.04, T("{a} 机座", "{a} base"), fontsize=10)
oc = cam + [0, 0, 0.2]
frame3(ax, R_ac, o=oc, length=0.12, sub="c", lw=1.1, fs=9.5, alpha=0.55)
ax.text(*(oc + [0.0, 0.06, 0.08]), T("{c} 支架", "{c} bracket"), fontsize=9.5, color=C["muted"])
ax.plot(*np.column_stack([oc, cam]), color=C["muted"], lw=3, alpha=0.5)
frame3(ax, R_ab, o=cam, length=0.2, sub="b", lw=2.0, fs=11)
ax.text(*(cam + [0.0, 0.12, 0.05]), T("{b} 相机", "{b} camera"), fontsize=10)
arrow3(ax, cam, d_a, C["ink"], 2.0, ratio=0.06)
ax.text(*(cam + 0.6 * d_a + [0.0, -0.06, 0]), r"$\boldsymbol{d}$", fontsize=15)
ax.plot([cam[0], cam[0]], [cam[1], cam[1]], [zt, cam[2]], ":", color=C["muted"], lw=0.8)
circle3(ax, cam, np.array([0, 0, -1.0]), unit(np.array([-1.0, 0, 0])), 0.14, 0, d(20), C["accent"], 1.2)
ax.text(*(cam + [0.0, 0.07, -0.13]), r"$20^\circ$", fontsize=11, color=C["accent"])
figure(fig, "fig3_3_2")
plt.close(fig)
