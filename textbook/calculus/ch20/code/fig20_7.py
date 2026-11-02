"""图 20.7.1：PD 关节的阶跃响应（0.5 rad）：设计值、肘端加 2 kg、竖直平面受重力；以及对应的关节转矩。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from _fig import ACC, BLUE, GREEN, INK, MUTED, RED, T, clean, figure, plt

Ja, Jr, b = 0.5129, 137e-7 * 101 ** 2, 0.5
J = Ja + Jr
Kp, Kd = J * 100, 2 * 0.7 * 10 * J - b
mgd = 8.393 * 9.81 * 0.2125
ts = np.linspace(0, 1.5, 1501)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4.0))
for lab, Jx, g, col in ((T("设计（ζ = 0.7，ω_n = 10）", "design (ζ = 0.7, ω_n = 10)"), J, 0.0, BLUE),
                        (T("肘端加 2 kg", "2 kg at the elbow"), J + 2 * 0.425 ** 2, 0.0, ACC),
                        (T("竖直平面，受重力", "vertical plane, gravity"), J, mgd, RED)):
    s = solve_ivp(lambda t, y: [y[1], (Kp * (0.5 - y[0]) - Kd * y[1] - b * y[1] - g * math.cos(y[0])) / Jx], (0, 1.5), [0, 0], t_eval=ts, max_step=1e-3)
    a1.plot(ts, s.y[0], color=col, lw=2, label=lab)
    a2.plot(ts, Kp * (0.5 - s.y[0]) - Kd * s.y[1], color=col, lw=1.8)
a1.axhline(0.5, color=MUTED, ls=":", lw=1)
a1.axhspan(0.49, 0.51, color=GREEN, alpha=0.12)
a1.set_xlabel(T("时间 t / s", "time t / s"))
a1.set_ylabel(T("关节角 q / rad", "joint angle q / rad"))
a1.set_title(T("PD 控制的关节阶跃响应（目标 0.5 rad）", "PD-controlled joint, 0.5 rad step"), fontsize=10)
a1.legend(fontsize=9, frameon=False, loc="lower right")
clean(a1)
a2.axhline(0.187 * 101, color=MUTED, ls="--", lw=1)
a2.text(1.0, 20.5, T("额定转矩 18.9 N·m", "rated 18.9 N·m"), fontsize=9, color=MUTED)
a2.set_xlabel(T("时间 t / s", "time t / s"))
a2.set_ylabel(T("关节转矩 τ / (N·m)", "joint torque τ / (N·m)"))
a2.set_title(T("控制转矩：启动瞬间最大", "Control torque peaks at the start"), fontsize=10)
clean(a2)
fig.tight_layout()
figure(fig, "fig20_7_1")
