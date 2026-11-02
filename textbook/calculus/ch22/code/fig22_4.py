"""图 22.4.1：左：y′ = −1000(y − cos t)，h = 2.1 ms 时显式欧拉振荡发散、隐式欧拉平稳；右：显式欧拉、隐式欧拉、RK4 的稳定区域（z = hλ 平面）。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

lam, h = 1000.0, 2.1e-3
n = 14
tf, yf, yb = [0.0], [0.0], [0.0]
for j in range(n):
    t = (j + 1) * h
    yf.append(yf[-1] + h * (-lam * (yf[-1] - math.cos(t - h))))
    yb.append((yb[-1] + h * lam * math.cos(t)) / (1 + h * lam))
    tf.append(t)
tf = np.array(tf)
tt = np.linspace(0, tf[-1], 400)
ex = (lam ** 2 * np.cos(tt) + lam * np.sin(tt)) / (lam ** 2 + 1) - lam ** 2 / (lam ** 2 + 1) * np.exp(-lam * tt)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
a1.plot(tt * 1000, ex, color=INK, lw=2, label=T("准确解", "exact"))
a1.plot(tf * 1000, yf, "o-", color=RED, ms=3, lw=1, label=T("显式欧拉 h = 2.1 ms", "explicit Euler h = 2.1 ms"))
a1.plot(tf * 1000, yb, "s-", color=BLUE, ms=3, lw=1, label=T("隐式欧拉 h = 2.1 ms", "implicit Euler h = 2.1 ms"))
a1.set_ylim(-1.5, 3)
a1.set_xlabel(T("时间 t / ms", "time t / ms")); a1.set_ylabel("y")
a1.set_title(T("y′ = −1000(y − cos t)：hλ = 2.1 > 2", "y′ = −1000(y − cos t): hλ = 2.1 > 2"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="lower right"); clean(a1)
x, y = np.meshgrid(np.linspace(-4.5, 3, 600), np.linspace(-3.5, 3.5, 600))
z = x + 1j * y
a2.contourf(x, y, (np.abs(1 / (1 - z)) <= 1).astype(float), levels=[0.5, 1.5], colors=[BLUE], alpha=0.15)
a2.contour(x, y, np.abs(1 - z), levels=[1], colors=[BLUE], linewidths=1.8)
a2.contour(x, y, np.abs(1 + z), levels=[1], colors=[RED], linewidths=1.8)
a2.contour(x, y, np.abs(1 + z + z ** 2 / 2 + z ** 3 / 6 + z ** 4 / 24), levels=[1], colors=[GREEN], linewidths=1.8)
a2.axhline(0, color=MUTED, lw=0.6); a2.axvline(0, color=MUTED, lw=0.6)
a2.text(-1.75, 0.15, T("显式欧拉", "explicit Euler"), color=RED, fontsize=9)
a2.text(-3.2, 2.5, "RK4", color=GREEN, fontsize=10)
a2.text(1.1, 1.3, T("隐式欧拉：\n圆外都稳定", "implicit Euler:\nstable outside"), color=BLUE, fontsize=9)
a2.plot([-2.785], [0], "o", color=GREEN, ms=4)
a2.set_xlabel("Re hλ"); a2.set_ylabel("Im hλ"); a2.set_aspect("equal")
a2.set_title(T("稳定区域：hλ 落在里面，误差不放大", "Stability regions: hλ inside ⇒ errors not amplified"), fontsize=10)
for s in ("top", "right"):
    a2.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig22_4_1")
