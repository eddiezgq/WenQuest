"""图 11.6.1：函数的正交基。(a) 勒让德多项式 P₀～P₄（[−1, 1] 上两两正交）；(b) 方波的傅里叶部分和（1、5、25 项），间断点附近的过冲不随项数减小（吉布斯现象）；
(c) 编码器偏心误差的测量值与 4 阶傅里叶拟合。"""
import numpy as np
from numpy.polynomial import legendre as Lg

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, axs = plt.subplots(1, 3, figsize=(13.0, 3.8))
x = np.linspace(-1, 1, 400)
cols = [INK, RED, GREEN, BLUE, ACC]
for k in range(5):
    axs[0].plot(x, Lg.legval(x, np.eye(5)[k]), color=cols[k], lw=2, label=f"P{'₀₁₂₃₄'[k]}")
axs[0].legend(frameon=False, fontsize=9, ncol=5, loc="lower center")
axs[0].set_ylim(-1.55, 1.1)
axs[0].set_title(T("(a) 勒让德多项式", "(a) Legendre polynomials"), fontsize=11)
t = np.linspace(-np.pi, np.pi, 4000)
axs[1].plot(t, np.sign(t), color=MUTED, lw=1.5)
for N, col in ((1, RED), (5, GREEN), (25, BLUE)):
    S = sum(4 / (k * np.pi) * np.sin(k * t) for k in range(1, N + 1, 2))
    axs[1].plot(t, S, color=col, lw=1.4, label=T(f"{N} 次谐波以内", f"up to harmonic {N}"))
axs[1].legend(frameon=False, fontsize=9, loc="upper left")
axs[1].set_title(T("(b) 方波的傅里叶部分和", "(b) partial sums for a square wave"), fontsize=11)
rng = np.random.default_rng(116)
th = np.arange(360) * np.pi / 180
e = 40 * np.sin(th) + 15 * np.cos(th) - 12 * np.sin(2 * th) + 6 * np.cos(3 * th) + rng.normal(scale=2.0, size=th.size)
A = np.column_stack([np.ones_like(th)] + [f(k * th) for k in range(1, 5) for f in (np.cos, np.sin)])
c = np.linalg.lstsq(A, e, rcond=None)[0]
axs[2].plot(np.degrees(th), e, ".", color=MUTED, ms=3, label=T("测量", "measured"))
axs[2].plot(np.degrees(th), A @ c, color=RED, lw=2, label=T("4 阶傅里叶拟合", "Fourier fit, 4 harmonics"))
axs[2].plot(np.degrees(th), e - A @ c, color=BLUE, lw=0.8, label=T("补偿后的残差", "residual after compensation"))
axs[2].set_xlabel(T("转角 / °", "angle / °")); axs[2].set_ylabel(T("误差 / 角秒", "error / arcsec"))
axs[2].legend(frameon=False, fontsize=9, loc="lower left")
axs[2].set_title(T("(c) 编码器偏心误差的补偿", "(c) compensating encoder eccentricity"), fontsize=11)
for a in axs:
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig11_6_1")
