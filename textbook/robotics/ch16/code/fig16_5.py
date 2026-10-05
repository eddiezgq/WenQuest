"""16.5 节的示意图。

图 16.5.1：运动与静力的对偶（平面 2R 臂，0.425 m、0.392 m，θ₁ = 30°）。末端的速度椭圆（单位关节速度）与力椭圆
           （单位关节力矩）主轴相同、半轴互为倒数：(a) θ₂ = 90°；(b) θ₂ = 15°，手臂接近伸直，速度椭圆在径向被压扁，
           力椭圆在径向被拉长。
图 16.5.2：(a) 算例 16.5.1：UR5e 在 θ* 处向下压 50 N，各关节力矩与上限之比；(b) 算例 16.5.2：Panda 用关节力矩
           传感器估计手上的外力，七维力矩中“手上的力解释不了”的那一维的残差：手上受力时只有噪声，肘部被推时远超噪声。
"""
import math

import numpy as np

from _fig16 import C, arm_pts, base_mark, draw_arm, plane
from _jac import (PANDA_READY, TAU_MAX, TH_STAR, body_screws, exp6, jac_2r, jacobian_body, jacobian_space, panda_screws,
                  ur_jv)
from bookout import T, figure, style

plt = style()
LL = (0.425, 0.392)

# ---------------------------------------------------------------- 图 16.5.1
fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.8))
for ax, t2d, tag in ((axs[0], 90, "(a)"), (axs[1], 30, "(b)")):
    plane(ax, (-0.12, 1.12), (-0.1, 0.92))
    th = np.radians([30, t2d])
    pts = arm_pts(th, LL)
    base_mark(ax)
    draw_arm(ax, pts, C["z"], lw=6)
    J = jac_2r(th, LL)
    U, s, _ = np.linalg.svd(J)
    t = np.linspace(0, 2 * math.pi, 200)
    circ = np.vstack([np.cos(t), np.sin(t)])
    kv, kf = 0.35, 0.03                                              # 作图比例：速度 1 m/s → 0.35 m；力 1 N → 0.03 m
    Ev = U @ np.diag(s) @ circ * kv
    Ef = U @ np.diag(1 / s) @ circ * kf
    p = pts[-1]
    ax.plot(p[0] + Ev[0], p[1] + Ev[1], color=C["accent"], lw=2.0, label=T("速度椭圆：", "velocity ellipse: ") + r"$\{J\dot\theta : \|\dot\theta\| \leq 1\}$")
    ax.plot(p[0] + Ef[0], p[1] + Ef[1], color=C["x"], lw=2.0, ls="--", label=T("力椭圆：", "force ellipse: ") + r"$\{F : \|J^{T}F\| \leq 1\}$")
    for k in range(2):
        d = U[:, k]
        ax.plot(*np.array([p - 0.45 * d, p + 0.45 * d]).T, color=C["muted"], lw=0.6, ls=":")
    ax.text(-0.1, 0.88, f"{tag} θ₂ = {t2d}°", fontsize=11)
    ax.text(-0.1, 0.81, T("速度半轴 σ₁, σ₂ = ", "velocity semi-axes σ₁, σ₂ = ") + f"{s[0]:.3f}, {s[1]:.3f} m", fontsize=9, color=C["accent"])
    ax.text(-0.1, 0.75, T("力半轴 1/σ₂, 1/σ₁ = ", "force semi-axes 1/σ₂, 1/σ₁ = ") + f"{1 / s[1]:.2f}, {1 / s[0]:.2f} N/(N·m)", fontsize=9, color=C["x"])
    if tag == "(a)":
        ax.legend(fontsize=8.8, frameon=False, loc="lower right")
ax.text(0.30, -0.06, T("比例：1 m/s → 0.35 m；1 N → 0.03 m", "scale: 1 m/s → 0.35 m; 1 N → 0.03 m"), fontsize=8.5, color=C["muted"])
fig.tight_layout()
figure(fig, "fig16_5_1")
plt.close(fig)

