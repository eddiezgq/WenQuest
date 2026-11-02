"""21.1 节：一阶方程组与状态空间。RE 40 计入绕组电感的二阶模型（状态：电流 i、转速 ω），系数矩阵的特征值与
两个时间常数；与一阶模型的阶跃响应比较；19.7 节双节点热模型写成状态方程。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import out

V, R, L, k, J = 48.0, 1.13, 0.33e-3, 60.3e-3, 137e-7
A = np.array([[-R / L, -k / L], [k / J, 0.0]])
ev = np.linalg.eigvals(A)
ev = np.sort(ev.real)
out(mo_l1=float(ev[0]), mo_l2=float(ev[1]), mo_t1_ms=float(-1000 / ev[0]), mo_t2_ms=float(-1000 / ev[1]),
    mo_tau_e_ms=L / R * 1000, mo_tau_m_ms=R * J / k ** 2 * 1000, mo_disc=float((R / L) ** 2 - 4 * k * k / (L * J)))
tau = R * J / k ** 2
s = solve_ivp(lambda t, y: [(V - R * y[0] - k * y[1]) / L, k * y[0] / J], (0, 0.03), [0, 0], t_eval=np.linspace(0, 0.03, 3001),
              rtol=1e-10, atol=1e-10)
w1 = V / k * (1 - np.exp(-s.t / tau))
out(mo_maxdiff=float(np.max(np.abs(s.y[1] - w1))), mo_maxdiff_pct=float(np.max(np.abs(s.y[1] - w1)) / (V / k) * 100),
    mo_ipk=float(s.y[0].max()), mo_istall=V / R)
# 双节点热模型：Cw dTw/dt = P − (Tw − Th)/R2，Ch dTh/dt = (Tw − Th)/R2 − (Th − Ta)/R1（偏离环境温度的量）
R1, R2, tw, tm = 4.65, 1.93, 41.5, 809.0
Cw, Ch = tw / R2, tm / R1
At = np.array([[-1 / (R2 * Cw), 1 / (R2 * Cw)], [1 / (R2 * Ch), -1 / (R2 * Ch) - 1 / (R1 * Ch)]])
et = np.sort(np.linalg.eigvals(At).real)
out(th_l1=float(et[0]), th_l2=float(et[1]), th_t1=float(-1 / et[0]), th_t2=float(-1 / et[1]), th_Cw=Cw, th_Ch=Ch)
