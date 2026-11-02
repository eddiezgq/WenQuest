"""图 21.6.1：左：有阻尼单摆的轨线与能量等值线；右：带重力补偿的 PD 关节，李雅普诺夫函数 V 随时间单调减小。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

k, c = 9.81 / 0.5, 1.0
th = np.linspace(-np.pi, np.pi, 300)
w = np.linspace(-9, 9, 300)
TH, W = np.meshgrid(th, w)
V = 0.5 * W ** 2 + k * (1 - np.cos(TH))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
a1.contour(TH, W, V, levels=np.linspace(2, 38, 10), colors=MUTED, linewidths=0.7, linestyles="solid")
a1.contour(TH, W, V, levels=[2 * k], colors=RED, linewidths=1.6)
s = solve_ivp(lambda t, y: [y[1], -k * math.sin(y[0]) - c * y[1]], (0, 15), [2.6, 0], max_step=0.01)
a1.plot(s.y[0], s.y[1], color=BLUE, lw=1.6)
a1.plot(2.6, 0, "o", color=BLUE)
a1.set_xlabel(T("摆角 θ / rad", "angle θ / rad"))
a1.set_ylabel(T("角速度 ω / (rad/s)", "angular speed ω / (rad/s)"))
a1.set_title(T("轨线只能穿过 V 的等值线向内走（红：分界线）", "Orbits only cross V's level curves inward (red: separatrix)"), fontsize=10)
clean(a1)
J = 0.5129 + 137e-7 * 101 ** 2
b, Kp = 0.5, J * 100
Kd = 2 * 0.7 * 10 * J - b
mgd = 8.393 * 9.81 * 0.2125
s = solve_ivp(lambda t, y: [y[1], (Kp * (0.5 - y[0]) - Kd * y[1] - b * y[1]) / J], (0, 1.5), [0, 0], t_eval=np.linspace(0, 1.5, 600))
Vt = 0.5 * J * s.y[1] ** 2 + 0.5 * Kp * (0.5 - s.y[0]) ** 2
a2.plot(s.t, Vt, color=BLUE, lw=2.2, label=T("V = ½Jq̇² + ½K_p e²", "V = ½Jq̇² + ½K_p e²"))
a2.plot(s.t, 0.5 * Kp * (0.5 - s.y[0]) ** 2, color=ACC, lw=1.2, ls="--", label=T("其中弹簧势能 ½K_p e²", "spring energy ½K_p e²"))
a2.set_xlabel(T("时间 t / s", "time t / s"))
a2.set_ylabel("V / J")
a2.set_title(T("带重力补偿的 PD 关节：V 单调减小", "PD with gravity compensation: V decreases"), fontsize=10)
a2.legend(fontsize=9, frameon=False)
clean(a2)
fig.tight_layout()
figure(fig, "fig21_6_1")
