"""3.6 节的示意图。

图 3.6.1：刚体绕定轴转动：角速度矢量 ω 沿转轴（右手定则），点 P 在半径为 ρ 的圆上运动，速度 v = ω × r 沿圆的切线；
          参考点 O 换成轴上另一点 O′，r′ 不同而 ω × r′ 相同。
图 3.6.2：算例 3.6.1、3.6.2：UR5e 零位。(a) 俯视，关节 1 转动时法兰盘中心的速度；(b) 侧视，关节 2 转动时的速度。
"""
import math

import numpy as np

from _vec import C, arc2, arrow2, arrow3, circle3, sub3d
from bookout import T, figure, style

plt = style()
from mpl_toolkits.mplot3d.art3d import Poly3DCollection  # noqa: E402

# ---------------------------------------------------------------- 图 3.6.1
fig = plt.figure(figsize=(7.2, 5.6))
ax = sub3d(fig, 111, elev=16, azim=-55, lim=1.0, zoom=1.2, center=(0.1, 0.0, 0.45))
# 一个绕 z 轴转动的圆盘形刚体
t = np.linspace(0, 2 * math.pi, 80)
Rd, hz = 0.85, 0.35
top = np.column_stack([Rd * np.cos(t), Rd * np.sin(t), np.full_like(t, hz)])
ax.add_collection3d(Poly3DCollection([top], facecolor="#f3e2b3", edgecolor=C["accent"], alpha=0.35, lw=0.8))
ax.plot([0, 0], [0, 0], [-0.15, 1.25], color=C["muted"], lw=1, ls="--")
w = np.array([0, 0, 1.0])
arrow3(ax, np.array([0, 0, 0.95]), w * 0.32, C["ink"], 2.6, ratio=0.3)
ax.text(0.06, 0.0, 1.27, r"$\boldsymbol{\omega}=\dot\theta\,\hat{\boldsymbol{\omega}}$", fontsize=13)
circle3(ax, np.array([0, 0, 1.05]), np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), 0.14, 0.3, 5.6, C["ink"], 1.0)
P = np.array([0.6, 0.0, hz])
O = np.array([0, 0, 0.0])
O2 = np.array([0, 0, 0.8])
ax.plot(*P, "o", color=C["x"], ms=6)
ax.text(*(P + [0.05, -0.08, 0.02]), "P", fontsize=13)
for o, lab, col in ((O, r"$O$", C["z"]), (O2, r"$O'$", C["y"])):
    ax.plot(*o, "o", color=col, ms=5)
    ax.text(*(o + [-0.12, 0, 0]), lab, fontsize=12, color=col)
    arrow3(ax, o, P - o, col, 1.6, ratio=0.06)
ax.text(*(0.5 * (O + P) + [0.0, 0.05, -0.1]), r"$\boldsymbol{r}$", fontsize=13, color=C["z"])
ax.text(*(0.5 * (O2 + P) + [0.0, 0.05, 0.05]), r"$\boldsymbol{r}'$", fontsize=13, color=C["y"])
ax.plot([0, P[0]], [0, 0], [hz, hz], color=C["accent"], lw=2)
ax.text(0.3, 0.0, hz + 0.04, r"$\rho$", fontsize=13, color=C["accent"])
circle3(ax, np.array([0, 0, hz]), np.array([1.0, 0, 0]), np.array([0, 1.0, 0]), 0.6, 0, 2 * math.pi, C["x"], 0.9, ":")
v = np.cross(w, P - O) * 0.9
arrow3(ax, P, v, C["x"], 2.6, ratio=0.15)
ax.text(*(P + v + [-0.35, 0.0, 0.16]), r"$\boldsymbol{v}=\boldsymbol{\omega}\times\boldsymbol{r}=\boldsymbol{\omega}\times\boldsymbol{r}'$",
        fontsize=12, color=C["x"])
