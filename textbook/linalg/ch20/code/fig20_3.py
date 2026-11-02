"""图 20.3.1：铜合金配料对成分测量误差的敏感性。每个质量分数有 0.3 个百分点的随机误差，各算 2000 次配料量：
(a) 第 3 章原来的三种料（κ₂ ≈ 12）；(b) 料 C 换成几乎是 A、B 对半混合的 C′（κ₂ ≈ 150）。黑点为真实配料量。"""
import numpy as np

from _fig import BLUE, INK, MUTED, RED, T, figure, plt

M0 = np.array([[0.80, 0.60, 0.70], [0.15, 0.35, 0.10], [0.05, 0.05, 0.20]])
M1 = M0.copy()
M1[:, 2] = [0.70, 0.24, 0.06]
x_true = np.array([40.0, 30.0, 30.0])
rng = np.random.default_rng(2003)
fig, axs = plt.subplots(1, 2, figsize=(11.0, 4.6), sharex=True, sharey=True)
for ax, M, col, title in ((axs[0], M0, BLUE, T("(a) 原来的料 A、B、C", "(a) Original materials A, B, C")),
                          (axs[1], M1, RED, T("(b) 料 C 换成 C′", "(b) C replaced by C′"))):
    b = M @ x_true
    X = np.array([np.linalg.solve(M + 0.003 * rng.standard_normal((3, 3)), b) for _ in range(2000)])
    ax.scatter(X[:, 0], X[:, 2], s=4, color=col, alpha=0.35, lw=0, rasterized=True)
    ax.plot(x_true[0], x_true[2], "ko", ms=6)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.axvline(0, color=MUTED, lw=0.8)
    ax.set_title(title + T(f"，κ₂ = {np.linalg.cond(M):.0f}", f", κ₂ = {np.linalg.cond(M):.0f}"), fontsize=11)
    ax.set_xlabel(T("料 A 的用量 x₁ / kg", "amount of A, x₁ / kg"))
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
axs[0].set_ylabel(T("料 C（C′）的用量 x₃ / kg", "amount of C (C′), x₃ / kg"))
axs[0].set_xlim(-40, 120)
axs[0].set_ylim(-60, 150)
fig.tight_layout()
figure(fig, "fig20_3_1")
