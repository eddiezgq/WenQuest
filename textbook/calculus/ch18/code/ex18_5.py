"""18.5 节：基本定理的条件——F(x) = x² sin(1/x)：处处可导，F′ 有界、在 0 处不连续，仍可积，∫₀¹F′ = F(1) = sin 1；
G(x) = x² sin(1/x²)：处处可导，但 G′ 在 0 附近无界，不是黎曼可积的（只能按反常积分理解）。"""
import math

from bookout import out

Fp = lambda x: 2 * x * math.sin(1 / x) - math.cos(1 / x) if x != 0 else 0.0
Gp = lambda x: 2 * x * math.sin(1 / x ** 2) - 2 / x * math.cos(1 / x ** 2) if x != 0 else 0.0
rows = []
for n in (1000, 10000, 100000):
    h = 1 / n
    s = sum(Fp((i + 0.5) * h) * h for i in range(n))
    rows.append(f"| {n} | {s:.6f} | {s - math.sin(1):+.1e} |")
out(F_tab="\n".join(rows), sin1=math.sin(1))
# G′ 在 [ε, 1] 上的最大值
rows = []
for eps in (0.1, 0.01, 0.001):
    m = max(abs(Gp(eps + (1 - eps) * k / 200000)) for k in range(200001))
    rows.append(f"| {eps:g} | {m:.3g} |")
out(G_tab="\n".join(rows))
