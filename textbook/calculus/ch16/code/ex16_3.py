"""16.3 节：旋转体的体积——真空吸盘的抛物面内腔（圆盘法，阿基米德：等于外切圆柱的一半）与抽真空时间；
关节密封 O 形圈（柱壳法，2π²Ra²）；y = x(2 − x) 绕 y 轴（柱壳与圆盘两种算法）；空心轴（垫圈法）；加百列号角的体积。"""
import math

from scipy import integrate

from bookout import out

# 吸盘：口径半径 R = 20 mm，深 h = 8 mm，内腔是抛物面 z = h(r/R)²……绕 z 轴，截面圆半径 r(z) = R√(z/h)
R, h = 20.0, 8.0
V_cup = integrate.quad(lambda z: math.pi * R * R * z / h, 0, h)[0]     # mm³
out(cup_R=R, cup_h=h, V_cup=V_cup / 1000, V_cyl=math.pi * R * R * h / 1000, cup_ratio=V_cup / (math.pi * R * R * h))
# 抽真空：泵抽速 Q = 1 L/min（等温，p = p0 e^{−Qt/V}），抽到 −60 kPa（绝对压力 40 kPa）的时间；软管死容积 V_d = 5 mL
Q = 1000 / 60.0                       # mL/s
out(p0=101.3)
for name, V in (("cup", V_cup / 1000), ("tot", V_cup / 1000 + 5.0)):
    out(**{f"t_{name}": V / Q * math.log(101.3 / 40.0)})
# O 形圈：中径 2R = 50 mm，截面直径 2a = 3 mm，橡胶密度取 1.2 g/cm³
Ro, a = 25.0, 1.5
V_o = integrate.quad(lambda x: 2 * math.pi * x * 2 * math.sqrt(max(a * a - (x - Ro) ** 2, 0)), Ro - a, Ro + a)[0]
out(V_o=V_o, V_o_ex=2 * math.pi ** 2 * Ro * a * a, m_o=V_o / 1000 * 1.2)
# y = x(2 − x)，0 ≤ x ≤ 2，绕 y 轴
V_shell = integrate.quad(lambda x: 2 * math.pi * x * x * (2 - x), 0, 2)[0]
V_disk = integrate.quad(lambda y: math.pi * ((1 + math.sqrt(1 - y)) ** 2 - (1 - math.sqrt(1 - y)) ** 2), 0, 1)[0]
out(V_shell=V_shell, V_disk=V_disk, V_ex=8 * math.pi / 3)
# 空心轴：外径 40 mm、内径 30 mm、长 200 mm，铝 2.7 g/cm³；与同质量实心轴的直径
Ro2, Ri2, Ls = 20.0, 15.0, 200.0
V_hs = math.pi * (Ro2 ** 2 - Ri2 ** 2) * Ls
d_solid = 2 * math.sqrt(Ro2 ** 2 - Ri2 ** 2)
out(V_hs=V_hs / 1000, m_hs=V_hs / 1000 * 2.7, d_solid=d_solid, stiff_ratio=(Ro2 ** 4 - Ri2 ** 4) / (d_solid / 2) ** 4)
# 加百列号角：y = 1/x，x ≥ 1，绕 x 轴
out(horn_V=integrate.quad(lambda x: math.pi / x ** 2, 1, math.inf)[0])
