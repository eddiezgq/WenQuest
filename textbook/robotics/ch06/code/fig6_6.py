"""6.6 节的示意图。

图 6.6.1：算例 6.6.3（潘索）：两个不共面的力 f₁、f₂ 合成一个力旋量：沿中心轴的合力 f，加上绕中心轴的力偶矩 m；节距 h = m·f/|f|²。
图 6.6.2：算例 6.6.1：UR5e 零位托住 5 kg 负载，侧视（x–z 平面）。关节 2、3、4 的轴垂直于纸面；
          关节 i 需要的力矩 = m𝔤 × 负载质心到该轴的水平距离（带符号）。
"""
import math

import numpy as np

from _screw import AXIS, C, H1, H2, L1, L2, UR_M, axes3d, tight3d
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 6.6.1
P1, f1 = np.array([0.2, 0, 0]), np.array([0, 0, -10.0])
P2, f2 = np.array([0, 0, 0.3]), np.array([0, 10.0, 0])
fR = f1 + f2
mR = np.cross(P1, f1) + np.cross(P2, f2)
h = mR @ fR / (fR @ fR)
q = np.cross(fR, mR) / (fR @ fR)
u = fR / np.linalg.norm(fR)
k = 0.012                                       # 力的箭头：每牛顿 0.012 m

fig, ax = axes3d(plt, size=(6.2, 4.6), elev=20, azim=-50)
for i in range(3):
    e = np.zeros(3)
    e[i] = 0.12
    ax.quiver(0, 0, 0, *e, color=AXIS[i], lw=1.4, arrow_length_ratio=0.3)
ax.text(-0.03, -0.03, -0.04, "O", fontsize=11)
for P, f, name in ((P1, f1, "1"), (P2, f2, "2")):
    ax.scatter(*P, color=C["ink"], s=12, depthshade=False)
    ax.quiver(*P, *(f * k), color=C["muted"], lw=1.8, arrow_length_ratio=0.15)
    ax.text(*(P + f * k * 1.1 + np.array([0.01, 0, 0])), rf"$f_{name}$", fontsize=12, color=C["muted"])
L = np.array([q - 0.25 * u, q + 0.3 * u])
ax.plot(*L.T, color=C["accent"], lw=1.4, ls="-.")
ax.quiver(*q, *(fR * k), color=C["accent"], lw=2.6, arrow_length_ratio=0.15)
ax.text(*(q + fR * k + np.array([0.0, 0.0, 0.03])), r"$f$", fontsize=13, color=C["accent"])
# 力偶矩：绕中心轴的圆弧箭头
e1 = np.cross(u, [1.0, 0, 0])
e1 /= np.linalg.norm(e1)
e2 = np.cross(u, e1)
cc = q + 0.06 * u
t = np.linspace(0.2, 1.75 * math.pi, 60)
arc = cc + 0.045 * (np.outer(np.cos(t), e1) + np.outer(np.sin(t), e2))
ax.plot(*arc.T, color=C["z"], lw=1.8)
ax.quiver(*arc[-2], *(arc[-1] - arc[-2]) * 2.5, color=C["z"], lw=1.8, arrow_length_ratio=1.0)
ax.text(*(cc - 0.09 * e1 + np.array([0, 0, 0.05])), r"$m = h f$", fontsize=12, color=C["z"], ha="right")
ax.scatter(*q, color=C["accent"], s=16, depthshade=False)
ax.text(*(q + np.array([0.02, 0.0, -0.04])), "$q$", fontsize=12, color=C["accent"])
ax.text2D(0.02, 0.96, T("灰：原来的两个力；金：中心轴上的合力；蓝：绕中心轴的力偶矩", "grey: the two forces; gold: resultant on the central axis; blue: couple about it"),
          transform=ax.transAxes, fontsize=9.5)
