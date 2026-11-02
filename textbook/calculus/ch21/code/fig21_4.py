"""图 21.4.1：左：自平衡机器人（PD，转矩限幅 15 N·m）的相图与吸引域（网格上逐点仿真）；
右：PID 关节闭环特征根的最大实部随积分增益的变化。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

m, h, g = 5.0, 0.4, 9.81
I, mgl = m * h * h, m * g * h
Kp, Kd, Tmax = I * 64 + mgl, 2 * 0.7 * 8 * I, 15.0


def f(t, y):
    tau = max(-Tmax, min(Tmax, -Kp * y[0] - Kd * y[1]))
    return [y[1], (mgl * math.sin(y[0]) + tau) / I]


fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.2))
th = np.linspace(-1.5, 1.5, 61)
om = np.linspace(-6, 6, 61)
ok = np.zeros((om.size, th.size))
ev = lambda t, y: abs(y[0]) - 1.6
ev.terminal = True
for i, w0 in enumerate(om):
    for j, t0 in enumerate(th):
        s = solve_ivp(f, (0, 3), [t0, w0], events=ev, max_step=0.01)
        ok[i, j] = 1.0 if (s.status == 0 and abs(s.y[0, -1]) < 0.05) else 0.0
a1.contourf(th, om, ok, levels=[0.5, 1.5], colors=[GREEN], alpha=0.25)
for t0, w0 in ((0.6, 0), (-0.6, 2), (0.95, 0), (0.3, 4), (-0.3, -4.5)):
    s = solve_ivp(f, (0, 3), [t0, w0], events=ev, max_step=0.01)
    a1.plot(s.y[0], s.y[1], color=BLUE if abs(s.y[0, -1]) < 0.05 else RED, lw=1.5)
    a1.plot(t0, w0, "o", color=INK, ms=3)
a1.axvline(math.asin(Tmax / mgl), color=MUTED, ls=":", lw=1)
a1.axvline(-math.asin(Tmax / mgl), color=MUTED, ls=":", lw=1)
a1.set_xlabel(T("倾角 θ / rad", "tilt θ / rad"))
a1.set_ylabel(T("倾角速度 / (rad/s)", "tilt rate / (rad/s)"))
a1.set_title(T("自平衡机器人：绿色为吸引域（转矩限幅 15 N·m）", "Balancing robot: green = basin of attraction (15 N·m limit)"), fontsize=10)
clean(a1)
J = 0.5129 + 137e-7 * 101 ** 2
B, Kpj = 2 * 0.7 * 10 * J, J * 100 - 8.393 * 9.81 * 0.2125 * math.sin(0.5)
Ki = np.linspace(1, 1400, 400)
mx = [max(np.roots([J, B, Kpj, k]).real) for k in Ki]
a2.plot(Ki, mx, color=BLUE, lw=2)
a2.axhline(0, color=MUTED, lw=0.8)
a2.axvline(B * Kpj / J, color=RED, ls="--", lw=1.2)
a2.text(B * Kpj / J + 20, -4, "K_i = B K′ / J", color=RED, fontsize=9)
a2.set_xlabel(T("积分增益 K_i / (N·m/(rad·s))", "integral gain K_i / (N·m/(rad·s))"))
a2.set_ylabel(T("特征根的最大实部 / s⁻¹", "largest real part / s⁻¹"))
a2.set_title(T("PID 关节：积分增益超过上限就不稳定", "PID joint: unstable beyond the K_i limit"), fontsize=10)
clean(a2, zero=False)
fig.tight_layout()
figure(fig, "fig21_4_1")
