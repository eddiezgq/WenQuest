"""图 24.2.1：用 arctan 级数的前 6 项计算 arctan x：直接用（只在 0 附近准）与先化简到 |t| ≤ tan 15°（全实轴相对误差约 1e-8）。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

m = 6
t15 = math.tan(math.pi / 12)
poly = lambda x: sum((-1) ** k * x ** (2 * k + 1) / (2 * k + 1) for k in range(m))


def red(x):
    s = np.sign(x); x = np.abs(x)
    big = x > 1
    x1 = np.where(big, 1 / np.where(big, x, 1), x)
    mid = x1 > t15
    x2 = np.where(mid, (math.sqrt(3) * x1 - 1) / (x1 + math.sqrt(3)), x1)
    r = poly(x2) + np.where(mid, math.pi / 6, 0)
    return s * np.where(big, math.pi / 2 - r, r)


x = np.linspace(-4, 4, 4001)
x = x[x != 0]
fig, ax = plt.subplots(figsize=(8, 4))
ax.semilogy(x, np.abs(poly(x) - np.arctan(x)) / np.abs(np.arctan(x)) + 1e-18, color=RED, lw=1.8, label=T("直接用前 6 项", "first 6 terms, directly"))
ax.semilogy(x, np.abs(red(x) - np.arctan(x)) / np.abs(np.arctan(x)) + 1e-18, color=BLUE, lw=1.4, label=T("先化简到 |t| ≤ tan 15° 再用前 6 项", "reduce to |t| ≤ tan 15°, then 6 terms"))
ax.axhline(2 ** -24, color=MUTED, ls="--", lw=1)
ax.text(2.2, 2 ** -24 * 2, T("单精度 2⁻²⁴", "single precision 2⁻²⁴"), fontsize=9, color=MUTED)
ax.set_ylim(1e-18, 1e3)
ax.set_xlabel("x"); ax.set_ylabel(T("相对误差", "relative error"))
ax.set_title(T("arctan x：范围化简让几项级数在全实轴上可用", "arctan x: range reduction makes a few terms work everywhere"), fontsize=10)
ax.legend(fontsize=9, frameon=False, loc="upper left"); clean(ax, zero=False)
fig.tight_layout()
figure(fig, "fig24_2_1")
