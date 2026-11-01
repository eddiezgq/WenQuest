"""第 18 章部分习题答案中的数值。"""
import math

from scipy import integrate, stats

from bookout import out

# 18.1.2
h = math.pi / 4
out(e1812_U=h * (math.sin(h) + 1 + 1 + math.sin(3 * h)), e1812_L=h * (0 + math.sin(h) + math.sin(3 * h) + 0))
# 18.3.3
out(e1833_vs=12 * 0.5 * 0.02 * 1000, e1833_rms=12 * math.sqrt(0.5))
# 18.4.5
g, h0, e = 9.81, 1.0, 0.6
t0 = math.sqrt(2 * h0 / g)
v1 = math.sqrt(2 * g * h0)
out(e1845_t=t0 + 2 * e * v1 / (g * (1 - e)), e1845_d=h0 * (1 + e * e) / (1 - e * e))
# 18.6.5
lam, L, mg = 2.0, 0.4, 1.5
M = lam * L + mg
out(e1865_M=M, e1865_x=(lam * L * L / 2 + mg * L) / M, e1865_I=lam * L ** 3 / 3 + mg * L * L)
# 18.6.6：量程 ±100 N
sig, F = 40.0, 100.0
p_hi = 1 - stats.norm.cdf(F / sig)
EY2 = integrate.quad(lambda x: x * x * stats.norm.pdf(x, 0, sig), -F, F)[0] + 2 * F * F * p_hi
out(e1866_p=2 * p_hi * 100, e1866_under=(1 - math.sqrt(EY2) / sig) * 100)
