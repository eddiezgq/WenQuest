"""20.2 节：线性方程解的结构。起重机器人提升吊重时的摆动 l θ″ + 2 l′ θ′ + g θ = 0（变系数线性方程）：
两个解的朗斯基行列式与阿贝尔公式 W = W0 (l0/l)² 比较；摆角幅值随绳长缩短而增大。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import out

g, l0, v, T = 9.81, 4.0, 0.3, 10.0          # 绳长 4 m，以 0.3 m/s 收绳，10 s
l = lambda t: l0 - v * t
dl = -v


def rhs(t, z):
    th, w = z
    return [w, -(2 * dl * w + g * th) / l(t)]


ts = np.linspace(0, T, 20001)
s1 = solve_ivp(rhs, (0, T), [1.0, 0.0], t_eval=ts, rtol=1e-11, atol=1e-13)
s2 = solve_ivp(rhs, (0, T), [0.0, 1.0], t_eval=ts, rtol=1e-11, atol=1e-13)
W = s1.y[0] * s2.y[1] - s1.y[1] * s2.y[0]
W_abel = (l0 / l(ts)) ** 2
out(cr_l0=l0, cr_v=v, cr_T=T, cr_l1=l(T), cr_W_end=float(W[-1]), cr_W_abel=float(W_abel[-1]),
    cr_W_err=float(np.max(np.abs(W - W_abel) / W_abel)))
# 摆角幅值：初始 0.05 rad 静止释放，比较开头一个周期与最后一个周期的最大摆角
th = 0.05 * s1.y[0]
P0, P1 = 2 * math.pi * math.sqrt(l0 / g), 2 * math.pi * math.sqrt(l(T) / g)
a0 = float(np.max(np.abs(th[ts <= P0])))
a1 = float(np.max(np.abs(th[ts >= T - P1])))
out(cr_a0=a0, cr_a1=a1, cr_ratio=a1 / a0, cr_pred=(l0 / l(T)) ** 0.75)