# ---------------------------------------------------------------- 图 16.5.2
fig, axs = plt.subplots(1, 2, figsize=(11.6, 4.2))
ax = axs[0]
Jv = ur_jv(TH_STAR)
tau = Jv.T @ np.array([0, 0, -50.0])
r = np.abs(tau) / TAU_MAX
bars = ax.bar(range(1, 7), r * 100, color=[C["z"]] * 3 + [C["accent"]] * 3)
for i, (x, tv) in enumerate(zip(r, tau)):
    ax.text(i + 1, x * 100 + 0.6, f"{tv:.1f}", ha="center", fontsize=9)
ax.set_xticks(range(1, 7))
ax.set_xlabel(T("关节", "joint"))
ax.set_ylabel(T("|τᵢ| / 力矩上限 (%)", "|τᵢ| / torque limit (%)"))
ax.set_ylim(0, 27)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.text(0.55, 25.3, T("(a) UR5e 在 θ* 处向下压 50 N（柱顶数字为 τᵢ / N·m）", "(a) UR5e at θ* pressing down 50 N (τᵢ / N·m on top)"), fontsize=10)
ax.text(4.55, 19, T("上限：关节 1～3 为 150 N·m\n          关节 4～6 为 28 N·m", "limits: joints 1–3 150 N·m\n            joints 4–6 28 N·m"), fontsize=8.5, color=C["muted"])

ax = axs[1]
S, M, W, Q, pa = panda_screws()
B = body_screws(S, M)
q = PANDA_READY
Jp = jacobian_body(B, q)
n = np.linalg.svd(Jp)[2][-1]
rng = np.random.default_rng(1652)
sig = 0.05
F_hand = np.array([0, 0, 0, 10.0, 0, -5.0])
E4 = np.eye(4)
for Si, ti in zip(S[:4], q[:4]):
    E4 = E4 @ exp6(Si, ti)
c = E4[:3, :3] @ Q[3] + E4[:3, 3]
fc = np.array([0, 15.0, 0])
Jsp = jacobian_space(S, q)
tau_c = np.r_[Jsp[:, :4].T @ np.r_[np.cross(c, fc), fc], np.zeros(3)]
n = n * np.sign(n @ tau_c)                                          # n 的正负号任取，取碰撞时残差为正
tt = np.arange(0, 2.0, 0.01)
res = []
for k, x in enumerate(tt):
    tau_k = Jp.T @ F_hand + (tau_c if 1.0 <= x < 1.4 else 0) + rng.normal(0, sig, 7)
    res.append(n @ tau_k)
ax.plot(tt, res, color=C["z"], lw=1.2)
ax.axhspan(-3 * sig, 3 * sig, color="#dde7f1", lw=0)
ax.axvspan(1.0, 1.4, color="#f6dede", lw=0)
ax.text(0.03, 3 * sig + 0.08, T("±3σ（只有噪声）", "±3σ (noise only)"), fontsize=8.5, color=C["muted"])
ax.text(1.02, 2.62, T("肘部被侧推 15 N", "elbow pushed sideways, 15 N"), fontsize=8.5, color=C["x"])
ax.text(0.03, 2.62, T("手上始终受 (10, 0, −5) N", "hand loaded with (10, 0, −5) N throughout"), fontsize=8.5, color=C["ink"])
ax.set_xlabel(T("时间 / s", "time / s"))
ax.set_ylabel(T("残差 nᵀτ / (N·m)", "residual nᵀτ / (N·m)"))
ax.set_ylim(-0.6, 2.95)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.set_title(T("(b) Panda：手上的外力解释不了的那一维", "(b) Panda: the one dimension a hand wrench cannot explain"), fontsize=10.5, loc="left")
fig.tight_layout()
figure(fig, "fig16_5_2")
plt.close(fig)
