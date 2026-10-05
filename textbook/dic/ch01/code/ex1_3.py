"""1.3 节的计算：尺寸与对称。

算例 1.3.1  电机控制芯片的时钟缓冲，FO4 负载（驱动 4 个同样的反相器）：Wp/Wn = 1、√r、r 三种尺寸的 tPHL、tPLH 与平均延时。
算例 1.3.2  平均延时最小的尺寸比，在 0.5～4 之间扫描求出，与 √r 比较。
图 1.3.1    tPHL、tPLH 与平均延时随 Wp/Wn 的变化。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from mos import Wmin, fo4, kn, kp, req_n, req_p
import _draw as d

r = kn / kp
rows = {}
for key, ratio in (("one", 1.0), ("sqrt", math.sqrt(r)), ("r", r)):
    a, b = fo4(Wmin, ratio * Wmin)
    rows[key] = (ratio, a, b, (a + b) / 2, (b - a) / ((a + b) / 2))
for key, (ratio, a, b, tp, mis) in rows.items():
    out(**{f"ratio_{key}": ratio, f"tphl_{key}": a * 1e12, f"tplh_{key}": b * 1e12, f"tp_{key}": tp * 1e12, f"mis_{key}": mis * 100})
ratios = np.linspace(0.5, 4, 701)
tps = [sum(fo4(Wmin, x * Wmin)) / 2 for x in ratios]
k = int(np.argmin(tps))
out(r=r, sqrt_r=math.sqrt(r), best=ratios[k], tp_best=tps[k] * 1e12,
    rn_k=req_n(Wmin) / 1e3, rp_k=req_p(Wmin) / 1e3)
fclk = 500e6                                          # 1.3.1 节：高速计数时钟
a, b = fo4(Wmin, Wmin)
out(fclk_mhz=fclk / 1e6, period_ns=1e9 / fclk, duty_one=50 + (a - b) * fclk * 100, dt_one_ps=(b - a) * 1e12)

plt = style()
fig, ax = plt.subplots(figsize=(5.4, 3.6))
ax.plot(ratios, [fo4(Wmin, x * Wmin)[0] * 1e12 for x in ratios], color=d.NMOS, lw=1.6, label=T("tPHL（下拉）", "tPHL (pull-down)"))
ax.plot(ratios, [fo4(Wmin, x * Wmin)[1] * 1e12 for x in ratios], color=d.PMOS, lw=1.6, label=T("tPLH（上拉）", "tPLH (pull-up)"))
ax.plot(ratios, [t * 1e12 for t in tps], color=d.MEAN, lw=2.0, label=T("平均 tp", "average tp"))
for x, name in ((math.sqrt(r), "√r"), (r, "r")):
    ax.axvline(x, color=d.MUTED, lw=0.8, ls="--")
    ax.text(x + 0.04, 23, name, color=d.MUTED, fontsize=10)
ax.set_xlim(0.5, 4); ax.set_ylim(20, 100)
ax.set_xlabel(T("尺寸比 Wp/Wn", "size ratio Wp/Wn"))
ax.set_ylabel(T("FO4 延时 / ps", "FO4 delay / ps"))
ax.legend(fontsize=9, frameon=False, loc="upper right")
d.spines(ax)
figure(fig, "fig1_3_1")
