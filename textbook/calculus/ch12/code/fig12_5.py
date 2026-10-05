"""图 12.5.1：左：AGV 一次搬运的电功率 P(t) 与累计能耗（右轴）；右：五次多项式运动的角加速度、它的平方与均方根。"""
import math

import numpy as np

from _agv import T, power
from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T as TT, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
t = np.linspace(0, T, 2000)
P = np.array([power(s) for s in t])
E = np.concatenate([[0], np.cumsum((P[1:] + P[:-1]) / 2 * np.diff(t))])
a1.plot(t, P, color=BLUE, lw=2, label=TT("功率 P(t)", "power P(t)"))
a1.axhline(E[-1] / T, color=BLUE, lw=0.8, ls="--")
a1.set_xlabel("t / s")
a1.set_ylabel("P / W")
a1b = a1.twinx()
a1b.plot(t, E, color=RED, lw=1.6, label=TT("累计能耗", "energy used"))
a1b.set_ylabel("E / J")
a1.set_title(TT("能耗是功率曲线下的面积；虚线为平均功率", "Energy = area under power; dashed: average"), fontsize=10)
h1, l1 = a1.get_legend_handles_labels()
h2, l2 = a1b.get_legend_handles_labels()
a1.legend(h1 + h2, l1 + l2, fontsize=9, frameon=False, loc="upper center")
clean(a1, zero=False)
a1b.spines["top"].set_visible(False)
Tq, D = 2.0, math.pi / 2
tq = np.linspace(0, Tq, 600)
s = tq / Tq
al = D / Tq ** 2 * 60 * s * (1 - s) * (1 - 2 * s)
rms = math.sqrt(np.mean(al ** 2))
a2.plot(tq, al, color=INK, lw=2, label="α(t)")
a2.plot(tq, al ** 2, color=GREEN, lw=1.4, label="α²(t)")
a2.axhline(rms ** 2, color=GREEN, lw=0.8, ls="--")
a2.axhline(rms, color=RED, lw=1.2, ls="--", label=TT("均方根", "RMS"))
a2.set_xlabel("t / s")
a2.set_title(TT("均方根 = √(α² 的平均值)", "RMS = √(mean of α²)"), fontsize=10)
a2.legend(fontsize=9, frameon=False, loc="lower left")
clean(a2)
fig.tight_layout()
figure(fig, "fig12_5_1")
