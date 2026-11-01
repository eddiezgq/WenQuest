"""第 15 章部分习题答案中的数值。"""
import math

from scipy import integrate, special

from _quad import gauss, romberg, simpson, trap
from bookout import out

# 15.1.1
f = lambda x: 1 / (1 + x * x)
out(e1511_t=trap(f, 0, 1, 4), e1511_s=simpson(f, 0, 1, 4), e1511_ex=math.pi / 4)
# 15.1.4：AGV 速度每 0.5 s
v = [0, 0.42, 0.81, 1.05, 1.18, 1.20, 1.20, 1.12, 0.85, 0.40, 0]
h = 0.5
out(e1514_t=h / 2 * (v[0] + 2 * sum(v[1:-1]) + v[-1]),
    e1514_s=h / 3 * (v[0] + v[-1] + sum((4 if k % 2 else 2) * v[k] for k in range(1, len(v) - 1))))
# 15.2.1：∫₁² ln x，误差 ≤ 1e-6
n_t = math.ceil(1 / math.sqrt(12e-6))
n_s = math.ceil(1 / (180e-6 / 6) ** 0.25)
n_s += n_s % 2
out(e1521_t=n_t, e1521_s=n_s)
# 15.2.4：龙贝格求 π
R = romberg(lambda x: 4 / (1 + x * x), 0, 1, 4)
out(e1524=R[3][3], e1524_err=abs(R[3][3] - math.pi))
# 15.3.1
out(e1531_2=gauss(math.exp, 0, 1, 2), e1531_3=gauss(math.exp, 0, 1, 3), e1531_ex=math.e - 1)
# 15.3.4：钢连杆，截面 6 → 2 cm²，L = 0.4
rho, L = 7850.0, 0.4
A = lambda x: 6e-4 - 4e-4 * x / L
m = gauss(lambda x: rho * A(x), 0, L, 2)
out(e1534_I=gauss(lambda x: rho * A(x) * x * x, 0, L, 2), e1534_xc=gauss(lambda x: rho * A(x) * x, 0, L, 2) / m, e1534_m=m)
# 15.4.5：有效质量 2 kg
Jp = 400 * 2 * 0.001 / math.pi
out(e1545_v=Jp / 2)
# 15.5.3
out(e1553=0.8 * math.log(20) / 4)
# 15.6.2
out(e1562=gauss(lambda u: 2 * math.exp(u * u), 0, 1, 3), e1562_ex=integrate.quad(lambda u: 2 * math.exp(u * u), 0, 1)[0])
# 15.6.4：等效摆长 0.4 m，120°
Leq, g = 0.4, 9.81
k = math.sin(math.radians(60))
K = gauss(lambda p: 1 / math.sqrt(1 - k * k * math.sin(p) ** 2), 0, math.pi / 2, 10)
T0 = 2 * math.pi * math.sqrt(Leq / g)
out(e1564_T=4 * math.sqrt(Leq / g) * K, e1564_T0=T0, e1564_ratio=4 * math.sqrt(Leq / g) * K / T0)
# 15.6.5：水箱
H, Atank, a = 0.5, 0.2, math.pi * 0.005 ** 2
t_all = Atank / a * math.sqrt(2 * H / g)
t_first = t_all * (1 - 1 / math.sqrt(2))
out(e1565=t_all, e1565_1=t_first, e1565_2=t_all - t_first)
# 15.7.2（3）、15.7.4
out(e1572=math.gamma(4 / 3))
eta, beta = 15000.0, 2.5
b10 = eta * (-math.log(0.9)) ** (1 / beta)
out(e1574_m=eta * math.gamma(1 + 1 / beta), e1574_b10=b10, e1574_y=b10 / 16 / 365)
# 15.7.6
out(e1576=integrate.quad(lambda t: t ** (-0.9) * math.exp(-t), 0, math.inf)[0], e1576_ex=math.gamma(0.1))
