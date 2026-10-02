"""8.2 节的示意图。

图 8.2.1：左：靠墙的菜园，三边篱笆共 20 m；右：面积 S = xy 的等高线与约束直线 2x + y = 20。
         最优点处等高线与约束直线相切，∇S 与约束的梯度 ∇h 平行；在约束上的其他点，二者不平行，沿直线还能改进。
图 8.2.2：关节装有扭簧的平面 3R 臂：自然形态 θ_c（虚线），手把末端拉到 p_d 后的平衡形态（实线），
         手施加的力 F = −λ，以及各关节扭簧的力矩。
"""
import math

import numpy as np

from _fig8 import BLUE, C, GREY, ORANGE, arrow, clean, draw_arm, target
from _opt import L3R, arm_points, d, jac, tip, tip_hessians
from bookout import T, figure, style

plt = style()

# ---------------------------------------------------------------- 图 8.2.1
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.0, 5.6), gridspec_kw=dict(width_ratios=[1.0, 0.75]))
clean(a1)
a1.fill([-0.5, 10.5, 10.5, -0.5], [5.4, 5.4, 6.0, 6.0], color="#c9c2b6")
for xx in np.arange(-0.3, 10.5, 0.7):
    a1.plot([xx, xx + 0.5], [5.4, 6.0], color="#a59d90", lw=0.8)
a1.text(4.2, 6.25, T("墙", "wall"), fontsize=10)
a1.fill([0.5, 9.5, 9.5, 0.5], [0.6, 0.6, 5.4, 5.4], color="#dfeccd")
a1.plot([0.5, 0.5, 9.5, 9.5], [5.4, 0.6, 0.6, 5.4], color="#7a5a2a", lw=3)
for xx in np.linspace(0.5, 9.5, 13):
    a1.plot([xx], [0.6], "s", color="#7a5a2a", ms=4)
for yy in np.linspace(0.6, 5.4, 7):
    a1.plot([0.5, 9.5], [yy, yy], "s", color="#7a5a2a", ms=4)
a1.text(5.0, -0.1, "$y$", fontsize=13, ha="center")
a1.text(-0.2, 3.0, "$x$", fontsize=13, ha="center")
a1.text(9.8, 3.0, "$x$", fontsize=13)
a1.text(5.0, 3.0, T("菜园\n面积 S = xy", "garden\narea S = xy"), fontsize=10, ha="center", va="center")
a1.text(0.0, -1.3, T("篱笆共 20 m：2x + y = 20", "20 m of fence: 2x + y = 20"), fontsize=10)
a1.set_xlim(-0.8, 10.8)
a1.set_ylim(-1.6, 6.6)

xs = np.linspace(0.05, 11, 400)
for S, ls in ((20, ":"), (35, ":"), (50, "-"), (65, ":")):
    a2.plot(xs, S / xs, color=C["muted"] if S != 50 else BLUE, lw=0.9 if S != 50 else 1.4, ls=ls)
    xl = 8.9 if S < 50 else 8.3
    a2.text(xl, S / xl + 0.4, f"S = {S}", fontsize=8.5, color=C["muted"] if S != 50 else BLUE)
a2.plot([0, 10], [20, 0], color=C["ink"], lw=1.6)
a2.text(0.35, 20.2, T("约束 2x + y = 20", "constraint 2x + y = 20"), fontsize=9.5)
xo, yo = 5.0, 10.0
a2.plot(xo, yo, "o", color=C["x"], ms=6, zorder=6)
gs = np.array([yo, xo]) / np.hypot(yo, xo) * 3.0
gh = np.array([2.0, 1.0]) / np.hypot(2, 1) * 3.0
arrow(a2, (xo, yo), (xo + gs[0], yo + gs[1]), BLUE, 1.6)
arrow(a2, (xo, yo), (xo + gh[0] * 0.75, yo + gh[1] * 0.75), C["x"], 2.2)
a2.text(xo + gs[0] + 0.15, yo + gs[1] + 0.2, r"$\nabla S$", color=BLUE, fontsize=11)
a2.text(xo + gh[0] * 0.75 + 0.1, yo + gh[1] * 0.75 - 1.4, r"$\nabla h$", color=C["x"], fontsize=11)
a2.text(0.3, 4.2, T("最优点 (5, 10)：\n∇S ∥ ∇h，\n等高线与约束相切", "optimum (5, 10):\n∇S ∥ ∇h; the\nlevel curve\ntouches the line"),
        fontsize=9, color=C["x"])
