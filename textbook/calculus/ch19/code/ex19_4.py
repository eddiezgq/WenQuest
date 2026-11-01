"""19.4 节：一阶线性方程。RE 40 经减速比 101 驱动 UR5e 上臂（绕肩轴转动惯量取 17.4 节的零件库值）时的时间常数；
电压斜坡启动时转速的滞后；RC 低通滤波器（10 kΩ、1 μF）对不同频率的正弦信号的幅值比与相位滞后。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import T, out

R, k, Jm = 1.13, 60.3e-3, 137e-7
N, JL = 101, 0.5129                         # 减速比（假设）；上臂绕肩轴的转动惯量（17.4 节）
Jr = JL / N ** 2
Jt = Jm + Jr
tau = R * Jt / k ** 2
out(jt_Jr_gcm2=Jr * 1e7, jt_Jt_gcm2=Jt * 1e7, jt_tau_ms=tau * 1000, jt_tau0_ms=R * Jm / k ** 2 * 1000, jt_ratio=Jr / Jm,
    jt_wj=48 / k / N, jt_N=N, jt_JL=JL)

# 电压斜坡：0.2 s 内从 0 升到 48 V，再保持；转速滞后 τ
Tr, V1 = 0.2, 48.0
u = lambda t: V1 * min(t / Tr, 1.0)
s = solve_ivp(lambda t, w: [(u(t) / k - w[0]) / tau], (0, 0.4), [0.0], max_step=1e-4, dense_output=True)
t1 = 0.1
w_num = float(s.sol(t1)[0])
a = V1 / Tr / k                              # 理想转速的上升率 rad/s²
w_formula = a * (t1 - tau + tau * math.exp(-t1 / tau))
out(rp_Tr=Tr, rp_a=a, rp_w_num=w_num, rp_w_formula=w_formula, rp_lag=a * tau, rp_ideal=a * t1)

# RC 低通：R = 10 kΩ，C = 1 μF
Rr, C = 10e3, 1e-6
tc = Rr * C
fc = 1 / (2 * math.pi * tc)
rows = []
for f in (1, 5, fc, 50, 200):
    wt = 2 * math.pi * f * tc
    amp = 1 / math.sqrt(1 + wt * wt)
    ph = math.degrees(math.atan(wt))
    lab = f"{f:.1f}" + T("（截止频率）", " (cutoff)") if abs(f - fc) < 1e-9 else f"{f:g}"
    rows.append(f"| {lab} | {wt:.3f} | {amp:.3f} | {ph:.1f}° |")
out(rc_tau_ms=tc * 1000, rc_fc=fc, rc_tab="\n".join(rows))
wt50 = 2 * math.pi * 50 * tc
out(rc_a50=1 / math.sqrt(1 + wt50 ** 2), rc_p50=math.degrees(math.atan(wt50)), rc_a1=1 / math.sqrt(1 + (2 * math.pi * tc) ** 2),
    rc_delay1_ms=math.atan(2 * math.pi * tc) / (2 * math.pi) * 1000)
# 数值核对：输入 1 Hz 信号 + 50 Hz 干扰，稳态后输出中 50 Hz 成分的幅值
sig = lambda t: math.sin(2 * math.pi * t) + 0.5 * math.sin(2 * math.pi * 50 * t)
s = solve_ivp(lambda t, y: [(sig(t) - y[0]) / tc], (0, 2), [0.0], max_step=2e-4, t_eval=np.linspace(1, 2, 20001))
y = s.y[0]
ideal = (1 / math.sqrt(1 + (2 * math.pi * tc) ** 2)) * np.sin(2 * math.pi * s.t - math.atan(2 * math.pi * tc))
out(rc_resid50=float(np.max(np.abs(y - ideal))), rc_pred50=0.5 / math.sqrt(1 + wt50 ** 2))
