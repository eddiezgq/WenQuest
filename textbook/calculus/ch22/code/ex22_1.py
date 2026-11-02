"""22.1 节：欧拉法的误差。y′ = x − y、y(0) = 2：局部截断误差（一步）与 h² 成正比、整体误差与 h 成正比，
与定理 19.6.1 的误差界比较；单精度（float32）计算时舍入误差使步长过小反而变差。"""
import math

import numpy as np

from bookout import out

f = lambda x, y: x - y
ex = lambda x: x - 1 + 3 * math.exp(-x)
rows = []
for h in (0.2, 0.1, 0.05, 0.025):
    loc = abs(2 + h * f(0, 2) - ex(h))
    n = round(2 / h)
    x, y = 0.0, 2.0
    for _ in range(n):
        y += h * f(x, y)
        x += h
    glob = abs(y - ex(2))
    # 误差界：L = 1，M = max|y″| = max 3e^{-x} = 3
    bound = 3 * h / 2 * (math.exp(2) - 1)
    rows.append(f"| {h:g} | {loc:.2e} | {loc / h ** 2:.3f} | {glob:.2e} | {glob / h:.3f} | {bound:.2e} |")
out(err_tab="\n".join(rows))

# 单精度：y′ = −y，y(0) = 1，积到 x = 1，与 e^{-1} 比较
rows = []
best = (None, 1e9)
for k in range(1, 8):
    h = 10.0 ** (-k / 1.0) if k <= 6 else 10.0 ** (-6.5)
    n = int(round(1 / h))
    if n > 4_000_000:
        continue
    y32 = np.float32(1.0)
    h32 = np.float32(1.0 / n)
    for _ in range(n):
        y32 = y32 - h32 * y32
    y64 = 1.0
    h64 = 1.0 / n
    for _ in range(n):                      # 双精度也逐步迭代
        y64 = y64 - h64 * y64
    e32 = abs(float(y32) - math.exp(-1))
    e64 = abs(y64 - math.exp(-1))
    tr = abs((1 - 1 / n) ** n - math.exp(-1))      # 截断误差（准确算术下欧拉法的误差）
    rows.append(f"| {n} | {tr:.2e} | {e64:.2e} | {e32:.2e} |")
    if e32 < best[1]:
        best = (n, e32)
out(fp_tab="\n".join(rows), fp_best_n=best[0], fp_best_e=best[1], fp_eps32=float(np.finfo(np.float32).eps), fp_eps64=float(np.finfo(np.float64).eps))
