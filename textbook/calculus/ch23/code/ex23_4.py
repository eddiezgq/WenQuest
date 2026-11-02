"""23.4 节：交错级数；绝对收敛与条件收敛。
(1) ln 2 = 1 − 1/2 + 1/3 − …：部分和的误差与莱布尼茨判别法的误差界 1/(n+1)，误差的符号；相邻两个部分和的平均；
(2) 莱布尼茨级数 π/4 = 1 − 1/3 + 1/5 − …：要 6 位有效数字需要多少项；
(3) 控制器里算 sin：|x| ≤ π/4 时泰勒展开是交错级数，取几项使误差小于单精度的精度，与实际误差比较。"""
import math

import numpy as np

from bookout import out

rows = []
for n in (1, 2, 3, 10, 100, 1000):
    S = math.fsum((-1) ** (k + 1) / k for k in range(1, n + 1))
    S2 = S + (-1) ** (n + 2) / (n + 1)
    rows.append(f"| {n} | {S:.6f} | {S - math.log(2):+.2e} | {1 / (n + 1):.2e} | {abs((S + S2) / 2 - math.log(2)):.1e} |")
out(ln_tab="\n".join(rows), ln2=math.log(2))
# 莱布尼茨级数：误差 ≤ 1/(2n+1)；4 倍后 π 的误差 < 5e-6（6 位有效数字）需要的项数
n6 = math.ceil((4 / 5e-6 - 1) / 2)
S = math.fsum((-1) ** k / (2 * k + 1) for k in range(n6))
out(lb_n6=n6, lb_err6=abs(4 * S - math.pi), lb_1000=abs(4 * math.fsum((-1) ** k / (2 * k + 1) for k in range(1000)) - math.pi))
# sin x 在 |x| ≤ π/4：x − x³/3! + …，最后一项 x^(2m−1)/(2m−1)!，误差 ≤ 下一项
x = math.pi / 4
m = 1
while x ** (2 * m + 1) / math.factorial(2 * m + 1) >= 2 ** -24:
    m += 1
out(sin_terms=m, sin_bound=x ** (2 * m + 1) / math.factorial(2 * m + 1), sin_eps=2 ** -24)
xs = np.linspace(-x, x, 20001).astype(np.float32)
acc = np.zeros_like(xs)
term = xs.copy()
for j in range(m):
    acc = (acc + term).astype(np.float32)
    term = (-term * xs * xs / np.float32((2 * j + 2) * (2 * j + 3))).astype(np.float32)
err = np.max(np.abs(acc.astype(np.float64) - np.sin(xs.astype(np.float64))))
out(sin_maxerr=float(err))
# 绝对收敛：Σ|(-1)^k/k²| = π²/6 收敛；Σ|(-1)^k/k| 发散
out(abs_sum=math.pi ** 2 / 6, alt2_sum=math.pi ** 2 / 12)
