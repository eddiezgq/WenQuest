"""第 22 章部分习题答案中的数值。"""
import math

from bookout import out

# 22.1.1：y′ = y、y(0) = 1，h = 0.1 走到 x = 1；误差界 Mh/(2L)(e^L − 1)，M = e、L = 1
y = 1.1 ** 10
out(e2211_y=y, e2211_err=math.e - y, e2211_bound=math.e * 0.1 / 2 * (math.e - 1))
# 22.2.1：y′ = y 一步 h = 0.1：休恩、RK4 与 e^0.1 之差
h = 0.1
out(e2221_heun=abs(1 + h + h * h / 2 - math.exp(h)), e2221_rk4=abs(1 + h + h ** 2 / 2 + h ** 3 / 6 + h ** 4 / 24 - math.exp(h)))
# 22.4.3：y′ = −y³、y(0) = 1、h = 0.5 的一步隐式欧拉：解 z + 0.5 z³ = 1（牛顿法，从 z = 1 开始）
z, its = 1.0, []
for _ in range(5):
    z = z - (z + 0.5 * z ** 3 - 1) / (1 + 1.5 * z * z)
    its.append(z)
out(e2243_z1=its[0], e2243_z2=its[1], e2243_z=its[-1], e2243_exact=1 / math.sqrt(1 + 2 * 0.5))
# 22.4.4：电–机–热模型，显式方法步长上限 2/|λ_max| 与仿真 1 小时所需步数
lam_max = 3458.777638318345        # 程序 22.4.1 的结果（工作点 i = 1.5 A、ω = 330 rad/s）
out(e2244_h_ms=2 / lam_max * 1000, e2244_steps=3600 / (2 / lam_max))
