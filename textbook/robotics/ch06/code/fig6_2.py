"""6.2 节的示意图。

图 6.2.1：李群与李代数的直观图景：SO(3) 画成一张弯曲的曲面，单位矩阵 I 处的切平面就是 so(3)；
          切平面中的矢量 [ω] 经指数映射沿曲面走到 e^{[ω]t}。（示意图：真实的 SO(3) 是三维的，无法画出。）
图 6.2.2：算例 6.2.1，t = 1 s 时的角速度矢量 ω：同一支箭头，在 {s} 中读出 ω_s，在 {b} 中读出 ω_b。
"""
import math

import numpy as np

from _screw import AXIS, C, UR_AXES, UR_M, axes3d, exp3, frame3d, tight3d
from bookout import T, figure, style

plt = style()
d = math.radians

# ---------------------------------------------------------------- 图 6.2.1
fig, ax = axes3d(plt, size=(5.8, 4.2), elev=24, azim=-70)
Rr = 1.6
u = np.linspace(-0.75, 0.75, 40)
v = np.linspace(-0.6, 0.6, 30)
U, V = np.meshgrid(u, v)
X = Rr * np.sin(U) * np.cos(V)
Y = Rr * np.sin(V)
Z = Rr * np.cos(U) * np.cos(V) - Rr
ax.plot_surface(X, Y, Z, color="#cfd8de", alpha=0.55, lw=0, rstride=1, cstride=1, shade=False)
ax.plot_wireframe(X, Y, Z, color="#a9b4bb", lw=0.3, rstride=5, cstride=5)
# 切平面
P = np.array([[-0.75, -0.55], [0.75, -0.55], [0.75, 0.55], [-0.75, 0.55], [-0.75, -0.55]])
ax.plot(P[:, 0], P[:, 1], 0 * P[:, 0] + 0.02, color=C["z"], lw=1.2)
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
ax.add_collection3d(Poly3DCollection([np.c_[P[:4], np.full(4, 0.02)]], facecolor="#bcd6ee", alpha=0.35, edgecolor="none"))
ax.scatter([0], [0], [0], color=C["ink"], s=18, depthshade=False)
ax.text(-0.08, -0.05, 0.06, "$I$", fontsize=13)
# 切矢量与曲面上的曲线
a = 0.62
ax.quiver(0, 0, 0, a, 0.25, 0, color=C["accent"], lw=2.0, arrow_length_ratio=0.15)
ax.text(a + 0.03, 0.28, 0.03, r"$[\omega]$", color=C["accent"], fontsize=13)
s = np.linspace(0, 1.0, 50)
cu, cv = s * a / Rr * 1.15, s * 0.25 / Rr * 1.15
ax.plot(Rr * np.sin(cu) * np.cos(cv), Rr * np.sin(cv), Rr * np.cos(cu) * np.cos(cv) - Rr, color=C["x"], lw=2.0)
e = (Rr * math.sin(cu[-1]) * math.cos(cv[-1]), Rr * math.sin(cv[-1]), Rr * math.cos(cu[-1]) * math.cos(cv[-1]) - Rr)
ax.scatter(*e, color=C["x"], s=16, depthshade=False)
ax.text(e[0] + 0.02, e[1] - 0.02, e[2] - 0.12, r"$e^{[\omega]t}$", color=C["x"], fontsize=13)
ax.text(-0.72, 0.5, 0.03, T("切空间 so(3)", "tangent space so(3)"), color=C["z"], fontsize=10)
ax.text(-0.5, -0.55, -0.42, T("李群 SO(3)（示意）", "Lie group SO(3) (sketch)"), color=C["muted"], fontsize=10)
tight3d(ax, np.array([[-0.8, -0.6, -0.45], [0.8, 0.6, 0.1]]), pad=0.05, zoom=0.95)
figure(fig, "fig6_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 6.2.2
w1, w6 = UR_AXES[0][0], UR_AXES[5][0]
r1, r6 = d(30), d(90)
Rt = exp3(w1 * r1) @ exp3(w6 * r6) @ UR_M[:3, :3]
ws = r1 * w1 + r6 * exp3(w1 * r1) @ w6
wb = Rt.T @ ws
fig, ax = axes3d(plt, size=(6.0, 4.6), elev=16, azim=25)
Ts = np.eye(4)
Tb = np.eye(4)
Tb[:3, :3] = Rt
Tb[:3, 3] = [0.0, 1.5, 1.3]
frame3d(ax, Ts, 0.8, "", fs=12, sub="s")
frame3d(ax, Tb, 0.8, "", fs=12, sub="b")
ax.text(0.0, 0.25, -0.22, "{s}", fontsize=12)
ax.text(0.0, 1.75, 1.05, "{b}", fontsize=12)
k = 0.55
for Tm in (Ts, Tb):
    o = Tm[:3, 3]
    ax.quiver(*o, *(ws * k), color=C["accent"], lw=2.6, arrow_length_ratio=0.12)
    ax.text(*(o + ws * k * 1.12), r"$\boldsymbol{\omega}$", color=C["accent"], fontsize=14)
ax.text2D(0.02, 0.06, T("在 {s} 中读出：", "read in {s}: ") + r"$\omega_s = (0.79,\ -1.36,\ 0.52)$ rad/s", transform=ax.transAxes, fontsize=10)
ax.text2D(0.02, 0.0, T("在 {b} 中读出：", "read in {b}: ") + r"$\omega_b = (0.52,\ 1.57,\ 0)$ rad/s", transform=ax.transAxes, fontsize=10)
tight3d(ax, np.array([[-0.5, -0.9, -0.3], [0.9, 2.4, 2.2]]), pad=0.0, zoom=1.15)
assert np.allclose(np.round(ws, 2), [0.79, -1.36, 0.52]) and np.allclose(np.round(wb, 2), [0.52, 1.57, 0])
figure(fig, "fig6_2_2")
plt.close(fig)
