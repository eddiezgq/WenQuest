"""算例 9.5.1～9.5.3：一维卡尔曼滤波。

AGV 沿直线通道行驶，采样周期 Δt = 0.1 s，里程计给出的速度 u = 0.5 m/s。
过程模型 x_k = x_{k−1} + uΔt + w，w ~ 𝒩(0, σ_w²)，σ_w = 0.01 m（每步里程计的误差）；
测量模型 z_k = x_k + v，v ~ 𝒩(0, σ_v²)，σ_v = 0.05 m（超宽带定位）。初值 x̂₀ = 0，P₀ = 0.2² m²（真实起点 0.15 m）。
9.5.1 前三步的手算：预测、增益、更新。
9.5.2 100 步（10 s）的仿真：只用里程计、只用测量、卡尔曼滤波三者的均方根误差；
      卡尔曼滤波在最后一步的估计与“把全部里程计和测量一起做加权最小二乘”的结果一致（两种算法）。
9.5.3 稳态：P、K 收敛到式 (9.5.8)、(9.5.9) 的值；2000 次蒙特卡洛，误差的样本方差与 P_k 一致（滤波器“说的”与“实际的”相符）。
"""
import math

import numpy as np

from bookout import out

dt, u = 0.1, 0.5
sw, sv = 0.01, 0.05
q, r = sw ** 2, sv ** 2
x0_true, xhat0, P0 = 0.15, 0.0, 0.2 ** 2
N = 100


def kalman(z, xh=xhat0, P=P0):
    xs, Ps, Ks, Pm = [], [], [], []
    for k in range(len(z)):
        xm = xh + u * dt                 # 式 (9.5.3)
        Pmk = P + q                      # 式 (9.5.4)
        K = Pmk / (Pmk + r)              # 式 (9.5.5)
        xh = xm + K * (z[k] - xm)        # 式 (9.5.6)
        P = (1 - K) * Pmk                # 式 (9.5.7)
        xs.append(xh)
        Ps.append(P)
        Ks.append(K)
        Pm.append(Pmk)
    return np.array(xs), np.array(Ps), np.array(Ks), np.array(Pm)


def simulate(rng):
    x = np.empty(N + 1)
    x[0] = x0_true
    w = sw * rng.standard_normal(N)
    v = sv * rng.standard_normal(N)
    for k in range(N):
        x[k + 1] = x[k] + u * dt + w[k]
    z = x[1:] + v
    return x, z


rng = np.random.default_rng(905)
x, z = simulate(rng)
xs, Ps, Ks, Pm = kalman(z)

# ---------------------------------------------------------------- 算例 9.5.1 前三步
steps = []
xh, P = xhat0, P0
for k in range(3):
    xm, Pmk = xh + u * dt, P + q
    K = Pmk / (Pmk + r)
    xh, P = xm + K * (z[k] - xm), (1 - K) * Pmk
    steps.append((xm, Pmk, K, z[k], xh, P))
assert abs(steps[2][4] - xs[2]) < 1e-15

# ---------------------------------------------------------------- 算例 9.5.2 三种做法的误差
odo = xhat0 + u * dt * np.arange(1, N + 1)          # 只用里程计（航位推算）
e_odo = odo - x[1:]
e_z = z - x[1:]
e_kf = xs - x[1:]
rms = lambda e: float(np.sqrt(np.mean(e ** 2)))
half = slice(N // 2, N)                            # 后 50 步（滤波已稳定）
rms_odo, rms_z, rms_kf = rms(e_odo[half]), rms(e_z[half]), rms(e_kf[half])
assert rms_kf < rms_z < rms_odo

# 两种算法：把未知的 x_0 … x_N 全部当作未知量，做一次加权最小二乘（定理 9.4.2）
n = N + 1
rows, rhs, wts = [], [], []
e0 = np.zeros(n)
e0[0] = 1
rows.append(e0); rhs.append(xhat0); wts.append(1 / P0)               # 初值的先验
for k in range(1, n):
    a = np.zeros(n)
    a[k], a[k - 1] = 1, -1
    rows.append(a); rhs.append(u * dt); wts.append(1 / q)            # 里程计：x_k − x_{k−1} = uΔt
    b = np.zeros(n)
    b[k] = 1
    rows.append(b); rhs.append(z[k - 1]); wts.append(1 / r)          # 测量：x_k = z_k
A = np.array(rows)
W = np.diag(wts)
batch = np.linalg.solve(A.T @ W @ A, A.T @ W @ np.array(rhs))
covb = np.linalg.inv(A.T @ W @ A)
assert abs(batch[-1] - xs[-1]) < 1e-12 and abs(covb[-1, -1] - Ps[-1]) < 1e-15

# ---------------------------------------------------------------- 算例 9.5.3 稳态与一致性
Pm_inf = (q + math.sqrt(q * q + 4 * q * r)) / 2      # 式 (9.5.8)
K_inf = Pm_inf / (Pm_inf + r)                        # 式 (9.5.9)
P_inf = (1 - K_inf) * Pm_inf
assert abs(Ks[-1] - K_inf) < 1e-9 and abs(Ps[-1] - P_inf) < 1e-12
k_conv = int(np.argmax(np.abs(Ks - K_inf) < 0.01 * K_inf)) + 1        # K 进入稳态值 1% 以内的步数
R = 2000
E = np.empty((R, N))
rng2 = np.random.default_rng(9051)
for i in range(R):
    xi, zi = simulate(rng2)
    E[i] = kalman(zi)[0] - xi[1:]
var_mc = E.var(axis=0, ddof=1)
nees = float(np.mean(E[:, -1] ** 2 / Ps[-1]))
assert abs(var_mc[-1] / Ps[-1] - 1) < 0.08 and abs(var_mc[0] / Ps[0] - 1) < 0.08
assert abs(np.mean(E[:, -1])) < 4 * math.sqrt(Ps[-1] / R)            # 无偏

out(dt=dt, u=u, sw=sw, sv=sv, q=q, r=r, P0=P0, x0_true=x0_true, N=N,
    s1_xm=steps[0][0], s1_Pm=steps[0][1], s1_K=steps[0][2], s1_z=steps[0][3], s1_x=steps[0][4], s1_P=steps[0][5],
    s1_sd=math.sqrt(steps[0][5]),
    s2_xm=steps[1][0], s2_Pm=steps[1][1], s2_K=steps[1][2], s2_z=steps[1][3], s2_x=steps[1][4], s2_P=steps[1][5],
    s3_K=steps[2][2], s3_x=steps[2][4], s3_sd=math.sqrt(steps[2][5]),
    rms_odo=rms_odo * 1000, rms_z=rms_z * 1000, rms_kf=rms_kf * 1000, odo_end=abs(e_odo[-1]) * 1000,
    odo_sd_end=math.sqrt(N) * sw * 1000,
    Pm_inf=Pm_inf, K_inf=K_inf, P_inf=P_inf, sd_inf=math.sqrt(P_inf) * 1000, sdm_inf=math.sqrt(Pm_inf) * 1000,
    K_end=Ks[-1], k_conv=k_conv, R=R, ratio_mc=var_mc[-1] / Ps[-1], nees=nees, sd_mc=math.sqrt(var_mc[-1]) * 1000,
    batch_end=batch[-1], kf_end=xs[-1], nb=n,
    gain_ratio=sv / sw)
