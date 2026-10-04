"""6.7 节：上极限与下极限——关节跟踪误差在周期扰动下不收敛，尾部上确界单调递减，趋于上极限（最终误差界）；
数列 (−1)ⁿ(1 + 1/n) 的尾部上确界、下确界。"""
import math

import numpy as np

from bookout import out

Ts = 0.01
t = np.arange(0, 200, Ts)
e = 0.2 * np.exp(-t / 2) * np.cos(9 * t) + 0.02 * np.sin(2 * math.pi * 1.3 * t) + 0.01 * np.sin(2 * math.pi * math.sqrt(2) * t)
rows = []
for T0 in (0, 2, 5, 10, 20, 100):
    tail = e[int(round(T0 / Ts)):]
    rows.append(f"| {T0} | {tail.max() * 1000:.2f} | {tail.min() * 1000:.2f} |")
out(err_tab="\n".join(rows), amp_sum=30.0)

a = lambda n: (-1) ** n * (1 + 1 / n)
rows = []
for n0 in (1, 2, 10, 100, 1000):
    tail = [a(n) for n in range(n0, n0 + 2001)]
    rows.append(f"| {n0} | {max(tail):.4f} | {min(tail):.4f} |")
out(alt_tab="\n".join(rows))
