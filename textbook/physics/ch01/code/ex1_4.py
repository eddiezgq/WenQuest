"""1.4 节的计算：

算例 1.4.1  估一估：数字工厂的一台 AGV（连货约 500 kg）一个 8 小时的班次要用多少电？电池够不够？
算例 1.4.2  估一估：一台 UR5e（约 21 kg，按铝估算）由多少个原子组成？
图 1.4.1    从质子到可观测宇宙：长度的数量级。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g, N_A
import _draw as d

# ---- 算例 1.4.1
m, Crr, v, frac, hours = 500.0, 0.015, 1.0, 0.5, 8.0
dist = v * hours * 3600 * frac                       # m
E_roll = Crr * m * g * dist                          # J
eta = 0.8
E_drive = E_roll / eta
P_elec, E_elec = 100.0, 100.0 * hours * 3600         # 控制器、激光雷达等电子设备
E_total_kWh = (E_drive + E_elec) / 3.6e6
batt_kWh = 48 * 40 / 1000

# ---- 算例 1.4.2
M_ur = 21.0
M_Al = 26.98e-3                                      # kg/mol
n_atoms = M_ur / M_Al * N_A

out(m=m, Crr=Crr, v=v, frac=frac, hours=hours, dist_km=dist / 1000, E_roll_MJ=E_roll / 1e6, E_roll_kWh=E_roll / 3.6e6,
    E_drive_kWh=E_drive / 3.6e6, E_elec_kWh=E_elec / 3.6e6, E_total_kWh=E_total_kWh, batt_kWh=batt_kWh, n_atoms=n_atoms,
    lg_atoms=math.log10(n_atoms))

plt = style()
items = [(-15, T("质子", "proton")), (-10, T("原子", "atom")), (-7, T("病毒", "virus")), (-4.1, T("头发直径", "a hair")),
         (-0.07, T("UR5e 工作半径", "UR5e reach")), (3.94, T("珠穆朗玛峰", "Everest")), (7.1, T("地球直径", "Earth's diameter")),
         (11.17, T("日地距离", "Earth–Sun")), (15.98, T("1 光年", "1 light-year")), (21, T("银河系", "Milky Way")),
         (26.9, T("可观测宇宙直径", "observable universe"))]
fig, ax = plt.subplots(figsize=(7.4, 2.2))
ax.plot([-16, 28], [0, 0], color=d.INK, lw=1.5)
for x in range(-15, 28, 5):
    ax.plot([x, x], [-0.08, 0.08], color=d.INK, lw=1)
    ax.text(x, -0.3, f"$10^{{{x}}}$", ha="center", fontsize=9)
for i, (x, lab) in enumerate(items):
    up = 1 if i % 2 == 0 else -1
    ax.plot([x], [0], "o", color=d.FIT, ms=5)
    ax.plot([x, x], [0, 0.45 * up], color=d.MUTED, lw=0.8)
    ax.text(x, 0.55 * up, lab, ha="center", va="bottom" if up > 0 else "top", fontsize=8.5)
ax.text(27.5, -0.3, "m", fontsize=9)
ax.set_xlim(-17, 29); ax.set_ylim(-1.1, 1.1); d.clean(ax)
figure(fig, "fig1_4_1")
