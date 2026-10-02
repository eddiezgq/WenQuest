"""5.5 节的示意图。

图 5.5.1：相机-机械臂-工件的坐标链。机器人已到达抓取位姿；虚线箭头依次标出链中的各个变换。
图 5.5.2：相机安装角误差沿链放大：在 {w} 的 x–z 平面内看，光线偏转 δ，抓取点偏离约 δ 乘以杠杆长度。
"""
import math

import numpy as np

from _fig5 import C, arrow, axes3d, box3d, camera3, cylinder3, draw_ur, frame3, plane, table3
from _frames import DEG, P_WC, T, T_bt, T_og, T_wc, T_ws, inv, rot_z, ur_ik
from bookout import T as TT, figure, style

plt = style()

Tws, Twc = T_ws(), T_wc()
Two = T(rot_z(25 * DEG), (0.80, 0.45, 0.02))
Twg = Two @ T_og()
th = ur_ik(inv(Tws) @ Twg @ inv(T_bt()), np.array([0, -60, 100, -130, -90, 0]) * DEG)

# ---------------------------------------------------------------- 图 5.5.1
fig, ax = axes3d(plt, size=(7.6, 5.4), elev=22, azim=-64)
ax.set_position([0.0, -0.1, 1.0, 1.25])
table3(ax)
cylinder3(ax, Two, 0.04, 0.03)
pts, frames, tip = draw_ur(ax, Tws, th)
stand = np.array([[1.17, 0.40, 0.0], [1.17, 0.40, 0.98], [1.05, 0.40, 0.98], [1.05, 0.40, 0.92]])
ax.plot(*stand.T, color="#5b6b75", lw=2.2)
camera3(ax, Twc, 0.07)
Twb = frames[-1][1]
frame3(ax, np.eye(4), 0.15, "{w}", off=(-0.06, -0.06, -0.04))
frame3(ax, Tws, 0.12, "{s}", off=(0.03, 0.1, -0.05))
frame3(ax, Twb, 0.08, "{b}", off=(-0.05, -0.09, 0.05))
frame3(ax, Twc, 0.12, "{c}", off=(-0.02, -0.12, 0.06))
frame3(ax, Two, 0.09, "{o}", off=(0.11, -0.05, -0.02))


def chain_arrow(p, q, label, off, color="#d62728"):
    p, q = np.asarray(p, float), np.asarray(q, float)
    ax.plot(*np.c_[p, q], color=color, lw=1.2, ls="--")
    d = q - p
    ax.scatter(*q, color=color, s=10)
    m = p + 0.5 * d + np.asarray(off)
    ax.text(*m, label, fontsize=11, color=color, ha="center")


chain_arrow((0, 0, 0), Tws[:3, 3], r"$T_{ws}$", (0.0, -0.08, 0.04))
chain_arrow((0, 0, 0), Twc[:3, 3], r"$T_{wc}$", (0.02, 0.06, 0.05))
chain_arrow(Twc[:3, 3], Two[:3, 3], r"$T_{co}$", (0.08, 0.0, 0.02))
chain_arrow(Tws[:3, 3], Twb[:3, 3], r"$T_{sb}(\theta)$", (-0.12, 0.0, 0.08), color="#1f77b4")
ax.text2D(0.01, 0.06, TT(r"闭合条件：$T_{ws}\,T_{sb}(\theta)\,T_{bt} = T_{wc}\,T_{co}\,T_{og}$",
                         r"Closure: $T_{ws}\,T_{sb}(\theta)\,T_{bt} = T_{wc}\,T_{co}\,T_{og}$"), transform=ax.transAxes, fontsize=11)
box3d(ax, (-0.05, -0.05, 0.0), (1.25, 0.85, 0.95), zoom=1.0)
figure(fig, "fig5_5_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 5.5.2（x–z 平面，误差角放大画出）
fig, ax = plt.subplots(figsize=(6.6, 4.4))
cam = np.array([P_WC[0], P_WC[2]])
g = np.array([Twg[0, 3], Twg[2, 3]])
r = g - cam
dshow = 6 * DEG                                         # 为了看得清，图中把 0.5° 画成 6°
c, s = math.cos(dshow), math.sin(dshow)
g2 = cam + np.array([[c, -s], [s, c]]) @ r
ax.plot([-0.05, 1.25], [0, 0], color="#9aa6ad", lw=2)
ax.fill_between([0.70, 0.90], 0, 0.02, color="#e7d7a8")
ax.fill_between([0.76, 0.84], 0.02, 0.05, color="#b8860b", alpha=0.8)
ax.plot([1.17, 1.17, 1.05], [0, 0.98, 0.98], color="#5b6b75", lw=2)
ax.plot(*cam, "s", color="#444c52", ms=8)
arrow(ax, cam, g, C["ink"], 1.4)
arrow(ax, cam, g2, "#d62728", 1.4, ls="--")
ax.plot(*g, "o", color=C["ink"], ms=4)
ax.plot(*g2, "o", color="#d62728", ms=4)
tt = np.linspace(math.atan2(r[1], r[0]), math.atan2(r[1], r[0]) + dshow, 20)
ax.plot(cam[0] + 0.5 * np.cos(tt), cam[1] + 0.5 * np.sin(tt), color="#d62728", lw=1.2)
ax.text(cam[0] - 0.07, cam[1] - 0.6, r"$\delta$", color="#d62728", fontsize=13)
ax.text(cam[0] - 0.4, cam[1] - 0.45, r"$\rho$", fontsize=12)
ax.annotate("", xy=g2, xytext=g, arrowprops=dict(arrowstyle="<->", color="#d62728", lw=1.0, shrinkA=2, shrinkB=2))
ax.text((g[0] + g2[0]) / 2 - 0.02, g[1] - 0.12, r"$e \approx \delta\,\rho$", color="#d62728", fontsize=12, ha="center")
ax.text(cam[0] - 0.05, cam[1] + 0.03, TT("相机", "camera"), fontsize=10, ha="right")
ax.text(0.65, 0.09, TT("齿轮坯", "gear blank"), fontsize=9.5, color="#8a6d2b", ha="right")
ax.text(-0.02, 0.92, TT("名义光线（实线）与实际光线（虚线）", "nominal ray (solid) and actual ray (dashed)"), fontsize=9.5)
ax.text(-0.02, 0.84, TT("图中误差角放大画出", "error angle exaggerated in the drawing"), fontsize=9, color=C["muted"])
ax.text(-0.02, -0.08, TT("台面（{w} 的 x 轴）", "table top (x axis of {w})"), fontsize=9, color=C["muted"])
plane(ax, (-0.05, 1.3), (-0.14, 1.05))
figure(fig, "fig5_5_2")
plt.close(fig)
