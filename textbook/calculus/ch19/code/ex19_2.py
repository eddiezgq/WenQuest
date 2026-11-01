"""19.2 节：方向场与解曲线。y′ = x − y 的解 y = x − 1 + Ce^(−x) 与数值解比较；y′ = y² 在有限处跑到无穷；
带风扇负载的 RE 40 电机 ω′ = (ω∞ − ω)/τ − (c/J)ω² 的平衡点（稳态转速）与稳定性。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import out

# y′ = x − y：数值解与公式解在 x = 3 处比较
rows = []
for y0 in (-2.0, -1.0, 0.0, 2.0):
    s = solve_ivp(lambda x, y: x - y, (0, 3), [y0], rtol=1e-10, atol=1e-12)
    exact = 3 - 1 + (y0 + 1) * math.exp(-3)
    rows.append(f"| {y0:g} | {y0 + 1:g} | {exact:.6f} | {s.y[0, -1]:.6f} |")
out(lin_tab="\n".join(rows))
# y′ = y²，y(0) = 1：数值方法在 x → 1 时步长越来越小
s = solve_ivp(lambda x, y: y * y, (0, 2), [1.0], rtol=1e-8, atol=1e-10)
out(blow_x_last=float(s.t[-1]), blow_y_last=float(s.y[0, -1]), blow_ok=bool(s.success), blow_n=int(s.t.size))

# 带风扇的电机：风扇阻力矩 c ω²，c 使稳态电流约为额定电流
V, R, k, J = 48.0, 1.13, 60.3e-3, 137e-7
tau, w_inf = R * J / k ** 2, V / k
cf = 3.3e-7
f = lambda w: (w_inf - w) / tau - cf / J * w * w
# 平衡点：(k²/R)(ω∞ − ω) = c ω²
a, b, c0 = cf, k * k / R, -k * k / R * w_inf
ws = (-b + math.sqrt(b * b - 4 * a * c0)) / (2 * a)
fp = -1 / tau - 2 * cf / J * ws                                   # f′(ω*)
out(fan_c=cf, fan_ws=ws, fan_ws_rpm=ws * 60 / (2 * math.pi), fan_i=(V - k * ws) / R, fan_T=cf * ws * ws * 1000,
    fan_fp=fp, fan_tau_eff_ms=-1000 / fp, fan_tau_ms=tau * 1000)
# 数值验证：从 0 启动与从 900 rad/s 减速都趋于 ω*
for w0, key in ((0.0, "fan_from0"), (900.0, "fan_from900")):
    s = solve_ivp(lambda t, w: f(w), (0, 0.05), [w0], rtol=1e-10, atol=1e-8)
    out(**{key: float(s.y[0, -1])})
ev = lambda t, w: w[0] - 0.95 * ws
s = solve_ivp(lambda t, w: f(w), (0, 0.05), [0.0], rtol=1e-10, atol=1e-8, events=ev)
out(fan_t95=float(s.t_events[0][0]) * 1000)
