"""3.1 节：数列的几个来源——刘徽割圆的面积数列（以及倍增公式的数值稳定性）；复利数列；
求平方根的迭代数列；斐波那契数列相邻两项之比；纸张对折。"""
import math
from fractions import Fraction

from bookout import out

# 刘徽割圆：半径 1，内接正 n 边形边长 a_n。倍增公式 a_{2n} = √(2 − √(4 − a_n²))，
# 等价的写法 a_{2n} = a_n / √(2 + √(4 − a_n²)) 不含相近数相减。正 2n 边形面积 S_{2n} = n a_n / 2。
a_bad = a_good = 1.0
n = 6
rows = []
for k in range(26):                    # 6, 12, 24, …, 6·2^25
    S_bad, S_good = n * a_bad / 2, n * a_good / 2       # 这是正 2n 边形的面积
    rows.append((2 * n, S_good, S_bad))
    a_bad = math.sqrt(2 - math.sqrt(4 - a_bad * a_bad))
    a_good = a_good / math.sqrt(2 + math.sqrt(4 - a_good * a_good))
    n *= 2
sel = [r for r in rows if r[0] in (12, 24, 48, 96, 192, 3072)]


def sci(v, d=2):
    m, e = f"{v:.{d}e}".split("e")
    return f"${m}\\times 10^{{{int(e)}}}$"


out(liu_table="\n".join(f"| {m} | {s:.8f} | {sci(math.pi - s)} |" for m, s, _ in sel))
out(S12=rows[0][1], S192=rows[4][1], S3072=rows[8][1])
# 边数很大时，不稳定的公式失效
big = rows[-1]
eb = [abs(math.pi - r[2]) for r in rows]
i_st = next(i for i in range(1, len(rows)) if eb[i] >= eb[i - 1])           # 误差第一次不再减小
i_wo = next(i for i in range(i_st, len(rows)) if eb[i] > 10 * eb[i_st])     # 误差明显回升
out(n_big=big[0], S_big_good=big[1], S_big_bad=big[2], pi=math.pi, n_stall=rows[i_st - 1][0], e_stall=eb[i_st],
    n_worse=rows[i_wo][0], e_worse=eb[i_wo])

# 复利：年利率 100%，一年结息 n 次
for n in (1, 2, 12, 365, 8760):
    out(**{f"c{n}": (1 + 1 / n) ** n})

# 求 √2 的迭代：x_{k+1} = (x_k + 2/x_k)/2，从 x_1 = 2 出发；用分数精确计算
x = Fraction(2)
it = []
for k in range(1, 6):
    it.append(x)
    x = (x + 2 / x) / 2
out(heron="、".join(f"{float(v):.12f}" for v in it[:5]), heron_frac="、".join(f"\\tfrac{{{v.numerator}}}{{{v.denominator}}}" for v in it[:4]))

# 斐波那契数列与相邻两项之比
F = [1, 1]
while len(F) < 30:
    F.append(F[-1] + F[-2])
phi = (1 + math.sqrt(5)) / 2
out(fib="、".join(map(str, F[:12])), r10=F[10] / F[9], r20=F[20] / F[19], r29=F[29] / F[28], phi=phi)

# 纸张对折：厚 0.1 mm，对折 n 次厚 0.1·2^n mm；地月平均距离约 38.4 万 km
t = lambda n: 0.1e-3 * 2**n
k = next(n for n in range(1, 100) if t(n) > 3.844e8)
out(fold_k=k, fold_km=t(k) / 1000, fold_10=t(10) * 1000, fold_20=t(20))
