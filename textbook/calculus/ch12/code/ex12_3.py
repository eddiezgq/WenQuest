"""12.3 节：定积分的定义——任意分点、任意取点的黎曼和随细度趋于零而收敛（连续函数 e^{−x²} 在 [0, 2] 上）。
"""
import math
import random

from bookout import out

rnd = random.Random(123)
f = lambda x: math.exp(-x * x)
ref = 0.5 * math.sqrt(math.pi) * math.erf(2.0)
rows = []
for n in (10, 100, 1000, 10000):
    sums = []
    for trial in range(5):
        cuts = sorted([0.0, 2.0] + [rnd.uniform(0, 2) for _ in range(n - 1)])
        s = 0.0
        mesh = 0.0
        for a, b in zip(cuts, cuts[1:]):
            s += f(rnd.uniform(a, b)) * (b - a)
            mesh = max(mesh, b - a)
        sums.append(s)
    rows.append(f"| {n} | {min(sums):.6f} | {max(sums):.6f} | {max(abs(x - ref) for x in sums):.1e} |")
out(rand_tab="\n".join(rows), ref=ref)
