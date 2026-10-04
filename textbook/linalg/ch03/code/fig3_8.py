"""图 3.8.1：消元与回代的乘除法次数随 n 的增长（双对数坐标），与 n³/3、n²/2 对照。"""
import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, figure, plt
from _elim import count_ops

ns = np.array([2, 3, 5, 10, 20, 50, 100, 200])
mul = np.array([count_ops(int(n))[0] for n in ns])
fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.loglog(ns, mul, "o", color=BLUE, label=T("逐次数出的乘除法次数", "multiplications/divisions counted"))
nn = np.logspace(np.log10(2), np.log10(200), 50)
ax.loglog(nn, nn ** 3 / 3, color=RED, lw=1.5, label=r"$n^3/3$")
ax.loglog(nn, nn ** 2 / 2, color=GREEN, lw=1.2, ls="--", label=T(r"$n^2/2$（回代）", r"$n^2/2$ (back substitution)"))
ax.set_xlabel("n")
ax.set_ylabel(T("次数", "count"))
ax.legend(frameon=False)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
figure(fig, "fig3_8_1")
