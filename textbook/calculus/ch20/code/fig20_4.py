"""图 20.4.1：左：PD 关节阶跃响应（ζ = 0.6、ω_n = 10 rad/s）= 稳态 1 + 衰减的暂态；
右：柔性上臂在“加速 T、减速 T”运动中的扭转角，T = T_n 与 T = 1.5 T_n 比较。"""
import numpy as np
from scipy.integrate import solve_ivp

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
z, wn = 0.6, 10.0
wd = wn * np.sqrt(1 - z * z)
t = np.linspace(0, 1.2, 500)
tr = -np.exp(-z * wn * t) * (np.cos(wd * t) + z / np.sqrt(1 - z * z) * np.sin(wd * t))
a1.plot(t, 1 + tr, color=BLUE, lw=2.4, label=T("q(t) = 稳态 + 暂态", "q(t) = steady + transient"))
a1.axhline(1, color=GREEN, lw=1.5, ls="--", label=T("稳态（特解）1", "steady state (particular) 1"))
a1.plot(t, tr, color=ACC, lw=1.5, ls="-.", label=T("暂态（齐次解）", "transient (homogeneous)"))
a1.set_xlabel(T("时间 t / s", "time t / s"))
a1.set_ylabel(T("关节角（目标为 1）", "joint angle (target 1)"))
a1.set_title(T("阶跃响应 = 特解 + 齐次解", "Step response = particular + homogeneous"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="center right")
clean(a1)
J, k, zz, a0 = 0.5129, 2e4, 0.02, 10.0
w = np.sqrt(k / J)
Tn = 2 * np.pi / w
for frac, col in ((1.0, BLUE), (1.5, RED)):
    Tm = frac * Tn
    al = lambda s, Tm=Tm: a0 if s < Tm else (-a0 if s < 2 * Tm else 0.0)
    s = solve_ivp(lambda s_, y: [y[1], -al(s_) - 2 * zz * w * y[1] - w * w * y[0]], (0, 0.25), [0, 0], max_step=Tn / 80, rtol=1e-9, atol=1e-12)
    a2.plot(s.t * 1000, s.y[0] * 1e6, color=col, lw=1.4, label=f"T = {frac:g} T_n")
    a2.axvline(2 * Tm * 1000, color=col, ls=":", lw=1)
a2.set_xlabel(T("时间 t / ms（点线：运动结束）", "time t / ms (dotted: motion ends)"))
a2.set_ylabel(T("扭转角 φ / μrad", "twist φ / μrad"))
a2.set_title(T("加速时间为整数个周期时，停下不抖", "Accelerating for whole periods leaves no residual vibration"), fontsize=10)
a2.legend(fontsize=9, frameon=False)
clean(a2)
fig.tight_layout()
figure(fig, "fig20_4_1")
