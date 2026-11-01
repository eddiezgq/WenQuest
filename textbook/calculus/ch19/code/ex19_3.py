"""19.3 节：可分离变量的方程。清洁机器人水箱流空的时间与流出一半水所需的时间（与数值解比较）；
逻辑斯谛方程的解与拐点；2.6 节架空电缆的悬链线（垂度、端点张力、减小垂度所需的张力）。"""
import math

from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from bookout import out

g = 9.81
# 水箱：h′ = −c√h
A, d, Cd, h0 = 0.03, 4e-3, 0.6, 0.2
c = Cd * math.pi * d * d / 4 * math.sqrt(2 * g) / A
T = 2 * math.sqrt(h0) / c
t_half = T * (1 - 1 / math.sqrt(2))                    # 水深降到 h0/2（体积一半）
s = solve_ivp(lambda t, h: [-c * math.sqrt(max(h[0], 0))], (0, T * 1.2), [h0], rtol=1e-10, atol=1e-12,
              events=lambda t, h: h[0] - 1e-9)
out(tk_T=T, tk_Tmin=T / 60, tk_half=t_half, tk_half_pct=100 * t_half / T, tk_T_num=float(s.t_events[0][0]))
# 若要流量恒定（保持初始流量），6 L 只需多久
q0 = Cd * math.pi * d * d / 4 * math.sqrt(2 * g * h0)
out(tk_T_const=A * h0 / q0, tk_ratio=T / (A * h0 / q0))

# 悬链线：2.6 节的架空电缆，立柱相距 2L = 20 m，a = T0/w = 25 m；设电缆每米质量 0.2 kg
L, a, lam = 10.0, 25.0, 0.2
w = lam * g
T0 = a * w
sag = a * (math.cosh(L / a) - 1)
out(cab_w=w, cab_T0=T0, cab_sag=sag, cab_Tmax=T0 * math.cosh(L / a), cab_sag_par=w * (2 * L) ** 2 / (8 * T0))
# 垂度要求不超过 0.5 m 时需要的水平张力
T0_req = brentq(lambda T0_: T0_ / w * (math.cosh(L / (T0_ / w)) - 1) - 0.5, 10, 1e4)
out(cab_T0_req=T0_req, cab_T0_req_par=w * (2 * L) ** 2 / (8 * 0.5))

# 逻辑斯谛：P′ = rP(1 − P/K)，K = 1000，r = 0.5，P0 = 10：到达 K/2 的时间与拐点
K, r, P0 = 1000.0, 0.5, 10.0
t_half_K = math.log((K - P0) / P0) / r
out(lg_K=K, lg_r=r, lg_P0=P0, lg_t_half=t_half_K, lg_rate_max=r * K / 4, lg_P10=K / (1 + (K - P0) / P0 * math.exp(-r * 10)))
