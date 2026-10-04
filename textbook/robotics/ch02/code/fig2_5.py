"""2.5 节的示意图。

图 2.5.1：平面 TCP 标定：机器人以不同姿态让工具尖端碰到同一个顶针 c；法兰位置 p_i 和转角 φ_i 由控制器读出，
         工具尖端在法兰坐标系中的位置 t 未知。
图 2.5.2：最小二乘的几何意义：b 在 A 的值域上的正交投影。左：A 只有一列（值域是一条直线）；右：A 有两列（值域是一个平面）。
         残差 r = b − Ax̂ 垂直于值域。
图 2.5.3：弹簧秤的直线拟合（算例 2.5.2）与残差。
"""
import math

import numpy as np

from _la import C, arrow, rot2
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 2.5.1
t_true = np.array([0.120, 0.035])
c = np.array([0.650, 0.150])
fig, ax = plt.subplots(figsize=(6.4, 4.4))
ax.set_aspect("equal")
ax.axis("off")
arrow(ax, (0.36, -0.05), (0.82, -0.05), C["x"], 1.0)           # x_s 轴放低一些，不压 φ = 80° 的标注
arrow(ax, (0.38, -0.07), (0.38, 0.3), C["y"], 1.0)
ax.text(0.825, -0.06, r"$x_s$", color=C["x"], fontsize=11)
ax.text(0.385, 0.29, r"$y_s$", color=C["y"], fontsize=11)
ax.plot(*c, "o", color=C["ink"], ms=7, zorder=6)
ax.plot([c[0], c[0]], [c[1] - 0.06, c[1]], color=C["ink"], lw=3)
ax.text(c[0] + 0.012, c[1] + 0.016, T("顶针 c", "pin c"), fontsize=10)      # 放在顶针右上方，不被工具线穿过
for k, deg in enumerate((-40, 20, 80)):
    f = math.radians(deg)
    R = rot2(f)
    p = c - R @ t_true
    # 法兰（小方块）与工具
    sq = p[:, None] + R @ (np.array([[-0.02, 0.02, 0.02, -0.02, -0.02], [-0.025, -0.025, 0.025, 0.025, -0.025]]))
    ax.fill(sq[0], sq[1], color="#c9d0d5", zorder=3)
    tool = np.array([p, p + R @ np.array([t_true[0], 0]), c])
    ax.plot(tool[:, 0], tool[:, 1], color=C["accent"], lw=3, zorder=4, solid_capstyle="round")
    for j, col in enumerate((C["x"], C["y"])):
        arrow(ax, p, p + 0.05 * R[:, j], col, 1.2, z=5, ms=8)
    ax.plot(*p, "o", color=C["ink"], ms=3, zorder=6)
    off = {0: (-0.075, -0.005), 1: (-0.07, -0.02), 2: (0.03, -0.02)}[k]
    ax.text(p[0] + off[0], p[1] + off[1], rf"$p_{k + 1}$", fontsize=11)
    ax.text(p[0] + off[0] - 0.01, p[1] + off[1] - 0.025, f"φ = {deg}°".replace("-", "−"), fontsize=8.5, color=C["muted"])
ax.text(0.36, 0.33, T("金色：工具；t = 尖端在法兰坐标系中的位置（未知）", "gold: the tool; t = position of the tool tip in the flange frame (unknown)"),
        fontsize=9, color=C["ink"])
ax.text(0.36, 0.305, T("每次接触：R(φᵢ) t + pᵢ = c，两个方程", "each touch: R(φᵢ) t + pᵢ = c, two equations"), fontsize=9, color=C["ink"])
ax.set_xlim(0.34, 0.86)
ax.set_ylim(-0.09, 0.35)
figure(fig, "fig2_5_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 2.5.2
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.4, 3.8))
for ax in (a1, a2):
    ax.set_aspect("equal")
    ax.axis("off")
a = np.array([2.0, 0.6])
b = np.array([1.0, 1.6])
xh = (a @ b) / (a @ a)
p = xh * a
a1.plot([-0.4 * a[0], 1.35 * a[0]], [-0.4 * a[1], 1.35 * a[1]], color=C["z"], lw=1.0)
a1.text(1.36 * a[0] - 0.1, 1.36 * a[1] + 0.08, T("A 的值域", "range of A"), color=C["z"], fontsize=10)
arrow(a1, (0, 0), a, C["z"], 2.0)
a1.text(a[0] - 0.05, a[1] - 0.22, "$a$", color=C["z"], fontsize=12)
arrow(a1, (0, 0), b, C["ink"], 2.0)
a1.text(b[0] - 0.15, b[1] + 0.05, "$b$", fontsize=12)
arrow(a1, (0, 0), p, C["accent"], 2.4)
a1.text(p[0] - 0.2, p[1] - 0.28, r"$\hat x\,a$", color=C["accent"], fontsize=12)
a1.plot([p[0], b[0]], [p[1], b[1]], color=C["x"], lw=1.6, ls="--")
a1.text((p[0] + b[0]) / 2 + 0.05, (p[1] + b[1]) / 2, r"$r = b - \hat x a$", color=C["x"], fontsize=11)
u = a / np.linalg.norm(a)
nrm = (b - p) / np.linalg.norm(b - p)
sq = np.array([p + 0.12 * u, p + 0.12 * u + 0.12 * nrm, p + 0.12 * nrm])
a1.plot(sq[:, 0], sq[:, 1], color=C["ink"], lw=0.8)
other = 1.2 * a
a1.plot([other[0], b[0]], [other[1], b[1]], color=C["muted"], lw=0.9, ls=":")
a1.plot(*other, "o", color=C["muted"], ms=3)
a1.text(other[0] + 0.05, other[1] - 0.2, T("别的 x：残差更长", "another x: longer residual"), fontsize=8.5, color=C["muted"])
a1.set_xlim(-0.9, 3.1)
a1.set_ylim(-0.6, 2.0)
a1.text(-0.9, -0.55, T("一个未知数：b 投影到一条直线上", "one unknown: b projected onto a line"), fontsize=9.5)


