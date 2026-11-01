"""第 19 章部分习题答案中的数值。"""
import math

from scipy.optimize import brentq

from bookout import out

R, k, J = 1.13, 60.3e-3, 137e-7
# 19.1.5：限流 10 A 启动
w1 = (48 - R * 10) / k
out(e1915_w=w1, e1915_t=w1 * J / (10 * k) * 1000)
# 19.3.5：电缆每米 0.5 kg，跨距 12 m，垂度 0.3 m
w = 0.5 * 9.81
T0p = w * 12 ** 2 / (8 * 0.3)
T0c = brentq(lambda T0: T0 / w * (math.cosh(6 / (T0 / w)) - 1) - 0.3, 10, 1e5)
out(e1935_par=T0p, e1935_cat=T0c)
# 19.4.4：电流不超过 3 A 时的最短斜坡时间
Jt = J + 0.5129 / 101 ** 2
out(e1944=Jt * 48 / (k * k * 3))
# 19.4.5：温度传感器 τ = 4 s，周期 60 s，幅值 2 °C
wt = 2 * math.pi / 60 * 4
out(e1945_amp=2 / math.sqrt(1 + wt * wt), e1945_lag=math.atan(wt) / (2 * math.pi / 60))
# 19.5.6：斜向上游渡河
out(e1956_t=50 / math.sqrt(2 ** 2 - 1 ** 2))
# 19.7.1：咖啡
kap = math.log(70 / 40) / 10
out(e1971=math.log(70 / 20) / kap - 10)
# 19.7.2：1.5 倍额定电流
P = (1.5 * 3.17) ** 2 * R
dT = P * 6.58
out(e1972_t=-809 * math.log(1 - 130 / dT), e1972_T=25 + dT)
