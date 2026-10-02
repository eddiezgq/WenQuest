"""7.4 节的算例（数值微分与刚性问题）。

算例 7.4.1：用差商求 sin t 在 t = 1 处的导数，h 从 10⁻¹ 取到 10⁻¹⁵：截断误差与舍入误差此消彼长，
            前向差商与中心差商各有一个最佳步长。
算例 7.4.2：编码器测速。关节按 θ(t) = A sin Ωt 运动（A = 2 rad，Ω = 2π rad/s），16384 线/转（四倍频后）的
            编码器以 1 kHz 采样。用跨度 h = n × 1 ms 的后向差商估计角速度，求均方根误差最小的 h，并与理论估计核对。
算例 7.4.3：带电流环和速度环的关节电机：状态 (i, ω) 的线性方程，两个特征值相差数百倍（刚性）。
            显式欧拉法的稳定步长上限；隐式欧拉法 h = 1 ms 的结果与精确解（矩阵指数）比较；隐式欧拉法的阶。
另：非线性单摆的隐式欧拉法，每步用牛顿法解方程；它不会发散，但会人为地耗散能量。
"""
import math

import numpy as np
from scipy.linalg import expm

from _ode import MOTOR, link_params, pend_energy
from bookout import out

# ---------------------------------------------------------------- 算例 7.4.1
t0 = 1.0
d_true = math.cos(t0)
ks = np.arange(1, 16)
fw = np.array([abs((math.sin(t0 + 10.0 ** -k) - math.sin(t0)) / 10.0 ** -k - d_true) for k in ks])
ce = np.array([abs((math.sin(t0 + 10.0 ** -k) - math.sin(t0 - 10.0 ** -k)) / (2 * 10.0 ** -k) - d_true) for k in ks])
k_fw, k_ce = int(ks[np.argmin(fw)]), int(ks[np.argmin(ce)])
eps = np.finfo(float).eps
assert 7 <= k_fw <= 9 and 4 <= k_ce <= 6                     # 理论：√ε ≈ 1e-8，ε^(1/3) ≈ 6e-6
assert fw[0] / fw[1] > 8 and ce[0] / ce[1] > 80              # 大步长时：前向一阶、中心二阶
h_fw_th = 2 * math.sqrt(eps * abs(math.sin(t0)) / abs(math.sin(t0)))   # 式 (7.4.5)：h* = 2√(ε|f|/|f''|)
h_ce_th = (3 * eps * abs(math.sin(t0)) / abs(math.cos(t0))) ** (1 / 3)   # 中心差商：h* = (3ε|f|/|f'''|)^(1/3)

# ---------------------------------------------------------------- 算例 7.4.2 编码器
A, Om = 2.0, 2 * math.pi
counts = 16384
q = 2 * math.pi / counts                                     # 量化步长，rad
Ts = 1e-3
t = np.arange(0, 2.2, Ts)
theta = A * np.sin(Om * t)
theta_q = np.floor(theta / q) * q                            # 编码器读数：向下取整到整数个计数
w_true = A * Om * np.cos(Om * t)
ns = np.arange(1, 61)
rms = []
start = 100                                                  # 从 0.1 s 起评估（前面没有足够的历史数据）
for n in ns:
    est = (theta_q[start:] - theta_q[start - n:-n]) / (n * Ts)          # 后向差商（式 (7.4.2)）
    rms.append(float(np.sqrt(np.mean((est - w_true[start:]) ** 2))))
rms = np.array(rms)
n_best = int(ns[np.argmin(rms)])
rms_best, rms_1 = float(rms.min()), float(rms[0])
# 理论估计：截断误差的均方根 h AΩ²/(2√2)，量化误差的均方根 q/(√6 h)，平方和最小处
h_th = (8 * q ** 2 / (6 * A ** 2 * Om ** 4)) ** 0.25
rms_th = math.sqrt((h_th * A * Om ** 2 / (2 * math.sqrt(2))) ** 2 + (q / (math.sqrt(6) * h_th)) ** 2)
assert abs(n_best * Ts - h_th) / h_th < 0.35 and abs(rms_best - rms_th) / rms_th < 0.35
q_over_T = q / Ts                                            # 一个计数的变化在 1 ms 内对应的速度
w_amp = A * Om
# 中心差商（需要“未来”的数据，结果要晚 h 才能得到）
rms_c = []
for n in ns:
    est = (theta_q[start + n:len(t) - n] - theta_q[start - n:len(t) - 3 * n]) / (2 * n * Ts)
    rms_c.append(float(np.sqrt(np.mean((est - w_true[start:len(t) - 2 * n]) ** 2))))
