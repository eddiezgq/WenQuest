"""16.3 节：稳定性与特征值的实部。
(1) 二阶系统的六种相图：由迹 τ 与行列式 Δ 判断（结点、鞍点、焦点、中心、退化结点、星形结点）；
(2) PD 控制的关节 θ̈ + K_dθ̇ + K_pθ = 0：K_p > 0 且 K_d > 0 时稳定；阻尼比 ζ = K_d/(2√K_p)；
(3) 倒立摆（均匀杆长 l = 0.5 m，绕底端转）：线性化 θ̈ = (3g/2l)θ + u/J，特征值 ±√(3g/2l)，鞍点；PD 反馈使它稳定的条件；
(4) 网球拍定理：手机大小的薄板（0.15 × 0.075 × 0.008 m，0.2 kg）绕三个主轴自旋 2 r/s，在欧拉方程的线性化中，
    绕中间主轴的特征值为一正一负（不稳定），其余两根轴为纯虚数（中心）；非线性仿真：绕中间轴自旋的薄板每隔一段时间翻转一次；
"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import out, vec


def kind(A):
    tau, det = np.trace(A), np.linalg.det(A)
    disc = tau ** 2 - 4 * det
    if det < 0:
        return "saddle"
    if abs(tau) < 1e-12:
        return "center"
    if disc < -1e-12:
        return "focus"
    return "node"


cases = {"node": [[-3.0, 1], [1, -3]], "saddle": [[1.0, 2], [2, 1]], "focus": [[-1.0, 4], [-4, -1]],
         "center": [[0.0, 2], [-2, 0]], "unode": [[2.0, 1], [0, 1]], "ufocus": [[0.5, -3], [3, 0.5]]}
for k, A in cases.items():
    A = np.array(A)
    ev = np.linalg.eigvals(A)
    out(**{f"ev_{k}": ", ".join((f"{z.real:g}" if abs(z.imag) < 1e-12 else f"{z.real:g} {'+' if z.imag > 0 else '−'} {abs(z.imag):g}\\mathrm i") for z in sorted(ev, key=lambda z: (z.real, z.imag))),
           f"tau_{k}": float(np.trace(A)), f"det_{k}": float(np.linalg.det(A)), f"kind_{k}": kind(A)})
# (2) PD 关节
for name, kp, kd in (("a", 100, 4), ("b", 100, 20), ("c", 100, 40)):
    A = np.array([[0.0, 1], [-kp, -kd]])
    ev = np.linalg.eigvals(A)
    out(**{f"pd_ev_{name}": ", ".join((f"{z.real:.2f}" if abs(z.imag) < 1e-9 else f"{z.real:.0f} {'+' if z.imag > 0 else '−'} {abs(z.imag):.2f}\\mathrm i") for z in sorted(ev, key=lambda z: (z.real, z.imag))[:1]).replace(" − ", "\\pm") if abs(ev[0].imag) > 1e-9 else ", ".join(f"{z.real:.2f}" for z in sorted(ev, key=lambda z: z.real)),
           f"pd_zeta_{name}": kd / (2 * math.sqrt(kp)), f"pd_ts_{name}": 4 / min(-ev.real)})
# (3) 倒立摆
g, l, m = 9.81, 0.5, 1.0
J = m * l ** 2 / 3
a = m * g * l / 2 / J                    # = 3g/(2l)
out(a_inv=a, s_inv=math.sqrt(a), t_double=math.log(2) / math.sqrt(a))
# PD：u = −K_pθ − K_dθ̇，A = [[0, 1], [a − K_p/J, −K_d/J]]
kp_min = a * J
out(J=J, kp_min=kp_min)
for name, kp, kd in (("no", 2.0, 0.5), ("lo", 3.0, 0.5), ("hi", 6.0, 0.5)):
    A = np.array([[0.0, 1], [a - kp / J, -kd / J]])
    out(**{f"inv_ev_{name}": vec(np.sort(np.linalg.eigvals(A).real), 2) if np.all(np.abs(np.linalg.eigvals(A).imag) < 1e-9)
           else f"{np.linalg.eigvals(A)[0].real:.2f}\\pm{abs(np.linalg.eigvals(A)[0].imag):.2f}\\mathrm i",
           f"inv_stab_{name}": bool(np.all(np.linalg.eigvals(A).real < 0))})
# (4) 网球拍定理
mass, a_, b_, c_ = 0.2, 0.15, 0.075, 0.008
I = np.array([mass * (b_ ** 2 + c_ ** 2) / 12, mass * (a_ ** 2 + c_ ** 2) / 12, mass * (a_ ** 2 + b_ ** 2) / 12])
w0 = 2 * 2 * math.pi
out(I=vec(I * 1e6, 1))
names = ["x", "y", "z"]
for i in range(3):
    j, k = [n for n in range(3) if n != i]
    # 绕 i 轴以 w0 自旋，扰动 (ω_j, ω_k)：I_j ω̇_j = (I_k − I_i) ω_k ω_i，I_k ω̇_k = (I_i − I_j) ω_i ω_j
    Al = w0 * np.array([[0, (I[k] - I[i]) / I[j]], [(I[i] - I[j]) / I[k], 0]])
    ev = np.linalg.eigvals(Al)
    out(**{f"spin_ev_{names[i]}": (vec(np.sort(ev.real), 2) if np.all(np.abs(ev.imag) < 1e-9)
                                   else f"\\pm{abs(ev[0].imag):.2f}\\mathrm i"), f"spin_rate_{names[i]}": float(max(ev.real))})


def euler(t, w):
    return [(I[1] - I[2]) / I[0] * w[1] * w[2], (I[2] - I[0]) / I[1] * w[2] * w[0], (I[0] - I[1]) / I[2] * w[0] * w[1]]


sol = solve_ivp(euler, (0, 6), [1e-3, w0, 1e-3], rtol=1e-10, atol=1e-12, max_step=0.005)
wy = sol.y[1]
flips = sol.t[np.nonzero(np.diff(np.sign(wy)))[0]]
out(flip1=float(flips[0]), flip_period=float(np.diff(flips).mean() * 2) if len(flips) > 1 else 0.0, nflips=int(len(flips)))
# 能量与角动量守恒（检验积分）
Ek = 0.5 * (I * sol.y.T ** 2).sum(1)
out(Ek_drift=float(abs(Ek[-1] / Ek[0] - 1)))
