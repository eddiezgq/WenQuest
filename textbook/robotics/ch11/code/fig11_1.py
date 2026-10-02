"""11.1 节的示意图。

图 11.1.1：七种常用关节（R、P、H、C、U、S、E）：两个构件、允许的相对运动（箭头）、自由度 f 与约束数 c。
图 11.1.2：螺旋副与滚珠丝杠花键轴：花键螺母带轴转 θ、丝杠螺母不动时，轴沿轴线移动 hθ；轴上一点走螺旋线。
"""
import math

import numpy as np

from _fig11 import C, arc3, arrow3, axline, box, clean3d, cylinder, sphere
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 11.1.1
fig = plt.figure(figsize=(9.6, 5.4))
z = np.array([0, 0, 1.0])
names = [("R", T("转动关节", "Revolute"), 1), ("P", T("移动关节", "Prismatic"), 1), ("H", T("螺旋副", "Helical"), 1),
         ("C", T("圆柱副", "Cylindrical"), 2), ("U", T("万向节", "Universal"), 2), ("S", T("球关节", "Spherical"), 3),
         ("E", T("平面副", "Planar"), 3)]
A, B = C["steel"], C["z"]          # 构件 A（灰）、构件 B（蓝）
for k, (sym, name, f) in enumerate(names):
    ax = fig.add_subplot(2, 4, k + 1, projection="3d")
    clean3d(ax, 1.0, elev=22, azim=-58, zoom=1.45)
    if sym == "R":
        cylinder(ax, (0, 0, -0.9), (0, 0, -0.1), 0.32, A)
        cylinder(ax, (0, 0, -0.1), (0, 0, 0.75), 0.18, B)
        box(ax, (0.35, 0, 0.55), (0.7, 0.14, 0.14), B)
        axline(ax, (0, 0, 0), z, 1.0)
        arc3(ax, (0, 0, 0.2), z, 0.42, 0.3, 2.4, C["x"])
    elif sym == "P":
        box(ax, (0, 0, -0.35), (0.5, 0.5, 0.9), A, alpha=0.55)
        box(ax, (0, 0, 0.15), (0.24, 0.24, 1.5), B)
        arrow3(ax, (0.42, 0, -0.2), (0, 0, 0.7), C["x"])
        arrow3(ax, (0.42, 0, 0.5), (0, 0, -0.7), C["x"])
    elif sym == "H":
        cylinder(ax, (0, 0, -0.25), (0, 0, 0.15), 0.34, A, alpha=0.45)
        cylinder(ax, (0, 0, -0.95), (0, 0, 0.95), 0.12, B)
        t = np.linspace(-0.9, 0.9, 600)
        ax.plot(0.125 * np.cos(t * 2 * math.pi / 0.22), 0.125 * np.sin(t * 2 * math.pi / 0.22), t, color="white", lw=0.9)
        tt = np.linspace(0, 1.6 * math.pi, 60)
        ax.plot(0.55 * np.cos(tt), 0.55 * np.sin(tt), 0.3 + 0.08 * tt, color=C["x"], lw=1.8)
        ax.quiver(0.55 * math.cos(tt[-1]), 0.55 * math.sin(tt[-1]), 0.3 + 0.08 * tt[-1], -0.2 * math.sin(tt[-1]), 0.2 * math.cos(tt[-1]), 0.03,
                  color=C["x"], lw=1.8, arrow_length_ratio=0.9)
    elif sym == "C":
        cylinder(ax, (0, 0, -0.6), (0, 0, 0.0), 0.3, A, alpha=0.6)
        cylinder(ax, (0, 0, -0.95), (0, 0, 0.9), 0.14, B)
        arc3(ax, (0, 0, 0.45), z, 0.4, 0.3, 2.4, C["x"])
        arrow3(ax, (0.5, 0, -0.5), (0, 0, 0.6), C["x"])
    elif sym == "U":
        cylinder(ax, (0, 0, -0.95), (0, 0, -0.35), 0.13, A)
        cylinder(ax, (-0.32, 0, -0.35), (0.32, 0, -0.35), 0.06, A)
        cylinder(ax, (0, 0, 0.35), (0, 0, 0.95), 0.13, B)
        cylinder(ax, (0, -0.32, 0.0), (0, 0.32, 0.0), 0.07, C["accent"])
        cylinder(ax, (-0.32, 0, 0.0), (0.32, 0, 0.0), 0.07, C["accent"])
        for s in (-1, 1):
            cylinder(ax, (0.32 * s, 0, -0.35), (0.32 * s, 0, 0.0), 0.05, A)
            cylinder(ax, (0, 0.32 * s, 0.35), (0, 0.32 * s, 0.0), 0.05, B)
        arc3(ax, (0.55, 0, 0), (1, 0, 0), 0.3, 0.5, 2.6, C["x"])
        arc3(ax, (0, 0.55, 0), (0, 1, 0), 0.3, 0.5, 2.6, C["y"])
    elif sym == "S":
        cylinder(ax, (0, 0, -0.95), (0, 0, -0.4), 0.14, A)
        sphere(ax, (0, 0, -0.05), 0.42, A, alpha=0.35)
        sphere(ax, (0, 0, -0.05), 0.3, B)
        cylinder(ax, (0, 0, 0.2), (0.35, 0, 0.9), 0.1, B)
        arc3(ax, (0, 0, 0.45), z, 0.35, 0.3, 2.4, C["z"])
        arc3(ax, (0.6, 0, 0), (1, 0, 0), 0.3, 0.5, 2.6, C["x"])
        arc3(ax, (0, 0.6, 0), (0, 1, 0), 0.3, 0.5, 2.6, C["y"])
    elif sym == "E":
        box(ax, (0, 0, -0.45), (1.8, 1.8, 0.1), A, alpha=0.35)
        box(ax, (0, 0, -0.25), (0.8, 0.6, 0.3), B, alpha=1.0)
        arrow3(ax, (0.45, 0.0, -0.05), (0.5, 0, 0), C["x"])
        arrow3(ax, (0.0, 0.35, -0.05), (0, 0.5, 0), C["y"])
        arc3(ax, (0, 0, 0.1), z, 0.4, 0.3, 2.4, C["z"])
    ax.set_title(f"{name}  {sym}\n$f = {f}$,  $c = {6 - f}$", fontsize=10.5, color=C["ink"], pad=-4)