n_best_c = int(ns[np.argmin(rms_c)])
rms_best_c = float(min(rms_c))
assert rms_best_c < rms_best

# ---------------------------------------------------------------- 算例 7.4.3 刚性：电流环 + 速度环
m = MOTOR
Kp, Kv = 20.0, 0.04                       # 电流环比例增益 V/A；速度环增益 A/(rad/s)
w_ref = 100.0                             # 转速指令，rad/s
L, R, Kt, Ke, Jm, b = m["L"], m["R"], m["Kt"], m["Ke"], m["Jm"], m["b"]
Am = np.array([[-(R + Kp) / L, -(Ke + Kp * Kv) / L],
               [Kt / Jm, -b / Jm]])
Bm = np.array([Kp * Kv * w_ref / L, 0.0])
lam = np.linalg.eigvals(Am)
lam = lam[np.argsort(np.abs(lam))]
assert np.all(lam.real < 0) and np.allclose(lam.imag, 0)
lam_slow, lam_fast = float(lam[0].real), float(lam[1].real)
ratio = lam_fast / lam_slow
assert ratio > 300
x_eq = -np.linalg.solve(Am, Bm)                              # 稳态
x0 = np.zeros(2)
exact = lambda tt: x_eq + expm(Am * tt) @ (x0 - x_eq)
Tend = 0.1
h_exp_max = 2 / abs(lam_fast)
h_rk4_max = 2.785 / abs(lam_fast)                            # RK4 在负实轴上的稳定区间约为 [−2.785, 0]


def explicit(h, T=Tend):
    x = x0.copy()
    for _ in range(int(round(T / h))):
        x = x + h * (Am @ x + Bm)
    return x


def implicit(h, T=Tend, keep=False):
    x = x0.copy()
    M = np.linalg.inv(np.eye(2) - h * Am)                    # 式 (7.4.10)：(I − hA) x_{k+1} = x_k + h B
    xs = [x.copy()]
    for _ in range(int(round(T / h))):
        x = M @ (x + h * Bm)
        xs.append(x.copy())
    return np.array(xs) if keep else x


def trapezoid(h, T=Tend):
    x = x0.copy()
    I = np.eye(2)
    M = np.linalg.solve(I - h / 2 * Am, I + h / 2 * Am)
    c = np.linalg.solve(I - h / 2 * Am, h * Bm)
    for _ in range(int(round(T / h))):
        x = M @ x + c
    return x


xe = exact(Tend)
ok_exp = explicit(50e-6)
bad_exp = explicit(60e-6)
assert abs(ok_exp[1] - xe[1]) < 0.5 and not np.all(np.abs(bad_exp) < 1e6)
gain_exp_1ms = abs(1 + 1e-3 * lam_fast)                      # 显式欧拉法 h = 1 ms 时快模态的放大因子
imp1 = implicit(1e-3)
err_imp1 = abs(imp1[1] - xe[1])
errs_imp = [abs(implicit(h)[1] - xe[1]) for h in (2e-3, 1e-3, 5e-4)]
r_imp = errs_imp[0] / errs_imp[1]
assert 1.8 < r_imp < 2.2
trap_bad = trapezoid(1e-3)                                   # 梯形法：A-稳定，但快模态以 ≈ −1 的因子振荡衰减
gain_trap = abs((1 + 1e-3 / 2 * lam_fast) / (1 - 1e-3 / 2 * lam_fast))
gain_imp = abs(1 / (1 - 1e-3 * lam_fast))
n_exp = math.ceil(Tend / h_exp_max)
n_imp = int(round(Tend / 1e-3))
# 隐式欧拉法的轨迹（1 ms）与精确解在整个 0.1 s 内的最大差
tr = implicit(1e-3, keep=True)
tt = np.arange(len(tr)) * 1e-3
ex_tr = np.array([exact(s) for s in tt])
max_dw = float(np.abs(tr[:, 1] - ex_tr[:, 1]).max())
# 电流峰值与转速的建立时间：在 1 µs 的细网格上求精确解（1 ms 的网格会漏掉 0.2 ms 处的峰值）
tf = np.arange(0, 1e-3, 1e-6)
i_f = np.array([exact(s)[0] for s in tf])
i_peak = float(i_f.max())
t_peak_ms = float(tf[np.argmax(i_f)] * 1e3)
assert i_peak > ex_tr[:, 0].max() and 0.05 < t_peak_ms < 0.5
tw = np.arange(0, Tend, 1e-5)
w_f = np.array([exact(s)[1] for s in tw])
t95_ms = float(tw[np.argmax(w_f >= 0.95 * x_eq[1])] * 1e3)    # 转速达到稳态值 95% 的时间
assert 2.5 < t95_ms / (-1e3 / lam_slow) < 3.5                  # 约 3 个慢时间常数
w_end = float(xe[1])
tau_slow_ms = -1e3 / lam_slow
tau_fast_us = -1e6 / lam_fast

