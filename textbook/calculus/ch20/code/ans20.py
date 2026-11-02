"""第 20 章部分习题答案中的数值。"""
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from bookout import out

# 20.1.6：碳纤维管
ro, ri, L, E, F = 0.010, 0.0085, 0.3, 120e9, 9.81
I = math.pi / 4 * (ro ** 4 - ri ** 4)
out(e2016=F * L ** 3 / (3 * E * I) * 1000)
# 20.3.3
z = 0.2
out(e2033=math.exp(2 * math.pi * z / math.sqrt(1 - z * z)))
# 20.3.4
wn = math.sqrt(2e4 / 0.5129)
out(e2034_k=wn * math.sqrt(2) / (2 * math.pi), e2034_J=wn / math.sqrt(1.5) / (2 * math.pi))
# 20.5.3
out(e2053=(30 ** 2 + 20 ** 2) / (30 ** 2 - 20 ** 2) * 10, e2053_b=20 * math.sqrt(5))
# 20.6.1、20.6.2
d = math.log(2.0 / 0.5) / 5
out(e2061=d / math.sqrt(4 * math.pi ** 2 + d * d))
wn2, z2, r2 = 20.0, 0.1, 0.75
M = 1 / math.sqrt((1 - r2 * r2) ** 2 + (2 * z2 * r2) ** 2)
out(e2062_X=10 / 800 * M * 1000, e2062_ph=math.degrees(math.atan2(2 * z2 * r2, 1 - r2 * r2)))
# 20.6.4
Ja, Jr = 0.5129, 137e-7 * 101 ** 2
mu = 1 / Ja + 1 / Jr
out(e2064_deg=math.degrees(math.sqrt(8e4 * mu) / (101 * 6)), e2064_urad=0.02 * 0.187 * 101 / (Jr * 8e4 * mu) / (2 * 0.02) * 1e6)
# 20.7.4：负载时的增益用于空载
J0, b = 0.5129 + 137e-7 * 101 ** 2, 0.5
Jl = J0 + 2 * 0.425 ** 2
Kp, Kd = Jl * 100, 14 * Jl - b
s = solve_ivp(lambda t, y: [y[1], (Kp * (0.5 - y[0]) - Kd * y[1] - b * y[1]) / J0], (0, 2), [0, 0], t_eval=np.linspace(0, 2, 4001), max_step=1e-3)
q = s.y[0]
band = np.abs(q - q[-1]) > 0.01
out(e2074_Kp=Kp, e2074_Kd=Kd, e2074_z=(b + Kd) / (2 * math.sqrt(Kp * J0)), e2074_over=max((q.max() - 0.5) / 0.5 * 100, 0),
    e2074_ts=float(s.t[np.nonzero(band)[0][-1] + 1]))
# 20.7.5：重力下误差 0.05 rad
mgd = 8.393 * 9.81 * 0.2125
Kp5 = mgd * math.cos(0.45) / 0.05
out(e2075_Kp=Kp5, e2075_wn=math.sqrt(Kp5 / J0), e2075_tau0=Kp5 * 0.5)