ax = fig.add_subplot(2, 4, 8)
ax.axis("off")
ax.text(0.02, 0.78, T("灰色：构件 A（不动）", "Grey: body A (held fixed)"), fontsize=9.5, color=C["dark"])
ax.text(0.02, 0.64, T("蓝色：构件 B", "Blue: body B"), fontsize=9.5, color=C["z"])
ax.text(0.02, 0.50, T("箭头：B 相对 A 允许的运动", "Arrows: motions of B allowed relative to A"), fontsize=9.5, color=C["x"])
ax.text(0.02, 0.32, T("$f$：关节自由度", "$f$: degrees of freedom of the joint"), fontsize=9.5, color=C["ink"])
ax.text(0.02, 0.18, T("$c = 6 - f$：约束数（空间）", "$c = 6 - f$: constraints (in space)"), fontsize=9.5, color=C["ink"])
fig.subplots_adjust(wspace=0.02, hspace=0.12, left=0.0, right=1.0, top=0.95, bottom=0.02)
figure(fig, "fig11_1_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 11.1.2
lead, th = 0.020, math.radians(90)
h = lead / (2 * math.pi)
fig = plt.figure(figsize=(8.4, 4.6))
ax = fig.add_subplot(1, 2, 1, projection="3d")
clean3d(ax, 1.0, elev=14, azim=-62, zoom=1.25)
# 示意尺寸：轴长 2，半径 0.13；导程放大画
L = 1.7
cylinder(ax, (0, 0, -0.95), (0, 0, 0.95), 0.12, C["light"], alpha=0.9)
t = np.linspace(-0.92, 0.92, 500)
ax.plot(0.125 * np.cos(t * 2 * math.pi / 0.25), 0.125 * np.sin(t * 2 * math.pi / 0.25), t, color=C["dark"], lw=0.7)
cylinder(ax, (0, 0, 0.35), (0, 0, 0.6), 0.3, C["accent"], alpha=0.85)        # 丝杠螺母（不动）
cylinder(ax, (0, 0, -0.55), (0, 0, -0.3), 0.3, C["z"], alpha=0.85)          # 花键螺母（转动）
axline(ax, (0, 0, 0), (0, 0, 1), 1.05)
arc3(ax, (0, 0, -0.75), (0, 0, 1), 0.42, 0.2, 1.9, C["x"])
ax.text(0.45, -0.1, 0.62, T("丝杠螺母\n（不动）", "screw nut\n(held)"), fontsize=9, color=C["accent"])
ax.text(0.45, -0.1, -0.45, T("花键螺母\n（带轴转 θ）", "spline nut\n(turns shaft by θ)"), fontsize=9, color=C["z"])
ax.text(0.05, 0.05, 1.05, T("轴线", "axis"), fontsize=9, color=C["muted"])
ax.set_title(T("(a) 滚珠丝杠花键轴", "(a) Ball-screw spline shaft"), fontsize=10.5, pad=-2)

ax = fig.add_subplot(1, 2, 2, projection="3d")
clean3d(ax, 1.0, elev=24, azim=-55, zoom=1.25)
axline(ax, (0, 0, 0), (0, 0, 1), 1.05)
# 节距画大一些以便看清：转一圈下降 0.75
hd = 0.6 / (2 * math.pi)
tt = np.linspace(0, 4.2 * math.pi, 500)
r, z0 = 0.5, 0.8
ax.plot(r * np.cos(tt), r * np.sin(tt), z0 - hd * tt, color=C["x"], lw=1.8)
ax.scatter([r], [0], [z0], color=C["ink"], s=14)
ax.scatter([r * math.cos(th)], [r * math.sin(th)], [z0 - hd * th], color=C["x"], s=16)
ax.plot([0, r], [0, 0], [z0, z0], color=C["muted"], lw=0.8)
ax.plot([r, r], [0, 0], [z0, z0 - hd * 2 * math.pi], color=C["accent"], lw=1.4)
ax.text(r + 0.08, 0, z0 - hd * math.pi, T("导程 $2\\pi h$", "lead $2\\pi h$"), fontsize=9.5, color=C["accent"])
ax.text(r * math.cos(th) - 0.1, r * math.sin(th), z0 - hd * th + 0.14, T("转 θ、移 hθ", "turn θ, advance hθ"), fontsize=9.5, color=C["x"])
ax.quiver(0, 0, 1.0, 0, 0, -0.35, color=C["ink"], lw=1.6, arrow_length_ratio=0.25)
ax.text(0.07, 0.0, 0.95, r"$\hat\omega$", fontsize=11)
ax.text2D(0.02, 0.06, r"$\mathcal{S} = (\hat\omega,\ -\hat\omega\times q + h\hat\omega)$", transform=ax.transAxes, fontsize=10.5)
ax.set_title(T("(b) 轴上一点的螺旋线（节距放大画）", "(b) Helix of a point on the shaft (pitch exaggerated)"), fontsize=10.5, pad=-2)
fig.subplots_adjust(wspace=0.0, left=0.0, right=1.0, top=0.95, bottom=0.0)
figure(fig, "fig11_1_2")
plt.close(fig)
