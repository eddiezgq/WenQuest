"""图 15.4.1：正定的判据。(a) A = [[1, b], [b, 1]]：特征值 1 ± b、第二个顺序主子式（= 两个主元之积）1 − b² 随 b 变化，
在 |b| = 1 处变号，|b| < 1 时三者都为正（正定）；(b) 腱驱动手指的关节刚度 K_q = Rᵀdiag(k)R（程序 15.4.1）：弹性势能 ½ΔqᵀK_qΔq = 1 mJ 的等值线。
三根腱都拉紧、腱 2 松弛：椭圆（正定）；只剩腱 3：一对平行直线（半正定），沿 (1, 4) 方向转动不需要力矩。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.3))
b = np.linspace(-2, 2, 401)
a1.plot(b, 1 + b, color=BLUE, lw=2, label=T("λ₁ = 1 + b", "λ₁ = 1 + b"))
a1.plot(b, 1 - b, color=GREEN, lw=2, label=T("λ₂ = 1 − b", "λ₂ = 1 − b"))
a1.plot(b, 1 - b ** 2, color=RED, lw=2, label=T("det A = 1 − b²", "det A = 1 − b²"))
a1.axhline(0, color=MUTED, lw=0.8)
a1.axvspan(-1, 1, color=ACC, alpha=0.12)
a1.text(0, -2.4, T("正定区间 |b| < 1", "positive definite for |b| < 1"), ha="center", color=ACC, fontsize=10)
a1.set_ylim(-3, 3); a1.set_xlabel("b")
a1.legend(frameon=False, fontsize=9, loc="upper left")
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.set_title(T("(a) [[1, b], [b, 1]]：判据同时变号", "(a) [[1, b], [b, 1]]: the criteria change sign together"), fontsize=11)

Rm = np.array([[10.0, 8], [9, -8], [-12, 3]]) * 1e-3
kt = np.array([5e4, 4e4, 6e4])
u = np.linspace(-0.08, 0.08, 401)
X, Y = np.meshgrid(u, u)
for k, col, lab in ((kt, BLUE, T("三根腱都拉紧", "all three tendons taut")),
                    (kt * [1, 0, 1], GREEN, T("腱 2 松弛", "tendon 2 slack")),
                    (kt * [0, 0, 1], RED, T("只剩腱 3", "tendon 3 only"))):
    K = Rm.T @ np.diag(k) @ Rm
    Z = 0.5 * (K[0, 0] * X ** 2 + 2 * K[0, 1] * X * Y + K[1, 1] * Y ** 2)
    a2.contour(np.degrees(X), np.degrees(Y), Z, levels=[1e-3], colors=[col], linewidths=2)
    a2.plot([], [], color=col, lw=2, label=lab)
t = np.array([1.0, 4.0]) / np.sqrt(17)
a2.annotate("", xy=4.2 * t, xytext=-4.2 * t, arrowprops=dict(arrowstyle="<->", color=INK, lw=1.2))
a2.text(1.3, 2.4, T("(1, 4) 方向", "direction (1, 4)"), fontsize=9, color=INK)
a2.set_aspect("equal"); a2.set_xlim(-4.6, 4.6); a2.set_ylim(-4.6, 4.6)
a2.axhline(0, color=MUTED, lw=0.6); a2.axvline(0, color=MUTED, lw=0.6)
a2.set_xlabel(T("Δq₁ / °", "Δq₁ / °")); a2.set_ylabel(T("Δq₂ / °", "Δq₂ / °"))
a2.legend(frameon=False, fontsize=8.5, loc="lower right")
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
a2.set_title(T("(b) 手指关节的弹性势能 = 1 mJ", "(b) Finger joint elastic energy = 1 mJ"), fontsize=11)
fig.tight_layout()
figure(fig, "fig15_4_1")
