"""23.4 节的示意图。

图 23.4.1：算例 23.4.2：工具箱 0.40 × 0.24 × 0.10 m、6 kg（示意值）绕三根主轴转动（ω₀ = 8 rad/s，另两轴各 1% 的扰动），
          角速度的三个分量：实线为 MuJoCo 自由刚体，点为本章的 RK4 积分欧拉方程。
图 23.4.2：潘索的几何解释：角动量在物体坐标系中的分量 L_b 在球面 |L| = 常数与能量椭球的交线上运动（工具箱的主惯量，
          2K 取 1）；过中间轴的交线（分界线）用红色。
"""
import math

import numpy as np

from _ch23 import box_inertia, free_spin, mj_load
from bookout import COLORS as C, T, figure, style

plt = style()
a, b, c, M = 0.40, 0.24, 0.10, 6.0
I = np.diag(box_inertia(M, a, b, c))
w0, eps = 8.0, 0.01

# ---------------------------------------------------------------- 图 23.4.1
fig, axs = plt.subplots(1, 3, figsize=(13.2, 3.9), sharey=True)
names = [T("(a) 绕最小惯量轴（最长边）", "(a) about the least axis (longest edge)"),
         T("(b) 绕中间轴（中间边）", "(b) about the intermediate axis"),
         T("(c) 绕最大惯量轴（最短边）", "(c) about the greatest axis (shortest edge)")]
cols = [C["x"], C["y"], C["z"]]
for k in range(3):
    w = np.full(3, eps * w0)
    w[k] = w0
    xml = (f'<mujoco><option timestep="0.001" integrator="RK4" gravity="0 0 0"/><worldbody>'
           f'<body pos="0 0 0.8"><freejoint/><geom type="box" size="{a / 2} {b / 2} {c / 2}" mass="{M}"/></body></worldbody></mujoco>')
    mj, mm, dd = mj_load(xml)
    dd.qvel[3:6] = w
    n = 10000
    Wm = np.zeros((n + 1, 3))
    Wm[0] = w
    for i in range(n):
        mj.mj_step(mm, dd)
        Wm[i + 1] = dd.qvel[3:6]
    t = np.arange(n + 1) * 0.001
    tr, Wr = free_spin(I, w, 10.0)
    ax = axs[k]
    for j in range(3):
        ax.plot(t, Wm[:, j], color=cols[j], lw=1.5, label=[r"$\omega_1$", r"$\omega_2$", r"$\omega_3$"][j])
        ax.plot(tr[::250], Wr[::250, j], "o", color=cols[j], ms=2.6)
    ax.set_title(names[k], fontsize=11, loc="left")
    ax.set_xlabel("t / s")
    ax.set_xlim(0, 10)
    ax.set_ylim(-9.5, 9.5)
    ax.axhline(0, color="#bbbbbb", lw=0.6)
    ax.grid(True, color="#ececec", lw=0.6)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
axs[0].set_ylabel(T("物体坐标系中的角速度 / (rad/s)", "body angular velocity / (rad/s)"))
axs[0].legend(loc="lower right", frameon=False, fontsize=10, ncol=3)
figure(fig, "fig23_4_1")

# ---------------------------------------------------------------- 图 23.4.2
fig = plt.figure(figsize=(7.6, 6.6))
ax = fig.add_axes([0, 0, 1, 1], projection="3d")
ax.set_axis_off()
ax.view_init(elev=26, azim=-32)
E2 = 1.0                                                             # 2K
s = np.sqrt(E2 * I)                                                  # 能量椭球的半轴
u, v = np.meshgrid(np.linspace(0, 2 * math.pi, 60), np.linspace(0, math.pi, 30))
ax.plot_surface(s[0] * np.cos(u) * np.sin(v), s[1] * np.sin(u) * np.sin(v), s[2] * np.cos(v), color="#dbe9f6", alpha=0.25,
                linewidth=0, shade=False)
# 交线：|L|² = λ 2K，λ 在 (I₁, I₃) 内；在椭球上用 RK4 的轨道画（从 L 的初值出发积分一个周期，避免手解交线的分支）
lams = list(np.linspace(I[0] * 1.02, I[1] * 0.985, 5)) + list(np.linspace(I[1] * 1.012, I[2] * 0.985, 5))
for lam in lams:
    # 取 L₂ = 0 的一点：L₁²/I₁ + L₃²/I₃ = 1，L₁² + L₃² = λ
    A = np.array([[1 / I[0], 1 / I[2]], [1.0, 1.0]])
    L13 = np.linalg.solve(A, [E2, lam * E2])
    for sg in (1, -1):
        L0 = np.array([math.sqrt(max(L13[0], 0)), 0.0, sg * math.sqrt(max(L13[1], 0))])
        tt, W = free_spin(I, L0 / I, 30.0, dt=2e-3)
        Lb = W * I
        ax.plot(*Lb.T, color=C["z"], lw=0.9, alpha=0.85)
# 分界线：|L|² = 2K I₂，过 ±L₂ 轴的两条曲线
for sg1 in (1, -1):
    for sg3 in (1, -1):
        tt = np.linspace(-1, 1, 400)
        # 分界线：|L|² = 2K I₂，对给定的 L₂ 由式 (23.4.15) 的两式解出 L₁²、L₃²
        L2 = np.sqrt(E2 * I[1]) * tt
        rest = E2 * I[1] - L2 ** 2
        L1 = sg1 * np.sqrt(np.maximum(rest * I[0] * (I[2] - I[1]) / (I[1] * (I[2] - I[0])), 0))
        L3 = sg3 * np.sqrt(np.maximum(rest * I[2] * (I[1] - I[0]) / (I[1] * (I[2] - I[0])), 0))
        ax.plot(L1, L2, L3, color=C["x"], lw=2.0)
for k, (lab, col) in enumerate(((r"$L_1$", C["x"]), (r"$L_2$", C["y"]), (r"$L_3$", C["z"]))):
    e = np.zeros(3)
    e[k] = s[k] * 1.35
    ax.plot([-e[0], e[0]], [-e[1], e[1]], [-e[2], e[2]], color="#999999", lw=0.8, ls="--")
    ax.text(*(e * 1.08), lab, fontsize=13, color=col)
ax.text2D(0.04, 0.07, T("绕最小惯量轴（L₁）与最大惯量轴（L₃）：小圈，稳定", "about the least (L₁) and greatest (L₃) axes: small loops, stable"),
          transform=ax.transAxes, fontsize=10.5, color=C["z"])
ax.text2D(0.04, 0.025, T("过中间轴（L₂）的分界线（红）：附近出发的运动绕到另一端", "separatrix through the intermediate axis (L₂, red): motions nearby go round to the other end"),
          transform=ax.transAxes, fontsize=10.5, color=C["x"])
r = s.max() * 1.15
ax.set_xlim(-r, r)
ax.set_ylim(-r, r)
ax.set_zlim(-r, r)
ax.set_box_aspect((1, 1, 1), zoom=1.15)
figure(fig, "fig23_4_2")
