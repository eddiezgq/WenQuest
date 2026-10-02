"""7.8 节：三种运动规律的速度、加速度、加加速度；按限速和限加速度选运动时间；用编码器数据求角加速度。"""
import math

import numpy as np
import sympy as sp

from _traj import cubic, quintic, trapezoid
from bookout import out

T, D, ta = 2.0, math.pi / 2, 0.5
t = np.linspace(0, T, 400001)
res = {}
for name, f in (("cub", lambda tt: cubic(tt, T, D)), ("qui", lambda tt: quintic(tt, T, D)), ("tra", lambda tt: trapezoid(tt, T, D, ta))):
    th, w, a, j = f(t)
    res[name] = (float(np.max(np.abs(w))), float(np.max(np.abs(a))), float(np.max(np.abs(j))))
# 两端的极值（t → 0⁺）在网格上取不到，用公式给出，并与网格结果核对
assert abs(res["cub"][1] - 6 * D / T**2) < 1e-4 and abs(res["qui"][2] - 60 * D / T**3) < 1e-3
out(cub_w=res["cub"][0], cub_a=6 * D / T**2, cub_j=12 * D / T**3,
    qui_w=res["qui"][0], qui_a=res["qui"][1], qui_j=60 * D / T**3, qui_jmid=30 * D / T**3,
    tra_w=res["tra"][0], tra_a=res["tra"][1])
assert abs(res["qui"][1] - 10 * D / (math.sqrt(3) * T**2)) < 1e-6
assert abs(res["qui"][0] - 15 * D / (8 * T)) < 1e-9

# 算例 7.8.2：限速 ω_max = π rad/s（180°/s），限角加速度 α_max = 5 rad/s²，五次多项式运动转过 90° 的最短时间
w_lim, a_lim = math.pi, 5.0
T_w = 15 * D / (8 * w_lim)
T_a = math.sqrt(10 * D / (math.sqrt(3) * a_lim))
out(T_w=T_w, T_a=T_a, T_min=max(T_w, T_a), a_lim=a_lim)

# 算例 7.8.1：莱布尼茨公式 (x² eˣ)^(10) = eˣ(x² + 20x + 90)，在 x = 1 处
x = sp.symbols("x")
d10 = sp.diff(x**2 * sp.exp(x), x, 10)
assert sp.simplify(d10 - sp.exp(x) * (x**2 + 20 * x + 90)) == 0
out(leib=float(d10.subs(x, 1)))

# 7.8.5 节：17 位编码器（一圈 2^17 个刻度），采样周期 Ts = 1 ms，五次多项式运动；用二阶中心差商估计角加速度
q = 2 * math.pi / 2**17
Ts = 0.001
tk = np.arange(0, T + Ts / 2, Ts)
thk = np.round(quintic(tk, T, D)[0] / q) * q          # 编码器读数：取整到刻度
a_true = quintic(tk, T, D)[2]
rms = {}
for k in (1, 5, 20, 50):
    h = k * Ts
    est = (thk[2 * k:] - 2 * thk[k:-k] + thk[:-2 * k]) / h**2
    rms[k] = float(np.sqrt(np.mean((est - a_true[k:-k]) ** 2)))
w_rms = {}
for k in (1, 5, 20):
    h = k * Ts
    est = (thk[2 * k:] - thk[:-2 * k]) / (2 * h)
    w_rms[k] = float(np.sqrt(np.mean((est - quintic(tk, T, D)[1][k:-k]) ** 2)))
out(q=q, q_urad=q * 1e6, a_rms1=rms[1], a_rms5=rms[5], a_rms20=rms[20], a_rms50=rms[50],
    w_rms1=w_rms[1], w_rms5=w_rms[5], w_rms20=w_rms[20], a_bound1=q / Ts**2)
