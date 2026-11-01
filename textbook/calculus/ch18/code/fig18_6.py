"""图 18.6.1：左：UR5e 上臂“铝管 + 两端关节模块”的累计质量 m(x)：在 0 和 L 处有跳跃（关节模块），中间线性增加（铝管）；
右：量程 ±50 N 的力传感器读数的分布函数：真实力服从 N(0, 40²)，读数被截断，分布函数在 ±50 N 处有跳跃。"""
import math

import numpy as np
from scipy import stats

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
L, lam, m1, m2 = 0.425, 2.918, 3.55, 3.55
a1.plot([-0.05, 0], [0, 0], color=BLUE, lw=2)
a1.plot([0, L], [m1, m1 + lam * L], color=BLUE, lw=2)
a1.plot([L, L + 0.05], [m1 + lam * L + m2] * 2, color=BLUE, lw=2)
for xx, lo, hi in ((0, 0, m1), (L, m1 + lam * L, m1 + lam * L + m2)):
    a1.plot([xx, xx], [lo, hi], color=BLUE, lw=1, ls=":")
    a1.plot([xx], [hi], "o", color=BLUE)
    a1.plot([xx], [lo], "o", mfc="white", color=BLUE)
a1.text(0.02, 1.5, T("跳跃 3.55 kg\n（肩端模块）", "jump 3.55 kg\n(shoulder module)"), fontsize=9)
a1.text(0.25, 6.2, T("跳跃 3.55 kg\n（肘端模块）", "jump 3.55 kg\n(elbow module)"), fontsize=9)
a1.set_xlabel("x / m")
a1.set_ylabel(T("累计质量 m(x) / kg", "cumulative mass m(x) / kg"))
a1.set_title(T("I = ∫x² dm：连续部分 + 跳跃部分", "I = ∫x² dm: continuous part + jumps"), fontsize=10)
clean(a1)
x = np.linspace(-80, 80, 400)
Fy = np.where(x < -50, 0, np.where(x >= 50, 1, stats.norm.cdf(x / 40)))
a2.plot(x, stats.norm.cdf(x / 40), color=MUTED, ls="--", lw=1, label=T("真实力的分布函数", "CDF of the true force"))
a2.plot(x[x < -50], Fy[x < -50], color=RED, lw=2)
m = (x >= -50) & (x < 50)
a2.plot(x[m], Fy[m], color=RED, lw=2, label=T("读数的分布函数（±50 N 处跳跃）", "CDF of the reading (jumps at ±50 N)"))
a2.plot(x[x >= 50], Fy[x >= 50], color=RED, lw=2)
a2.set_xlabel(T("力 / N", "force / N"))
a2.legend(fontsize=9, frameon=False, loc="upper left")
a2.set_title(T("截断的读数：E[Y²] = ∫y² dF_Y", "Saturated reading: E[Y²] = ∫y² dF_Y"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig18_6_1")
