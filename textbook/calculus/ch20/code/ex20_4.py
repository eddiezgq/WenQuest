"""20.4 节：非齐次方程。PD 控制关节的阶跃响应（ζ = 0.6，ω_n = 10 rad/s，与第 5、10 章相同）：公式与数值解；
无阻尼共振的特解 −t cos ωt/(2ω)；柔性上臂（ω_n、ζ 同 20.3 节）在“先加速后减速”的运动后的残余振动，
由常数变易法（杜阿梅尔积分）计算，并与数值解比较：加速时间是振动周期的整数倍时残余振动消失。"""
import math

import numpy as np
from scipy import integrate
from scipy.integrate import solve_ivp

from bookout import out

# PD 阶跃响应
z, wn = 0.6, 10.0
wd = wn * math.sqrt(1 - z * z)
q = lambda t: 1 - math.exp(-z * wn * t) * (math.cos(wd * t) + z / math.sqrt(1 - z * z) * math.sin(wd * t))
s = solve_ivp(lambda t, y: [y[1], wn * wn * (1 - y[0]) - 2 * z * wn * y[1]], (0, 1), [0, 0], rtol=1e-11, atol=1e-13, dense_output=True)
out(st_q03=q(0.3), st_q03_num=float(s.sol(0.3)[0]), st_wd=wd)

# 共振：y″ + 4y = sin 2t，y(0) = y′(0) = 0 → y = (sin 2t − 2t cos 2t)/8
s = solve_ivp(lambda t, y: [y[1], math.sin(2 * t) - 4 * y[0]], (0, 10), [0, 0], rtol=1e-11, atol=1e-13)
out(rs_num=float(s.y[0, -1]), rs_formula=(math.sin(20) - 20 * math.cos(20)) / 8)

# 柔性上臂的残余振动：φ″ + 2ζω φ′ + ω² φ = −α(t)，α = +α0（0～T），−α0（T～2T）
J, k, zz = 0.5129, 2e4, 0.02
w = math.sqrt(k / J)
wdd = w * math.sqrt(1 - zz * zz)
Tn = 2 * math.pi / w
a0 = 10.0
out(rv_w=w, rv_Tn_ms=Tn * 1000, rv_a0=a0)


def resid(T):
    al = lambda t: a0 if t < T else (-a0 if t < 2 * T else 0.0)
    # 杜阿梅尔积分（常数变易法）：φ(t) = −(1/ω_d) ∫0^t e^{−ζω(t−s)} sin ω_d(t−s) α(s) ds
    h = lambda u: math.exp(-zz * w * u) * math.sin(wdd * u) / wdd
    tend = 2 * T

    def phi(t):
        pts = [p for p in (T, 2 * T) if p < t]
        return -integrate.quad(lambda s_: h(t - s_) * al(s_), 0, t, points=pts or None, limit=400)[0]

    def dphi(t, dt=1e-6):
        return (phi(t + dt) - phi(t - dt)) / (2 * dt)

    p, v = phi(tend), dphi(tend)
    amp = math.sqrt(p * p + ((v + zz * w * p) / wdd) ** 2)            # 停止后自由振动的幅值
    sn = solve_ivp(lambda t, y: [y[1], -al(t) - 2 * zz * w * y[1] - w * w * y[0]], (0, tend), [0, 0], rtol=1e-11, atol=1e-14,
                   max_step=Tn / 50)
    pn, vn = sn.y[0, -1], sn.y[1, -1]
    ampn = math.sqrt(pn * pn + ((vn + zz * w * pn) / wdd) ** 2)
    return amp, ampn


rows = []
for frac in (0.5, 0.75, 1.0, 1.5, 2.0, 3.0):
    T = frac * Tn
    amp, ampn = resid(T)
    rows.append(f"| {T * 1000:.1f} | {frac:g} | {amp * 1e6:.1f} | {ampn * 1e6:.1f} | {amp * 0.425 * 1e6:.1f} |")
out(rv_tab="\n".join(rows), rv_static_urad=a0 / w ** 2 * 1e6, rv_max_urad=4 * a0 / w ** 2 * 1e6)
