"""10.4 节：函数作图——x³/(x − 1)² 的渐近线、极值、拐点（数值核对）；
临界阻尼关节的速度 ωₙ²t e^{−ωₙt}：最大值与拐点；作图程序的陷阱：采样点太少时 sin(2π·99x) 看起来像 −sin(2πx)。"""
import math

from bookout import out

f = lambda x: x ** 3 / (x - 1) ** 2
fp = lambda x: x * x * (x - 3) / (x - 1) ** 3
fpp = lambda x: 6 * x / (x - 1) ** 4
out(f3=f(3), fp3=fp(3), fpp3=fpp(3), gap_1e3=f(1e3) - (1e3 + 2), gap_1e6=f(1e6) - (1e6 + 2))
# 临界阻尼速度 h(t) = ωₙ²t e^{−ωₙt}
wn = 10.0
h = lambda t: wn * wn * t * math.exp(-wn * t)
out(h_tmax=1 / wn, h_max=h(1 / wn), h_tinf=2 / wn, h_inf=h(2 / wn))
# 混叠：在 x = k/100（k = 0…100）处，sin(2π·99x) = −sin(2πx)
out(alias=max(abs(math.sin(2 * math.pi * 99 * k / 100) + math.sin(2 * math.pi * k / 100)) for k in range(101)))
