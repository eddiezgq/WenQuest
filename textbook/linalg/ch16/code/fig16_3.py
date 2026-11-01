"""图 16.3.1：二阶线性系统 u' = Au 的六种相图（程序 16.3.1 的六个矩阵），以及迹–行列式平面上的分类。
图 16.3.2：网球拍定理（程序 16.3.1）。手机大小的薄板绕中间主轴（y）自旋 2 r/s，初始只有 10⁻³ rad/s 的扰动：
ω_y 每隔约 4.6 s 反向两次，薄板一次次翻转；绕最小、最大主轴自旋时扰动只做小幅振荡。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

cases = [([[-3.0, 1], [1, -3]], T("稳定结点", "stable node"), "λ = −4, −2"),
         ([[1.0, 2], [2, 1]], T("鞍点", "saddle"), "λ = −1, 3"),
         ([[-1.0, 4], [-4, -1]], T("稳定焦点", "stable focus"), "λ = −1 ± 4i"),
         ([[0.0, 2], [-2, 0]], T("中心", "center"), "λ = ±2i"),
         ([[2.0, 1], [0, 1]], T("不稳定结点", "unstable node"), "λ = 1, 2"),
         ([[0.5, -3], [3, 0.5]], T("不稳定焦点", "unstable focus"), "λ = 0.5 ± 3i")]
fig = plt.figure(figsize=(12.0, 6.6))
gs = fig.add_gridspec(2, 4, width_ratios=[1, 1, 1, 1.25])
u = np.linspace(-2, 2, 21)
X, Y = np.meshgrid(u, u)
for n, (A, name, ev) in enumerate(cases):
    A = np.array(A)
    ax = fig.add_subplot(gs[n // 3, n % 3])
    ax.set_rasterization_zorder(1.5)
    ax.streamplot(X, Y, A[0, 0] * X + A[0, 1] * Y, A[1, 0] * X + A[1, 1] * Y, color=MUTED, density=0.9, linewidth=0.7, arrowsize=0.8, zorder=1)
    stable = np.all(np.linalg.eigvals(A).real < 0)
    col = BLUE if stable else (INK if abs(np.trace(A)) < 1e-12 else RED)
    for r_, th in zip((1.8, 1.5, 1.2, 1.8, 1.0, 0.6), np.linspace(0, 2 * math.pi, 7)[:-1]):
        center = abs(np.trace(A)) < 1e-12
        p0 = (r_ if center else 1.8) * np.array([math.cos(th), math.sin(th)]) if stable or center else 0.15 * np.array([math.cos(th), math.sin(th)])
        s = solve_ivp(lambda t, y: A @ y, (0, 6), p0, max_step=0.02)
        P = s.y[:, (np.abs(s.y) < 2.05).all(0)]
        ax.plot(P[0], P[1], color=col, lw=1.4)
    if np.all(np.abs(np.linalg.eigvals(A).imag) < 1e-12):
        w, V = np.linalg.eig(A)
        for j in range(2):
            v = V[:, j].real / np.linalg.norm(V[:, j].real)
            ax.plot([-2.2 * v[0], 2.2 * v[0]], [-2.2 * v[1], 2.2 * v[1]], color=ACC, lw=1.2, ls="--")
    ax.set_xlim(-2, 2); ax.set_ylim(-2, 2); ax.set_aspect("equal"); ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(f"{name}\n{ev}", fontsize=10, color=col)
ax = fig.add_subplot(gs[:, 3])
tau = np.linspace(-8, 5, 300)
ax.plot(tau, tau ** 2 / 4, color=INK, lw=1.5)
ax.axhline(0, color=INK, lw=1.2); ax.axvline(0, color=INK, lw=1.2, ymin=4 / 23)
ax.set_xlim(-8, 5); ax.set_ylim(-4, 19)
for (x, y), s, c in (((-7.6, 4.0), T("稳定结点", "stable node"), BLUE), ((-4.2, 14.5), T("稳定焦点", "stable focus"), BLUE),
                     ((2.3, 0.6), T("不稳定结点", "unstable node"), RED), ((0.4, 14.5), T("不稳定焦点", "unstable focus"), RED),
                     ((-3.0, -3.0), T("鞍点（Δ < 0）", "saddle (Δ < 0)"), RED), ((0.2, 17.6), T("中心（τ = 0）", "center (τ = 0)"), INK)):
    ax.text(x, y, s, color=c, fontsize=10)
ax.text(-7.8, 16.5, "Δ = τ²/4", fontsize=9, color=INK)
for A, _, _ in cases:
    A = np.array(A)
    ax.plot(np.trace(A), np.linalg.det(A), "o", color=ACC, ms=6)
ax.set_xlabel(T("迹 τ = λ₁ + λ₂", "trace τ = λ₁ + λ₂")); ax.set_ylabel(T("行列式 Δ = λ₁λ₂", "determinant Δ = λ₁λ₂"))
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title(T("迹–行列式平面：τ < 0 且 Δ > 0 时稳定", "Trace–determinant plane: stable iff τ < 0, Δ > 0"), fontsize=10)
fig.tight_layout()
fig.set_dpi(200)
figure(fig, "fig16_3_1")

# 图 16.3.2
mass, a_, b_, c_ = 0.2, 0.15, 0.075, 0.008
I = np.array([mass * (b_ ** 2 + c_ ** 2) / 12, mass * (a_ ** 2 + c_ ** 2) / 12, mass * (a_ ** 2 + b_ ** 2) / 12])
w0 = 4 * math.pi
eul = lambda t, w: [(I[1] - I[2]) / I[0] * w[1] * w[2], (I[2] - I[0]) / I[1] * w[2] * w[0], (I[0] - I[1]) / I[2] * w[0] * w[1]]
fig, axs = plt.subplots(1, 3, figsize=(12.0, 3.4), sharey=True)
for i, (ax, lab) in enumerate(zip(axs, (T("绕最小主轴 x", "about the smallest axis x"), T("绕中间主轴 y：翻转", "about the middle axis y: flips"), T("绕最大主轴 z", "about the largest axis z")))):
    w_init = np.full(3, 1e-3); w_init[i] = w0
    s = solve_ivp(eul, (0, 10), w_init, rtol=1e-10, atol=1e-12, max_step=0.005)
    for k, col, nm in ((0, RED, "ωx"), (1, GREEN, "ωy"), (2, BLUE, "ωz")):
        ax.plot(s.t, s.y[k], color=col, lw=1.5, label=nm)
    ax.set_title(lab, fontsize=11); ax.set_xlabel(T("t / s", "t / s"))
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
axs[0].set_ylabel(T("角速度 / rad·s⁻¹", "angular velocity / rad·s⁻¹")); axs[0].legend(frameon=False, fontsize=9, loc="center right")
fig.tight_layout()
figure(fig, "fig16_3_2")
