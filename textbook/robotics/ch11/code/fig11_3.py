"""11.3 节的示意图。

图 11.3.1：(a) 正方形 [−180°, 180°)²，左右两边、上下两边分别粘合；(b) 粘合后的环面 T²。两图中画出钟表两针的构型曲线 θm = 12 θh。
图 11.3.2：(a) 平面 2R 臂、圆形障碍物、起点与终点构型；(b) 构型空间：障碍物占据的区域（灰），直线路径（红，碰撞）与跨过 ±180° 的最短路径（绿）。
"""
import math

import numpy as np

from _fig11 import C, plane
from bookout import T, figure, style
from _ch11 import L1, L2, OBS_C, OBS_R, collide, fk2, wrap

plt = style()

# ---------------------------------------------------------------- 图 11.3.1
fig = plt.figure(figsize=(9.6, 4.2))
ax = fig.add_subplot(1, 2, 1)
ax.set_aspect("equal")
ax.set_xlim(-222, 200)
ax.set_ylim(-218, 200)
ax.axis("off")
ax.add_patch(plt.Rectangle((-180, -180), 360, 360, facecolor=C["fill"], edgecolor="none"))
for x0, y0, x1, y1, col, n in ((-180, -180, -180, 180, C["x"], 1), (180, -180, 180, 180, C["x"], 1),
                               (-180, -180, 180, -180, C["z"], 2), (-180, 180, 180, 180, C["z"], 2)):
    ax.plot([x0, x1], [y0, y1], color=col, lw=2)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    for k in range(n):
        off = (k - (n - 1) / 2) * 16
        if x0 == x1:
            ax.annotate("", xy=(mx, my + off + 10), xytext=(mx, my + off - 10), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6))
        else:
            ax.annotate("", xy=(mx + off + 10, my), xytext=(mx + off - 10, my), arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6))
th = np.linspace(-180, 180, 4000)
tm = (12 * (th + 180)) % 360 - 180
br = np.where(np.abs(np.diff(tm)) > 180)[0] + 1
for seg_h, seg_m in zip(np.split(th, br), np.split(tm, br)):
    ax.plot(seg_h, seg_m, color=C["accent"], lw=1.1)
ax.plot([-180, 180], [-180, 180], color=C["muted"], lw=0.9, ls="--")
ax.text(0, -210, T("时针角 θh / (°)", "hour hand θh / (°)"), ha="center", fontsize=9.5)
ax.text(-212, 0, T("分针角 θm / (°)", "minute hand θm / (°)"), ha="center", va="center", rotation=90, fontsize=9.5)
for v in (-180, 180):
    ax.text(v, -188, str(v), ha="center", va="top", fontsize=8, color=C["muted"])
    ax.text(-186, v, str(v), ha="right", va="center", fontsize=8, color=C["muted"])
ax.text(60, 120, T("虚线：两针重合", "dashed: hands overlap"), fontsize=8.5, color=C["muted"],
        bbox=dict(facecolor="white", edgecolor="none", pad=1))
ax.set_title(T("(a) 左右边（红）粘合，上下边（蓝）粘合", "(a) glue left to right (red), top to bottom (blue)"), fontsize=10)

ax = fig.add_subplot(1, 2, 2, projection="3d")
Rr, rr = 1.0, 0.42
u, v = np.meshgrid(np.linspace(0, 2 * math.pi, 60), np.linspace(0, 2 * math.pi, 30))
X = (Rr + rr * np.cos(v)) * np.cos(u)
Y = (Rr + rr * np.cos(v)) * np.sin(u)
Z = rr * np.sin(v)
ax.plot_surface(X, Y, Z, color=C["light"], alpha=0.55, linewidth=0, shade=True)
uu = np.linspace(0, 2 * math.pi, 3000)
vv = 12 * uu
ax.plot((Rr + rr * np.cos(vv)) * np.cos(uu), (Rr + rr * np.cos(vv)) * np.sin(uu), rr * np.sin(vv), color=C["accent"], lw=1.0)
ax.plot((Rr + rr) * np.cos(uu), (Rr + rr) * np.sin(uu), 0 * uu, color=C["x"], lw=1.5)          # 原正方形的左右边（θh = 常数的圈在另一方向）
ax.plot(Rr + rr * np.cos(uu), 0 * uu, rr * np.sin(uu), color=C["z"], lw=1.5)
ax.set_xlim(-1.3, 1.3)
ax.set_ylim(-1.3, 1.3)
ax.set_zlim(-1.3, 1.3)
ax.set_box_aspect((1, 1, 1), zoom=1.45)
ax.view_init(elev=35, azim=-60)
ax.set_axis_off()
ax.set_title(T("(b) 环面 T²：两针联动时只能在橙色曲线上", "(b) Torus T²: geared hands stay on the orange curve"), fontsize=10)
fig.subplots_adjust(wspace=0.02, left=0.02, right=0.98, top=0.92, bottom=0.04)
figure(fig, "fig11_3_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 11.3.2
ta, tb = np.radians([150.0, -60.0]), np.radians([-120.0, 60.0])
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 4.6), gridspec_kw=dict(width_ratios=[1.05, 1]))
plane(a1, (-0.9, 0.9), (-0.75, 0.9))
a1.add_patch(plt.Circle(OBS_C, OBS_R, facecolor=C["steel"], edgecolor=C["dark"], zorder=2))
a1.text(OBS_C[0] + 0.12, OBS_C[1] + 0.06, T("障碍物", "obstacle"), fontsize=9.5, color=C["dark"])
d = wrap(tb - ta)
for s in np.linspace(0.15, 0.85, 5):
    e, w = fk2(*(ta + s * d))
    a1.plot([0, e[0], w[0]], [0, e[1], w[1]], color=C["y"], lw=1.5, alpha=0.35, zorder=1)
