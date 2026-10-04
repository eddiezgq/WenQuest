"""4.5 节：两个重要极限——cos x < sin x / x < 1 的数值核对；(1 + 1/x)^x 在非整数 x 处；
差速 AGV 的里程计公式在转速 ω → 0 时的极限（直线运动），以及按原式在 ω = 0 处计算的问题。"""
import math

import numpy as np

from bookout import out

xs = np.linspace(1e-4, math.pi / 2 - 1e-4, 100001)
r = np.sin(xs) / xs
assert np.all(np.cos(xs) < r) and np.all(r < 1)
out(sq_ok=1)

for x in (10.5, 1000.5, -1000.5):
    out(**{f"ex_{str(x).replace('.', '_').replace('-', 'm')}": (1 + 1 / x) ** x})
for u in (0.1, 0.001):
    out(**{f"ln_{str(u).replace('.', '_')}": math.log1p(u) / u, f"exp_{str(u).replace('.', '_')}": math.expm1(u) / u})

# 差速 AGV：车速 v，转速 ω，在 T 内保持不变；车体坐标系中的位移
v, T = 1.0, 0.02


def disp(w):
    return v / w * math.sin(w * T), v / w * (1 - math.cos(w * T))


rows = []
for w in (2.0, 0.5, 0.01, 1e-4):
    dx, dy = disp(w)
    rows.append(f"| {w:g} | {dx * 1000:.6f} | {dy * 1000:.6f} |")
out(odo_tab="\n".join(rows), straight_mm=v * T * 1000)
try:
    disp(0.0)
    zero = "ok"
except ZeroDivisionError:
    zero = "ZeroDivisionError"
out(zero_err=zero)
# 小角度时用 sin(ωT)/(ωT) 的形式：Δx = vT · sinc，Δy = vT · (1 − cos ωT)/(ωT)
