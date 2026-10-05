"""图 12.2.1：左：∫₀¹ x³ dx 的中点和（n = 6）；右：左、右、中点和的误差随 n 的变化（双对数坐标），斜率 −1 与 −2。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
f = lambda x: x ** 3
n = 6
x = np.linspace(0, 1, 300)
for k in range(n):
    m = (k + 0.5) / n
    a1.add_patch(plt.Rectangle((k / n, 0), 1 / n, f(m), facecolor=GREEN, alpha=0.3, edgecolor=GREEN, lw=0.8))
    a1.plot([m], [f(m)], "o", color=GREEN, ms=4)
a1.plot(x, f(x), color=INK, lw=2)
a1.set_title(T("中点和：每个小矩形的高取中点的函数值", "Midpoint sum: heights at the midpoints"), fontsize=10)
clean(a1, zero=False)
ns = np.array([2 ** k for k in range(2, 12)])
for rule, c, lab in (("L", BLUE, T("左", "left")), ("R", RED, T("右", "right")), ("M", GREEN, T("中点", "midpoint"))):
    err = []
    for N in ns:
        h = 1 / N
        k = np.arange(N)
        pts = {"L": k * h, "R": (k + 1) * h, "M": (k + 0.5) * h}[rule]
        err.append(abs(np.sum(f(pts)) * h - 0.25))
    a2.loglog(ns, err, "o-", color=c, ms=4, lw=1.2, label=lab)
a2.set_xlabel("n")
a2.set_ylabel(T("误差", "error"))
a2.set_title(T("左、右和的误差 ∝ 1/n，中点和 ∝ 1/n²", "Left/right error ∝ 1/n, midpoint ∝ 1/n²"), fontsize=10)
a2.legend(fontsize=9, frameon=False)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig12_2_1")
