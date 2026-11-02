"""第 24 章部分习题答案中的数值。"""
import math

from scipy import special
from scipy.optimize import brentq

from bookout import out

# 24.2.6：|y| ≤ (√2 − 1)/(√2 + 1)，ln m = 2(y + y³/3 + …)，单精度（相对 2^-24）所需项数（按 ln m 的大小估计）
y = (math.sqrt(2) - 1) / (math.sqrt(2) + 1)
m = 1
while 2 * y ** (2 * m + 1) / (2 * m + 1) / (1 - y * y) >= 2 ** -24 * 2 * y:
    m += 1
out(e2426_y=y, e2426_m=m)
# 24.4.2：∛1.03、√26 = 5√(1 + 1/25)
def binom_terms(a, x, tol):
    s, c, n = 1.0, 1.0, 0
    while True:
        c *= (a - n) / (n + 1) * x
        n += 1
        if abs(c) < tol:
            return s, n
        s += c
v1, n1 = binom_terms(1 / 3, 0.03, 1e-6)
v2, n2 = binom_terms(0.5, 1 / 25, 1e-6 / 5)
out(e2442_v1=v1, e2442_n1=n1, e2442_v2=5 * v2, e2442_n2=n2)
# 24.4.3
out(e2443=1 / math.cos(math.radians(1)) - 1)
# 24.4.6：π = 6 arcsin(1/2)
x, S, n, c = 0.5, 0.0, 0, 1.0
while True:
    term = c * x ** (2 * n + 1) / (2 * n + 1)
    S += term
    n += 1
    c *= (2 * n - 1) / (2 * n)
    if 6 * c * x ** (2 * n + 1) / (2 * n + 1) < 1e-10:
        break
out(e2446_n=n, e2446_err=abs(6 * S - math.pi))
# 24.5.1
out(e2451_ii=math.exp(-math.pi / 2))
# 24.6.1：Si(0.5) = Σ (−1)ⁿ x^{2n+1}/((2n+1)(2n+1)!)
x, n, S = 0.5, 0, 0.0
while True:
    t = x ** (2 * n + 1) / ((2 * n + 1) * math.factorial(2 * n + 1))
    if t < 1e-8:
        break
    S += (-1) ** n * t
    n += 1
out(e2461_v=S, e2461_n=n, e2461_true=special.sici(0.5)[0])
# 24.6.2：∫₀¹ cos x² = Σ (−1)ⁿ/((2n)!(4n+1))
n, S = 0, 0.0
while True:
    t = 1 / (math.factorial(2 * n) * (4 * n + 1))
    if t < 1e-6:
        break
    S += (-1) ** n * t
    n += 1
out(e2462_v=S, e2462_n=n)
# 24.6.6：erf(a/(σ√2)) = 0.999
z = brentq(lambda z: special.erf(z) - 0.999, 1, 5)
out(e2466_k=z * math.sqrt(2), e2466_a=z * math.sqrt(2) * 0.02)
