"""图 9.7.1：AGV 里程计 Δy/(vT) = (1 − cos u)/u（u = ωT）：直接公式的相对误差随 u 减小而增大（相消），
三项泰勒公式的相对误差随 u 增大而增大（截断）；两条误差模型在 u ≈ 0.04 处相等，取它作切换阈值。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

u = 10.0 ** np.linspace(-8, 0, 300)
ref = 2 * np.sin(u / 2) ** 2 / u
d = np.abs((1 - np.cos(u)) / u - ref) / ref
s = np.abs(u / 2 - u ** 3 / 24 + u ** 5 / 720 - ref) / ref
fig, ax = plt.subplots(figsize=(7.2, 4.2))
ax.loglog(u, np.maximum(d, 1e-17), ".", color=BLUE, ms=3, label=T("直接公式 (1 − cos u)/u", "direct (1 − cos u)/u"))
ax.loglog(u, np.maximum(s, 1e-17), ".", color=RED, ms=3, label=T("泰勒公式 u/2 − u³/24 + u⁵/720", "Taylor u/2 − u³/24 + u⁵/720"))
ax.loglog(u, 2 * 2.220446049250313e-16 / u ** 2, color=BLUE, lw=0.8, ls="--")
ax.loglog(u, u ** 6 / 20160, color=RED, lw=0.8, ls="--")
ax.axvline((40320 * 2.220446049250313e-16) ** (1 / 8), color=MUTED, lw=1)
ax.set_ylim(1e-17, 10)
ax.set_xlabel("u = ωT")
ax.set_ylabel(T("相对误差", "relative error"))
ax.set_title(T("u 小于约 0.04 时换用泰勒公式", "Switch to the Taylor formula below u ≈ 0.04"), fontsize=10)
ax.legend(fontsize=9, frameon=False, loc="upper center")
clean(ax, zero=False)
fig.tight_layout()
figure(fig, "fig9_7_1")
