"""19.1 节：用微分方程建模。maxon RE 40（148877，48 V）的一阶模型：τ = RJ/k²、ω∞ = V/k，与样本数据比较；
清洁机器人水箱的托里拆利模型（h′ = −c√h）与它的非唯一性；指数函数验证。"""
import math

from bookout import out

# maxon RE 40，型号 148877（厂家样本，2026 年查阅）
V, R, Lw, k, J = 48.0, 1.13, 0.33e-3, 60.3e-3, 137e-7       # V、Ω、H、N·m/A、kg·m²（137 g·cm²）
tau = R * J / k ** 2
w_inf = V / k
out(re_V=V, re_R=R, re_k_mNm=k * 1000, re_J_gcm2=137, re_tau_cat=4.28, re_n0_cat=7590, re_L_mH=0.33)
out(re_tau_ms=tau * 1000, re_winf=w_inf, re_winf_rpm=w_inf * 60 / (2 * math.pi), re_tau_e_ms=Lw / R * 1000,
    re_alpha0=w_inf / tau, re_kV=k)
# 启动瞬间的电流与转矩（堵转电流）：i = V/R
out(re_i0=V / R, re_T0=k * V / R)
# t = τ、3τ、5τ 时的转速
out(re_w_tau=w_inf * (1 - math.exp(-1)), re_w_3tau=w_inf * (1 - math.exp(-3)), re_t5_ms=5 * tau * 1000)

# 清洁机器人水箱：截面积 A，出水孔直径 d，流量系数 Cd，h′ = −c√h，c = Cd·a·√(2g)/A
g = 9.81
A, d, Cd, h0 = 0.03, 4e-3, 0.6, 0.2
a = math.pi * d * d / 4
c = Cd * a * math.sqrt(2 * g) / A
T_empty = 2 * math.sqrt(h0) / c
out(tk_A=A, tk_d_mm=d * 1000, tk_Cd=Cd, tk_h0=h0, tk_c=c, tk_T=T_empty, tk_Tmin=T_empty / 60, tk_V_L=A * h0 * 1000,
    tk_q0=Cd * a * math.sqrt(2 * g * h0) * 1000 * 60)                     # 初始流量 L/min
