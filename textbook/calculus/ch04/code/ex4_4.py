"""4.4 节：ε–δ 定义——对 x² 在 2 处、√x 在 a 处，按证明中的公式给出 δ，并在 δ 邻域内密集取点核对；
sin(1/x) 沿两列点的函数值（海涅定理）。"""
import math

import numpy as np

from bookout import out


def check(f, a, L, eps, delta, n=200001):
    x = a + np.linspace(-delta, delta, n)[1:-1]
    x = x[x != a]
    return float(np.max(np.abs(f(x) - L)))


rows = []
for eps in (1.0, 0.1, 0.01, 0.001):
    d = min(1.0, eps / 5)                      # 算例 4.4.2：δ = min(1, ε/5)
    worst = check(lambda x: x * x, 2.0, 4.0, eps, d)
    # 实际上能用的最大 δ：|x² − 4| < ε ⇔ √(4 − ε) < x < √(4 + ε)，取两侧中较小的距离
    dmax = min(2 - math.sqrt(4 - eps), math.sqrt(4 + eps) - 2)
    rows.append(f"| {eps:g} | {d:g} | {worst:.3g} | {dmax:.5g} |")
    assert worst < eps
out(delta_tab="\n".join(rows))

# √x 在 a = 0.25 处：δ = min(a, √a ε)
a = 0.25
for eps in (0.1, 0.001):
    d = min(a, math.sqrt(a) * eps)
    assert check(np.sqrt, a, math.sqrt(a), eps, d) < eps
out(sqrt_ok=1)

# 海涅：x_n = 1/(2nπ + π/2) → 0 时 sin(1/x_n) = 1；y_n = 1/(2nπ − π/2) 时 = −1
xs = [1 / (2 * n * math.pi + math.pi / 2) for n in range(1, 6)]
ys = [1 / (2 * n * math.pi - math.pi / 2) for n in range(1, 6)]
out(heine_x=min(math.sin(1 / v) for v in xs), heine_y=max(math.sin(1 / v) for v in ys), x5=xs[-1])
