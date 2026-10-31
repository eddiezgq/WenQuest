"""14.7 节：不能用初等函数表示的积分——单摆（断电后自由摆动的机械臂连杆可近似为物理摆）的大振幅周期：
T = 4√(L/g) K(k)，k = sin(θ₀/2)，K 为第一类完全椭圆积分；与小振幅公式 2π√(L/g) 比较；
误差函数、正弦积分的几个值。"""
import math

from scipy import integrate, special

from bookout import out

rows = []
for th in (10, 30, 60, 90, 120, 150):
    k = math.sin(math.radians(th) / 2)
    ratio = 2 / math.pi * special.ellipk(k * k)
    # 直接数值积分能量守恒给出的原始积分：T = 4√(L/(2g))∫₀^{θ₀} dθ/√(cos θ − cos θ₀)，T₀ = 2π√(L/g)
    t0 = math.radians(th)
    num, _ = integrate.quad(lambda a: 1 / math.sqrt(math.cos(a) - math.cos(t0)), 0, t0, limit=200)
    rows.append(f"| {th} | {ratio:.5f} | {4 / math.sqrt(2) * num / (2 * math.pi):.5f} | {(ratio - 1) * 100:.2f} |")
out(pend_tab="\n".join(rows))
lo, hi = 1.0, 90.0
for _ in range(80):
    mid = (lo + hi) / 2
    if 2 / math.pi * special.ellipk(math.sin(math.radians(mid) / 2) ** 2) < 1.01:
        lo = mid
    else:
        hi = mid
out(th1pct=(lo + hi) / 2)
# 连杆当物理摆：均匀细杆绕一端，等效摆长 2l/3；取 l = 0.4 m
l = 0.4
Leq = 2 * l / 3
out(Leq=Leq, T0=2 * math.pi * math.sqrt(Leq / 9.81), T90=4 * math.sqrt(Leq / 9.81) * special.ellipk(math.sin(math.pi / 4) ** 2))
out(erf1=math.erf(1), si_pi=special.sici(math.pi)[0], si_inf=math.pi / 2)
