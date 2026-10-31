"""图 15.8.1：可操作度椭圆与末端的等效质量（程序 15.8.1，l = 0.4/0.3 m，m = 2/1 kg，q₁ = 30°）。
(a) q₂ = 90°、(b) q₂ = 10°（接近伸直的奇异姿态）：绿色为速度椭圆 {Jq̇ : ‖q̇‖ ≤ 1}（单位 m/s，半轴 = J 的奇异值），
红色为等效质量椭圆 xᵀΛ⁻¹x = 1（沿单位方向 u 的半径的平方 = 沿 u 推末端时感到的质量；两图用同一比例）；
(c) 可操作度 w = l₁l₂|sin q₂| 与质量矩阵 M(q₂) 的两个特征值随 q₂ 的变化：特征值始终为正。"""
import numpy as np

import _arm2m as A2
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig = plt.figure(figsize=(12.0, 4.2))
gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 1.15])
d = np.pi / 180
q1 = 30 * d
th = np.linspace(0, 2 * np.pi, 241)
for i, q2d in enumerate((90, 10)):
    ax = fig.add_subplot(gs[0, i])
    q2 = q2d * d
    P = A2.points(q1, q2)
    ax.plot(*P[:2].T, color=BLUE, lw=6, solid_capstyle="round")
    ax.plot(*P[1:].T, color=BLUE, lw=4, solid_capstyle="round", alpha=0.7)
    ax.plot(*P[:2].T, "o", color=INK, ms=5)
    J = A2.jac(q1, q2)
    V = J @ np.vstack([np.cos(th), np.sin(th)]) * 0.25
    ax.plot(P[2, 0] + V[0], P[2, 1] + V[1], color=GREEN, lw=2)
    Lam = np.linalg.inv(J @ np.linalg.inv(A2.mass(q2)) @ J.T)
    # 等效质量椭圆 xᵀΛ⁻¹x = 1：沿单位方向 u 的半径² = 1/(uᵀΛ⁻¹u) = 沿 u 推末端时的等效质量（按 0.06 m/√kg 缩放）
    E = np.linalg.cholesky(Lam) @ np.vstack([np.cos(th), np.sin(th)]) * 0.06
    ax.plot(P[2, 0] + E[0], P[2, 1] + E[1], color=RED, lw=2)
    ax.set_aspect("equal")
    ax.set_xlim(-0.1, 0.75); ax.set_ylim(-0.15, 0.7)
    ax.axhline(0, color=MUTED, lw=0.5); ax.axvline(0, color=MUTED, lw=0.5)
    ax.set_title(T(f"({'ab'[i]}) q₂ = {q2d}°", f"({'ab'[i]}) q₂ = {q2d}°"), fontsize=11)
    ax.set_xlabel(T("x / m", "x / m"))
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if i == 0:
        ax.plot([], [], color=GREEN, lw=2, label=T("速度椭圆（×0.25）", "velocity ellipse (×0.25)"))
        ax.plot([], [], color=RED, lw=2, label=T("等效质量椭圆（×0.06）", "effective-mass ellipse (×0.06)"))
        ax.legend(frameon=False, fontsize=8.5, loc="upper left")
        ax.set_ylabel(T("y / m", "y / m"))
ax = fig.add_subplot(gs[0, 2])
q = np.linspace(-180, 180, 721)
w = A2.L1 * A2.L2 * np.abs(np.sin(q * d))
lm = np.array([np.linalg.eigvalsh(A2.mass(v * d)) for v in q])
ax.plot(q, w, color=GREEN, lw=2, label=T("可操作度 w / m²", "manipulability w / m²"))
ax.plot(q, lm[:, 1], color=BLUE, lw=2, label=T("M 的大特征值 / kg·m²", "larger eigenvalue of M / kg·m²"))
ax.plot(q, lm[:, 0], color=RED, lw=2, label=T("M 的小特征值 / kg·m²", "smaller eigenvalue of M / kg·m²"))
ax.axvline(120, color=ACC, lw=1, ls="--"); ax.axvline(-120, color=ACC, lw=1, ls="--")
ax.text(122, 0.40, T("m₁₂ = 0", "m₁₂ = 0"), color=ACC, fontsize=9)
ax.axhline(0, color=MUTED, lw=0.6)
ax.set_xlim(-180, 180); ax.set_xticks([-180, -120, -60, 0, 60, 120, 180])
ax.set_xlabel(T("q₂ / °", "q₂ / °"))
ax.legend(frameon=False, fontsize=8.5, loc="upper left", bbox_to_anchor=(0.0, 0.93))
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_ylim(-0.02, 0.5)
ax.set_title(T("(c) 可操作度与质量矩阵的特征值", "(c) Manipulability and eigenvalues of M"), fontsize=11)
fig.tight_layout()
figure(fig, "fig15_8_1")
