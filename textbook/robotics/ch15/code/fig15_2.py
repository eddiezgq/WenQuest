"""15.2 节的示意图。

图 15.2.1：雅可比转置法的力学解释（平面 2R 臂，算例 15.2.1）。(a) 末端被一根虚拟弹簧拉向目标，关节力矩 τ = Jᵀ F；
           (b) 末端走过的路线：雅可比转置法（固定步长 α = 3、每步最优 α）与牛顿法。
图 15.2.2：收敛速度。(a) 平面 2R 臂；(b) UR5e（算例 15.2.2），不同权重下的雅可比转置法与牛顿-拉夫森法。
"""
import math

import numpy as np

from _fig15 import BLUE2, C, arc, arrow2, base_mark, draw_arm, logaxis, plane
from _nik import L2R, PD2R, TH_CUR, fk_planar, jac_planar, joints_planar, jt, jt_planar, newton_planar, nr, ur_fk, ur_jb, ur_target
from bookout import T, figure, style

plt = style()
th0 = np.array([0.0, 1.0])

# ---------------------------------------------------------------- 图 15.2.1
fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.6))
ax = axs[0]
plane(ax, (-0.12, 0.92), (-0.12, 0.62))
base_mark(ax)
P = joints_planar(th0, L2R)
draw_arm(ax, P, C["z"], lw=6)
p, e = P[-1], PD2R - P[-1]
# 弹簧（锯齿线）
n = 14
u = e / np.linalg.norm(e)
w = np.array([-u[1], u[0]])
zz = [p + u * 0.012]
for i in range(1, n):
    zz.append(p + u * 0.012 + (e - 0.024 * u) * i / n + w * 0.012 * (1 if i % 2 else -1))
zz.append(PD2R - u * 0.012)
zz = np.array(zz)
ax.plot(zz[:, 0], zz[:, 1], color=C["accent"], lw=1.2, zorder=5)
ax.plot(*PD2R, "o", color=C["x"], ms=8, zorder=8)
ax.text(PD2R[0] - 0.04, PD2R[1] + 0.035, T("目标", "target"), fontsize=10, color=C["x"])
arrow2(ax, p, p + 0.55 * e, C["x"], lw=2.0, ms=14)
ax.text(p[0] - 0.02, p[1] - 0.06, "F = kₛ e", fontsize=11, color=C["x"])
J = jac_planar(th0, L2R)
tau = J.T @ (100 * e)
arc(ax, P[0], 0.09, 0.3, 1.9, C["y"], lw=1.6, arrow=True)
ax.text(P[0][0] + 0.02, P[0][1] + 0.11, f"τ₁ = {tau[0]:.2f} N·m", fontsize=10, color=C["y"])
arc(ax, P[1], 0.07, 1.4, 2.9, C["y"], lw=1.6, arrow=True)
ax.text(P[1][0] - 0.2, P[1][1] + 0.08, f"τ₂ = {tau[1]:.2f} N·m", fontsize=10, color=C["y"])
ax.text(-0.1, 0.58, T("(a) 虚拟弹簧：τ = Jᵀ F", "(a) A virtual spring: τ = Jᵀ F"), fontsize=11)
ax.text(-0.1, -0.1, T("kₛ = 100 N/m；逆时针为正", "kₛ = 100 N/m; counter-clockwise positive"), fontsize=9, color=C["muted"])

ax = axs[1]
plane(ax, (0.3, 0.72), (0.18, 0.52))
_, _, _, TH3 = jt_planar(PD2R, th0, alpha=3.0)
_, _, _, THb = jt_planar(PD2R, th0)
_, _, _, THn = newton_planar(PD2R, th0)
for TH, c, lab, m in ((TH3, C["accent"], T("雅可比转置，α = 3", "Jacobian transpose, α = 3"), "."),
                      (THb, C["z"], T("雅可比转置，最优 α", "Jacobian transpose, optimal α"), "o"),
                      (THn, C["x"], T("牛顿法", "Newton"), "s")):
    tips = np.array([fk_planar(t, L2R)[:2] for t in TH])
    ax.plot(tips[:, 0], tips[:, 1], color=c, lw=1.3, marker=m, ms=3.5 if m != "." else 4, label=lab, zorder=4)
