"""12.5 节的计算：

算例 12.5.1  卷扬机：卷筒（连同电机转子折算）转动惯量 0.80 kg·m²、半径 0.20 m，钢丝绳下挂 50 kg 的货物。制动器突然松开、电机断电，
            货物由静止下落：加速度、绳的拉力、卷筒的角加速度；忽略卷筒的转动惯量时会算成多少。
算例 12.5.2  测转动惯量：UR5e 小臂装在竖直轴的试验台上（在水平面内转动，重力不产生力矩），电机给恒定力矩，编码器测角速度。
            两次试验：0.30 N·m 时 α₁，0.60 N·m 时 α₂。轴承有不变的摩擦力矩 0.040 N·m。由两次的 α 求 J 和摩擦力矩（图 12.5.1）。
"""
import math

import numpy as np

from bookout import T, figure, out, style
from constants import g
import _draw as d

J, R, m = 0.80, 0.20, 50.0
a = m * g / (m + J / R ** 2)
Tn = m * (g - a)
out(Jd=J, Rd=R, md=m, a=a, Tn=Tn, al=a / R, Jeff=J / R ** 2, frac=a / g)

J_true, tf = 0.118576, 0.040                                       # 小臂绕肘关节（算例 12.3.2）；轴承摩擦力矩
taus = (0.30, 0.60)
als = [(tq - tf) / J_true for tq in taus]
J_fit = (taus[1] - taus[0]) / (als[1] - als[0])
tf_fit = taus[0] - J_fit * als[0]
assert abs(J_fit - J_true) < 1e-12 and abs(tf_fit - tf) < 1e-12
out(tau1=taus[0], tau2=taus[1], al1=als[0], al2=als[1], J_fit=J_fit, tf_fit=tf_fit, J_naive=taus[0] / als[0],
    err_naive=(taus[0] / als[0] - J_true) / J_true)

plt = style()
fig, ax = plt.subplots(figsize=(4.8, 2.9))
tq = np.linspace(0, 0.7, 50)
ax.plot(tq, np.maximum(0, (tq - tf) / J_true), color=d.FIT, lw=1.8, label=r"$\alpha = (M - M_\mathrm{f})/J$")
ax.plot(taus, als, "o", color=d.DATA, ms=6, label=T("两次试验", "two runs"))
ax.axvline(tf, color=d.MUTED, lw=0.7, ls=":"); ax.text(tf + 0.01, 0.35, T("摩擦力矩 $M_\\mathrm{f}$", "friction torque $M_\\mathrm{f}$"), fontsize=8.5, color=d.MUTED)
ax.set_xlabel(T("电机力矩 M / (N·m)", "motor torque M / (N·m)")); ax.set_ylabel(T("角加速度 α / (rad/s²)", "angular acceleration α / (rad/s²)"))
ax.set_xlim(0, 0.7); ax.set_ylim(0, 5.6); ax.legend(frameon=False, fontsize=8.5, loc="upper left"); d.spines(ax)
figure(fig, "fig12_5_1")
