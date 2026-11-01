"""第 17 章部分习题答案中的数值。"""
import math

from scipy import integrate, special

from _quad import simpson
from bookout import out

g = 9.81
# 17.1.4：绝热压缩 pV^1.4 = 常数
p0, V0, V1, gam = 0.5e6, 50e-6, 30e-6, 1.4
W_ad = integrate.quad(lambda V: p0 * (V0 / V) ** gam, V1, V0)[0]
out(e1714=W_ad, e1714_iso=p0 * V0 * math.log(V0 / V1))
# 17.1.5
out(fa_m=2.275, e1715=2.275 * g * 0.196)
# 17.2.2、17.2.3
out(e1722=1000 * g * 3 * math.pi / 1000, e1723=1000 * g * 1.7 * 0.03)
# 17.3.4
out(sh_h=0.1625, fa_h=0.8375)
out(e1734_v=(12 * 0.1 + 8.4 * 0.375 + 4 * 0.8375) / 24.4, e1734_h=(8.4 * 0.2125 + 4 * (0.425 + 0.25)) / 24.4)
# 17.3.6：半斗物料（物料高 0.25 m）
a, b, h, rho = 0.6, 0.2, 0.5, 1600.0
s = lambda z: b + (a - b) * z / h
V = integrate.quad(lambda z: s(z) ** 2, 0, 0.25)[0]
zc = integrate.quad(lambda z: z * s(z) ** 2, 0, 0.25)[0] / V
m_load = rho * V
h_tot = (90 * 0.22 + m_load * (0.45 + zc)) / (90 + m_load)
out(e1736_m=m_load, e1736_h=h_tot, e1736_a=g * 0.3 / h_tot)
# 17.5.5
out(e1755=0.8 * math.sqrt(2) * special.erfinv(0.999))
# 17.6.1
E = integrate.quad(lambda t: 50 * (1 - math.exp(-t / 2)), 0, 10)[0]
out(e1761=E, e1761_avg=E / 10)
# 17.6.3：AGV
m, v, ta, tc = 200.0, 1.5, 2.0, 20.0
acc = v / ta
Fr = 0.02 * m * g
d_a = v * ta / 2
W_acc = (m * acc + Fr) * d_a
W_cru = Fr * v * tc
W_dec = max(Fr - m * acc, 0) * d_a          # 减速时阻力不足，电机要制动，不输出正功
out(e1763=W_acc + W_cru + W_dec, e1763_roll=Fr * (d_a + v * tc), e1763_ek=0.5 * m * v * v)
# 17.7.1、17.7.3、17.7.4
out(e1771=5 * (1 - math.exp(-0.3)) / 0.05, e1773=integrate.quad(lambda q: 120 - q * q - 56, 0, 8)[0])
c = [0, 2.1, 6.4, 7.9, 6.2, 4.1, 2.4, 1.3, 0.6, 0.3, 0.1]
I = 3 / 3 * (c[0] + c[-1] + 4 * sum(c[1:-1:2]) + 2 * sum(c[2:-1:2]))
out(e1774_I=I, e1774=8 / I * 60)
