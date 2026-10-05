"""图 13.2.1：牛顿–莱布尼茨公式。左：v(t) = 3(t − 1)(t − 3) 在 [0, 4] 上的带符号面积；
右：位置 x(t) = t³ − 6t² + 9t，各段的面积等于 x 在两端的差。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
t = np.linspace(0, 4, 400)
v = 3 * (t - 1) * (t - 3)
x = t ** 3 - 6 * t ** 2 + 9 * t
a1.plot(t, v, color=INK, lw=2)
a1.fill_between(t, 0, v, where=v >= 0, color=BLUE, alpha=0.3)
a1.fill_between(t, 0, v, where=v < 0, color=RED, alpha=0.3)
for xc, yc, s in ((0.45, 1.2, "+4"), (2.0, -1.4, "−4"), (3.6, 2.0, "+4")):
    a1.text(xc, yc, s, fontsize=12, ha="center")
a1.set_xlabel("t / s")
a1.set_ylabel("v / (m/s)")
a1.set_title(T("速度曲线下的带符号面积", "Signed area under the speed curve"), fontsize=10)
clean(a1)
a2.plot(t, x, color=BLUE, lw=2)
for t0, t1, c in ((0, 1, BLUE), (1, 3, RED), (3, 4, BLUE)):
    x0, x1 = t0 ** 3 - 6 * t0 ** 2 + 9 * t0, t1 ** 3 - 6 * t1 ** 2 + 9 * t1
    a2.annotate("", xy=(t1, x1), xytext=(t1, x0), arrowprops=dict(arrowstyle="->", color=c, lw=1.5))
    a2.plot([t0, t1], [x0, x0], color=c, lw=0.8, ls="--")
a2.set_xlabel("t / s")
a2.set_ylabel("x / m")
a2.set_title(T("面积 = x(b) − x(a)：+4、−4、+4", "Area = x(b) − x(a): +4, −4, +4"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig13_2_1")
