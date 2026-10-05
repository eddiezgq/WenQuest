"""图 12.1.1：左：y = x² 在 [0, 1] 上的左矩形（蓝）与右矩形（红，只画出比左矩形多的部分），面积夹在两者之间；
右：AGV 速度读数（每 0.1 s 一个）与真实速度，阴影面积就是行驶距离。"""
import numpy as np

from _agv import T, samples, v
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T as TT, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
n = 8
x = np.linspace(0, 1, 300)
for k in range(n):
    xa, xb = k / n, (k + 1) / n
    a1.add_patch(plt.Rectangle((xa, 0), 1 / n, xa ** 2, facecolor=BLUE, alpha=0.25, edgecolor=BLUE, lw=0.8))
    a1.add_patch(plt.Rectangle((xa, xa ** 2), 1 / n, xb ** 2 - xa ** 2, facecolor=RED, alpha=0.25, edgecolor=RED, lw=0.8))
a1.plot(x, x ** 2, color=INK, lw=2)
a1.set_xlim(0, 1.02)
a1.set_ylim(0, 1.05)
a1.set_title(TT("左矩形和 ≤ 面积 ≤ 右矩形和（n = 8）", "Left sum ≤ area ≤ right sum (n = 8)"), fontsize=10)
clean(a1, zero=False)
ts, vs = samples()
tt = np.linspace(0, T + 0.3, 500)
vt = np.array([v(t) for t in tt])
a2.fill_between(tt, 0, vt, color=GREEN, alpha=0.15)
a2.plot(tt, vt, color=INK, lw=1.5, label=TT("真实速度", "true speed"))
a2.plot(ts, vs, ".", color=BLUE, ms=4, label=TT("编码器读数", "encoder readings"))
a2.set_xlabel("t / s")
a2.set_ylabel("v / (m/s)")
a2.set_title(TT("速度曲线下的面积 = 行驶距离", "Area under the speed curve = distance"), fontsize=10)
a2.legend(fontsize=9, frameon=False, loc="lower center")
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig12_1_1")
