"""7.1 节的算例。

算例 7.1.1：差商逼近导数。f(t) = t² 在 t = 1 处，h = 0.1、0.01、0.001 的差商；一阶泰勒近似的误差随 h² 减小。
算例 7.1.2：关节电机的一阶模型 τ ω̇ + ω = K u。由电机参数求时间常数 τ 和增益 K，12 V 阶跃时的稳态转速；
            解析解 (7.1.5) 与高精度数值积分核对。
算例 7.1.3：刹车松开后自由摆动的连杆（单摆）：小角度固有角频率与周期；从水平位置释放时的精确周期
            （椭圆积分）与数值仿真测得的周期核对。
算例 7.1.4：单摆在两个平衡点处线性化：雅可比矩阵的特征值；θ = 0 处的线性解 e^{At}x0 与数值积分核对。
另：无阻尼单摆的能量 (7.1.13) 沿真实轨迹不变。
"""
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import expm

from _ode import MOTOR, G, link_params, motor_first_order, pend_energy, pend_exact_period, pend_f, rk4, run
from bookout import out, tex

# ---------------------------------------------------------------- 算例 7.1.1 差商
f = lambda t: t * t
dq = {h: (f(1 + h) - f(1)) / h for h in (0.1, 0.01, 0.001)}
for h, q in dq.items():
    assert abs(q - (2 + h)) < 1e-9                       # (t² 的差商恰为 2t + h)
# 一阶泰勒近似 e^{h} ≈ 1 + h 的误差：h 减半，误差约变为 1/4
taylor_err = {h: math.exp(h) - (1 + h) for h in (0.2, 0.1, 0.05)}
ratio_taylor = taylor_err[0.1] / taylor_err[0.05]
assert 3.8 < ratio_taylor < 4.2

# ---------------------------------------------------------------- 算例 7.1.2 关节电机
m = MOTOR
tau, K = motor_first_order()
u = 12.0                                                 # 阶跃电压，V
w_inf = K * u                                            # 稳态转速，rad/s
rpm = w_inf * 60 / (2 * math.pi)
frac1 = 1 - math.exp(-1)                                 # t = τ 时达到的比例
frac3 = 1 - math.exp(-3)
den = m["R"] * m["b"] + m["Kt"] * m["Ke"]


def motor_rhs(t, x):                                     # 式 (7.1.3) 整理后：J ω̇ = Kt (u − Ke ω)/R − b ω
    w = x[0]
    i = (u - m["Ke"] * w) / m["R"]
    return np.array([(m["Kt"] * i - m["b"] * w) / m["Jm"]])


t_chk = 0.05
w_exact = w_inf * (1 - math.exp(-t_chk / tau))           # 式 (7.1.5)
w_num = run(rk4, motor_rhs, [0.0], t_chk, 1e-5)[0]
assert abs(w_num - w_exact) < 1e-8 * w_inf
i0 = u / m["R"]                                          # 起动瞬间的电流
i_inf = (u - m["Ke"] * w_inf) / m["R"]
dw0 = w_inf / tau                                        # 起动瞬间的角加速度 = 切线斜率
assert abs(dw0 - motor_rhs(0, [0.0])[0]) < 1e-6 * dw0

# ---------------------------------------------------------------- 算例 7.1.3 连杆单摆
Jo, lc, wn2 = link_params()
wn = math.sqrt(wn2)
T0 = 2 * math.pi / wn                                    # 小角度周期
th0 = math.pi / 2                                        # 从水平位置释放
T_ell = pend_exact_period(wn2, th0)
sol = solve_ivp(pend_f(wn2), (0, 3 * T_ell), [th0, 0.0], method="DOP853", rtol=1e-12, atol=1e-12,
                dense_output=True, events=lambda t, x: x[1])
ev = sol.t_events[0]                                     # θ̇ = 0 的时刻：每半个周期一次
ev = ev[ev > 1e-6]
T_sim = ev[1]                                            # 第二次速度为零：回到出发点，一个周期
assert abs(T_sim - T_ell) < 1e-8
ratio_T = T_ell / T0

# 能量守恒：沿真实轨迹 E 不变
ts = np.linspace(0, 3 * T_ell, 400)
E = pend_energy(sol.sol(ts).T, wn2)
assert np.ptp(E) < 1e-9 * E[0]
v_bottom = math.sqrt(2 * wn2 * (1 - math.cos(th0)))      # 摆到最低点时的角速度，rad/s

# ---------------------------------------------------------------- 算例 7.1.4 线性化
A0 = np.array([[0, 1], [-wn2, 0]])                       # θ = 0 处
Api = np.array([[0, 1], [wn2, 0]])                       # θ = π 处
ev0 = np.linalg.eigvals(A0)
evpi = np.linalg.eigvals(Api)
assert np.allclose(sorted(ev0.imag), [-wn, wn]) and np.allclose(ev0.real, 0)
assert np.allclose(sorted(evpi.real), [-wn, wn])
# 雅可比矩阵由数值求导核对
fp = pend_f(wn2)
eps = 1e-6
for xe, A in (([0.0, 0.0], A0), ([math.pi, 0.0], Api)):
    Jn = np.column_stack([(fp(0, np.array(xe) + eps * e) - fp(0, np.array(xe) - eps * e)) / (2 * eps) for e in np.eye(2)])
    assert np.allclose(Jn, A, atol=1e-6)
# 小角度：线性解 e^{At} x0 与非线性方程的数值解
x0s = np.array([math.radians(5), 0.0])
t1 = 1.0
x_lin = expm(A0 * t1) @ x0s
x_non = run(rk4, fp, x0s, t1, 1e-4)
x_lin_rk = run(rk4, lambda t, x: A0 @ x, x0s, t1, 1e-4)
assert np.allclose(x_lin, x_lin_rk, atol=1e-12)          # 矩阵指数与数值积分一致
lin_gap_deg = math.degrees(abs(x_lin[0] - x_non[0]))     # 线性化带来的差别（5° 时很小）
# 有阻尼：b/J_o = 1 1/s
c = 1.0
Ad = np.array([[0, 1], [-wn2, -c]])
evd = np.linalg.eigvals(Ad)
assert np.allclose(evd.real, -c / 2)

out(
    dq1=dq[0.1], dq2=dq[0.01], dq3=dq[0.001],
    te1=taylor_err[0.1], te2=taylor_err[0.05], ratio_taylor=ratio_taylor,
    tau=tau, tau_ms=tau * 1e3, K=K, den=den, w_inf=w_inf, rpm=rpm, frac1=frac1, frac3=frac3,
    t_chk_ms=t_chk * 1e3, w_chk=w_exact, i0=i0, i_inf=i_inf, dw0=dw0,
    Jo=Jo, lc=lc, wn2=wn2, wn=wn, T0=T0, T_ell=T_ell, T_sim=T_sim, ratio_T=ratio_T, v_bottom=v_bottom,
    E0=float(E[0]), Eptp=float(np.ptp(E)),
    A0=tex(A0, 2), Api=tex(Api, 2), ev_wn=wn, evd_re=float(evd.real[0]), evd_im=float(abs(evd.imag[0])),
    lin_gap_deg=lin_gap_deg, x_lin_deg=math.degrees(x_lin[0]), x_non_deg=math.degrees(x_non[0]),
    g=G,
)