ax.plot(*PD2R, "o", color=C["x"], ms=9, mfc="none", mew=1.5, zorder=6)
ax.plot(*fk_planar(th0, L2R)[:2], "o", color=C["ink"], ms=6, zorder=6)
ax.text(fk_planar(th0, L2R)[0] - 0.02, fk_planar(th0, L2R)[1] + 0.015, T("起点", "start"), fontsize=10)
ax.text(PD2R[0] - 0.045, PD2R[1] - 0.025, T("目标", "target"), fontsize=10, color=C["x"])
ax.legend(fontsize=9, frameon=False, loc="lower right")
ax.text(0.305, 0.505, T("(b) 末端走过的路线（局部放大）", "(b) Paths of the tip (close-up)"), fontsize=11)
fig.tight_layout()
figure(fig, "fig15_2_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 15.2.2
fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.0))
ax = axs[0]
J = jac_planar(np.array([-0.0967868, 1.598687]), L2R)
for a, c, lab in ((1.0, C["muted"], "α = 1"), (3.0, C["accent"], "α = 3"), (None, C["z"], T("最优 α", "optimal α"))):
    _, _, E, _ = jt_planar(PD2R, th0, alpha=a)
    ax.plot(range(len(E)), E, color=c, lw=1.5, label=T("雅可比转置，", "Jacobian transpose, ") + lab)
_, _, E, _ = newton_planar(PD2R, th0)
ax.plot(range(len(E)), E, color=C["x"], lw=1.5, marker="s", ms=4, label=T("牛顿法", "Newton"))
logaxis(ax)
ax.set_ylim(1e-11, 1)
ax.set_xlabel(T("迭代次数 k", "iteration k"))
ax.set_ylabel(T("‖e‖ / m", "‖e‖ / m"))
ax.legend(fontsize=8.5, frameon=False)
ax.set_title(T("(a) 平面 2R 臂（算例 15.2.1）", "(a) Planar 2R arm (Example 15.2.1)"), fontsize=10.5, loc="left")

ax = axs[1]
Td = ur_target()
for Lc, c, lab in ((None, C["muted"], T("不加权", "unweighted")), (0.3, C["z"], "$L_c$ = 0.3 m"), (0.1, C["accent"], "$L_c$ = 0.1 m")):
    W = None if Lc is None else np.diag([1, 1, 1] + [1 / Lc ** 2] * 3)
    _, _, h = jt(ur_fk, ur_jb, Td, TH_CUR, W=W, tol_w=1e-9, tol_v=1e-9, iters=50000)
    y = [float(np.linalg.norm(V)) for _, V in h]
    ax.plot(np.arange(1, len(y) + 1), y, color=c, lw=1.5, label=T("雅可比转置，", "Jacobian transpose, ") + lab)
_, _, h = nr(ur_fk, ur_jb, Td, TH_CUR)
y = [max(float(np.linalg.norm(V)), 1e-16) for _, V in h]
ax.plot(np.arange(1, len(y) + 1), y, color=C["x"], lw=1.5, marker="s", ms=4, label=T("牛顿-拉夫森", "Newton-Raphson"))
logaxis(ax)
ax.set_xscale("log")
ax.set_ylim(1e-16, 1)
ax.set_xlabel(T("迭代次数 k + 1（对数坐标）", "iteration k + 1 (log scale)"))
ax.set_ylabel(T("‖V$_b$‖", "‖V$_b$‖"))
ax.legend(fontsize=8.5, frameon=False, loc="lower left")
ax.set_title(T("(b) UR5e（算例 15.2.2）", "(b) UR5e (Example 15.2.2)"), fontsize=10.5, loc="left")
fig.tight_layout()
figure(fig, "fig15_2_2")
plt.close(fig)
