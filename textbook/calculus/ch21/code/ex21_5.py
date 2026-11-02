"""21.5 节：非线性系统。有阻尼单摆的平衡点；捕食者–猎物（洛特卡–沃尔泰拉）方程的守恒量与周期轨道；
范德波尔振子（μ = 1）的极限环：从里面和外面出发都趋于同一个闭轨，振幅与周期。"""
import math

import numpy as np
from scipy.integrate import solve_ivp

from bookout import out

# 洛特卡–沃尔泰拉：x′ = a x − b x y，y′ = −c y + d x y
a, b, c, d = 1.0, 0.1, 1.5, 0.075
H = lambda x, y: d * x - c * math.log(x) + b * y - a * math.log(y)
s = solve_ivp(lambda t, z: [a * z[0] - b * z[0] * z[1], -c * z[1] + d * z[0] * z[1]], (0, 30), [10.0, 5.0],
              rtol=1e-11, atol=1e-12, dense_output=True, max_step=0.01)
Hs = [H(x, y) for x, y in zip(s.y[0], s.y[1])]
# 周期：x 的相邻两个极大值
from scipy.signal import argrelmax
im = argrelmax(s.y[0])[0]
out(lv_xeq=c / d, lv_yeq=a / b, lv_H_drift=float(max(Hs) - min(Hs)), lv_T=float(s.t[im[1]] - s.t[im[0]]),
    lv_xmax=float(s.y[0].max()), lv_xmin=float(s.y[0].min()), lv_T0=2 * math.pi / math.sqrt(a * c))

# 范德波尔：x″ − μ(1 − x²)x′ + x = 0，μ = 1
mu = 1.0
vdp = lambda t, z: [z[1], mu * (1 - z[0] ** 2) * z[1] - z[0]]
res = {}
for x0, key in ((0.1, "in"), (4.0, "out")):
    s = solve_ivp(vdp, (0, 60), [x0, 0.0], rtol=1e-11, atol=1e-12, max_step=0.01)
    tail = s.t > 40
    xs = s.y[0][tail]
    im = argrelmax(xs)[0]
    res[key] = (float(xs.max()), float(np.diff(s.t[tail][im]).mean()))
out(vp_amp_in=res["in"][0], vp_amp_out=res["out"][0], vp_T_in=res["in"][1], vp_T_out=res["out"][1])
