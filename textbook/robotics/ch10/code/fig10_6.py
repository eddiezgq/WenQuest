"""10.6 节的示意图。

图 10.6.1：定系 {s}、动系 {p}（以角速度 Ω 转动）、动点 P；位置矢量 r = p_O′ + r′；相对轨迹与牵连点。
图 10.6.2：算例 10.6.1，转台上的 AGV（俯视，t = 2.5 s）。(a) 相对速度、牵连速度、绝对速度与地面上的绝对轨迹；
           (b) 牵连（向心）加速度、科氏加速度与绝对加速度。
图 10.6.3：在转台上自由滚动的小球。(a) 地面上看：沿直线匀速运动；(b) 转台上看：轨迹向右弯曲（科氏偏转）。
"""
import math

import numpy as np

from _kin import A_COL, C, G_COL, V_COL, arrow, rotz
from bookout import T, figure, style

plt = style()
TABLE = "#e9edf0"

# ---------------------------------------------------------------- 图 10.6.1
fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.set_aspect("equal")
ax.axis("off")
O = np.array([0.0, 0.0])
arrow(ax, O, (1.2, 0), C["x"], 1.1)
arrow(ax, O, (0, 1.2), C["y"], 1.1)
ax.text(1.22, -0.05, "$x_s$", color=C["x"], fontsize=11)
ax.text(0.04, 1.2, "$y_s$", color=C["y"], fontsize=11)
ax.text(-0.25, -0.15, T("O（定系 {s}）", "O (fixed frame {s})"), fontsize=9.5)
Op = np.array([2.2, 0.6])
ang = math.radians(10)
ex, ey = np.array([math.cos(ang), math.sin(ang)]), np.array([-math.sin(ang), math.cos(ang)])
circ = plt.Circle(Op, 1.25, color=TABLE, zorder=0)
ax.add_patch(circ)
arrow(ax, Op, Op + 0.9 * ex, C["x"], 1.1)
arrow(ax, Op, Op + 0.9 * ey, C["y"], 1.1)
ax.text(*(Op + 0.98 * ex + np.array([0, -0.08])), "$x_p$", color=C["x"], fontsize=11)
ax.text(*(Op + 0.98 * ey + np.array([-0.12, 0])), "$y_p$", color=C["y"], fontsize=11)
ax.text(Op[0] - 0.05, Op[1] - 0.22, T("O′（动系 {p}）", "O′ (moving frame {p})"), fontsize=9.5)
t = np.linspace(-0.6, 0.8, 50)
rel = np.array([Op + (0.2 + 0.5 * (u + 0.6)) * ex + (0.3 + 0.6 * u - 0.3 * u * u) * ey for u in t])
ax.plot(rel[:, 0], rel[:, 1], color=C["accent"], lw=1.2, ls="--")
P = rel[30]
ax.text(*(rel[-1] + np.array([-0.2, 0.08])), T("相对轨迹（画在 {p} 上）", "relative path (drawn on {p})"), fontsize=9, color=C["accent"])
arrow(ax, O, Op, G_COL, 1.0)
ax.text(*(Op * 0.5 + np.array([0.02, -0.18])), r"$p_{O'}$", color=G_COL, fontsize=11)
arrow(ax, O, P, C["ink"], 1.3)
ax.text(*(P * 0.5 + np.array([-0.15, 0.08])), "$r$", fontsize=12)
arrow(ax, Op, P, C["z"], 1.3)
ax.text(*((Op + P) / 2 + np.array([-0.16, 0.04])), "$r'$", color=C["z"], fontsize=12)
ax.plot(*P, "o", color=C["ink"], ms=5, zorder=6)
ax.text(P[0] + 0.08, P[1] - 0.12, T("动点 P", "moving point P"), fontsize=9.5)
a = np.linspace(math.radians(200), math.radians(320), 40)
ax.plot(Op[0] + 1.38 * np.cos(a), Op[1] + 1.38 * np.sin(a), color=C["ink"], lw=1.0)
arrow(ax, (Op[0] + 1.38 * math.cos(a[-2]), Op[1] + 1.38 * math.sin(a[-2])), (Op[0] + 1.38 * math.cos(a[-1]), Op[1] + 1.38 * math.sin(a[-1])), C["ink"], 1.0)
ax.text(Op[0] + 0.25, Op[1] - 1.55, r"$\Omega$", fontsize=13)
ax.text(-0.3, -1.3, T("P 此刻所在的、固连于转台的那一点，称为牵连点", "the point of the table where P is at this instant: the coincident point"),
        fontsize=9)
