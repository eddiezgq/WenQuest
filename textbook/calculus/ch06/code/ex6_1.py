"""6.1 节：有理数的缝隙——用齿数（整数）之比逼近传动比 √2：渐近分数 p/q、误差、齿数上限内的最佳齿轮对；
有理数列 3/2, 7/5, 17/12, … 越来越密集地挤向 √2，却没有有理数极限；十二平均律的半音比 2^(1/12)。"""
import math
from fractions import Fraction

from bookout import out

r2 = math.sqrt(2)


def convergents(x, n):
    """连分数展开的前 n 个渐近分数（用 Fraction 精确计算，x 取浮点值，前十几项足够准确）。"""
    a, cs, h0, h1, k0, k1 = [], [], 0, 1, 1, 0
    y = x
    for _ in range(n):
        ai = math.floor(y)
        a.append(ai)
        h0, h1 = h1, ai * h1 + h0
        k0, k1 = k1, ai * k1 + k0
        cs.append(Fraction(h1, k1))
        y = 1 / (y - ai)
    return a, cs


a, cs = convergents(r2, 9)
out(cf_r2=", ".join(map(str, a)))
rows = [f"| {c.numerator}/{c.denominator} | {float(c):.10f} | {abs(float(c) - r2):.2e} | {abs(float(c) - r2) * c.denominator ** 2:.3f} |" for c in cs]
out(conv_tab="\n".join(rows))
# 有理数列 p/q 满足 p² − 2q² = ±1（佩尔方程），所以 (p/q)² − 2 = ±1/q²
out(pell=", ".join(str(c.numerator ** 2 - 2 * c.denominator ** 2) for c in cs))

# 一对齿轮：两齿数都不超过 N 时，最接近 √2 的比
for N in (40, 100, 200):
    best = min(((abs(p / q - r2), p, q) for q in range(10, N + 1) for p in range(q, N + 1)), key=lambda t: t[0])
    out(**{f"gear_{N}": f"{best[1]}/{best[2]}", f"gear_err_{N}": best[0]})

# π 的渐近分数：22/7（约率）、355/113（密率，祖冲之）
_, cp = convergents(math.pi, 4)
out(pi_conv=", ".join(f"{c.numerator}/{c.denominator}" for c in cp), pi_355=abs(355 / 113 - math.pi))

# 十二平均律：半音之比 2^(1/12)，纯五度 3/2 与七个半音 2^(7/12) 的差（音分，一个八度 1200 音分）
semi = 2 ** (1 / 12)
out(semi=semi, fifth_et=2 ** (7 / 12), fifth_cents=1200 * math.log2(1.5) - 700)

# 两级齿轮系：(p₁/q₁)(p₂/q₂)，每个齿轮 12 到 100 齿
import bisect as _bs

ratios = sorted({(p / q, p, q) for q in range(12, 101) for p in range(12, 101)})
vals = [t[0] for t in ratios]
best = (1, None, None)
for v1, p1, q1 in ratios:
    t = r2 / v1
    i = _bs.bisect_left(vals, t)
    for j in (i - 1, i):
        if 0 <= j < len(vals):
            e = abs(v1 * vals[j] - r2)
            if e < best[0]:
                best = (e, (p1, q1), ratios[j][1:])
(p1, q1), (p2, q2) = best[1], best[2]
out(train=f"({p1}/{q1})·({p2}/{q2})", train_err=best[0])
