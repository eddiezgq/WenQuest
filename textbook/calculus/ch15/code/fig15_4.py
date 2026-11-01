"""图 15.4.1：夹爪接触力（1 ms 的半正弦冲击脉冲加逐渐建立的夹持力）与自适应辛普森的求值点：上图全程，下图放大到脉冲附近；
底部短竖线是求值点，集中在脉冲两侧。"""
import math

import numpy as np

from _quad import adaptive_simpson
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

t0, w, Fp, Tm = 0.4013, 0.001, 400.0, 1.0


def F(t):
    hold = 2 * (1 - math.exp(-max(t - t0, 0.0) / 0.05))
    pulse = Fp * math.sin(math.pi * (t - t0) / w) if t0 <= t <= t0 + w else 0.0
    return hold + pulse


v, pts = adaptive_simpson(F, 0, Tm, 1e-5)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(9, 5.6))
t = np.linspace(0, Tm, 20001)
a1.plot(t, [F(s) for s in t], color=INK, lw=1.2)
a1.plot(pts, [-15] * len(pts), "|", color=RED, ms=8)
a1.set_xlabel("t / s")
a1.set_ylabel("F / N")
a1.set_title(T(f"全程：自适应辛普森共求值 {len(pts)} 次，集中在冲击附近", f"Whole record: {len(pts)} adaptive evaluations, clustered at the impact"), fontsize=10)
clean(a1)
tt = np.linspace(t0 - 0.002, t0 + 0.003, 2000)
a2.plot((tt - t0) * 1000, [F(s) for s in tt], color=INK, lw=1.6)
near = [p for p in pts if t0 - 0.002 <= p <= t0 + 0.003]
a2.plot([(p - t0) * 1000 for p in near], [F(p) for p in near], "o", color=RED, ms=3)
a2.set_xlabel(T("t − t₀ / ms", "t − t₀ / ms"))
a2.set_ylabel("F / N")
a2.set_title(T("放大：脉冲上的求值点", "Zoom: evaluation points on the pulse"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig15_4_1")
