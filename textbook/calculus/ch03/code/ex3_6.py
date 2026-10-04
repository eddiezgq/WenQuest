"""3.6 节：数 e——(1 + 1/n)ⁿ 与 Σ 1/k! 的比较（高精度）；(1 + 1/n)ⁿ 在双精度下的崩溃；
电机转速的离散化 (1 − T_s/τ)ⁿ 趋于 e^(−t/τ)。"""
import math
from decimal import Decimal, getcontext
from fractions import Fraction

from bookout import out

getcontext().prec = 50
E = sum(Decimal(1) / math.factorial(k) for k in range(60))          # e 的 50 位近似
out(e30=str(E)[:32])


def tex(d):
    m, e = f"{float(d):.2e}".split("e")
    return f"${m}\\times 10^{{{int(e)}}}$"


rows = []
for n in (1, 2, 5, 10, 100, 1000, 10**6):
    en = (Decimal(1) + Decimal(1) / n) ** n
    bn = sum(Decimal(1) / math.factorial(k) for k in range(min(n, 40) + 1)) if n <= 40 else None
    rows.append((n, en, bn))
lines = []
for n, en, bn in rows:
    lines.append(f"| {n} | {float(en):.10f} | {tex(E - en)} | " + (f"{float(bn):.10f} | {tex(E - bn)} |" if bn is not None and n <= 10 else "— | — |"))
out(e_table="\n".join(lines))
# e − e_n ≈ e/(2n)
n = 10**6
en = (Decimal(1) + Decimal(1) / n) ** n
out(gap_1e6=float(E - en), approx_1e6=float(E) / (2 * n))
# Σ_{k≤n} 1/k! 的误差上界 1/(n!·n)
b10 = sum(Fraction(1, math.factorial(k)) for k in range(11))
out(b10_err=float(E - Decimal(b10.numerator) / Decimal(b10.denominator)), b10_bound=1 / (math.factorial(10) * 10))

# 双精度下 (1 + 1/n)^n
dbl = {k: (1 + 1 / 10.0**k) ** (10.0**k) for k in (6, 8, 12, 15, 16, 17)}
out(**{f"f{k}": v for k, v in dbl.items()}, e=math.e)

# 电机转速：dω/dt = (ω∞ − ω)/τ，τ = 0.05 s，ω∞ = 300 rad/s；每 T_s 更新一次：ω_{k+1} = ω_k + (T_s/τ)(ω∞ − ω_k)
tau, winf, t = 0.05, 300.0, 0.1
exact = winf * (1 - math.exp(-t / tau))
for Ts in (0.01, 0.001, 0.0001):
    n = round(t / Ts)
    w = winf * (1 - (1 - Ts / tau) ** n)
    out(**{f"w_{round(Ts * 1e4)}": w})
out(w_exact=exact, tau=tau, winf=winf, t_motor=t)
