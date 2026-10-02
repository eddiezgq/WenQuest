"""4.3 节的示意图。

图 4.3.1：欧拉定理——转轴不动；与轴垂直的平面内，各点绕轴转过同一角度 θ。
（轴和角取算例 4.3.1 的结果。）
"""
import math

import numpy as np

from _rot import C, axes3d, circle_arc, rot_axis, rot_x, rot_z
from bookout import T, figure, style

plt = style()
d = math.radians
R = rot_z(d(30)) @ rot_x(d(45))
tr = np.trace(R)
theta = math.acos((tr - 1) / 2)
vals, vecs = np.linalg.eig(R)
w = np.real(vecs[:, int(np.argmin(abs(vals - 1)))])
w /= np.linalg.norm(w)
if not np.allclose(rot_axis(w, theta), R):
    w = -w

fig, ax = axes3d(plt, size=(4.6, 3.8), elev=14, azim=-35, lim=0.5, zoom=1.35, center=tuple(0.4 * w))
# 为了看清，把转轴画在图中央：取一个观察角度使轴斜向上
ax.plot(*np.array([-0.15 * w, 1.0 * w]).T, color=C["ink"], lw=1.6)
ax.quiver(*(0.85 * w), *(0.15 * w), color=C["ink"], lw=1.6, arrow_length_ratio=0.6)
ax.text(*(1.04 * w), T(r"转轴 $\hat\omega$", r"axis $\hat\omega$"), fontsize=11, color=C["ink"])
u = np.cross(w, [0, 0, 1.0])
u /= np.linalg.norm(u)
v = np.cross(w, u)
for h, r in ((0.2, 0.42), (0.62, 0.26)):
    c = h * w
    circle_arc(ax, c, u, v, r, 0, 2 * math.pi, C["muted"], 0.7, ":")
    circle_arc(ax, c, u, v, r, 0, theta, C["accent"], 2.2)
    p0 = c + r * u
    p1 = c + r * (math.cos(theta) * u + math.sin(theta) * v)
    ax.plot(*np.array([c, p0]).T, color=C["muted"], lw=0.9)
    ax.plot(*np.array([c, p1]).T, color=C["muted"], lw=0.9)
    ax.scatter(*p0, color=C["ink"], s=16)
    ax.scatter(*p1, color=C["accent"], s=18)
    ax.scatter(*c, color=C["ink"], s=8)
    m = c + 0.55 * r * (math.cos(theta / 2) * u + math.sin(theta / 2) * v)
    ax.text(*m, r"$\theta$", fontsize=12, color=C["accent"])
ax.text2D(0.02, 0.01, T("各点沿垂直于轴的圆周转过同一个角度 θ；轴上的点不动",
                        "Every point turns through the same angle θ on a circle\nperpendicular to the axis; points on the axis stay put"),
          transform=ax.transAxes, fontsize=9.5)
figure(fig, "fig4_3_1")
plt.close(fig)
