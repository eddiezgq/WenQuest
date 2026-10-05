"""图 11.1.1：左：负载角加速度随减速比的变化，n* = √(J_L/J_m) 处最大（惯量匹配）；右：相机的视角随距离的变化，x* = √(ab) 处最大。"""
import math

import numpy as np

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
Jm, JL, tau = 1.2e-4, 0.30, 0.8
n = np.logspace(0.5, 3, 400)
al = n * tau / (n * n * Jm + JL)
a1.semilogx(n, al, color=INK, lw=2)
ns = math.sqrt(JL / Jm)
a1.plot([ns], [ns * tau / (2 * JL)], "o", color=ACC, ms=7)
a1.axvline(ns, color=MUTED, lw=0.8, ls="--")
a1.set_xlabel(T("减速比 n", "gear ratio n"))
a1.set_ylabel(T("负载角加速度 / (rad/s²)", "load acceleration / (rad/s²)"))
a1.set_title(T("n 太小力矩不够，n 太大电机自身惯量拖累", "Too small: little torque; too large: rotor inertia dominates"), fontsize=10)
clean(a1, zero=False)
a, b = 0.30, 0.50
x = np.linspace(0.05, 2.0, 400)
th = np.degrees(np.arctan(b / x) - np.arctan(a / x))
a2.plot(x, th, color=INK, lw=2)
xs = math.sqrt(a * b)
a2.plot([xs], [math.degrees(math.atan(b / xs) - math.atan(a / xs))], "o", color=ACC, ms=7)
a2.set_xlabel(T("相机到工件的水平距离 x / m", "horizontal distance x / m"))
a2.set_ylabel(T("视角 / (°)", "viewing angle / (°)"))
a2.set_title(T("太近看斜了，太远看小了，x* = √(ab)", "Too close: oblique; too far: small; x* = √(ab)"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig11_1_1")