x1, y1 = 2.0, 16.0
a2.plot(x1, y1, "o", color=ORANGE, ms=5, zorder=6)
g1 = np.array([y1, x1]) / np.hypot(y1, x1) * 3.0
arrow(a2, (x1, y1), (x1 + g1[0], y1 + g1[1]), ORANGE, 1.4)
a2.text(x1 + g1[0] + 0.2, y1 + g1[1] - 0.3, r"$\nabla S$", color=ORANGE, fontsize=10)
tdir = np.array([1.0, -2.0]) / math.sqrt(5) * 2.2
arrow(a2, (x1, y1), (x1 + tdir[0], y1 + tdir[1]), C["accent"], 1.4, ms=9)
a2.text(0.3, 9.9, T("沿约束走，\nS 还能增大", "along the\nconstraint\nS still grows"), fontsize=8.5, color=C["accent"])
a2.set_xlim(0, 11)
a2.set_ylim(0, 22)
a2.set_aspect("equal")
a2.set_xlabel("$x$ / m", fontsize=10)
a2.set_ylabel("$y$ / m", fontsize=10)
a2.tick_params(labelsize=8)
figure(fig, "fig8_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 8.2.2
L = L3R
thc = np.array([d(30), d(60), d(-60)])
Kw = np.diag([20.0, 10.0, 5.0])
pd = np.array([0.55, 0.45])
x, lam = thc.copy(), np.zeros(2)
for _ in range(20):
    Jx, H2 = jac(x, L), tip_hessians(x, L)
    HL = Kw + lam[0] * H2[0] + lam[1] * H2[1]
    st = np.linalg.solve(np.block([[HL, Jx.T], [Jx, np.zeros((2, 2))]]), -np.r_[Kw @ (x - thc) + Jx.T @ lam, tip(x, L) - pd])
    x, lam = x + st[:3], lam + st[3:]
F = -lam
tau = -Kw @ (x - thc)
fig, ax = plt.subplots(figsize=(6.6, 5.0))
clean(ax)
arrow(ax, (-0.08, 0), (0.78, 0), C["x"], 1.0)
arrow(ax, (0, -0.08), (0, 0.78), C["y"], 1.0)
ax.text(0.785, -0.02, "$x$", color=C["x"], fontsize=12)
ax.text(0.015, 0.77, "$y$", color=C["y"], fontsize=12)
pc = arm_points(thc, L)
ps = arm_points(x, L)
draw_arm(ax, pc, GREY, lw=3.0, alpha=0.8, ls=(0, (4, 2)))
draw_arm(ax, ps, BLUE, lw=3.5)
target(ax, pd)
ax.text(pc[-1][0] - 0.24, pc[-1][1] + 0.03, T(r"自然形态 $\theta_c$（扭簧不受力）", r"natural posture $\theta_c$ (springs relaxed)"), fontsize=9, color=C["muted"])
ax.text(pd[0] + 0.03, pd[1] - 0.04, T("拉到 $p_d$ 后的\n平衡形态", "equilibrium with\nthe tip at $p_d$"), fontsize=9, color=BLUE)
s = 0.006
arrow(ax, pd, pd + s * F, C["accent"], 2.2, ms=13)
ax.text(pd[0] + s * F[0] + 0.02, pd[1] + s * F[1] - 0.05, T(r"手的力 $F = -\lambda$", r"hand force $F = -\lambda$"), fontsize=10, color=C["accent"])
for i in range(3):
    c = ps[i]
    r = 0.045
    sg = 1 if tau[i] > 0 else -1
    a0 = math.radians(200)
    a_ = np.linspace(a0, a0 + sg * math.radians(min(300, 40 * abs(tau[i]))), 40)
    ax.plot(c[0] + r * np.cos(a_), c[1] + r * np.sin(a_), color=C["x"], lw=1.2)
    tipp = np.array([c[0] + r * math.cos(a_[-1]), c[1] + r * math.sin(a_[-1])])
    dirn = np.array([-math.sin(a_[-1]), math.cos(a_[-1])]) * sg
    arrow(ax, tipp - 0.004 * dirn, tipp + 0.012 * dirn, C["x"], 1.2, ms=8)
    off = [(-0.02, -0.095), (0.05, 0.0), (-0.07, 0.06)][i]
    ax.text(c[0] + off[0], c[1] + off[1], f"$\\tau_{i + 1}$ = {tau[i]:.2f} N·m".replace("-", "−"), fontsize=8.5, color=C["x"])
ax.text(-0.08, -0.2, T("扭簧刚度 k = (20, 10, 5) N·m/rad；红色弧线：扭簧作用在关节上的力矩", "spring stiffness k = (20, 10, 5) N·m/rad; red arcs: spring torques on the joints"),
        fontsize=8.5)
ax.set_xlim(-0.12, 0.92)
ax.set_ylim(-0.24, 0.82)
figure(fig, "fig8_2_2")
plt.close(fig)
