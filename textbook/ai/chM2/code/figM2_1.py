"""M2.1 节的示意图。

图 M2.1.1：（a）切线是对曲线的一阶逼近，差是二阶小量；（b）在一个点上，沿各个方向走同样一步，
下降最多的正是负梯度方向——图上画出各方向的下降量（极坐标），最长的那一瓣指向负梯度。
"""
import numpy as np

from _chM2 import quad
from bookout import COLORS, T, figure, style

plt = style()
C = COLORS

fig, (a, b) = plt.subplots(1, 2, figsize=(11.0, 4.0))
xs = np.linspace(0.2, 1.8, 300)
f = lambda x: x ** 3 - 2 * x + 1          # noqa: E731
df = lambda x: 3 * x ** 2 - 2             # noqa: E731
a.plot(xs, f(xs), color=C["z"], lw=1.8, label=T("函数 $f$", "the function $f$"))
x0 = 1.0
a.plot(xs, f(x0) + df(x0) * (xs - x0), color=C["accent"], lw=1.6, ls="--",
       label=T("在 $x_0$ 处的切线", "tangent at $x_0$"))
a.plot([x0], [f(x0)], "o", color=C["ink"], ms=6)
for h in (0.4, 0.2):
    a.annotate("", xy=(x0 + h, f(x0 + h)), xytext=(x0 + h, f(x0) + df(x0) * h),
               arrowprops=dict(arrowstyle="<->", color=C["x"], lw=1.3))
    a.text(x0 + h + 0.03, (f(x0 + h) + f(x0) + df(x0) * h) / 2,
           T(f"$h={h}$ 的差", f"gap at $h={h}$"), fontsize=9, color=C["x"])
a.set_xlabel("$x$")
a.set_ylabel("$f(x)$")
a.set_title(T("(a) 切线逼近：$h$ 减半，差约为四分之一", "(a) Tangent: halve $h$, the gap quarters"), fontsize=10)
a.legend(fontsize=9)
a.grid(alpha=0.25, lw=0.5)

loss, grad, lam = quad([1.0, 100.0])
th = np.array([1.0, 1.0])
g = grad(th)
step = 1e-3
ang = np.linspace(0, 2 * np.pi, 721)
drop = np.array([loss(th) - loss(th + step * np.array([np.cos(t), np.sin(t)])) for t in ang])
b.plot(np.cos(ang) * np.maximum(drop, 0) / drop.max(), np.sin(ang) * np.maximum(drop, 0) / drop.max(),
       color=C["z"], lw=1.8)
gd = -g / np.linalg.norm(g)
b.annotate("", xy=tuple(gd), xytext=(0, 0), arrowprops=dict(arrowstyle="-|>", color=C["x"], lw=2))
b.text(gd[0] * 1.08, gd[1] * 1.08, T("负梯度方向", "$-\\nabla\\mathcal{L}$"), color=C["x"], fontsize=10,
       ha="center", va="center")
b.set_aspect("equal")
b.set_xlim(-1.25, 1.25)
b.set_ylim(-1.25, 1.25)
b.axhline(0, color=C["muted"], lw=0.6)
b.axvline(0, color=C["muted"], lw=0.6)
b.set_title(T("(b) 各方向上的下降量（已归一化）", "(b) Decrease in each direction (normalised)"), fontsize=10)
b.grid(alpha=0.25, lw=0.5)
fig.tight_layout()
figure(fig, "figM2_1_1")
