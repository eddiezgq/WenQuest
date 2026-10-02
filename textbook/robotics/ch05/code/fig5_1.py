"""5.1 节的示意图。

图 5.1.1：原点不同的两个坐标系 {a}、{b}，同一点 P；三个位置矢量构成三角形 O_a O_b P。
图 5.1.2：UR5e 工作站中的坐标系：工作台 {w}、基座 {s}、法兰 {b}、工具 {t}、相机 {c}、工件 {o}。
"""
import math

import numpy as np

from _fig5 import C, arrow, axes3d, box3d, camera3, cylinder3, draw_ur, equal3d, frame2, frame3, plane, table3
from _frames import DEG, T, T_bt, T_og, T_wc, T_ws, inv, rot_z, ur_ik
from bookout import T as TT, figure, style

plt = style()

# ---------------------------------------------------------------- 图 5.1.1
fig, ax = plt.subplots(figsize=(6.0, 4.3))
Oa, Ob, P = np.array([0.0, 0.0]), np.array([2.3, 0.8]), np.array([3.4, 2.75])
ang_b = 35 * DEG
frame2(ax, Oa, 0, 1.0, "{a}", sub="a", name_off=(-0.15, -0.2))
frame2(ax, Ob, ang_b, 0.9, "{b}", sub="b", name_off=(0.05, -0.28))
arrow(ax, Oa, P, C["ink"], 1.8)
arrow(ax, Oa, Ob, C["accent"], 1.8)
arrow(ax, Ob, P, "#1f77b4", 1.8)
ax.plot(*P, "o", color=C["ink"], ms=5, zorder=7)
ax.text(P[0] + 0.08, P[1] + 0.05, "P", fontsize=13)
ax.text(1.18, 1.75, r"$\overrightarrow{O_aP}$", fontsize=13, color=C["ink"], rotation=0)
ax.text(1.3, 0.22, r"$\overrightarrow{O_aO_b}$", fontsize=13, color=C["accent"])
ax.text(3.05, 1.55, r"$\overrightarrow{O_bP}$", fontsize=13, color="#1f77b4")
ax.text(0.15, 2.95, TT("在 {a} 中读：", "read in {a}:") + r"  $p_a$", fontsize=10.5, color=C["ink"])
ax.text(0.15, 2.65, TT("在 {a} 中读：", "read in {a}:") + r"  $p_{ab}$", fontsize=10.5, color=C["accent"])
ax.text(0.15, 2.35, TT("在 {b} 中读：", "read in {b}:") + r"  $p_b$", fontsize=10.5, color="#1f77b4")
ax.text(-0.35, -0.75, TT("矢量等式  " + r"$\overrightarrow{O_aP}=\overrightarrow{O_aO_b}+\overrightarrow{O_bP}$" + "  与坐标系无关",
                         "The vector equation " + r"$\overrightarrow{O_aP}=\overrightarrow{O_aO_b}+\overrightarrow{O_bP}$" + " holds in every frame"),
        fontsize=10.5, color=C["ink"])
plane(ax, (-0.5, 4.1), (-0.9, 3.2))
figure(fig, "fig5_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 5.1.2
Tws, Twc = T_ws(), T_wc()
Two = T(rot_z(25 * DEG), (0.80, 0.45, 0.02))
Tsb_goal = inv(Tws) @ Two @ T_og() @ inv(T_bt())
th = ur_ik(Tsb_goal, np.array([0, -60, 100, -130, -90, 0]) * DEG)

fig, ax = axes3d(plt, size=(7.4, 5.0), elev=24, azim=-58)
ax.set_position([0.0, -0.08, 1.0, 1.25])
table3(ax)
tray = np.array([[0.70, 0.37, 0.02], [0.90, 0.37, 0.02], [0.90, 0.53, 0.02], [0.70, 0.53, 0.02], [0.70, 0.37, 0.02]])
ax.plot(*tray.T, color="#8a6d2b", lw=0.9)
cylinder3(ax, Two, 0.04, 0.03)
pts, frames, tip = draw_ur(ax, Tws, th)
# 相机支架
stand = np.array([[1.17, 0.40, 0.0], [1.17, 0.40, 0.98], [1.05, 0.40, 0.98], [1.05, 0.40, 0.92]])
ax.plot(*stand.T, color="#5b6b75", lw=2.2)
camera3(ax, Twc, 0.07)
Twb = frames[-1][1]
Twt = Twb @ T_bt()
L = 0.13
frame3(ax, np.eye(4), 0.16, "{w}", off=(-0.05, -0.05, -0.05))
frame3(ax, Tws, L, "{s}", off=(0.05, 0.07, -0.05))
frame3(ax, Twb, 0.09, "{b}", off=(-0.04, -0.1, 0.06))
frame3(ax, Twt, 0.07, "{t}", off=(-0.11, -0.03, 0.02))
frame3(ax, Twc, L, "{c}", off=(-0.02, -0.12, 0.06))
frame3(ax, Two, 0.1, "{o}", off=(0.1, -0.06, -0.02))
ax.text(1.0, -0.07, 0.0, TT("工作台", "worktable"), fontsize=9, color=C["muted"])
ax.text(0.72, 0.10, 0.0, TT("料盘与齿轮坯", "tray and gear blank"), fontsize=9, color="#8a6d2b")
ax.text(1.19, 0.44, 0.45, TT("相机支架", "camera stand"), fontsize=9, color=C["muted"])
box3d(ax, (-0.05, -0.05, 0.0), (1.25, 0.85, 0.95), zoom=1.12)
figure(fig, "fig5_1_2")
plt.close(fig)
