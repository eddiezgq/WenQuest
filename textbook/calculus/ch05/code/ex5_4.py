"""5.4 节：闭区间上连续函数的性质——两节连杆能伸到的距离（介值定理给出工作空间是圆环）；
cos x = x 的根；四足机器人（四条腿的桌子）在不平地面上转一个角度就能四脚着地。"""
import math

import numpy as np

from _arm import L1, L2
from bookout import out

r = lambda t2: math.sqrt(L1 * L1 + L2 * L2 + 2 * L1 * L2 * math.cos(t2))
out(r_max=r(0) * 1000, r_min=r(math.pi) * 1000)
d = 0.6
lo, hi = 0.0, math.pi              # r(0) > d > r(π)，r 连续，介值定理保证有根
for _ in range(60):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if r(m) > d else (lo, m)
out(d_mm=d * 1000, t2_bis=math.degrees(lo), t2_exact=math.degrees(math.acos((d * d - L1 * L1 - L2 * L2) / (2 * L1 * L2))))

# 不动点：cos x = x
g = lambda x: math.cos(x) - x
lo, hi = 0.0, 1.0
for _ in range(60):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if g(m) > 0 else (lo, m)
out(fix=lo, cos0=g(0.0), cos1=g(1.0))

# 四足机器人：地面高度 z(x, y)，四只脚在半径 ρ 的正方形四角，整体转 φ 角。
# 先让 1、2、3 号脚着地，4 号脚离地的高度正比于 D(φ) = z₁ + z₃ − z₂ − z₄；而 D(φ + π/2) = −D(φ)。
z = lambda x, y: 0.03 * math.sin(2.1 * x + 0.4) * math.cos(1.7 * y) + 0.02 * math.sin(3.3 * x * y + 1.0) + 0.015 * x
rho = 0.35


def D(phi):
    h = [z(rho * math.cos(phi + k * math.pi / 2), rho * math.sin(phi + k * math.pi / 2)) for k in range(4)]
    return h[0] + h[2] - h[1] - h[3]


lo, hi = 0.0, math.pi / 2
out(D0_mm=D(lo) * 1000, D90_mm=D(hi) * 1000)
assert (D(lo) > 0) != (D(hi) > 0)
for _ in range(60):
    m = (lo + hi) / 2
    lo, hi = (m, hi) if (D(m) > 0) == (D(0.0) > 0) else (lo, m)
out(phi_star=math.degrees(lo), D_star=D(lo))
phis = np.linspace(0, 2 * math.pi, 721)
out(n_zero=int(np.sum(np.diff(np.sign([D(p) for p in phis])) != 0)))
