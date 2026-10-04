"""5.6 节：一致连续——x² 在不同点处能用的最大 δ；√x 的 δ = ε²；肘关节角 θ₂(r) 在伸直位置附近的 δ 与 ε² 成正比；
关节编码器的分辨率：末端定位误差不超过 ε 时，关节角误差允许多大（利普希茨常数 l₁ + 2l₂）。"""
import math

from _arm import L1, L2
from bookout import out

eps = 0.01
rows = []
for x0 in (1, 10, 100, 1000):
    d = min(math.sqrt(x0 * x0 + eps) - x0, x0 - math.sqrt(x0 * x0 - eps))     # |x² − x0²| < ε 的最大 δ
    rows.append(f"| {x0} | {d:.3e} | {eps / (2 * x0):.3e} |")
out(sq_tab="\n".join(rows))

# √x：|√x − √y| ≤ √|x − y|，δ = ε² 处处可用；x0 = 0 处最大的 δ 恰为 ε²
out(sqrt_d0=eps ** 2, sqrt_d1=min((1 + eps) ** 2 - 1, 1 - (1 - eps) ** 2))

# 肘关节角 θ₂(r) = arccos((r² − l₁² − l₂²)/(2l₁l₂))，r ∈ [|l₁ − l₂|, l₁ + l₂]
R = L1 + L2
th2 = lambda r: math.acos(max(-1.0, min(1.0, (r * r - L1 * L1 - L2 * L2) / (2 * L1 * L2))))
rows = []
rr = lambda t: math.sqrt(L1 * L1 + L2 * L2 + 2 * L1 * L2 * math.cos(t))      # 腕心距离 r(θ₂)
for e_deg in (1.0, 0.1, 0.01):
    e = math.radians(e_deg)
    d0 = R - rr(e)                                     # 伸直位置：θ₂(R − δ) = ε
    dpi = rr(math.pi - e) - rr(math.pi)                # 完全折回：r = |l₁ − l₂| 处
    h = math.pi / 2
    d90 = min(rr(h - e) - rr(h), rr(h) - rr(h + e))    # θ₂ = 90° 处
    rows.append(f"| {e_deg:g} | {d0 * 1000:.3e} | {dpi * 1000:.3e} | {d90 * 1000:.3e} |")
out(th_tab="\n".join(rows), th_coef=L1 * L2 / (2 * R))

# 编码器：末端定位误差 ≤ 0.1 mm，两个关节角误差都 ≤ δ 时，|Δp| ≤ (l₁ + 2l₂)δ
eps_p = 1e-4
K = L1 + 2 * L2
dth = eps_p / K
out(K=K, dth=dth, counts=2 * math.pi / dth, bits=math.ceil(math.log2(2 * math.pi / dth)))
