"""8.2 节：线性近似与误差估计——常见函数在一点附近的线性近似及误差、误差上界 M·h²/2；
关节重力矩在工作点 θ₀ = 30° 附近的线性化：误差不超过 1% 的范围；NTC 热敏电阻在 50 °C 附近的线性化。"""
import json
import math
from pathlib import Path

from _traj import ur5e_links
from bookout import out

rows = []
cases = [
    ("√(4 + h)", lambda h: math.sqrt(4 + h), 2, 0.25, 1 / (4 * 3.9 ** 1.5)),          # f″ = −¼ x^(−3/2)，在 [3.9, 4.1] 上 |f″| ≤ ¼·3.9^(−3/2)
    ("e^h", lambda h: math.exp(h), 1, 1, math.exp(0.1)),
    ("ln(1 + h)", lambda h: math.log1p(h), 0, 1, 1 / 0.9 ** 2),
    ("sin(π/6 + h)", lambda h: math.sin(math.pi / 6 + h), 0.5, math.cos(math.pi / 6), math.sin(math.pi / 6 + 0.1)),   # |f″| = sin，在区间上不超过 sin(π/6 + 0.1)
]
for name, f, f0, d0, M in cases:
    for h in (0.1, -0.1):
        lin = f0 + d0 * h
        rows.append(f"| {name}，h = {h:g} | {f(h):.8f} | {lin:.8f} | {abs(f(h) - lin):.2e} | {M * h * h / 2:.2e} |")
out(lin_tab="\n".join(rows))

# 关节重力矩：额定负载 m 在末端，臂伸直长 L = l₁ + l₂，θ 从水平量起，τ = m g L cos θ
e = json.loads((Path(__file__).resolve().parents[2] / "models" / "B-ARM-UR5E" / "entry.json").read_text(encoding="utf-8"))
m = e["datasheet"]["values"]["payload_kg"]
l1, l2 = ur5e_links()
L, g = l1 + l2, 9.81
th0 = math.radians(30)
tau = lambda th: m * g * L * math.cos(th)
lin = lambda th: tau(th0) - m * g * L * math.sin(th0) * (th - th0)
out(m=m, L=L, tau0=tau(th0), k=m * g * L * math.sin(th0))
# 误差不超过 τ₀ 的 1% 的范围（两侧分别求）
def edge(sign):
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if abs(tau(th0 + sign * mid) - lin(th0 + sign * mid)) <= 0.01 * tau(th0):
            lo = mid
        else:
            hi = mid
    return math.degrees(lo)
out(range_plus=edge(1), range_minus=edge(-1), range_bound=math.degrees(math.sqrt(2 * 0.01 * math.cos(th0))))

# NTC 热敏电阻（2.5 节）：R(T) = R₀ exp[B(1/T − 1/T₀)]，在 50 °C 处线性化
R0, B, T0 = 10.0, 3950.0, 298.15
R = lambda T: R0 * math.exp(B * (1 / T - 1 / T0))
Ta = 323.15
dR = -B / Ta ** 2 * R(Ta)
out(R50=R(Ta), dR50=dR)
rows = []
for dt in (-10, -5, 5, 10):
    T = Ta + dt
    approx = R(Ta) + dR * dt
    rows.append(f"| {50 + dt} | {R(T):.4f} | {approx:.4f} | {abs(R(T) - approx) / R(T) * 100:.2f} |")
out(ntc_tab="\n".join(rows))
