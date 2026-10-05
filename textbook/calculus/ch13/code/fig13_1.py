"""图 13.1.1：左：变上限积分 Φ(x) = ∫₀ˣ e^{−t²} dt 是阴影的面积；中：Φ 的图像，x = 1 处切线的斜率等于 f(1)；
右：被积函数有跳跃（阶跃）时，Φ 连续但在跳跃点有折角。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(13, 4))
f = lambda t: np.exp(-t * t)
t = np.linspace(0, 2.5, 400)
x0 = 1.0
a1.plot(t, f(t), color=INK, lw=2)
tt = t[t <= x0]
a1.fill_between(tt, 0, f(tt), color=BLUE, alpha=0.25)
a1.axvline(x0, color=RED, lw=1, ls="--")
a1.text(0.3, 0.35, "Φ(x)", color=BLUE, fontsize=12)
a1.text(x0 + 0.05, f(x0) + 0.03, "f(x)", color=RED, fontsize=11)
a1.set_xlabel("t")
a1.set_title(T("$f(t) = e^{-t^2}$，阴影面积 = Φ(x)", "$f(t) = e^{-t^2}$; shaded area = Φ(x)"), fontsize=10)
clean(a1, zero=False)
Phi = np.array([0.5 * math.sqrt(math.pi) * math.erf(v) for v in t])
p0 = 0.5 * math.sqrt(math.pi) * math.erf(x0)
a2.plot(t, Phi, color=BLUE, lw=2, label="Φ(x)")
a2.plot(t, f(t), color=INK, lw=1, ls=":", label="f(x)")
xx = np.linspace(x0 - 0.7, x0 + 0.7, 2)
a2.plot(xx, p0 + f(x0) * (xx - x0), color=RED, lw=1.3, label=T("切线，斜率 f(1)", "tangent, slope f(1)"))
a2.plot([x0], [p0], "o", color=RED, ms=5)
a2.axhline(math.sqrt(math.pi) / 2, color=MUTED, lw=0.8, ls="--")
a2.set_xlabel("x")
a2.legend(fontsize=9, frameon=False, loc="center right")
a2.set_title(T("Φ′(x) = f(x)", "Φ′(x) = f(x)"), fontsize=10)
clean(a2, zero=False)
s = np.linspace(0, 2, 401)
g = np.where(s < 1, 1.0, 2.0)
G = np.where(s < 1, s, 1 + 2 * (s - 1))
a3.plot(s[s < 1], g[s < 1], color=INK, lw=2, label="f")
a3.plot(s[s >= 1], g[s >= 1], color=INK, lw=2)
a3.plot(s, G, color=BLUE, lw=2, label="Φ")
a3.plot([1], [1], "o", color=RED, ms=5)
a3.set_xlabel("x")
a3.legend(fontsize=9, frameon=False, loc="upper left")
a3.set_title(T("f 在 x = 1 处跳跃，Φ 在那里有折角", "f jumps at x = 1; Φ has a corner"), fontsize=10)
clean(a3, zero=False)
fig.tight_layout()
figure(fig, "fig13_1_1")
