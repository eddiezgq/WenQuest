"""6.3 节：致密性定理——有界数列 sin n 不收敛，但有收敛于 0.5 的子数列；用二分法“挑”子数列；
齿轮的“追齿”设计：两齿数互素时每个齿与对方每个齿都啮合；无理比时啮合位置在一圈上处处稠密。"""
import math

import numpy as np

from bookout import out

N = 10 ** 6
n = np.arange(1, N + 1)
s = np.sin(n.astype(np.float64))

# 挑出 sin n_k → 0.5 的子数列：n_k 递增，|sin n_k − 0.5| < 10^(−k)
rows, last = [], 0
for k in range(1, 6):
    idx = np.nonzero((n > last) & (np.abs(s - 0.5) < 10.0 ** (-k)))[0]
    i = int(idx[0])
    last = int(n[i])
    rows.append(f"| {k} | {last} | {s[i]:.8f} |")
out(sub_tab="\n".join(rows))

# 二分法证明的“算法版”：在 [−1, 1] 上二分，每次保留含有更多项（代表“无穷多项”）的一半
a, b, picks, last = -1.0, 1.0, [], 0
for k in range(12):
    m = (a + b) / 2
    left = np.count_nonzero((s >= a) & (s <= m))
    right = np.count_nonzero((s >= m) & (s <= b))
    a, b = (a, m) if left >= right else (m, b)
    idx = np.nonzero((n > last) & (s >= a) & (s <= b))[0]
    last = int(n[idx[0]])
    picks.append((k + 1, a, b, last))
out(bw_tab="\n".join(f"| {k} | [{a:.6f}, {b:.6f}] | {nk} |" for k, a, b, nk in picks))

# 追齿：小轮 z1 齿、大轮 z2 齿，小轮第 0 齿依次与大轮哪些齿啮合
for z1, z2 in ((20, 40), (20, 41), (23, 37)):
    partners = {(z1 * k) % z2 for k in range(z2)}
    out(**{f"hunt_{z1}_{z2}": len(partners), f"lcm_{z1}_{z2}": z1 * z2 // math.gcd(z1, z2)})

# 无理比（摩擦轮或带传动，不打滑）：每转一圈，接触点前进 α 圈（α = √2 − 1），前 M 个接触点在一圈上的最大空隙与最小间距
alpha = math.sqrt(2) - 1
for M in (10, 100, 1000):
    pts = np.sort((np.arange(M) * alpha) % 1.0)
    gaps = np.diff(np.concatenate([pts, [pts[0] + 1]]))
    out(**{f"gap_{M}": float(gaps.max()), f"mind_{M}": float(gaps.min())})
