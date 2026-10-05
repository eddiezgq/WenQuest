"""16.4 节的示意图。

图 16.4.1：UR5e 在 θ* 处的两个椭球（算例 16.4.1）。(a) 法兰盘中心的线速度椭球（J_v 的像），画出三个半轴 σ_i u_i；
           (b) 角速度椭球（J_ω 的像）：半轴 √3、√2、1，分别沿 y′（关节 2、3、4）、竖直方向（关节 1、6）和关节 5 的轴。
图 16.4.2：算例 16.4.2：法兰盘姿态与高度不变、中心沿水平射线移动。(a) 手臂平面内的侧视：三个位置的手臂与
           “姿态保持”线速度椭球在该竖直平面内的截面；(b) 可操作度、最小半轴与 1/κ 随 ρ 的变化（姿态保持，实线；
           姿态可变的 J_v，虚线），三个指标的最优位置不同，两端（肩部、肘部奇异）姿态保持的椭球退化。
"""
import math

import numpy as np

from _fig16 import C, axes3d, draw_chain, equal3d, floor3d, ur_chain
from _jac import (D4, TH_STAR, ellipsoid, held_ellipsoid, manip, svals, ur_fk, ur_ik, ur_jv, ur_jw, ur_radial, ur_radial_point)
from bookout import T, figure, style

plt = style()


def wire(ax, c, A, color, n=14, lw=0.45, alpha=0.4):
    """以 c 为中心、A（3×3，列为半轴矢量）的椭球线框。"""
    u, v = np.meshgrid(np.linspace(0, 2 * math.pi, 2 * n), np.linspace(0, math.pi, n))
    S = np.stack([np.cos(u) * np.sin(v), np.sin(u) * np.sin(v), np.cos(v)])
    P = np.einsum("ij,jkl->ikl", A, S)
    ax.plot_wireframe(c[0] + P[0], c[1] + P[1], c[2] + P[2], color=color, lw=lw, alpha=alpha, rstride=1, cstride=1)


# ---------------------------------------------------------------- 图 16.4.1
fig = plt.figure(figsize=(11.6, 4.8))
_, ax = axes3d(plt, fig=fig, pos=121, elev=22, azim=-125)
P = ur_chain(TH_STAR)
floor3d(ax, 0.55)
draw_chain(ax, P, C["z"], lw=5)
p = ur_fk(TH_STAR)[:3, 3]
sv, U = ellipsoid(ur_jv(TH_STAR))
sc = 0.3                                                  # 作图比例：1 m/s（每 rad/s）画成 0.25 m
wire(ax, p, sc * U * sv, C["accent"])
labs = []
for k, col in enumerate((C["x"], C["y"], C["z"])):
    d = sc * sv[k] * U[:, k] * np.sign(U[np.argmax(np.abs(U[:, k])), k])
    ax.quiver(*p, *d, color=col, lw=2.0, arrow_length_ratio=0.15)
    labs.append((p + d * (1.25, 1.35, 1.9)[k], rf"$\sigma_{k + 1}u_{k + 1}$", col))
ax.text2D(0.02, 0.95, T("(a) 法兰盘中心的线速度椭球", "(a) velocity ellipsoid of the flange centre"), transform=ax.transAxes, fontsize=11)
ax.text2D(0.02, 0.89, T("半轴（每 rad/s）：", "semi-axes (per rad/s): ") + ", ".join(f"{x:.3f}" for x in sv) + " m/s",
          transform=ax.transAxes, fontsize=9, color=C["muted"])
equal3d(ax, np.vstack([P, p + 0.3 * np.eye(3), p - 0.3 * np.eye(3)]), pad=0.02, zoom=1.15)
from mpl_toolkits.mplot3d import proj3d
for X, s, col in labs:                                    # 标注画在最上层（二维坐标），不被连杆遮住
    x2, y2, _ = proj3d.proj_transform(*X, ax.get_proj())
    ax.annotate(s, (x2, y2), fontsize=10, color=col, ha="center", va="center", zorder=20,
                bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.5))

_, ax = axes3d(plt, fig=fig, pos=122, elev=24, azim=-105)
sw, Uw = ellipsoid(ur_jw(TH_STAR))
wire(ax, np.zeros(3), Uw * sw, C["accent"])
names = [r"$\sqrt{3}\ \ (y')$", r"$\sqrt{2}\ \ (z)$", T("1（关节 5 的轴）", "1 (axis of joint 5)")]
for k, col in enumerate((C["x"], C["y"], C["z"])):
    d = sw[k] * Uw[:, k] * np.sign(Uw[np.argmax(np.abs(Uw[:, k])), k])
    ax.quiver(0, 0, 0, *d, color=col, lw=2.0, arrow_length_ratio=0.12)
    ax.text(*(d * 1.12), names[k], fontsize=10, color=col)
ax.text2D(0.02, 0.95, T("(b) 角速度椭球", "(b) angular-velocity ellipsoid"), transform=ax.transAxes, fontsize=11)
ax.text2D(0.02, 0.89, T("半轴（rad/s 每 rad/s）：√3、√2、1", "semi-axes (rad/s per rad/s): √3, √2, 1"),
          transform=ax.transAxes, fontsize=9, color=C["muted"])