tight3d(ax, np.vstack([L, [P1, P2, P1 + f1 * k, P2 + f2 * k, [0, 0, 0], q + fR * k]]), pad=0.04, zoom=1.15)
figure(fig, "fig6_6_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 6.6.2
g, m = 9.81, 5.0
j2, j3, j4 = np.array([0, H1]), np.array([-L1, H1]), np.array([-L1 - L2, H1])
fl = UR_M[[0, 2], 3]
cxz = fl                                         # 质心的 x、z 与法兰盘中心相同（沿 y 偏出纸面）
fig, ax = plt.subplots(figsize=(6.6, 3.6))
ax.set_aspect("equal")
ax.axis("off")
ax.fill([-0.06, 0.06, 0.04, -0.04], [0, 0, H1 - 0.03, H1 - 0.03], color="#d5dbe0")
ax.plot([0.1, -1.0], [0, 0], color=C["muted"], lw=1)
pts = np.array([j2, j3, j4, j4 + np.array([0, -H2])])
ax.plot(*pts.T, color="#9aa5ad", lw=7, solid_capstyle="round")
for p, name, tau in ((j2, "2", m * g * (cxz[0] - j2[0])), (j3, "3", m * g * (cxz[0] - j3[0])), (j4, "4", m * g * (cxz[0] - j4[0]))):
    ax.add_patch(plt.Circle(p, 0.022, facecolor="white", edgecolor=C["ink"], lw=1.4, zorder=5))
    ax.plot(*p, marker="o", color=C["ink"], ms=3, zorder=6)          # ⊙：轴垂直于纸面、指向读者
    lab = T(f"关节 {name}", f"joint {name}") + "\n" + rf"$\tau_{name} = {tau:.1f}$ N·m"
    ax.text(p[0] + 0.01, p[1] + 0.05, lab, fontsize=9.5, ha="center")
ax.add_patch(plt.Rectangle((cxz[0] - 0.04, cxz[1] - 0.09), 0.08, 0.07, facecolor="#f3e2b3", edgecolor=C["accent"], zorder=4))
ax.plot(*cxz, "o", color=C["accent"], ms=4, zorder=6)
ax.annotate("", xy=(cxz[0], cxz[1] - 0.30), xytext=(cxz[0], cxz[1] - 0.06), arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=1.6))
ax.text(cxz[0] + 0.02, cxz[1] - 0.26, r"$m\mathfrak{g}$ = 49.05 N", fontsize=10, color=C["x"])
for p, yy in ((j2, -0.32), (j3, -0.4)):
    ax.annotate("", xy=(cxz[0], yy), xytext=(p[0], yy), arrowprops=dict(arrowstyle="<->", color=C["z"], lw=1.0))
    ax.plot([p[0], p[0]], [p[1] - 0.03, yy - 0.02], color=C["z"], lw=0.6, ls=":")
    ax.text((p[0] + cxz[0]) / 2, yy + 0.015, f"{abs(cxz[0] - p[0]):.3f} m", fontsize=9, color=C["z"], ha="center")
ax.plot([cxz[0], cxz[0]], [cxz[1] - 0.3, -0.42], color=C["z"], lw=0.6, ls=":")
ax.annotate("", xy=(-0.75, 0.42), xytext=(-0.95, 0.42), arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=1.2))
ax.annotate("", xy=(-0.95, 0.62), xytext=(-0.95, 0.42), arrowprops=dict(arrowstyle="-|>", color=C["z"], lw=1.2))
ax.text(-0.74, 0.40, "$x$", color=C["x"], fontsize=11)
ax.text(-0.94, 0.62, "$z$", color=C["z"], fontsize=11)
ax.text(-0.70, 0.45, T("从 −y 一侧看；关节轴 −ŷ 指向读者，逆时针为正", "seen from the −y side; joint axes −ŷ point at the reader, anticlockwise positive"), fontsize=8.5, color=C["muted"])
ax.set_xlim(-1.02, 0.12)
ax.set_ylim(-0.47, 0.68)
figure(fig, "fig6_6_2")
plt.close(fig)
