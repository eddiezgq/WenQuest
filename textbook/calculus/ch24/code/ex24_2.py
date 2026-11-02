"""24.2 节：幂级数的运算。
(1) 逐项积分得到 arctan x 的级数；单片机上计算 atan2（航向角）：先把自变量化到 |t| ≤ tan 15°，再用几项级数，
    求单精度所需的项数与全实轴上的最大误差；不做范围化简时 x 接近 1 要多少项；
(2) 逐项积分得到 ln(1 + x)，ln 2 的两种算法：x = 1 处的慢级数与 ln((1+y)/(1−y)) = 2(y + y³/3 + …)（y = 1/3）；
(3) 逐项求导：Σ n xⁿ = x/(1 − x)²。"""
import math

import numpy as np

from bookout import out

t15 = math.tan(math.pi / 12)
# 截断误差 ≤ 下一项 t^{2m+1}/(2m+1)（交错级数）；要 ≤ 2^-24 · |atan t| ≈ 2^-24 · t（相对误差）
m = 1
while t15 ** (2 * m + 1) / (2 * m + 1) >= 2 ** -24 * math.atan(t15):
    m += 1
out(at_t15=t15, at_m=m, at_bound=t15 ** (2 * m + 1) / (2 * m + 1) / math.atan(t15))


def my_atan(x, m=m):
    s = 1.0
    if x < 0:
        x, s = -x, -1.0
    off = 0.0
    if x > 1:
        x, off, sgn = 1 / x, math.pi / 2, -1.0
    else:
        sgn = 1.0
    off2 = 0.0
    if x > t15:
        x, off2 = (math.sqrt(3) * x - 1) / (x + math.sqrt(3)), math.pi / 6
    p = sum((-1) ** k * x ** (2 * k + 1) / (2 * k + 1) for k in range(m))
    return s * (off + sgn * (off2 + p))


xs = np.concatenate([np.linspace(-50, 50, 200001), np.linspace(-1.2, 1.2, 100001)])
rel = max(abs(my_atan(x) - math.atan(x)) / max(abs(math.atan(x)), 1e-300) for x in xs if x != 0)
out(at_maxrel=rel)
# 不化简：x = 0.9、0.99 时同样相对精度所需的项数
for x in (0.9, 0.99):
    n, S = 0, 0.0
    while abs(S - math.atan(x)) >= 2 ** -24 * math.atan(x):
        S += (-1) ** n * x ** (2 * n + 1) / (2 * n + 1)
        n += 1
    out(**{f"at_naive_{round(x * 100)}": n})
# (2) ln 2
y = 1 / 3
n, S = 0, 0.0
while abs(S - math.log(2)) > 1e-15:
    S += 2 * y ** (2 * n + 1) / (2 * n + 1)
    n += 1
out(ln2_fast_n=n, ln2_slow_n_est=round(1 / (2 * 1e-15)))
# (3) 逐项求导
x = 0.5
out(d_sum=math.fsum(k * x ** k for k in range(1, 200)), d_formula=x / (1 - x) ** 2)