equal3d(ax, np.array([[-1.8, -1.8, -1.8], [1.8, 1.8, 1.8]]), pad=0.0, zoom=1.1)
fig.subplots_adjust(wspace=0.02)
figure(fig, "fig16_4_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 16.4.2
p0 = ur_fk(TH_STAR)[:3, 3]
er = np.array([p0[0], p0[1], 0.0]) / math.hypot(p0[0], p0[1])     # 水平径向
ez = np.array([0, 0, 1.0])
lo_, hi_ = 0.67, 1.2
for _ in range(60):
    m = (lo_ + hi_) / 2
    Tm = ur_fk(TH_STAR)
    Tm[:3, 3] = ur_radial_point(m)
    lo_, hi_ = (m, hi_) if ur_ik(Tm) else (lo_, m)
rho_max = lo_
rhos = np.linspace(0.20, rho_max - 1e-4, 240)
Q = ur_radial(rhos)
W, S, IK, WF = [], [], [], []
for q in Q:
    a, _ = held_ellipsoid(q)
    W.append(np.prod(a))
    S.append(a[-1])
    IK.append(a[-1] / a[0])
    WF.append(manip(ur_jv(q)))
W, S, IK, WF = map(np.array, (W, S, IK, WF))

fig, axs = plt.subplots(1, 2, figsize=(12.0, 4.8), gridspec_kw={"width_ratios": [1.15, 1.0]})
ax = axs[0]
ax.set_aspect("equal")
ax.axis("off")
show = [0.30, float(rhos[int(np.argmax(W))]), 0.89]
cols = [C["muted"], C["z"], C["x"]]
for rho, col in zip(show, cols):
    q = ur_radial([rho])[0]
    Pc = ur_chain(q)
    xy = np.c_[Pc @ er, Pc @ ez]
    ax.plot(xy[:, 0], xy[:, 1], color=col, lw=4, solid_capstyle="round", alpha=0.9)
    ax.scatter(xy[1:-1, 0], xy[1:-1, 1], s=14, color="white", edgecolor=col, zorder=5)
    a, D = held_ellipsoid(q)
    # 椭球 {x : xᵀ M x ≤ 1}，M = D diag(1/a²) Dᵀ；在 (e_r, e_z) 平面内的截面
    M = D @ np.diag(1 / a ** 2) @ D.T
    B = np.c_[er, ez]
    M2 = B.T @ M @ B
    lam, V = np.linalg.eigh(M2)
    t = np.linspace(0, 2 * math.pi, 120)
    E = (V @ np.diag(1 / np.sqrt(lam)) @ np.vstack([np.cos(t), np.sin(t)])) * 0.25
    c = np.array([rho, p0[2]])
    ax.plot(c[0] + E[0], c[1] + E[1], color=C["accent"], lw=1.6)
    ax.text(rho, -0.07 - 0.07 * (rho > 0.85), rf"$\rho$ = {rho:.2f} m", ha="center", fontsize=9, color=col)
ax.axhline(p0[2], color=C["muted"], lw=0.6, ls=":")
ax.plot([-0.4, 1.0], [0, 0], color=C["ink"], lw=1.0)
ax.plot([D4, D4], [0, 1.0], color=C["x"], lw=0.8, ls="--")
ax.text(D4 + 0.01, 0.95, T("ρ = d₄（肩部奇异）", "ρ = d₄ (shoulder singularity)"), fontsize=8.5, color=C["x"])
ax.text(-0.4, 1.1, T("(a) 侧视：三个位置的手臂与姿态保持的线速度椭球（截面，比例 0.25）",
                       "(a) side view: the arm and the orientation-held velocity ellipsoid (section, scale 0.25)"), fontsize=10)
ax.set_xlim(-0.42, 1.02)
ax.set_ylim(-0.18, 1.16)

ax = axs[1]
ax.plot(rhos, W / W.max(), color=C["z"], lw=2.0, label=T("可操作度 w（姿态保持）", "manipulability w (orientation held)"))
ax.plot(rhos, S / S.max(), color=C["y"], lw=2.0, label=T("最小半轴 σ_min（姿态保持）", "smallest semi-axis σ_min (held)"))
ax.plot(rhos, IK / IK.max(), color=C["x"], lw=2.0, label=T("1/κ（姿态保持）", "1/κ (held)"))
ax.plot(rhos, WF / WF.max(), color=C["z"], lw=1.4, ls="--", label=T("可操作度 w（J_v，姿态可变）", "manipulability w (J_v, orientation free)"))
for arr, col in ((W, C["z"]), (S, C["y"]), (IK, C["x"]), (WF, C["z"])):
    i = int(np.argmax(arr))
    ax.plot(rhos[i], 1.0, "o", color=col, ms=5)
ax.axvline(math.hypot(p0[0], p0[1]), color=C["muted"], lw=0.8, ls=":")
ax.text(math.hypot(p0[0], p0[1]) + 0.005, 0.04, "θ*", fontsize=10, color=C["muted"])
ax.set_xlabel(T("法兰盘中心到基座轴线的水平距离 ρ / m", "horizontal distance ρ of the flange centre from the base axis / m"))
ax.set_ylabel(T("各指标 / 各自的最大值", "each index / its own maximum"))
ax.set_ylim(0, 1.08)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.legend(fontsize=8.5, frameon=False, loc="lower center")
ax.set_title(T("(b) 三个指标随 ρ 的变化，最优位置各不相同", "(b) the three indices against ρ: each peaks somewhere else"), fontsize=10.5, loc="left")
fig.tight_layout()
figure(fig, "fig16_4_2")
plt.close(fig)
