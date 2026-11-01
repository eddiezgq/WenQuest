"""16.2 节：矩阵指数 e^{At}。
(1) 三种算法：按定义的级数、对角化 Xe^{Λt}X⁻¹、scipy.linalg.expm（缩放与平方 + 帕德近似）；
    莫勒–范洛恩的例子 A = [[−49, 24], [−64, 31]]（特征值 −1、−17）：级数在浮点数中因相消而失准；
(2) e^{A+B} ≠ e^A e^B（A、B 不交换）；
(3) 不能对角化：A = [[−2, 1], [0, −2]]，e^{At} = e^{−2t}[[1, t], [0, 1]]，出现 t e^{−2t}；
(4) 常数输入：x(t) = e^{At}x₀ + A⁻¹(e^{At} − I)bP。电机过载 P = 80 W，从冷态开始，绕组温升多久达到 100 K（稳态会到 120 K）；
(5) 精确离散化与欧拉法：13.5 节采样 PD 控制 θ̈ + 4θ̇ + 100θ = 0，T = 0.05 s。欧拉法 I + AT 的特征值模 > 1，
    精确的 e^{AT} 的特征值模 = e^{−2T} < 1。"""
import math

import numpy as np
import scipy.linalg as sl
from scipy.optimize import brentq

from _motor import A as AM, B as BM
from _num import sci
from bookout import out, tex, vec

# (1) 莫勒–范洛恩：A = X diag(−1, −17) X⁻¹，X = [[1, 3], [2, 4]]，精确值可以手算
A = np.array([[-49.0, 24], [-64, 31]])
lam, X = np.linalg.eig(A)


def exact(t):
    e1, e17 = math.exp(-t), math.exp(-17 * t)
    return np.array([[-2 * e1 + 3 * e17, 1.5 * e1 - 1.5 * e17], [-4 * e1 + 4 * e17, 3 * e1 - 2 * e17]])


def series(M, n=400):
    S, term, big = np.eye(2), np.eye(2), 0.0
    for k in range(1, n):
        term = term @ M / k
        S = S + term
        big = max(big, float(np.abs(term).max()))
    return S, big


out(lamA=vec(np.sort(lam), 0), E=tex(sl.expm(A), 4))
for name, t in (("1", 1.0), ("25", 2.5)):
    E = sl.expm(A * t)
    Ed = (X * np.exp(lam * t)) @ np.linalg.inv(X)
    S, big = series(A * t)
    out(**{f"err_expm_{name}": sci(float(np.abs(E - exact(t)).max()) + 1e-18, 0),
           f"err_diag_{name}": sci(float(np.abs(Ed - exact(t)).max()) + 1e-18, 0),
           f"err_series_{name}": sci(float(np.abs(S - exact(t)).max()), 0), f"big_{name}": sci(big, 0),
           f"Emax_{name}": float(np.abs(exact(t)).max())})
out(E25=tex(exact(2.5), 4), S25=tex(series(A * 2.5)[0], 0))
# (2) 不交换
P = np.array([[0.0, 1], [0, 0]])
Q = np.array([[0.0, 0], [1, 0]])
out(eAB=tex(sl.expm(P + Q), 3), eAeB=tex(sl.expm(P) @ sl.expm(Q), 3))
# (3) 若尔当块
J = np.array([[-2.0, 1], [0, -2]])
t = 1.5
out(eJ_err=sci(float(np.abs(sl.expm(J * t) - math.exp(-2 * t) * np.array([[1, t], [0, 1]])).max()) + 1e-18, 0),
    teJ_max_t=0.5, teJ_max=float(0.5 * math.exp(-1)))
# (4) 电机过载
P80 = 80.0
x_t = lambda t: sl.expm(AM * t) @ np.zeros(2) + np.linalg.solve(AM, (sl.expm(AM * t) - np.eye(2)) @ BM * P80)
xss = -np.linalg.solve(AM, BM * P80)
t100 = brentq(lambda t: x_t(t)[0] - 100, 1, 5000)
out(xss80=vec(xss, 0), t100=float(t100), t100_min=float(t100 / 60), x_60=vec(x_t(60), 1), xh_t100=float(x_t(t100)[1]))
# 单时间常数的估计：把电机看成一个热容 C_w + C_h、一个热阻 R_wh + R_ha（会严重高估允许时间）
tau_one = (500 + 50) * 1.5
t100_one = -tau_one * math.log(1 - 100 / 120)
out(t100_one_min=float(t100_one / 60))
# 数值积分检验
from scipy.integrate import solve_ivp
s = solve_ivp(lambda t, y: AM @ y + BM * P80, (0, 600), [0, 0], rtol=1e-10, atol=1e-12, dense_output=True)
out(err_ivp=sci(float(max(np.abs(s.sol(t) - x_t(t)).max() for t in np.linspace(0, 600, 61))) + 1e-17, 0))
# (5) 离散化
T = 0.05
Ac = np.array([[0.0, 1], [-100, -4]])
Ae, Ax = np.eye(2) + Ac * T, sl.expm(Ac * T)
out(lam_c=", ".join(f"{z.real:.0f} {'+' if z.imag > 0 else '−'} {abs(z.imag):.2f}i" for z in np.linalg.eigvals(Ac)),
    rho_e=float(max(abs(np.linalg.eigvals(Ae)))), rho_x=float(max(abs(np.linalg.eigvals(Ax)))), e2T=float(math.exp(-2 * T)),
    Ax=tex(Ax, 4))
xe, xx = np.array([1.0, 0]), np.array([1.0, 0])
for k in range(60):
    xe, xx = Ae @ xe, Ax @ xx
# 控制量也按零阶保持采样（13.5 节已算过）：精确模型是 A_d − B_dK（16.6.4 节）
Ao = np.array([[0.0, 1], [0, 0]]); Bo = np.array([[0.0], [1.0]]); Kpd = np.array([[100.0, 4.0]])
Mb = np.zeros((3, 3)); Mb[:2, :2], Mb[:2, 2:] = Ao, Bo
Ez = sl.expm(Mb * T)
out(rho_zoh=float(max(abs(np.linalg.eigvals(Ez[:2, :2] - Ez[:2, 2:] @ Kpd)))))
out(th_e60=float(xe[0]), th_x60=float(xx[0]), th_true=float((sl.expm(Ac * 3.0) @ [1.0, 0])[0]))
