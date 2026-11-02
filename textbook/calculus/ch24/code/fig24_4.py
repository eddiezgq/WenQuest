"""图 24.4.1：单摆周期与小振幅周期之比：椭圆积分的精确值与二项式级数取 2、3、5、11 项。"""
import math

import numpy as np
from scipy import special

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt


def coef(n):
    c = 1.0
    for j in range(1, n + 1):
        c *= (2 * j - 1) / (2 * j)
    return c * c


th = np.linspace(0.5, 175, 400)
k = np.sin(np.radians(th) / 2)
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(th, 2 / np.pi * special.ellipk(k * k), color=INK, lw=2.5, label=T("精确（椭圆积分）", "exact (elliptic integral)"))
for m, col in ((2, RED), (3, ACC), (5, GREEN), (11, BLUE)):
    ax.plot(th, sum(coef(n) * k ** (2 * n) for n in range(m)), color=col, lw=1.4, label=T(f"级数前 {m} 项", f"first {m} terms"))
ax.set_ylim(0.95, 3)
ax.set_xlabel(T("摆幅 θ₀ / °", "amplitude θ₀ / °")); ax.set_ylabel("T/T₀")
ax.set_title(T("摆幅越大，需要的项数越多；接近 180° 时级数收敛极慢", "Larger swings need more terms; near 180° the series crawls"), fontsize=10)
ax.legend(fontsize=9, frameon=False, loc="upper left"); clean(ax, zero=False)
fig.tight_layout()
figure(fig, "fig24_4_1")
