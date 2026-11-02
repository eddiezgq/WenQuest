"""20.5 节：欧拉方程。液压夹爪油缸（内半径 20 mm、外半径 25 mm，内压 10 MPa）的拉梅解：径向位移满足欧拉方程
r²u″ + r u′ − u = 0，解 u = A r + B/r；周向应力的最大值与薄壁公式比较；用边值问题的数值解核对。"""
import math

import numpy as np
from scipy.integrate import solve_bvp

from bookout import out

a, b, p = 0.020, 0.025, 10e6
E, nu = 70e9, 0.33                      # 铝合金
C1 = p * a * a / (b * b - a * a)
C2 = p * a * a * b * b / (b * b - a * a)
sr = lambda r: C1 - C2 / r ** 2
st = lambda r: C1 + C2 / r ** 2
out(lm_a_mm=a * 1000, lm_b_mm=b * 1000, lm_p=p / 1e6, lm_st_a=st(a) / 1e6, lm_st_b=st(b) / 1e6,
    lm_thin=p * a / (b - a) / 1e6, lm_thin_mean=p * (a + b) / 2 / (b - a) / 1e6)
rows = []
for r in np.linspace(a, b, 6):
    rows.append(f"| {r * 1000:.0f} | {sr(r) / 1e6:.2f} | {st(r) / 1e6:.2f} |")
out(lm_tab="\n".join(rows))
# 位移 u = A r + B/r（平面应力）：σ_r = E/(1−ν²)(u′ + ν u/r)
A = C1 * (1 - nu) / E
B = C2 * (1 + nu) / E
out(lm_ua_um=(A * a + B / a) * 1e6)


# 数值核对：把欧拉方程作为边值问题求解，边界条件为 σ_r(a) = −p、σ_r(b) = 0
def f(r, y):
    return np.vstack([y[1], -y[1] / r + y[0] / r ** 2])


def bc(ya, yb):
    k = E / (1 - nu * nu)
    return np.array([k * (ya[1] + nu * ya[0] / a) + p, k * (yb[1] + nu * yb[0] / b)])


rr = np.linspace(a, b, 50)
sol = solve_bvp(f, bc, rr, np.zeros((2, rr.size)) + 1e-6, tol=1e-12)
ua_num = float(sol.sol(a)[0])
out(lm_ua_num_um=ua_num * 1e6)
