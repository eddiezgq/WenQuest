"""21.4 节：平衡点与稳定性；线性化。单摆两个平衡点的雅可比矩阵与特征值；自平衡机器人（倒立摆，m = 5 kg，
质心高 0.4 m，简化为绕支点转动）在 PD 控制下的稳定条件、增益设计，以及转矩限幅时能救回的最大倾角；
PID 控制的关节（20.7 节的参数）：三阶特征多项式的稳定条件与积分增益的上限（公式与二分法）。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import out

g, l = 9.81, 0.5
for th, key in ((0.0, "bot"), (math.pi, "top")):
    Jm = np.array([[0, 1], [-g / l * math.cos(th), 0]])
    ev = np.linalg.eigvals(Jm)
    out(**{f"pe_{key}_re": float(max(ev.real)), f"pe_{key}_im": float(max(ev.imag))})

# 自平衡机器人：m l² θ″ = m g l sin θ − Kp θ − Kd θ′
m, h = 5.0, 0.4
I, mgl = m * h * h, m * g * h
wn, z = 8.0, 0.7
Kp = I * wn * wn + mgl
Kd = 2 * z * wn * I
out(bal_I=I, bal_mgl=mgl, bal_Kp=Kp, bal_Kd=Kd, bal_up=math.sqrt(mgl / I))
Tmax = 15.0


def recovers(th0):
    def rhs(t, y):
        tau = max(-Tmax, min(Tmax, -Kp * y[0] - Kd * y[1]))
        return [y[1], (mgl * math.sin(y[0]) + tau) / I]
    ev = lambda t, y: abs(y[0]) - math.pi / 2
    ev.terminal = True
    s = solve_ivp(rhs, (0, 5), [th0, 0.0], events=ev, max_step=1e-3, rtol=1e-9, atol=1e-11)
    return s.status == 0 and abs(s.y[0, -1]) < 1e-3


lo, hi = 0.01, 1.5
for _ in range(40):
    mid = (lo + hi) / 2
    if recovers(mid):
        lo = mid
    else:
        hi = mid
out(bal_Tmax=Tmax, bal_thmax_deg=math.degrees(lo), bal_th_static_deg=math.degrees(math.asin(Tmax / mgl)))

# PID 关节（竖直平面，目标 0.5 rad）：在目标处线性化，重力贡献刚度 −mgd sin q_ref，
# 特征多项式 J s³ + B s² + (Kp − mgd sin q_ref) s + Ki，B = b + Kd
J = 0.5129 + 137e-7 * 101 ** 2
B = 2 * 0.7 * 10 * J
Kp0 = J * 100
mgd = 8.393 * 9.81 * 0.2125
kg = mgd * math.sin(0.5)
Kpj = Kp0 - kg
Ki_max = B * Kpj / J
Ki_max0 = B * Kp0 / J


def stable(Ki):
    return bool(np.all(np.roots([J, B, Kpj, Ki]).real < 0))


lo, hi, n = 0.0, 5000.0, 0
while hi - lo > 1e-6:
    mid = (lo + hi) / 2
    n += 1
    if stable(mid):
        lo = mid
    else:
        hi = mid
out(pid_kg=kg, pid_Kp0=Kp0, pid_Kimax0=Ki_max0, pid_J=J, pid_B=B, pid_Kp=Kpj, pid_Kimax=Ki_max, pid_Kimax_bis=lo, pid_nbis=n, pid_wosc=math.sqrt(Kpj / J))
r = np.roots([J, B, Kpj, 0.5 * Ki_max])
out(pid_half_maxre=float(max(r.real)))
