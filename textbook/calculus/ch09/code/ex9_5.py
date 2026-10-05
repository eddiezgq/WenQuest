"""9.5 节：泰勒公式——腕心距离 r(θ₂) 在 60° 处的一次、二次、三次泰勒多项式及其误差（误差分别与 h²、h³、h⁴ 成正比）；
中心差商与二阶差商的误差系数 f‴/6、f⁗/12 的验证（五次多项式关节运动，t₀ = 0.5 s）；拉格朗日余项的中值点。"""
import math

from _traj import ur5e_links
from bookout import out

l1, l2 = ur5e_links()
a, b = l1 * l1 + l2 * l2, 2 * l1 * l2
r0 = lambda t: math.sqrt(a + b * math.cos(t))
t0 = math.radians(60)
# r² = a + b cos θ 逐次求导：2rr′ = −b sin θ；r″ = (−b cos θ/2 − r′²)/r；r‴ = (b sin θ/2 − 3r′r″)/r
R = r0(t0)
R1 = -b * math.sin(t0) / (2 * R)
R2 = (-b * math.cos(t0) / 2 - R1 * R1) / R
R3 = (b * math.sin(t0) / 2 - 3 * R1 * R2) / R
out(R_mm=R * 1000, R1=R1 * 1000, R2=R2 * 1000, R3=R3 * 1000, half_R2=R2 / 2 * 1000, sixth_R3=R3 / 6 * 1000)
rows = []
for h in (0.1, 0.05, 0.01, 0.001):
    f = r0(t0 + h)
    p1 = R + R1 * h
    p2 = p1 + R2 / 2 * h * h
    p3 = p2 + R3 / 6 * h ** 3
    rows.append(f"| {h:g} | {abs(f - p1) * 1000:.2e} | {abs(f - p2) * 1000:.2e} | {abs(f - p3) * 1000:.2e} | {(f - p2) / h ** 3 * 1000:.3f} |")
out(r_tab="\n".join(rows))

# 中心差商与二阶差商：θ(t) = Δ(10s³ − 15s⁴ + 6s⁵)，T = 2 s，Δ = π/2，t₀ = 0.5 s
T, D = 2.0, math.pi / 2
th = lambda t: D * (10 * (t / T) ** 3 - 15 * (t / T) ** 4 + 6 * (t / T) ** 5)
s0 = 0.5 / T
d1 = D / T * (30 * s0 ** 2 - 60 * s0 ** 3 + 30 * s0 ** 4)
d2 = D / T ** 2 * (60 * s0 - 180 * s0 ** 2 + 120 * s0 ** 3)
d3 = D / T ** 3 * (60 - 360 * s0 + 360 * s0 ** 2)
d4 = D / T ** 4 * (-360 + 720 * s0)
out(d3_6=d3 / 6, d4_12=d4 / 12)
rows = []
for h in (0.1, 0.01, 0.001):
    c = (th(0.5 + h) - th(0.5 - h)) / (2 * h)
    s2 = (th(0.5 + h) - 2 * th(0.5) + th(0.5 - h)) / h ** 2
    rows.append(f"| {h:g} | {(c - d1) / h ** 2:.6f} | {(s2 - d2) / h ** 2:.6f} |")
out(diff_tab="\n".join(rows))

# 拉格朗日余项的中值点：eʰ = 1 + h + h²/2 + e^{θh}h³/6，θ → 1/4
rows = []
for h in (1.0, 0.1, 0.01):
    rem = math.expm1(h) - h - h * h / 2
    theta = math.log(rem * 6 / h ** 3) / h
    rows.append(f"| {h:g} | {theta:.5f} |")
out(lag_tab="\n".join(rows))
