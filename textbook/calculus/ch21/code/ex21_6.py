"""21.6 节：李雅普诺夫函数初步。带重力补偿的 PD 控制关节（20.7 节的参数，竖直平面）：V = ½Jq̇² + ½K_p e²
沿解单调减小（数值核对）；有阻尼单摆的能量；线性系统的二次型李雅普诺夫函数 AᵀP + PA = −I 的解与它的正定性。"""
import math

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import solve_continuous_lyapunov

from bookout import out

J = 0.5129 + 137e-7 * 101 ** 2
b = 0.5
Kp = J * 100
Kd = 2 * 0.7 * 10 * J - b
mgd = 8.393 * 9.81 * 0.2125
qr = 0.5


def rhs(t, y):
    q, w = y
    tau = Kp * (qr - q) - Kd * w + mgd * math.cos(q)        # 重力补偿
    return [w, (tau - b * w - mgd * math.cos(q)) / J]


ts = np.linspace(0, 2, 2001)
s = solve_ivp(rhs, (0, 2), [0.0, 0.0], t_eval=ts, rtol=1e-11, atol=1e-13)
V = 0.5 * J * s.y[1] ** 2 + 0.5 * Kp * (qr - s.y[0]) ** 2
out(ly_V0=float(V[0]), ly_V1=float(V[-1]), ly_mono=bool(np.all(np.diff(V) <= 1e-12)), ly_err=float(qr - s.y[0, -1]),
    ly_maxinc=float(np.max(np.diff(V))))
# 不补偿重力时的对比（20.7 节）：稳态误差
s2 = solve_ivp(lambda t, y: [y[1], (Kp * (qr - y[0]) - Kd * y[1] - b * y[1] - mgd * math.cos(y[0])) / J], (0, 2), [0, 0],
               rtol=1e-10, atol=1e-12)
out(ly_err_nocomp=float(qr - s2.y[0, -1]))

# 线性系统 x′ = Ax（PD 关节的误差方程），解 AᵀP + PA = −I
A = np.array([[0, 1], [-Kp / J, -(b + Kd) / J]])
P = solve_continuous_lyapunov(A.T, -np.eye(2))
ev = np.linalg.eigvalsh(P)
out(lp_p11=float(P[0, 0]), lp_p12=float(P[0, 1]), lp_p22=float(P[1, 1]), lp_ev1=float(ev[0]), lp_ev2=float(ev[1]),
    lp_resid=float(np.max(np.abs(A.T @ P + P @ A + np.eye(2)))))
