"""5.3 节：连续函数的运算与初等函数的连续性——2^x 在 0 处的夹逼；两节连杆正运动学的连续性
（关节角误差趋于 0，末端位置误差趋于 0）；幂指函数的极限。"""
import math

import numpy as np

from _arm import L1, L2
from bookout import out

# 2^x 在 0 处：0 < x < 1/n 时 1 < 2^x < 2^(1/n)，而 2^(1/n) → 1
out(r2_10=2 ** (1 / 10), r2_1000=2 ** (1 / 1000), r2_1e6=2 ** (1 / 1e6))

# 正运动学 p(θ₁, θ₂) = (l₁cos θ₁ + l₂cos(θ₁+θ₂), l₁sin θ₁ + l₂sin(θ₁+θ₂))
def fk(t1, t2):
    return np.stack([L1 * np.cos(t1) + L2 * np.cos(t1 + t2), L1 * np.sin(t1) + L2 * np.sin(t1 + t2)])


rng = np.random.default_rng(53)
t1, t2 = rng.uniform(-math.pi, math.pi, 200000), rng.uniform(-math.pi, math.pi, 200000)
rows = []
for d in (1e-2, 1e-3, 1e-4, 1e-5):
    s1, s2 = rng.choice([-1, 1], t1.size), rng.choice([-1, 1], t1.size)
    dp = np.linalg.norm(fk(t1 + s1 * d, t2 + s2 * d) - fk(t1, t2), axis=0)
    rows.append(f"| $10^{{{int(round(math.log10(d)))}}}$ | {dp.max() * 1000:.4g} | {(L1 + 2 * L2) * d * 1000:.4g} |")
out(fk_tab="\n".join(rows), bound_coef=L1 + 2 * L2, reach=(L1 + L2) * 1000)

# 幂指函数：u^v = e^{v ln u}
f = lambda x: (1 + 2 * x) ** (1 / math.sin(x))
out(pe_1=f(0.01), pe_2=f(1e-4), e2=math.e ** 2, xx_3=1e-3 ** 1e-3, xx_6=1e-6 ** 1e-6)