ax.set_xlim(-0.4, 3.8)
ax.set_ylim(-1.4, 2.3)
figure(fig, "fig10_6_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 10.6.2
Om, vr, t1 = 0.5, 0.4, 2.5
psi = Om * t1
R = rotz(psi)[:2, :2]
er, ep = R @ np.array([1.0, 0]), R @ np.array([0, 1.0])
P = 1.0 * er
fig, axs = plt.subplots(1, 2, figsize=(9.6, 4.6))
for ax in axs:
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(plt.Circle((0, 0), 1.5, color=TABLE, zorder=0))
    ax.plot([0, 1.5 * er[0]], [0, 1.5 * er[1]], color=G_COL, lw=0.8, ls="-.")
    ax.plot(0, 0, "o", color=C["ink"], ms=3)
    a = np.linspace(math.radians(-60), math.radians(10), 30)
    ax.plot(1.65 * np.cos(a), 1.65 * np.sin(a), color=C["ink"], lw=1.0)
    arrow(ax, (1.65 * math.cos(a[-2]), 1.65 * math.sin(a[-2])), (1.65 * math.cos(a[-1]), 1.65 * math.sin(a[-1])), C["ink"], 1.0)
    ax.text(1.72, -0.6, r"$\Omega$", fontsize=13)
    car = np.array([[-0.14, -0.1], [0.14, -0.1], [0.14, 0.1], [-0.14, 0.1], [-0.14, -0.1]]) @ R.T + P
    ax.fill(car[:, 0], car[:, 1], color="#1f77b4", alpha=0.35)
    ax.plot(car[:, 0], car[:, 1], color="#1f77b4", lw=1.0)
    ax.text(*(P - 0.2 * ep + np.array([0.0, -0.06])), "AGV", fontsize=9.5, color="#1f77b4")
    ax.text(-1.85, -2.05, T("点划线：转台上画的一条半径，AGV 沿它行驶", "dash-dot: a radius drawn on the table, the AGV drives along it"),
            fontsize=8.5, color=G_COL)
ax = axs[0]
tt = np.linspace(0, 3.75, 200)
spiral = np.array([vr * t * np.array([math.cos(Om * t), math.sin(Om * t)]) for t in tt])
ax.plot(spiral[:, 0], spiral[:, 1], color=C["accent"], lw=1.2, ls="--")
ax.text(-1.85, -1.85, T("虚线：地面上的绝对轨迹（阿基米德螺线）", "dashed: absolute path on the ground (Archimedean spiral)"), fontsize=8.5, color=C["accent"])
k = 1.2
vrel, vtr = vr * er, Om * 1.0 * ep
for vec, lab, col, ls, off in ((vrel, r"$v_{\mathrm{rel}}$", C["x"], "--", (0.03, -0.12)), (vtr, r"$v_{\mathrm{tr}}$", C["y"], "--", (-0.25, 0.0)),
                               (vrel + vtr, r"$v_{\mathrm{abs}}$", V_COL, "-", (0.02, 0.04))):
    arrow(ax, P, P + k * vec, col, 1.8 if ls == "-" else 1.2, ls=ls)
    ax.text(*(P + k * vec + np.array(off)), lab, color=col, fontsize=11)
ax.set_title(T("(a) 速度", "(a) Velocities"), fontsize=11)
ax.set_xlim(-1.9, 2.0)
ax.set_ylim(-2.1, 1.9)
ax = axs[1]
k = 1.6
atr, aC = -Om ** 2 * 1.0 * er, 2 * Om * vr * ep
for vec, lab, col, ls, off in ((atr, r"$a_{\mathrm{tr}}$", C["x"], "--", (0.06, -0.12)), (aC, r"$a_C = 2\Omega\times v_{\mathrm{rel}}$", C["y"], "--", (-0.9, 0.08)),
                               (atr + aC, r"$a_{\mathrm{abs}}$", A_COL, "-", (-0.3, 0.05))):
    arrow(ax, P, P + k * vec, col, 1.8 if ls == "-" else 1.2, ls=ls)
    ax.text(*(P + k * vec + np.array(off)), lab, color=col, fontsize=11)
ax.set_title(T("(b) 加速度（相对加速度为零）", "(b) Accelerations (relative acceleration zero)"), fontsize=11)
ax.set_xlim(-1.9, 2.0)
ax.set_ylim(-2.1, 1.9)
figure(fig, "fig10_6_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 10.6.3
v0, Om = 0.6, 0.5
tt = np.linspace(0, 2.5, 200)
ground = np.array([[v0 * t, 0.0] for t in tt])
table = np.array([rotz(-Om * t)[:2, :2] @ np.array([v0 * t, 0.0]) for t in tt])
fig, axs = plt.subplots(1, 2, figsize=(9.2, 4.4))
for ax, path, title, rot in ((axs[0], ground, T("(a) 地面上看", "(a) Seen from the ground"), True),
                             (axs[1], table, T("(b) 转台上看", "(b) Seen on the table"), False)):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(plt.Circle((0, 0), 1.5, color=TABLE, zorder=0))
    if rot:
        for k in range(4):                 # 转台上画的四条半径：t = 2.5 s 时的位置
            a = Om * 2.5 + k * math.pi / 2
            ax.plot([0, 1.5 * math.cos(a)], [0, 1.5 * math.sin(a)], color=G_COL, lw=0.7, ls="-.")
        a = np.linspace(math.radians(-60), math.radians(10), 30)
        ax.plot(1.65 * np.cos(a), 1.65 * np.sin(a), color=C["ink"], lw=1.0)
        arrow(ax, (1.65 * math.cos(a[-2]), 1.65 * math.sin(a[-2])), (1.65 * math.cos(a[-1]), 1.65 * math.sin(a[-1])), C["ink"], 1.0)
        ax.text(1.72, -0.6, r"$\Omega$", fontsize=13)
    else:
        for k in range(4):
            a = k * math.pi / 2
            ax.plot([0, 1.5 * math.cos(a)], [0, 1.5 * math.sin(a)], color=G_COL, lw=0.7, ls="-.")
    ax.plot(path[:, 0], path[:, 1], color=C["accent"], lw=1.8)
    for k in range(0, 200, 40):
        ax.plot(*path[k], "o", color=C["accent"], ms=5, alpha=0.5)
    ax.plot(*path[-1], "o", color=C["accent"], ms=8)
    ax.set_title(title, fontsize=11)
    ax.set_xlim(-1.8, 1.9)
    ax.set_ylim(-1.8, 1.8)
axs[0].text(-1.7, -1.75, T("小球不受水平力：直线、匀速", "no horizontal force: straight line, constant speed"), fontsize=9)
axs[1].text(-1.7, -1.75, T("转台逆时针转，小球的相对轨迹向右弯", "the table turns anticlockwise; the relative path bends right"), fontsize=9)
figure(fig, "fig10_6_3")
plt.close(fig)
