"""第 10 章部分习题答案中的数值。"""
import math

from _path import curvature, lane
from bookout import out

# 10.2.1（2）、（3）
out(e1021_2=-3 * 2 ** (2 / 3), e1021_3=1 / math.sqrt(2 * math.e))
# 10.2.4：超调 2%
M = 0.02
z = -math.log(M) / math.sqrt(math.pi ** 2 + math.log(M) ** 2)
out(e1024_z=z, e1024_tp=math.pi / (10 * math.sqrt(1 - z * z)))
# 10.2.6：由两个峰的比与由第一个峰估计 ζ
x2 = math.log(0.12 / 0.002) / 2
x1 = -math.log(0.12)
out(e1026_two=x2 / math.sqrt(math.pi ** 2 + x2 ** 2), e1026_one=x1 / math.sqrt(math.pi ** 2 + x1 ** 2))
# 10.4.3：欠阻尼速度响应的第一个极大值
zeta, wn = 0.6, 10.0
wd = wn * math.sqrt(1 - zeta ** 2)
out(e1043=math.atan2(wd, zeta * wn) / wd)
# 10.5.1（4）
out(e1051_x=-math.log(2) / 2, e1051_k=2 / (3 * math.sqrt(3)))
# 10.5.3：L 加倍
for L in (4.0, 8.0):
    y, yp, ypp = lane("quintic", 1.0, L)
    km = max(curvature(yp, ypp, L * k / 20000) for k in range(20001))
    out(**{f"e1053_k{int(L)}": km, f"e1053_v{int(L)}": math.sqrt(1.0 / km)})
# 10.6.1（2）
out(e1061_max=math.pi / 6 + math.sqrt(3), e1061_min=5 * math.pi / 6 - math.sqrt(3))
# 10.6.2
out(e1062=math.sqrt(11) / 2)
# 10.6.4：P = (Iα + bω)ω，五次多项式，T = 2 s，Δ = π/2
T, D, I, b = 2.0, math.pi / 2, 1.0, 0.5
w = lambda t: D / T * 30 * (t / T) ** 2 * (1 - t / T) ** 2
a = lambda t: D / T ** 2 * 60 * (t / T) * (1 - t / T) * (1 - 2 * t / T)
P = lambda t: (I * a(t) + b * w(t)) * w(t)
tg = max((T * k / 100 for k in range(101)), key=P)
h = 1e-5
for _ in range(6):
    tg -= ((P(tg + h) - P(tg - h)) / (2 * h)) / ((P(tg + h) - 2 * P(tg) + P(tg - h)) / h ** 2)
out(e1064_t=tg, e1064_P=P(tg))
