"""算例 7.3.3：五次多项式运动时，关节驱动转动部分所需的机械功率 P = Iαω 何时最大。
设转动部分（含负载）对转轴的转动惯量 I = 2.0 kg·m²（假设值），关节在 T = 2 s 内转过 Δ = 90°，不计重力和摩擦。"""
import math

import numpy as np

from _traj import quintic
from bookout import out

I, T, D = 2.0, 2.0, math.pi / 2
s_star = 0.5 - math.sqrt(7) / 14            # 14s² − 14s + 3 = 0 的较小根
t_star = s_star * T
_, w, a, _ = quintic(t_star, T, D)
P_star = I * float(a) * float(w)
# 用程序在细网格上找最大值，核对手算
t = np.linspace(0, T, 200001)
_, W, A, _ = quintic(t, T, D)
P = I * A * W
k = int(np.argmax(P))
assert abs(t[k] - t_star) < 1e-4 and abs(P[k] - P_star) < 1e-6
out(s_star=s_star, t_star=t_star, w_star=float(w), a_star=float(a), P_star=P_star,
    P_min=float(P.min()), t_min=float(t[int(np.argmin(P))]), sqrt7_14=math.sqrt(7) / 14)

# 算例 7.3.1：f(x) = (x² + 1)(x³ − 2x) 用乘积法则求导，在 x = 2 处的值，与展开后求导比较
f1 = lambda x: (2 * x) * (x**3 - 2 * x) + (x**2 + 1) * (3 * x**2 - 2)
f2 = lambda x: 5 * x**4 - 3 * x**2 - 2
assert abs(f1(2.0) - f2(2.0)) < 1e-12
out(ex1_val=f1(2.0))
