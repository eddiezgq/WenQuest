"""16.5 节的计算：

算例 16.5.1  文丘里流量计：水管内径 50 mm，喉部内径 25 mm，两处的压强差 12.0 kPa。流速和体积流量各多大？
            沿管道的流速和压强（图 16.5.1）。
算例 16.5.2  无人机的皮托管：动压（总压 − 静压）读数 150 Pa，空气密度 1.20 kg/m³。空速多大？
算例 16.5.3  托里拆利：直径 0.50 m 的圆柱形水箱，水深 1.00 m，底部开一个直径 10 mm 的小孔。刚开始的出水速度多大？
            水流完要多久（图 16.5.2）？（不计黏性和孔口收缩）
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

g, rho = 9.81, 1000.0
D1, D2, dp = 0.050, 0.025, 12.0e3
A1, A2 = math.pi * D1 ** 2 / 4, math.pi * D2 ** 2 / 4
v2 = math.sqrt(2 * dp / (rho * (1 - (A2 / A1) ** 2)))
v1 = v2 * A2 / A1
Q = v2 * A2
out(v1=v1, v2=v2, Q_Ls=Q * 1000)

dpp, rho_a = 150.0, 1.20
out(va=math.sqrt(2 * dpp / rho_a), va_kmh=math.sqrt(2 * dpp / rho_a) * 3.6)

Dt, H0, dh = 0.50, 1.00, 0.010
At, Ah = math.pi * Dt ** 2 / 4, math.pi * dh ** 2 / 4
v0 = math.sqrt(2 * g * H0)
Tdrain = At / Ah * math.sqrt(2 * H0 / g)
out(v0=v0, Tdrain_min=Tdrain / 60, Thalf_min=At / Ah * (math.sqrt(2 * H0 / g) - math.sqrt(2 * H0 / 2 / g)) / 60)

plt = style()
fig, (a1, a2) = plt.subplots(2, 1, figsize=(4.8, 3.6), sharex=True)
xx = np.linspace(0, 1, 400)
Dx = D1 - (D1 - D2) * np.exp(-((xx - 0.5) / 0.12) ** 2)
vx = Q / (math.pi * Dx ** 2 / 4)
px = (0.5 * rho * v1 ** 2 - 0.5 * rho * vx ** 2) / 1000
a1.fill_between(xx, Dx / 2 * 1000, -Dx / 2 * 1000, color="#dfe8ef"); a1.plot(xx, Dx / 2 * 1000, color=d.INK, lw=1); a1.plot(xx, -Dx / 2 * 1000, color=d.INK, lw=1)
a1.set_ylabel(T("管壁 / mm", "wall / mm")); d.spines(a1)
a2.plot(xx, vx, color=d.VA, lw=2, label=T("流速 / (m/s)", "speed / (m/s)"))
a2.plot(xx, px, color=d.VR, lw=2, ls="--", label=T("压强变化 / kPa", "pressure change / kPa"))
a2.axhline(0, color=d.MUTED, lw=0.6)
a2.set_xlabel(T("沿管道的位置（相对）", "position along the pipe (relative)")); a2.legend(frameon=False, fontsize=8, loc="lower left"); d.spines(a2)
fig.tight_layout()
figure(fig, "fig16_5_1")

fig, ax = plt.subplots(figsize=(4.8, 2.9))
tt = np.linspace(0, Tdrain, 200)
hh = (math.sqrt(H0) - Ah / At * math.sqrt(g / 2) * tt) ** 2
ax.plot(tt / 60, hh, color=d.VA, lw=2)
ax.set_xlabel(T("时间 / min", "time / min")); ax.set_ylabel(T("水深 / m", "water depth / m")); d.spines(ax)
figure(fig, "fig16_5_2")
