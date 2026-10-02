"""13.4 节的示意图。

图 13.4.1：Panda 零位时按 Craig 约定（改进 DH）建立的连杆坐标系 {1}…{7} 与法兰坐标系 {F}；
          点画线是由推论 13.4.1 换算出的七根旋量轴：每根都恰好是对应坐标系的 z 轴所在的直线。
"""
import math

import numpy as np

from _dh import Rz, Tz, fk_mdh, mdh, mdh_to_poe
from _fig13 import C, equal3d, frame3d, line3d
from bookout import T, figure, style

plt = style()
pi = math.pi
franka = [(0, 0, 0.333, 0), (0, -pi / 2, 0, 0), (0, pi / 2, 0.316, 0), (0.0825, pi / 2, 0, 0),
          (-0.0825, -pi / 2, 0.384, 0), (0, pi / 2, 0, 0), (0.088, pi / 2, 0, 0)]
F = fk_mdh(franka, np.zeros(7), frames=True)
Ff = F[-1] @ Tz(0.107)
S, M = mdh_to_poe(franka, T_nb=Tz(0.107))
for i, s in enumerate(S):                     # 旋量轴就在 {i+1} 的 z 轴上
    w, v = s[:3], s[3:]
    assert np.allclose(w, F[i + 1][:3, 2]) and np.allclose(-np.cross(w, F[i + 1][:3, 3]), v)

fig = plt.figure(figsize=(6.6, 6.2))
ax = fig.add_subplot(111, projection="3d")
ax.view_init(elev=12, azim=-58)
ax.set_axis_off()
body = np.array([[0, 0, 0], [0, 0, 0.333], [0, 0, 0.649], [0.0825, 0, 0.649], [0.0825, 0, 0.75], [0, 0, 1.033], [0.088, 0, 1.033], Ff[:3, 3]])
ax.plot(*body.T, color="#c3cbd0", lw=9, solid_capstyle="round", alpha=0.7)
for i, s in enumerate(S):                     # 画在 {i+1} 的原点附近（原点在这根轴上）
    w = s[:3]
    line3d(ax, F[i + 1][:3, 3], w, -0.15, 0.15, C["accent"], lw=1.3, ls="-.")
offs = {1: (0.03, 0.0, -0.06), 2: (-0.13, 0.0, 0.0), 3: (-0.12, 0.0, 0.02), 4: (0.06, 0.0, -0.07), 5: (-0.13, 0.0, 0.03),
        6: (-0.12, 0.0, -0.07), 7: (0.05, 0.0, 0.03)}
frame3d(ax, F[0], 0.09, "{0}", off=(0.03, 0.0, -0.06))
for i in range(1, 8):
    frame3d(ax, F[i], 0.09, "{%d}" % i, off=offs[i], lw=1.4)
frame3d(ax, Ff, 0.09, "{F}", off=(0.05, 0.0, -0.06), lw=1.4)
ax.text2D(0.02, 0.02, T("点画线：由 Craig 表换算出的旋量轴，各在 $z_i$ 上；{1}、{2} 和 {5}、{6} 原点重合",
                        "dash-dot: screw axes converted from the Craig table, each on $z_i$; {1}, {2} and {5}, {6} share origins"),
          transform=ax.transAxes, fontsize=9)
equal3d(ax, np.r_[body, [[0.25, 0.1, 0.0], [-0.2, -0.1, 1.1]]], pad=0.0, zoom=1.35)
figure(fig, "fig13_4_1")
plt.close(fig)
