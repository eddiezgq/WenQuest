"""6.2 节：确界原理——关节过阻尼响应 q(t) = 1 − e^(−t/τ) 的上确界 1 取不到；
数集 {sin n} 的上确界为 1，前 N 项的最大值越来越接近 1 却永远不等于 1；有理数集 {x : x² < 2} 在实数中的上确界 √2。"""
import math

import numpy as np

from bookout import out

tau = 0.15                                   # 时间常数 / s
out(tau=tau)
for T in (1, 3, 10):
    t = np.linspace(0, T, 100001)
    out(**{f"q_max_{T}": float(np.max(1 - np.exp(-t / tau))), f"q_gap_{T}": float(np.exp(-T / tau))})
# 上确界的 ε 刻画：对 ε，取 t > τ ln(1/ε) 即有 q(t) > 1 − ε
for e in (1e-2, 1e-6):
    out(**{f"t_eps_{-int(math.log10(e))}": tau * math.log(1 / e)})

# sup{sin n : n = 1, 2, …} = 1
rows = []
s = np.sin(np.arange(1, 10 ** 6 + 1, dtype=np.float64))
for N in (10, 100, 10 ** 3, 10 ** 4, 10 ** 5, 10 ** 6):
    k = int(np.argmax(s[:N]))
    rows.append(f"| $10^{{{int(math.log10(N))}}}$ | {k + 1} | {1 - s[k]:.2e} |")
out(sin_tab="\n".join(rows))

# {x ∈ ℚ : x² < 2} 的上确界：用二分法得到一列有理数上界，逼近 √2
from fractions import Fraction
lo, hi = Fraction(1), Fraction(2)
for _ in range(30):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if m * m < 2 else (lo, m)
out(sup_hi=float(hi), sup_hi_den=hi.denominator, sup_gap=float(hi - lo))
