"""24.6 节：幂级数的应用。
(1) 误差函数：交错级数 erf x = (2/√π) Σ (−1)ⁿ x^{2n+1}/(n!(2n+1)) 与正项级数 erf x = (2/√π) e^{−x²} Σ 2ⁿ x^{2n+1}/(2n+1)!!，
    在不同 x 处所需项数、最大项与双精度下的相对误差；机器人重复定位误差落在公差内的概率；
(2) ∫₀¹ e^{−x²} dx 的级数（12.4 节）；
(3) 用幂级数解 y′ = x² + y²、y(0) = 0（22.6 节）：系数递推、由系数估计收敛半径（即解趋于无穷的位置）。"""
import math

from scipy import special
from scipy.integrate import solve_ivp

from bookout import out

c = 2 / math.sqrt(math.pi)


def erf_alt(x, rel=1e-17):
    s, n, big = 0.0, 0, 0.0
    t = x                                            # x^{2n+1}/n!
    while True:
        term = t / (2 * n + 1) * (-1) ** n
        s += term
        big = max(big, abs(term))
        if abs(term) < rel * abs(s) and n > 2:
            break
        n += 1
        t *= x * x / n
    return c * s, n + 1, c * big


def erf_pos(x, rel=1e-17):
    s, n, t = 0.0, 0, x                              # 2ⁿ x^{2n+1}/(2n+1)!!
    while True:
        s += t
        if t < rel * s and n > 2:
            break
        n += 1
        t *= 2 * x * x / (2 * n + 1)
    return c * math.exp(-x * x) * s, n + 1


rows = []
for x in (0.5, 1.0, 2.0, 3.0, 5.0):
    a, na, big = erf_alt(x)
    b, nb = erf_pos(x)
    ex = special.erf(x)
    rows.append(f"| {x:g} | {na} | {big:.1e} | {abs(a - ex) / ex:.1e} | {nb} | {abs(b - ex) / ex:.1e} |")
out(erf_tab="\n".join(rows))
# 机器人：重复定位误差 ~ N(0, σ²)，σ = 0.01 mm，公差 ±0.03 mm
sig, tol = 0.01, 0.03
out(rp_p=erf_pos(tol / (sig * math.sqrt(2)))[0], rp_ppm=(1 - erf_pos(tol / (sig * math.sqrt(2)))[0]) * 1e6)
# (2) ∫₀¹ e^{−x²}
S, n = 0.0, 0
while True:
    term = (-1) ** n / (math.factorial(n) * (2 * n + 1))
    S += term
    n += 1
    if 1 / (math.factorial(n) * (2 * n + 1)) < 5e-11:
        break
out(int_val=S, int_terms=n, int_exact=math.sqrt(math.pi) / 2 * special.erf(1))
# (3) Riccati 方程的幂级数解
K = 400
a = [0.0] * (K + 1)
for k in range(K):
    conv = sum(a[i] * a[k - i] for i in range(k + 1))
    a[k + 1] = ((1.0 if k == 2 else 0.0) + conv) / (k + 1)
out(ri_a3=a[3], ri_a7=a[7], ri_a11=a[11])
# 由 a_k ~ C/R^k 估计 R：|a_{k}/a_{k+4}|^{1/4}
for k in (39, 99, 199, 395):
    out(**{f"ri_R_{k}": (a[k] / a[k + 4]) ** 0.25})
blow = solve_ivp(lambda x, y: [x * x + y[0] ** 2], (0, 3), [0.0], events=lambda x, y: y[0] - 1e8, rtol=1e-12, atol=1e-12)
out(ri_blow=float(blow.t_events[0][0]))
for xv in (1.0, 1.9):
    ser = sum(a[k] * xv ** k for k in range(K + 1))
    num = solve_ivp(lambda x, y: [x * x + y[0] ** 2], (0, xv), [0.0], rtol=1e-12, atol=1e-14).y[0, -1]
    out(**{f"ri_ser_{round(xv * 10)}": ser, f"ri_num_{round(xv * 10)}": float(num)})
