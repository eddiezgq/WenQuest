"""17.4 节：转动惯量——均匀细杆绕端点与绕中点；圆盘；空心轴与实心轴的极惯性矩；第 15 章变截面连杆（绕根部与绕质心）；
零件库 UR5e 上臂（均匀实心圆柱近似：质量 8.393 kg，半径 0.06 m，长 0.425 m）绕质心与绕肩关节轴的转动惯量；
电机转子经减速器折算到关节的惯量。"""
import math

from scipy import integrate

from bookout import out

# 细杆 m = 1、L = 1
out(rod_end=integrate.quad(lambda x: x * x, 0, 1)[0], rod_mid=integrate.quad(lambda x: x * x, -0.5, 0.5)[0])
# 圆盘（面密度均匀，按圆环叠加）
out(disk=integrate.quad(lambda r: r * r * 2 * r, 0, 1)[0] / 1.0)          # m = π·1²·σ，σ = 1/π → ∫r²·2πr σ dr = ∫2r³ dr
# 空心轴（外径 40、内径 30 mm）与等质量实心轴（直径 26.46 mm）的极惯性矩之比
Ro, Ri = 20.0, 15.0
rs = math.sqrt(Ro ** 2 - Ri ** 2)
out(J_ratio=(Ro ** 4 - Ri ** 4) / rs ** 4)
# 变截面铝连杆（15.3 节）
rho, A0, L = 2700.0, 4e-4, 0.5
lam = lambda x: rho * A0 * (1 - x / (2 * L))
m = integrate.quad(lam, 0, L)[0]
I_root = integrate.quad(lambda x: x * x * lam(x), 0, L)[0]
xc = integrate.quad(lambda x: x * lam(x), 0, L)[0] / m
I_cm = I_root - m * xc * xc
out(link_m=m, link_I_root=I_root, link_xc=xc, link_I_cm=I_cm, link_I_cm_direct=integrate.quad(lambda x: (x - xc) ** 2 * lam(x), 0, L)[0],
    link_uniform=m * L * L / 3)
# UR5e 上臂（零件库：均匀实心圆柱）
mu, ru, Lu = 8.393, 0.06, 0.425
I_trans = mu * (3 * ru * ru + Lu * Lu) / 12
I_axial = mu * ru * ru / 2
I_sh = I_trans + mu * (Lu / 2) ** 2
out(ur_m=mu, ur_r=ru, ur_L=Lu, ur_I_cm=I_trans, ur_I_axial=I_axial, ur_I_sh=I_sh, ur_md2=mu * (Lu / 2) ** 2, ur_rod=mu * Lu * Lu / 12,
    ur_tau_a=I_sh * 5.0)
out(ur_lib_I=0.133886, ur_lib_ax=0.0151074, ur_manual=8.058)      # 零件库模型与厂家手册中的值
# 电机转子折算：转子 1.0×10⁻⁴ kg·m²，减速比 101
Im, N = 1.0e-4, 101
out(Im=Im, N=N, I_refl=Im * N * N)
