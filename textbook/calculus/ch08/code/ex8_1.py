"""8.1 节：微分——两节连杆（UR5e 上臂、前臂）肘关节角改变 Δθ 时，腕心到肩的距离 r 的增量 Δr 与微分 dr = r′(θ)Δθ；
差 Δr − dr 与 Δθ² 成正比（高阶无穷小）。方形钢板受热膨胀：ΔA = 2xΔx + Δx²。"""
import math

from _traj import ur5e_links
from bookout import out

l1, l2 = ur5e_links()
r = lambda t: math.sqrt(l1 * l1 + l2 * l2 + 2 * l1 * l2 * math.cos(t))
dr = lambda t: -l1 * l2 * math.sin(t) / r(t)          # r′(θ)
t0 = math.radians(60)
out(t0_deg=60, r0_mm=r(t0) * 1000, dr0=dr(t0) * 1000)           # r′ 的单位：mm/rad
rows = []
for d in (0.1, 0.01, 0.001, 1e-4):
    D = r(t0 + d) - r(t0)
    lin = dr(t0) * d
    rows.append(f"| {d:g} | {D * 1000:.6f} | {lin * 1000:.6f} | {(D - lin) * 1000:.3e} | {(D - lin) / d ** 2 * 1000:.3f} |")
out(tab="\n".join(rows))
# r″(θ)/2：Δr − dr ≈ ½ r″ Δθ²
h = 1e-4
r2 = (r(t0 + h) - 2 * r(t0) + r(t0 - h)) / h ** 2
out(half_r2=r2 / 2 * 1000)

# 钢板：边长 x = 0.5 m，温度升高 ΔT，线膨胀系数 α = 1.2e−5 /K
x, alpha = 0.5, 1.2e-5
for dT in (10, 100):
    dx = alpha * x * dT
    out(**{f"plate_dA_{dT}": (2 * x * dx + dx * dx) * 1e6, f"plate_dA_lin_{dT}": 2 * x * dx * 1e6, f"plate_sq_{dT}": dx * dx * 1e6})
