"""第 16 章部分习题答案中的数值。"""
import math

from scipy import integrate, optimize

from _quad import gauss, simpson, trap
from bookout import out

# 16.1.4：两连杆，|θ2| ≤ 150°
l1, l2 = 0.4, 0.3
rmin = math.sqrt(l1 ** 2 + l2 ** 2 + 2 * l1 * l2 * math.cos(math.radians(150)))
out(e1614=math.pi * ((l1 + l2) ** 2 - rmin ** 2), e1614_rmin=rmin, e1614_full=math.pi * ((l1 + l2) ** 2 - (l1 - l2) ** 2))
# 16.1.5：客厅
A_room = integrate.quad(lambda x: 4 + 0.5 * math.sin(math.pi * x / 6), 0, 6)[0]
A_clean = A_room - 1.2 * 2 - math.pi * 0.4 ** 2
out(e1615_A=A_clean, e1615_t=A_clean / 1.2)
# 16.1.6：草坪，6 个值与 11 个值的梯形公式
top = lambda x: 12 + 2 * math.sin(math.pi * x / 20) + 0.8 * math.sin(3 * math.pi * x / 20)
bot = lambda x: 1.5 * math.sin(math.pi * x / 10) ** 2 + 0.05 * x
w = lambda x: top(x) - bot(x)
t5, t10 = trap(w, 0, 20, 5), trap(w, 0, 20, 10)
out(e1616_t5=t5, e1616_t10=t10, e1616_est=(t10 - t5) / 3, e1616_true=integrate.quad(w, 0, 20)[0] - t10)
# 16.2.1
out(e1621_sq=16 / 3, e1621_tri=4 * math.sqrt(3) / 3)
# 16.2.5：铸件
A = [0, 12.4, 20.1, 24.8, 26.0, 25.1, 21.6, 15.0, 6.2, 0]          # 9 段，奇数：辛普森用前 8 段 + 最后一段梯形
h = 0.5  # cm
vt = h * (sum(A) - (A[0] + A[-1]) / 2)
vs = h / 3 * (A[0] + 4 * sum(A[1:8:2]) + 2 * sum(A[2:7:2]) + A[8]) + h / 2 * (A[8] + A[9])
out(e1625_t=vt, e1625_s=vs, e1625_m=vt * 2.7)
# 16.3.3：半球内腔 r = 15 mm，Q = 2 L/min，到 30 kPa；软管 4 mm × 1 m
V1 = 2 / 3 * math.pi * 15 ** 3 / 1000            # mL
Vh = math.pi * 2 ** 2 * 1000 / 1000               # mL
Q = 2000 / 60
out(e1633_t=V1 / Q * math.log(101.3 / 30), e1633_th=(V1 + Vh) / Q * math.log(101.3 / 30), e1633_V=V1, e1633_Vh=Vh)
# 16.3.6：酒杯 r = 3.5√(z/8)，V(z) = π·3.5²·z²/16
k = math.pi * 3.5 ** 2 / 16
out(e1636_V=k * 64, e1636_50=math.sqrt(50 / k), e1636_100=math.sqrt(100 / k), e1636_150=math.sqrt(150 / k))
# 16.4.1（3）星形线全长 6；16.4.3
out(e1643_L=0.3 * 2 * math.pi / 3 + 0.3 * math.sqrt(3), e1643_t=(0.3 * 2 * math.pi / 3 + 0.3 * math.sqrt(3)) / 0.5)
# 16.4.4：拖链电缆，半跨 1 m，垂度 0.3 m
a = optimize.brentq(lambda a: a * (math.cosh(1 / a) - 1) - 0.3, 0.3, 10)
out(e1644_a=a, e1644_L=2 * a * math.sinh(1 / a))
# 16.4.5：五次多项式换道路径，高斯 4、8 点
d, Lx = 1.0, 4.0
g = lambda x: math.sqrt(1 + (d * 30 * (x / Lx) ** 2 * (1 - x / Lx) ** 2 / Lx) ** 2)
out(e1645_4=gauss(g, 0, Lx, 4), e1645_8=gauss(g, 0, Lx, 8), e1645_ex=integrate.quad(g, 0, Lx)[0])
# 16.5.3（2）
out(e1653b=math.pi * (2 + math.sinh(2)))
# 16.5.5：电机外壳
r, L = 40.0, 120.0
S = 2 * math.pi * r * L + 4 * math.pi * r * r
out(e1655=S * 2.5 / 1e6)
# 16.5.6：最优 R
V = 30e6
Rs = (3 * V / (5 * math.pi)) ** (1 / 3)
out(e1656_R=Rs, e1656_S=(2 * V / Rs + 5 / 3 * math.pi * Rs * Rs) / 1e6)
