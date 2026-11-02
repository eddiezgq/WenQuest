"""图 22.1.1：y′ = x − y 用欧拉法的整体误差与步长（对数坐标，斜率 1），与误差界比较；单精度计算时误差先降后升。"""
import math

import numpy as np

from _fig import BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

ex = lambda x: x - 1 + 3 * math.exp(-x)
hs = 2.0 ** -np.arange(1, 12)
glob, loc = [], []
for h in hs:
    x, y = 0.0, 2.0
    for _ in range(round(2 / h)):
        y += h * (x - y); x += h
    glob.append(abs(y - ex(2)))
    loc.append(abs(2 + h * (0 - 2) - ex(h)))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
a1.loglog(hs, glob, "o-", color=BLUE, lw=2, label=T("整体误差（x = 2）", "global error (x = 2)"))
a1.loglog(hs, loc, "s-", color=RED, lw=2, label=T("局部误差（一步）", "local error (one step)"))
a1.loglog(hs, 1.5 * hs * (math.e ** 2 - 1), "--", color=MUTED, lw=1.2, label=T("误差界 3h(e² − 1)/2（L = 1，M = 3）", "bound 3h(e² − 1)/2 (L = 1, M = 3)"))
a1.set_xlabel(T("步长 h", "step h")); a1.set_ylabel(T("误差", "error"))
a1.set_title(T("局部误差 ∝ h²，整体误差 ∝ h", "Local error ∝ h², global error ∝ h"), fontsize=10)
a1.legend(fontsize=9, frameon=False); clean(a1, zero=False)
ns = np.unique(np.round(np.logspace(1, 6.5, 23)).astype(int))
e32, e64 = [], []
for n in ns:
    y = np.float32(1.0); h = np.float32(1.0 / n)
    # 逐步迭代（向量化写法会改变舍入，保持逐步）
    for _ in range(n):
        y = y - h * y
    e32.append(abs(float(y) - math.exp(-1)))
    y64, h64 = 1.0, 1.0 / n
    for _ in range(n):
        y64 = y64 - h64 * y64
    e64.append(abs(y64 - math.exp(-1)))
a2.loglog(ns, e64, "o-", color=BLUE, lw=2, ms=4, label=T("双精度（64 位）", "double (64-bit)"))
a2.loglog(ns, e32, "s-", color=RED, lw=2, ms=4, label=T("单精度（32 位）", "single (32-bit)"))
a2.set_xlabel(T("步数 n（h = 1/n）", "steps n (h = 1/n)")); a2.set_ylabel(T("x = 1 处的误差", "error at x = 1"))
a2.set_title(T("y′ = −y：步长太小时舍入误差占上风", "y′ = −y: round-off wins when h is too small"), fontsize=10)
a2.legend(fontsize=9, frameon=False); clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig22_1_1")
