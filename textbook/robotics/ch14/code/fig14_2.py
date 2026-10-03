"""14.2 节的示意图。

图 14.2.1：2R 臂逆解的几何法：基座 O、肘点 E、目标 P 构成三角形；β 是 OP 的方向角，ψ 是大臂与 OP 的夹角，
           θ2 是小臂相对大臂延长线转过的角。虚线是关于 OP 对称的另一组解。
图 14.2.2：(a) 平面 3R 臂到达 (0.6, 0.05) m、工具朝下的两组解，先由工具朝向求腕点 W；
           (b) 只给末端位置 (0.75, 0.10) m 时的一族解：腕点在以 P 为圆心、半径 L3 的圆上，只有落在 2R 外圆以内的那一段可用。
图 14.2.3：|dθ2/dr| 随 θ2 的变化（式 (14.2.7)）：手臂接近伸直或折回时，θ2 对目标位置极其敏感。
"""
import math

import numpy as np

from _fig14 import BLUE2, C, PALE, arc, arm_pts, base_mark, draw_arm, plane
from _ik import ik2r, ik3r, wrap
from bookout import T, figure, style

plt = style()
l1, l2, l3 = 0.425, 0.392, 0.1

# ---------------------------------------------------------------- 图 14.2.1
fig, ax = plt.subplots(figsize=(6.4, 4.6))
plane(ax, (-0.16, 0.78), (-0.12, 0.62))
P = (0.45, 0.35)
s_dn, s_up = ik2r(*P, l1, l2)
pd = arm_pts(s_dn, (l1, l2))
pu = arm_pts(s_up, (l1, l2))
draw_arm(ax, pu, C["muted"], lw=3, alpha=0.6, ls="--")
draw_arm(ax, pd, C["accent"], lw=5)
base_mark(ax)
ax.plot([0, P[0]], [0, P[1]], color=C["ink"], lw=1.0, ls=":")
ax.plot([0, 0.7], [0, 0], color=C["muted"], lw=0.8)
ax.text(0.71, -0.012, "x", fontsize=11, color=C["muted"])
beta = math.atan2(P[1], P[0])
arc(ax, (0, 0), 0.20, 0, beta, C["z"], arrow=True)
ax.text(0.205, 0.05, r"$\beta$", fontsize=12, color=C["z"])
arc(ax, (0, 0), 0.13, s_dn[0], beta, C["x"], arrow=True)
ax.text(0.135, 0.035, r"$\psi$", fontsize=12, color=C["x"])
E = pd[1]
ext = E + 0.16 * (E - pd[0]) / l1
ax.plot([E[0], ext[0]], [E[1], ext[1]], color=C["accent"], lw=0.9, ls="--")
a_link1 = s_dn[0]
arc(ax, E, 0.09, a_link1, a_link1 + s_dn[1], C["accent"], arrow=True)
ax.text(E[0] + 0.085, E[1] + 0.05, r"$\theta_2$", fontsize=12, color=C["accent"])
ax.text(-0.06, -0.06, "O", fontsize=12)
ax.text(E[0] + 0.015, E[1] - 0.045, "E", fontsize=12)
ax.text(P[0] + 0.015, P[1] + 0.01, "P", fontsize=12)
ax.text(E[0] / 2 + 0.01, E[1] / 2 - 0.05, r"$l_1$", fontsize=12)
ax.text((E[0] + P[0]) / 2 + 0.015, (E[1] + P[1]) / 2 - 0.02, r"$l_2$", fontsize=12)
ax.text(0.27 * P[0] - 0.06, 0.27 * P[1] + 0.035, r"$r$", fontsize=12)
ax.text(pu[1][0] - 0.12, pu[1][1] + 0.03, "E′", fontsize=12, color=C["muted"])
ax.text(-0.15, 0.58, T("实线：肘下（θ₂ > 0）；虚线：肘上（θ₂ < 0），两者关于 OP 对称",
                        "solid: elbow down (θ₂ > 0); dashed: elbow up (θ₂ < 0), mirror images about OP"), fontsize=9, color=C["ink"])
figure(fig, "fig14_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 14.2.2
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.6, 4.4))
L = (l1, l2, l3)
# (a)
plane(a1, (-0.12, 0.86), (-0.22, 0.72))
p, phi = (0.6, 0.05), math.radians(-90)
w = (p[0] - l3 * math.cos(phi), p[1] - l3 * math.sin(phi))
cols = [C["accent"], C["z"]]
for s, col in zip(ik3r(*p, phi, *L), cols):
    draw_arm(a1, arm_pts(s, L), col, lw=4)
