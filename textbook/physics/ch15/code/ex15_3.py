"""15.3 节的计算：

算例 15.3.1  把 1 kg 的物体从地面升高 400 km（空间站的高度），引力势能增加多少？用 mgh 估算差多少？
算例 15.3.2  地球、月球表面的逃逸速度。
算例 15.3.3  把 1 kg 的载荷从地面（不计地球自转）送上 400 km 高的圆轨道，最少要给它多少机械能？其中多少变成势能，多少是动能？
            （图 15.3.1：引力势能曲线和几种轨道的总能量）
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import GM_earth, R_earth_mean, G, M_moon, R_moon, g_n
import _draw as d

R, h = R_earth_mean, 400e3
U = lambda r: -GM_earth / r
dU = U(R + h) - U(R)
mgh = 9.81 * h
out(dU_MJ=dU / 1e6, mgh_MJ=mgh / 1e6, mgh_err=abs(dU - mgh) / dU)

ve = math.sqrt(2 * GM_earth / R)
vm = math.sqrt(2 * G * M_moon / R_moon)
out(ve=ve / 1000, vm=vm / 1000)

r = R + h
v_c = math.sqrt(GM_earth / r)
E_orb = 0.5 * v_c ** 2 + U(r)
E0 = U(R)
out(v_c=v_c / 1000, K_MJ=0.5 * v_c ** 2 / 1e6, dE_MJ=(E_orb - E0) / 1e6, frac_U=dU / (E_orb - E0), E_orb_MJ=-E_orb / 1e6)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
rr = np.linspace(R, 8 * R, 400)
ax.plot(rr / R, U(rr) / 1e6, color=d.INK, lw=2, label=T("引力势能 U/m", "potential energy U/m"))
ax.axhline(0, color=d.MUTED, lw=0.7)
ax.axhline(E_orb / 1e6, xmin=0, xmax=0.18, color=d.VA, lw=2)
ax.text(3.4, E_orb / 1e6 - 4.5, T("蓝线：400 km 圆轨道的总能量", "total energy, 400 km circular orbit"), fontsize=8, color=d.VA)
ax.axhline(0, xmin=0.0, xmax=1.0, color=d.VR, lw=1.2, ls="--")
ax.text(5.0, 1.5, T("总能量 ≥ 0：逃逸", "total energy ≥ 0: escape"), fontsize=8, color=d.VR)
ax.plot(1, U(R) / 1e6, "o", color=d.INK, ms=4); ax.text(1.1, U(R) / 1e6, T("地面", "ground"), fontsize=8)
ax.set_xlabel(T("到地心的距离 r / R", "distance from Earth's centre r / R")); ax.set_ylabel(T("每千克的能量 / MJ", "energy per kg / MJ"))
ax.set_xlim(0.8, 8); ax.set_ylim(-70, 6); d.spines(ax)
figure(fig, "fig15_3_1")
