"""16.6 节的计算：

算例 16.6.1  真空吸盘的气管：内径 4.0 mm、长 2.0 m，空气黏度 1.8×10⁻⁵ Pa·s，两端压强差 100 Pa。按泊肃叶定律，体积流量多大？
            平均流速、雷诺数各多大，层流的假设成立吗？压强差加到 10 kPa 呢？内径换成 6.0 mm，流量变成几倍？（图 16.6.1）
算例 16.6.2  几种流动的雷诺数：水管里的水（d = 20 mm，v = 1 m/s），无人机桨叶（弦长 2 cm，相对速度 60 m/s），
            毛细血管里的血（d = 8 μm，v = 1 mm/s，ν 取 3×10⁻⁶ m²/s），水中游动的微型机器人（尺寸 10 μm，v = 10 μm/s）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
import _draw as d

eta, R, L, dp, rho_air = 1.8e-5, 2.0e-3, 2.0, 100.0, 1.2
Q = math.pi * R ** 4 * dp / (8 * eta * L)
vm = Q / (math.pi * R ** 2)
Re = rho_air * vm * 2 * R / eta
out(Q_Lmin=Q * 1000 * 60, vm=vm, Re=Re, ratio6=(3.0 / 2.0) ** 4, Re10k=Re * 100, vm10k=vm * 100)

nu_w, nu_a = 1.0e-6, 1.5e-5
cases = {"pipe": 0.020 * 1.0 / nu_w, "prop": 0.02 * 60 / nu_a, "cap": 8e-6 * 1e-3 / 3e-6, "micro": 10e-6 * 10e-6 / nu_w}
out(**{f"Re_{k}": v for k, v in cases.items()})

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
rr = np.linspace(-1, 1, 200)
ax.plot(2 * vm * (1 - rr ** 2), rr * R * 1000, color=d.VA, lw=2)
for y in np.linspace(-0.8, 0.8, 9):
    ax.annotate("", xy=(2 * vm * (1 - y ** 2), y * R * 1000), xytext=(0, y * R * 1000), arrowprops=dict(arrowstyle="->", color=d.MUTED, lw=0.8))
ax.axhline(R * 1000, color=d.INK, lw=2); ax.axhline(-R * 1000, color=d.INK, lw=2)
ax.set_xlabel(T("流速 / (m/s)", "speed / (m/s)")); ax.set_ylabel(T("离管轴的距离 / mm", "distance from axis / mm"))
ax.set_title(T("层流：管壁处流速为零，管轴上最大", "laminar: zero at the wall, maximum on the axis"), fontsize=9)
d.spines(ax)
figure(fig, "fig16_6_1")