def P3(v):                         # 斜二测：x 向右下、y 向右、z 向上
    x, y, z = v
    return np.array([y - 0.5 * x, z - 0.32 * x])


c1, c2 = np.array([2.0, 0.0, 0.0]), np.array([0.0, 2.6, 0.0])
corners = [-0.3 * c1 - 0.2 * c2, 1.2 * c1 - 0.2 * c2, 1.2 * c1 + 1.0 * c2, -0.3 * c1 + 1.0 * c2]
poly = np.array([P3(v) for v in corners])
a2.fill(poly[:, 0], poly[:, 1], color="#dce8f3", alpha=0.8)
a2.plot(*np.vstack([poly, poly[:1]]).T, color=C["z"], lw=0.8)
B = np.array([1.0, 1.6, 1.5])
Pb = np.array([1.0, 1.6, 0.0])
arrow(a2, P3((0, 0, 0)), P3(c1 * 0.7), C["z"], 1.8)
arrow(a2, P3((0, 0, 0)), P3(c2 * 0.5), C["z"], 1.8)
a2.text(*(P3(c1 * 0.7) + np.array([-0.25, -0.15])), r"$a_1$", color=C["z"], fontsize=12)
a2.text(*(P3(c2 * 0.5) + np.array([0.08, 0.06])), r"$a_2$", color=C["z"], fontsize=12)
arrow(a2, P3((0, 0, 0)), P3(B), C["ink"], 2.0)
a2.text(*(P3(B) + np.array([-0.2, 0.08])), "$b$", fontsize=12)
arrow(a2, P3((0, 0, 0)), P3(Pb), C["accent"], 2.4)
a2.text(*(P3(Pb) + np.array([0.05, -0.28])), r"$A\hat x$", color=C["accent"], fontsize=12)
a2.plot(*np.array([P3(Pb), P3(B)]).T, color=C["x"], lw=1.6, ls="--")
a2.text(*(P3((Pb + B) / 2) + np.array([0.08, 0.0])), r"$r \perp a_1,\ a_2$", color=C["x"], fontsize=11)
a2.text(*(P3(-0.3 * c1 + 1.0 * c2) + np.array([-0.9, -0.3])), T("A 的值域", "range of A"), color=C["z"], fontsize=10)
a2.set_xlim(-0.9, 3.2)
a2.set_ylim(-1.2, 2.0)
a2.text(-0.9, -1.15, T("两个未知数：b 投影到一个平面上", "two unknowns: b projected onto a plane"), fontsize=9.5)
figure(fig, "fig2_5_2")
plt.close(fig)

# ---------------------------------------------------------------- 图 2.5.3
m = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0])
y = np.array([0.3, 10.2, 19.6, 30.4, 40.1, 49.6])
k, b0 = np.polyfit(m, y, 1)
fig, (l, r_) = plt.subplots(1, 2, figsize=(9.0, 3.4), gridspec_kw={"width_ratios": [1.3, 1]})
l.plot(m, y, "o", color=C["ink"], ms=5, label=T("读数", "readings"))
mm = np.linspace(-0.2, 5.2, 10)
l.plot(mm, k * mm + b0, color=C["accent"], lw=1.6, label=T("最小二乘直线", "least-squares line"))
l.set_xlabel(T("砝码质量 m / kg", "mass m / kg"))
l.set_ylabel(T("弹簧伸长 y / mm", "extension y / mm"))
l.legend(frameon=False)
l.spines[["top", "right"]].set_visible(False)
res = y - (k * m + b0)
r_.axhline(0, color=C["muted"], lw=0.8)
r_.vlines(m, 0, res, color=C["x"], lw=2.5)
r_.plot(m, res, "o", color=C["x"], ms=4)
r_.set_xlabel(T("砝码质量 m / kg", "mass m / kg"))
r_.set_ylabel(T("残差 / mm", "residual / mm"))
r_.spines[["top", "right"]].set_visible(False)
figure(fig, "fig2_5_3")
plt.close(fig)
