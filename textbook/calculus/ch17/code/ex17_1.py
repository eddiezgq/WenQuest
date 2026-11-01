"""17.1 节：变力做功——夹爪弹簧；绞车提升水下机器人（缆绳自重随深度减少）；气弹簧的等温压缩；把 UR5e 上臂从竖直下垂抬到水平
（重力矩 m g d cos θ 的功等于势能增量）；把圆柱形水箱里的水抽到箱顶以上。"""
import math

from scipy import integrate

from bookout import out

g = 9.81
# 夹爪弹簧：k = 2000 N/m，压缩 20 mm
k, x1 = 2000.0, 0.02
out(spring_W=integrate.quad(lambda x: k * x, 0, x1)[0])
# 绞车：ROV 在水中重（扣除浮力）120 N，缆绳水中线重 3 N/m，从 60 m 深提到水面
F0, lam, D = 120.0, 3.0, 60.0
W_rov = integrate.quad(lambda y: F0 + lam * (D - y), 0, D)[0]       # y：已提升的距离
out(rov_F0=F0, rov_lam=lam, rov_D=D, W_rov=W_rov / 1000, W_rov_payload=F0 * D / 1000, W_rov_cable=lam * D * D / 2 / 1000,
    rov_t=W_rov / 600.0)                                                  # 600 W 绞车的最短时间
# 气弹簧：初始 0.5 MPa（绝对）、容积 50 mL，等温压缩到 30 mL
p0, V0, V1 = 0.5e6, 50e-6, 30e-6
W_gas = integrate.quad(lambda V: p0 * V0 / V, V1, V0)[0]
out(W_gas=W_gas, W_gas_ex=p0 * V0 * math.log(V0 / V1), F_end=(p0 * V0 / V1 - 0.1013e6) * math.pi * 0.01 ** 2)
# UR5e 上臂（零件库模型 8.393 kg，质心距肩关节 0.2125 m）从竖直下垂（θ = −90°）抬到水平（θ = 0）
m, d = 8.393, 0.2125
W_arm = integrate.quad(lambda th: m * g * d * math.cos(th), -math.pi / 2, 0)[0]
out(arm_m=m, arm_d=d, W_arm=W_arm, tau_max=m * g * d)
# 水箱：圆柱，半径 0.15 m、高 0.4 m，装满水，从箱顶抽出（抽到箱顶以上 0.1 m 的出水口）
R, H, h_out, rho = 0.15, 0.4, 0.1, 1000.0
W_tank = integrate.quad(lambda y: rho * g * math.pi * R * R * (H + h_out - y), 0, H)[0]
out(W_tank=W_tank, m_water=rho * math.pi * R * R * H)
