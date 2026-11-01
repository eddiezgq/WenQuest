"""19.7 节：应用。RE 40 绕组温升（单节点模型与双节点模型，厂家热参数）；带收获的逻辑斯谛模型；
电机驱动器直流母线电容的预充电（RC 电路）；RE 40 的一阶模型计入摩擦后与样本空载转速比较；
由带噪声的阶跃响应数据读出时间常数（63.2% 点、切线、半对数拟合、最小二乘）。"""
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar

from bookout import out

# ---------- RE 40 的热模型（厂家样本：Rth1 = 4.65 K/W 外壳–环境，Rth2 = 1.93 K/W 绕组–外壳，
# 绕组热时间常数 41.5 s，电机热时间常数 809 s；最高绕组温度 155 °C；额定电流 3.17 A）
R, Rth1, Rth2, tw, tm, Tmax, In, Ta = 1.13, 4.65, 1.93, 41.5, 809.0, 155.0, 3.17, 25.0
Rth = Rth1 + Rth2
P1 = In ** 2 * R
out(th_Rth=Rth, th_P1=P1, th_dT1=P1 * Rth, th_T1=Ta + P1 * Rth)
# 单节点模型：τ_th dT/dt = P·Rth − (T − Ta)，取电机热时间常数
P2 = (2 * In) ** 2 * R
dT2 = P2 * Rth
t1node = -tm * math.log(1 - (Tmax - Ta) / dT2)
out(th_P2=P2, th_dT2=dT2, th_t1node=t1node)
# 双节点模型：绕组热容 Cw = τw/Rth2，外壳热容 Ch = τm/Rth1（按样本的两个时间常数近似）
Cw, Ch = tw / Rth2, tm / Rth1


def two(t, z, P):
    Tw, Th = z
    return [(P - (Tw - Th) / Rth2) / Cw, ((Tw - Th) / Rth2 - (Th - Ta) / Rth1) / Ch]


ev = lambda t, z, P: z[0] - Tmax
ev.terminal = True
s = solve_ivp(two, (0, 5000), [Ta, Ta], args=(P2,), events=ev, max_step=1.0)
out(th_t2node=float(s.t_events[0][0]), th_Cw=Cw, th_Ch=Ch)
s = solve_ivp(two, (0, 20000), [Ta, Ta], args=(P1,), max_step=5.0)
out(th_T1_2node=float(s.y[0, -1]))

# ---------- 带收获的逻辑斯谛模型：P′ = rP(1 − P/K) − H
K, r = 1000.0, 0.5
Hmax = r * K / 4
H = 100.0
dsc = math.sqrt(1 - 4 * H / (r * K))
out(hv_K=K, hv_Hmax=Hmax, hv_H=H, hv_lo=K / 2 * (1 - dsc), hv_hi=K / 2 * (1 + dsc))

# ---------- 直流母线电容预充电：C = 1000 μF，48 V，预充电电阻 47 Ω；不加电阻时回路电阻约 0.05 Ω
C, V, Rp, Rw = 1000e-6, 48.0, 47.0, 0.05
tau_p = Rp * C
E_R = 0.5 * C * V * V
# 数值核对：电阻上消耗的能量 ∫ i²R dt
tt = np.linspace(0, 20 * tau_p, 200001)
i = V / Rp * np.exp(-tt / tau_p)
out(pc_tau_ms=tau_p * 1000, pc_i0=V / Rp, pc_i0_wire=V / Rw, pc_t95_ms=3 * tau_p * 1000, pc_E=E_R,
    pc_E_num=float(np.trapezoid(i * i * Rp, tt)), pc_E_cap=E_R)

# ---------- RE 40 的一阶模型计入摩擦：空载电流 I0 = 68.6 mA 对应摩擦转矩 k·I0
k, J, L = 60.3e-3, 137e-7, 0.33e-3
I0 = 68.6e-3
Tf = k * I0
w_inf_f = (48 - R * I0) / k
out(mf_Tf=Tf * 1000, mf_winf=w_inf_f, mf_rpm=w_inf_f * 60 / (2 * math.pi), mf_rpm_cat=7590, mf_I0=I0 * 1000)

# ---------- 由阶跃响应数据读时间常数：用含电感的二阶模型生成“实测”数据，采样 0.25 ms，噪声 σ = 5 rad/s
rng = np.random.default_rng(19)


def motor2(t, z):
    w, i_ = z
    return [(k * i_ - Tf) / J, (48 - R * i_ - k * w) / L]


ts = np.arange(0, 0.03 + 1e-12, 0.25e-3)
s = solve_ivp(motor2, (0, 0.03), [0.0, 0.0], t_eval=ts, rtol=1e-9, atol=1e-9, max_step=2e-5)
w_true = s.y[0]
w_meas = w_true + 5.0 * rng.standard_normal(ts.size)
w_end = float(np.mean(w_meas[ts > 0.025]))
# (a) 63.2% 点：第一次超过 0.632 ω∞ 的时刻（线性插值）
j = int(np.argmax(w_meas > 0.632 * w_end))
t63 = ts[j - 1] + (0.632 * w_end - w_meas[j - 1]) / (w_meas[j] - w_meas[j - 1]) * (ts[j] - ts[j - 1])
# (b) 半对数法：用 0.5 ms 以后、90% 以前的数据拟合 ln(ω∞ − ω) 的直线
msk = (ts > 0.5e-3) & (w_meas < 0.9 * w_end)
sl, ic = np.polyfit(ts[msk], np.log(w_end - w_meas[msk]), 1)
tau_log = -1 / sl
# (c) 最小二乘：ω = ω∞(1 − e^(−t/τ)) 对 τ 最小化残差平方和
S = lambda tau: float(np.sum((w_meas - w_end * (1 - np.exp(-ts / tau))) ** 2))
tau_ls = minimize_scalar(S, bounds=(1e-3, 0.02), method="bounded").x
# (d) 初始斜率（切线法）：前 1 ms 数据的直线斜率 → τ = ω∞ / 斜率
m1 = ts <= 1e-3
slope = np.polyfit(ts[m1], w_meas[m1], 1)[0]
out(rd_n=ts.size, rd_wend=w_end, rd_t63=t63 * 1000, rd_log=tau_log * 1000, rd_ls=tau_ls * 1000, rd_tan=w_end / slope * 1000,
    rd_theory=R * J / k ** 2 * 1000, rd_lag_ms=L / R * 1000)