for q, col, name in ((ta, C["z"], T("起点 A", "start A")), (tb, C["accent"], T("终点 B", "goal B"))):
    e, w = fk2(*q)
    a1.plot([0, e[0], w[0]], [0, e[1], w[1]], color=col, lw=5, solid_capstyle="round", zorder=3)
    a1.plot([0, e[0]], [0, e[1]], "o", color="white", mec=C["ink"], ms=6, zorder=4)
    a1.text(w[0] + 0.03, w[1] - 0.06, name, fontsize=9.5, color=col)
a1.plot(0, 0, "s", color=C["dark"], ms=8)
a1.text(-0.85, -0.7, T("淡绿：沿环面最短路的中间构型", "faint green: intermediate poses on the shortest path"), fontsize=8.5, color=C["dark"])
a1.set_title(T("(a) 工作空间中的两连杆臂", "(a) The 2R arm in its workspace"), fontsize=10)

g = np.arange(-180, 180, 1.0)
Cm = collide(*np.meshgrid(np.radians(g), np.radians(g), indexing="ij"))
a2.imshow(Cm.T, origin="lower", extent=(-180, 180, -180, 180), cmap="Greys", vmin=0, vmax=1.6, interpolation="nearest")
A, B = np.degrees(ta), np.degrees(tb)
a2.plot([A[0], B[0]], [A[1], B[1]], color=C["x"], lw=1.8, ls="--")
# 跨过 ±180° 的最短路：分成两段画
dd = np.degrees(d)
s_cut = (180 - A[0]) / dd[0]
mid = A + s_cut * dd
a2.plot([A[0], 180], [A[1], mid[1]], color=C["y"], lw=2.2)
a2.plot([-180, B[0]], [mid[1], B[1]], color=C["y"], lw=2.2)
for P, col, name in ((A, C["z"], "A"), (B, C["accent"], "B")):
    a2.plot(*P, "o", color=col, ms=8, zorder=5)
    a2.text(P[0] - 16, P[1] + 8, name, fontsize=11, color=col, weight="bold")
a2.set_xlim(-180, 180)
a2.set_ylim(-180, 180)
a2.set_xticks([-180, -90, 0, 90, 180])
a2.set_yticks([-180, -90, 0, 90, 180])
a2.set_xlabel(T("θ₁ / (°)", "θ₁ / (°)"))
a2.set_ylabel(T("θ₂ / (°)", "θ₂ / (°)"))
a2.text(-20, 150, T("红虚线：当作平面走，穿过障碍物", "red dashed: treated as a plane, hits the obstacle"), fontsize=8.5, color=C["x"],
        bbox=dict(facecolor="white", edgecolor="none", pad=1), ha="center")
a2.text(-20, -165, T("绿线：在环面上走，跨过 ±180°", "green: on the torus, across ±180°"), fontsize=8.5, color=C["y"],
        bbox=dict(facecolor="white", edgecolor="none", pad=1), ha="center")
a2.set_title(T("(b) 构型空间（灰色为障碍物占据的构型）", "(b) C-space (grey: configurations in collision)"), fontsize=10)
fig.subplots_adjust(wspace=0.18, left=0.02, right=0.98, top=0.92, bottom=0.1)
figure(fig, "fig11_3_2")
plt.close(fig)
