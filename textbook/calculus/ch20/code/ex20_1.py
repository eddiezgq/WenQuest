"""20.1 节：可降阶的高阶方程。悬臂铝管连杆（17.4 节实验的尺寸）在末端负载与自重下的挠度（逐次积分 EI y″ = M(x)）；
单摆周期与摆幅的关系（令 p = θ′ 化为一阶，得到椭圆积分），与小摆幅公式 2π√(l/g) 比较。"""
import math

from scipy import integrate, special

from bookout import out

# 悬臂铝管：外半径 45 mm，壁厚 4 mm，长 0.425 m，E = 70 GPa；末端负载 5 kg（UR5e 的额定负载）
E, ro, t, L, g = 70e9, 0.045, 0.004, 0.425, 9.81
ri = ro - t
Ia = math.pi / 4 * (ro ** 4 - ri ** 4)
lam = 2700 * math.pi * (ro * ro - ri * ri)            # kg/m
F = 5 * g
dF = F * L ** 3 / (3 * E * Ia)
dq = lam * g * L ** 4 / (8 * E * Ia)
out(bm_I_cm4=Ia * 1e8, bm_F=F, bm_dF_um=dF * 1e6, bm_dq_um=dq * 1e6, bm_ang_mrad=F * L * L / (2 * E * Ia) * 1000,
    bm_lam=lam, bm_E_GPa=E / 1e9)
# 同样截面积的实心杆
rs = math.sqrt(ro * ro - ri * ri)
out(bm_solid_ratio=(math.pi / 4 * rs ** 4) / Ia, bm_solid_pct=100 * (math.pi / 4 * rs ** 4) / Ia)

# 单摆：T / T0 = (2/π) K(k)，k = sin(θ0/2)
rows = []
for deg in (5, 10, 30, 60, 90, 120, 170):
    th0 = math.radians(deg)
    k = math.sin(th0 / 2)
    ratio = 2 / math.pi * special.ellipk(k * k)
    # 数值核对：T/T0 = (√2/π) ∫_0^θ0 dθ/√(cos θ − cos θ0)，代换 θ = θ0 sin φ 去掉端点奇性
    f = lambda ph: th0 * math.cos(ph) / math.sqrt(max(math.cos(th0 * math.sin(ph)) - math.cos(th0), 1e-300))
    num = math.sqrt(2) / math.pi * integrate.quad(f, 0, math.pi / 2, limit=200)[0]
    rows.append(f"| {deg} | {ratio:.5f} | {num:.5f} | {(ratio - 1) * 100:.2f}% |")
out(pd_tab="\n".join(rows), pd_10=(2 / math.pi * special.ellipk(math.sin(math.radians(5)) ** 2) - 1) * 100,
    pd_60=(2 / math.pi * special.ellipk(math.sin(math.radians(30)) ** 2) - 1) * 100,
    pd_approx60=math.radians(60) ** 2 / 16 * 100)
# 对比：减速器的扭转柔度（假设的扭转刚度 2×10⁴ N·m/rad）使末端产生的位移
kj = 2e4
out(bm_kj=kj, bm_gear_um=F * L / kj * L * 1e6, bm_gear_ratio=F * L / kj * L / dF)
