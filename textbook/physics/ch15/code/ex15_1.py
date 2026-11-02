"""15.1 节的计算：

算例 15.1.1  两个 80 kg 的人相距 1.0 m，引力多大？与 1 mg 的物体所受的重力比一比。
算例 15.1.2  卡文迪什扭秤（数据取卡文迪什 1798 年装置的量级）：大铅球 158 kg，小铅球 0.73 kg，两球心相距 0.225 m；
            小球挂在长 1.86 m 的轻杆两端（离悬丝 0.93 m）。扭秤自由摆动的周期 7.0 min。求悬丝的扭转系数、
            一对球之间的引力、扭秤的偏转角；把大球移到另一侧时，偏转角改变多少（图 15.1.1）？
            由测得的 G 和地面的 g 求地球的质量和平均密度。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import G, R_earth_mean, g_n
import _draw as d

m1, r1 = 80.0, 1.0
F1 = G * m1 * m1 / r1 ** 2
out(F1_e7=F1 * 1e7, W_mg=1e-6 * g_n, ratio_mg=F1 / (1e-6 * g_n))

M, m, r, l, Tp = 158.0, 0.73, 0.225, 0.93, 7.0 * 60
I = 2 * m * l ** 2
kappa = 4 * math.pi ** 2 * I / Tp ** 2
F = G * M * m / r ** 2
th = 2 * F * l / kappa
out(I=I, kappa_e4=kappa * 1e4, F_e7=F * 1e7, th_e3=th * 1e3, th_deg=math.degrees(th), dth_e3=2 * th * 1e3,
    spot_mm=2 * 2 * th * 5.0 * 1000, ratio_w=F / (m * g_n))
# 反过来：由偏转角和周期求 G（这就是卡文迪什的做法）
G_back = kappa * th / (2 * l) * r ** 2 / (M * m)                   # θ = 2Fl/κ ⇒ F = κθ/(2l) ⇒ G = F r²/(Mm)
assert abs(G_back - G) / G < 1e-12
Me = g_n * R_earth_mean ** 2 / G
rho = Me / (4 / 3 * math.pi * R_earth_mean ** 3)
out(Me_e24=Me / 1e24, rho=rho / 1000, G_e11=G * 1e11, gn=g_n)

# 图：大球换到另一侧（t = 0）后扭秤的摆动，衰减时间取 30 min
tt = np.linspace(0, 60 * 60, 2000)
w = 2 * math.pi / Tp
tau = 30 * 60
ang = -th + 2 * th * np.exp(-tt / tau) * np.cos(w * tt)
plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
ax.plot(tt / 60, ang * 1e3, color=d.VA, lw=1.6)
ax.axhline(th * 1e3, color=d.MUTED, lw=0.8, ls="--"); ax.axhline(-th * 1e3, color=d.VR, lw=0.8, ls="--")
ax.text(41, th * 1e3 + 0.12, T("原来的平衡位置", "old equilibrium"), fontsize=8, color=d.MUTED)
ax.text(33, -2.65, T("红色虚线：新的平衡位置", "new equilibrium"), fontsize=8, color=d.VR)
ax.set_xlabel(T("时间 / min", "time / min")); ax.set_ylabel(T("扭转角 / mrad", "twist angle / mrad"))
ax.set_xlim(0, 60); d.spines(ax)
figure(fig, "fig15_1_1")
