"""图 15.7.1：半正定矩阵与协方差。(a) 勒夫纳序：直线拟合的两种无偏估计（程序 15.7.1）的 95% 置信椭圆。
P₂ − P_LS 半正定 ⇔ 最小二乘的椭圆整个落在另一个估计的椭圆之内；(b) 两两估计的相关矩阵 C 有负特征值，
把负特征值截成 0、再把对角元缩放回 1 之后的特征值。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.0, 4.2), gridspec_kw={"width_ratios": [1.2, 1]})
t = np.arange(10.0)
Am = np.column_stack([np.ones(10), t])
P_ls = np.linalg.inv(Am.T @ Am)
w1 = np.r_[np.ones(3), np.zeros(7)] / 3
w2 = np.r_[np.zeros(7), np.ones(3)] / 3
slope = (w2 - w1) / (w2 @ t - w1 @ t)
W = np.vstack([w1 - (w1 @ t) * slope, slope])
P2 = W @ W.T
c95 = -2 * np.log(0.05)
th = np.linspace(0, 2 * np.pi, 361)
for P, col, lab in ((P2, RED, T("只用两端各 3 点：P₂", "three points at each end: P₂")),
                    (P_ls, BLUE, T("最小二乘：P_LS", "least squares: P_LS"))):
    L = np.linalg.cholesky(c95 * P)
    E = L @ np.vstack([np.cos(th), np.sin(th)])
    a1.plot(1 + E[0], 0.5 + E[1], color=col, lw=2, label=lab)
rng = np.random.default_rng(1571)
Ys = 1 + 0.5 * t + rng.normal(size=(400, 10))
c_ls = Ys @ np.linalg.pinv(Am).T
a1.plot(c_ls[:, 0], c_ls[:, 1], ".", color=BLUE, ms=2, alpha=0.4, rasterized=True)
a1.plot(1, 0.5, "+", color=INK, ms=10)
a1.set_xlabel(T("截距 c₀", "intercept c₀")); a1.set_ylabel(T("斜率 c₁", "slope c₁"))
a1.legend(frameon=False, fontsize=9, loc="upper right")
for s in ("top", "right"):
    a1.spines[s].set_visible(False)
a1.set_title(T("(a) P₂ ⪰ P_LS：小椭圆在大椭圆之内", "(a) P₂ ⪰ P_LS: the small ellipse lies inside"), fontsize=11)
C = np.array([[1.0, 0.9, 0.1], [0.9, 1, 0.9], [0.1, 0.9, 1]])
lc, Vc = np.linalg.eigh(C)
Cp = Vc @ np.diag(np.maximum(lc, 0)) @ Vc.T
dsc = 1 / np.sqrt(np.diag(Cp))
lf = np.linalg.eigvalsh(Cp * np.outer(dsc, dsc))
x = np.arange(3)
a2.bar(x - 0.18, lc, 0.34, color=[RED if v < 0 else MUTED for v in lc], label=T("两两估计的 C", "pairwise C"))
a2.bar(x + 0.18, lf, 0.34, color=GREEN, label=T("修复后", "repaired"))
for xi, v in zip(x, lc):
    a2.text(xi - 0.18, v + (0.06 if v >= 0 else -0.16), f"{v:.2f}", ha="center", fontsize=8.5, color=INK)
for xi, v in zip(x, lf):
    a2.text(xi + 0.18, v + 0.06, f"{abs(v):.2f}", ha="center", fontsize=8.5, color=INK)
a2.axhline(0, color=INK, lw=0.8)
a2.set_xticks(x); a2.set_xticklabels(["λ₁", "λ₂", "λ₃"])
a2.legend(frameon=False, fontsize=9, loc="upper left")
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
a2.set_title(T("(b) 相关矩阵的特征值", "(b) Eigenvalues of the correlation matrix"), fontsize=11, color=INK)
a2.text(0.6, -0.45, T("负特征值：不是合法的相关矩阵", "a negative eigenvalue: not a valid correlation matrix"), fontsize=8.5, color=ACC)
a2.set_ylim(-0.6, 2.6)
fig.tight_layout()
fig.set_dpi(200)
figure(fig, "fig15_7_1")
