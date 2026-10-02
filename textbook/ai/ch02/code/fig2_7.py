"""2.7 节的示意图。

图 2.7.1：15 个带噪声的点（y = sin 2πx + 噪声）上 1、3、9、14 次多项式的拟合：欠拟合、合适、过拟合。
图 2.7.2：（a）训练误差与测试误差随多项式次数的变化；（b）14 次多项式加权重衰减后测试误差随 λ 的变化。
"""
import numpy as np
from numpy.polynomial import chebyshev as Ch

from _ch2 import poly_data
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS
xt, yt, xs, ys = poly_data()
n = len(xt)
D = lambda x, d: Ch.chebvander(2 * x - 1, d)


def fit(deg, lam=0.0):
    X = D(xt, deg)
    return np.linalg.solve(X.T @ X + n * lam * np.eye(deg + 1), X.T @ yt)


xf = np.linspace(0, 1, 800)
fig, axs = plt.subplots(1, 4, figsize=(11.4, 3.0), sharey=True)
for ax, deg in zip(axs, (1, 3, 9, 14)):
    w = fit(deg)
    ax.plot(xf, np.sin(2 * np.pi * xf), color=C["y"], lw=1.2, ls="--")
    ax.plot(xf, D(xf, deg) @ w, color=C["x"], lw=1.6)
    ax.plot(xt, yt, "o", color=C["z"], ms=4.5)
    ax.set_ylim(-1.8, 1.8)
    ax.set_title(T(f"{deg} 次", f"degree {deg}"), fontsize=11)
    ax.set_xlabel("$x$")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
axs[0].set_ylabel("$y$")
axs[0].text(0.02, -1.65, T("虚线：真实函数 sin 2πx", "dashed: true sin 2πx"), fontsize=8.5, color=C["y"])
fig.tight_layout()
figure(fig, "fig2_7_1")
plt.close(fig)

fig, axs = plt.subplots(1, 2, figsize=(10.4, 3.8))
ax = axs[0]
degs = np.arange(0, 15)
tr, te = [], []
for d in degs:
    w = fit(d)
    tr.append(np.mean((D(xt, d) @ w - yt) ** 2))
    te.append(np.mean((D(xs, d) @ w - ys) ** 2))
ax.semilogy(degs, np.maximum(tr, 1e-12), "o-", color=C["z"], ms=4, label=T("训练误差", "training error"))
ax.semilogy(degs, te, "s-", color=C["x"], ms=4, label=T("测试误差", "test error"))
ax.axhline(0.15 ** 2, color=C["muted"], ls=":", lw=1)
ax.text(4.5, 0.15 ** 2 * 0.12, T("噪声方差 0.0225", "noise variance 0.0225"), fontsize=8.5, color=C["muted"])
ax.set_xlabel(T("多项式次数", "polynomial degree"))
ax.set_ylabel(T("均方误差", "mean squared error"))
ax.legend(fontsize=9, frameon=False)
ax.set_title(T("（a）模型越复杂，训练误差越小", "(a) More complex, lower training error"), fontsize=11)
ax = axs[1]
lams = np.geomspace(1e-7, 10, 60)
te_l = [np.mean((D(xs, 14) @ fit(14, l) - ys) ** 2) for l in lams]
tr_l = [np.mean((D(xt, 14) @ fit(14, l) - yt) ** 2) for l in lams]
ax.loglog(lams, tr_l, color=C["z"], lw=1.6, label=T("训练误差", "training error"))
ax.loglog(lams, te_l, color=C["x"], lw=1.6, label=T("测试误差", "test error"))
ax.set_xlabel(T("权重衰减系数 $\\lambda$", "weight decay $\\lambda$"))
ax.set_ylabel(T("均方误差", "mean squared error"))
ax.legend(fontsize=9, frameon=False)
ax.set_title(T("（b）14 次多项式加权重衰减", "(b) Degree 14 with weight decay"), fontsize=11)
for a_ in axs:
    for s in ("top", "right"):
        a_.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig2_7_2")
plt.close(fig)
