"""图 23.6.1：求 π 的几种办法：莱布尼茨级数直接求和、反复平均、艾特肯加速、梅钦公式，误差与所用项数（对数坐标）。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt


def leib(n):
    k = np.arange(n)
    return 4 * np.cumsum((-1.0) ** k / (2 * k + 1))


def aitken(s):
    s = np.asarray(s)
    d1, d2 = s[2:] - s[1:-1], s[1:-1] - s[:-2]
    with np.errstate(invalid="ignore", divide="ignore"):
        return s[2:] - d1 ** 2 / (d1 - d2)


ns = np.arange(3, 26)
plain = [abs(leib(n)[-1] - math.pi) for n in ns]
avg = []
for n in ns:
    s = leib(n)
    while len(s) > 1:
        s = (s[1:] + s[:-1]) / 2
    avg.append(abs(s[-1] - math.pi))
ait = []
for n in ns:
    s = leib(n)
    while len(s) >= 3:
        s = aitken(s)
    ait.append(max(abs(s[-1] - math.pi), 1e-16))
mach = []
for m in range(1, 12):
    v = sum((-1) ** k * ((1 / 5) ** (2 * k + 1) * 16 - (1 / 239) ** (2 * k + 1) * 4) / (2 * k + 1) for k in range(m))
    mach.append(max(abs(v - math.pi), 1e-16))
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.semilogy(ns, plain, "o-", color=RED, ms=4, label=T("莱布尼茨级数直接求和", "Leibniz series, plain"))
ax.semilogy(ns, avg, "s-", color=ACC, ms=4, label=T("反复取相邻平均", "repeated averaging"))
ax.semilogy(ns, ait, "^-", color=BLUE, ms=4, label=T("反复艾特肯加速", "repeated Aitken"))
ax.semilogy(range(1, 12), mach, "d-", color=GREEN, ms=4, label=T("梅钦公式（每项算两个反正切项）", "Machin's formula"))
ax.axhline(2.2e-16, color=MUTED, ls=":", lw=1)
ax.text(17, 4e-16, T("双精度的极限", "double-precision limit"), fontsize=9, color=MUTED)
ax.set_xlabel(T("所用的项数", "terms used")); ax.set_ylabel(T("与 π 的误差", "error from π"))
ax.set_title(T("同样几十项：慢级数加速，或者换一个快级数", "A few dozen terms: accelerate a slow series, or use a fast one"), fontsize=10)
ax.legend(fontsize=9, frameon=False); clean(ax, zero=False)
fig.tight_layout()
figure(fig, "fig23_6_1")
