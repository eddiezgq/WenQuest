"""图 17.7.1：左：焊接机器人投资的累计现值（折现与不折现）与买价 30 万元，交点是回收期；
右：指示剂稀释法：动脉中指示剂浓度的采样（每 2 s）与浓度曲线，曲线下面积决定心输出量。"""
import math

import numpy as np
from scipy import integrate

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
flow = lambda t: 12 - (1 + 0.5 * t)
tt = np.linspace(0, 8, 200)
pv = [integrate.quad(lambda s: flow(s) * math.exp(-0.06 * s), 0, x)[0] for x in tt]
nd = [integrate.quad(flow, 0, x)[0] for x in tt]
a1.plot(tt, pv, color=BLUE, lw=2, label=T("累计现值（折现率 6%）", "cumulative present value (6%)"))
a1.plot(tt, nd, color=MUTED, lw=1.5, ls="--", label=T("不折现", "undiscounted"))
a1.axhline(30, color=RED, lw=1.5, label=T("买价 30 万元", "price 300k yuan"))
a1.set_xlabel(T("年", "years"))
a1.set_ylabel(T("万元", "10k yuan"))
a1.legend(fontsize=9, frameon=False)
a1.set_title(T("PV = ∫ f(t) e^(−rt) dt", "PV = ∫ f(t) e^(−rt) dt"), fontsize=10)
clean(a1)
c = lambda t: 3.75 * t * t * np.exp(-t / 2)
t = np.linspace(0, 24, 300)
a2.fill_between(t, 0, c(t), color=GREEN, alpha=0.2)
a2.plot(t, c(t), color=GREEN, lw=2)
ts = np.arange(0, 25, 2)
a2.plot(ts, c(ts), "o", color=INK, ms=5, label=T("每 2 s 一次采样", "sample every 2 s"))
a2.set_xlabel("t / s")
a2.set_ylabel(T("浓度 / (mg/L)", "concentration / (mg/L)"))
a2.legend(fontsize=9, frameon=False)
a2.set_title(T("心输出量 = 注入量 / ∫c dt", "Cardiac output = dose / ∫c dt"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig17_7_1")
