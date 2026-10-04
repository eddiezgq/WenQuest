"""图 5.5.1：用二分法求关节阶跃响应首次到达 95% 的时刻。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

zeta, wn = 0.6, 10.0
wd = wn * math.sqrt(1 - zeta ** 2)
q = lambda t: 1 - np.exp(-zeta * wn * t) * (np.cos(wd * t) + zeta / math.sqrt(1 - zeta ** 2) * np.sin(wd * t))
tp = math.pi / wd
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 3.9), gridspec_kw={"width_ratios": [1.2, 1]})
t = np.linspace(0, 1, 500)
a1.plot(t, q(t), color=BLUE, lw=2)
a1.axhline(0.95, color=RED, lw=1, ls="--")
a1.axvspan(0, tp, color=MUTED, alpha=0.1)
a1.text(0.95, 0.9, "95%", color=RED, ha="right")
a1.set_xlabel(T("时间 t / s", "time t / s"))
a1.set_ylabel(T("关节角 / 目标值", "joint angle / target"))
a1.set_title(T("阶跃响应；灰色区间 [0, 峰值时刻] 上单调", "Step response; monotone on the grey interval"), fontsize=10)
clean(a1, zero=False)
a, b = 0.0, tp
for k in range(8):
    a2.plot([a, b], [k, k], color=BLUE, lw=3)
    m = (a + b) / 2
    a2.plot([m], [k], "|", color=RED, ms=10)
    if q(m) - 0.95 > 0:
        b = m
    else:
        a = m
a2.invert_yaxis()
a2.set_yticks(range(8))
a2.set_yticklabels([str(k + 1) for k in range(8)])
a2.set_ylabel(T("第 k 步", "step k"))
a2.set_xlabel(T("时间 t / s", "time t / s"))
a2.set_title(T("每一步区间减半（红线是中点）", "Each step halves the interval (red: midpoint)"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig5_5_1")
