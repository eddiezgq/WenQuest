"""图 19.4.1：左：关节电机（τ ≈ 19.9 ms）在电压斜坡（0.2 s 内升到 48 V）下的转速与“理想转速”，暂态后落后 τ；
右：RC 低通滤波器（τ = 10 ms）的输入（1 Hz 信号 + 50 Hz 干扰）与输出。"""
import numpy as np
from scipy.integrate import solve_ivp

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
R, k, Jt = 1.13, 60.3e-3, 137e-7 + 0.5129 / 101 ** 2
tau = R * Jt / k ** 2
Tr = 0.2
u = lambda t: 48 * np.minimum(t / Tr, 1.0)
s = solve_ivp(lambda t, w: [(u(t) / k - w[0]) / tau], (0, 0.35), [0.0], max_step=1e-4, dense_output=True)
t = np.linspace(0, 0.35, 700)
a1.plot(t * 1000, u(t) / k, color=MUTED, ls="--", lw=1.5, label=T("理想转速 V(t)/k", "ideal speed V(t)/k"))
a1.plot(t * 1000, s.sol(t)[0], color=BLUE, lw=2, label=T("电机转速 ω(t)", "motor speed ω(t)"))
t1 = 0.15
a1.annotate("", xy=(t1 * 1000, u(t1) / k), xytext=((t1 + tau) * 1000, u(t1) / k), arrowprops=dict(arrowstyle="<->", color=RED, lw=1.2))
a1.text((t1 + tau / 2) * 1000, u(t1) / k + 25, "τ", color=RED, fontsize=11, ha="center")
a1.set_xlabel(T("时间 t / ms", "time t / ms"))
a1.set_ylabel(T("电机转速 / (rad/s)", "motor speed / (rad/s)"))
a1.set_title(T("电压斜坡启动：转速在时间上落后 τ ≈ 19.9 ms", "Ramp start: the speed lags by τ ≈ 19.9 ms"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="lower right")
clean(a1)
tc = 10e-3
sig = lambda t: np.sin(2 * np.pi * t) + 0.5 * np.sin(2 * np.pi * 50 * t)
s = solve_ivp(lambda t, y: [(sig(t) - y[0]) / tc], (0, 2), [0.0], max_step=2e-4, t_eval=np.linspace(1, 2, 4001))
a2.plot(s.t, sig(s.t), color=MUTED, lw=0.6, label=T("输入：1 Hz 信号 + 50 Hz 干扰", "input: 1 Hz signal + 50 Hz hum"))
a2.plot(s.t, s.y[0], color=BLUE, lw=1.6, label=T("RC 滤波后的输出", "RC filter output"))
a2.set_xlabel(T("时间 t / s", "time t / s"))
a2.set_ylabel(T("电压（归一化）", "voltage (normalized)"))
a2.set_title(T("RC 低通（τ = 10 ms，f_c ≈ 15.9 Hz）", "RC low-pass (τ = 10 ms, f_c ≈ 15.9 Hz)"), fontsize=10)
a2.legend(fontsize=9, frameon=False, loc="lower left")
clean(a2)
fig.tight_layout()
figure(fig, "fig19_4_1")