base_mark(a1)
a1.plot(*w, "s", color=C["ink"], ms=5, zorder=9)
a1.text(w[0] + 0.02, w[1] + 0.02, "W", fontsize=11)
a1.plot(*p, "o", color=C["x"], ms=6, zorder=9)
a1.text(p[0] - 0.07, p[1] - 0.03, "P", fontsize=11, color=C["x"])
a1.annotate("", xy=(p[0] + 0.0, p[1] - 0.12), xytext=p, arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=1.2))
a1.text(p[0] + 0.02, p[1] - 0.15, r"$\varphi = -90^\circ$", fontsize=10, color=C["x"])
a1.text(-0.1, 0.66, T("(a) 给定位置与朝向：两组解", "(a) position and orientation given: two solutions"), fontsize=10)
# (b)
plane(a2, (-0.12, 0.98), (-0.42, 0.72))
pB = np.array([0.75, 0.10])
rB = np.linalg.norm(pB)
bB = math.atan2(pB[1], pB[0])
half = math.acos((rB * rB + l3 * l3 - (l1 + l2) ** 2) / (2 * l3 * rB))
t = np.linspace(-math.pi, math.pi, 400)
a2.plot((l1 + l2) * np.cos(np.linspace(-0.5, 0.75, 100)), (l1 + l2) * np.sin(np.linspace(-0.5, 0.75, 100)), color=BLUE2, lw=1.2)
a2.text(0.80 * math.cos(0.62) - 0.02, 0.80 * math.sin(0.62) + 0.03, T("2R 的外圆", "outer circle of the 2R"), fontsize=9, color=BLUE2)
ok = np.array([abs(wrap(f - bB)) <= half for f in t])
for k, (ls, col) in enumerate((("-", C["accent"]), (":", C["muted"]))):
    sel = ok if k == 0 else ~ok
    ww = np.array([pB - l3 * np.array([math.cos(f), math.sin(f)]) for f in t])
    ww[~sel] = np.nan
    a2.plot(ww[:, 0], ww[:, 1], ls=ls, color=col, lw=1.6)
for f in np.linspace(bB - half + 0.05, bB + half - 0.05, 9):
    s = ik3r(pB[0], pB[1], f, *L)
    if s:
        draw_arm(a2, arm_pts(s[0], L), C["z"], lw=2.2, alpha=0.45, jr=0.012)
base_mark(a2)
a2.plot(*pB, "o", color=C["x"], ms=6, zorder=9)
a2.text(pB[0] + 0.03, pB[1] + 0.02, "P", fontsize=11, color=C["x"])
a2.text(0.53, -0.18, T("腕点可用的一段（实线）", "usable part of the wrist circle (solid)"), fontsize=9, color=C["accent"])
a2.text(-0.1, 0.66, T("(b) 只给位置：一族解（图中画出肘下的一支）", "(b) position only: a family (elbow-down branch drawn)"), fontsize=10)
figure(fig, "fig14_2_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 14.2.3
fig, ax = plt.subplots(figsize=(6.2, 3.4))
th = np.radians(np.linspace(0.2, 179.8, 900))
r = np.sqrt(l1 ** 2 + l2 ** 2 + 2 * l1 * l2 * np.cos(th))
sens = r / (l1 * l2 * np.sin(th))                    # |dθ2/dr|，rad/m
ax.semilogy(np.degrees(th), sens, color=C["z"], lw=1.8)
for d in (1.0, 90.0):
    rr = math.sqrt(l1 ** 2 + l2 ** 2 + 2 * l1 * l2 * math.cos(math.radians(d)))
    v = rr / (l1 * l2 * math.sin(math.radians(d)))
    ax.plot(d, v, "o", color=C["x"], ms=5)
    ax.text(d + 4, v * 1.15, f"θ₂ = {d:.0f}°", fontsize=9.5, color=C["x"])
ax.set_xlabel(T("θ₂ / (°)", "θ₂ / (°)"), fontsize=10)
ax.set_ylabel(T("|dθ₂/dr| / (rad/m)", "|dθ₂/dr| / (rad/m)"), fontsize=10)
ax.set_xlim(0, 180)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.text(60, 300, T("两端：手臂伸直（θ₂ = 0）或折回（θ₂ = 180°）", "ends: arm straight (θ₂ = 0) or folded (θ₂ = 180°)"), fontsize=9, color=C["muted"])
figure(fig, "fig14_2_3")
plt.close(fig)
