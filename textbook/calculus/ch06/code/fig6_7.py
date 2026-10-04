"""图 6.7.1：上极限与下极限——跟踪误差的尾部上确界、下确界随起点后移单调变化，趋于 ±30 mm。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

Ts = 0.01
t = np.arange(0, 60, Ts)
e = (0.2 * np.exp(-t / 2) * np.cos(9 * t) + 0.02 * np.sin(2 * math.pi * 1.3 * t) + 0.01 * np.sin(2 * math.pi * math.sqrt(2) * t)) * 1000
sup_tail = np.maximum.accumulate(e[::-1])[::-1]
inf_tail = np.minimum.accumulate(e[::-1])[::-1]
fig, ax = plt.subplots(figsize=(11, 3.6))
ax.plot(t, e, color=MUTED, lw=0.6, label=T("跟踪误差 e(t)", "tracking error e(t)"))
ax.plot(t, sup_tail, color=RED, lw=2, label=T("尾部上确界 sup_{s≥t} e(s)", "tail sup"))
ax.plot(t, inf_tail, color=BLUE, lw=2, label=T("尾部下确界 inf_{s≥t} e(s)", "tail inf"))
ax.axhline(30, color=RED, lw=0.8, ls="--")
ax.axhline(-30, color=BLUE, lw=0.8, ls="--")
ax.set_ylim(-60, 80)
ax.set_xlim(0, 30)
ax.set_xlabel(T("时间 t / s", "time t / s"))
ax.set_ylabel("mm")
ax.legend(fontsize=9, frameon=False, ncol=3, loc="upper right")
clean(ax)
fig.tight_layout()
figure(fig, "fig6_7_1")
