"""图 13.6.1：由加速度到速度、由速度到位置。AGV 的梯形速度曲线：加速度分段为常数，积分一次得到连续、有折角的速度，
再积分一次得到光滑的位置；阴影为加速段加速度曲线下的面积，等于匀速段的速度 1.2 m/s。"""
import numpy as np

from _agv import T, acc, v
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T as TT, clean, figure, plt

t = np.linspace(0, T, 2000)
a = np.array([acc(s) for s in t])
vv = np.array([v(s) for s in t])
x = np.concatenate([[0], np.cumsum((vv[1:] + vv[:-1]) / 2 * np.diff(t))])
fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(13, 3.8))
a1.plot(t, a, color=RED, lw=2)
m = t <= 2.4
a1.fill_between(t[m], 0, a[m], color=RED, alpha=0.25)
a1.set_xlabel("t / s")
a1.set_ylabel("a / (m/s²)")
a1.set_title(TT("加速度：阴影面积 0.5 × 2.4 = 1.2", "Acceleration: shaded area 0.5 × 2.4 = 1.2"), fontsize=10)
clean(a1)
a2.plot(t, vv, color=ACC, lw=2)
a2.fill_between(t, 0, vv, color=BLUE, alpha=0.15)
a2.set_xlabel("t / s")
a2.set_ylabel("v / (m/s)")
a2.set_title(TT("速度 = v₀ + ∫a dt；面积 = 10 m", "Speed = v₀ + ∫a dt; area = 10 m"), fontsize=10)
clean(a2, zero=False)
a3.plot(t, x, color=BLUE, lw=2)
a3.set_xlabel("t / s")
a3.set_ylabel("x / m")
a3.set_title(TT("位置 = x₀ + ∫v dt", "Position = x₀ + ∫v dt"), fontsize=10)
clean(a3, zero=False)
fig.tight_layout()
figure(fig, "fig13_6_1")
