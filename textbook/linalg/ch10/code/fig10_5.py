"""图 10.5.1：三种拟合。(a) 夹爪手指的力–变形数据与拟合直线；(b) 温度漂移的多项式拟合：训练误差随次数单调下降，检验误差先降后升；
(c) 关节摩擦辨识：去掉惯性项后的力矩 τ − Îα 与角速度 ω，以及拟合的 b̂ω + ĉ sign(ω)。"""
import numpy as np

from _data10 import T_test, T_train, alpha, delta, force, omega, tau, y_test, y_train
from _fig import BLUE, GREEN, INK, MUTED, RED, T, figure, plt

fig, axs = plt.subplots(1, 3, figsize=(13.0, 3.9))
A = np.column_stack([np.ones_like(delta), delta])
F0, k = np.linalg.solve(A.T @ A, A.T @ force)
ax = axs[0]
ax.plot(delta, force, "o", color=BLUE, ms=6)
dd = np.linspace(0, 5, 2)
ax.plot(dd, F0 + k * dd, color=RED, lw=2)
for x, y in zip(delta, force):
    ax.plot([x, x], [y, F0 + k * x], color=MUTED, lw=1)
ax.set_xlabel(T("变形 δ / mm", "deflection δ / mm")); ax.set_ylabel(T("力 F / N", "force F / N"))
ax.set_title(T(f"(a) 直线拟合：k̂ = {k:.2f} N/mm", f"(a) line fit: k̂ = {k:.2f} N/mm"), fontsize=11)
xs = lambda Tm: (Tm - 40.0) / 20.0
tr, te = [], []
degs = range(1, 12)
for d in degs:
    V = np.vander(xs(T_train), d + 1, increasing=True)
    c = np.linalg.lstsq(V, y_train, rcond=None)[0]
    tr.append(np.sqrt(np.mean((V @ c - y_train) ** 2)) * 1000)
    te.append(np.sqrt(np.mean((np.vander(xs(T_test), d + 1, increasing=True) @ c - y_test) ** 2)) * 1000)
ax = axs[1]
ax.plot(list(degs), tr, "o-", color=BLUE, label=T("训练误差", "training error"))
ax.plot(list(degs), te, "s-", color=RED, label=T("检验误差", "test error"))
ax.set_xlabel(T("多项式次数", "degree")); ax.set_ylabel(T("均方根误差 / mN", "RMS error / mN"))
ax.legend(frameon=False, fontsize=10)
ax.set_ylim(0, 115)
ax.set_title(T("(b) 训练误差一直降，检验误差先降后升", "(b) training error falls, test error turns up"), fontsize=11)
X = np.column_stack([alpha, omega, np.sign(omega)])
I, b, c = np.linalg.solve(X.T @ X, X.T @ tau)
ax = axs[2]
ax.plot(omega, tau - I * alpha, ".", color=BLUE, ms=3, alpha=0.6)
w = np.linspace(omega.min(), omega.max(), 400)
ax.plot(w, b * w + c * np.sign(w), color=RED, lw=2)
ax.axhline(0, color=MUTED, lw=0.6); ax.axvline(0, color=MUTED, lw=0.6)
ax.set_xlabel(T("角速度 ω / (rad/s)", "angular velocity ω / (rad/s)")); ax.set_ylabel(T("τ − Îα / (N·m)", "τ − Îα / (N·m)"))
ax.set_title(T("(c) 摩擦：b̂ω + ĉ sign(ω)", "(c) friction: b̂ω + ĉ sign(ω)"), fontsize=11)
for a in axs:
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig10_5_1")
