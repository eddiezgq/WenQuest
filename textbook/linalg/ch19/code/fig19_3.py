"""图 19.3.1：(a) AGV 的激光雷达扫到一面与车体 y 轴平行的墙：主成分直线（总体最小二乘，垂直距离）与普通最小二乘
（竖直距离）；(b) 三个尺寸 a、b、a + b 的奇异值：直接 SVD 与先形成 XᵀX 再开方（纵轴为对数）。"""
import math

import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.8), gridspec_kw={"width_ratios": [1, 1.15]})
rng = np.random.default_rng(2026)
dirv = np.array([0.0, 1.0])
tt = np.linspace(-0.6, 0.6, 40)
P = np.array([2.0, 0.5]) + np.outer(tt, dirv) + 0.005 * rng.standard_normal((40, 2))
c = P.mean(axis=0)
v1 = np.linalg.svd(P - c)[2][0]
k, b0 = np.polyfit(P[:, 0], P[:, 1], 1)
yy = np.array([-0.15, 1.15])
a1.axvline(0, color=MUTED, lw=6, alpha=0.3, label=T("真实墙面", "true wall"))
a1.plot((P[:, 0] - 2) * 1000, P[:, 1], "o", color=BLUE, ms=3.5, label=T("测点（误差 5 mm）", "points (5 mm noise)"))
a1.plot((c[0] + (yy - c[1]) * v1[0] / v1[1] - 2) * 1000, yy, color=GREEN, lw=2, label=T("主成分直线", "principal line"))
a1.plot(((yy - b0) / k - 2) * 1000, yy, color=RED, lw=2, ls="--", label=T("普通最小二乘 y = kx + b", "ordinary LS y = kx + b"))
a1.set_xlim(-80, 80)
a1.set_ylim(-0.15, 1.15)
a1.set_xlabel(T("x − 2 m / mm（注意横纵比例不同）", "x − 2 m / mm (unequal scales)"))
a1.set_ylabel("y / m")
a1.legend(frameon=False, fontsize=8.5, loc="upper left")
a1.set_title(T("(a) 沿墙行驶时拟合墙面", "(a) Fitting a wall beside the AGV"), fontsize=11)
for s in ("top", "right"):
    a1.spines[s].set_visible(False)

rng = np.random.default_rng(1810)
a = 42.0 + 0.05 * rng.standard_normal(50)
b = 31.5 + 0.04 * rng.standard_normal(50)
A3c = np.c_[a, b, a + b]
A3c = A3c - A3c.mean(axis=0)
s_svd = np.linalg.svd(A3c, compute_uv=False)
s_eig = np.sqrt(np.abs(np.linalg.eigvalsh(A3c.T @ A3c)[::-1]))
x = np.arange(3)
a2.bar(x - 0.18, s_svd, width=0.34, color=GREEN, label=T("直接对 X 做 SVD", "SVD of X"))
a2.bar(x + 0.18, s_eig, width=0.34, color=RED, label=T("XᵀX 的特征值开方", "√eigenvalues of XᵀX"))
a2.set_yscale("log")
a2.set_ylim(1e-17, 10)
eps = np.finfo(float).eps
a2.axhline(math.sqrt(eps) * s_svd[0], color=RED, lw=0.8, ls=":")
a2.text(2.45, math.sqrt(eps) * s_svd[0] * 2.2, "√ε·σ₁", color=RED, fontsize=9.5, ha="right")
a2.axhline(eps * s_svd[0], color=GREEN, lw=0.8, ls=":")
a2.text(2.45, eps * s_svd[0] * 2.2, "ε·σ₁", color=GREEN, fontsize=9.5, ha="right")
for i in range(3):
    a2.text(i - 0.18, s_svd[i] * 2, f"{s_svd[i]:.1e}", ha="center", fontsize=8, color=GREEN)
    a2.text(i + 0.18, s_eig[i] * 2, f"{s_eig[i]:.1e}", ha="center", fontsize=8, color=RED)
a2.set_xticks(x)
a2.set_xticklabels(["σ₁", "σ₂", T("σ₃（理论上为 0）", "σ₃ (exactly 0 in theory)")])
a2.legend(frameon=False, fontsize=9, loc="upper right")
a2.set_title(T("(b) 小奇异值：SVD 与 XᵀX 的差别", "(b) Small singular values: SVD versus XᵀX"), fontsize=11)
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig19_3_1")
