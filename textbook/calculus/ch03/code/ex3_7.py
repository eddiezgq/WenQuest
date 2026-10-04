"""3.7 节：无穷小与无穷大——几类趋于无穷的数列增长快慢的比较（取常用对数以免溢出）；斯特林公式；
n^k / aⁿ 的峰值位置。"""
import math

from bookout import out

def lg_row(n):
    return [math.log10(math.log(n)), 0.5 * math.log10(n), math.log10(n), math.log10(n * math.log(n)), 2 * math.log10(n),
            n * math.log10(2), math.lgamma(n + 1) / math.log(10), n * math.log10(n)]


def show(v):
    if v > 4 + 1e-9:
        return f"$10^{{{round(v)}}}$" if abs(v - round(v)) < 1e-9 else f"$10^{{{v:.1f}}}$"
    x = 10 ** v
    return f"{x:.0f}" if x >= 100 else f"{x:.3g}"


rows = []
for n in (10, 100, 1000, 10**6):
    rows.append(f"| $10^{{{round(math.log10(n))}}}$ | " + " | ".join(show(v) for v in lg_row(n)) + " |")
out(growth="\n".join(rows))

# 斯特林公式 n! ~ √(2πn) (n/e)^n：比值趋于 1
for n in (5, 10, 100, 1000):
    st = 0.5 * math.log(2 * math.pi * n) + n * (math.log(n) - 1)
    out(**{f"st{n}": math.exp(math.lgamma(n + 1) - st)})

# n^10 / 1.1^n：先增后减，最大值在 n ≈ 10/ln 1.1 附近，此后趋于 0
f = lambda n: 10 * math.log10(n) - n * math.log10(1.1)
nmax = max(range(1, 2000), key=f)
n_small = next(n for n in range(nmax, 10**5) if f(n) < 0)
out(peak_n=nmax, peak_lg=f(nmax), below1=n_small)