# ---------------------------------------------------------------- 非线性：单摆的隐式欧拉法 + 牛顿法
Jo, lc, wn2 = link_params()
h = 0.02
x = np.array([math.pi / 2, 0.0])
E0 = float(pend_energy(x, wn2))
newton_its = []
for _ in range(int(round(10 / h))):
    # 未知量 θ⁺：θ⁺ = θ + h ω⁺，ω⁺ = ω − h ω_n² sin θ⁺  ⇒  g(θ⁺) = θ⁺ − θ − h ω + h² ω_n² sin θ⁺ = 0
    th, om = x
    y = th + h * om                                           # 初值：显式预测
    for it in range(1, 20):
        g = y - th - h * om + h * h * wn2 * math.sin(y)
        dy = g / (1 + h * h * wn2 * math.cos(y))
        y -= dy
        if abs(dy) < 1e-13:
            break
    newton_its.append(it)
    x = np.array([y, om - h * wn2 * math.sin(y)])
    assert abs(x[0] - th - h * x[1]) < 1e-12                  # 确实满足隐式方程
E10 = float(pend_energy(x, wn2))
loss_imp = (1 - E10 / E0) * 100
assert 0 < loss_imp < 100
its_max, its_mean = max(newton_its), float(np.mean(newton_its))

out(
    **{f"fw{k}": float(fw[k - 1]) for k in ks}, **{f"ce{k}": float(ce[k - 1]) for k in ks},
    k_fw=k_fw, k_ce=k_ce, fw_best=float(fw.min()), ce_best=float(ce.min()), eps=eps, h_fw_th=h_fw_th, h_ce_th=h_ce_th,
    q=q, q_urad=q * 1e6, counts=counts, q_over_T=q_over_T, w_amp=w_amp, n_best=n_best, h_best_ms=n_best * Ts * 1e3,
    rms_best=rms_best, rms_1=rms_1, rms_1_pct=rms_1 / w_amp * 100, rms_best_pct=rms_best / w_amp * 100,
    h_th_ms=h_th * 1e3, rms_th=rms_th, n_best_c=n_best_c, rms_best_c=rms_best_c,
    Kp=Kp, Kv=Kv, w_ref=w_ref, a11=float(Am[0, 0]), a12=float(Am[0, 1]), a21=float(Am[1, 0]), a22=float(Am[1, 1]), b1=float(Bm[0]), lam_slow=lam_slow, lam_fast=lam_fast, ratio=ratio,
    tau_slow_ms=tau_slow_ms, tau_fast_us=tau_fast_us,
    h_exp_max_us=h_exp_max * 1e6, h_rk4_max_us=h_rk4_max * 1e6, gain_exp_1ms=gain_exp_1ms, n_exp=n_exp, n_imp=n_imp,
    w_exact=w_end, w_imp1=float(imp1[1]), err_imp1=err_imp1, r_imp=r_imp, err_imp2=errs_imp[0], err_imp05=errs_imp[2],
    max_dw=max_dw, i_peak=i_peak, t_peak_ms=t_peak_ms, t95_ms=t95_ms, ok_exp_w=float(ok_exp[1]), gain_trap=gain_trap, gain_imp=gain_imp,
    w_trap=float(trap_bad[1]), i_eq=float(x_eq[0]),
    loss_imp=loss_imp, its_max=its_max, its_mean=its_mean,
)