ax.text(0.9, -0.6, -0.1, r"$|\boldsymbol{v}|=\rho\,\dot\theta$" + T("，方向沿圆的切线", ", along the tangent of the circle"), fontsize=10, color=C["muted"])
figure(fig, "fig3_6_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 3.6.2
H1, W1, L1, W2, L2, W3, H2, W4 = 0.163, 0.138, 0.425, 0.131, 0.392, 0.127, 0.1, 0.1
p = np.array([-L1 - L2, -W1 + W2 - W3 - W4, H1 - H2])
w1 = math.radians(60)
v1 = np.cross([0, 0, w1], p)
fig, (axa, axb) = plt.subplots(1, 2, figsize=(10.4, 4.4))
for a_ in (axa, axb):
    a_.set_aspect("equal")
    a_.axis("off")
# (a) 俯视：x 向右、y 向上
arrow2(axa, (0, 0), (0.25, 0), C["x"], 1.2)
arrow2(axa, (0, 0), (0, 0.25), C["y"], 1.2)
axa.text(0.26, -0.02, "$x$", color=C["x"], fontsize=12)
axa.text(0.01, 0.26, "$y$", color=C["y"], fontsize=12)
axa.add_patch(plt.Circle((0, 0), 0.075, fc="#d9dee2", ec=C["muted"]))
axa.annotate(T("关节 1 轴（垂直纸面向外）", "joint 1 axis (out of the page)"), xy=(-0.06, 0.04), xytext=(-0.76, 0.05),
             fontsize=9.5, color=C["muted"], va="bottom", arrowprops=dict(arrowstyle="-", color=C["muted"], lw=0.8))
pts = [(0, 0), (0, -0.138), (-0.425, -0.138), (-0.425, -0.007), (-0.817, -0.007), (-0.817, -0.134), (-0.817, -0.234)]
axa.plot(*zip(*pts), color="#5b7c99", lw=6, alpha=0.5, solid_capstyle="round")
axa.plot(p[0], p[1], "o", color=C["x"], ms=6)
axa.text(p[0] - 0.2, p[1] - 0.08, T("法兰盘中心", "flange centre"), fontsize=10, ha="center")
axa.plot([0, p[0]], [0, p[1]], color=C["accent"], lw=1.4, ls="--")
axa.text(p[0] / 2 - 0.05, p[1] / 2 - 0.1, rf"$\rho={math.hypot(p[0], p[1]):.3f}$ m", fontsize=11, color=C["accent"])
s = 0.35
arrow2(axa, p[:2], p[:2] + s * v1[:2], C["x"], 2.4)
axa.text(*(p[:2] + s * v1[:2] + [0.02, -0.02]), r"$\boldsymbol{v}$", fontsize=14, color=C["x"])
arc2(axa, (0, 0), math.hypot(p[0], p[1]), math.atan2(p[1], p[0]) + 0.15, math.atan2(p[1], p[0]) + 0.45, C["muted"], 1.0, ":")
arc2(axa, (0, 0), 0.12, -0.6, 3.6, C["ink"], 1.0)
axa.text(0.1, 0.1, r"$\dot\theta_1$", fontsize=12)
axa.text(-1.0, 0.33, T("(a) 俯视：关节 1 以 60°/s 转动", "(a) Top view: joint 1 turning at 60°/s"), fontsize=10)
axa.set_xlim(-1.02, 0.4)
axa.set_ylim(-0.6, 0.38)
# (b) 侧视：x 向右、z 向上；关节 2 轴沿 −y（垂直纸面）
w2 = math.radians(30)
q2 = np.array([0, -W1, H1])
v2 = np.cross([0, -w2, 0], p - q2)
arrow2(axb, (0.1, 0), (0.35, 0), C["x"], 1.2)
arrow2(axb, (0.1, 0), (0.1, 0.25), C["z"], 1.2)
axb.text(0.36, -0.02, "$x$", color=C["x"], fontsize=12)
axb.text(0.11, 0.26, "$z$", color=C["z"], fontsize=12)
axb.plot([-0.9, 0.3], [0, 0], color=C["muted"], lw=1)
axb.plot([0, 0, -0.425, -0.817, -0.817], [0, 0.163, 0.163, 0.163, 0.063], color="#5b7c99", lw=6, alpha=0.5, solid_capstyle="round")
axb.add_patch(plt.Circle((0, 0.163), 0.04, fc="white", ec=C["ink"], lw=1.2, zorder=4))
axb.plot(0, 0.163, "o", color=C["ink"], ms=3, zorder=5)
axb.text(-0.95, 0.33, T("关节 2 轴（沿 −y，垂直纸面向外，⊙）", "joint 2 axis (along −y, out of the page, ⊙)"), fontsize=9.5, color=C["muted"])
arc2(axb, (0, 0.163), 0.08, 0.3, 3.0, C["ink"], 1.0)
axb.plot(p[0], p[2], "o", color=C["x"], ms=6)
axb.plot([0, p[0]], [0.163, p[2]], color=C["accent"], lw=1.4, ls="--")
axb.text(-0.45, 0.06, r"$\boldsymbol{r}$", fontsize=13, color=C["accent"])
s2 = 0.45
arrow2(axb, (p[0], p[2]), (p[0] + s2 * v2[0], p[2] + s2 * v2[2]), C["x"], 2.4)
axb.text(p[0] + 0.04, p[2] + s2 * v2[2] - 0.02, r"$\boldsymbol{v}$", fontsize=14, color=C["x"])
axb.text(-0.95, 0.4, T("(b) 侧视：关节 2 以 30°/s 转动", "(b) Side view: joint 2 turning at 30°/s"), fontsize=10)
axb.set_xlim(-1.0, 0.45)
axb.set_ylim(-0.3, 0.45)
fig.subplots_adjust(wspace=0.08)
figure(fig, "fig3_6_2")
plt.close(fig)
