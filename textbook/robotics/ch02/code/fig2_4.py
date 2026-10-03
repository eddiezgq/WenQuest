"""2.4 节的示意图。

图 2.4.1：奇异值分解的几何意义（J 为算例 2.4.1 的雅可比矩阵）：单位圆 →（Vᵀ：转动）→ 圆 →（Σ：沿坐标轴伸缩）→
         椭圆 →（U：转动）→ 椭圆。v1、v2 变成 σ1u1、σ2u2。
图 2.4.2：平面 2R 臂的可操作度椭圆（关节速度取单位圆时末端速度的集合）在三种形态下的样子，以及 σ1、σ2、σ1σ2 随 θ2 的变化。
"""
import math

import numpy as np

from _la import C, L2R, arm_points, arrow, base, d, draw_arm, ellipse_pts, jac
from bookout import T, figure, style

plt = style()

J = jac([d(30), d(60)], L2R)
U, s, Vt = np.linalg.svd(J)
V = Vt.T
if V[0, 0] < 0:            # 与算例 2.4.1 取同样的符号
    V[:, 0] *= -1
    U[:, 0] *= -1
if np.linalg.det(V) < 0:
    V[:, 1] *= -1
    U[:, 1] *= -1
S = np.diag(s)
k = 1.0 / s[0]             # 画图比例：把最长的半轴画成 1

# ---------------------------------------------------------------- 图 2.4.1
stages = [(np.eye(2), T(r"单位圆：关节速度 $\dot\theta$", r"unit circle: joint speeds $\dot\theta$"), V),
          (Vt, T("① 乘 Vᵀ：转动", "① Vᵀ: rotate"), np.eye(2)),
          (k * S @ Vt, T("② 乘 Σ：沿坐标轴伸缩", "② Σ: stretch along axes"), k * S),
          (k * U @ S @ Vt, T("③ 乘 U：再转动，得 J 的像", "③ U: rotate; image under J"), k * U @ S)]
fig, axs = plt.subplots(1, 4, figsize=(10.4, 3.2))
for i, (ax, (M, title, cols)) in enumerate(zip(axs, stages)):
    ax.set_aspect("equal")
    ax.axis("off")
    ax.plot([-1.25, 1.25], [0, 0], color="#d5dade", lw=0.7)
    ax.plot([0, 0], [-1.25, 1.25], color="#d5dade", lw=0.7)
    E = ellipse_pts(M)
    ax.fill(E[0], E[1], color="#f3e2b3", alpha=0.6, lw=0)
    ax.plot(E[0], E[1], color=C["accent"], lw=1.2)
    for j, col in enumerate((C["x"], C["z"])):
        arrow(ax, (0, 0), cols[:, j], col, 2.0)
    lab1 = (r"$v_1$", r"$v_2$") if i == 0 else (r"$e_1$", r"$e_2$") if i == 1 else (r"$\sigma_1 e_1$", r"$\sigma_2 e_2$") if i == 2 else (r"$\sigma_1 u_1$", r"$\sigma_2 u_2$")
    for j, col in enumerate((C["x"], C["z"])):
        p = cols[:, j]
        off = np.array([0.08, 0.06]) if j == 0 else np.array([0.06, -0.14])
        if i == 0 and j == 1:
            off = np.array([-0.3, 0.02])
        if i == 3:
            off = np.array([-0.32, 0.1]) if j == 0 else np.array([0.05, -0.05])
        ax.text(p[0] + off[0], p[1] + off[1], lab1[j], color=col, fontsize=11)
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.text(-1.3, -1.55, title, fontsize=9.5, color=C["ink"])
fig.text(0.02, 0.0, T("J = UΣVᵀ：任何矩阵都把单位圆变成椭圆；椭圆的半轴长是奇异值，方向是 U 的列（图中按 σ₁ 画成 1 的比例缩小）",
                        "J = UΣVᵀ: every matrix maps the unit circle to an ellipse; semi-axes = singular values, directions = columns of U (scaled so σ₁ is drawn as 1)"),
         fontsize=9, color=C["ink"])
figure(fig, "fig2_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 2.4.2
fig = plt.figure(figsize=(10.0, 3.9))
ax = fig.add_axes([0.0, 0.08, 0.5, 0.9])
ax.set_aspect("equal")
ax.axis("off")
base(ax, w=0.05)
kk = 0.25                      # 1 m/s 画成 0.25 m
for n, (t2, col, lab) in enumerate(((5, C["x"], "θ₂ = 5°"), (60, C["accent"], "θ₂ = 60°"), (120, C["z"], "θ₂ = 120°"))):
    th = [d(30), d(t2)]
    pts = arm_points(th, L2R)
    draw_arm(ax, pts, col, lw=4, alpha=0.85)
    E = ellipse_pts(kk * jac(th, L2R)) + pts[-1][:, None]
    ax.plot(E[0], E[1], color=col, lw=1.4)
    ax.text(0.68, 0.9 - 0.07 * n, lab, fontsize=10.5, color=col)
ax.set_xlim(-0.15, 1.0)
ax.set_ylim(-0.08, 0.95)
ax.text(-0.15, -0.07, T(r"椭圆：$|\dot\theta|$ = 1 rad/s 时末端速度的端点（1 m/s 画成 0.25 m）", r"ellipses: end-effector velocities for $|\dot\theta|$ = 1 rad/s (1 m/s drawn as 0.25 m)"),
        fontsize=9, color=C["ink"])
ax2 = fig.add_axes([0.58, 0.17, 0.4, 0.75])
t2 = np.arange(0, 181)
ss = np.array([np.linalg.svd(jac([0, d(a)], L2R), compute_uv=False) for a in t2])
ax2.plot(t2, ss[:, 0], color=C["x"], lw=1.5, label=r"$\sigma_1$")
ax2.plot(t2, ss[:, 1], color=C["z"], lw=1.5, label=r"$\sigma_2$")
ax2.plot(t2, ss[:, 0] * ss[:, 1], color=C["accent"], lw=1.8, label=r"$w = \sigma_1\sigma_2$")
ax2.axvline(90, color=C["muted"], lw=0.8, ls=":")
ax2.set_xlim(0, 180)
ax2.set_xticks([0, 30, 60, 90, 120, 150, 180])
ax2.set_xlabel(T(r"$\theta_2$ / (°)", r"$\theta_2$ / deg"))
ax2.set_ylabel(T("m/s 每 rad/s（w：m²）", "m/s per rad/s (w: m²)"))
ax2.legend(frameon=False, fontsize=10)
ax2.spines[["top", "right"]].set_visible(False)
figure(fig, "fig2_4_2")
plt.close(fig)
