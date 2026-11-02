"""24.3 节：泰勒级数与麦克劳林级数。
(1) eˣ 的级数在 x = 10 与 x = −10 处：双精度直接求和的相对误差（负数时大量相消），改用 1/e¹⁰；
(2) ln(1 + x) 在 x = −0.75：拉格朗日余项给出的界无用，积分余项（逐项积分几何级数）给出可用的界；
(3) 光滑但不解析：ψ(x) = e^{−1/x}（x > 0）、ψ(x) = 0（x ≤ 0）；用它做的 C^∞ 平滑过渡（夹爪力的斜坡），
    与三次、五次多项式过渡比较一阶、二阶导数的峰值。"""
import math

import numpy as np

from bookout import out


def exp_series(x, tol=1e-17):
    s, t, k = 1.0, 1.0, 0
    terms = []
    while abs(t) > tol * abs(s) or k < 5:
        k += 1
        t *= x / k
        s += t
        terms.append(abs(t))
    return s, k, max(terms)


for x in (10, -10):
    s, k, big = exp_series(x)
    tag = "p" if x > 0 else "m"
    out(**{f"ex_{tag}_val": s, f"ex_{tag}_rel": abs(s - math.exp(x)) / math.exp(x), f"ex_{tag}_n": k, f"ex_{tag}_big": big})
s, k, _ = exp_series(10)
out(ex_inv_rel=abs(1 / s - math.exp(-10)) / math.exp(-10))
# (2) ln(1+x)，x = −0.75
x = -0.75
rows = []
for n in (5, 10, 20, 40):
    Sn = sum((-1) ** (k + 1) * x ** k / k for k in range(1, n + 1))
    err = abs(Sn - math.log1p(x))
    lag = (abs(x) / (1 + x)) ** (n + 1) / (n + 1)          # 拉格朗日余项的最坏情形（ξ 取到 x 附近）
    integ = abs(x) ** (n + 1) / ((n + 1) * (1 - abs(x)))
    rows.append(f"| {n} | {err:.2e} | {lag:.2e} | {integ:.2e} |")
out(ln_tab="\n".join(rows))


# (3) 平滑过渡
def psi(x):
    return np.where(x > 0, np.exp(-1 / np.maximum(x, 1e-300)), 0.0)


def step_inf(x):
    return psi(x) / (psi(x) + psi(1 - x))


t = np.linspace(0, 1, 200001)
h = t[1] - t[0]
for name, f in (("c3", lambda x: 3 * x ** 2 - 2 * x ** 3), ("c5", lambda x: 10 * x ** 3 - 15 * x ** 4 + 6 * x ** 5), ("inf", step_inf)):
    y = f(t)
    d1 = np.gradient(y, h); d2 = np.gradient(d1, h)
    sl = slice(50, -50)
    out(**{f"st_{name}_d1": float(np.max(np.abs(d1[sl]))), f"st_{name}_d2": float(np.max(np.abs(d2[sl])))})
# ψ 在 0 附近有多小：x = 0.1、0.05 处
out(psi_01=math.exp(-10), psi_005=math.exp(-20))
