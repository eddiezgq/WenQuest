"""图 14.5.1：主轴定理。(a) 5x² + 4xy + 8y² = 36 是斜椭圆，主轴沿 [[5, 2], [2, 8]] 的特征向量 (2, −1)、(1, 2)，半轴 3 和 2；
(b) AGV 定位误差的协方差 Σ = [[4, 2], [2, 3]] cm²：10⁴ 个误差样本与 95% 置信椭圆，长轴沿最不确定的方向（约 38°）。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, axes_box, figure, plt

t = np.linspace(0, 2 * np.pi, 400)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.8))
A = np.array([[5.0, 2], [2, 8]])
w, Q = np.linalg.eigh(A)
E = Q @ np.vstack([np.sqrt(36 / w[0]) * np.cos(t), np.sqrt(36 / w[1]) * np.sin(t)])
axes_box(a1, 3.8)
a1.plot(E[0], E[1], color=ACC, lw=2)
for j, c, r in ((0, RED, 3), (1, GREEN, 2)):
    v = Q[:, j] * np.sign(Q[np.argmax(np.abs(Q[:, j])), j])
    a1.plot([-3.7 * v[0], 3.7 * v[0]], [-3.7 * v[1], 3.7 * v[1]], ls="--", color=c, lw=1)
    a1.annotate("", xy=r * v, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=c, lw=2, mutation_scale=12))
    a1.text(*(r * v + np.array([0.1, 0.15])), T(f"半轴 {r}", f"semi-axis {r}"), color=c, fontsize=10)
a1.set_title(T("(a) 5x² + 4xy + 8y² = 36", "(a) 5x² + 4xy + 8y² = 36"), fontsize=11)
S = np.array([[4.0, 2], [2, 3]])
rng = np.random.default_rng(145)
X = rng.multivariate_normal([0, 0], S, size=10000)
a2.plot(X[:, 0], X[:, 1], ".", color=BLUE, ms=1, alpha=0.3, rasterized=True)
ws, Qs = np.linalg.eigh(S)
c = -2 * np.log(0.05)
E2 = Qs @ np.vstack([np.sqrt(c * ws[0]) * np.cos(t), np.sqrt(c * ws[1]) * np.sin(t)])
a2.plot(E2[0], E2[1], color=ACC, lw=2)
for j, col in ((0, RED), (1, GREEN)):
    v = Qs[:, j] * np.sign(Qs[np.argmax(np.abs(Qs[:, j])), j]) * np.sqrt(c * ws[j])
    a2.annotate("", xy=v, xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=col, lw=2, mutation_scale=12))
a2.set_aspect("equal"); a2.set_xlim(-9, 9); a2.set_ylim(-8, 8)
a2.axhline(0, color=MUTED, lw=0.6); a2.axvline(0, color=MUTED, lw=0.6)
a2.set_xlabel(T("x 误差 / cm", "x error / cm")); a2.set_ylabel(T("y 误差 / cm", "y error / cm"))
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
a2.set_title(T("(b) AGV 定位误差的 95% 置信椭圆", "(b) 95% confidence ellipse of AGV position error"), fontsize=11)
fig.tight_layout()
fig.set_dpi(200)
figure(fig, "fig14_5_1")
